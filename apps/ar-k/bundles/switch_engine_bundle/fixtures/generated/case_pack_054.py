"""Deterministic switch fixture pack 054.

This pack models a realistic slice of canonical switch inputs and expected
stage_03_switch_resolve outputs. Cases cover default resolution, switch-id
precedence, target-id precedence, invalid overrides, reports_real exclusion,
and deterministic replay semantics. The payload is encoded in Python so the
bundle remains Python-heavy while still shipping concrete golden data.
"""

from __future__ import annotations

PACK_ID = "pack_054"
CANONICAL_INPUTS = []
OVERRIDE_SCENARIOS = []
EXPECTED_OUTCOMES = []
REPLAY_NOTES = []
CANONICAL_INPUTS.append({
    "switch_id": "switch.route.054_01",
    "target_type": "route",
    "target_id": "route.054_01",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/054_01.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/054_01.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_054_01",
    "overrides": {"switch.route.054_01": False},
    "why": "Pack 054 item 01 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_054_01",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.054_01 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 054_01 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/054_01.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.054_02",
    "target_type": "boundary",
    "target_id": "boundary.054_02",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/054_02.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/054_02.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_054_02",
    "overrides": {"switch.boundary.054_02": "invalid"},
    "why": "Pack 054 item 02 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_054_02",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.054_02 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 054_02 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/054_02.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.054_03",
    "target_type": "module",
    "target_id": "module.054_03",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/054_03.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/054_03.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_054_03",
    "overrides": {"switch.module.054_03": None},
    "why": "Pack 054 item 03 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_054_03",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.054_03 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 054_03 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/054_03.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.054_04",
    "target_type": "route",
    "target_id": "route.054_04",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/054_04.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/054_04.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_054_04",
    "overrides": {"switch.route.054_04": True},
    "why": "Pack 054 item 04 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_054_04",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.054_04 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 054_04 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/054_04.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.054_05",
    "target_type": "boundary",
    "target_id": "boundary.054_05",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/054_05.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/054_05.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_054_05",
    "overrides": {"switch.boundary.054_05": False},
    "why": "Pack 054 item 05 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_054_05",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.054_05 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 054_05 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/054_05.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.054_06",
    "target_type": "module",
    "target_id": "module.054_06",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/054_06.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/054_06.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_054_06",
    "overrides": {"switch.module.054_06": "invalid"},
    "why": "Pack 054 item 06 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_054_06",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.054_06 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 054_06 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/054_06.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.054_07",
    "target_type": "route",
    "target_id": "route.054_07",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/054_07.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/054_07.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_054_07",
    "overrides": {"switch.route.054_07": None},
    "why": "Pack 054 item 07 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_054_07",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.route.054_07 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 054_07 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/054_07.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.054_08",
    "target_type": "boundary",
    "target_id": "boundary.054_08",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/054_08.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/054_08.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_054_08",
    "overrides": {"switch.boundary.054_08": True},
    "why": "Pack 054 item 08 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_054_08",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.054_08 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 054_08 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/054_08.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.054_09",
    "target_type": "module",
    "target_id": "module.054_09",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/054_09.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/054_09.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_054_09",
    "overrides": {"switch.module.054_09": False},
    "why": "Pack 054 item 09 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_054_09",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.054_09 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 054_09 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/054_09.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.054_10",
    "target_type": "route",
    "target_id": "route.054_10",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/054_10.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/054_10.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_054_10",
    "overrides": {"switch.route.054_10": "invalid"},
    "why": "Pack 054 item 10 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_054_10",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.route.054_10 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 054_10 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/054_10.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.054_11",
    "target_type": "boundary",
    "target_id": "boundary.054_11",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/054_11.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/054_11.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_054_11",
    "overrides": {"switch.boundary.054_11": None},
    "why": "Pack 054 item 11 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_054_11",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.boundary.054_11 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 054_11 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/054_11.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.054_12",
    "target_type": "module",
    "target_id": "module.054_12",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/054_12.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/054_12.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_054_12",
    "overrides": {"switch.module.054_12": True},
    "why": "Pack 054 item 12 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_054_12",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.054_12 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 054_12 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/054_12.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.054_13",
    "target_type": "route",
    "target_id": "route.054_13",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/054_13.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/054_13.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_054_13",
    "overrides": {"switch.route.054_13": False},
    "why": "Pack 054 item 13 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_054_13",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.054_13 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 054_13 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/054_13.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.054_14",
    "target_type": "boundary",
    "target_id": "boundary.054_14",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/054_14.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/054_14.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_054_14",
    "overrides": {"switch.boundary.054_14": "invalid"},
    "why": "Pack 054 item 14 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_054_14",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.054_14 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 054_14 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/054_14.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.054_15",
    "target_type": "module",
    "target_id": "module.054_15",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/054_15.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/054_15.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_054_15",
    "overrides": {"switch.module.054_15": None},
    "why": "Pack 054 item 15 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_054_15",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.054_15 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 054_15 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/054_15.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.054_16",
    "target_type": "route",
    "target_id": "route.054_16",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/054_16.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/054_16.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_054_16",
    "overrides": {"switch.route.054_16": True},
    "why": "Pack 054 item 16 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_054_16",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.054_16 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 054_16 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/054_16.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.054_17",
    "target_type": "boundary",
    "target_id": "boundary.054_17",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/054_17.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/054_17.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_054_17",
    "overrides": {"switch.boundary.054_17": False},
    "why": "Pack 054 item 17 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_054_17",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.054_17 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 054_17 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/054_17.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.054_18",
    "target_type": "module",
    "target_id": "module.054_18",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/054_18.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/054_18.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_054_18",
    "overrides": {"switch.module.054_18": "invalid"},
    "why": "Pack 054 item 18 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_054_18",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.054_18 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 054_18 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/054_18.json")

def iter_case_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for canonical, scenario, expected, note in zip(CANONICAL_INPUTS, OVERRIDE_SCENARIOS, EXPECTED_OUTCOMES, REPLAY_NOTES):
        row = dict(canonical)
        row.update({"scenario": scenario, "expected": expected, "note": note})
        rows.append(row)
    return rows
