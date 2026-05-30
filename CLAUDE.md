# CLAUDE.md — hexxu-skills

Instructions for any AI agent (Claude Code, pi, Codex, others) working in this
repository. Read this whole file before authoring or revising skills here.

This repo is the **central skill registry for the hexxu central brain**. Workers'
pi installations sync from here on session start. Every change ships to every
worker on their next pi session. Behave accordingly.

---

## The seven design constraints (load-bearing — read carefully)

These constraints exist so the A (this repo) → B (federation via SaaS) → C
(self-hosted Hexxu platform) trajectory stays open. Violating them does not
break today's runtime — it bakes in cleanup work that surfaces 12-24 months
from now during migration. Treat them as non-negotiable.

### 1. Skill versioning lives in SKILL.md frontmatter, not in git tags

Every skill MUST carry a `version` field in its frontmatter (semver). Workers
read the frontmatter to know what version they have. Git tags are convenient
but break the moment we move to a non-git skill registry.

### 2. Worker identity is session-scoped, not skill-scoped

Skills MUST NOT read identity from `git config user.*`, `whoami`, `$USER`,
`$LOGNAME`, or any other ad-hoc source. Identity comes from `HEXXU_WORKER_ID`
(see constraint #7) and ONLY that. This is enforced by
`.github/workflows/identity-drift.yml` (lands in T3).

### 3. Skill registry URL is configurable in pi config; never hard-coded

Workers' pi config points at this repo via a configurable URL. The pi extension
`hexxu-skills-sync` (lands in T4) reads that config; it never hard-codes
`github.com/boldthemes/hexxu-skills`. When we eventually move to a custom
registry service, only the URL changes.

### 4. Skill manifest schema (authoritative spec)

Every skill's frontmatter MUST carry these fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | matches the directory basename, lowercase + hyphens |
| `description` | string ≤ 1024 chars | yes | drives pi's trigger detection (routing-model facing) |
| `version` | semver string | yes | constraint #1 |
| `owner` | UUID | yes | matches a `HEXXU_WORKER_ID`; constraint #2/#7 |
| `last_reviewed` | ISO date | yes | enables skill-rot detection |
| `scope` | string 30–512 chars | yes | one-sentence positive statement; reviewer-facing anchor (T15) |
| `non_goals` | array of 2–8 strings | yes | explicit anti-scope; routing-margin CI tests against these (T15) |
| `supersedes` | array of skill names | no | when set, superseded skill dir MUST be deleted in same PR (T15) |
| `requires` | array of `extension:<name>` / `data:<scope>` strings | no | foreshadows the dependency surface for pillars 2 & 3 |

The full spec with examples lives in `docs/manifest-schema.md` (lands in T5).

### 5. Offline-first

Workers MUST keep working when this repo is unreachable. `hexxu-skills-sync`
falls back to cached skills with a visible warning. Cold-start (no cache yet
+ GitHub unreachable) falls open with empty skills, never blocks the pi
session.

### 6. Permission checks happen in extensions at the data layer

Skills do not authorize. Skills do not check roles. When a skill needs data
(via `requires: data:postgres:hexxu_main`), the extension that exposes that
data layer performs the authorization. This keeps the skill content portable
and the permission model swappable.

### 7. Identity contract: `HEXXU_WORKER_ID`

- **Format:** UUID v4
- **Source:** `HEXXU_WORKER_ID` env var, injected by the worker's shell
  profile (onboarding doc in `docs/onboarding.md`, lands in T9)
- **Visibility:** every pi extension and skill that needs identity reads it
  from this single env var
- **Rotation policy:** a compromised or replaced UUID = a new worker. Old
  telemetry stays bound to the old UUID, no cross-linking. No "rename" or
  "merge" semantics.
- **Portability:** the same UUID travels with the worker across machines

---

## Repo conventions

### Skill layout

```
skills/
  <skill-name>/
    SKILL.md       # frontmatter + body
    references/    # optional, lazy-loaded by pi
    scripts/       # optional helper scripts
    assets/        # optional templates / static files
    evals/         # optional eval prompts (mandatory once eval-gate is revived)
```

`<skill-name>` is lowercase + hyphens, ≤ 64 chars, matches the `name`
frontmatter field. No leading/trailing/consecutive hyphens.

### Frontmatter (canonical example)

```markdown
---
name: meeting-action-items
description: Extracts action items with owners from meeting transcripts. Use when the user pastes a transcript and asks for next steps.
version: 0.1.0
owner: 8f3e9d2c-1b4a-4f7e-9c8d-2a1b3c4d5e6f
last_reviewed: 2026-05-30
requires:
  - extension:hexxu-telemetry
---
```

### Branch / PR workflow

- All changes go through PRs (branch protection on `main`)
- Required: 1 approving review (you can self-review while solo; this changes
  when `CONTRIBUTORS.md` has > 1 entry — see eval-gate revival in TODOS)
- Branch names: `<task-id>-<short-slug>` (e.g. `t2-docs-scaffold`)
- Commit messages: imperative mood, reference the task (`chore: T2 docs scaffold`)

### CI checks (today + planned)

- **identity-drift** (T3): fails if any skill code matches `git config user\.`,
  `\bwhoami\b`, `\$USER`, `\$LOGNAME`. Constraint #2 enforcement.
- **eval-gate** (deferred to TODOS; revived when `CONTRIBUTORS.md` has > 1
  entry): runs the skill-creator eval suite; skill must score ≥ 0.8 averaged
  across 3 deterministic seeded runs.

---

## When authoring a skill in this repo

1. Use `pi-skill-creator` from Claude Code, or the pi-side `skill-creator`
   from interactive pi, to draft frontmatter and body.
2. Name the skill directory after the `name` field exactly.
3. Fill in all six required frontmatter fields.
4. Write at minimum a small `evals/evals.json` with 2-5 realistic prompts
   (mandatory once eval-gate revives; optional but recommended today).
5. Run the existing pi-side skill-creator pipeline locally to validate
   (`/skill-run-evals` in pi).
6. Open a PR against `main`. Get 1 approving review. Merge.

## When revising an existing skill

1. Bump the `version` field (semver).
2. Update `last_reviewed` to today's date.
3. If the skill's behavior changed in a way workers will notice, also update
   the description.
4. Same PR workflow.

## Anti-patterns

- Adding `tools:`, `permissions:`, `mcp:` or other Claude-Code-specific
  frontmatter fields — pi parses but ignores them; they pollute the file.
- Referencing identity sources other than `HEXXU_WORKER_ID` in skill code.
- Hard-coding the registry URL anywhere.
- Stuffing every detail into SKILL.md — spill detail into `references/`.
- Shipping a skill without bumping `version` or updating `last_reviewed`.

---

## Where to learn more

- `docs/architecture.md` — system shape, A→B→C trajectory, constraint rationale
- `docs/manifest-schema.md` — full frontmatter spec with examples (lands in T5)
- `docs/onboarding.md` — `HEXXU_WORKER_ID` setup for new workers (lands in T9)
- `docs/extension-authoring.md` — pi extension patterns used by `hexxu-skills-sync` and `hexxu-telemetry`
- `CONTRIBUTORS.md` — current contributors + eval-gate revival trigger
- `TODOS.md` — deferred work with explicit revival triggers (populated by T11)

The original CEO plan that produced this repo lives at
`/home/macak/Development/hexxu/docs/designs/central-brain.md` in the parent
project (untracked until hexxu's git is re-enabled).
