---
name: "dedupe-factor"
description: "Use to find duplicated logic (copy-paste, redundant helpers) and factor it into shared primitives."
---

Read `.quota-burner/CONTRACT.md` and the configured team context before targeting. Standalone invocation follows repository permissions and does not authorize a PR by itself.

Find duplicated logic and factor it into shared primitives, one coherent batch per run.

Targeting: similarity across one side of the codebase; where the shared primitive should live follows your guidelines.

Done: duplication removed, all call sites migrated, tests green.
