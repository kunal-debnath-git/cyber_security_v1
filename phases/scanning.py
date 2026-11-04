"""Scanning phase: host discovery, port scanning, vulnerability scanning.

Techniques Used (from the phase table): Network mapping, Port scanning,
Vulnerability scanning. All backed by `nmap`.

Unlike Reconnaissance, these techniques send packets at the target, so
every action here requires an explicit y/n authorization confirmation
first (you confirm you own the target or are authorized to test it).
Nothing is logged yet; that is a separate, later task.
"""

from utils import run_cmd, prompt, confirm

TITLE = "Scanning"


def _authorized(target, input_fn):
    return confirm(
        f"Confirm you own or are authorized to scan '{target}' (y/N): ",
        input_fn=input_fn,
    )


def host_discovery(target, input_fn=input):
    print(f"\n-- Host discovery (nmap -sn): {target} --")
    ok, output = run_cmd(["nmap", "-sn", target])
    print(output if output else "(no output)")


def port_scan(target, input_fn=input):
    print(f"\n-- Port scan (nmap -sV): {target} --")
    ok, output = run_cmd(["nmap", "-sV", target])
    print(output if output else "(no output)")


def vuln_scan(target, input_fn=input):
    print(f"\n-- Vulnerability scan (nmap --script vuln): {target} --")
    print("This runs nmap's vuln NSE scripts; it is noisy and can take a while.")
    ok, output = run_cmd(["nmap", "--script", "vuln", target], timeout=300)
    print(output if output else "(no output)")


SUBMENU = {
    "1": ("Host discovery (network mapping)", host_discovery),
    "2": ("Port scanning", port_scan),
    "3": ("Vulnerability scanning", vuln_scan),
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
    target = prompt("Target host/IP/CIDR: ", input_fn=input_fn)
    if not target:
        print("No target given, aborting.")
        return
    if not _authorized(target, input_fn):
        print("Not confirmed as authorized; aborting.")
        return
    fn(target, input_fn=input_fn)
