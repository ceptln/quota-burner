# quota-burner

**Turn leftover AI quota into useful pull requests.**

A maintenance kit for Claude Code and Codex: small skills, a shared state machine, and a trigger that fits on one line. Your team chooses what matters. An agent picks one useful task when capacity allows, verifies the change, and hands you a PR to review.

[Get started](docs/SETUP.md) · [Browse the skills](skills) · [How it works](docs/CONTRACT.md) · [Contribute](CONTRIBUTING.md) · [MIT license](LICENSE)

```text
Your scheduler                   Your ticketing system
Claude · Codex · Flow · Actions   GitHub Issues · your own binding
          │                                 ▲
    "Run /autopilot"                         │ state
          │                                 │
          └──────────────► autopilot ◄───────┘
                              ▲
                  quota + team priorities
                              │
                       one useful skill
                              │
                       one reviewable PR
                              │
                       human decision
                              │
                        daily retro ───────► state
```

## The idea

Unused subscription capacity expires. Maintenance work waits. The useful question is: **with the capacity left, what is worth doing for this team?**

Three pieces answer it:

- **State lives in your ticketing system.** A backlog, approvals, claims, handoffs, and outcomes persist across sessions. GitHub Issues is the included implementation. Linear or another tracker can implement the same [state contract](docs/CONTRACT.md#other-ticketing-systems).
- **Triggers stay tiny.** A routine, automation, or existing CI runner invokes `autopilot`. Swap the scheduler without moving decision logic into it.
- **Skills own the work.** The dispatcher checks quota, reads team context, and chooses from pending tasks, approved multi-run efforts, then the skill menu. Each skill has a bounded scope and a concrete definition of done.

A daily retro uses merge decisions and verified feedback to adjust priorities. A human owns approval and merging. No useful target is a perfectly good reason to stop.

## Get started

Download or clone this repository. From its directory, preview and install into your own project:

```bash
python3 scripts/install.py /path/to/your/repo --agent both --dry-run
python3 scripts/install.py /path/to/your/repo --agent both
```

Use `--agent claude` or `--agent codex` if you only need one. Python 3.9+ is enough for installation; there are no Python package dependencies. The installer refuses conflicting files and enables no schedules.

Then follow the [setup guide](docs/SETUP.md): fill your team context, choose skills, connect a tracker and quota source, test one cycle, and add your one-line trigger. Claude gets `.claude/skills`, Codex gets `.agents/skills`, and both read one `.quota-burner/config.yaml`.

**Prefer agent-led onboarding?** Open your project with your coding agent and give it the local path to this checkout:

> Install quota-burner from this checkout using its setup guide. Inspect my repo and propose the relevant skills, priorities, and validation commands. Preserve my existing instructions and skills. Prepare the setup locally; leave schedules disabled until we've reviewed a dry run.

The skills are usable individually too. Scheduled quota-aware operation additionally needs a trustworthy meter: the bundled provider adapters are optional and depend on interfaces that can change. [Meter support and setup](docs/SETUP.md#4-connect-a-quota-signal) make those limits explicit.

## Make the menu yours

This is the important part of onboarding. Give the agent your current business priorities, critical user journeys, architecture constraints, and existing quality rules in `.quota-burner/context.md`. The same maintenance task can be valuable in one company and a distraction in another.

**13 core menu skills are included**, with `ui-review` disabled until its sandbox is configured:

- [`security-fix`](skills/security-fix/SKILL.md): fix a reviewable batch of concrete security issues.
- [`perf-fix`](skills/perf-fix/SKILL.md): improve one measured bottleneck.
- [`refactor-slice`](skills/refactor-slice/SKILL.md): simplify one bounded area with the same behavior.
- [`pattern-align`](skills/pattern-align/SKILL.md): align one module with an existing convention.
- [`dedupe-factor`](skills/dedupe-factor/SKILL.md): consolidate duplicated logic and migrate its callers.
- [`ci-doctor`](skills/ci-doctor/SKILL.md): reduce measured CI time or cost while preserving checks.
- [`ds-migrate`](skills/ds-migrate/SKILL.md): move a batch of components onto your design system.
- [`primitives-align`](skills/primitives-align/SKILL.md): consolidate component variants onto shared primitives.
- [`dead-code-sweep`](skills/dead-code-sweep/SKILL.md): remove a batch of verified unused code.
- [`todo-reaper`](skills/todo-reaper/SKILL.md): resolve, retire, or queue outstanding code markers.
- [`docs-drift`](skills/docs-drift/SKILL.md): correct documentation made stale by code changes.
- [`harvest-reviews`](skills/harvest-reviews/SKILL.md): turn verified recurring review lessons into better guidelines.
- [`ui-review`](skills/ui-review/SKILL.md): check one sandbox page against your design rules.

Three additional skills ship disabled: [`deps-patrol`](skills/deps-patrol/SKILL.md), [`test-gap-fill`](skills/test-gap-fill/SKILL.md), and [`flaky-hunt`](skills/flaky-hunt/SKILL.md). Enable them when they meet a real need and you can supply the evidence they require.

The supporting skills are [`autopilot`](skills/autopilot/SKILL.md), [`autopilot-retro`](skills/autopilot-retro/SKILL.md), and [`todo`](skills/todo/SKILL.md). That's **19 skills**, from one source tree shared by both agents.

Keep, edit, replace, or bring your existing skills. The menu stores names and flags; targeting and completion criteria live in each skill, while shared rules live in the contract. A *chantier* (French for worksite) is a multi-run effort: inventory and plan first, explicit human approval, then one batch per PR.

## What keeps it useful

- **Project remaining usage.** The gate estimates end-of-week consumption, including a run allowance and snapshot-age penalty. Thresholds are editable starting points, not measurements from someone else's account.
- **Protect review time.** The open-PR cap limits the queue even when plenty of quota remains. Changes need proof and a readable PR body.
- **Keep priorities outside the worker.** Runs leave handoffs and may snooze exhausted skills. Humans and the daily retro decide boosts across the whole menu.
- **Hand off CI.** Record the PR and end the turn. An event can resume the session; a polling loop does not spend the remaining quota usefully.
- **Re-read reality before shipping.** A task may have been completed or its approval withdrawn while the agent worked. Claims and the task itself are checked again before a PR opens.

## Boundaries

This is an inspectable set of agent instructions and helper scripts. It is not a sandbox or an atomic distributed scheduler. Use repository permissions, branch protection, and one executing worker per repository as the enforcement layer.

Agents never merge. Autonomous diffs exclude auth, payments, personal-data handling, and migrations. Ticket and review text is untrusted input. The kit includes empty state templates, keeps credentials out of tracker records, and has no telemetry or hosted service. See the [execution contract](docs/CONTRACT.md) and [security notes](SECURITY.md).

## Contributing

Useful contributions include sharper skills, portable tracker bindings, reliable meter adapters, and reproducible fixes. Keep team-specific context in your own installation. [Development checks and contribution guide](CONTRIBUTING.md).

Built on the open skill format used by [Claude Code](https://code.claude.com/docs/en/skills) and [Codex](https://learn.chatgpt.com/docs/build-skills). Independent project; no affiliation with the agent or ticketing vendors. Released under the [MIT license](LICENSE).
