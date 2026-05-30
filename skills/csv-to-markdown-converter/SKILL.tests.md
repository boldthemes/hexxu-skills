---
schema: hexxu-routing-test/v1
margin: 0.15

positive_prompts:
  - "Write a CLI that turns a CSV file into a markdown table"
  - "How do I handle commas inside quoted CSV fields when emitting markdown?"
  - "Add a flag to my csv-to-md converter for header alignment"
  - "Build tests for my CSV to markdown table function"

negative_prompts:
  - prompt: "Parse this markdown table back into CSV"
    why: "Converting markdown back into CSV"
    must_not_route_to: ["csv-to-markdown-converter"]
  - prompt: "Turn this CSV into JSON for an API payload"
    why: "Converting CSV to JSON, HTML, or other non-markdown output formats"
    must_not_route_to: ["csv-to-markdown-converter"]
  - prompt: "Why is my standalone CSV parser dropping the last row?"
    why: "Diagnosing arbitrary CSV parse errors outside a converter context"
    must_not_route_to: ["csv-to-markdown-converter"]
  - prompt: "Format this paragraph as a markdown blockquote"
    why: "General markdown editing unrelated to tables"
    must_not_route_to: ["csv-to-markdown-converter"]
---

# Why these tests

The positives cover four authoring stances: building a CLI, debugging a parsing
edge case, extending an existing converter with options, and writing tests. All
four must land here regardless of which sub-task the user is on.

The negatives walk the four `non_goals` in order. The reverse-direction
(markdown→CSV) and other-format (CSV→JSON) tests are the obvious overlap
risks. The standalone CSV parser test catches the keyword-matching risk on
"CSV parsing rules"; the blockquote test catches the same on "markdown
formatting". Both keywords appear in the description but only in service of
the converter purpose.
