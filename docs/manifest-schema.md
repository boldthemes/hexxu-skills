# Skill manifest schema

Canonical specification for the YAML frontmatter at the top of every
`skills/<name>/SKILL.md` file in this repo. This document is **authoritative**;
CLAUDE.md's constraint #4 references it; T6's grandfather migration retrofits
the five existing skills against it.

> The manifest is what makes a skill *addressable*. Workers, CI, the future
> registry service, and the `hexxu telemetry-summary` CLI all read the same
> six fields. One spec, one source of truth.

---

## Fields

### `name` (required, string)

The skill's stable identifier.

- **Pattern:** `^[a-z0-9]+(-[a-z0-9]+)*$`
- **Max length:** 64 characters
- **MUST match the directory basename** exactly. A skill at `skills/meeting-action-items/SKILL.md` MUST have `name: meeting-action-items`.
- Lowercase ASCII alphanumerics + hyphens. No leading hyphen, no trailing hyphen, no consecutive hyphens.

Renaming a skill = directory rename + `name` field update in the same PR.

### `description` (required, string)

Human-readable summary that drives pi's trigger detection.

- **Max length:** 1024 characters
- **Should state both WHAT and WHEN:** what the skill does AND when pi should invoke it.
- **Add a negative-class clause** when the skill could be confused with adjacent concepts: "Use when X. Not for Y or Z."

Pi loads SKILL.md only when the model decides this description matches the user's intent. A vague description is invisible; an over-specific one is brittle. Aim for 100-400 chars in practice; the 1024 cap exists for unusual cases.

### `version` (required, string)

Semver version of the skill itself.

- **Pattern (canonical):** `^\d+\.\d+\.\d+(?:-[\w.]+)?(?:\+[\w.]+)?$`
- Pre-release (`-rc.1`) and build metadata (`+sha.abc123`) are allowed but rarely needed.
- Workers read this to know what version they're running; the future registry service uses it for compatibility checks.

**Bump rules:**

| Change | Bump |
|---|---|
| Body text edits, doc improvements, no behavior change | patch (`0.1.0` → `0.1.1`) |
| New optional behavior; old prompts still work | minor (`0.1.0` → `0.2.0`) |
| `description` refined (wording, prompt-shaping) but stays inside `scope` and respects `non_goals` | minor |
| `non_goals` entry added | minor |
| `scope` text edited substantively | major |
| `non_goals` entry removed or relaxed | major |
| `supersedes` added (replacing a prior skill) | major; old skill dir MUST be deleted in the same PR |
| Trigger description changes substantially OR breaking workflow change | major (`0.1.0` → `1.0.0`) |
| Pre-1.0 development (initial bootstrap) | start at `0.1.0`; bump minor liberally |

### `owner` (required, UUID v4)

The `HEXXU_WORKER_ID` of whoever maintains this skill going forward.

- **Pattern:** `^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$` (UUID v4)
- **MUST be the maintainer's `HEXXU_WORKER_ID`**, not the original author's, not an email, not a GitHub handle. Constraint #7.

Maintenance ownership transfers via a PR that updates this field; the transfer commit is the audit trail. Workers whose UUID rotates (constraint #7 rotation policy) MUST also update any skills they own to the new UUID — those owner-update PRs are titled `chore: rotate owner UUID for @<handle>` per `docs/onboarding.md`.

### `last_reviewed` (required, ISO date)

The date this skill was last substantively reviewed.

- **Format:** `YYYY-MM-DD` (ISO 8601 date, no time component)
- **Bumped on every PR that touches this skill**, including ownership transfers and frontmatter-only changes.
- Drives skill-rot detection in future tooling: skills with `last_reviewed` more than N days old surface for re-review.

### `scope` (required, string)

One-sentence positive statement of what this skill is for. The single line a
human reviewer reads to judge "is this iteration still the same skill?"

- **Min/max length:** 30–512 characters
- **Should be a noun phrase or a single declarative sentence**, not a paragraph.
- **Must be consistent with `description`** but is allowed to differ in phrasing.
  `description` is prompt-shaped (drives routing); `scope` is reviewer-shaped
  (drives "did we drift?" judgments).
- Bumping `scope` text substantively = **major version bump**. It's a behavioral
  promise to workers and to the routing layer.

`scope` exists so self-improvement iterations can refine `description` for
routing quality without it counting as a scope change, and so reviewers have a
fixed reference point when judging an iteration PR.

### `non_goals` (required, array of strings)

Explicit anti-scope. The set of things this skill is NOT for.

- **Item count:** 2–8 entries
- **Item length:** 10–200 characters
- **Each entry should be testable** — concrete enough that a routing prompt
  could exercise it (see `docs/routing-tests.md`).
- The 2-entry minimum exists to force authors past the obvious "not for X" and
  enumerate the *adjacent neighbours* — the skills nearby in concept space that
  could plausibly steal routing.

`non_goals` is the contract that self-improvement iterations are checked
against. Adding an entry is a **minor bump**; removing or relaxing one is a
**major bump** (you are widening the skill's scope).

### `supersedes` (optional, array of strings)

Names of skills this one replaces.

- **Pattern per entry:** same as `name` (`^[a-z0-9]+(-[a-z0-9]+)*$`)
- **CI rule:** if skill B has `supersedes: [a]` then skill A's directory MUST
  be deleted in the same PR. Prevents zombie skills that never fire but pollute
  the routing space.
- Use when iterating produces a sufficiently different skill that keeping the
  old one would create a routing collision. Most version bumps are NOT a
  supersession — only a rewrite that warrants a new `name`.

### `requires` (optional, array of strings)

Declared dependencies on pi extensions and/or external data layers.

- **Format per entry:** `extension:<name>` or `data:<scope>`
- **Examples:**
  - `extension:hexxu-telemetry` — skill expects this extension to be present
  - `data:postgres:hexxu_main` — skill expects an extension that exposes a `data:postgres:hexxu_main` capability
- Omit the field entirely if the skill uses only pi's built-in tools (`read`, `bash`, `edit`, `write`, `grep`, `find`, `ls`).
- Today this is **informational** — workers see it but pi doesn't enforce dependency resolution. Foreshadows phase B's extension surface; when the postgres/files extensions land, declaration becomes load-time validation.

---

## Worked example

```yaml
---
name: meeting-action-items
description: Extracts action items with owners from meeting transcripts. Use when the user pastes a transcript and asks for next steps. Not for summarizing email threads or chat logs.
version: 0.3.0
owner: 8f3e9d2c-1b4a-4f7e-9c8d-2a1b3c4d5e6f
last_reviewed: 2026-05-30
scope: Distill action items, owners, due dates, decisions, blockers, dependencies, and open questions from informal meeting and call notes.
non_goals:
  - Summarizing email threads or chat logs
  - Drafting agendas or pre-meeting briefs
  - Composing recap or follow-up emails
  - Calendar scheduling or invite management
requires:
  - extension:hexxu-telemetry
---

# Meeting Action Items

When the user pastes a meeting transcript ...
```

Minimal example (no `requires`):

```yaml
---
name: csv-to-markdown-converter
description: Converts CSV input into a markdown table. Use when the user pastes CSV data and asks for a table.
version: 0.1.0
owner: 8f3e9d2c-1b4a-4f7e-9c8d-2a1b3c4d5e6f
last_reviewed: 2026-05-30
scope: Build or improve tools that convert CSV data into markdown tables and documents.
non_goals:
  - Converting markdown back into CSV
  - Converting CSV to JSON, HTML, or other non-markdown formats
  - Diagnosing arbitrary CSV parse errors outside a converter context
  - General markdown editing unrelated to tables
---

# CSV to Markdown Converter
...
```

---

## Unknown fields

**Unknown fields are silently accepted and ignored.** This preserves forward
compatibility: new fields can be added in a future spec version without
breaking the existing reader population.

Notable Claude-Code-specific fields (`tools`, `permissions`, `mcp`) fall under
this rule — pi ignores them. Don't add them; they pollute the file without
effect. Same applies to `model`, which Claude Code sometimes uses but pi
sources from the session, not the skill.

---

## Validation surfaces

Today and planned. The schema is enforced at multiple points so a malformed
manifest is caught early.

| Surface | Status | Scope |
|---|---|---|
| Human review on PR | live (T1) | All fields, plus prose quality |
| `identity-drift` CI workflow | live (T3) | Skill body only; doesn't touch frontmatter |
| `manifest-schema` CI workflow | **deferred** (revival trigger: any PR adding a skill, or 2+ contributors) | Frontmatter against this spec |
| `hexxu-skills-sync` extension | live (T4) | None today; foreshadowed for phase B |
| Eval-gate CI | deferred (revival trigger: 2+ contributors) | Runs only on skills that pass schema check |
| `hexxu telemetry-summary` CLI (T8) | in progress | Reads `name`, `version` for ROI correlation |

---

## JSON Schema (machine-readable)

For programmatic validation. Embed in a CI workflow with a YAML→JSON adapter
when the deferred `manifest-schema` CI lands.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "hexxu skill manifest",
  "type": "object",
  "required": ["name", "description", "version", "owner", "last_reviewed", "scope", "non_goals"],
  "properties": {
    "name": {
      "type": "string",
      "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$",
      "maxLength": 64
    },
    "description": {
      "type": "string",
      "minLength": 1,
      "maxLength": 1024
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+(?:-[\\w.]+)?(?:\\+[\\w.]+)?$"
    },
    "owner": {
      "type": "string",
      "pattern": "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
    },
    "last_reviewed": {
      "type": "string",
      "format": "date",
      "pattern": "^\\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\\d|3[01])$"
    },
    "scope": {
      "type": "string",
      "minLength": 30,
      "maxLength": 512
    },
    "non_goals": {
      "type": "array",
      "items": { "type": "string", "minLength": 10, "maxLength": 200 },
      "minItems": 2,
      "maxItems": 8,
      "uniqueItems": true
    },
    "supersedes": {
      "type": "array",
      "items": { "type": "string", "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$" },
      "uniqueItems": true
    },
    "requires": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^(?:extension|data):.+$"
      },
      "uniqueItems": true
    }
  },
  "additionalProperties": true
}
```

---

## Anti-patterns

- **Description shorter than ~30 chars** — pi's trigger detection won't have enough signal; the skill becomes effectively invisible.
- **Bumping `version` without updating `last_reviewed`** — signals that you didn't actually re-read what you changed.
- **Using a handle, email, or `git config user.name` for `owner`** — UUID only. Constraint #7.
- **Adding `tools:`, `permissions:`, `mcp:`** — Claude Code idioms; pi ignores. Don't pollute.
- **Omitting `requires` when the skill talks to telemetry / postgres / files** — declarations make the data layer explicit; future tooling validates against them. Better to declare and be wrong than to silently couple.
- **`name` ≠ directory basename** — workers won't find the skill. CI doesn't catch this today; T11's TODOS includes a revival trigger to add directory-name validation when the broader schema CI lands.
- **`scope` that just paraphrases `description`** — the two fields exist to serve different consumers (`description` → routing model, `scope` → human reviewer). If they read identically, you have not actually committed to a scope. Re-write `scope` as a fixed reference point.
- **`non_goals` that are operational notes, not routing-distinguishable** — entries like "do not run if disk is full" belong in the body. `non_goals` must be things a routing test could exercise: an adjacent prompt that *looks* like a fit but isn't.
- **`non_goals` shorter than 2 entries** — schema rejects this; the floor is there to force enumeration of *adjacent neighbours*, not just the obvious "not for X".
- **Iterating `description` past the `scope` line without bumping major** — the routing-margin CI gate (lands with this spec) catches the routing drift; the version field tells the human reviewer about the semantic drift. Both are required.
- **Adding `supersedes` without deleting the superseded skill's directory** — zombie skills pollute the routing space and lie to workers about what's available. CI rejects this.

---

## When to revise this spec

Add a new field: append it to the "Fields" section with the same shape (purpose, type, constraints, bump rules if relevant). Update the JSON Schema. Bump nothing; consumers ignore unknown fields by design.

Change an existing field's semantics: this is a breaking change. Bump the spec's implicit version (this file's last commit), audit consumers, plan a migration window. Don't do this lightly — every skill carries the old shape.

Remove a field: never. Required-to-optional is fine; required-to-removed breaks every consumer that reads it. Mark deprecated, give consumers a window to migrate, then remove only when zero skills carry the field.
