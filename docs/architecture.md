# Architecture

System shape of the **hexxu central brain** as it exists today (Phase A), the
trajectory through B and C, and the rationale behind each of the seven
design constraints in `CLAUDE.md`.

The full CEO-plan rationale that produced these choices lives in
`/home/macak/Development/hexxu/docs/designs/central-brain.md` (parent project,
untracked until hexxu's git is re-enabled).

## What "central brain" means

**Workers** use [pi](https://github.com/earendil-works/pi-coding-agent) as
their daily-driver agent harness. **Developers** use Claude Code in parallel
for skill and tool authoring. The "central brain" is the shared substrate
that lets one developer's skill instantly become every worker's capability.

Three pillars in the long-term vision:

1. **Central skill registry** (this repo — Phase A, live today)
2. **Central data layer** (Phase B — pi extensions for postgres / Supabase)
3. **Central file layer** (Phase B — pi extensions for Drive / Notion / S3)

Phase A is the only one shipped today. B and C are the trajectory, not the project.

## Phase A architecture (current)

```
                                    GitHub: boldthemes/hexxu-skills
                                              │
                                  git pull (configurable URL,
                                  constraint #3)
                                              │
                                              ▼
                          ┌────────── Worker machine ──────────┐
                          │                                     │
                          │   HEXXU_WORKER_ID env var (UUID v4) │
                          │           │                         │
                          │           ▼                         │
                          │   ┌─────────────────────┐           │
                          │   │ pi session          │           │
                          │   │ (loads skills from  │           │
                          │   │  ~/.pi/agent/       │           │
                          │   │  skills/)           │           │
                          │   └──────────┬──────────┘           │
                          │              │                      │
                          │       session_shutdown              │
                          │              │                      │
                          │              ▼                      │
                          │   ┌─────────────────────┐           │
                          │   │ hexxu-telemetry     │──▶ JSONL  │
                          │   │ (pi extension)      │   (0600)  │
                          │   └─────────────────────┘           │
                          │                                     │
                          │   hexxu-skills-sync                 │
                          │   (pi extension, non-blocking,      │
                          │    5-min staleness cache)           │
                          └─────────────────────────────────────┘

                          + `hexxu telemetry-summary` CLI reads
                            the local JSONL on demand
```

Components shipped or in progress:

| Component | Status | Lives in |
|---|---|---|
| `hexxu-skills` git repo | T1 done | `github.com/boldthemes/hexxu-skills` |
| Branch protection on `main` | T1 done | GitHub Rulesets |
| CLAUDE.md + docs scaffold | **T2 in progress** | this PR |
| Identity-drift CI workflow | T3 | `.github/workflows/identity-drift.yml` |
| `hexxu-skills-sync` pi extension | T4 | hexxu project, `.pi/extensions/hexxu-skills-sync/` |
| Manifest schema spec | T5 | `docs/manifest-schema.md` |
| Grandfather migration of 5 existing skills | T6 | this repo, `skills/` |
| `hexxu-telemetry` pi extension | T7 | hexxu project, `.pi/extensions/hexxu-telemetry/` |
| `hexxu telemetry-summary` CLI | T8 | hexxu project, `cli/` |
| `HEXXU_WORKER_ID` onboarding doc | T9 | `docs/onboarding.md` |
| E2E acceptance tests | T10 | hexxu project, `test/` |
| `TODOS.md` populated | T11 | this repo, root |

## A → B → C trajectory

**A (now, ~1.5 days of build):** Skills-First Lake. Central git repo for
skills. Workers' pi pulls via `hexxu-skills-sync`. Telemetry local-only.

**B (weeks 2-7, demand-driven):** Federation. Pi extensions for Drive/Notion
(file pillar) and Supabase (data pillar). All three pillars covered via
SaaS. Telemetry aggregated to Supabase.

**C (months 3-24, piece-by-piece):** Selective self-hosting where SaaS
cost or compliance pain demands it. Never a discrete project — each piece
moves from SaaS to self-hosted independently, justified by specific
observed pain.

The seven design constraints are the discipline that keeps the trajectory
intact. If we violate them, the eventual move from A to B to C becomes a
rewrite, not a migration.

## Constraint rationale (one paragraph each)

### #1 Versioning in frontmatter

Git tags work today because skills live in a git repo. They break when
skills move to a registry service (Phase C). Putting `version` in the
frontmatter means workers know "I have skill X v0.3.0" regardless of how
they got it — git pull, registry API, scp, whatever. Decouples delivery
from identity.

### #2 No ad-hoc identity sources

Skills run inside pi sessions on worker machines. If a skill reads
`whoami` or `git config user.email`, it gets *that machine's* identity,
which may be a shared service account, a leftover dev config, or just
wrong. `HEXXU_WORKER_ID` is the contract. Mechanically enforced by the
identity-drift CI workflow (T3).

### #3 Configurable registry URL

Phase A's registry is `github.com/boldthemes/hexxu-skills`. Phase B's
registry might still be GitHub but with mirrors. Phase C's registry
might be `registry.hexxu.io`. Skills that hard-code the URL break twice;
configurable URL never breaks.

### #4 Manifest schema as authoritative spec

Frontmatter is read by workers, by CI, by the future registry service,
by `hexxu telemetry-summary`, by any developer auditing the catalog.
One spec, one source of truth. Without a manifest schema, every consumer
re-invents what to look for.

### #5 Offline-first

Workers can't be blocked when GitHub is down or a worker is on a plane.
The sync extension warns but doesn't block; cached skills keep working.
Cold-start fails open with empty skills + visible warning rather than
blocking the pi session. This is also a defense against "central brain
becomes a SPOF" — workers degrade gracefully.

### #6 Authorization in the data layer

Skills are markdown content loaded into the pi system prompt. They have
no privileged execution; they describe what pi should do. Authorization
happens when pi (via an extension) calls postgres or reads files —
the extension checks `HEXXU_WORKER_ID` against ACLs at that boundary.
Putting auth in skills means it's everywhere, untestable, and inconsistent.

### #7 `HEXXU_WORKER_ID` UUID v4

UUID v4 is portable across SSO providers, doesn't leak personal info
(unlike email), survives email changes and rebranding, and is large
enough that you can't accidentally collide. Rotation = new UUID, no
migration of old data — keeps the audit story honest. Portable across
machines means worker telemetry correlates across their laptop and
desktop without identity-mapping logic.

## Failure modes and mitigations

| Risk | Mitigation | Reference |
|---|---|---|
| Worker non-adoption | Skill quality + onboarding investment | (deferred CLI in TODOS) |
| Skill rot | `last_reviewed` field + (deferred) eval-gate | constraint #4, TODOS |
| Identity drift | Identity-drift CI check enforces constraint #2 | T3 |
| Telemetry privacy | Local-only JSONL, mode 0600, no upload | T7 |
| Solo author quality drift | Pre-commit hook (optional) + eval-gate when revived | TODOS |
| Prompt injection via skill commit | Branch protection on `main`, no bypass | T1 done |
| Observability rot | `hexxu telemetry-summary` CLI ships in initial scope | T8 |

## What's intentionally out of scope (Phase A)

- Files pillar (Drive/Notion/S3 reads from pi) → Phase B
- Postgres pillar (shared DB, RAG, embeddings) → Phase B
- Auth/SSO/permissions → Phase C; the identity contract (constraint #7) preserves the door
- Web UI for workers or developers → Phase C, questionable even then
- Skill marketplace / cross-org sharing → not yet contemplated
- Multi-tenant brain serving multiple orgs → out of scope, may never apply
