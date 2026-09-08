---
name: "autopilot"
description: "Run one quota-aware maintenance cycle when invoked manually or by a scheduled trigger. Gate on usage, pick useful work, and hand off at most one PR."
---

Read `.quota-burner/CONTRACT.md` and `.quota-burner/config.yaml`. The contract owns state, selection, claims, delivery, and trust boundaries. A trigger supplies no policy. Manual invocation follows the same gate.

## Gate first

Locate the unique hub through the configured tracker binding. Read the latest trusted meter snapshot for this session's provider only: Claude uses `claude`, Codex uses `codex`. Never substitute another provider's quota or estimate usage from the run journal. Unknown provider, missing binding, author, fields, or unreadable state means NO-GO.

Require numeric finite utilization fractions in 0..1, integer reset epochs, and `five_hour` / `seven_day` windows of 18000 / 604800 seconds. Require a timezone-qualified `taken_at` no later than now. Missing or inconsistent data means NO-GO. A reset at or before now also means NO-GO: get a new scheduled snapshot; never infer that new-window consumption is zero. Resets cannot be farther away than their window length.

Compute the weekly elapsed share at the sampling time from the weekly reset and window length. Project at that instant, then add the age penalty:

- `elapsed = 1 - (seven_day.resets_at - taken_at) / 604800`, constrained to 0..1.
- `weekly_points = 100 * seven_day.utilization`.
- `projected = weekly_points + weekly_points * (1 - elapsed) / max(elapsed, gate.rate_floor) + gate.run_cost_points + gate.staleness_points_per_hour * age_hours`.

NO-GO if the snapshot exceeds `snapshot_max_age_minutes`, projection exceeds `weekly_ceiling_points`, five-hour utilization exceeds `five_hour_max`, or open autopilot PRs reach `max_open_prs`. Claude also requires `overage_utilization <= overage_max`; Codex requires `limit_reached: false`. Config values must be sensible nonnegative numbers, with `0 < rate_floor <= 1`, positive age/PR limits, and utilization caps at most 1. Invalid config means NO-GO.

On NO-GO, update only the hub's `Status` section with wake time, result, projection terms, and consecutive NO-GO count since the last GO; then exit. A dry run reports the same decision in the session and writes nothing. Do not dispatch a meter or poll for fresh data.

## One useful unit

Once the gate passes, read the configured team context and follow the contract's selection order. A dry run explains the proposed target and missing setup without claiming it or writing anything. Live runs claim the target, invoke its installed skill by name, and follow its targeting and completion criterion. If nothing is eligible or the search is empty, report that result without opening an empty PR.

Reconcile state immediately before delivery. Write the handoff and outcome before ending the turn; CI follows the contract's event-based handoff. A successful gate is permission to consider work, never a reason to invent work.
