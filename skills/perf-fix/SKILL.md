---
name: "perf-fix"
description: "Use to fix one measured performance problem on an endpoint, query, or render path: N+1, oversized payload, slow component."
---

Read `.quota-burner/CONTRACT.md` and the configured team context before targeting. Standalone invocation follows repository permissions and does not authorize a PR by itself.

Fix ONE measured performance problem, chosen for impact.

Targeting: hot paths and recently touched endpoints/queries; your guidelines define what "fast enough" means.

Schema or index findings are handed over under the shared sensitive-scope rule.

Done: before/after measurement in the PR description; behavior unchanged.
