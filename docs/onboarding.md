# Onboarding (worker setup)

From zero to a worker pi-session that syncs central skills and logs
telemetry locally. Today this is a manual ~5-minute setup; a deferred
`hexxu` onboarding CLI will collapse it into one command (revival trigger:
worker #2 about to join).

## What a worker gets

After the steps below:

- **Skills auto-sync** from this repo into `~/.pi/agent/skills/central/` on
  every pi `session_start`, non-blocking, with a 5-minute staleness cache
- **Telemetry** lands at `~/.hexxu/telemetry/telemetry.jsonl` (mode 0600 on
  POSIX/WSL; on Git Bash the mode is a no-op and privacy rides on your
  `%USERPROFILE%` ACL — see the Windows section), local-only, append-only,
  rotates at 50 MB or 90 days
- **CLI** `hexxu-telemetry-summary` available on `PATH` to roll up the
  telemetry by skill / exit reason / duration percentile
- **Identity** scoped via `HEXXU_WORKER_ID`, an env var carrying the
  worker's UUID v4 across all hexxu tooling

## Platform: Windows workers

> **Skip this section if your machine is Linux or macOS** — go straight to
> Prerequisites.

Pi itself [requires a bash shell on
Windows](https://github.com/earendil-works/pi-coding-agent) and finds one
in this order: a custom `shellPath` in `~/.pi/agent/settings.json`, then
**Git Bash** (`C:\Program Files\Git\bin\bash.exe`), then any `bash.exe` on
`PATH` (Cygwin / MSYS2 / WSL). The hexxu worker stack also leans on a POSIX
environment — a bash, real symlinks (the central-skills mount), and Unix
file modes (`0600` on the telemetry log). You have two supported ways to
provide that, and you run every command in this doc inside whichever bash
you pick:

### Option 1 — Git Bash (recommended; matches pi's default)

Install [Git for Windows](https://git-scm.com/download/win) — that's it for
the shell. Pi auto-discovers Git Bash, so there's nothing to configure
(point pi at it explicitly with a `shellPath` setting only if you installed
Git somewhere non-standard). Then install **Node 24+** for Windows and pi
per the Prerequisites below, and run all steps from the **Git Bash** prompt.

The two extensions handle Windows transparently:

- The skills mount uses a **directory junction** instead of a symlink, so it
  needs no Admin / Developer Mode.
- The telemetry log's `0600` mode is a no-op on NTFS; its privacy instead
  rides on your per-user `%USERPROFILE%` ACL (the file lives under
  `~/.hexxu`, inside your profile). This is fine for a single-user desktop —
  see the note in Step 4. If you need a hard owner-only guarantee, use WSL.

> **One env-var caveat:** `HEXXU_WORKER_ID` (Step 1) goes in Git Bash's
> `~/.bashrc`, so it's only visible to processes launched **from Git Bash**.
> Start pi from the Git Bash prompt, not a desktop shortcut or PowerShell,
> or the telemetry extension won't see your worker ID.

### Option 2 — WSL (optional; full POSIX guarantees)

Run the entire stack inside WSL (Windows Subsystem for Linux) for a real
Linux environment — real symlinks and a real owner-only `0600` telemetry
mode. Choose this if the profile-ACL story above isn't enough for you.

1. **Install WSL with Ubuntu** (elevated PowerShell): `wsl --install -d Ubuntu`,
   reboot if prompted, launch **Ubuntu**, create your Linux user.
2. **Install git + Node 24+ inside Ubuntu:**

   ```bash
   sudo apt update && sudo apt install -y git
   curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
   sudo apt install -y nodejs
   ```
3. **Install pi inside WSL** per the Prerequisites below.

> **Keep everything in the WSL filesystem, not `/mnt/c/`.** Clone under your
> Linux home (`~/Development/...`), never a Windows drive at `/mnt/c/...` —
> on `/mnt/c` symlinks need elevation and Unix modes are ignored, which
> defeats the whole point of using WSL. Inside `~` (ext4) both work.

From here on, run every command inside your chosen bash, and `~` means that
shell's home.

## Prerequisites

> **Windows workers:** pick a shell in the section above first (Git Bash or
> WSL), then run all of the following from that bash.

- **Pi installed** — see [@earendil-works/pi-coding-agent install
  docs](https://github.com/earendil-works/pi-coding-agent). Recommended pi
  version: 0.78.x or newer. Verify with `pi --version`.
- **GitHub access** — this repo is public, so any read path works
  (`https://github.com/boldthemes/hexxu-skills.git`). No auth needed for
  sync.
- **Node 24+** — required for `--experimental-strip-types` (the CLI runs as
  TS directly, no build step). On Git Bash this is Node for Windows; on WSL
  it's the Linux Node installed above.
- **git** — for cloning the platform repo (Step 2). Bundled with Git for
  Windows (Option 1) or installed inside WSL (Option 2).

## Step 1 — Generate and export `HEXXU_WORKER_ID`

Every worker has a stable UUID v4 that travels with them across machines.
Constraint #7 (see [CLAUDE.md](../CLAUDE.md)).

```bash
# Generate a fresh UUID v4 (pick the line that works in your shell)
WORKER_ID=$(uuidgen | tr 'A-Z' 'a-z')                        # POSIX / WSL
# Git Bash (no uuidgen bundled; openssl is) — synthesize a v4:
# WORKER_ID=$(openssl rand -hex 16 | sed -E 's/^(.{8})(.{4}).(.{3}).(.{3})(.{12})$/\1-\2-4\3-8\4-\5/')
# Or, in any shell with Python: WORKER_ID=$(python3 -c "import uuid; print(uuid.uuid4())")
echo "Your HEXXU_WORKER_ID is: $WORKER_ID"

# Add it to your shell profile (pick the right one for your shell)
echo "export HEXXU_WORKER_ID=$WORKER_ID" >> ~/.bashrc
# or ~/.zshrc, ~/.profile, etc.

# Activate for this session too
export HEXXU_WORKER_ID=$WORKER_ID
```

**Verify:**

```bash
echo $HEXXU_WORKER_ID
# Expect: a UUID v4 like 8f3e9d2c-1b4a-4f7e-9c8d-2a1b3c4d5e6f
```

**Save this UUID** somewhere safe — your password manager, a notes app, a
text file. Recovering it later is hard once your shell profile is gone, and
losing it means your historical telemetry can't be re-attributed to you
(the rotation policy below makes the old UUID a former worker, period).

## Step 2 — Clone the hexxu platform repo

The pi extensions, the CLI, and the prompt templates live in
[boldthemes/hexxu](https://github.com/boldthemes/hexxu) (the platform
repo; paired with this repo which holds skill content). Clone it
somewhere stable on your machine:

```bash
git clone git@github.com:boldthemes/hexxu.git ~/Development/hexxu
# Or clone via HTTPS if you don't have SSH access set up:
# git clone https://github.com/boldthemes/hexxu.git ~/Development/hexxu
```

You'll reference this clone in Steps 3-5. The path is yours to choose;
`~/Development/hexxu` is the convention.

## Step 3 — Install the `hexxu-skills-sync` pi extension

The sync extension pulls this repo into `~/.pi/agent/skills/central/` on
every pi session start.

```bash
mkdir -p ~/.pi/agent/extensions
cp -r ~/Development/hexxu/.pi/extensions/hexxu-skills-sync \
  ~/.pi/agent/extensions/hexxu-skills-sync
```

Pi auto-discovers extensions in `~/.pi/agent/extensions/`. No registration step.

**Verify the directory structure:**

```
~/.pi/agent/extensions/hexxu-skills-sync/
├── index.ts
└── README.md
```

**Optional configuration** (env vars; defaults are sensible):

| Var | Default | Notes |
|---|---|---|
| `HEXXU_SKILLS_URL` | `https://github.com/boldthemes/hexxu-skills.git` | Constraint #3: configurable |
| `HEXXU_SKILLS_CACHE_DIR` | `~/.hexxu/skills-cache` | Local clone target |
| `HEXXU_SKILLS_MOUNT` | `~/.pi/agent/skills/central` | Symlink target |
| `HEXXU_SKILLS_STALENESS_S` | `300` | Min seconds between automatic syncs |
| `HEXXU_SKILLS_DISABLED` | (unset) | Set to `1` to skip sync entirely |

See `~/.pi/agent/extensions/hexxu-skills-sync/README.md` for the full
behavior matrix.

## Step 4 — Install the `hexxu-telemetry` pi extension

The telemetry extension captures one JSONL record per pi session at
`session_shutdown`. Local-only. Same install pattern:

```bash
cp -r ~/Development/hexxu/.pi/extensions/hexxu-telemetry \
  ~/.pi/agent/extensions/hexxu-telemetry
```

Without `HEXXU_WORKER_ID` set (Step 1), this extension WARNs once per
session and skips writing — set the env var first.

See `~/.pi/agent/extensions/hexxu-telemetry/README.md` for the locked
schema and rotation policy.

## Step 5 — Install the `hexxu-telemetry-summary` CLI

The CLI reads `~/.hexxu/telemetry/telemetry.jsonl` and prints a rollup. Recommended for daily-driver use; without it you have telemetry data but no view into it.

Install a small wrapper that invokes the CLI via `node`. This works
identically on POSIX and Git Bash — it avoids both the `env -S` shebang
(not portable to Git Bash) and a file symlink (needs elevation on Windows),
and it still tracks the live `.ts` in your clone, so `git pull` updates the
CLI behavior. If you cloned hexxu somewhere other than `~/Development/hexxu`,
edit the path in the wrapper.

```bash
mkdir -p ~/.hexxu/bin
cat > ~/.hexxu/bin/hexxu-telemetry-summary <<'EOF'
#!/usr/bin/env bash
exec node --experimental-strip-types "$HOME/Development/hexxu/cli/telemetry-summary.ts" "$@"
EOF
chmod +x ~/.hexxu/bin/hexxu-telemetry-summary

# Add ~/.hexxu/bin to PATH (one-time)
echo 'export PATH="$HOME/.hexxu/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Verify:**

```bash
hexxu-telemetry-summary -h
# Expect: usage banner
```

See `~/Development/hexxu/cli/README.md` for full CLI docs (or browse it on GitHub: [boldthemes/hexxu/cli/README.md](https://github.com/boldthemes/hexxu/blob/main/cli/README.md)).

## Step 6 — First-session verification

Start a pi session in any directory, ask it a trivial question, exit:

```bash
pi
> What's 2 + 2?
> /quit
```

Then check:

```bash
# 1. The central skills should be mounted
ls ~/.pi/agent/skills/central/
# Expect: 5 directories (csv-to-markdown-converter, karpathy-guidelines,
# meeting-action-items, pi-docs-map, skill-creator)

# 2. The sync state should show a recent successful sync
cat ~/.hexxu/skills-sync-state.json
# Expect: { "last_sync_status": "success", ... }

# 3. The telemetry log should have one record
hexxu-telemetry-summary --since 1h
# Expect: "Sessions in period: 1" + details

# 4. The telemetry file should be mode 0600 (POSIX / WSL only)
ls -la ~/.hexxu/telemetry/telemetry.jsonl
# Expect on POSIX/WSL: -rw------- (only you can read)
# On Git Bash: the mode bits are not meaningful on NTFS; privacy rides on
# your %USERPROFILE% ACL instead (see the Windows section). Skip this check.
```

If any of these don't show what's expected, see the troubleshooting
section below.

## Troubleshooting

### `hexxu-skills-sync: HEXXU_WORKER_ID is not set` warning

Step 1 wasn't applied. Run `echo $HEXXU_WORKER_ID` — if empty, your shell
profile didn't get re-sourced. Restart your terminal or run
`source ~/.bashrc` (or wherever you added the export).

### Sync output says `cold-start failed; starting with no central skills`

The first git clone couldn't reach GitHub. Check:
- Network: `curl -I https://github.com/boldthemes/hexxu-skills.git` should return 200/301
- Proxy: if you're behind a corporate proxy, set `HTTPS_PROXY` in your shell
- The constraint #5 fail-open semantics mean pi still works without central
  skills — just nothing in `~/.pi/agent/skills/central/`

### `~/.pi/agent/skills/central/` exists but isn't a symlink

You had real files there before installing the sync extension. The
extension refuses to destroy non-symlink content. Move your existing files
elsewhere (or delete the dir), then run `/sync-skills` in pi (or wait for
the next session) to re-create the mount. (On Windows the mount is a
directory **junction**, which `lstat` reports as a symlink — same handling.)

### (Git Bash) `hexxu-telemetry-summary: command not found` or wrong worker ID

Both come from the env-var / PATH living only in Git Bash's `~/.bashrc`.
Confirm you launched pi **from the Git Bash prompt** (not PowerShell, cmd,
or a desktop shortcut), then `source ~/.bashrc` or restart the Git Bash
terminal. See the "One env-var caveat" note in the Windows section.

### (WSL) Sync junction/symlink fails or telemetry file isn't mode 0600

You almost certainly cloned into `/mnt/c/...` (a Windows drive) instead of
your WSL home. On `/mnt/c` real symlinks need Admin/Developer Mode and Unix
file modes are ignored, so the central-skills mount and the `0600`
telemetry permission both break. Move everything under `~` (e.g.
`~/Development/hexxu`) inside the Ubuntu shell and re-run the affected
steps. See Option 2 in the Windows section.

### Telemetry file is empty after a session

- Is `HEXXU_WORKER_ID` set? (`echo $HEXXU_WORKER_ID`)
- Is `HEXXU_TELEMETRY_DISABLED` set? (`echo $HEXXU_TELEMETRY_DISABLED`)
- Did the session crash mid-way? `session_shutdown` doesn't fire on SIGKILL.

### `pi --print` mode telemetry shows `skills=0` but I used skills

Pi's `--print` (non-interactive) mode disables tools unless you pass
`--tools`. With tools disabled, no SKILL.md reads happen, so `skills_invoked`
is empty. Use interactive mode for a meaningful test.

## Identity rotation

If your `HEXXU_WORKER_ID` is compromised, lost, or otherwise needs
replacement:

1. Generate a new UUID v4 and update `HEXXU_WORKER_ID` in your shell
   profile.
2. The old UUID is **dead** — telemetry attributed to it stays attributed
   to it (no migration). Treat the old UUID as a former worker.
3. If you authored skills with `owner: <old-uuid>` in frontmatter, update
   those entries in a PR titled `chore: rotate owner UUID for @<handle>`.
4. Do NOT cross-link old and new UUIDs anywhere. The audit story stays
   clean (constraint #7 rotation policy).

This applies to the rare case; most workers will keep one stable UUID for
the duration of their tenure.

## When `hexxu-onboarding-cli` ships (deferred to TODOS)

The CEO plan deferred building a `npx hexxu` onboarding CLI until worker #2
is about to join. That CLI will collapse Steps 1-4 above into one command:

```bash
npx hexxu onboard   # generates UUID, installs extensions, installs CLI,
                    # configures shell profile
```

The deferred-eval-gate revival trigger is the same: when `CONTRIBUTORS.md`
gains a second entry, both the onboarding CLI and the eval-gate become
in-scope. Until then, this manual flow is the canonical path.

## What you do NOT need on a worker machine

- npm/yarn/pnpm (no build step; everything runs via `node
  --experimental-strip-types`)
- A package.json (each pi extension is self-contained)
- A GitHub token for read access (both `hexxu-skills` and `hexxu` are public)
- The full pi source tree (`pisource/` is gitignored in `boldthemes/hexxu`; clone it separately if you want it as a reference)
- The full hexxu-skills repo (the sync extension fetches it on its own — you can clone it for local browsing but the worker doesn't need a manual clone)
