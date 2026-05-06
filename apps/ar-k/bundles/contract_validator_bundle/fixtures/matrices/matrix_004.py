from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 4/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 4/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 4/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 4/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 4/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 4/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 4/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 4/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 4/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 4/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 4/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 4/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 4/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 4/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 4/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 4/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 4/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 4/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 4/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 4/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 4/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 4/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 4/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 4/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 4/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_004_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 4: validator observes canonical read-only evidence and compares 2 registries against policy segment 4.",
    "bad_pattern": "bad pattern 1 in matrix 4: writer drift toward family 1, generated path reports_real/segment_4_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_4_1, boundary=bnd_matrix_4_1, switch=sw_matrix_4_1, hash_hint=4caaa93fb401cbc5"
  },
  {
    "matrix_row_id": "matrix_004_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 4: validator observes canonical read-only evidence and compares 3 registries against policy segment 4.",
    "bad_pattern": "bad pattern 2 in matrix 4: writer drift toward family 2, generated path reports_real/segment_4_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_4_2, boundary=bnd_matrix_4_2, switch=sw_matrix_4_2, hash_hint=2afafcddf683494c"
  },
  {
    "matrix_row_id": "matrix_004_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 4: validator observes canonical read-only evidence and compares 4 registries against policy segment 4.",
    "bad_pattern": "bad pattern 3 in matrix 4: writer drift toward family 3, generated path reports_real/segment_4_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_4_3, boundary=bnd_matrix_4_3, switch=sw_matrix_4_3, hash_hint=2a17f163b5fe3845"
  },
  {
    "matrix_row_id": "matrix_004_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 4: validator observes canonical read-only evidence and compares 5 registries against policy segment 4.",
    "bad_pattern": "bad pattern 4 in matrix 4: writer drift toward family 4, generated path reports_real/segment_4_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_4_4, boundary=bnd_matrix_4_4, switch=sw_matrix_4_4, hash_hint=9e22dafdfa889997"
  },
  {
    "matrix_row_id": "matrix_004_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 4: validator observes canonical read-only evidence and compares 1 registries against policy segment 4.",
    "bad_pattern": "bad pattern 5 in matrix 4: writer drift toward family 5, generated path reports_real/segment_4_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_4_5, boundary=bnd_matrix_4_5, switch=sw_matrix_4_5, hash_hint=0bf18b49509506f8"
  },
  {
    "matrix_row_id": "matrix_004_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 4: validator observes canonical read-only evidence and compares 2 registries against policy segment 4.",
    "bad_pattern": "bad pattern 6 in matrix 4: writer drift toward family 6, generated path reports_real/segment_4_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_4_6, boundary=bnd_matrix_4_6, switch=sw_matrix_4_6, hash_hint=9983f17a347c88dd"
  },
  {
    "matrix_row_id": "matrix_004_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 4: validator observes canonical read-only evidence and compares 3 registries against policy segment 4.",
    "bad_pattern": "bad pattern 7 in matrix 4: writer drift toward family 0, generated path reports_real/segment_4_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_4_7, boundary=bnd_matrix_4_7, switch=sw_matrix_4_7, hash_hint=7b11c5f72091e97a"
  },
  {
    "matrix_row_id": "matrix_004_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 4: validator observes canonical read-only evidence and compares 4 registries against policy segment 4.",
    "bad_pattern": "bad pattern 8 in matrix 4: writer drift toward family 1, generated path reports_real/segment_4_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_4_8, boundary=bnd_matrix_4_8, switch=sw_matrix_4_8, hash_hint=38678eee06598adb"
  },
  {
    "matrix_row_id": "matrix_004_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 4: validator observes canonical read-only evidence and compares 5 registries against policy segment 4.",
    "bad_pattern": "bad pattern 9 in matrix 4: writer drift toward family 2, generated path reports_real/segment_4_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_4_9, boundary=bnd_matrix_4_9, switch=sw_matrix_4_9, hash_hint=2b9dd0cdd43eb694"
  },
  {
    "matrix_row_id": "matrix_004_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 4: validator observes canonical read-only evidence and compares 1 registries against policy segment 4.",
    "bad_pattern": "bad pattern 10 in matrix 4: writer drift toward family 3, generated path reports_real/segment_4_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_4_10, boundary=bnd_matrix_4_10, switch=sw_matrix_4_10, hash_hint=1ef3e4d25d6a5dc8"
  },
  {
    "matrix_row_id": "matrix_004_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 4: validator observes canonical read-only evidence and compares 2 registries against policy segment 4.",
    "bad_pattern": "bad pattern 11 in matrix 4: writer drift toward family 4, generated path reports_real/segment_4_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_4_11, boundary=bnd_matrix_4_11, switch=sw_matrix_4_11, hash_hint=ad6b7faa302bf398"
  },
  {
    "matrix_row_id": "matrix_004_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 4: validator observes canonical read-only evidence and compares 3 registries against policy segment 4.",
    "bad_pattern": "bad pattern 12 in matrix 4: writer drift toward family 5, generated path reports_real/segment_4_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_4_12, boundary=bnd_matrix_4_12, switch=sw_matrix_4_12, hash_hint=3e4270b504b08bf4"
  },
  {
    "matrix_row_id": "matrix_004_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 4: validator observes canonical read-only evidence and compares 4 registries against policy segment 4.",
    "bad_pattern": "bad pattern 13 in matrix 4: writer drift toward family 6, generated path reports_real/segment_4_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_4_13, boundary=bnd_matrix_4_13, switch=sw_matrix_4_13, hash_hint=033d028abd00cb36"
  },
  {
    "matrix_row_id": "matrix_004_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 4: validator observes canonical read-only evidence and compares 5 registries against policy segment 4.",
    "bad_pattern": "bad pattern 14 in matrix 4: writer drift toward family 0, generated path reports_real/segment_4_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_4_14, boundary=bnd_matrix_4_14, switch=sw_matrix_4_14, hash_hint=1e4d8c9a3ab8733f"
  },
  {
    "matrix_row_id": "matrix_004_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 4: validator observes canonical read-only evidence and compares 1 registries against policy segment 4.",
    "bad_pattern": "bad pattern 15 in matrix 4: writer drift toward family 1, generated path reports_real/segment_4_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_4_15, boundary=bnd_matrix_4_15, switch=sw_matrix_4_15, hash_hint=4b6a6a36d88bc2f0"
  },
  {
    "matrix_row_id": "matrix_004_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 4: validator observes canonical read-only evidence and compares 2 registries against policy segment 4.",
    "bad_pattern": "bad pattern 16 in matrix 4: writer drift toward family 2, generated path reports_real/segment_4_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_4_16, boundary=bnd_matrix_4_16, switch=sw_matrix_4_16, hash_hint=42155ee3e0ea7b00"
  },
  {
    "matrix_row_id": "matrix_004_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 4: validator observes canonical read-only evidence and compares 3 registries against policy segment 4.",
    "bad_pattern": "bad pattern 17 in matrix 4: writer drift toward family 3, generated path reports_real/segment_4_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_4_17, boundary=bnd_matrix_4_17, switch=sw_matrix_4_17, hash_hint=8b0c0d7f9ebe2e73"
  },
  {
    "matrix_row_id": "matrix_004_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 4: validator observes canonical read-only evidence and compares 4 registries against policy segment 4.",
    "bad_pattern": "bad pattern 18 in matrix 4: writer drift toward family 4, generated path reports_real/segment_4_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_4_18, boundary=bnd_matrix_4_18, switch=sw_matrix_4_18, hash_hint=274c0b51a3c01d1e"
  },
  {
    "matrix_row_id": "matrix_004_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 4: validator observes canonical read-only evidence and compares 5 registries against policy segment 4.",
    "bad_pattern": "bad pattern 19 in matrix 4: writer drift toward family 5, generated path reports_real/segment_4_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_4_19, boundary=bnd_matrix_4_19, switch=sw_matrix_4_19, hash_hint=0de68a831324b87f"
  },
  {
    "matrix_row_id": "matrix_004_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 4: validator observes canonical read-only evidence and compares 1 registries against policy segment 4.",
    "bad_pattern": "bad pattern 20 in matrix 4: writer drift toward family 6, generated path reports_real/segment_4_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_4_20, boundary=bnd_matrix_4_20, switch=sw_matrix_4_20, hash_hint=05cf4537cc6b9898"
  },
  {
    "matrix_row_id": "matrix_004_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 4: validator observes canonical read-only evidence and compares 2 registries against policy segment 4.",
    "bad_pattern": "bad pattern 21 in matrix 4: writer drift toward family 0, generated path reports_real/segment_4_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_4_21, boundary=bnd_matrix_4_21, switch=sw_matrix_4_21, hash_hint=5d03f275fce95198"
  },
  {
    "matrix_row_id": "matrix_004_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 4: validator observes canonical read-only evidence and compares 3 registries against policy segment 4.",
    "bad_pattern": "bad pattern 22 in matrix 4: writer drift toward family 1, generated path reports_real/segment_4_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_4_22, boundary=bnd_matrix_4_22, switch=sw_matrix_4_22, hash_hint=816010bd0df200ba"
  },
  {
    "matrix_row_id": "matrix_004_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 4: validator observes canonical read-only evidence and compares 4 registries against policy segment 4.",
    "bad_pattern": "bad pattern 23 in matrix 4: writer drift toward family 2, generated path reports_real/segment_4_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_4_23, boundary=bnd_matrix_4_23, switch=sw_matrix_4_23, hash_hint=eff6cc895a632d6a"
  },
  {
    "matrix_row_id": "matrix_004_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 4: validator observes canonical read-only evidence and compares 5 registries against policy segment 4.",
    "bad_pattern": "bad pattern 24 in matrix 4: writer drift toward family 3, generated path reports_real/segment_4_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_4_24, boundary=bnd_matrix_4_24, switch=sw_matrix_4_24, hash_hint=48db33b5ff7b7c3e"
  },
  {
    "matrix_row_id": "matrix_004_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 4: validator observes canonical read-only evidence and compares 1 registries against policy segment 4.",
    "bad_pattern": "bad pattern 25 in matrix 4: writer drift toward family 4, generated path reports_real/segment_4_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_4_25, boundary=bnd_matrix_4_25, switch=sw_matrix_4_25, hash_hint=fc1c6fafe0e1bea8"
  },
  {
    "matrix_row_id": "matrix_004_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 4: validator observes canonical read-only evidence and compares 2 registries against policy segment 4.",
    "bad_pattern": "bad pattern 26 in matrix 4: writer drift toward family 5, generated path reports_real/segment_4_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_4_26, boundary=bnd_matrix_4_26, switch=sw_matrix_4_26, hash_hint=d69884b85eac0acd"
  },
  {
    "matrix_row_id": "matrix_004_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 4: validator observes canonical read-only evidence and compares 3 registries against policy segment 4.",
    "bad_pattern": "bad pattern 27 in matrix 4: writer drift toward family 6, generated path reports_real/segment_4_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_4_27, boundary=bnd_matrix_4_27, switch=sw_matrix_4_27, hash_hint=1530a1617fc1d07c"
  },
  {
    "matrix_row_id": "matrix_004_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 4: validator observes canonical read-only evidence and compares 4 registries against policy segment 4.",
    "bad_pattern": "bad pattern 28 in matrix 4: writer drift toward family 0, generated path reports_real/segment_4_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_4_28, boundary=bnd_matrix_4_28, switch=sw_matrix_4_28, hash_hint=88f841e3fe9acfbf"
  },
  {
    "matrix_row_id": "matrix_004_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 4: validator observes canonical read-only evidence and compares 5 registries against policy segment 4.",
    "bad_pattern": "bad pattern 29 in matrix 4: writer drift toward family 1, generated path reports_real/segment_4_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_4_29, boundary=bnd_matrix_4_29, switch=sw_matrix_4_29, hash_hint=0c394be461f82ca0"
  },
  {
    "matrix_row_id": "matrix_004_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 4: validator observes canonical read-only evidence and compares 1 registries against policy segment 4.",
    "bad_pattern": "bad pattern 30 in matrix 4: writer drift toward family 2, generated path reports_real/segment_4_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_4_30, boundary=bnd_matrix_4_30, switch=sw_matrix_4_30, hash_hint=3a5b9253d5b2932d"
  },
  {
    "matrix_row_id": "matrix_004_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 4: validator observes canonical read-only evidence and compares 2 registries against policy segment 4.",
    "bad_pattern": "bad pattern 31 in matrix 4: writer drift toward family 3, generated path reports_real/segment_4_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_4_31, boundary=bnd_matrix_4_31, switch=sw_matrix_4_31, hash_hint=bf95b2d157b9fa0e"
  },
  {
    "matrix_row_id": "matrix_004_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 4: validator observes canonical read-only evidence and compares 3 registries against policy segment 4.",
    "bad_pattern": "bad pattern 32 in matrix 4: writer drift toward family 4, generated path reports_real/segment_4_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_4_32, boundary=bnd_matrix_4_32, switch=sw_matrix_4_32, hash_hint=5ec9419a35d3625e"
  },
  {
    "matrix_row_id": "matrix_004_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 4: validator observes canonical read-only evidence and compares 4 registries against policy segment 4.",
    "bad_pattern": "bad pattern 33 in matrix 4: writer drift toward family 5, generated path reports_real/segment_4_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_4_33, boundary=bnd_matrix_4_33, switch=sw_matrix_4_33, hash_hint=623cdee7aabbce0b"
  },
  {
    "matrix_row_id": "matrix_004_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 4: validator observes canonical read-only evidence and compares 5 registries against policy segment 4.",
    "bad_pattern": "bad pattern 34 in matrix 4: writer drift toward family 6, generated path reports_real/segment_4_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_4_34, boundary=bnd_matrix_4_34, switch=sw_matrix_4_34, hash_hint=3af10039a65e4f42"
  },
  {
    "matrix_row_id": "matrix_004_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 4: validator observes canonical read-only evidence and compares 1 registries against policy segment 4.",
    "bad_pattern": "bad pattern 35 in matrix 4: writer drift toward family 0, generated path reports_real/segment_4_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_4_35, boundary=bnd_matrix_4_35, switch=sw_matrix_4_35, hash_hint=7cfc8fe0425332fa"
  },
  {
    "matrix_row_id": "matrix_004_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 4: validator observes canonical read-only evidence and compares 2 registries against policy segment 4.",
    "bad_pattern": "bad pattern 36 in matrix 4: writer drift toward family 1, generated path reports_real/segment_4_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_4_36, boundary=bnd_matrix_4_36, switch=sw_matrix_4_36, hash_hint=1b3735e9f113f11a"
  },
  {
    "matrix_row_id": "matrix_004_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 4: validator observes canonical read-only evidence and compares 3 registries against policy segment 4.",
    "bad_pattern": "bad pattern 37 in matrix 4: writer drift toward family 2, generated path reports_real/segment_4_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_4_37, boundary=bnd_matrix_4_37, switch=sw_matrix_4_37, hash_hint=579867cba4cc48fe"
  },
  {
    "matrix_row_id": "matrix_004_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 4: validator observes canonical read-only evidence and compares 4 registries against policy segment 4.",
    "bad_pattern": "bad pattern 38 in matrix 4: writer drift toward family 3, generated path reports_real/segment_4_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_4_38, boundary=bnd_matrix_4_38, switch=sw_matrix_4_38, hash_hint=a8dcfbdf42221ebf"
  },
  {
    "matrix_row_id": "matrix_004_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 4: validator observes canonical read-only evidence and compares 5 registries against policy segment 4.",
    "bad_pattern": "bad pattern 39 in matrix 4: writer drift toward family 4, generated path reports_real/segment_4_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_4_39, boundary=bnd_matrix_4_39, switch=sw_matrix_4_39, hash_hint=e6c7055d4acb4a16"
  },
  {
    "matrix_row_id": "matrix_004_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 4: validator observes canonical read-only evidence and compares 1 registries against policy segment 4.",
    "bad_pattern": "bad pattern 40 in matrix 4: writer drift toward family 5, generated path reports_real/segment_4_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_4_40, boundary=bnd_matrix_4_40, switch=sw_matrix_4_40, hash_hint=b04bf9550f313646"
  },
  {
    "matrix_row_id": "matrix_004_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 4: validator observes canonical read-only evidence and compares 2 registries against policy segment 4.",
    "bad_pattern": "bad pattern 41 in matrix 4: writer drift toward family 6, generated path reports_real/segment_4_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_4_41, boundary=bnd_matrix_4_41, switch=sw_matrix_4_41, hash_hint=b29cf6c459471570"
  },
  {
    "matrix_row_id": "matrix_004_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 4: validator observes canonical read-only evidence and compares 3 registries against policy segment 4.",
    "bad_pattern": "bad pattern 42 in matrix 4: writer drift toward family 0, generated path reports_real/segment_4_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_4_42, boundary=bnd_matrix_4_42, switch=sw_matrix_4_42, hash_hint=bb56d96847831022"
  },
  {
    "matrix_row_id": "matrix_004_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 4: validator observes canonical read-only evidence and compares 4 registries against policy segment 4.",
    "bad_pattern": "bad pattern 43 in matrix 4: writer drift toward family 1, generated path reports_real/segment_4_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_4_43, boundary=bnd_matrix_4_43, switch=sw_matrix_4_43, hash_hint=402fdd582881cba4"
  },
  {
    "matrix_row_id": "matrix_004_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 4: validator observes canonical read-only evidence and compares 5 registries against policy segment 4.",
    "bad_pattern": "bad pattern 44 in matrix 4: writer drift toward family 2, generated path reports_real/segment_4_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_4_44, boundary=bnd_matrix_4_44, switch=sw_matrix_4_44, hash_hint=eb96780429e72e52"
  },
  {
    "matrix_row_id": "matrix_004_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 4: validator observes canonical read-only evidence and compares 1 registries against policy segment 4.",
    "bad_pattern": "bad pattern 45 in matrix 4: writer drift toward family 3, generated path reports_real/segment_4_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_4_45, boundary=bnd_matrix_4_45, switch=sw_matrix_4_45, hash_hint=e47a3956d5b800a8"
  },
  {
    "matrix_row_id": "matrix_004_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 4: validator observes canonical read-only evidence and compares 2 registries against policy segment 4.",
    "bad_pattern": "bad pattern 46 in matrix 4: writer drift toward family 4, generated path reports_real/segment_4_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_4_46, boundary=bnd_matrix_4_46, switch=sw_matrix_4_46, hash_hint=ded062ba94bd5816"
  },
  {
    "matrix_row_id": "matrix_004_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 4: validator observes canonical read-only evidence and compares 3 registries against policy segment 4.",
    "bad_pattern": "bad pattern 47 in matrix 4: writer drift toward family 5, generated path reports_real/segment_4_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_4_47, boundary=bnd_matrix_4_47, switch=sw_matrix_4_47, hash_hint=759c0820e7462609"
  },
  {
    "matrix_row_id": "matrix_004_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 4: validator observes canonical read-only evidence and compares 4 registries against policy segment 4.",
    "bad_pattern": "bad pattern 48 in matrix 4: writer drift toward family 6, generated path reports_real/segment_4_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_4_48, boundary=bnd_matrix_4_48, switch=sw_matrix_4_48, hash_hint=a780315bc77d8d4a"
  },
  {
    "matrix_row_id": "matrix_004_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 4: validator observes canonical read-only evidence and compares 5 registries against policy segment 4.",
    "bad_pattern": "bad pattern 49 in matrix 4: writer drift toward family 0, generated path reports_real/segment_4_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_4_49, boundary=bnd_matrix_4_49, switch=sw_matrix_4_49, hash_hint=f146f8df9f58a3a7"
  },
  {
    "matrix_row_id": "matrix_004_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 4: validator observes canonical read-only evidence and compares 1 registries against policy segment 4.",
    "bad_pattern": "bad pattern 50 in matrix 4: writer drift toward family 1, generated path reports_real/segment_4_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_4_50, boundary=bnd_matrix_4_50, switch=sw_matrix_4_50, hash_hint=4d470e58be3ef384"
  },
  {
    "matrix_row_id": "matrix_004_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 4: validator observes canonical read-only evidence and compares 2 registries against policy segment 4.",
    "bad_pattern": "bad pattern 51 in matrix 4: writer drift toward family 2, generated path reports_real/segment_4_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_4_51, boundary=bnd_matrix_4_51, switch=sw_matrix_4_51, hash_hint=c4906fe8e202ff1c"
  },
  {
    "matrix_row_id": "matrix_004_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 4: validator observes canonical read-only evidence and compares 3 registries against policy segment 4.",
    "bad_pattern": "bad pattern 52 in matrix 4: writer drift toward family 3, generated path reports_real/segment_4_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_4_52, boundary=bnd_matrix_4_52, switch=sw_matrix_4_52, hash_hint=a4cad0980226577a"
  },
  {
    "matrix_row_id": "matrix_004_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 4: validator observes canonical read-only evidence and compares 4 registries against policy segment 4.",
    "bad_pattern": "bad pattern 53 in matrix 4: writer drift toward family 4, generated path reports_real/segment_4_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_4_53, boundary=bnd_matrix_4_53, switch=sw_matrix_4_53, hash_hint=6feb7992bf0ed045"
  },
  {
    "matrix_row_id": "matrix_004_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 4: validator observes canonical read-only evidence and compares 5 registries against policy segment 4.",
    "bad_pattern": "bad pattern 54 in matrix 4: writer drift toward family 5, generated path reports_real/segment_4_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_4_54, boundary=bnd_matrix_4_54, switch=sw_matrix_4_54, hash_hint=3f03362fd36bdabe"
  },
  {
    "matrix_row_id": "matrix_004_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 4: validator observes canonical read-only evidence and compares 1 registries against policy segment 4.",
    "bad_pattern": "bad pattern 55 in matrix 4: writer drift toward family 6, generated path reports_real/segment_4_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_4_55, boundary=bnd_matrix_4_55, switch=sw_matrix_4_55, hash_hint=e639eead2dfa8b78"
  },
  {
    "matrix_row_id": "matrix_004_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 4: validator observes canonical read-only evidence and compares 2 registries against policy segment 4.",
    "bad_pattern": "bad pattern 56 in matrix 4: writer drift toward family 0, generated path reports_real/segment_4_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_4_56, boundary=bnd_matrix_4_56, switch=sw_matrix_4_56, hash_hint=4365b773ab1de3e5"
  },
  {
    "matrix_row_id": "matrix_004_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 4: validator observes canonical read-only evidence and compares 3 registries against policy segment 4.",
    "bad_pattern": "bad pattern 57 in matrix 4: writer drift toward family 1, generated path reports_real/segment_4_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_4_57, boundary=bnd_matrix_4_57, switch=sw_matrix_4_57, hash_hint=cb0184ff8d8b7807"
  },
  {
    "matrix_row_id": "matrix_004_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 4: validator observes canonical read-only evidence and compares 4 registries against policy segment 4.",
    "bad_pattern": "bad pattern 58 in matrix 4: writer drift toward family 2, generated path reports_real/segment_4_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_4_58, boundary=bnd_matrix_4_58, switch=sw_matrix_4_58, hash_hint=865370e1bba791ba"
  },
  {
    "matrix_row_id": "matrix_004_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 4: validator observes canonical read-only evidence and compares 5 registries against policy segment 4.",
    "bad_pattern": "bad pattern 59 in matrix 4: writer drift toward family 3, generated path reports_real/segment_4_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_4_59, boundary=bnd_matrix_4_59, switch=sw_matrix_4_59, hash_hint=8611164954c379c5"
  },
  {
    "matrix_row_id": "matrix_004_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 4: validator observes canonical read-only evidence and compares 1 registries against policy segment 4.",
    "bad_pattern": "bad pattern 60 in matrix 4: writer drift toward family 4, generated path reports_real/segment_4_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_4_60, boundary=bnd_matrix_4_60, switch=sw_matrix_4_60, hash_hint=81615912cc5f36dc"
  }
]
