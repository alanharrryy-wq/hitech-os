"""Deterministic switch fixture pack 064.

This pack models a realistic slice of canonical switch inputs and expected
stage_03_switch_resolve outputs. Cases cover default resolution, switch-id
precedence, target-id precedence, invalid overrides, reports_real exclusion,
and deterministic replay semantics. The payload is encoded in Python so the
bundle remains Python-heavy while still shipping concrete golden data.
"""

from __future__ import annotations

PACK_ID = "pack_064"
CANONICAL_INPUTS = []
OVERRIDE_SCENARIOS = []
EXPECTED_OUTCOMES = []
REPLAY_NOTES = []
CANONICAL_INPUTS.append({
    "switch_id": "switch.route.064_01",
    "target_type": "route",
    "target_id": "route.064_01",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/064_01.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/064_01.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_064_01",
    "overrides": {"switch.route.064_01": False},
    "why": "Pack 064 item 01 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_064_01",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.064_01 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 064_01 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/064_01.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.064_02",
    "target_type": "boundary",
    "target_id": "boundary.064_02",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/064_02.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/064_02.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_064_02",
    "overrides": {"switch.boundary.064_02": "invalid"},
    "why": "Pack 064 item 02 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_064_02",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.064_02 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 064_02 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/064_02.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.064_03",
    "target_type": "module",
    "target_id": "module.064_03",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/064_03.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/064_03.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_064_03",
    "overrides": {"switch.module.064_03": None},
    "why": "Pack 064 item 03 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_064_03",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.064_03 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 064_03 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/064_03.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.064_04",
    "target_type": "route",
    "target_id": "route.064_04",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/064_04.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/064_04.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_064_04",
    "overrides": {"switch.route.064_04": True},
    "why": "Pack 064 item 04 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_064_04",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.064_04 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 064_04 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/064_04.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.064_05",
    "target_type": "boundary",
    "target_id": "boundary.064_05",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/064_05.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/064_05.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_064_05",
    "overrides": {"switch.boundary.064_05": False},
    "why": "Pack 064 item 05 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_064_05",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.064_05 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 064_05 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/064_05.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.064_06",
    "target_type": "module",
    "target_id": "module.064_06",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/064_06.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/064_06.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_064_06",
    "overrides": {"switch.module.064_06": "invalid"},
    "why": "Pack 064 item 06 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_064_06",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.064_06 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 064_06 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/064_06.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.064_07",
    "target_type": "route",
    "target_id": "route.064_07",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/064_07.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/064_07.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_064_07",
    "overrides": {"switch.route.064_07": None},
    "why": "Pack 064 item 07 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_064_07",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.route.064_07 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 064_07 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/064_07.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.064_08",
    "target_type": "boundary",
    "target_id": "boundary.064_08",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/064_08.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/064_08.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_064_08",
    "overrides": {"switch.boundary.064_08": True},
    "why": "Pack 064 item 08 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_064_08",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.064_08 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 064_08 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/064_08.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.064_09",
    "target_type": "module",
    "target_id": "module.064_09",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/064_09.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/064_09.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_064_09",
    "overrides": {"switch.module.064_09": False},
    "why": "Pack 064 item 09 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_064_09",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.064_09 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 064_09 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/064_09.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.064_10",
    "target_type": "route",
    "target_id": "route.064_10",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/064_10.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/064_10.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_064_10",
    "overrides": {"switch.route.064_10": "invalid"},
    "why": "Pack 064 item 10 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_064_10",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.route.064_10 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 064_10 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/064_10.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.064_11",
    "target_type": "boundary",
    "target_id": "boundary.064_11",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/064_11.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/064_11.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_064_11",
    "overrides": {"switch.boundary.064_11": None},
    "why": "Pack 064 item 11 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_064_11",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.boundary.064_11 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 064_11 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/064_11.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.064_12",
    "target_type": "module",
    "target_id": "module.064_12",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/064_12.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/064_12.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_064_12",
    "overrides": {"switch.module.064_12": True},
    "why": "Pack 064 item 12 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_064_12",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.064_12 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 064_12 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/064_12.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.064_13",
    "target_type": "route",
    "target_id": "route.064_13",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/064_13.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/064_13.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_064_13",
    "overrides": {"switch.route.064_13": False},
    "why": "Pack 064 item 13 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_064_13",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.064_13 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 064_13 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/064_13.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.064_14",
    "target_type": "boundary",
    "target_id": "boundary.064_14",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/064_14.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/064_14.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_064_14",
    "overrides": {"switch.boundary.064_14": "invalid"},
    "why": "Pack 064 item 14 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_064_14",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.064_14 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 064_14 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/064_14.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.064_15",
    "target_type": "module",
    "target_id": "module.064_15",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/064_15.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/064_15.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_064_15",
    "overrides": {"switch.module.064_15": None},
    "why": "Pack 064 item 15 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_064_15",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.064_15 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 064_15 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/064_15.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.064_16",
    "target_type": "route",
    "target_id": "route.064_16",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/064_16.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/064_16.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_064_16",
    "overrides": {"switch.route.064_16": True},
    "why": "Pack 064 item 16 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_064_16",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.064_16 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 064_16 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/064_16.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.064_17",
    "target_type": "boundary",
    "target_id": "boundary.064_17",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/064_17.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/064_17.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_064_17",
    "overrides": {"switch.boundary.064_17": False},
    "why": "Pack 064 item 17 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_064_17",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.064_17 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 064_17 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/064_17.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.064_18",
    "target_type": "module",
    "target_id": "module.064_18",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/064_18.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/064_18.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_064_18",
    "overrides": {"switch.module.064_18": "invalid"},
    "why": "Pack 064 item 18 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_064_18",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.064_18 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 064_18 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/064_18.json")

def iter_case_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for canonical, scenario, expected, note in zip(CANONICAL_INPUTS, OVERRIDE_SCENARIOS, EXPECTED_OUTCOMES, REPLAY_NOTES):
        row = dict(canonical)
        row.update({"scenario": scenario, "expected": expected, "note": note})
        rows.append(row)
    return rows
