import contextlib
import io
import os
import shutil
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from phases import gaining_access  # noqa: E402


def run_with(inputs):
    it = iter(inputs)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        gaining_access.run(input_fn=lambda _prompt: next(it))
    return buf.getvalue()


class GainingAccessTest(unittest.TestCase):
    def test_back_option_does_nothing(self):
        out = run_with(["0"])
        self.assertIn("Gaining Access", out)

    def test_invalid_option(self):
        self.assertIn("Invalid option", run_with(["9"]))

    def test_sqli_rejects_url_without_param(self):
        out = run_with(["1", "http://example.com/"])
        self.assertIn("Need a URL containing", out)

    def test_sqli_declining_authorization_aborts(self):
        out = run_with(["1", "http://example.com/?id=1", "n"])
        self.assertIn("Not confirmed as authorized", out)

    def test_sqli_runs_against_unreachable_host(self):
        # No network in this sandbox: every request should fail cleanly,
        # not raise.
        out = run_with(["1", "http://127.0.0.1:1/?id=1", "y", "0"])
        self.assertIn("SQL injection probe", out)
        self.assertIn("request failed", out)

    def test_buffer_overflow_no_target_aborts(self):
        self.assertIn("No target given", run_with(["2", ""]))

    def test_buffer_overflow_declining_authorization_aborts(self):
        out = run_with(["2", "127.0.0.1", "n"])
        self.assertIn("Not confirmed as authorized", out)

    def test_buffer_overflow_bad_port_aborts(self):
        out = run_with(["2", "127.0.0.1", "y", "0"])
        self.assertIn("Need a valid port", out)

    def test_buffer_overflow_reports_dropped_connection(self):
        # Port 1 on localhost should refuse immediately in this sandbox.
        out = run_with(["2", "127.0.0.1", "y", "1", "200"])
        self.assertIn("Buffer overflow fuzz", out)
        self.assertTrue(
            "connection failed/dropped" in out or "sent ok" in out
        )

    def test_phishing_provision_writes_template_files_only(self):
        out_dir = "./_test_phishing_templates"
        self.addCleanup(lambda: shutil.rmtree(out_dir, ignore_errors=True))
        out = run_with(["3", "TestCo", out_dir])
        self.assertIn("provision only, nothing is sent", out)
        self.assertTrue(os.path.isfile(os.path.join(out_dir, "awareness_email_template.txt")))
        self.assertTrue(os.path.isfile(os.path.join(out_dir, "awareness_login_mock.html")))
        self.assertTrue(os.path.isfile(os.path.join(out_dir, "awareness_notes.md")))
        with open(os.path.join(out_dir, "awareness_notes.md")) as fh:
            notes = fh.read()
        self.assertIn("not configured to send", notes)
        self.assertIn("not configured to collect", notes)


if __name__ == "__main__":
    unittest.main()
