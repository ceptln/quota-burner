---
name: "docs-drift"
description: "Use to fix stale documentation against recently merged PRs. Never adds new docs; deletes more than it writes."
---

Read `.quota-burner/CONTRACT.md` and the configured team context before targeting. Standalone invocation follows repository permissions and does not authorize a PR by itself.

Fix docs that recent merges made stale. This skill never adds new documentation.

Targeting: recent merged PRs vs whatever ownership map your docs have (an index, a docs folder convention).

Done: zero stale references in the scanned scope.
