---
name: "dead-code-sweep"
description: "Use to remove dead code: unused exports, unreachable branches, commented-out code, orphan helpers."
---

Read `.quota-burner/CONTRACT.md` and the configured team context before targeting. Standalone invocation follows repository permissions and does not authorize a PR by itself.

Remove dead code in confidence-ordered batches.

Targeting: the static dead-code tools for your stack (knip, ts-prune, vulture, deadcode); take one reviewable batch from most to least certain. Check dynamic loading, configured scan exclusions, stylesheets, assets, and public entry points before treating an unreported reference as absent.

Done: build, typecheck, and tests green; uncertain candidates listed in the PR body, not deleted (dynamic imports, reflection, and externally consumed APIs are the classic false positives).
