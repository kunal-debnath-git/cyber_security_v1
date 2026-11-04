"""Social Engineering: a dedicated top-level menu for social-engineering
techniques, borrowing structure/feature ideas from well-known public
projects while leaving out their live/attacking components.

Borrowed from (see pending-for-coding-and-testing.md for the fuller
writeup):
- Social-Engineer Toolkit (SET, trustedsec) - the phase-structured,
  deeply-nested menu this category is modeled on.
- Zphisher (htr-tech) - the idea of offering several pre-built
  templates to choose from, rather than one generic one.

What's deliberately NOT borrowed: SET's and Zphisher's actual live
components - a real credential-harvesting backend behind the mock
pages, live email/SMS sending, and payload/executable generation for
"infectious media". Every function below only writes local template/
briefing/script files or encodes a URL you already own into a QR code;
nothing here sends anything, collects anything, or executes anything
on a target. Use it to prepare material for a documented, authorized
internal security-awareness exercise - the same posture as the
Phishing feature this replaces (previously under Gaining Access).

Techniques Used (from the original phase table): Social engineering
tactics (Reconnaissance), Phishing attacks (Gaining Access) - both
centralized here instead, plus a few related techniques SET's menu
covers that weren't represented yet.
"""

import os

from utils import append_timestamped_log, prompt, run_cmd, tool_available

TITLE = "Social Engineering"

ACTIVITY_LOG_PATH = "activity.log"
DEFAULT_OUTPUT_DIR = "./social_engineering_templates"

AWARENESS_FOOTER = (
    "\n--- FOR INTERNAL AWARENESS USE ONLY. Do not send/use this against "
    "real people without a documented, authorized campaign (security team "
    "+ HR/legal sign-off). ---\n"
)

EMAIL_TEMPLATES = {
    "1": (
        "IT helpdesk - password reset",
        lambda org: (
            f"Subject: Action required - verify your {org} account\n\n"
            f"Hi {{{{first_name}}}},\n\n"
            f"We noticed unusual sign-in activity on your {org} account. "
            f"Please verify your identity using the secure link below within "
            f"24 hours, or your access will be suspended.\n\n"
            f"[VERIFY MY ACCOUNT]({{{{tracking_link}}}})\n\n"
            f"{org} IT Security Team\n"
        ),
    ),
    "2": (
        "Finance - overdue invoice",
        lambda org: (
            f"Subject: Overdue invoice from {org} - payment required\n\n"
            f"Hi {{{{first_name}}}},\n\n"
            f"Invoice #{{{{invoice_number}}}} is now overdue. Please review "
            f"and settle the attached statement to avoid a late fee.\n\n"
            f"[VIEW INVOICE]({{{{tracking_link}}}})\n\n"
            f"{org} Accounts Payable\n"
        ),
    ),
    "3": (
        "Shipping - delivery failed",
        lambda org: (
            f"Subject: {org} - delivery attempt failed\n\n"
            f"Hi {{{{first_name}}}},\n\n"
            f"We tried to deliver your package but no one was available. "
            f"Reschedule delivery using the link below within 48 hours or "
            f"the package will be returned to sender.\n\n"
            f"[RESCHEDULE DELIVERY]({{{{tracking_link}}}})\n\n"
            f"{org} Logistics\n"
        ),
    ),
    "4": (
        "Prize / gift notification",
        lambda org: (
            f"Subject: You've been selected - {org} rewards\n\n"
            f"Hi {{{{first_name}}}},\n\n"
            f"Congratulations! You've been randomly selected for a {org} "
            f"rewards bonus. Claim it within 24 hours before it expires.\n\n"
            f"[CLAIM MY REWARD]({{{{tracking_link}}}})\n\n"
            f"{org} Rewards Team\n"
        ),
    ),
}

PAGE_TEMPLATES = {
    "1": ("Generic SSO sign-in", "SSO"),
    "2": ("Generic webmail sign-in", "Webmail"),
    "3": ("Generic cloud storage sign-in", "Cloud Storage"),
    "4": ("Generic VPN portal sign-in", "VPN Portal"),
}

PRETEXT_SCENARIOS = {
    "1": (
        "IT support - urgent ticket",
        lambda org: (
            f"PRETEXT: IT support calling about an urgent ticket\n\n"
            f'Opening: "Hi, this is {{{{caller_name}}}} from {org} IT '
            f'Support. We\'re seeing repeated failed logins on your '
            f'account and wanted to confirm it\'s really you before we '
            f'lock it."\n\n'
            f"Goal (awareness exercise): see whether the target reads out "
            f"a password/MFA code or installs 'remote support' software on "
            f"request. Do not actually request real credentials even in a "
            f"sanctioned test - capture only whether they would comply.\n"
        ),
    ),
    "2": (
        "Vendor - invoice confirmation",
        lambda org: (
            f"PRETEXT: Vendor calling to confirm a wire/invoice change\n\n"
            f'Opening: "Hi, this is {{{{caller_name}}}} from '
            f'{{{{vendor_name}}}}, a supplier for {org}. We updated our '
            f'banking details and wanted to confirm your team has the new '
            f'ones before the next payment."\n\n'
            f"Goal (awareness exercise): see whether finance staff follow "
            f"the documented verification process (callback to a known "
            f"number) rather than trusting the inbound call.\n"
        ),
    ),
    "3": (
        "Executive impersonation - urgent request",
        lambda org: (
            f"PRETEXT: Caller impersonating an executive, urgent request\n\n"
            f'Opening: "Hi, this is {{{{exec_name}}}}, I\'m in a meeting '
            f'and need you to action something quickly for {org} - can you '
            f'help?"\n\n'
            f"Goal (awareness exercise): see whether urgency/authority "
            f"pressure gets a policy (payment, access, info-sharing) "
            f"bypassed without secondary verification.\n"
        ),
    ),
}


def _write_text(path, content):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def spear_phishing_email(input_fn=input):
    print("\n-- Spear-phishing email template --")
    print("Writes a local template file; does not send anything.\n")
    for key, (label, _fn) in EMAIL_TEMPLATES.items():
        print(f"  {key}. {label}")
    choice = prompt("Pick a template (number): ", input_fn=input_fn)
    entry = EMAIL_TEMPLATES.get(choice)
    if entry is None:
        print("Invalid template choice, aborting.")
        return
    label, builder = entry
    org = prompt("Organization/brand name (default 'Acme Corp'): ",
                 input_fn=input_fn, default="Acme Corp")
    out_dir = prompt(f"Output directory (default '{DEFAULT_OUTPUT_DIR}'): ",
                     input_fn=input_fn, default=DEFAULT_OUTPUT_DIR)
    slug = label.split(" - ")[0].lower().replace(" ", "_")
    path = os.path.join(out_dir, f"email_{slug}.txt")
    _write_text(path, builder(org) + AWARENESS_FOOTER)
    print(f"Wrote: {path}")


def mock_landing_page(input_fn=input):
    print("\n-- Mock landing/login page --")
    print("Static HTML only, no backend/form action; collects nothing.\n")
    for key, (label, _service) in PAGE_TEMPLATES.items():
        print(f"  {key}. {label}")
    choice = prompt("Pick a page style (number): ", input_fn=input_fn)
    entry = PAGE_TEMPLATES.get(choice)
    if entry is None:
        print("Invalid page choice, aborting.")
        return
    label, service = entry
    org = prompt("Organization/brand name (default 'Acme Corp'): ",
                 input_fn=input_fn, default="Acme Corp")
    out_dir = prompt(f"Output directory (default '{DEFAULT_OUTPUT_DIR}'): ",
                     input_fn=input_fn, default=DEFAULT_OUTPUT_DIR)
    slug = service.lower().replace(" ", "_")
    path = os.path.join(out_dir, f"page_{slug}.html")
    html = (
        "<!doctype html><html><head><title>"
        f"{org} {service} (AWARENESS MOCK - NOT FOR REAL USE)</title></head>\n"
        "<body style=\"font-family:sans-serif;max-width:360px;margin:60px auto;\">\n"
        f"<h2>{org} {service}</h2>\n"
        "<p style=\"color:red;font-weight:bold;\">INTERNAL AWARENESS MOCK "
        "- do not deploy publicly or collect real credentials.</p>\n"
        "<form onsubmit=\"return false;\">\n"
        "  <input placeholder=\"Email\"><br><br>\n"
        "  <input placeholder=\"Password\" type=\"password\"><br><br>\n"
        "  <button type=\"submit\">Sign in</button>\n"
        "</form>\n</body></html>\n"
    )
    _write_text(path, html)
    print(f"Wrote: {path}")


def pretexting_script(input_fn=input):
    print("\n-- Pretexting / vishing call script --")
    print("Writes a local script file for an authorized phone-based "
          "social-engineering test; does not place any call.\n")
    for key, (label, _fn) in PRETEXT_SCENARIOS.items():
        print(f"  {key}. {label}")
    choice = prompt("Pick a scenario (number): ", input_fn=input_fn)
    entry = PRETEXT_SCENARIOS.get(choice)
    if entry is None:
        print("Invalid scenario choice, aborting.")
        return
    label, builder = entry
    org = prompt("Organization/brand name (default 'Acme Corp'): ",
                 input_fn=input_fn, default="Acme Corp")
    out_dir = prompt(f"Output directory (default '{DEFAULT_OUTPUT_DIR}'): ",
                     input_fn=input_fn, default=DEFAULT_OUTPUT_DIR)
    slug = label.split(" - ")[0].lower().replace(" ", "_")
    path = os.path.join(out_dir, f"pretext_{slug}.txt")
    _write_text(path, builder(org) + AWARENESS_FOOTER)
    print(f"Wrote: {path}")


def usb_drop_briefing(input_fn=input):
    print("\n-- USB-drop awareness briefing --")
    print("Writes a briefing/warning document only; generates no payload "
          "or executable of any kind.\n")
    org = prompt("Organization/brand name (default 'Acme Corp'): ",
                 input_fn=input_fn, default="Acme Corp")
    out_dir = prompt(f"Output directory (default '{DEFAULT_OUTPUT_DIR}'): ",
                     input_fn=input_fn, default=DEFAULT_OUTPUT_DIR)
    path = os.path.join(out_dir, "usb_drop_awareness_briefing.md")
    content = (
        f"# USB-drop awareness briefing - {org}\n\n"
        "## What this exercise tests\n\n"
        "Whether staff plug in and open an unknown USB drive found on-site "
        "(a car park, lobby, desk) instead of handing it to Security.\n\n"
        "## How to run it (people/process only - no device payload here)\n\n"
        "1. Get documented authorization (security team + HR/legal) before "
        "placing any drives.\n"
        "2. Label drives clearly enough to track which one was picked up, "
        "without a malicious payload on them.\n"
        "3. Record who plugged one in and what they did, as a training "
        "signal, not a disciplinary one.\n"
        "4. Debrief: show staff what a real malicious drive could have "
        "done, and the \"don't plug in unknown media, hand it to Security\" "
        "policy.\n\n"
        "## What this tool deliberately does not do\n\n"
        "It does not generate an autorun script, executable, or any other "
        "payload to put on a drive. If your exercise needs a harmless "
        "'beacon' file to prove a drive was opened, build and review that "
        "separately with your security team - it's out of scope here.\n"
    )
    _write_text(path, content)
    print(f"Wrote: {path}")


def qr_code_generator(input_fn=input):
    print("\n-- QR code generator --")
    print("Encodes a URL you provide into a QR code image. Use only a URL "
          "you control (e.g. your own awareness-training landing page).\n")
    url = prompt("URL to encode: ", input_fn=input_fn)
    if not url:
        print("No URL given, aborting.")
        return
    out_dir = prompt(f"Output directory (default '{DEFAULT_OUTPUT_DIR}'): ",
                     input_fn=input_fn, default=DEFAULT_OUTPUT_DIR)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "qr_code.png")

    if not tool_available("qrencode"):
        print("'qrencode' not found on PATH; can't render an image. "
              "On Kali: sudo apt install qrencode")
        print(f"URL to encode manually: {url}")
        return
    ok, output = run_cmd(["qrencode", "-o", out_path, url])
    if ok:
        print(f"Wrote: {out_path}")
    else:
        print(output)
        print(f"URL to encode manually: {url}")


def campaign_log(input_fn=input):
    print("\n-- Campaign log --")
    note = prompt(
        "Note (campaign/template used, target org, authorization ref): ",
        input_fn=input_fn,
    )
    if not note:
        print("Empty note, nothing logged.")
        return
    line = append_timestamped_log(ACTIVITY_LOG_PATH, f"[social-engineering] {note}")
    if line is None:
        print(f"Could not write to '{ACTIVITY_LOG_PATH}'.")
        return
    print(f"Logged to {ACTIVITY_LOG_PATH}: {line.strip()}")


SUBMENU = {
    "1": ("Spear-phishing email template", spear_phishing_email),
    "2": ("Mock landing/login page", mock_landing_page),
    "3": ("Pretexting / vishing call script", pretexting_script),
    "4": ("USB-drop awareness briefing", usb_drop_briefing),
    "5": ("QR code generator (for a URL you control)", qr_code_generator),
    "6": ("Campaign log", campaign_log),
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
