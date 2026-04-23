"""Deterministic switch fixture pack 017.

This pack models a realistic slice of canonical switch inputs and expected
stage_03_switch_resolve outputs. Cases cover default resolution, switch-id
precedence, target-id precedence, invalid overrides, reports_real exclusion,
and deterministic replay semantics. The payload is encoded in Python so the
bundle remains Python-heavy while still shipping concrete golden data.
"""

from __future__ import annotations

PACK_ID = "pack_017"
CANONICAL_INPUTS = []
OVERRIDE_SCENARIOS = []
EXPECTED_OUTCOMES = []
REPLAY_NOTES = []
CANONICAL_INPUTS.append({
    "switch_id": "switch.route.017_01",
    "target_type": "route",
    "target_id": "route.017_01",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/017_01.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/017_01.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_017_01",
    "overrides": {"switch.route.017_01": False},
    "why": "Pack 017 item 01 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_017_01",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.017_01 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 017_01 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/017_01.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.017_02",
    "target_type": "boundary",
    "target_id": "boundary.017_02",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/017_02.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/017_02.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_017_02",
    "overrides": {"switch.boundary.017_02": "invalid"},
    "why": "Pack 017 item 02 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_017_02",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.017_02 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 017_02 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/017_02.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.017_03",
    "target_type": "module",
    "target_id": "module.017_03",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/017_03.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/017_03.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_017_03",
    "overrides": {"switch.module.017_03": None},
    "why": "Pack 017 item 03 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_017_03",
    "resolved_value": True,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.017_03 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 017_03 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/017_03.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.017_04",
    "target_type": "route",
    "target_id": "route.017_04",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/017_04.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/017_04.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_017_04",
    "overrides": {"switch.route.017_04": True},
    "why": "Pack 017 item 04 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_017_04",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.017_04 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 017_04 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/017_04.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.017_05",
    "target_type": "boundary",
    "target_id": "boundary.017_05",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/017_05.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/017_05.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_017_05",
    "overrides": {"switch.boundary.017_05": False},
    "why": "Pack 017 item 05 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_017_05",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.017_05 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 017_05 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/017_05.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.017_06",
    "target_type": "module",
    "target_id": "module.017_06",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/017_06.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/017_06.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_017_06",
    "overrides": {"switch.module.017_06": "invalid"},
    "why": "Pack 017 item 06 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_017_06",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.017_06 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 017_06 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/017_06.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.017_07",
    "target_type": "route",
    "target_id": "route.017_07",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/017_07.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/017_07.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_017_07",
    "overrides": {"switch.route.017_07": None},
    "why": "Pack 017 item 07 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_017_07",
    "resolved_value": True,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.route.017_07 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 017_07 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/017_07.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.017_08",
    "target_type": "boundary",
    "target_id": "boundary.017_08",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/017_08.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/017_08.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_017_08",
    "overrides": {"switch.boundary.017_08": True},
    "why": "Pack 017 item 08 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_017_08",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.017_08 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 017_08 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/017_08.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.017_09",
    "target_type": "module",
    "target_id": "module.017_09",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/017_09.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/017_09.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_017_09",
    "overrides": {"switch.module.017_09": False},
    "why": "Pack 017 item 09 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_017_09",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.017_09 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 017_09 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/017_09.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.017_10",
    "target_type": "route",
    "target_id": "route.017_10",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/017_10.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/017_10.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_017_10",
    "overrides": {"switch.route.017_10": "invalid"},
    "why": "Pack 017 item 10 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_017_10",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.route.017_10 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 017_10 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/017_10.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.017_11",
    "target_type": "boundary",
    "target_id": "boundary.017_11",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/017_11.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/017_11.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_017_11",
    "overrides": {"switch.boundary.017_11": None},
    "why": "Pack 017 item 11 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_017_11",
    "resolved_value": True,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.boundary.017_11 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 017_11 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/017_11.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.017_12",
    "target_type": "module",
    "target_id": "module.017_12",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/017_12.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/017_12.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_017_12",
    "overrides": {"switch.module.017_12": True},
    "why": "Pack 017 item 12 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_017_12",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.module.017_12 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 017_12 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/017_12.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.017_13",
    "target_type": "route",
    "target_id": "route.017_13",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/route/017_13.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/017_13.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_017_13",
    "overrides": {"switch.route.017_13": False},
    "why": "Pack 017 item 13 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_017_13",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.017_13 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 017_13 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/017_13.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.017_14",
    "target_type": "boundary",
    "target_id": "boundary.017_14",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/boundary/017_14.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/017_14.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_017_14",
    "overrides": {"switch.boundary.017_14": "invalid"},
    "why": "Pack 017 item 14 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_017_14",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.boundary.017_14 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 017_14 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/017_14.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.017_15",
    "target_type": "module",
    "target_id": "module.017_15",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/module/017_15.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/017_15.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_017_15",
    "overrides": {"switch.module.017_15": None},
    "why": "Pack 017 item 15 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_017_15",
    "resolved_value": True,
    "decision_source": "default",
    "precedence_path": ['default'],
    "trace_note": "Trace retains explicit path for switch.module.017_15 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 017_15 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/017_15.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.route.017_16",
    "target_type": "route",
    "target_id": "route.017_16",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/route/017_16.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/route/017_16.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_017_16",
    "overrides": {"switch.route.017_16": True},
    "why": "Pack 017 item 16 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_017_16",
    "resolved_value": True,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.route.017_16 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 017_16 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/route/017_16.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.boundary.017_17",
    "target_type": "boundary",
    "target_id": "boundary.017_17",
    "default_value": True,
    "declared_in": "apps/ar-k/pya/generated/boundary/017_17.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/boundary/017_17.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_017_17",
    "overrides": {"switch.boundary.017_17": False},
    "why": "Pack 017 item 17 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_017_17",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'switch_id'],
    "trace_note": "Trace retains explicit path for switch.boundary.017_17 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 017_17 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/boundary/017_17.json")

CANONICAL_INPUTS.append({
    "switch_id": "switch.module.017_18",
    "target_type": "module",
    "target_id": "module.017_18",
    "default_value": False,
    "declared_in": "apps/ar-k/pya/generated/module/017_18.py",
    "excluded_counterexample": "apps/ar-k/reports_real/generated/module/017_18.json",
})
OVERRIDE_SCENARIOS.append({
    "scenario_id": "override_017_18",
    "overrides": {"switch.module.017_18": "invalid"},
    "why": "Pack 017 item 18 verifies deterministic precedence and safe handling of invalid overrides.",
})
EXPECTED_OUTCOMES.append({
    "scenario_id": "override_017_18",
    "resolved_value": False,
    "decision_source": "switch_id",
    "precedence_path": ['default', 'invalid_override_ignored'],
    "trace_note": "Trace retains explicit path for switch.module.017_18 and never rewrites canonical inputs.",
})
REPLAY_NOTES.append("Replay 017_18 must preserve ordering by switch_id and leave reports_real excluded: apps/ar-k/reports_real/generated/module/017_18.json")

def iter_case_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for canonical, scenario, expected, note in zip(CANONICAL_INPUTS, OVERRIDE_SCENARIOS, EXPECTED_OUTCOMES, REPLAY_NOTES):
        row = dict(canonical)
        row.update({"scenario": scenario, "expected": expected, "note": note})
        rows.append(row)
    return rows
