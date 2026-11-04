# Menu tree — where we are

Current structure of the CLI (`main.py`), as of commit `2c5ad6c`.
Legend: ✅ built & tested · 🟡 proposed, not yet built · ⬜ stub / undecided

```
Cyber Security Toolkit v1
│
├── 1. General Task                                  ✅ implemented
│     (phases/general_task.py — local box only, no remote target)
│     ├── 1. Update system & tools (apt update, confirm before upgrade) ✅
│     ├── 2. System & network info report (host/kernel/IPs/disk/uptime) ✅
│     ├── 3. Listening ports & active connections (ss, netstat fallback) ✅
│     ├── 4. File hash calculator (MD5/SHA1/SHA256)                    ✅
│     ├── 5. MAC address viewer / randomizer (macchanger, confirm first) ✅
│     ├── 6. Start/stop key services (postgresql, ssh — confirm first) ✅
│     └── 7. Session activity log (append timestamped note to activity.log) ✅
│
├── 2. Reconnaissance                                 ✅ implemented
│     (phases/reconnaissance.py — passive/OSINT, no auth prompt)
│     ├── 1. WHOIS lookup                             ✅
│     ├── 2. DNS enumeration (dig, falls back to socket) ✅
│     └── 3. Google dork builder (prints queries only)  ✅
│
├── 3. Scanning                                       ✅ implemented
│     (phases/scanning.py — nmap-backed, y/n auth confirm every run)
│     ├── 1. Host discovery (nmap -sn)                 ✅
│     ├── 2. Port scanning (nmap -sV)                  ✅
│     └── 3. Vulnerability scanning (nmap --script vuln) ✅
│
├── 4. Gaining Access                                 ✅ implemented
│     (phases/gaining_access.py — target + y/n auth confirm)
│     ├── 1. SQL injection test (error-based probe)    ✅
│     └── 2. Buffer overflow fuzzing (TCP)             ✅
│            (Phishing moved out to 7. Social Engineering — see below)
│
├── 5. Maintaining Access                             ⬜ stub
│     (phases/maintaining_access.py — not built)
│     Original phase table techniques: rootkits, hidden user accounts,
│     tunneling. Rootkits/hidden accounts intentionally dropped from
│     scope (see pending-for-coding-and-testing.md).
│     Proposed narrower submenu, awaiting your go-ahead:
│     └── 1. Tunneling (SSH -L/-R port-forward wrapper)  🟡
│
├── 6. Clearing Tracks                                ⬜ stub
│     (phases/clearing_tracks.py — not built)
│     Original phase table techniques: modifying/deleting logs.
│     Proposed narrower option, awaiting your go-ahead:
│     └── 1. Read-only log review (tail/grep, no modify/delete) 🟡
│
├── 7. Social Engineering                             ✅ implemented
│     (phases/social_engineering.py — local only, no target, no auth
│      prompt; everything is provision-only, see README.md)
│     Modeled on SET's menu structure + Zphisher's multi-template idea,
│     minus their live/attacking components.
│     ├── 1. Spear-phishing email template (4 templates)       ✅
│     ├── 2. Mock landing/login page (4 page styles)            ✅
│     ├── 3. Pretexting / vishing call script (3 scenarios)     ✅
│     ├── 4. USB-drop awareness briefing (no payload generated) ✅
│     ├── 5. QR code generator (for a URL you supply)           ✅
│     └── 6. Campaign log (tagged entry in activity.log)        ✅
│
└── 0. Exit                                           ✅
```

## Status summary

| Phase | Build status | Tests |
|---|---|---|
| 1. General Task | ✅ done | `tests/test_general_task.py` |
| 2. Reconnaissance | ✅ done | `tests/test_reconnaissance.py` |
| 3. Scanning | ✅ done | `tests/test_scanning.py` |
| 4. Gaining Access | ✅ done | `tests/test_gaining_access.py` |
| 5. Maintaining Access | not built — narrower proposal pending | — |
| 6. Clearing Tracks | not built — narrower proposal pending | — |
| 7. Social Engineering | ✅ done | `tests/test_social_engineering.py` |
| Menu loop itself | ✅ done | `tests/test_menu.py` |

54/54 tests passing as of the last push. See
`pending-for-coding-and-testing.md` for the full backlog and open
decisions behind each 🟡/⬜ item above.

Run `python3 main.py` to walk the live menu; this file is a static
snapshot and should be updated whenever a submenu is added or changed.
