---
name: "security-fix"
description: "Use to find and fix one batch of concrete security issues: vulnerable dependencies, injection risks, secrets in code, unsafe patterns."
---

Read `.quota-burner/CONTRACT.md` and the configured team context before targeting. Standalone invocation follows repository permissions and does not authorize a PR by itself.

Find and fix one batch of concrete security issues, sized for a single reviewable PR.

Targeting: dependency advisories plus your security-review rubric if you have one, else your guidelines files (CLAUDE.md, AGENTS.md, or dedicated guidelines docs).

Done: fix with tests green. Findings in sensitive scopes (auth, payments) are not fixed autonomously: list them in the PR body by file and line, never with secret values.
