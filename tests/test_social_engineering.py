import contextlib
import io
import os
import shutil
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from phases import social_engineering  # noqa: E402


def run_with(inputs):
    it = iter(inputs)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        social_engineering.run(input_fn=lambda _prompt: next(it))
    return buf.getvalue()


class SocialEngineeringTest(unittest.TestCase):
    def setUp(self):
        self.out_dir = "./_test_social_engineering"
        self.addCleanup(lambda: shutil.rmtree(self.out_dir, ignore_errors=True))

    def test_back_option_does_nothing(self):
        out = run_with(["0"])
        self.assertIn("Social Engineering", out)

    def test_invalid_option(self):
        self.assertIn("Invalid option", run_with(["9"]))

    def test_spear_phishing_invalid_template_aborts(self):
        self.assertIn("Invalid template choice", run_with(["1", "9"]))

    def test_spear_phishing_writes_file_with_footer(self):
        out = run_with(["1", "1", "TestCo", self.out_dir])
        self.assertIn("Wrote:", out)
        path = os.path.join(self.out_dir, "email_it_helpdesk.txt")
        self.assertTrue(os.path.isfile(path))
        with open(path) as fh:
            content = fh.read()
        self.assertIn("TestCo", content)
        self.assertIn("INTERNAL AWARENESS USE ONLY", content)

    def test_mock_landing_page_invalid_choice_aborts(self):
        self.assertIn("Invalid page choice", run_with(["2", "9"]))

    def test_mock_landing_page_writes_inert_html(self):
        out = run_with(["2", "1", "TestCo", self.out_dir])
        self.assertIn("Wrote:", out)
        path = os.path.join(self.out_dir, "page_sso.html")
        self.assertTrue(os.path.isfile(path))
        with open(path) as fh:
            html = fh.read()
        self.assertIn("AWARENESS MOCK", html)
        self.assertNotIn("<form action=", html)  # no real submit target

    def test_pretexting_invalid_scenario_aborts(self):
        self.assertIn("Invalid scenario choice", run_with(["3", "9"]))

    def test_pretexting_writes_script(self):
        out = run_with(["3", "1", "TestCo", self.out_dir])
        self.assertIn("Wrote:", out)
        path = os.path.join(self.out_dir, "pretext_it_support.txt")
        self.assertTrue(os.path.isfile(path))
        with open(path) as fh:
            content = fh.read()
        self.assertIn("PRETEXT", content)

    def test_usb_drop_briefing_has_no_payload_language(self):
        out = run_with(["4", "TestCo", self.out_dir])
        self.assertIn("Wrote:", out)
        path = os.path.join(self.out_dir, "usb_drop_awareness_briefing.md")
        with open(path) as fh:
            content = fh.read()
        self.assertIn("does not generate", content)

    def test_qr_code_no_url_aborts(self):
        self.assertIn("No URL given", run_with(["5", ""]))

    def test_qr_code_handles_missing_qrencode(self):
        out = run_with(["5", "http://example.com/training", self.out_dir])
        self.assertIn("URL to encode manually", out)

    def test_campaign_log_empty_note_skips(self):
        out = run_with(["6", ""])
        self.assertIn("Empty note", out)

    def test_campaign_log_writes_tagged_entry(self):
        log_path = "./_test_se_activity.log"
        self.addCleanup(lambda: os.path.exists(log_path) and os.unlink(log_path))
        original = social_engineering.ACTIVITY_LOG_PATH
        social_engineering.ACTIVITY_LOG_PATH = log_path
        try:
            out = run_with(["6", "ran IT helpdesk template against pilot group"])
        finally:
            social_engineering.ACTIVITY_LOG_PATH = original
        self.assertIn("Logged to", out)
        with open(log_path) as fh:
            content = fh.read()
        self.assertIn("[social-engineering]", content)
        self.assertIn("pilot group", content)


if __name__ == "__main__":
    unittest.main()
