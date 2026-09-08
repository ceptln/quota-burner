---
name: "ui-review"
description: "Use to review one app page per run in a sandbox environment: screenshots, design-system deviations, UX of the main flow; fixes objective deviations only. Chantier: needs an approved chantier issue and a sandbox target."
---

Read `.quota-burner/CONTRACT.md` and the configured team context before targeting. Standalone invocation follows repository permissions and does not authorize a PR by itself.

Review ONE app page per run in a sandbox environment, and fix the objective deviations found.

Targeting: page rotation lives in the chantier issue; your design system defines "objective deviation". Use the available browser tooling for before/after screenshots at desktop and mobile sizes, including key states.

Done: PR with before/after screenshots from synthetic sandbox data, attached through the repository’s review flow. Never a redesign: ambitious ideas become issues, not diffs.

Requires a sandbox target (deployed URL + test credentials) and its domains in your session's network allowlist; keep disabled until they exist.
