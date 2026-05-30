---
schema: hexxu-routing-test/v1
margin: 0.15

positive_prompts:
  - "Help me write a SKILL.md for parsing customer feedback"
  - "Refine this skill's trigger description so it doesn't overlap with meeting-action-items"
  - "Design eval prompts for my new csv-cleanup skill"
  - "Iterate on this skill based on the feedback I got from pi yesterday"

negative_prompts:
  - prompt: "Polish the wording on the pr.md prompt template"
    why: "Iterating on pi prompt templates under .pi/prompts/"
    must_not_route_to: ["skill-creator"]
  - prompt: "Set up an eval harness for generic OpenAI prompt quality"
    why: "Generic LLM eval design unrelated to pi skills"
    must_not_route_to: ["skill-creator"]
  - prompt: "Write a pi extension that syncs messages with Slack"
    why: "Authoring pi extensions or SDK scripts"
    must_not_route_to: ["skill-creator"]
  - prompt: "Author a SKILL.md for Claude Code that uses the tools: frontmatter field"
    why: "Authoring Claude Code skills (different format and host)"
    must_not_route_to: ["skill-creator"]
---

# Why these tests

The positives cover the four authoring stances: greenfield SKILL.md, trigger
refinement against a named neighbour, eval-prompt design, and feedback-driven
iteration. All four are recognizably "pi skill work" and must route here.

The negatives are the three closest hexxu-internal neighbours plus the
cross-host trap. Prompt templates and pi extensions both live in `.pi/` and
share authoring vocabulary, so they're the highest collision risk. Generic LLM
evals catch the "eval prompts" keyword. The Claude Code trap is the most
dangerous as self-improvement loops scale — a SKILL.md request without a host
qualifier should NOT silently route to pi-skill authoring when the user meant
Claude Code's skill system.
