# hexxu-skills

Central skill registry for the **hexxu** central brain. Workers' pi installations sync skills from this repo; developers author and revise skills via Claude Code or pi.

Owned by [@boldthemes](https://github.com/boldthemes).

## What lives here

- `skills/<name>/SKILL.md` — pi skills loaded into every worker's `~/.pi/agent/skills/`
- `docs/` — manifest schema, architecture, onboarding, extension authoring
- `CONTRIBUTORS.md` — contributor list; **trigger:** when this file has more than one entry, the eval-gate TODO in `TODOS.md` becomes mandatory
- `TODOS.md` — deferred work with explicit revival triggers
- `.github/workflows/identity-drift.yml` — CI check enforcing constraint #2 (no ad-hoc identity sources in skill code)

## Plan & status

The shape of this repo, its constraints, and the multi-year trajectory are documented in:

- [`docs/architecture.md`](docs/architecture.md) — the seven design constraints (file lands in T2)
- [`docs/manifest-schema.md`](docs/manifest-schema.md) — skill frontmatter authoritative spec (file lands in T5)
- [`docs/onboarding.md`](docs/onboarding.md) — `HEXXU_WORKER_ID` setup + first-time worker flow (file lands in T9)
- [`docs/extension-authoring.md`](docs/extension-authoring.md) — pi extension authoring patterns (file lands in T2 stub)

The original CEO plan is at `/home/macak/Development/hexxu/docs/designs/central-brain.md` in the parent project.

## Workflow

1. Author a skill via Claude Code (`pi-skill-creator` skill) or directly.
2. Open a PR against this repo.
3. CI runs the identity-drift check.
4. Once `CONTRIBUTORS.md` has more than one entry, the deferred eval-gate revives and PRs must also pass the skill-creator eval suite.
5. Merge to `main` (requires PR + 1 approving review under branch protection).
6. Workers' next pi session syncs the change via `hexxu-skills-sync` (non-blocking, 5-minute staleness cache).

## Status

Bootstrapping. Tasks T1-T11 from the CEO plan. This commit is T1 (repo + branch protection).
