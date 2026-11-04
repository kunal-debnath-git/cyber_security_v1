"""General Task phase: everyday Kali housekeeping/utilities, not tied
to any one of the five hacking phases.

Techniques Used: package/tool updates, system & network info, listening
ports, file hashing, MAC address info, service control, activity log.

Everything here runs on the local box only (no remote target). Actions
that change system state (apt upgrade, restarting a service, changing
a MAC address) ask for a plain y/n confirmation first; read-only items
(info report, listening ports, hashing, viewing MACs, logging a note)
do not.
"""

import hashlib
import os
import platform
import shutil
import socket
from datetime import datetime, timezone

from utils import confirm, prompt, run_cmd, tool_available

TITLE = "General Task"

ACTIVITY_LOG_PATH = "activity.log"


def update_system(input_fn=input):
    print("\n-- Update system & tools --")
    print("Step 1: apt update (refresh package index)")
    ok, output = run_cmd(["apt", "update"], timeout=120)
    print(output if output else "(no output)")
    if not ok:
        return
    if confirm("\nProceed with 'apt upgrade -y' now? (y/N): ", input_fn=input_fn):
        print("\nStep 2: apt upgrade -y")
        ok, output = run_cmd(["apt", "upgrade", "-y"], timeout=1800)
        print(output if output else "(no output)")
    else:
        print("Skipped upgrade.")


def system_network_info(input_fn=input):
    print("\n-- System & network info --")
    print(f"Hostname : {socket.gethostname()}")
    uname = platform.uname()
    print(f"System   : {uname.system} {uname.release} ({uname.machine})")
    print(f"Python   : {platform.python_version()}")

    ok, output = run_cmd(["uptime", "-p"])
    print(f"Uptime   : {output if ok else '(unavailable)'}")

    try:
        total, used, free = shutil.disk_usage("/")
        gb = 1024 ** 3
        print(f"Disk /   : {used / gb:.1f} GB used / {total / gb:.1f} GB total "
              f"({free / gb:.1f} GB free)")
    except OSError as exc:
        print(f"Disk /   : unavailable ({exc})")

    print("\nNetwork interfaces:")
    ok, output = run_cmd(["ip", "-brief", "addr"])
    if ok:
        print(output if output else "(no interfaces reported)")
    else:
        print(output)
        try:
            ip_addr = socket.gethostbyname(socket.gethostname())
            print(f"(fallback) local IP: {ip_addr}")
        except OSError as exc:
            print(f"(fallback) could not resolve local IP: {exc}")


def listening_ports(input_fn=input):
    print("\n-- Listening ports & active connections --")
    ok, output = run_cmd(["ss", "-tulpn"])
    if ok:
        print(output if output else "(no output)")
        return
    print(output)
    print("Falling back to 'netstat -tulpn'...")
    ok, output = run_cmd(["netstat", "-tulpn"])
    print(output if output else "(no output)")


def file_hash_calculator(input_fn=input):
    print("\n-- File hash calculator --")
    path = prompt("Path to file: ", input_fn=input_fn)
    if not path:
        print("No file given, aborting.")
        return
    if not os.path.isfile(path):
        print(f"'{path}' is not a file, aborting.")
        return

    hashers = {
        "md5": hashlib.md5(),
        "sha1": hashlib.sha1(),
        "sha256": hashlib.sha256(),
    }
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                for hasher in hashers.values():
                    hasher.update(chunk)
    except OSError as exc:
        print(f"Could not read '{path}': {exc}")
        return

    print(f"File: {path}")
    for name, hasher in hashers.items():
        print(f"  {name.upper():6s}: {hasher.hexdigest()}")


def mac_address_info(input_fn=input):
    print("\n-- MAC address viewer / randomizer --")
    ok, output = run_cmd(["ip", "-brief", "link"])
    print(output if output else "(no interfaces reported)")
    if not ok:
        return

    if not tool_available("macchanger"):
        print("\n'macchanger' not found on PATH; randomization unavailable. "
              "On Kali: sudo apt install macchanger")
        return

    iface = prompt(
        "\nInterface to randomize the MAC of (blank to skip): ",
        input_fn=input_fn,
    )
    if not iface:
        print("Skipped.")
        return
    if not confirm(
        f"Confirm: randomize the MAC address of '{iface}' now? (y/N): ",
        input_fn=input_fn,
    ):
        print("Cancelled.")
        return
    ok, output = run_cmd(["macchanger", "-r", iface])
    print(output if output else "(no output)")


SERVICES = ["postgresql", "ssh"]


def service_control(input_fn=input):
    print("\n-- Start/stop key services --")
    print("Services: " + ", ".join(f"{i}) {name}" for i, name in enumerate(SERVICES, 1)))
    choice = prompt("Pick a service (number): ", input_fn=input_fn)
    try:
        service = SERVICES[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid choice, aborting.")
        return
    action = prompt("start or stop? ", input_fn=input_fn, default="").strip().lower()
    if action not in ("start", "stop"):
        print("Must be 'start' or 'stop', aborting.")
        return
    if not confirm(
        f"Confirm: {action} service '{service}' now? (y/N): ", input_fn=input_fn
    ):
        print("Cancelled.")
        return
    ok, output = run_cmd(["systemctl", action, service])
    print(output if output else f"(no output, exit {'ok' if ok else 'failed'})")


def session_activity_log(input_fn=input):
    print("\n-- Session activity log --")
    note = prompt("Note (what you're doing / target / authorization ref): ",
                  input_fn=input_fn)
    if not note:
        print("Empty note, nothing logged.")
        return
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"{timestamp} {note}\n"
    try:
        with open(ACTIVITY_LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError as exc:
        print(f"Could not write to '{ACTIVITY_LOG_PATH}': {exc}")
        return
    print(f"Logged to {ACTIVITY_LOG_PATH}: {line.strip()}")


SUBMENU = {
    "1": ("Update system & tools", update_system),
    "2": ("System & network info report", system_network_info),
    "3": ("Listening ports & active connections", listening_ports),
    "4": ("File hash calculator (MD5/SHA1/SHA256)", file_hash_calculator),
    "5": ("MAC address viewer / randomizer", mac_address_info),
    "6": ("Start/stop key services (postgresql, ssh)", service_control),
    "7": ("Session activity log", session_activity_log),
}


def run(input_fn=input):
    print(f"\n== {TITLE} ==")
    for key, (label, _fn) in SUBMENU.items():
        print(f" {key}. {label}")
    print(" 0. Back")
    choice = prompt("Select an option: ", input_fn=input_fn)
    if choice == "0" or choice == "":
        return
    entry = SUBMENU.get(choice)
    if entry is None:
        print("Invalid option.")
        return
    _label, fn = entry
    fn(input_fn=input_fn)
