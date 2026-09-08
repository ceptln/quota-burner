# Contributing

A useful skill fixes a bounded problem and names the evidence that proves it. A useful adapter preserves the state contract across hosts. Explain the concrete need and include a reproducible example with synthetic data.

## Development

Python 3.9+, Bash, and curl are sufficient. Runtime scripts use the Python standard library. From this repository:

```bash
python3 -m unittest discover -s tests -v
bash -n scripts/claude-meter.sh scripts/codex-meter.sh
shellcheck scripts/claude-meter.sh scripts/codex-meter.sh
```

ShellCheck is optional locally. Tests use temporary directories and fake network clients; they never need provider tokens or GitHub access. Add regression coverage for changed installer, parser, or publisher behavior. Check a fresh installation for each agent before changing the setup guide.

## Where changes belong

- `skills/` is the canonical skill source for both agents. Use quoted `name` and `description` frontmatter. Keep targeting local to the skill and shared rules in `docs/CONTRACT.md`.
- `skills/autopilot/config.example.yaml` owns the initial menu and gate defaults. Installed copies belong to the adopting team.
- `templates/context.md` prompts teams for priorities and pointers to their own rules. Never bake a company's paths, metrics, or practices into the generic pack.
- `scripts/` contains the local installer and optional meters; `workflows/` contains an inert template until explicitly installed and enabled.

Keep tracker and scheduler support claims precise. A documented adaptation contract is different from a working integration. Verify provider behavior against current primary sources, and identify internal interfaces as such.

## Sharing a change

Use a short PR description: problem, resulting behavior, and validation. Include no credentials, private URLs, customer data, real production fixtures, or private operational measurements. Review the full files, not only keyword scan results. For vulnerabilities, follow [SECURITY.md](SECURITY.md).
