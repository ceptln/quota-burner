---
name: "deps-patrol"
description: "Use to upgrade dependencies minor and patch in one batch after reading changelogs; each major gets its own dedicated PR."
---

Read `.quota-burner/CONTRACT.md` and the configured team context before targeting. Standalone invocation follows repository permissions and does not authorize a PR by itself.

Upgrade dependencies safely, one batch per run.

Targeting: your package manager's outdated listing; read changelogs before bumping.

Done: lockfile updated, tests green, breaking-change notes in the PR body.
