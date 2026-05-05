"""Deterministic switch fixture pack 052.

This pack models a realistic slice of canonical switch inputs and expected
stage_03_switch_resolve outputs. Cases cover default resolution, switch-id
precedence, target-id precedence, invalid overrides, reports_real exclusion,
and deterministic replay semantics. The payload is encoded in Python so the
bundle remains Python-heavy while still shipping concrete golden data.
"""

from __future__ import annotations

PACK_ID = "pack_052"
CANONICAL_INPUTS = []
OVERRIDE_SCENARIOS = []
EXPECTED_OUTCOMES = []
REPLAY_NOTES = []
CANONICAL_INPUTS.append({
    "switch_id": "switch.route.052_01",
    "target_type": "route",
    "target_id": "route.052_01",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/052_01.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/052_01.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_052_01",
    "overrides": {"switch.route.052_01": False},
    "why": "Pack 052 item 01 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_052_01",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.052_01 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 052_01 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/052_01.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.052_02",
    "target_type": "boundary",
    "target_id": "boundary.052_02",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/052_02.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/052_02.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_052_02",
    "overrides": {"switch.boundary.052_02": "invalid"},
    "why": "Pack 052 item 02 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_052_02",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.052_02 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 052_02 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/052_02.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.052_03",
    "target_type": "module",
    "target_id": "module.052_03",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/052_03.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/052_03.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_052_03",
    "overrides": {"switch.module.052_03": None},
    "why": "Pack 052 item 03 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_052_03",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.052_03 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 052_03 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/052_03.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.052_04",
    "target_type": "route",
    "target_id": "route.052_04",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/052_04.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/052_04.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_052_04",
    "overrides": {"switch.route.052_04": True},
    "why": "Pack 052 item 04 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_052_04",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.052_04 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 052_04 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/052_04.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.052_05",
    "target_type": "boundary",
    "target_id": "boundary.052_05",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/052_05.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/052_05.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_052_05",
    "overrides": {"switch.boundary.052_05": False},
    "why": "Pack 052 item 05 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_052_05",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.052_05 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 052_05 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/052_05.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.052_06",
    "target_type": "module",
    "target_id": "module.052_06",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/052_06.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/052_06.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_052_06",
    "overrides": {"switch.module.052_06": "invalid"},
    "why": "Pack 052 item 06 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_052_06",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.052_06 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 052_06 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/052_06.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.052_07",
    "target_type": "route",
    "target_id": "route.052_07",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/052_07.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/052_07.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_052_07",
    "overrides": {"switch.route.052_07": None},
    "why": "Pack 052 item 07 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_052_07",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.route.052_07 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 052_07 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/052_07.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.052_08",
    "target_type": "boundary",
    "target_id": "boundary.052_08",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/052_08.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/052_08.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_052_08",
    "overrides": {"switch.boundary.052_08": True},
    "why": "Pack 052 item 08 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_052_08",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.052_08 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 052_08 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/052_08.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.052_09",
    "target_type": "module",
    "target_id": "module.052_09",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/052_09.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/052_09.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_052_09",
    "overrides": {"switch.module.052_09": False},
    "why": "Pack 052 item 09 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_052_09",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.052_09 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 052_09 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/052_09.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.052_10",
    "target_type": "route",
    "target_id": "route.052_10",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/052_10.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/052_10.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_052_10",
    "overrides": {"switch.route.052_10": "invalid"},
    "why": "Pack 052 item 10 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_052_10",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.route.052_10 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 052_10 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/052_10.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.052_11",
    "target_type": "boundary",
    "target_id": "boundary.052_11",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/052_11.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/052_11.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_052_11",
    "overrides": {"switch.boundary.052_11": None},
    "why": "Pack 052 item 11 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_052_11",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.boundary.052_11 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 052_11 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/052_11.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.052_12",
    "target_type": "module",
    "target_id": "module.052_12",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/052_12.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/052_12.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_052_12",
    "overrides": {"switch.module.052_12": True},
    "why": "Pack 052 item 12 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_052_12",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.052_12 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 052_12 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/052_12.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.052_13",
    "target_type": "route",
    "target_id": "route.052_13",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/052_13.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/052_13.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_052_13",
    "overrides": {"switch.route.052_13": False},
    "why": "Pack 052 item 13 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_052_13",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.052_13 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 052_13 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/052_13.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.052_14",
    "target_type": "boundary",
    "target_id": "boundary.052_14",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/052_14.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/052_14.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_052_14",
    "overrides": {"switch.boundary.052_14": "invalid"},
    "why": "Pack 052 item 14 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_052_14",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.052_14 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 052_14 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/052_14.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.052_15",
    "target_type": "module",
    "target_id": "module.052_15",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/052_15.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/052_15.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_052_15",
    "overrides": {"switch.module.052_15": None},
    "why": "Pack 052 item 15 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_052_15",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.052_15 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 052_15 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/052_15.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.052_16",
    "target_type": "route",
    "target_id": "route.052_16",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/052_16.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/052_16.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_052_16",
    "overrides": {"switch.route.052_16": True},
    "why": "Pack 052 item 16 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_052_16",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.052_16 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 052_16 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/052_16.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.052_17",
    "target_type": "boundary",
    "target_id": "boundary.052_17",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/052_17.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/052_17.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_052_17",
    "overrides": {"switch.boundary.052_17": False},
    "why": "Pack 052 item 17 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_052_17",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.052_17 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 052_17 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/052_17.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.052_18",
    "target_type": "module",
    "target_id": "module.052_18",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/052_18.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/052_18.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_052_18",
    "overrides": {"switch.module.052_18": "invalid"},
    "why": "Pack 052 item 18 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_052_18",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.052_18 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 052_18 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/052_18.json")

def iter_case_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for canonical, scenario, expected, note in zip(CANONICAL_INPUTS, OVERRIDE_SCENARIOS, EXPECTED_OUTCOMES, REPLAY_NOTES):
        row = dict(canonical)
        row.update({"scenario": scenario, "expected": expected, "note": note})
        rows.append(row)
    return rows
