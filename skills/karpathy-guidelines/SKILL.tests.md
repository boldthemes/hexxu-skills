---
schema: hexxu-routing-test/v1
margin: 0.15

positive_prompts:
  - "Review this diff and tell me if it's overcomplicated"
  - "I'm about to write a big refactor — what should I keep in mind?"
  - "How do I define verifiable success criteria for this fix?"
  - "What assumptions am I making in this implementation plan?"

negative_prompts:
  - prompt: "Set up eslint and prettier rules for my TypeScript project"
    why: "Language-specific style or formatting rules (lint configs, formatters)"
    must_not_route_to: ["karpathy-guidelines"]
  - prompt: "Should I use hexagonal architecture for this microservice?"
    why: "Project-specific architecture or design pattern decisions"
    must_not_route_to: ["karpathy-guidelines"]
  - prompt: "Write the concrete test plan for PR #482"
    why: "Replacing concrete code review feedback or test plans for a given diff"
    must_not_route_to: ["karpathy-guidelines"]
  - prompt: "Should I build this CLI in Go or Rust?"
    why: "Choosing between languages, frameworks, or runtimes"
    must_not_route_to: ["karpathy-guidelines"]
---

# Why these tests

The positives all invoke the behavioral-guardrail shape: a review request, a
pre-work-checklist request, the success-criteria question, and the
surface-assumptions question. They map 1:1 to the four behaviors named in the
description.

The negatives all *sound* like coding-process questions but each crosses a
specific `non_goals` line. The eslint case catches the "code mistakes" keyword
trap. The hexagonal case catches "review/refactor" trapping all architectural
discussions. The PR-test-plan case catches "verifiable success" being read as
"write the test plan." The language-choice case catches "what should I keep in
mind" being read as a general decision aid.
