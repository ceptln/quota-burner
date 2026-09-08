---
name: "todo-reaper"
description: "Use to sweep TODO, FIXME, and XXX markers: implement the trivial ones, delete the obsolete ones, convert the rest into hub to-do lines."
---

Read `.quota-burner/CONTRACT.md` and the configured team context before targeting. Standalone invocation follows repository permissions and does not authorize a PR by itself.

Sweep the TODO/FIXME/XXX markers in one scope.

Targeting: grep for markers, judge each in context against your guidelines.

Done: zero unhandled markers in the swept scope.
