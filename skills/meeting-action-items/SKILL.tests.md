---
schema: hexxu-routing-test/v1
margin: 0.15

positive_prompts:
  - "Here are my notes from today's standup — pull out the action items"
  - "Extract owners and due dates from this brainstorm transcript"
  - "What decisions and blockers came out of this call?"
  - "Turn these messy notes into a tracker-ready task list"

negative_prompts:
  - prompt: "Summarize this email thread for me"
    why: "Summarizing email threads or chat logs"
    must_not_route_to: ["meeting-action-items"]
  - prompt: "Draft an agenda for tomorrow's planning meeting"
    why: "Drafting agendas or pre-meeting briefs"
    must_not_route_to: ["meeting-action-items"]
  - prompt: "Write a recap email for the team after this call"
    why: "Composing recap or follow-up emails after the meeting"
    must_not_route_to: ["meeting-action-items"]
  - prompt: "Schedule a 30-minute follow-up with @alex"
    why: "Calendar scheduling or invite management"
    must_not_route_to: ["meeting-action-items"]
---

# Why these tests

The positives sample the four extraction targets named in the description:
action items, owners and dates, decisions and blockers, and tracker-ready
output. All from informal-note shapes (standup, brainstorm, call notes).

The negatives walk the four `non_goals` in order. The email-thread test is the
classic adjacency — same "extract structure from informal text" but wrong
source. The agenda test catches the pre-meeting use of the same vocabulary.
The recap email and scheduling tests catch downstream-of-the-meeting tasks
that look like they share the "meeting" keyword but live elsewhere.
