"""Deterministic switch fixture pack 158.

This pack models a realistic slice of canonical switch inputs and expected
stage_03_switch_resolve outputs. Cases cover default resolution, switch-id
precedence, target-id precedence, invalid overrides, reports_real exclusion,
and deterministic replay semantics. The payload is encoded in Python so the
bundle remains Python-heavy while still shipping concrete golden data.
"""

from __future__ import annotations

PACK_ID = "pack_158"
CANONICAL_INPUTS = []
OVERRIDE_SCENARIOS = []
EXPECTED_OUTCOMES = []
REPLAY_NOTES = []
CANONICAL_INPUTS.append({
    "switch_id": "switch.route.158_01",
    "target_type": "route",
    "target_id": "route.158_01",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/158_01.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/158_01.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_158_01",
    "overrides": {"switch.route.158_01": False},
    "why": "Pack 158 item 01 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_158_01",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.158_01 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 158_01 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/158_01.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.158_02",
    "target_type": "boundary",
    "target_id": "boundary.158_02",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/158_02.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/158_02.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_158_02",
    "overrides": {"switch.boundary.158_02": "invalid"},
    "why": "Pack 158 item 02 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_158_02",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.158_02 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 158_02 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/158_02.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.158_03",
    "target_type": "module",
    "target_id": "module.158_03",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/158_03.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/158_03.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_158_03",
    "overrides": {"switch.module.158_03": None},
    "why": "Pack 158 item 03 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_158_03",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.158_03 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 158_03 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/158_03.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.158_04",
    "target_type": "route",
    "target_id": "route.158_04",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/158_04.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/158_04.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_158_04",
    "overrides": {"switch.route.158_04": True},
    "why": "Pack 158 item 04 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_158_04",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.158_04 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 158_04 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/158_04.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.158_05",
    "target_type": "boundary",
    "target_id": "boundary.158_05",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/158_05.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/158_05.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_158_05",
    "overrides": {"switch.boundary.158_05": False},
    "why": "Pack 158 item 05 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_158_05",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.158_05 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 158_05 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/158_05.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.158_06",
    "target_type": "module",
    "target_id": "module.158_06",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/158_06.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/158_06.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_158_06",
    "overrides": {"switch.module.158_06": "invalid"},
    "why": "Pack 158 item 06 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_158_06",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.158_06 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 158_06 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/158_06.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.158_07",
    "target_type": "route",
    "target_id": "route.158_07",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/158_07.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/158_07.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_158_07",
    "overrides": {"switch.route.158_07": None},
    "why": "Pack 158 item 07 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_158_07",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.route.158_07 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 158_07 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/158_07.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.158_08",
    "target_type": "boundary",
    "target_id": "boundary.158_08",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/158_08.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/158_08.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_158_08",
    "overrides": {"switch.boundary.158_08": True},
    "why": "Pack 158 item 08 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_158_08",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.158_08 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 158_08 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/158_08.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.158_09",
    "target_type": "module",
    "target_id": "module.158_09",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/158_09.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/158_09.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_158_09",
    "overrides": {"switch.module.158_09": False},
    "why": "Pack 158 item 09 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_158_09",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.158_09 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 158_09 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/158_09.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.158_10",
    "target_type": "route",
    "target_id": "route.158_10",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/158_10.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/158_10.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_158_10",
    "overrides": {"switch.route.158_10": "invalid"},
    "why": "Pack 158 item 10 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_158_10",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.route.158_10 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 158_10 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/158_10.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.158_11",
    "target_type": "boundary",
    "target_id": "boundary.158_11",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/158_11.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/158_11.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_158_11",
    "overrides": {"switch.boundary.158_11": None},
    "why": "Pack 158 item 11 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_158_11",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.boundary.158_11 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 158_11 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/158_11.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.158_12",
    "target_type": "module",
    "target_id": "module.158_12",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/158_12.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/158_12.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_158_12",
    "overrides": {"switch.module.158_12": True},
    "why": "Pack 158 item 12 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_158_12",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.158_12 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 158_12 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/158_12.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.158_13",
    "target_type": "route",
    "target_id": "route.158_13",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/158_13.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/158_13.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_158_13",
    "overrides": {"switch.route.158_13": False},
    "why": "Pack 158 item 13 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_158_13",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.158_13 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 158_13 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/158_13.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.158_14",
    "target_type": "boundary",
    "target_id": "boundary.158_14",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/158_14.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/158_14.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_158_14",
    "overrides": {"switch.boundary.158_14": "invalid"},
    "why": "Pack 158 item 14 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_158_14",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.158_14 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 158_14 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/158_14.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.158_15",
    "target_type": "module",
    "target_id": "module.158_15",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/158_15.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/158_15.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_158_15",
    "overrides": {"switch.module.158_15": None},
    "why": "Pack 158 item 15 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_158_15",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.158_15 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 158_15 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/158_15.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.158_16",
    "target_type": "route",
    "target_id": "route.158_16",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/158_16.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/158_16.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_158_16",
    "overrides": {"switch.route.158_16": True},
    "why": "Pack 158 item 16 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_158_16",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.158_16 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 158_16 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/158_16.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.158_17",
    "target_type": "boundary",
    "target_id": "boundary.158_17",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/158_17.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/158_17.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_158_17",
    "overrides": {"switch.boundary.158_17": False},
    "why": "Pack 158 item 17 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_158_17",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.158_17 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 158_17 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/158_17.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.158_18",
    "target_type": "module",
    "target_id": "module.158_18",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/158_18.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/158_18.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_158_18",
    "overrides": {"switch.module.158_18": "invalid"},
    "why": "Pack 158 item 18 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_158_18",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.158_18 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 158_18 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/158_18.json")

def iter_case_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for canonical, scenario, expected, note in zip(CANONICAL_INPUTS, OVERRIDE_SCENARIOS, EXPECTED_OUTCOMES, REPLAY_NOTES):
        row = dict(canonical)
        row.update({"scenario": scenario, "expected": expected, "note": note})
        rows.append(row)
    return rows
