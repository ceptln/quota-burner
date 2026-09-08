---
name: "flaky-hunt"
description: "Use to detect a flaky test via reruns and fix it."
---

Read `.quota-burner/CONTRACT.md` and the configured team context before targeting. Standalone invocation follows repository permissions and does not authorize a PR by itself.

Find one flaky test and fix it.

Targeting: CI history and repeated local runs.

Done: reproduce the failure, fix its cause, and report the result over repeated runs with the run count. Disabling or quarantining a test requires a human decision.
