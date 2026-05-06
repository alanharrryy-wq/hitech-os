"""Deterministic switch fixture pack 102.

This pack models a realistic slice of canonical switch inputs and expected
stage_03_switch_resolve outputs. Cases cover default resolution, switch-id
precedence, target-id precedence, invalid overrides, reports_real exclusion,
and deterministic replay semantics. The payload is encoded in Python so the
bundle remains Python-heavy while still shipping concrete golden data.
"""

from __future__ import annotations

PACK_ID = "pack_102"
CANONICAL_INPUTS = []
OVERRIDE_SCENARIOS = []
EXPECTED_OUTCOMES = []
REPLAY_NOTES = []
CANONICAL_INPUTS.append({
    "switch_id": "switch.route.102_01",
    "target_type": "route",
    "target_id": "route.102_01",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/102_01.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/102_01.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_102_01",
    "overrides": {"switch.route.102_01": False},
    "why": "Pack 102 item 01 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_102_01",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.102_01 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 102_01 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/102_01.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.102_02",
    "target_type": "boundary",
    "target_id": "boundary.102_02",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/102_02.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/102_02.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_102_02",
    "overrides": {"switch.boundary.102_02": "invalid"},
    "why": "Pack 102 item 02 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_102_02",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.102_02 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 102_02 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/102_02.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.102_03",
    "target_type": "module",
    "target_id": "module.102_03",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/102_03.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/102_03.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_102_03",
    "overrides": {"switch.module.102_03": None},
    "why": "Pack 102 item 03 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_102_03",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.102_03 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 102_03 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/102_03.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.102_04",
    "target_type": "route",
    "target_id": "route.102_04",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/102_04.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/102_04.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_102_04",
    "overrides": {"switch.route.102_04": True},
    "why": "Pack 102 item 04 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_102_04",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.102_04 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 102_04 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/102_04.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.102_05",
    "target_type": "boundary",
    "target_id": "boundary.102_05",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/102_05.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/102_05.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_102_05",
    "overrides": {"switch.boundary.102_05": False},
    "why": "Pack 102 item 05 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_102_05",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.102_05 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 102_05 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/102_05.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.102_06",
    "target_type": "module",
    "target_id": "module.102_06",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/102_06.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/102_06.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_102_06",
    "overrides": {"switch.module.102_06": "invalid"},
    "why": "Pack 102 item 06 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_102_06",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.102_06 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 102_06 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/102_06.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.102_07",
    "target_type": "route",
    "target_id": "route.102_07",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/102_07.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/102_07.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_102_07",
    "overrides": {"switch.route.102_07": None},
    "why": "Pack 102 item 07 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_102_07",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.route.102_07 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 102_07 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/102_07.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.102_08",
    "target_type": "boundary",
    "target_id": "boundary.102_08",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/102_08.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/102_08.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_102_08",
    "overrides": {"switch.boundary.102_08": True},
    "why": "Pack 102 item 08 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_102_08",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.102_08 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 102_08 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/102_08.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.102_09",
    "target_type": "module",
    "target_id": "module.102_09",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/102_09.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/102_09.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_102_09",
    "overrides": {"switch.module.102_09": False},
    "why": "Pack 102 item 09 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_102_09",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.102_09 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 102_09 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/102_09.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.102_10",
    "target_type": "route",
    "target_id": "route.102_10",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/102_10.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/102_10.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_102_10",
    "overrides": {"switch.route.102_10": "invalid"},
    "why": "Pack 102 item 10 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_102_10",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.route.102_10 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 102_10 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/102_10.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.102_11",
    "target_type": "boundary",
    "target_id": "boundary.102_11",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/102_11.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/102_11.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_102_11",
    "overrides": {"switch.boundary.102_11": None},
    "why": "Pack 102 item 11 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_102_11",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.boundary.102_11 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 102_11 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/102_11.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.102_12",
    "target_type": "module",
    "target_id": "module.102_12",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/102_12.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/102_12.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_102_12",
    "overrides": {"switch.module.102_12": True},
    "why": "Pack 102 item 12 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_102_12",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.102_12 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 102_12 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/102_12.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.102_13",
    "target_type": "route",
    "target_id": "route.102_13",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/102_13.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/102_13.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_102_13",
    "overrides": {"switch.route.102_13": False},
    "why": "Pack 102 item 13 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_102_13",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.102_13 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 102_13 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/102_13.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.102_14",
    "target_type": "boundary",
    "target_id": "boundary.102_14",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/102_14.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/102_14.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_102_14",
    "overrides": {"switch.boundary.102_14": "invalid"},
    "why": "Pack 102 item 14 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_102_14",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.102_14 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 102_14 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/102_14.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.102_15",
    "target_type": "module",
    "target_id": "module.102_15",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/102_15.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/102_15.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_102_15",
    "overrides": {"switch.module.102_15": None},
    "why": "Pack 102 item 15 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_102_15",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.102_15 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 102_15 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/102_15.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.102_16",
    "target_type": "route",
    "target_id": "route.102_16",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/102_16.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/102_16.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_102_16",
    "overrides": {"switch.route.102_16": True},
    "why": "Pack 102 item 16 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_102_16",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.102_16 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 102_16 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/102_16.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.102_17",
    "target_type": "boundary",
    "target_id": "boundary.102_17",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/102_17.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/102_17.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_102_17",
    "overrides": {"switch.boundary.102_17": False},
    "why": "Pack 102 item 17 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_102_17",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.102_17 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 102_17 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/102_17.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.102_18",
    "target_type": "module",
    "target_id": "module.102_18",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/102_18.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/102_18.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_102_18",
    "overrides": {"switch.module.102_18": "invalid"},
    "why": "Pack 102 item 18 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_102_18",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.102_18 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 102_18 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/102_18.json")

def iter_case_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for canonical, scenario, expected, note in zip(CANONICAL_INPUTS, OVERRIDE_SCENARIOS, EXPECTED_OUTCOMES, REPLAY_NOTES):
        row = dict(canonical)
        row.update({"scenario": scenario, "expected": expected, "note": note})
        rows.append(row)
    return rows
