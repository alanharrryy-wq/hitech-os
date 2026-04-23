"""Deterministic switch fixture pack 117.

This pack models a realistic slice of canonical switch inputs and expected
stage_03_switch_resolve outputs. Cases cover default resolution, switch-id
precedence, target-id precedence, invalid overrides, reports_real exclusion,
and deterministic replay semantics. The payload is encoded in Python so the
bundle remains Python-heavy while still shipping concrete golden data.
"""

from __future__ import annotations

PACK_ID = "pack_117"
CANONICAL_INPUTS = []
OVERRIDE_SCENARIOS = []
EXPECTED_OUTCOMES = []
REPLAY_NOTES = []
CANONICAL_INPUTS.append({
    "switch_id": "switch.route.117_01",
    "target_type": "route",
    "target_id": "route.117_01",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/117_01.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/117_01.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_117_01",
    "overrides": {"switch.route.117_01": False},
    "why": "Pack 117 item 01 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_117_01",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.117_01 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 117_01 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/117_01.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.117_02",
    "target_type": "boundary",
    "target_id": "boundary.117_02",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/117_02.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/117_02.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_117_02",
    "overrides": {"switch.boundary.117_02": "invalid"},
    "why": "Pack 117 item 02 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_117_02",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.117_02 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 117_02 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/117_02.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.117_03",
    "target_type": "module",
    "target_id": "module.117_03",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/117_03.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/117_03.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_117_03",
    "overrides": {"switch.module.117_03": None},
    "why": "Pack 117 item 03 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_117_03",
    "resolved_value": True,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.117_03 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 117_03 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/117_03.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.117_04",
    "target_type": "route",
    "target_id": "route.117_04",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/117_04.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/117_04.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_117_04",
    "overrides": {"switch.route.117_04": True},
    "why": "Pack 117 item 04 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_117_04",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.117_04 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 117_04 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/117_04.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.117_05",
    "target_type": "boundary",
    "target_id": "boundary.117_05",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/117_05.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/117_05.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_117_05",
    "overrides": {"switch.boundary.117_05": False},
    "why": "Pack 117 item 05 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_117_05",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.117_05 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 117_05 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/117_05.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.117_06",
    "target_type": "module",
    "target_id": "module.117_06",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/117_06.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/117_06.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_117_06",
    "overrides": {"switch.module.117_06": "invalid"},
    "why": "Pack 117 item 06 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_117_06",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.117_06 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 117_06 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/117_06.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.117_07",
    "target_type": "route",
    "target_id": "route.117_07",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/117_07.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/117_07.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_117_07",
    "overrides": {"switch.route.117_07": None},
    "why": "Pack 117 item 07 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_117_07",
    "resolved_value": True,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.route.117_07 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 117_07 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/117_07.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.117_08",
    "target_type": "boundary",
    "target_id": "boundary.117_08",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/117_08.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/117_08.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_117_08",
    "overrides": {"switch.boundary.117_08": True},
    "why": "Pack 117 item 08 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_117_08",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.117_08 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 117_08 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/117_08.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.117_09",
    "target_type": "module",
    "target_id": "module.117_09",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/117_09.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/117_09.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_117_09",
    "overrides": {"switch.module.117_09": False},
    "why": "Pack 117 item 09 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_117_09",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.117_09 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 117_09 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/117_09.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.117_10",
    "target_type": "route",
    "target_id": "route.117_10",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/117_10.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/117_10.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_117_10",
    "overrides": {"switch.route.117_10": "invalid"},
    "why": "Pack 117 item 10 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_117_10",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.route.117_10 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 117_10 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/117_10.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.117_11",
    "target_type": "boundary",
    "target_id": "boundary.117_11",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/117_11.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/117_11.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_117_11",
    "overrides": {"switch.boundary.117_11": None},
    "why": "Pack 117 item 11 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_117_11",
    "resolved_value": True,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.boundary.117_11 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 117_11 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/117_11.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.117_12",
    "target_type": "module",
    "target_id": "module.117_12",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/117_12.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/117_12.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_117_12",
    "overrides": {"switch.module.117_12": True},
    "why": "Pack 117 item 12 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_117_12",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.117_12 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 117_12 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/117_12.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.117_13",
    "target_type": "route",
    "target_id": "route.117_13",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/117_13.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/117_13.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_117_13",
    "overrides": {"switch.route.117_13": False},
    "why": "Pack 117 item 13 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_117_13",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.117_13 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 117_13 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/117_13.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.117_14",
    "target_type": "boundary",
    "target_id": "boundary.117_14",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/117_14.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/117_14.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_117_14",
    "overrides": {"switch.boundary.117_14": "invalid"},
    "why": "Pack 117 item 14 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_117_14",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.117_14 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 117_14 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/117_14.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.117_15",
    "target_type": "module",
    "target_id": "module.117_15",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/117_15.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/117_15.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_117_15",
    "overrides": {"switch.module.117_15": None},
    "why": "Pack 117 item 15 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_117_15",
    "resolved_value": True,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.117_15 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 117_15 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/117_15.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.117_16",
    "target_type": "route",
    "target_id": "route.117_16",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/117_16.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/117_16.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_117_16",
    "overrides": {"switch.route.117_16": True},
    "why": "Pack 117 item 16 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_117_16",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.117_16 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 117_16 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/117_16.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.117_17",
    "target_type": "boundary",
    "target_id": "boundary.117_17",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/117_17.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/117_17.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_117_17",
    "overrides": {"switch.boundary.117_17": False},
    "why": "Pack 117 item 17 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_117_17",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.117_17 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 117_17 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/117_17.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.117_18",
    "target_type": "module",
    "target_id": "module.117_18",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/117_18.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/117_18.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_117_18",
    "overrides": {"switch.module.117_18": "invalid"},
    "why": "Pack 117 item 18 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_117_18",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.117_18 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 117_18 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/117_18.json")

def iter_case_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for canonical, scenario, expected, note in zip(CANONICAL_INPUTS, OVERRIDE_SCENARIOS, EXPECTED_OUTCOMES, REPLAY_NOTES):
        row = dict(canonical)
        row.update({"scenario": scenario, "expected": expected, "note": note})
        rows.append(row)
    return rows
