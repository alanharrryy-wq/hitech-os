"""Deterministic switch fixture pack 022.

This pack models a realistic slice of canonical switch inputs and expected
stage_03_switch_resolve outputs. Cases cover default resolution, switch-id
precedence, target-id precedence, invalid overrides, reports_real exclusion,
and deterministic replay semantics. The payload is encoded in Python so the
bundle remains Python-heavy while still shipping concrete golden data.
"""

from __future__ import annotations

PACK_ID = "pack_022"
CANONICAL_INPUTS = []
OVERRIDE_SCENARIOS = []
EXPECTED_OUTCOMES = []
REPLAY_NOTES = []
CANONICAL_INPUTS.append({
    "switch_id": "switch.route.022_01",
    "target_type": "route",
    "target_id": "route.022_01",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/022_01.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/022_01.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_022_01",
    "overrides": {"switch.route.022_01": False},
    "why": "Pack 022 item 01 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_022_01",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.022_01 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 022_01 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/022_01.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.022_02",
    "target_type": "boundary",
    "target_id": "boundary.022_02",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/022_02.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/022_02.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_022_02",
    "overrides": {"switch.boundary.022_02": "invalid"},
    "why": "Pack 022 item 02 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_022_02",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.022_02 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 022_02 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/022_02.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.022_03",
    "target_type": "module",
    "target_id": "module.022_03",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/022_03.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/022_03.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_022_03",
    "overrides": {"switch.module.022_03": None},
    "why": "Pack 022 item 03 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_022_03",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.022_03 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 022_03 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/022_03.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.022_04",
    "target_type": "route",
    "target_id": "route.022_04",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/022_04.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/022_04.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_022_04",
    "overrides": {"switch.route.022_04": True},
    "why": "Pack 022 item 04 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_022_04",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.022_04 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 022_04 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/022_04.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.022_05",
    "target_type": "boundary",
    "target_id": "boundary.022_05",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/022_05.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/022_05.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_022_05",
    "overrides": {"switch.boundary.022_05": False},
    "why": "Pack 022 item 05 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_022_05",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.022_05 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 022_05 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/022_05.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.022_06",
    "target_type": "module",
    "target_id": "module.022_06",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/022_06.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/022_06.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_022_06",
    "overrides": {"switch.module.022_06": "invalid"},
    "why": "Pack 022 item 06 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_022_06",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.022_06 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 022_06 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/022_06.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.022_07",
    "target_type": "route",
    "target_id": "route.022_07",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/022_07.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/022_07.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_022_07",
    "overrides": {"switch.route.022_07": None},
    "why": "Pack 022 item 07 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_022_07",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.route.022_07 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 022_07 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/022_07.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.022_08",
    "target_type": "boundary",
    "target_id": "boundary.022_08",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/022_08.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/022_08.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_022_08",
    "overrides": {"switch.boundary.022_08": True},
    "why": "Pack 022 item 08 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_022_08",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.022_08 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 022_08 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/022_08.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.022_09",
    "target_type": "module",
    "target_id": "module.022_09",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/022_09.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/022_09.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_022_09",
    "overrides": {"switch.module.022_09": False},
    "why": "Pack 022 item 09 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_022_09",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.022_09 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 022_09 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/022_09.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.022_10",
    "target_type": "route",
    "target_id": "route.022_10",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/022_10.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/022_10.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_022_10",
    "overrides": {"switch.route.022_10": "invalid"},
    "why": "Pack 022 item 10 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_022_10",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.route.022_10 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 022_10 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/022_10.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.022_11",
    "target_type": "boundary",
    "target_id": "boundary.022_11",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/022_11.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/022_11.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_022_11",
    "overrides": {"switch.boundary.022_11": None},
    "why": "Pack 022 item 11 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_022_11",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.boundary.022_11 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 022_11 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/022_11.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.022_12",
    "target_type": "module",
    "target_id": "module.022_12",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/022_12.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/022_12.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_022_12",
    "overrides": {"switch.module.022_12": True},
    "why": "Pack 022 item 12 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_022_12",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.022_12 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 022_12 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/022_12.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.022_13",
    "target_type": "route",
    "target_id": "route.022_13",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/022_13.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/022_13.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_022_13",
    "overrides": {"switch.route.022_13": False},
    "why": "Pack 022 item 13 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_022_13",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.022_13 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 022_13 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/022_13.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.022_14",
    "target_type": "boundary",
    "target_id": "boundary.022_14",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/022_14.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/022_14.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_022_14",
    "overrides": {"switch.boundary.022_14": "invalid"},
    "why": "Pack 022 item 14 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_022_14",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.022_14 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 022_14 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/022_14.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.022_15",
    "target_type": "module",
    "target_id": "module.022_15",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/022_15.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/022_15.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_022_15",
    "overrides": {"switch.module.022_15": None},
    "why": "Pack 022 item 15 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_022_15",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.022_15 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 022_15 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/022_15.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.022_16",
    "target_type": "route",
    "target_id": "route.022_16",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/022_16.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/022_16.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_022_16",
    "overrides": {"switch.route.022_16": True},
    "why": "Pack 022 item 16 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_022_16",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.022_16 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 022_16 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/022_16.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.022_17",
    "target_type": "boundary",
    "target_id": "boundary.022_17",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/022_17.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/022_17.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_022_17",
    "overrides": {"switch.boundary.022_17": False},
    "why": "Pack 022 item 17 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_022_17",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.022_17 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 022_17 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/022_17.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.022_18",
    "target_type": "module",
    "target_id": "module.022_18",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/022_18.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/022_18.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_022_18",
    "overrides": {"switch.module.022_18": "invalid"},
    "why": "Pack 022 item 18 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_022_18",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.022_18 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 022_18 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/022_18.json")

def iter_case_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for canonical, scenario, expected, note in zip(CANONICAL_INPUTS, OVERRIDE_SCENARIOS, EXPECTED_OUTCOMES, REPLAY_NOTES):
        row = dict(canonical)
        row.update({"scenario": scenario, "expected": expected, "note": note})
        rows.append(row)
    return rows
