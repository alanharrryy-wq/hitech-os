"""Deterministic switch fixture pack 154.

This pack models a realistic slice of canonical switch inputs and expected
stage_03_switch_resolve outputs. Cases cover default resolution, switch-id
precedence, target-id precedence, invalid overrides, reports_real exclusion,
and deterministic replay semantics. The payload is encoded in Python so the
bundle remains Python-heavy while still shipping concrete golden data.
"""

from __future__ import annotations

PACK_ID = "pack_154"
CANONICAL_INPUTS = []
OVERRIDE_SCENARIOS = []
EXPECTED_OUTCOMES = []
REPLAY_NOTES = []
CANONICAL_INPUTS.append({
    "switch_id": "switch.route.154_01",
    "target_type": "route",
    "target_id": "route.154_01",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/154_01.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/154_01.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_154_01",
    "overrides": {"switch.route.154_01": False},
    "why": "Pack 154 item 01 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_154_01",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.154_01 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 154_01 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/154_01.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.154_02",
    "target_type": "boundary",
    "target_id": "boundary.154_02",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/154_02.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/154_02.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_154_02",
    "overrides": {"switch.boundary.154_02": "invalid"},
    "why": "Pack 154 item 02 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_154_02",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.154_02 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 154_02 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/154_02.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.154_03",
    "target_type": "module",
    "target_id": "module.154_03",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/154_03.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/154_03.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_154_03",
    "overrides": {"switch.module.154_03": None},
    "why": "Pack 154 item 03 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_154_03",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.154_03 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 154_03 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/154_03.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.154_04",
    "target_type": "route",
    "target_id": "route.154_04",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/154_04.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/154_04.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_154_04",
    "overrides": {"switch.route.154_04": True},
    "why": "Pack 154 item 04 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_154_04",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.154_04 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 154_04 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/154_04.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.154_05",
    "target_type": "boundary",
    "target_id": "boundary.154_05",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/154_05.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/154_05.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_154_05",
    "overrides": {"switch.boundary.154_05": False},
    "why": "Pack 154 item 05 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_154_05",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.154_05 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 154_05 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/154_05.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.154_06",
    "target_type": "module",
    "target_id": "module.154_06",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/154_06.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/154_06.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_154_06",
    "overrides": {"switch.module.154_06": "invalid"},
    "why": "Pack 154 item 06 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_154_06",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.154_06 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 154_06 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/154_06.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.154_07",
    "target_type": "route",
    "target_id": "route.154_07",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/154_07.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/154_07.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_154_07",
    "overrides": {"switch.route.154_07": None},
    "why": "Pack 154 item 07 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_154_07",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.route.154_07 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 154_07 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/154_07.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.154_08",
    "target_type": "boundary",
    "target_id": "boundary.154_08",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/154_08.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/154_08.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_154_08",
    "overrides": {"switch.boundary.154_08": True},
    "why": "Pack 154 item 08 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_154_08",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.154_08 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 154_08 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/154_08.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.154_09",
    "target_type": "module",
    "target_id": "module.154_09",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/154_09.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/154_09.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_154_09",
    "overrides": {"switch.module.154_09": False},
    "why": "Pack 154 item 09 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_154_09",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.154_09 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 154_09 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/154_09.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.154_10",
    "target_type": "route",
    "target_id": "route.154_10",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/154_10.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/154_10.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_154_10",
    "overrides": {"switch.route.154_10": "invalid"},
    "why": "Pack 154 item 10 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_154_10",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.route.154_10 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 154_10 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/154_10.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.154_11",
    "target_type": "boundary",
    "target_id": "boundary.154_11",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/154_11.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/154_11.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_154_11",
    "overrides": {"switch.boundary.154_11": None},
    "why": "Pack 154 item 11 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_154_11",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.boundary.154_11 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 154_11 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/154_11.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.154_12",
    "target_type": "module",
    "target_id": "module.154_12",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/154_12.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/154_12.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_154_12",
    "overrides": {"switch.module.154_12": True},
    "why": "Pack 154 item 12 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_154_12",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.154_12 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 154_12 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/154_12.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.154_13",
    "target_type": "route",
    "target_id": "route.154_13",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/154_13.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/154_13.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_154_13",
    "overrides": {"switch.route.154_13": False},
    "why": "Pack 154 item 13 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_154_13",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.154_13 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 154_13 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/154_13.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.154_14",
    "target_type": "boundary",
    "target_id": "boundary.154_14",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/154_14.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/154_14.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_154_14",
    "overrides": {"switch.boundary.154_14": "invalid"},
    "why": "Pack 154 item 14 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_154_14",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.154_14 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 154_14 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/154_14.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.154_15",
    "target_type": "module",
    "target_id": "module.154_15",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/154_15.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/154_15.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_154_15",
    "overrides": {"switch.module.154_15": None},
    "why": "Pack 154 item 15 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_154_15",
    "resolved_value": False,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.154_15 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 154_15 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/154_15.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.154_16",
    "target_type": "route",
    "target_id": "route.154_16",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/154_16.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/154_16.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_154_16",
    "overrides": {"switch.route.154_16": True},
    "why": "Pack 154 item 16 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_154_16",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.154_16 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 154_16 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/154_16.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.154_17",
    "target_type": "boundary",
    "target_id": "boundary.154_17",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/154_17.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/154_17.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_154_17",
    "overrides": {"switch.boundary.154_17": False},
    "why": "Pack 154 item 17 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_154_17",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.154_17 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 154_17 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/154_17.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.154_18",
    "target_type": "module",
    "target_id": "module.154_18",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/154_18.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/154_18.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_154_18",
    "overrides": {"switch.module.154_18": "invalid"},
    "why": "Pack 154 item 18 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_154_18",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.154_18 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 154_18 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/154_18.json")

def iter_case_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for canonical, scenario, expected, note in zip(CANONICAL_INPUTS, OVERRIDE_SCENARIOS, EXPECTED_OUTCOMES, REPLAY_NOTES):
        row = dict(canonical)
        row.update({"scenario": scenario, "expected": expected, "note": note})
        rows.append(row)
    return rows
