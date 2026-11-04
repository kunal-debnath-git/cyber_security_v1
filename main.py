#!/usr/bin/env python3
"""CLI menu entry point. Python 3 stdlib only, Kali friendly.

Options 1-4 (General Task, Reconnaissance, Scanning, Gaining Access)
are implemented; 5-6 (Maintaining Access, Clearing Tracks) are stubs
pending a scope decision - see pending-for-coding-and-testing.md.
"""

from phases import (
    general_task,
    reconnaissance,
    scanning,
    gaining_access,
    maintaining_access,
    clearing_tracks,
    social_engineering,
)

MENU = {
    "1": general_task,
    "2": reconnaissance,
    "3": scanning,
    "4": gaining_access,
    "5": maintaining_access,
    "6": clearing_tracks,
    "7": social_engineering,
}


def show_menu():
    print("\n==== Cyber Security Toolkit v1 ====")
    for key, mod in MENU.items():
        print(f" {key}. {mod.TITLE}")
    print(" 0. Exit")


def run_menu(input_fn=input):
    while True:
        show_menu()
        try:
            choice = input_fn("Select an option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            return
        if choice == "0":
            print("Bye.")
            return
        mod = MENU.get(choice)
        if mod is None:
            print("Invalid option, try again.")
            continue
        mod.run(input_fn=input_fn)


if __name__ == "__main__":
    run_menu()
