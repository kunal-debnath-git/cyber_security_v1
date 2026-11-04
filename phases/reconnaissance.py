"""Reconnaissance phase: WHOIS, DNS enumeration, Google dork builder.

Techniques Used (from the phase table): Google Dorking, WHOIS lookups,
DNS enumeration, Social engineering tactics.

These are all passive/OSINT techniques against public records, so no
authorization prompt is required to use this submenu. Social engineering
tactics are not automated here; the dork builder is the stand-in for the
"Google Dorking" line.
"""

import socket

from utils import run_cmd, prompt

TITLE = "Reconnaissance"

DORK_TEMPLATES = [
    'site:{d}',
    'site:{d} filetype:pdf',
    'site:{d} intitle:"index of"',
    'site:{d} ext:log | ext:env | ext:sql',
    'site:{d} inurl:admin',
    'site:{d} inurl:login',
    '"{d}" intext:password',
]


def whois_lookup(target, input_fn=input):
    print(f"\n-- WHOIS lookup: {target} --")
    ok, output = run_cmd(["whois", target])
    print(output if output else "(no output)")


def dns_enumeration(target, input_fn=input):
    print(f"\n-- DNS enumeration: {target} --")
    records = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]
    used_dig = False
    for rtype in records:
        ok, output = run_cmd(["dig", "+short", target, rtype])
        if ok and "not found on PATH" not in output:
            used_dig = True
            print(f"{rtype:6s}: {output if output else '(none)'}")
    if not used_dig:
        print("'dig' not available, falling back to Python socket (A record only).")
        try:
            addr = socket.gethostbyname(target)
            print(f"A     : {addr}")
        except OSError as exc:
            print(f"Lookup failed: {exc}")


def google_dork_builder(target, input_fn=input):
    print(f"\n-- Google dork builder: {target} --")
    print("Paste these into Google yourself; nothing is sent over the network.\n")
    for template in DORK_TEMPLATES:
        dork = template.format(d=target)
        print(f"  {dork}")


SUBMENU = {
    "1": ("WHOIS lookup", whois_lookup),
    "2": ("DNS enumeration", dns_enumeration),
    "3": ("Google dork builder", google_dork_builder),
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
    target = prompt("Target domain/host: ", input_fn=input_fn)
    if not target:
        print("No target given, aborting.")
        return
    fn(target, input_fn=input_fn)
