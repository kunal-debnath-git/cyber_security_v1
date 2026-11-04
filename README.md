# cyber_security_v1

A CLI-menu-driven toolkit that walks through the five classic
ethical-hacking phases. Python 3 standard library + bash, built to run
on Kali Linux (uses Kali's own tools: `whois`, `dig`, `nmap`, ...).

No GUI, no web interface — menu only.

## Status: v1, in progress

| # | Menu item          | Status                                   |
|---|---------------------|-------------------------------------------|
| 1 | General Task        | **implemented** — update, info report, ports, hashing, MAC tools, services, activity log |
| 2 | Reconnaissance      | **implemented** — WHOIS, DNS enum, dork builder |
| 3 | Scanning            | **implemented** — host discovery, port scan, vuln scan (nmap) |
| 4 | Gaining Access      | **implemented** — SQLi probe, buffer overflow fuzzer, phishing *template provisioning only* |
| 5 | Maintaining Access  | stub — intentionally not built (rootkit/persistence/hidden-account content out of scope for this tool) |
| 6 | Clearing Tracks     | stub (not yet built) |

## Run it

```bash
python3 main.py
```

## Run the tests

```bash
python3 -m unittest discover -s tests -v
```

## Layout

```
main.py                   menu loop (options 1-6, 0 = Exit)
utils.py                  shared helpers: run external tools safely,
                           yes/no confirm prompt, text prompt
phases/
  general_task.py         1. General Task (update / info / ports / hash / MAC / services / log)
  reconnaissance.py       2. Reconnaissance (WHOIS / DNS / dork builder)
  scanning.py             3. Scanning (nmap: discovery / ports / vuln)
  gaining_access.py       4. Gaining Access (SQLi probe / BOF fuzzer / phishing templates)
  maintaining_access.py   5. Maintaining Access (stub)
  clearing_tracks.py      6. Clearing Tracks (stub)
tests/                    unittest suite, one file per module
```

## Phase reference

The five implemented/planned phases and the techniques each maps to:

| Phase | Description | Techniques Used |
|---|---|---|
| Reconnaissance | Gathering information about the target to identify potential vulnerabilities. | Google Dorking, WHOIS lookups, DNS enumeration, Social engineering tactics |
| Scanning | Using tools to identify vulnerabilities in the target through various scans. | Network mapping, Port scanning, Vulnerability scanning |
| Gaining Access | Attempting to exploit identified vulnerabilities to gain unauthorized access. | SQL injection, Buffer overflow attacks, Phishing attacks |
| Maintaining Access | Establishing a persistent connection to assess duration of undetected access. | Installing rootkits, Creating hidden user accounts, Tunneling |
| Clearing Tracks | Removing traces of activity from system logs. | Modifying log files, Deleting evidence of unauthorized access |

## General Task (option 1)

Kali housekeeping utilities, not tied to a target:

1. Update system & tools (`apt update`, then confirm before `apt upgrade -y`)
2. System & network info report (hostname, kernel, uptime, disk, interfaces)
3. Listening ports & active connections (`ss -tulpn`, falls back to `netstat`)
4. File hash calculator (MD5/SHA1/SHA256, stdlib `hashlib`)
5. MAC address viewer / randomizer (`ip link`, optional `macchanger -r`)
6. Start/stop key services — `postgresql` (Metasploit DB), `ssh` (confirm first)
7. Session activity log — appends a timestamped note to `activity.log`

## Authorization

- **Reconnaissance** is passive/OSINT only (public WHOIS/DNS records, a
  dork string builder that prints queries but makes no requests), so it
  runs without a confirmation prompt.
- **Scanning** sends packets at the target, so every run asks you to
  confirm you own or are authorized to test the target before it runs
  `nmap`.
- **Gaining Access** (SQLi probe, buffer-overflow fuzzer) takes a target
  at run time and asks the same y/n authorization confirmation first.
  Its "Phishing attacks" option is deliberately *provision only*: it
  writes local email/page template files for an internal awareness
  exercise and never sends anything or contacts a server.
- **Maintaining Access** and **Clearing Tracks** are not built. Rootkit
  installation, hidden-account creation, and log tampering are out of
  scope for this tool rather than being built with extra gating.

Only use this against systems you own or are explicitly authorized to
test.

## Requirements

Stdlib-only Python, plus these Kali command-line tools when you use the
matching submenu (each is checked for and reported as missing rather
than crashing if absent):

- `whois` — WHOIS lookups
- `dig` — DNS enumeration (falls back to Python's `socket` for an A
  record if `dig` isn't installed)
- `nmap` — host discovery, port scanning, vulnerability scanning
- `apt` — Update system & tools (standard on Kali/Debian-based systems)
- `ip` — system/network info report, MAC address viewer (falls back to
  Python's `socket` for the local IP if `ip` isn't installed)
- `ss` — listening ports (falls back to `netstat` if `ss` isn't installed)
- `macchanger` — MAC address randomization (viewing MACs works without it)
- `systemctl` — starting/stopping the `postgresql`/`ssh` services
- `uptime` — shown in the system/network info report (skipped if absent)

File hashing (MD5/SHA1/SHA256) needs no external tool — it uses
Python's stdlib `hashlib`.

Generated at runtime, not part of the source (ignored by git):
`activity.log` (Session activity log notes), `phishing_templates/`
(Phishing provision-only output).
