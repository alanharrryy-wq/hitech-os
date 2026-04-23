"""Deterministic switch fixture pack 114.

This pack models a realistic slice of canonical switch inputs and expected
stage_03_switch_resolve outputs. Cases cover default resolution, switch-id
precedence, target-id precedence, invalid overrides, reports_real exclusion,
and deterministic replay semantics. The payload is encoded in Python so the
bundle remains Python-heavy while still shipping concrete golden data.
"""

from __future__ import annotations

PACK_ID = "pack_114"
CANONICAL_INPUTS = []
OVERRIDE_SCENARIOS = []
EXPECTED_OUTCOMES = []
REPLAY_NOTES = []
CANONICAL_INPUTS.append({
    "switch_id": "switch.route.114_01",
    "target_type": "route",
    "target_id": "route.114_01",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/114_01.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/114_01.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_114_01",
    "overrides": {"switch.route.114_01": False},
    "why": "Pack 114 item 01 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_114_01",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.114_01 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 114_01 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/114_01.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.114_02",
    "target_type": "boundary",
    "target_id": "boundary.114_02",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/114_02.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/114_02.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_114_02",
    "overrides": {"switch.boundary.114_02": "invalid"},
    "why": "Pack 114 item 02 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_114_02",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.114_02 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 114_02 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/114_02.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.114_03",
    "target_type": "module",
    "target_id": "module.114_03",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/114_03.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/114_03.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_114_03",
    "overrides": {"switch.module.114_03": None},
    "why": "Pack 114 item 03 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_114_03",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.114_03 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 114_03 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/114_03.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.114_04",
    "target_type": "route",
    "target_id": "route.114_04",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/114_04.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/114_04.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_114_04",
    "overrides": {"switch.route.114_04": True},
    "why": "Pack 114 item 04 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_114_04",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.114_04 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 114_04 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/114_04.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.114_05",
    "target_type": "boundary",
    "target_id": "boundary.114_05",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/114_05.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/114_05.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_114_05",
    "overrides": {"switch.boundary.114_05": False},
    "why": "Pack 114 item 05 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_114_05",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.114_05 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 114_05 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/114_05.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.114_06",
    "target_type": "module",
    "target_id": "module.114_06",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/114_06.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/114_06.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_114_06",
    "overrides": {"switch.module.114_06": "invalid"},
    "why": "Pack 114 item 06 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_114_06",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.114_06 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 114_06 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/114_06.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.114_07",
    "target_type": "route",
    "target_id": "route.114_07",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/114_07.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/114_07.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_114_07",
    "overrides": {"switch.route.114_07": None},
    "why": "Pack 114 item 07 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_114_07",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.route.114_07 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 114_07 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/114_07.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.114_08",
    "target_type": "boundary",
    "target_id": "boundary.114_08",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/114_08.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/114_08.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_114_08",
    "overrides": {"switch.boundary.114_08": True},
    "why": "Pack 114 item 08 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_114_08",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.114_08 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 114_08 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/114_08.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.114_09",
    "target_type": "module",
    "target_id": "module.114_09",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/114_09.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/114_09.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_114_09",
    "overrides": {"switch.module.114_09": False},
    "why": "Pack 114 item 09 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_114_09",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.114_09 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 114_09 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/114_09.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.114_10",
    "target_type": "route",
    "target_id": "route.114_10",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/114_10.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/114_10.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_114_10",
    "overrides": {"switch.route.114_10": "invalid"},
    "why": "Pack 114 item 10 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_114_10",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.route.114_10 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 114_10 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/114_10.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.114_11",
    "target_type": "boundary",
    "target_id": "boundary.114_11",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/114_11.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/114_11.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_114_11",
    "overrides": {"switch.boundary.114_11": None},
    "why": "Pack 114 item 11 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_114_11",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.boundary.114_11 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 114_11 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/114_11.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.114_12",
    "target_type": "module",
    "target_id": "module.114_12",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/114_12.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/114_12.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_114_12",
    "overrides": {"switch.module.114_12": True},
    "why": "Pack 114 item 12 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_114_12",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.114_12 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 114_12 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/114_12.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.114_13",
    "target_type": "route",
    "target_id": "route.114_13",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/114_13.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/114_13.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_114_13",
    "overrides": {"switch.route.114_13": False},
    "why": "Pack 114 item 13 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_114_13",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.114_13 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 114_13 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/114_13.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.114_14",
    "target_type": "boundary",
    "target_id": "boundary.114_14",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/114_14.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/114_14.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_114_14",
    "overrides": {"switch.boundary.114_14": "invalid"},
    "why": "Pack 114 item 14 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_114_14",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.114_14 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 114_14 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/114_14.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.114_15",
    "target_type": "module",
    "target_id": "module.114_15",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/114_15.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/114_15.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_114_15",
    "overrides": {"switch.module.114_15": None},
    "why": "Pack 114 item 15 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_114_15",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.114_15 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 114_15 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/114_15.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.114_16",
    "target_type": "route",
    "target_id": "route.114_16",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/114_16.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/114_16.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_114_16",
    "overrides": {"switch.route.114_16": True},
    "why": "Pack 114 item 16 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_114_16",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.114_16 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 114_16 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/114_16.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.114_17",
    "target_type": "boundary",
    "target_id": "boundary.114_17",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/114_17.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/114_17.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_114_17",
    "overrides": {"switch.boundary.114_17": False},
    "why": "Pack 114 item 17 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_114_17",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.114_17 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 114_17 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/114_17.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.114_18",
    "target_type": "module",
    "target_id": "module.114_18",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/114_18.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/114_18.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_114_18",
    "overrides": {"switch.module.114_18": "invalid"},
    "why": "Pack 114 item 18 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_114_18",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.114_18 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 114_18 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/114_18.json")

def iter_case_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for canonical, scenario, expected, note in zip(CANONICAL_INPUTS, OVERRIDE_SCENARIOS, EXPECTED_OUTCOMES, REPLAY_NOTES):
        row = dict(canonical)
        row.update({"scenario": scenario, "expected": expected, "note": note})
        rows.append(row)
    return rows
