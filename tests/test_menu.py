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
        # Reconnaissance (2) and Scanning (3) are now real submenus and are
        # covered by their own test files; the rest are still bare stubs.
        for key in ("1", "4", "5", "6"):
            mod = main.MENU[key]
            out = run_with([key, "0"])
            self.assertIn(f"[{mod.TITLE}] not implemented yet.", out)

    def test_reconnaissance_and_scanning_open_their_submenu(self):
        for key in ("2", "3"):
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
