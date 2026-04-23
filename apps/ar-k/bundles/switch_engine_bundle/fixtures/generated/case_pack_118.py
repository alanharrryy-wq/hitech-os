"""Deterministic switch fixture pack 118.

This pack models a realistic slice of canonical switch inputs and expected
stage_03_switch_resolve outputs. Cases cover default resolution, switch-id
precedence, target-id precedence, invalid overrides, reports_real exclusion,
and deterministic replay semantics. The payload is encoded in Python so the
bundle remains Python-heavy while still shipping concrete golden data.
"""

from __future__ import annotations

PACK_ID = "pack_118"
CANONICAL_INPUTS = []
OVERRIDE_SCENARIOS = []
EXPECTED_OUTCOMES = []
REPLAY_NOTES = []
CANONICAL_INPUTS.append({
    "switch_id": "switch.route.118_01",
    "target_type": "route",
    "target_id": "route.118_01",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/118_01.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/118_01.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_118_01",
    "overrides": {"switch.route.118_01": False},
    "why": "Pack 118 item 01 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_118_01",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.118_01 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 118_01 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/118_01.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.118_02",
    "target_type": "boundary",
    "target_id": "boundary.118_02",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/118_02.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/118_02.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_118_02",
    "overrides": {"switch.boundary.118_02": "invalid"},
    "why": "Pack 118 item 02 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_118_02",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.118_02 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 118_02 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/118_02.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.118_03",
    "target_type": "module",
    "target_id": "module.118_03",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/118_03.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/118_03.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_118_03",
    "overrides": {"switch.module.118_03": None},
    "why": "Pack 118 item 03 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_118_03",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.118_03 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 118_03 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/118_03.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.118_04",
    "target_type": "route",
    "target_id": "route.118_04",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/118_04.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/118_04.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_118_04",
    "overrides": {"switch.route.118_04": True},
    "why": "Pack 118 item 04 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_118_04",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.118_04 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 118_04 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/118_04.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.118_05",
    "target_type": "boundary",
    "target_id": "boundary.118_05",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/118_05.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/118_05.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_118_05",
    "overrides": {"switch.boundary.118_05": False},
    "why": "Pack 118 item 05 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_118_05",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.118_05 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 118_05 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/118_05.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.118_06",
    "target_type": "module",
    "target_id": "module.118_06",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/118_06.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/118_06.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_118_06",
    "overrides": {"switch.module.118_06": "invalid"},
    "why": "Pack 118 item 06 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_118_06",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.118_06 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 118_06 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/118_06.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.118_07",
    "target_type": "route",
    "target_id": "route.118_07",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/118_07.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/118_07.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_118_07",
    "overrides": {"switch.route.118_07": None},
    "why": "Pack 118 item 07 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_118_07",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.route.118_07 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 118_07 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/118_07.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.118_08",
    "target_type": "boundary",
    "target_id": "boundary.118_08",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/118_08.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/118_08.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_118_08",
    "overrides": {"switch.boundary.118_08": True},
    "why": "Pack 118 item 08 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_118_08",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.118_08 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 118_08 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/118_08.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.118_09",
    "target_type": "module",
    "target_id": "module.118_09",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/118_09.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/118_09.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_118_09",
    "overrides": {"switch.module.118_09": False},
    "why": "Pack 118 item 09 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_118_09",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.118_09 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 118_09 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/118_09.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.118_10",
    "target_type": "route",
    "target_id": "route.118_10",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/118_10.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/118_10.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_118_10",
    "overrides": {"switch.route.118_10": "invalid"},
    "why": "Pack 118 item 10 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_118_10",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.route.118_10 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 118_10 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/118_10.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.118_11",
    "target_type": "boundary",
    "target_id": "boundary.118_11",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/118_11.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/118_11.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_118_11",
    "overrides": {"switch.boundary.118_11": None},
    "why": "Pack 118 item 11 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_118_11",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.boundary.118_11 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 118_11 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/118_11.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.118_12",
    "target_type": "module",
    "target_id": "module.118_12",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/118_12.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/118_12.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_118_12",
    "overrides": {"switch.module.118_12": True},
    "why": "Pack 118 item 12 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_118_12",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.118_12 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 118_12 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/118_12.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.118_13",
    "target_type": "route",
    "target_id": "route.118_13",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/118_13.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/118_13.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_118_13",
    "overrides": {"switch.route.118_13": False},
    "why": "Pack 118 item 13 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_118_13",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.118_13 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 118_13 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/118_13.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.118_14",
    "target_type": "boundary",
    "target_id": "boundary.118_14",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/118_14.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/118_14.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_118_14",
    "overrides": {"switch.boundary.118_14": "invalid"},
    "why": "Pack 118 item 14 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_118_14",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.118_14 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 118_14 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/118_14.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.118_15",
    "target_type": "module",
    "target_id": "module.118_15",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/118_15.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/118_15.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_118_15",
    "overrides": {"switch.module.118_15": None},
    "why": "Pack 118 item 15 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_118_15",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.118_15 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 118_15 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/118_15.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.118_16",
    "target_type": "route",
    "target_id": "route.118_16",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/118_16.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/118_16.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_118_16",
    "overrides": {"switch.route.118_16": True},
    "why": "Pack 118 item 16 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_118_16",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.118_16 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 118_16 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/118_16.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.118_17",
    "target_type": "boundary",
    "target_id": "boundary.118_17",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/118_17.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/118_17.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_118_17",
    "overrides": {"switch.boundary.118_17": False},
    "why": "Pack 118 item 17 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_118_17",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.118_17 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 118_17 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/118_17.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.118_18",
    "target_type": "module",
    "target_id": "module.118_18",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/118_18.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/118_18.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_118_18",
    "overrides": {"switch.module.118_18": "invalid"},
    "why": "Pack 118 item 18 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_118_18",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.118_18 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 118_18 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/118_18.json")

def iter_case_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for canonical, scenario, expected, note in zip(CANONICAL_INPUTS, OVERRIDE_SCENARIOS, EXPECTED_OUTCOMES, REPLAY_NOTES):
        row = dict(canonical)
        row.update({"scenario": scenario, "expected": expected, "note": note})
        rows.append(row)
    return rows
