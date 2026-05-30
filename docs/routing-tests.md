# Routing tests (`SKILL.tests.md`)

Every skill in this registry MUST ship with a `SKILL.tests.md` sibling file.
It exercises the **routing layer** — does pi's available_skills system prompt
plus this skill's `description` actually send the right prompts here, and keep
the wrong ones out?

This is distinct from `evals/evals.json` (outcome tests, deferred to TODOS).
Routing tests can land today because they don't need the full skill body to be
implemented — they only need the `description` and the `non_goals`.

---

## Why this exists

Self-improvement loops (skill-creator + the SDK's `optimize-description` /
`compare-iteration` flow) edit `description` text iteratively. Without a
mechanical gate, three failure modes accumulate silently:

1. **Scope creep.** Iteration N's `description` claims slightly more than
   N-1's; over time the skill grabs prompts that should land elsewhere.
2. **Adjacency overlap.** Two skills' descriptions become routing-equivalent;
   pi picks one nondeterministically.
3. **Reachability erosion.** A skill's positive prompts start routing to a
   neighbour; the original skill never fires again.

Routing tests catch all three the moment they appear in a PR.

---

## File location and format

```
skills/
  <skill-name>/
    SKILL.md
    SKILL.tests.md      # ← this file
```

YAML frontmatter (machine-readable), then a markdown body (author's reasoning).

```yaml
---
schema: hexxu-routing-test/v1
margin: 0.15

positive_prompts:
  - "Prompt that must route to this skill"
  - "Another phrasing the same user might use"
  - "A less obvious one — corner of the scope"
  - "An adjacent-but-still-mine phrasing"

negative_prompts:
  - prompt: "Looks like this skill but isn't"
    why: "Crosses non_goals entry: <copy of the entry>"
    must_not_route_to: ["<this-skill-name>"]
  - prompt: "Another nearby phrasing that belongs to a neighbour"
    why: "Crosses non_goals entry: <copy of the entry>"
    must_not_route_to: ["<this-skill-name>"]
---

# Why these tests

Prose explaining what scope and non_goals these tests enforce. One paragraph
per test cluster is plenty.
```

### Field semantics

| Field | Type | Required | Notes |
|---|---|---|---|
| `schema` | string | yes | Must equal `hexxu-routing-test/v1`. Versioned so the runner can evolve. |
| `margin` | float 0.0–1.0 | yes | Required confidence gap between this skill and the runner-up on positives. Default 0.15. Higher = stricter. |
| `positive_prompts` | array of 3–10 strings | yes | Prompts that MUST route to this skill with confidence ≥ runner-up + `margin`. |
| `negative_prompts` | array of 2–8 objects | yes | Each has `prompt` (string), `why` (string, must cite a `non_goals` entry), and `must_not_route_to` (array of skill names). |

### Counts and what they're for

- **Positives ≥ 3** because routing is fragile under paraphrase — a single
  prompt that happens to hit doesn't prove the description is robust.
- **Negatives ≥ 2** because a single negative test catches the obvious case;
  the second forces the author to articulate a *second* adjacent neighbour and
  thereby map the skill's actual boundary.

### Tying negatives to `non_goals`

Every negative's `why` MUST cite a `non_goals` entry verbatim. Schema
validation enforces a substring match. This prevents negatives from drifting
to "random prompts that fail today" and keeps them anchored to the skill's
stated anti-scope.

---

## What the CI gate does

The `.github/workflows/routing-margin.yml` job runs on every PR touching
`skills/**`:

1. **Always:** schema-validate every changed `SKILL.tests.md` (no API key
   required). Catches malformed test files, missing fields, `why` lines that
   don't cite a real `non_goals` entry.
2. **Conditional (requires `ANTHROPIC_API_KEY` repo secret):** invoke the
   routing oracle. For each touched skill's test file:
   - Send each positive prompt + the full registry of `name + description +
     scope` to a model with a fixed instruction ("pick the best skill or
     `none`; report confidence for top-3").
   - Assert `chosen == <this-skill>` and `confidence(chosen) -
     confidence(runner_up) ≥ margin`.
   - Send each negative prompt similarly. Assert `chosen != <this-skill>` and
     `chosen ∉ must_not_route_to`.
   - 3 deterministic seeded runs; majority wins.

Until the secret is configured, only step 1 runs. The job is wired in now so
the scaffolding ships with the schema; the oracle turns on when you're ready
to pay the per-PR API cost.

---

## Authoring guide

A good positive set covers:
- The most natural phrasing a user would use
- A paraphrase that drops keywords from `description`
- One that uses synonyms or domain jargon
- One that lives at the edge of `scope` — still inside, but only just

A good negative set covers:
- The closest neighbour skill (most likely overlap source)
- The most plausible misreading of `description`
- A prompt that pattern-matches `description` keywords but violates `scope`

If you can't articulate at least two negatives, the skill's boundary isn't
clear yet — refine `scope` and `non_goals` first, then come back.

---

## Anti-patterns

- **Negatives that cite `description` instead of `non_goals`** — schema
  rejects this. `non_goals` is the contract; `description` is the routing
  signal. Tests anchor to the contract.
- **`margin` of 0** — defeats the gate. Even a coin-flip routing decision
  passes. The 0.15 default is the floor; raise it for skills with very
  similar neighbours.
- **Positives that all share keywords** — robust routing means surviving
  paraphrase. Vary the wording deliberately.
- **`positive_prompts` repeated across skills** — if two skills share a
  positive, one of them is mis-scoped. Resolve by tightening descriptions
  or marking `supersedes`.
- **`why` line that paraphrases `non_goals`** — must be a verbatim substring
  match (case-insensitive, whitespace-normalized). The schema check enforces
  this.

---

## Worked example

See `skills/add-llm-provider/SKILL.tests.md` for the canonical example. The
six skills migrated in T15 all carry test files that round-trip through the
schema validator and represent the patterns above.
