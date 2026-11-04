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

    def test_still_unimplemented_stubs_print_placeholder(self):
        # General Task (1), Reconnaissance (2), Scanning (3) and Gaining
        # Access (4) are now real submenus, covered by their own test
        # files; 5/6 are still bare stubs.
        for key in ("5", "6"):
            mod = main.MENU[key]
            out = run_with([key, "0"])
            self.assertIn(f"[{mod.TITLE}] not implemented yet.", out)

    def test_submenu_phases_open_their_submenu(self):
        for key in ("1", "2", "3", "4"):
            mod = main.MENU[key]
            out = run_with([key, "0", "0"])
            self.assertIn(f"== {mod.TITLE} ==", out)

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
