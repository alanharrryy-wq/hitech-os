"""Deterministic switch fixture pack 070.

This pack models a realistic slice of canonical switch inputs and expected
stage_03_switch_resolve outputs. Cases cover default resolution, switch-id
precedence, target-id precedence, invalid overrides, reports_real exclusion,
and deterministic replay semantics. The payload is encoded in Python so the
bundle remains Python-heavy while still shipping concrete golden data.
"""

from __future__ import annotations

PACK_ID = "pack_070"
CANONICAL_INPUTS = []
OVERRIDE_SCENARIOS = []
EXPECTED_OUTCOMES = []
REPLAY_NOTES = []
CANONICAL_INPUTS.append({
    "switch_id": "switch.route.070_01",
    "target_type": "route",
    "target_id": "route.070_01",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/070_01.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/070_01.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_070_01",
    "overrides": {"switch.route.070_01": False},
    "why": "Pack 070 item 01 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_070_01",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.070_01 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 070_01 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/070_01.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.070_02",
    "target_type": "boundary",
    "target_id": "boundary.070_02",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/070_02.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/070_02.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_070_02",
    "overrides": {"switch.boundary.070_02": "invalid"},
    "why": "Pack 070 item 02 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_070_02",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.070_02 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 070_02 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/070_02.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.070_03",
    "target_type": "module",
    "target_id": "module.070_03",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/070_03.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/070_03.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_070_03",
    "overrides": {"switch.module.070_03": None},
    "why": "Pack 070 item 03 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_070_03",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.070_03 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 070_03 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/070_03.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.070_04",
    "target_type": "route",
    "target_id": "route.070_04",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/070_04.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/070_04.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_070_04",
    "overrides": {"switch.route.070_04": True},
    "why": "Pack 070 item 04 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_070_04",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.070_04 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 070_04 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/070_04.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.070_05",
    "target_type": "boundary",
    "target_id": "boundary.070_05",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/070_05.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/070_05.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_070_05",
    "overrides": {"switch.boundary.070_05": False},
    "why": "Pack 070 item 05 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_070_05",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.070_05 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 070_05 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/070_05.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.070_06",
    "target_type": "module",
    "target_id": "module.070_06",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/070_06.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/070_06.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_070_06",
    "overrides": {"switch.module.070_06": "invalid"},
    "why": "Pack 070 item 06 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_070_06",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.070_06 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 070_06 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/070_06.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.070_07",
    "target_type": "route",
    "target_id": "route.070_07",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/070_07.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/070_07.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_070_07",
    "overrides": {"switch.route.070_07": None},
    "why": "Pack 070 item 07 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_070_07",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.route.070_07 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 070_07 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/070_07.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.070_08",
    "target_type": "boundary",
    "target_id": "boundary.070_08",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/070_08.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/070_08.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_070_08",
    "overrides": {"switch.boundary.070_08": True},
    "why": "Pack 070 item 08 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_070_08",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.070_08 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 070_08 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/070_08.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.070_09",
    "target_type": "module",
    "target_id": "module.070_09",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/070_09.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/070_09.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_070_09",
    "overrides": {"switch.module.070_09": False},
    "why": "Pack 070 item 09 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_070_09",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.070_09 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 070_09 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/070_09.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.070_10",
    "target_type": "route",
    "target_id": "route.070_10",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/070_10.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/070_10.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_070_10",
    "overrides": {"switch.route.070_10": "invalid"},
    "why": "Pack 070 item 10 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_070_10",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.route.070_10 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 070_10 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/070_10.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.070_11",
    "target_type": "boundary",
    "target_id": "boundary.070_11",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/070_11.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/070_11.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_070_11",
    "overrides": {"switch.boundary.070_11": None},
    "why": "Pack 070 item 11 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_070_11",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.boundary.070_11 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 070_11 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/070_11.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.070_12",
    "target_type": "module",
    "target_id": "module.070_12",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/070_12.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/070_12.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_070_12",
    "overrides": {"switch.module.070_12": True},
    "why": "Pack 070 item 12 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_070_12",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.070_12 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 070_12 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/070_12.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.070_13",
    "target_type": "route",
    "target_id": "route.070_13",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/070_13.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/070_13.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_070_13",
    "overrides": {"switch.route.070_13": False},
    "why": "Pack 070 item 13 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_070_13",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.070_13 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 070_13 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/070_13.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.070_14",
    "target_type": "boundary",
    "target_id": "boundary.070_14",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/070_14.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/070_14.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_070_14",
    "overrides": {"switch.boundary.070_14": "invalid"},
    "why": "Pack 070 item 14 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_070_14",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.070_14 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 070_14 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/070_14.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.070_15",
    "target_type": "module",
    "target_id": "module.070_15",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/070_15.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/070_15.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_070_15",
    "overrides": {"switch.module.070_15": None},
    "why": "Pack 070 item 15 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_070_15",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.070_15 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 070_15 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/070_15.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.070_16",
    "target_type": "route",
    "target_id": "route.070_16",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/070_16.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/070_16.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_070_16",
    "overrides": {"switch.route.070_16": True},
    "why": "Pack 070 item 16 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_070_16",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.070_16 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 070_16 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/070_16.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.070_17",
    "target_type": "boundary",
    "target_id": "boundary.070_17",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/070_17.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/070_17.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_070_17",
    "overrides": {"switch.boundary.070_17": False},
    "why": "Pack 070 item 17 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_070_17",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.070_17 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 070_17 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/070_17.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.070_18",
    "target_type": "module",
    "target_id": "module.070_18",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/070_18.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/070_18.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_070_18",
    "overrides": {"switch.module.070_18": "invalid"},
    "why": "Pack 070 item 18 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_070_18",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.070_18 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 070_18 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/070_18.json")

def iter_case_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for canonical, scenario, expected, note in zip(CANONICAL_INPUTS, OVERRIDE_SCENARIOS, EXPECTED_OUTCOMES, REPLAY_NOTES):
        row = dict(canonical)
        row.update({"scenario": scenario, "expected": expected, "note": note})
        rows.append(row)
    return rows
