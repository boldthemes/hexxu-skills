---
schema: hexxu-routing-test/v1
margin: 0.15

positive_prompts:
  - "Where does pi configure default models?"
  - "How do pi extensions hook into session_start?"
  - "What providers does pi support out of the box?"
  - "Where in pi source is the slash command parser?"

negative_prompts:
  - prompt: "How does hexxu-skills-sync rotate the cache directory?"
    why: "Documenting hexxu or hexxu-skills internals (not pi itself)"
    must_not_route_to: ["pi-docs-map"]
  - prompt: "Write the documentation page for pi's new --bare flag"
    why: "Authoring or editing pi's own published documentation"
    must_not_route_to: ["pi-docs-map"]
  - prompt: "How does Claude Code's settingSources field work?"
    why: "Answering questions about other agents (Claude Code, OpenCode, Aider)"
    must_not_route_to: ["pi-docs-map"]
  - prompt: "Refactor pi's model resolver to support fallback chains"
    why: "Implementing changes to pi (this skill only locates docs and references)"
    must_not_route_to: ["pi-docs-map"]
---

# Why these tests

The positives all phrase a "where in pi source / docs is X" question across
the four most common topic clusters: model config, extension lifecycle,
provider catalog, and TUI internals. All four must land here regardless of
where in pi source the answer lives.

The negatives walk the four `non_goals`. The hexxu-skills-sync test is the
nearest-neighbour risk — same "where is X" shape but wrong project. The
documentation-authoring test catches "pi docs" being read as a write
intent. The Claude Code test catches the generic "agent internals" routing
attractor. The refactor test catches the "pi source" keyword trap when the
ask is actually an implementation request.
