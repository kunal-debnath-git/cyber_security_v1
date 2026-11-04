# Export / Import — moving this project to Kali-in-Termux

How to get code out of this cloud session, and how to bring it into
your real working environment: Kali Linux running inside Termux on
Android. Keep this file updated whenever the workflow changes (same
standing instruction as README.md / menu-tree.md /
pending-for-coding-and-testing.md).

## 1. Export (from this cloud session)

Everything here already lives on GitHub — that **is** the export path.
This session commits and pushes to:

```
Repo:   kunal-debnath-git/cyber_security_v1
Branch: main
```

Nothing further is needed from this side for a normal pull. If you
specifically want a one-off snapshot instead of a git history:

- **Zip of the current branch (no git needed on the other end):**
  on GitHub, Code → Download ZIP on the `main` branch, or:
  `https://github.com/kunal-debnath-git/cyber_security_v1/archive/refs/heads/main.zip`
- **Patch/diff instead of a full clone** (e.g. to review before
  applying): `git format-patch origin/main..HEAD` from a machine that
  already has the repo, or compare two commits on GitHub's compare
  view.

For day-to-day use, just pull — see below.

## 2. Import, test & validate on Kali-in-Termux

Termux on Android, not a full Linux install, so there are two setups
depending on what you've got:

- **A: plain Termux** — fine for the Python side (menu loop, hashing,
  tests) but most of the Kali *tools* the phases shell out to
  (`whois`, `dig`, `nmap`, `macchanger`, `apt`, `systemctl`) either
  aren't packaged for Termux or behave differently (no real `apt`, no
  `systemd`).
- **B: Kali inside Termux via `proot-distro`** (a Kali chroot) — closer
  to real Kali, has `apt`, and most of these tools install normally.
  `systemctl` still won't work (no systemd PID 1 in a chroot/proot
  environment) — see caveats below.

Use **B** if you want to exercise the toolkit close to how it'll behave
on a real Kali box. Use **A** only to run the Python test suite quickly.

### 2a. One-time setup

```bash
# In Termux itself
pkg update && pkg upgrade
pkg install git python proot-distro

# Get a Kali chroot (skip this block for setup A)
proot-distro install kali
proot-distro login kali
# you are now inside the Kali chroot for the rest of this section
apt update && apt install -y git python3 python3-pip \
    whois dnsutils nmap macchanger iproute2 net-tools
```

(`dnsutils` provides `dig`; `iproute2` provides `ip`/`ss`; on some
installs the package is `iproute2`, on others just check with
`apt search ip`.)

### 2b. Pull the code

```bash
git clone https://github.com/kunal-debnath-git/cyber_security_v1.git
cd cyber_security_v1
```

Already have a clone from before? Just update it:

```bash
cd cyber_security_v1
git pull origin main
```

### 2c. Run the automated tests

```bash
python3 -m unittest discover -s tests -v
```

Expect all tests to pass (41/41 as of the last review pass) regardless
of setup A or B — the tests are written to handle missing external
tools gracefully, so they don't require `nmap`/`whois`/etc. to be
installed to pass. A failure here means something broke in transit
(bad clone, wrong Python version) — check `python3 --version` (3.8+
expected) before digging further.

### 2d. Run the real menu and validate by hand

```bash
python3 main.py
```

Walk each implemented option (1–4) against something safe — your own
device/loopback, or a target you've separately confirmed you're
authorized to test — and confirm:

- **1. General Task** — info report and hashing should just work on
  either setup; update/services/MAC options need setup B (Kali chroot)
  and will report missing tools cleanly on setup A.
- **2. Reconnaissance** — WHOIS/DNS need `whois`/`dig` (setup B, or
  install them directly in plain Termux via `pkg install whois dnsutils`
  if available); the dork builder has no dependency, works either way.
- **3. Scanning / 4. Gaining Access** — need real network reachability
  from the phone (Wi-Fi/mobile data). `nmap` without root typically
  falls back to TCP connect scans rather than SYN scans — that's
  normal, not a bug. Every run still asks for the y/n authorization
  confirmation; answer only for a target you're actually authorized to
  test.

### 2e. Known Termux/proot-distro caveats

- **`systemctl` (General Task > service control) will not work** in a
  proot-distro chroot — there's no systemd PID 1 running. The command
  runs (binary exists) but fails with something like "System has not
  been booted with systemd". This is expected, not a bug in the code;
  `run_cmd()` reports it as a normal failure rather than crashing.
- **Raw sockets / SYN scans need root**, which a stock Termux/Android
  setup doesn't have. `nmap` degrades to connect-scan automatically;
  don't expect `-sS` to work.
- **MAC address randomization** (`macchanger -r`) generally needs a
  real network interface you control and often root — unlikely to
  succeed from a phone's Wi-Fi interface. Viewing MACs (`ip -brief
  link`) should still work.
- **File paths**: Termux's home is sandboxed (`/data/data/com.termux/files/home`,
  or `~` inside the proot chroot is separate again). `activity.log`
  and `phishing_templates/` land wherever you ran `python3 main.py`
  from — same rule as any other machine.

### 2f. Pushing changes back

If you make edits on the Kali-in-Termux side and want them back in
this project:

```bash
git add -A
git commit -m "describe the change"
git push origin main
```

You'll need a GitHub auth method set up in that Termux/Kali
environment (a personal access token is the simplest — `git` will
prompt for username/token on push, or configure a credential helper).
That's a one-time setup per device, not covered step-by-step here
since it depends on your GitHub account settings.
