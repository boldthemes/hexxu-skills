# TODOS

Deferred work from the CEO plan, each with an **explicit revival trigger**
so revival is mechanical, not aspirational. When a trigger fires, the item
becomes a P1 task and gets implemented; until it fires, the deferral is
intentional.

The trigger pattern matters. "Soon" or "when needed" rot into never-done.
Every entry below has a falsifiable condition: a count, a date, an
observable event. If you find yourself wanting to revive without a trigger
firing, write the trigger down first.

## Active deferrals

### 1. Eval-gate at merge time

**What:** GitHub Actions workflow on this repo that runs the skill-creator
eval suite on every PR touching `skills/**`. Skills must score ≥ 0.8
averaged across 3 deterministic seeded runs. Per-PR cost cap via
`max_eval_budget_usd` (default $0.50); overruns FAIL the workflow. Eval
results published to `evals/results/<skill>/<pr-sha>.json`.

**Revival trigger:** `CONTRIBUTORS.md` gains a second entry.

**Why deferred:** At solo stage the gate adds friction without the
cultural-norm payoff that gates provide on multi-contributor repos. A solo
contributor reviewing their own PR runs evals locally anyway. Once
contributors arrive, the cost calculus inverts — the gate becomes the only
defense against quality drift.

**Effort:** ~3h workflow + ~1h secrets/cost-cap plumbing (~4h total CC: ~20min).

**Refs:** CEO plan task T3.4 / deferred; full implementation spec
preserved in the CEO plan's "Deferred to TODOS.md" section so no
re-design is needed at revival time.

### 2. `/skill-feedback` worker→dev channel

**What:** Pi extension that registers a `/skill-feedback` slash command.
Worker types one line (snag, mis-trigger, output wrong, etc.); the
extension appends to a queue file in this repo with `{worker_id,
skill_name, skill_version, message, timestamp}`. Devs triage the queue
weekly.

**Revival trigger:** 2+ workers are actively using skills (not just
installed pi — actively invoking skills in their daily work).

**Why deferred:** The loop is currently dev↔dev (solo). The channel is
load-bearing only when workers are separate from devs. Pre-build risk: a
queue with no submitters loses signal and credibility.

**Effort:** ~4h human / ~25min CC.

**Refs:** CEO plan task D3.3 (deferred).

### 3. CHANGELOG.md per skill

**What:** Convention requiring each skill to maintain `CHANGELOG.md` next
to its `SKILL.md`. Workers see what changed between versions. Document the
convention in `CLAUDE.md`; optionally add a CI check that flags PRs which
bump `version` without updating `CHANGELOG.md`.

**Revival trigger:** 2+ contributors. (Same as eval-gate; revive both at
once to minimize CONTRIBUTORS.md transition friction.)

**Why deferred:** Process overhead without a team. Solo author knows what
they changed.

**Effort:** ~1h documentation + ~1h optional CI check.

### 4. `hexxu` onboarding CLI

**What:** `npx hexxu onboard` collapses `docs/onboarding.md`'s manual
steps into one command: generate UUID, install extensions to
`~/.pi/agent/extensions/`, install `hexxu-telemetry-summary` to
`~/.hexxu/bin/`, write the export lines to the shell profile, verify with
a smoke session.

Distribution path: publish as an npm package, OR ship from a published
hexxu-extensions repo (see TODO #9). Until either exists, install is by
filesystem copy per `docs/onboarding.md`.

**Revival trigger:** Worker #2 is about to onboard.

**Why deferred:** The marginal benefit kicks in at worker #2; worker #1
(you) bootstrapped manually and that's an acceptable one-time cost.
Pre-building forces decisions about distribution that aren't yet
informed by real onboarding pain.

**Effort:** ~M (1-2 days CC: ~2-3h).

**Refs:** CEO plan task D3.4 (deferred).

### 5. `/skill-search` slash command

**What:** Pi extension registering a `/skill-search <query>` command that
performs keyword/fuzzy match against installed skills' `name +
description + body` and returns the top N matches. Output: skill name,
short description preview, version, last_reviewed.

**Revival trigger:** Skill catalog exceeds 15 skills.

**Why deferred:** At 5 skills you remember them all. Search has no payoff
until the catalog is large enough that recall fails. The 15 threshold is a
heuristic; bump or lower as actual recall failures emerge.

**Effort:** ~3h CC: ~20min.

### 6. Skill compatibility matrix (`requires: pi >= X.Y`)

**What:** Extend the manifest schema (`docs/manifest-schema.md`) with an
optional `min_pi_version` field. Pi load path (or a CI check) refuses to
load skills declaring a higher minimum than the running pi version.

**Revival trigger:** Pi versions diverge across worker machines (i.e.,
some workers on pi 0.78, others on 0.85+, and a skill needs a feature
present only in the newer version).

**Why deferred:** Not an issue at single-developer scale; pi gets updated
in lockstep. Becomes load-bearing the first time a skill is unintentionally
incompatible with an older worker's pi install.

**Effort:** ~1h schema + ~2h pi-side enforcement.

### 7. Postgres extension for telemetry aggregation

**What:** First piece of phase B. Pi extension `hexxu-telemetry-upload`
that reads the local JSONL telemetry file and pushes records to a
hexxu-managed Postgres (Supabase to start; possibly self-hosted later).
Schema matches the locked JSONL fields exactly; new fields are additive.
ACL enforced at the extension boundary (constraint #6): each worker's
records are tagged with their `worker_id`; cross-worker queries require
explicit roles in Postgres.

**Revival trigger:** Local JSONL becomes a bottleneck for skill analysis
(e.g., you want to compare skill ROI across workers, or build trend
dashboards). The `hexxu telemetry-summary` CLI is single-worker; once
you want fleet-level views, postgres is the move.

**Why deferred:** Local JSONL is fine until cross-worker queries
matter. Building the upload path before then forces architectural
decisions (which postgres? which schema? how is auth set up?) without
the workflow context that would make those decisions obvious.

**Effort:** ~M (~1 week human / ~2h CC for the extension itself; Supabase
project setup is the other half of that).

**Refs:** CEO plan trajectory phase B.

### 8. Files extension (Drive / Notion read)

**What:** First piece of phase B's file pillar. Pi extension that exposes
a `read_central_file(path)` tool, wrapping Google Drive / Notion / S3
(start with one backend, structure for swappability). Skills declare
`requires: data:files:<scope>` in frontmatter; the extension enforces ACL
at read time.

**Revival trigger:** A specific worker workflow demands shared documents
(meeting notes that span teams, customer call recordings, contracts, etc.).

**Why deferred:** No workflow demanding it today. Building speculatively
locks in a backend choice (Drive? Notion? S3?) that should be informed by
the workflow's actual document source.

**Effort:** ~L (~1-2 weeks human / ~3-4h CC per backend).

**Refs:** CEO plan trajectory phase B.

## Done (kept for the revival audit trail)

Items the CEO plan considered and then explicitly accepted/scoped instead
of deferring. Listed here so a future contributor doesn't think they need
to "revive" them.

- ✅ Identity contract (`HEXXU_WORKER_ID`, UUID v4) — shipped T6/T9, constraint #7
- ✅ Telemetry extension + locked schema — shipped T7
- ✅ `hexxu telemetry-summary` CLI — shipped T8
- ✅ Branch protection on `main` (no bypass) — shipped T1
- ✅ Identity-drift CI workflow — shipped T3
- ✅ `docs/` directory + architecture/onboarding/extension-authoring/manifest-schema docs — shipped T2/T5/T9
- ✅ `CONTRIBUTORS.md` (with eval-gate revival trigger) — shipped T2
- ✅ **hexxu extension distribution mechanism** — shipped T12 as the published `boldthemes/hexxu` repo. Workers clone hexxu and copy `.pi/extensions/hexxu-skills-sync`, `.pi/extensions/hexxu-telemetry`, and `cli/telemetry-summary.ts` per `docs/onboarding.md`. Closes what was originally drafted as TODO #9 (deferred); resolved without deferral after the post-T11 audit uncovered the full scope of undistributed code (skill-creator extension + SDK + Claude Code skills + prompts + workflows + e2e harness).

## Add a TODO

Open a PR that appends a section here following the same shape:

```markdown
### N. Title

**What:** [concrete description of what the work is]

**Revival trigger:** [falsifiable condition — count, date, or observable event]

**Why deferred:** [the specific reason this isn't being built now]

**Effort:** [S/M/L/XL with human and CC scales]

**Refs:** [related sections, CEO plan tasks, etc.]
```

Increment the section number. If the trigger needs to be measured by code
(`CONTRIBUTORS.md` count, skill count, etc.), prefer a CI-checkable
condition over a subjective one.

## Why every TODO has a trigger

The CEO plan called this out explicitly: vague intentions ("we should add
X eventually") accumulate into untrackable debt. A trigger turns each
deferral into a contract: when condition Z fires, this item is no longer
optional. The pattern lets us defer aggressively without losing the
intent, and revive deterministically when the conditions change.
