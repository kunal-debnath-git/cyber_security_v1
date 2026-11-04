import contextlib
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main  # noqa: E402


def run_with(inputs):
    it = iter(inputs)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        main.run_menu(lambda _prompt: next(it))
    return buf.getvalue()


class MenuTest(unittest.TestCase):
    def test_menu_lists_all_options(self):
        out = run_with(["0"])
        for title in ["General Task", "Reconnaissance", "Scanning",
                      "Gaining Access", "Maintaining Access",
                      "Clearing Tracks", "0. Exit"]:
            self.assertIn(title, out)

    def test_each_option_runs_its_stub(self):
        for key, mod in main.MENU.items():
            out = run_with([key, "0"])
            self.assertIn(f"[{mod.TITLE}] not implemented yet.", out)

    def test_invalid_option(self):
        self.assertIn("Invalid option", run_with(["9", "abc", "0"]))

    def test_eof_exits_cleanly(self):
        buf = io.StringIO()
        def raise_eof(_):
            raise EOFError
        with contextlib.redirect_stdout(buf):
            main.run_menu(raise_eof)
        self.assertIn("Bye.", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
