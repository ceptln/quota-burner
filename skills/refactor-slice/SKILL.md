---
name: "refactor-slice"
description: "Use to refactor one bounded area for better architecture: extract responsibilities, respect layers, simplify with identical behavior."
---

Read `.quota-burner/CONTRACT.md` and the configured team context before targeting. Standalone invocation follows repository permissions and does not authorize a PR by itself.

Refactor ONE bounded area so it better matches your house architecture, with identical behavior.

Targeting: pick the area that most violates the architecture rules in your guidelines files; if you have an audit or review skill, use its rubric as the selection lens (never execute a full audit).

Done: tests green, no behavior change, the area reads simpler than before.
