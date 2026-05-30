# Onboarding (worker setup)

> **Status: STUB.** Full content lands in T9. This file documents the shape
> so anyone reading the repo today knows what's coming and where to find it
> later.

## What T9 will document

When a new worker joins, they need:

1. **Pi installed** on their machine
   - Pointer to the upstream `@earendil-works/pi-coding-agent` install docs
   - Recommended pi version (set when the manifest schema spec lands in T5)
2. **`HEXXU_WORKER_ID` generated and exported**
   - Command to generate a UUID v4 (`uuidgen` or `python3 -c "import uuid; print(uuid.uuid4())"`)
   - Where to put it (shell profile: `.bashrc`, `.zshrc`, or `.profile`)
   - How to verify (`echo $HEXXU_WORKER_ID`)
3. **`hexxu-skills-sync` extension installed**
   - Install command (depends on how T4 ships the extension; likely a pi
     extension registry pointer or a git URL)
   - Configuration: where the sync extension reads the registry URL from
     (constraint #3 — configurable, never hard-coded)
4. **`hexxu-telemetry` extension installed** (when T7 ships)
   - Same install pattern as above
   - Where the JSONL lands locally (likely `~/.hexxu/telemetry/`)
5. **First pi session verification**
   - Run `pi` once
   - Confirm `~/.pi/agent/skills/` populated from `hexxu-skills`
   - Confirm a JSONL line lands after exit

## Today (until T9 ships)

If you need to onboard a worker today (before the extensions exist):

1. Have them clone this repo manually: `git clone git@github.com:boldthemes/hexxu-skills.git ~/.pi/agent/skills-source`
2. Symlink: `ln -s ~/.pi/agent/skills-source/skills ~/.pi/agent/skills`
   (note: `skills/` directory inside this repo lands in T6 grandfather migration)
3. Set `HEXXU_WORKER_ID` in their shell profile:
   ```bash
   echo "export HEXXU_WORKER_ID=$(uuidgen)" >> ~/.bashrc
   source ~/.bashrc
   ```
4. They run pi. Skills load from the symlinked source. No telemetry yet.

This is the manual fallback for worker #1 (you) bootstrapping the system.
T9 replaces it with documented automation.

## When `hexxu-onboarding-cli` exists (deferred to TODOS)

The CEO plan deferred building a `npx hexxu` onboarding CLI until worker #2
joins. That CLI will collapse the steps above into a single command. The
trigger for building it is "second worker about to onboard" — see TODOS.md.

## Identity rotation

If a worker's UUID is compromised, lost, or otherwise needs replacement:

1. Generate a new UUID and update `HEXXU_WORKER_ID` in their shell profile.
2. The old UUID is **dead** — telemetry attributed to it stays attributed
   to it (no migration). Treat the old UUID as a former worker.
3. If the worker authored skills with `owner: <old-uuid>` in frontmatter,
   update those entries in a PR titled `chore: rotate owner UUID for @<handle>`.
4. Do NOT cross-link old and new UUIDs anywhere. The audit story stays clean.

This applies to the rare case; most workers will have a single stable UUID
for the duration of their tenure.
