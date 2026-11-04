import contextlib
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from phases import scanning  # noqa: E402


def run_with(inputs):
    it = iter(inputs)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        scanning.run(input_fn=lambda _prompt: next(it))
    return buf.getvalue()


class ScanningTest(unittest.TestCase):
    def test_back_option_does_nothing(self):
        out = run_with(["0"])
        self.assertIn("Scanning", out)

    def test_invalid_option(self):
        self.assertIn("Invalid option", run_with(["9"]))

    def test_no_target_aborts(self):
        self.assertIn("No target given", run_with(["1", ""]))

    def test_declining_authorization_aborts_before_scan(self):
        out = run_with(["1", "10.0.0.5", "n"])
        self.assertIn("Not confirmed as authorized", out)
        self.assertNotIn("Host discovery (nmap", out)

    def test_authorized_host_discovery_runs(self):
        out = run_with(["1", "10.0.0.5", "y"])
        self.assertIn("Host discovery (nmap -sn): 10.0.0.5", out)

    def test_authorized_port_scan_runs(self):
        out = run_with(["2", "10.0.0.5", "yes"])
        self.assertIn("Port scan (nmap -sV): 10.0.0.5", out)

    def test_authorized_vuln_scan_runs(self):
        out = run_with(["3", "10.0.0.5", "y"])
        self.assertIn("Vulnerability scan (nmap --script vuln): 10.0.0.5", out)


if __name__ == "__main__":
    unittest.main()
