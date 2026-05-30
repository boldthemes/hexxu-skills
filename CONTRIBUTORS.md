# Contributors

This file lists every human (and stable agent identity) who has shipped a
change to `hexxu-skills`. It is **load-bearing** — when the file has more
than one entry, the eval-gate TODO in `TODOS.md` is revived as mandatory.

## Eval-gate revival trigger

The CEO plan deferred the eval-gate (mandatory CI eval pass for skill PRs)
because at solo stage the gate adds friction without the cultural-norm
payoff that gates provide on multi-contributor repos. The trigger to revive
it is mechanical: **when this file has more than one contributor entry, the
TODOS.md eval-gate entry becomes a P1 task and PRs must wait until it ships.**

When you add a second contributor:
1. Open the corresponding PR.
2. In the PR description, link to the TODOS.md eval-gate entry.
3. Block merge of any *other* skill PRs until the gate ships.
4. After the gate ships, normal flow resumes — every skill PR now runs evals.

The full design for the gate is preserved in the CEO plan's "Deferred to
TODOS.md" section and in `TODOS.md` (lands in T11). No re-thinking needed
at revival time.

## Contributor list

| Handle | Email | Joined | Role |
|---|---|---|---|
| @rmackovic | rmackovic@gmail.com | 2026-05-30 | Owner; bootstrapping the central brain |

## Adding yourself

1. Add a row to the table above with your GitHub handle, contact email,
   joined date (ISO), and a one-line role description.
2. Include the change in your first substantive PR (not as a separate PR).
3. Before merging, check whether the addition crosses the threshold from
   1 contributor to 2 — if so, follow the revival trigger procedure above.
