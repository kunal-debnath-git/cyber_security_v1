import contextlib
import io
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from phases import general_task  # noqa: E402


def run_with(inputs):
    it = iter(inputs)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        general_task.run(input_fn=lambda _prompt: next(it))
    return buf.getvalue()


class GeneralTaskTest(unittest.TestCase):
    def test_back_option_does_nothing(self):
        out = run_with(["0"])
        self.assertIn("General Task", out)

    def test_invalid_option(self):
        self.assertIn("Invalid option", run_with(["9"]))

    def test_update_system_runs_and_declines_upgrade(self):
        # Works whether or not apt is installed: if apt update succeeds
        # it asks for upgrade confirmation (answered "n" here); if apt
        # is missing, it reports that and returns before asking.
        out = run_with(["1", "n"])
        self.assertIn("Update system", out)

    def test_system_network_info_runs(self):
        out = run_with(["2"])
        self.assertIn("Hostname", out)
        self.assertIn("Disk /", out)

    def test_listening_ports_handles_missing_tools(self):
        out = run_with(["3"])
        self.assertIn("Listening ports", out)

    def test_file_hash_calculator_no_path_aborts(self):
        self.assertIn("No file given", run_with(["4", ""]))

    def test_file_hash_calculator_missing_file_aborts(self):
        out = run_with(["4", "/no/such/file/here"])
        self.assertIn("is not a file", out)

    def test_file_hash_calculator_hashes_real_file(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as fh:
            fh.write("hello world")
            path = fh.name
        self.addCleanup(lambda: os.unlink(path))
        out = run_with(["4", path])
        self.assertIn("MD5", out)
        self.assertIn("SHA1", out)
        self.assertIn("SHA256", out)
        # Known SHA256 of "hello world"
        self.assertIn(
            "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9",
            out,
        )

    def test_mac_address_info_handles_missing_ip_tool(self):
        out = run_with(["5"])
        self.assertIn("MAC address", out)

    def test_service_control_invalid_choice_aborts(self):
        out = run_with(["6", "9"])
        self.assertIn("Invalid choice", out)

    def test_service_control_bad_action_aborts(self):
        out = run_with(["6", "1", "frobnicate"])
        self.assertIn("must be 'start' or 'stop'", out.lower())

    def test_session_activity_log_empty_note_skips(self):
        out = run_with(["7", ""])
        self.assertIn("Empty note", out)

    def test_session_activity_log_writes_entry(self):
        log_path = "./_test_activity.log"
        self.addCleanup(lambda: os.path.exists(log_path) and os.unlink(log_path))
        original = general_task.ACTIVITY_LOG_PATH
        general_task.ACTIVITY_LOG_PATH = log_path
        try:
            out = run_with(["7", "testing note"])
        finally:
            general_task.ACTIVITY_LOG_PATH = original
        self.assertIn("Logged to", out)
        with open(log_path) as fh:
            content = fh.read()
        self.assertIn("testing note", content)


if __name__ == "__main__":
    unittest.main()
