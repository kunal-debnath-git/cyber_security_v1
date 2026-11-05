"""Small shared helpers used by the phase modules.

Kept stdlib-only so the project runs on a stock Kali Python install.
External tools (whois, dig, nmap, ...) are invoked via subprocess and
their absence is reported instead of crashing, since the dev/test
container they were first written in does not have them installed.
"""

import shutil
import subprocess
from datetime import datetime, timezone


def tool_available(name):
    """True if `name` is on PATH."""
    return shutil.which(name) is not None


def run_cmd(cmd, timeout=30):
    """Run a command (list of args). Returns (ok: bool, output: str).

    ok is False both when the binary is missing and when it raised/timed
    out, so callers can just print `output` either way.
    """
    if not tool_available(cmd[0]):
        return False, (
            f"'{cmd[0]}' not found on PATH. On Kali: sudo apt install {cmd[0]}"
        )
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout or ""
        if result.returncode != 0:
            output = (output + "\n" + (result.stderr or "")).strip()
        return result.returncode == 0, output.strip()
    except subprocess.TimeoutExpired:
        return False, f"Timed out after {timeout}s: {' '.join(cmd)}"
    except OSError as exc:
        return False, f"Error running {' '.join(cmd)}: {exc}"


def confirm(prompt_text, input_fn=input):
    """Ask a yes/no question. Defaults to No on anything but y/yes."""
    try:
        answer = input_fn(prompt_text)
    except (EOFError, KeyboardInterrupt):
        return False
    return answer.strip().lower() in ("y", "yes")


def prompt(prompt_text, input_fn=input, default=""):
    """Ask for free text; returns `default` on empty/EOF/interrupt."""
    try:
        answer = input_fn(prompt_text)
    except (EOFError, KeyboardInterrupt):
        return default
    answer = answer.strip()
    return answer if answer else default


def append_timestamped_log(path, note):
    """Append a UTC-timestamped line to a local log file.

    Shared by any phase that logs activity notes (General Task's
    session log, Social Engineering's campaign log, ...), so they all
    write the same format to the same kind of file. Returns the
    formatted line on success, or None if the write failed.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"{timestamp} {note}\n"
    try:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError:
        return None
    return line
