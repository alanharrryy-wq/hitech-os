"""Deterministic switch fixture pack 078.

This pack models a realistic slice of canonical switch inputs and expected
stage_03_switch_resolve outputs. Cases cover default resolution, switch-id
precedence, target-id precedence, invalid overrides, reports_real exclusion,
and deterministic replay semantics. The payload is encoded in Python so the
bundle remains Python-heavy while still shipping concrete golden data.
"""

from __future__ import annotations

PACK_ID = "pack_078"
CANONICAL_INPUTS = []
OVERRIDE_SCENARIOS = []
EXPECTED_OUTCOMES = []
REPLAY_NOTES = []
CANONICAL_INPUTS.append({
    "switch_id": "switch.route.078_01",
    "target_type": "route",
    "target_id": "route.078_01",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/078_01.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/078_01.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_078_01",
    "overrides": {"switch.route.078_01": False},
    "why": "Pack 078 item 01 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_078_01",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.078_01 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 078_01 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/078_01.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.078_02",
    "target_type": "boundary",
    "target_id": "boundary.078_02",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/078_02.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/078_02.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_078_02",
    "overrides": {"switch.boundary.078_02": "invalid"},
    "why": "Pack 078 item 02 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_078_02",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.078_02 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 078_02 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/078_02.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.078_03",
    "target_type": "module",
    "target_id": "module.078_03",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/078_03.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/078_03.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_078_03",
    "overrides": {"switch.module.078_03": None},
    "why": "Pack 078 item 03 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_078_03",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.078_03 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 078_03 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/078_03.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.078_04",
    "target_type": "route",
    "target_id": "route.078_04",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/078_04.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/078_04.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_078_04",
    "overrides": {"switch.route.078_04": True},
    "why": "Pack 078 item 04 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_078_04",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.078_04 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 078_04 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/078_04.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.078_05",
    "target_type": "boundary",
    "target_id": "boundary.078_05",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/078_05.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/078_05.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_078_05",
    "overrides": {"switch.boundary.078_05": False},
    "why": "Pack 078 item 05 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_078_05",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.078_05 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 078_05 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/078_05.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.078_06",
    "target_type": "module",
    "target_id": "module.078_06",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/078_06.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/078_06.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_078_06",
    "overrides": {"switch.module.078_06": "invalid"},
    "why": "Pack 078 item 06 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_078_06",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.078_06 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 078_06 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/078_06.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.078_07",
    "target_type": "route",
    "target_id": "route.078_07",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/078_07.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/078_07.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_078_07",
    "overrides": {"switch.route.078_07": None},
    "why": "Pack 078 item 07 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_078_07",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.route.078_07 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 078_07 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/078_07.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.078_08",
    "target_type": "boundary",
    "target_id": "boundary.078_08",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/078_08.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/078_08.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_078_08",
    "overrides": {"switch.boundary.078_08": True},
    "why": "Pack 078 item 08 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_078_08",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.078_08 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 078_08 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/078_08.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.078_09",
    "target_type": "module",
    "target_id": "module.078_09",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/078_09.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/078_09.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_078_09",
    "overrides": {"switch.module.078_09": False},
    "why": "Pack 078 item 09 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_078_09",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.078_09 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 078_09 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/078_09.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.078_10",
    "target_type": "route",
    "target_id": "route.078_10",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/078_10.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/078_10.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_078_10",
    "overrides": {"switch.route.078_10": "invalid"},
    "why": "Pack 078 item 10 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_078_10",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.route.078_10 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 078_10 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/078_10.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.078_11",
    "target_type": "boundary",
    "target_id": "boundary.078_11",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/078_11.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/078_11.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_078_11",
    "overrides": {"switch.boundary.078_11": None},
    "why": "Pack 078 item 11 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_078_11",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.boundary.078_11 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 078_11 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/078_11.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.078_12",
    "target_type": "module",
    "target_id": "module.078_12",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/078_12.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/078_12.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_078_12",
    "overrides": {"switch.module.078_12": True},
    "why": "Pack 078 item 12 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_078_12",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.078_12 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 078_12 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/078_12.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.078_13",
    "target_type": "route",
    "target_id": "route.078_13",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/078_13.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/078_13.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_078_13",
    "overrides": {"switch.route.078_13": False},
    "why": "Pack 078 item 13 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_078_13",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.078_13 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 078_13 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/078_13.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.078_14",
    "target_type": "boundary",
    "target_id": "boundary.078_14",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/078_14.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/078_14.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_078_14",
    "overrides": {"switch.boundary.078_14": "invalid"},
    "why": "Pack 078 item 14 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_078_14",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.078_14 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 078_14 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/078_14.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.078_15",
    "target_type": "module",
    "target_id": "module.078_15",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/078_15.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/078_15.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_078_15",
    "overrides": {"switch.module.078_15": None},
    "why": "Pack 078 item 15 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_078_15",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.078_15 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 078_15 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/078_15.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.078_16",
    "target_type": "route",
    "target_id": "route.078_16",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/078_16.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/078_16.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_078_16",
    "overrides": {"switch.route.078_16": True},
    "why": "Pack 078 item 16 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_078_16",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.078_16 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 078_16 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/078_16.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.078_17",
    "target_type": "boundary",
    "target_id": "boundary.078_17",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/078_17.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/078_17.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_078_17",
    "overrides": {"switch.boundary.078_17": False},
    "why": "Pack 078 item 17 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_078_17",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.078_17 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 078_17 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/078_17.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.078_18",
    "target_type": "module",
    "target_id": "module.078_18",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/078_18.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/078_18.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_078_18",
    "overrides": {"switch.module.078_18": "invalid"},
    "why": "Pack 078 item 18 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_078_18",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.078_18 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 078_18 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/078_18.json")

def iter_case_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for canonical, scenario, expected, note in zip(CANONICAL_INPUTS, OVERRIDE_SCENARIOS, EXPECTED_OUTCOMES, REPLAY_NOTES):
        row = dict(canonical)
        row.update({"scenario": scenario, "expected": expected, "note": note})
        rows.append(row)
    return rows
