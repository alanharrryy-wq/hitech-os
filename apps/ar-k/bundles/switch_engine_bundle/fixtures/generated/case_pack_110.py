"""Deterministic switch fixture pack 110.

This pack models a realistic slice of canonical switch inputs and expected
stage_03_switch_resolve outputs. Cases cover default resolution, switch-id
precedence, target-id precedence, invalid overrides, reports_real exclusion,
and deterministic replay semantics. The payload is encoded in Python so the
bundle remains Python-heavy while still shipping concrete golden data.
"""

from __future__ import annotations

PACK_ID = "pack_110"
CANONICAL_INPUTS = []
OVERRIDE_SCENARIOS = []
EXPECTED_OUTCOMES = []
REPLAY_NOTES = []
CANONICAL_INPUTS.append({
    "switch_id": "switch.route.110_01",
    "target_type": "route",
    "target_id": "route.110_01",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/110_01.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/110_01.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_110_01",
    "overrides": {"switch.route.110_01": False},
    "why": "Pack 110 item 01 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_110_01",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.110_01 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 110_01 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/110_01.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.110_02",
    "target_type": "boundary",
    "target_id": "boundary.110_02",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/110_02.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/110_02.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_110_02",
    "overrides": {"switch.boundary.110_02": "invalid"},
    "why": "Pack 110 item 02 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_110_02",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.110_02 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 110_02 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/110_02.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.110_03",
    "target_type": "module",
    "target_id": "module.110_03",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/110_03.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/110_03.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_110_03",
    "overrides": {"switch.module.110_03": None},
    "why": "Pack 110 item 03 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_110_03",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.110_03 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 110_03 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/110_03.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.110_04",
    "target_type": "route",
    "target_id": "route.110_04",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/110_04.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/110_04.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_110_04",
    "overrides": {"switch.route.110_04": True},
    "why": "Pack 110 item 04 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_110_04",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.110_04 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 110_04 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/110_04.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.110_05",
    "target_type": "boundary",
    "target_id": "boundary.110_05",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/110_05.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/110_05.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_110_05",
    "overrides": {"switch.boundary.110_05": False},
    "why": "Pack 110 item 05 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_110_05",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.110_05 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 110_05 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/110_05.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.110_06",
    "target_type": "module",
    "target_id": "module.110_06",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/110_06.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/110_06.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_110_06",
    "overrides": {"switch.module.110_06": "invalid"},
    "why": "Pack 110 item 06 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_110_06",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.110_06 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 110_06 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/110_06.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.110_07",
    "target_type": "route",
    "target_id": "route.110_07",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/110_07.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/110_07.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_110_07",
    "overrides": {"switch.route.110_07": None},
    "why": "Pack 110 item 07 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_110_07",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.route.110_07 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 110_07 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/110_07.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.110_08",
    "target_type": "boundary",
    "target_id": "boundary.110_08",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/110_08.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/110_08.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_110_08",
    "overrides": {"switch.boundary.110_08": True},
    "why": "Pack 110 item 08 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_110_08",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.110_08 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 110_08 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/110_08.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.110_09",
    "target_type": "module",
    "target_id": "module.110_09",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/110_09.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/110_09.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_110_09",
    "overrides": {"switch.module.110_09": False},
    "why": "Pack 110 item 09 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_110_09",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.110_09 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 110_09 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/110_09.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.110_10",
    "target_type": "route",
    "target_id": "route.110_10",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/110_10.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/110_10.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_110_10",
    "overrides": {"switch.route.110_10": "invalid"},
    "why": "Pack 110 item 10 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_110_10",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.route.110_10 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 110_10 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/110_10.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.110_11",
    "target_type": "boundary",
    "target_id": "boundary.110_11",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/110_11.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/110_11.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_110_11",
    "overrides": {"switch.boundary.110_11": None},
    "why": "Pack 110 item 11 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_110_11",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.boundary.110_11 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 110_11 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/110_11.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.110_12",
    "target_type": "module",
    "target_id": "module.110_12",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/110_12.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/110_12.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_110_12",
    "overrides": {"switch.module.110_12": True},
    "why": "Pack 110 item 12 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_110_12",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.110_12 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 110_12 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/110_12.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.110_13",
    "target_type": "route",
    "target_id": "route.110_13",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/110_13.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/110_13.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_110_13",
    "overrides": {"switch.route.110_13": False},
    "why": "Pack 110 item 13 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_110_13",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.110_13 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 110_13 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/110_13.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.110_14",
    "target_type": "boundary",
    "target_id": "boundary.110_14",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/110_14.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/110_14.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_110_14",
    "overrides": {"switch.boundary.110_14": "invalid"},
    "why": "Pack 110 item 14 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_110_14",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.110_14 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 110_14 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/110_14.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.110_15",
    "target_type": "module",
    "target_id": "module.110_15",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/110_15.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/110_15.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_110_15",
    "overrides": {"switch.module.110_15": None},
    "why": "Pack 110 item 15 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_110_15",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.110_15 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 110_15 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/110_15.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.110_16",
    "target_type": "route",
    "target_id": "route.110_16",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/110_16.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/110_16.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_110_16",
    "overrides": {"switch.route.110_16": True},
    "why": "Pack 110 item 16 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_110_16",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.110_16 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 110_16 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/110_16.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.110_17",
    "target_type": "boundary",
    "target_id": "boundary.110_17",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/110_17.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/110_17.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_110_17",
    "overrides": {"switch.boundary.110_17": False},
    "why": "Pack 110 item 17 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_110_17",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.110_17 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 110_17 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/110_17.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.110_18",
    "target_type": "module",
    "target_id": "module.110_18",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/110_18.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/110_18.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_110_18",
    "overrides": {"switch.module.110_18": "invalid"},
    "why": "Pack 110 item 18 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_110_18",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.110_18 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 110_18 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/110_18.json")

def iter_case_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for canonical, scenario, expected, note in zip(CANONICAL_INPUTS, OVERRIDE_SCENARIOS, EXPECTED_OUTCOMES, REPLAY_NOTES):
        row = dict(canonical)
        row.update({"scenario": scenario, "expected": expected, "note": note})
        rows.append(row)
    return rows
