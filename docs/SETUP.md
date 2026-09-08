# Set up your autopilot

The installer only copies files. You choose the team's skills, connect durable state, verify a meter, and finally add a one-line trigger. All paths below are relative to your target repository.

## 1. Install the pack

From the downloaded quota-burner source directory, with Python 3.9 or newer:

```bash
python3 scripts/install.py /path/to/your/repo --agent both --dry-run
python3 scripts/install.py /path/to/your/repo --agent both
```

Use `--agent claude` or `--agent codex` for one agent. Claude receives `.claude/skills/`; Codex receives `.agents/skills/`, its documented repository skill location. The source files are identical, with quoted frontmatter compatible with both. Shared configuration, instructions, templates, and optional meter scripts live under `.quota-burner/`. No global agent settings are touched. See [Claude skills](https://code.claude.com/docs/en/skills) and [Codex skills](https://learn.chatgpt.com/docs/build-skills).

Existing files with identical content are skipped. Any different destination file aborts the entire preflight before writes; there is no force flag. If your repository already has a skill with the same name, compare the two, retain or adapt your own implementation, and copy the remaining desired files manually. The installed menu can name your existing skills. On upgrades, use a temporary installation to compare and merge changes, keeping your context and config. Reconcile any legacy `.codex/skills` copies yourself so a skill is not loaded twice.

You can also copy skills by hand. Copy their shared contract from `docs/CONTRACT.md`, config from `skills/autopilot/config.example.yaml`, and context from `templates/context.md` to the corresponding `.quota-burner/` destinations. These references are required, even when you use only one menu skill. In a target repository that mirrors Claude skills into `.codex/skills`, follow its convention and keep the bodies identical.

## 2. Make it yours

Fill `.quota-burner/context.md`: business priorities, important user journeys, technical constraints, existing guideline paths, validation commands, and delivery conventions. The agent should learn why a fix matters from this file and how to implement it from your existing documentation. Set `Setup: ready` only after replacing the prompts.

Edit `.quota-burner/config.yaml` to keep only relevant menu entries enabled. The source example owns the defaults; the installed file owns your policy. No frontend? Disable the UI/design-system entries. Already have a dependency bot? Leave `deps-patrol` disabled. No profiler or coverage report? Supply evidence or disable the corresponding skill. Set a review cap you can actually absorb, and adjust the run-cost estimate from observation.

The bundled skills reference your context rather than a prescribed framework or directory structure. Add your own skill by installing it in each agent's skill directory and adding its name to the shared menu. Give it a bounded target and an observable completion criterion. The dispatcher, not the trigger, resolves that name.

Record which unattended writes the owner authorizes. Repository instructions still win: a skill does not override a policy that forbids autonomous commits or PRs. Agent tools must already support the permitted git and ticketing operations, plus the project's build and test commands. This pack does not require a private `/pr`, audit, Slack, or review-bot skill.

## 3. Connect the state store

The included binding uses GitHub Issues. In your target repository, authenticate `gh` (or your agent's GitHub connector), then create these labels if absent:

```bash
gh label create autopilot-hub --color 7057ff --description 'Autopilot state hub'
gh label create autopilot-chantier --color 7057ff --description 'Approved multi-run maintenance'
gh label create autopilot --color 0e8a16 --description 'Maintenance PRs'
gh label create review-lessons --color fbca04 --description 'Verified review lessons'
gh issue create --title 'Autopilot hub' --label autopilot-hub --body-file .quota-burner/templates/hub-issue.md
```

Check first that no open hub already exists. Pin the hub for convenience. The template has an empty queue, so onboarding cannot accidentally launch a sample task. Agents need repository read/write and issue/PR access only where authorized. Keep production credentials outside the maintenance environment.

Prefer Linear or another ticketing tool? Map the records and operations in `.quota-burner/CONTRACT.md` to that tool, provide its connector, and update the binding and config. This is an adaptation step, not a shipped Linear integration. Keep a single executing worker per repository unless your tracker adapter implements atomic claims and capacity reservations.

## 4. Connect a quota signal

Each provider needs its own fresh, trusted snapshot. Claude usage cannot gate Codex, and journal counting is not a usage meter. A missing, expired, malformed, or unsupported window blocks the cycle. The gate requires both five-hour and weekly windows; a plan that exposes only one needs an explicitly designed alternative gate before unattended use.

The bundled meters are **optional compatibility adapters**, not official quota APIs. The Claude adapter makes a one-output-token model request and reads response headers. The Codex adapter reads an internal usage endpoint. Either can change or be unavailable for your account. The scripts normalize only quota fields; they publish no account ID, plan, token, prompt, or response body. Authentication failures publish nothing.

Verify provider permissions and account support before enabling an adapter. Anthropic documents restrictions on subscription OAuth credential use; this pack does not offer a hosted login, collect credentials, or promise that direct API use of subscription tokens is supported. Keep authentication in provider-approved flows and use another authorized quota source where needed. See [Anthropic credential rules](https://code.claude.com/docs/en/legal-and-compliance) and [Codex authentication](https://developers.openai.com/codex/auth/). API-funded agent runs need an API spending policy instead of a subscription gate.

### Claude: optional GitHub meter

Only if this access method is permitted for your account, provision a token through the provider's own flow and save it as the repository secret `CLAUDE_AUTOPILOT_TOKEN`. Do not paste it into a chat, issue, command argument, or tracked file.

Copy `.quota-burner/workflows/autopilot-meter.yml` to `.github/workflows/autopilot-meter.yml` and review it. It checks out the default branch, pins the action by commit, has a timeout, and publishes only normalized usage. After the files reach the default branch, set repository variable `QUOTA_BURNER_CLAUDE_METER_ENABLED` to `true`, then run the workflow manually once. The scheduled meter runs hourly. Installation does not enable it.

The expected publisher is `github-actions[bot]`, already set in config. Confirm the hub has an `autopilot-meter: claude` comment with a current `taken_at`, two windows, and `overage_utilization`. Never print the secret to debug a failure. Runner time and the inference request can incur charges; check your account's billing settings. The gate is an estimate, not a billing hard limit. Disable paid extra usage in provider settings if you require a hard subscription-only boundary.

### Codex: optional local meter

On a trusted machine with Python, Bash, curl, `gh`, and an existing authorized file-backed Codex ChatGPT login, set `meter.trusted_authors.codex` to the exact login that will publish snapshots (`gh api user --jq .login`). From the target repository:

```bash
set -o pipefail
python3 .quota-burner/scripts/codex-meter-local.py |
  python3 .quota-burner/scripts/publish-meter.py --repo OWNER/REPO
```

Replace `OWNER/REPO` with your target repository. The local wrapper reads the current access token from the configured Codex home, invokes the collector, and never stores or refreshes credentials. Use `--auth-file` only if your credential file lives elsewhere. A keychain-backed login needs an authorized adapter for that store; do not change your credential-storage policy just for this kit. If the token expires, renew your session in Codex. Do not upload `auth.json` or refresh tokens to GitHub Actions.

The low-level `codex-meter.sh` also accepts `CODEX_ACCESS_TOKEN` and optional `CODEX_ACCOUNT_ID` from an operator-managed environment. The parser maps windows by duration, never by whether the API called one primary or secondary. Check the resulting `autopilot-meter: codex` comment, then schedule this same pipeline hourly on the trusted machine if desired. Avoid concurrent publishers for the same provider. Each provider's snapshot retains its own timestamp and author.

### Bring your own meter

Publish the same normalized schema through an authenticated writer. `scripts/parse_meter.py` owns the bundled adapters' normalization; the gate contract is in the autopilot skill. The publisher accepts one provider per input and strips extra fields. A snapshot carries `taken_at` in timezone-qualified ISO format and a `claude` or `codex` object with `five_hour` and `seven_day` objects. Each window has `utilization` (fraction), `resets_at` (epoch seconds), and `window_seconds` (18000 or 604800). Claude adds `overage_utilization`; Codex adds `limit_reached` (boolean).

Keep snapshot publication on its own schedule. Work triggers read existing state and never request or wait for a meter refresh.

## 5. Test before scheduling

Invoke the installed autopilot skill with: `Dry run one cycle. Read state and explain the gate and proposed target; write nothing.` Verify that it finds the intended hub, uses its own provider's snapshot, reads your priorities, and resolves enabled skills. NO-GO is the expected result until setup and metering are complete.

Run one live cycle manually after authorizing its delivery permissions. Review its scope, proof, PR, and hub handoff. It should also exit cleanly when there is no useful target; a PR is not mandatory.

## 6. Add lightweight triggers

Choose the scheduler you already use. Each maintenance trigger has the same job: invoke `autopilot` in the configured repository. A second trigger invokes `autopilot-retro` daily. For example:

| Host | Maintenance prompt | Retro prompt |
| --- | --- | --- |
| Claude routine or desktop task | `Run /autopilot` | `Run /autopilot-retro` |
| Codex scheduled task | `Run the autopilot skill for one cycle.` | `Run the autopilot-retro skill.` |
| Flow or another orchestrator | Invoke the installed `autopilot` skill | Invoke the installed `autopilot-retro` skill |
| Your existing CLI/Actions runner | Pass the same prompt to its agent entry point | Pass the retro prompt |

Start with a maintenance wake every two hours, then tune cadence to your review capacity. Scheduling syntax, authentication, checkout, and tools belong to the host; priority, quota arithmetic, and task selection belong to the skills. The shipped GitHub workflow is a meter, not an agent runner.

Use a persistent scheduler: Claude's session-scoped loop is not a durable routine. Local project tasks require the computer and app to remain running; cloud tasks need repository access and an appropriate environment. See [Claude scheduling options](https://code.claude.com/docs/en/scheduled-tasks) and [Codex scheduled tasks](https://learn.chatgpt.com/docs/automations?surface=app).

Commit the installed skills and shared files through your normal review flow before using fresh worktrees or cloud checkouts. Start with one worker, using only the connectors it needs. No work cycle creates another schedule. Notifications remain off unless separately configured and authorized.

## Troubleshooting and removal

- **Skill missing:** check the selected agent's skill directory, required shared files, and any duplicate legacy installation. Reload the session if needed.
- **NO-GO every time:** read Status for the exact rule. Check author, provider, timestamps, reset epochs, required windows, and PR capacity before tuning thresholds.
- **No useful target:** update team context, add a concrete to-do, or disable skills without evidence. Do not lower quality standards to fill a schedule.
- **CI still pending:** the run hands off after opening its PR. Event-capable hosts may resume it once; other hosts leave the result to the reviewer. No polling worker is required.
- **Pause:** disable work and retro triggers first, then the optional meter schedule. Existing PRs remain for human review.
- **Uninstall:** stop schedules, remove the installed skill folders you no longer use, `.quota-burner/`, and the optional meter workflow. Remove its secret and variable if unused. Keep tracker history or archive it deliberately; no script deletes it.
