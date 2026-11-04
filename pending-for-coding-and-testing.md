# Pending — coding & testing backlog

Open items for this project, as of commit `8950ae4`. These are things
I'd like to build or revisit next; none are started yet unless noted.

**Standing instruction:** README.md, menu-tree.md,
export-import.md and this file get updated together with every
feature change, not just when asked.

## ~~General Task (menu option 1)~~ — done

Implemented in `phases/general_task.py`: update system & tools, system/
network info report, listening ports, file hash calculator, MAC
viewer/randomizer, service start/stop, session activity log. See
README.md and menu-tree.md for details. Tests in
`tests/test_general_task.py` (41/41 total passing).

## 1. Maintaining Access (menu option 5)

Currently a stub. The original phase table lists "Installing rootkits,
Creating hidden user accounts, Tunneling" as its techniques. I stopped
short of building any of these — including softened versions (a
persistence-detection report, a double-confirmed account-creation
flow) — after running into a content-safety stop while writing that
module, and I'm not going to re-approach rootkit/hidden-account content
under a different framing.

**What I'd like to build instead, if you want this option to do
anything:**
- **Tunneling only** — an SSH local/remote port-forward wrapper
  (`ssh -L`/`-R`) around a host you already have legitimate login
  access to. This is a normal admin/pentest technique, not an
  exploit, and fits the existing "target + y/n authorization" pattern
  already used in Scanning and Gaining Access.
- Leave "Installing rootkits" and "Creating hidden user accounts" out
  of this tool entirely rather than implemented in any form.

Needs your go-ahead before I write it.

## 2. Clearing Tracks (menu option 6)

Currently a stub. The phase table lists "Modifying log files, Deleting
evidence of unauthorized access." I haven't attempted this one yet.

**What I'd like to build, if anything:**
- A **read-only log review helper** only — e.g. tail/grep a log file
  you point it at for suspicious entries (your own authorized box) —
  with no delete/modify capability at all.
- Alternative: leave this stub as-is and not build it.

I'd lean toward the read-only version or leaving it as a stub, not an
actual log-modification/deletion feature, even gated — needs your call.

## 3. Smaller follow-ups (lower priority, not blocking)

- `phases/gaining_access.py`'s SQL injection probe is a simple
  error-string check only (no boolean-based/time-based detection). Fine
  for v1; could be extended later if you want more coverage.
- No automated linting (flake8/pylint) wired up yet — currently just
  `python3 -m unittest discover -s tests`. Could add a lint step if
  useful.
- No `requirements.txt`/packaging — intentional, since the project is
  stdlib-only by design; flag if that changes.
- Scope/authorization prompts (`utils.confirm`) are not logged
  automatically anywhere. General Task > Session activity log
  (`activity.log`) covers manual notes you type in, but nothing writes
  to it on its own — a y/n confirm in Scanning/Gaining Access doesn't
  auto-record itself. Could wire that up if you want every confirmed
  run captured without typing a note each time.

## How to use this file

Tell me which of the above you want built, and I'll move it from here
into the actual `phases/` modules + tests + README, the same way
Reconnaissance/Scanning/Gaining Access were done. I'll keep this file
updated as items get picked up or dropped.
