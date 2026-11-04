---
name: cyber-security-v1
description: Orientation and standing rules for the cyber_security_v1 project — a CLI-menu-driven ethical-hacking/cybersecurity toolkit (Python 3 stdlib + Bash) whose real target environment is Kali Linux running inside Termux on Android. Use this skill whenever working in this repo (kunal-debnath-git/cyber_security_v1), whenever the user asks to add/change a menu option, a "phase" (General Task, Reconnaissance, Scanning, Gaining Access, Maintaining Access, Clearing Tracks, Social Engineering), anything in phases/, main.py, utils.py or tests/, or whenever picking this project back up after a gap — even if they just say "continue the toolkit" or "add X to the menu" without naming the repo. Load this before writing any code here so the safety posture, the four-docs-updated standing instruction, and the push-to-main workflow aren't re-derived or re-litigated each session.
---

# cyber_security_v1 — project skill

A CLI-menu-driven ethical-hacking/cybersecurity toolkit. Python 3
stdlib + Bash only, no GUI, no web interface — menu only. Built to run
on Kali Linux, with the actual working environment being **Kali Linux
running inside Termux on Android** (not a desktop or VM) — see
`export-import.md` for exactly what that implies.

Repo: `kunal-debnath-git/cyber_security_v1`. Read this skill fully
before making changes; it's short on purpose. For anything beyond
orientation, go to the doc named for it rather than guessing.

## Layout

```
main.py                   menu loop (options 1-7, 0 = Exit)
utils.py                  shared helpers: run_cmd() (safe subprocess
                           wrapper, reports missing tools instead of
                           crashing), confirm()/prompt() (testable via
                           input_fn param), tool_available(),
                           append_timestamped_log()
phases/                   one module per menu option (see below)
tests/                    unittest suite, one file per phase module
.claude/skills/           this skill
```

Four docs track project state and **must be updated together with
every feature change, not just when asked** — this is a standing
instruction from the project owner, not a suggestion:

- `README.md` — usage, status table, requirements
- `menu-tree.md` — visual snapshot of what's built vs. proposed vs. stub
- `pending-for-coding-and-testing.md` — backlog, open decisions,
  borrowed-feature-idea proposals awaiting go-ahead
- `export-import.md` — how to get code out of a dev/cloud session and
  into Kali-in-Termux, including known caveats (no systemd in a
  proot-distro chroot, no root for raw sockets/SYN scans, etc.)

Read whichever of these is relevant before changing it; don't
duplicate their content here — this skill is the map, not the
territory.

## Menu structure

| # | Phase | Status |
|---|---|---|
| 1 | General Task | built — apt update/upgrade, system/network info, listening ports, file hashing, MAC view/randomize, service start/stop, session activity log (`activity.log`) |
| 2 | Reconnaissance | built — WHOIS, DNS enumeration, Google dork builder. Passive/OSINT only, **no** authorization prompt |
| 3 | Scanning | built — nmap host discovery / port scan / vuln scan. Touches a remote target, so **authorization-confirm gated** |
| 4 | Gaining Access | built — SQL injection probe, buffer overflow fuzzer. Authorization-confirm gated |
| 5 | Maintaining Access | **stub, not built** — see Safety posture below before touching this |
| 6 | Clearing Tracks | **stub, not built** — narrower "read-only log review" proposal pending go-ahead in the pending doc |
| 7 | Social Engineering | built — email/landing-page/pretext-script/USB-briefing/QR generators. All **provision-only** (writes local files, never sends/collects/executes), no target, no authorization prompt |

## Safety posture — preserve this, don't relitigate it

- Any phase that touches a remote target asks a plain y/n "are you
  authorized to test this?" confirmation first (`utils.confirm`),
  before doing anything. This pattern is established in Scanning and
  Gaining Access — reuse it for new target-touching features rather
  than inventing a new gate.
- Anything with real abuse potential (live phishing/credential
  harvesting, rootkits, hidden-account creation, log tampering) is
  either built as inert/provision-only (see Social Engineering, and
  Gaining Access's old Phishing option before it moved there) or
  deliberately left unbuilt, rather than built with extra confirmation
  steps bolted on.
- **Maintaining Access was attempted once and hit a content-safety
  stop** while writing rootkit/persistence/hidden-account code — even
  reframed as a "detection report" or "double-confirmed" flow. Do not
  retry that ground under a different framing. If asked to build
  Maintaining Access, the live option on record is a narrower
  "Tunneling only" (SSH `-L`/`-R` wrapper) — see
  `pending-for-coding-and-testing.md` for the current proposal and
  check with the user before writing it.
- When extending Social Engineering or similar provision-only
  features, keep new output inert: local files only, no live
  send/collect/execute capability, and keep the "AWARENESS
  MOCK"/"INTERNAL USE ONLY" framing in generated content.

## Standing workflow rules

1. **Push directly to `main`** on `kunal-debnath-git/cyber_security_v1`
   — not a feature branch, not a PR, unless the user explicitly asks
   for a PR.
2. **Update the four docs** above together with every feature change.
3. **Stdlib-only Python + Bash**, CLI-menu only — no GUI/web, no new
   third-party Python packages, no `requirements.txt` (intentional).
4. **Run the full test suite before calling anything done**:
   `python3 -m unittest discover -s tests -v`. Tests are written to
   handle missing external tools (`nmap`, `whois`, `macchanger`, ...)
   gracefully — they must pass even when those binaries aren't
   installed in the dev/cloud sandbox.
5. Confirm before pushing anything destructive/irreversible. In
   practice, an uncommitted/untracked-files stop hook tends to force a
   commit+push at the end of a turn — so write clear, well-described
   commit messages, since they'll likely go out promptly.

## Conventions when adding a new phase/feature

- New phase module in `phases/`, exposing `TITLE` and
  `run(input_fn=input)`, with a `SUBMENU` dict of
  `{"key": ("label", function)}` — follow the existing modules
  (`reconnaissance.py` is the simplest example, `general_task.py` and
  `social_engineering.py` show the richer multi-option pattern).
- Every function that prompts takes `input_fn=input` so tests can
  inject canned input (see any `tests/test_*.py` for the pattern:
  `run_with([...])` feeding a list of answers via an iterator).
- Reuse `utils.py` helpers (`run_cmd`, `confirm`, `prompt`,
  `tool_available`, `append_timestamped_log`) instead of duplicating
  subprocess/logging logic in a new phase module.
- Wire a new top-level phase into `main.py`'s `MENU` dict and update
  `tests/test_menu.py` accordingly.
- Write a `tests/test_<phase>.py` alongside it, following the existing
  files' structure.

## When picking this project back up cold

1. Skim this file (you just did).
2. Check `pending-for-coding-and-testing.md` for what's open/proposed.
3. Check `menu-tree.md` for what's built vs. stub right now.
4. Run the test suite to confirm the baseline is green before changing
   anything.
