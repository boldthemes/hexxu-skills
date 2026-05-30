---
schema: hexxu-routing-test/v1
margin: 0.15

positive_prompts:
  - "How do I add a new LLM provider to packages/ai?"
  - "I want to wire up Bedrock as a provider in pi"
  - "Add support for the Cohere API to packages/ai"
  - "What files do I need to touch to add Mistral to pi's providers?"

negative_prompts:
  - prompt: "Change the default model for the OpenAI provider"
    why: "Modifying an existing provider's defaults, model list, or auth scheme"
    must_not_route_to: ["add-llm-provider"]
  - prompt: "How does pi decide which provider to call when I run /model?"
    why: "Changing pi's model-selection or runtime routing logic"
    must_not_route_to: ["add-llm-provider"]
  - prompt: "Add SSE streaming to the existing Anthropic provider"
    why: "Adding a new transport (SSE, websocket) to an existing provider"
    must_not_route_to: ["add-llm-provider"]
  - prompt: "Refactor packages/coding-agent/src/cli/args.ts to use Zod"
    why: "Edits in packages/coding-agent unrelated to provider wiring"
    must_not_route_to: ["add-llm-provider"]
---

# Why these tests

The positives cover four natural phrasings of "I am adding a brand new
provider": the literal canonical phrase, a provider-name-first phrase, the
verbose "add support for" form, and the file-set-focused form. They should all
route here regardless of which provider the user names.

The negatives walk the four `non_goals` entries in order. The first three are
the closest adjacency risks — model defaults, runtime routing, transports —
each of which touches provider code without being a *new* provider. The fourth
guards against keyword-matching on `packages/coding-agent` since the skill
mentions it; that mention is wiring-only, not a general invite.
