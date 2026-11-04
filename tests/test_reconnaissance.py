import contextlib
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from phases import reconnaissance  # noqa: E402


def run_with(inputs):
    it = iter(inputs)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        reconnaissance.run(input_fn=lambda _prompt: next(it))
    return buf.getvalue()


class ReconnaissanceTest(unittest.TestCase):
    def test_back_option_does_nothing(self):
        out = run_with(["0"])
        self.assertIn("Reconnaissance", out)
        self.assertNotIn("WHOIS lookup: ", out)

    def test_invalid_option(self):
        self.assertIn("Invalid option", run_with(["9"]))

    def test_no_target_aborts(self):
        self.assertIn("No target given", run_with(["1", ""]))

    def test_whois_runs_without_crashing_when_tool_missing(self):
        out = run_with(["1", "example.com"])
        self.assertIn("WHOIS lookup", out)

    def test_dns_enumeration_falls_back_to_socket_when_dig_missing(self):
        out = run_with(["2", "localhost"])
        self.assertIn("DNS enumeration", out)

    def test_google_dork_builder_prints_dorks_for_target(self):
        out = run_with(["3", "example.com"])
        self.assertIn("site:example.com", out)
        self.assertIn("intitle", out)


if __name__ == "__main__":
    unittest.main()
