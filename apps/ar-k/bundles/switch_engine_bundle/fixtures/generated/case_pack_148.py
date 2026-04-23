"""Deterministic switch fixture pack 148.

This pack models a realistic slice of canonical switch inputs and expected
stage_03_switch_resolve outputs. Cases cover default resolution, switch-id
precedence, target-id precedence, invalid overrides, reports_real exclusion,
and deterministic replay semantics. The payload is encoded in Python so the
bundle remains Python-heavy while still shipping concrete golden data.
"""

from __future__ import annotations

PACK_ID = "pack_148"
CANONICAL_INPUTS = []
OVERRIDE_SCENARIOS = []
EXPECTED_OUTCOMES = []
REPLAY_NOTES = []
CANONICAL_INPUTS.append({
    "switch_id": "switch.route.148_01",
    "target_type": "route",
    "target_id": "route.148_01",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/148_01.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/148_01.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_148_01",
    "overrides": {"switch.route.148_01": False},
    "why": "Pack 148 item 01 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_148_01",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.148_01 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 148_01 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/148_01.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.148_02",
    "target_type": "boundary",
    "target_id": "boundary.148_02",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/148_02.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/148_02.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_148_02",
    "overrides": {"switch.boundary.148_02": "invalid"},
    "why": "Pack 148 item 02 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_148_02",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.148_02 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 148_02 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/148_02.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.148_03",
    "target_type": "module",
    "target_id": "module.148_03",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/148_03.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/148_03.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_148_03",
    "overrides": {"switch.module.148_03": None},
    "why": "Pack 148 item 03 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_148_03",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.148_03 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 148_03 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/148_03.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.148_04",
    "target_type": "route",
    "target_id": "route.148_04",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/148_04.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/148_04.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_148_04",
    "overrides": {"switch.route.148_04": True},
    "why": "Pack 148 item 04 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_148_04",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.148_04 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 148_04 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/148_04.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.148_05",
    "target_type": "boundary",
    "target_id": "boundary.148_05",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/148_05.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/148_05.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_148_05",
    "overrides": {"switch.boundary.148_05": False},
    "why": "Pack 148 item 05 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_148_05",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.148_05 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 148_05 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/148_05.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.148_06",
    "target_type": "module",
    "target_id": "module.148_06",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/148_06.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/148_06.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_148_06",
    "overrides": {"switch.module.148_06": "invalid"},
    "why": "Pack 148 item 06 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_148_06",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.148_06 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 148_06 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/148_06.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.148_07",
    "target_type": "route",
    "target_id": "route.148_07",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/148_07.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/148_07.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_148_07",
    "overrides": {"switch.route.148_07": None},
    "why": "Pack 148 item 07 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_148_07",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.route.148_07 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 148_07 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/148_07.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.148_08",
    "target_type": "boundary",
    "target_id": "boundary.148_08",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/148_08.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/148_08.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_148_08",
    "overrides": {"switch.boundary.148_08": True},
    "why": "Pack 148 item 08 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_148_08",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.148_08 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 148_08 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/148_08.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.148_09",
    "target_type": "module",
    "target_id": "module.148_09",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/148_09.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/148_09.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_148_09",
    "overrides": {"switch.module.148_09": False},
    "why": "Pack 148 item 09 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_148_09",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.148_09 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 148_09 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/148_09.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.148_10",
    "target_type": "route",
    "target_id": "route.148_10",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/148_10.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/148_10.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_148_10",
    "overrides": {"switch.route.148_10": "invalid"},
    "why": "Pack 148 item 10 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_148_10",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.route.148_10 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 148_10 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/148_10.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.148_11",
    "target_type": "boundary",
    "target_id": "boundary.148_11",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/148_11.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/148_11.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_148_11",
    "overrides": {"switch.boundary.148_11": None},
    "why": "Pack 148 item 11 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_148_11",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.boundary.148_11 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 148_11 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/148_11.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.148_12",
    "target_type": "module",
    "target_id": "module.148_12",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/148_12.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/148_12.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_148_12",
    "overrides": {"switch.module.148_12": True},
    "why": "Pack 148 item 12 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_148_12",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.148_12 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 148_12 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/148_12.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.148_13",
    "target_type": "route",
    "target_id": "route.148_13",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/148_13.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/148_13.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_148_13",
    "overrides": {"switch.route.148_13": False},
    "why": "Pack 148 item 13 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_148_13",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.148_13 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 148_13 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/148_13.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.148_14",
    "target_type": "boundary",
    "target_id": "boundary.148_14",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/148_14.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/148_14.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_148_14",
    "overrides": {"switch.boundary.148_14": "invalid"},
    "why": "Pack 148 item 14 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_148_14",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.148_14 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 148_14 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/148_14.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.148_15",
    "target_type": "module",
    "target_id": "module.148_15",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/148_15.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/148_15.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_148_15",
    "overrides": {"switch.module.148_15": None},
    "why": "Pack 148 item 15 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_148_15",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.148_15 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 148_15 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/148_15.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.148_16",
    "target_type": "route",
    "target_id": "route.148_16",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/148_16.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/148_16.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_148_16",
    "overrides": {"switch.route.148_16": True},
    "why": "Pack 148 item 16 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_148_16",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.148_16 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 148_16 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/148_16.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.148_17",
    "target_type": "boundary",
    "target_id": "boundary.148_17",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/148_17.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/148_17.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_148_17",
    "overrides": {"switch.boundary.148_17": False},
    "why": "Pack 148 item 17 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_148_17",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.148_17 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 148_17 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/148_17.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.148_18",
    "target_type": "module",
    "target_id": "module.148_18",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/148_18.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/148_18.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_148_18",
    "overrides": {"switch.module.148_18": "invalid"},
    "why": "Pack 148 item 18 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_148_18",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.148_18 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 148_18 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/148_18.json")

def iter_case_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for canonical, scenario, expected, note in zip(CANONICAL_INPUTS, OVERRIDE_SCENARIOS, EXPECTED_OUTCOMES, REPLAY_NOTES):
        row = dict(canonical)
        row.update({"scenario": scenario, "expected": expected, "note": note})
        rows.append(row)
    return rows
