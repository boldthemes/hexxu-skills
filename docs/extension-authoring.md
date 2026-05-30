# Extension Authoring (pi extensions for hexxu)

> **Status: STUB.** Full content lands as `hexxu-skills-sync` (T4) and
> `hexxu-telemetry` (T7) are built. This file documents the shape so
> developers can preview the patterns before the reference implementations
> exist.

## What lives in extensions (vs. skills)

Skills (markdown files in this repo) describe what pi should do.
**Extensions** (TypeScript code in the hexxu project, NOT in this repo)
extend pi's tool surface and lifecycle hooks. Examples in the hexxu
trajectory:

| Extension | Purpose | Status |
|---|---|---|
| `hexxu-skills-sync` | Pulls this repo into `~/.pi/agent/skills/` on session start | T4 |
| `hexxu-telemetry` | Listens for `session_shutdown`, writes JSONL | T7 |
| (Phase B) `hexxu-postgres` | Exposes a postgres tool, enforces ACLs by `HEXXU_WORKER_ID` | deferred |
| (Phase B) `hexxu-files` | Reads from Drive/Notion/S3 backends | deferred |

## Where extension code lives

**Not in this repo.** This repo is the **skill registry**. Extensions
live in the parent project, currently at:

```
/home/macak/Development/hexxu/.pi/extensions/<extension-name>/index.ts
```

The split is intentional: skills are content workers pull on every session;
extensions are code workers install once. Mixing them would conflate the
two release cadences.

## Patterns extensions in hexxu MUST follow

1. **Read identity from `HEXXU_WORKER_ID` env var only.** Never from
   `git config user.*`, `whoami`, `$USER`, or any other ad-hoc source.
   Constraint #2.
2. **Non-blocking on degraded state.** If the extension can't do its job
   (network down, missing env var, broken config), it WARNs to stderr and
   returns. It never blocks the pi session start. Constraint #5.
3. **No hard-coded URLs or paths.** Anything site-specific reads from
   pi config or environment. Constraint #3.
4. **Permissions in the data layer.** If an extension exposes data
   (postgres, files, etc.), it authorizes by `HEXXU_WORKER_ID` at the
   extension boundary, not inside skills. Constraint #6.
5. **Forward-compatible artifacts.** Telemetry JSONL, sync state files, etc.
   add new fields as needed but never remove existing fields without a
   bumped extension version.

## Reference patterns (from existing hexxu extensions)

Three precedents already exist in `.pi/extensions/` of the hexxu project:

- `.pi/extensions/skill-creator/` — heavy extension with slash commands,
  typed tools, persisted state, SDK script invocation
- `.pi/extensions/git/` — simple wrapper around git operations
- `.pi/extensions/npm/` — simple wrapper around npm operations

`hexxu-skills-sync` (T4) and `hexxu-telemetry` (T7) are sized between
these — bigger than git/npm wrappers, smaller than skill-creator. Study
the skill-creator extension for state persistence patterns; study git/npm
for the minimum viable shape.

## Testing extensions

Until the test harness pattern is locked, expect each extension to ship
with:

- Unit tests for pure functions (env-var parsing, JSONL formatting, etc.)
- One integration test that boots a mock pi session and asserts the
  extension's lifecycle hooks fire correctly
- The end-to-end acceptance criteria in T10 cover sync + telemetry
  together

## Open questions for T4/T7

- Where do hexxu extensions get distributed? Same git URL pattern as the
  skills registry, or via npm packages, or both?
- How do workers discover available hexxu extensions? Manual install
  command in `docs/onboarding.md`, or auto-install via an aggregator?
- Do extensions declare their pi-version compatibility in `requires`-style
  metadata? (Mirrors constraint #4 for skills.)

These get resolved as T4 and T7 build the reference implementations. This
file gets updated then to document the answers.
