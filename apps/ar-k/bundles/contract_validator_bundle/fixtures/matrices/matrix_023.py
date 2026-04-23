from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 23/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 23/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 23/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 23/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 23/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 23/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 23/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 23/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 23/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 23/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 23/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 23/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 23/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 23/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 23/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 23/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 23/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 23/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 23/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 23/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 23/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 23/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 23/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 23/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 23/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_023_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 23: validator observes canonical read-only evidence and compares 2 registries against policy segment 23.",
    "bad_pattern": "bad pattern 1 in matrix 23: writer drift toward family 1, generated path reports_real/segment_23_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_23_1, boundary=bnd_matrix_23_1, switch=sw_matrix_23_1, hash_hint=4a0e28713d67dd94"
  },
  {
    "matrix_row_id": "matrix_023_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 23: validator observes canonical read-only evidence and compares 3 registries against policy segment 23.",
    "bad_pattern": "bad pattern 2 in matrix 23: writer drift toward family 2, generated path reports_real/segment_23_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_23_2, boundary=bnd_matrix_23_2, switch=sw_matrix_23_2, hash_hint=632910ed2e977518"
  },
  {
    "matrix_row_id": "matrix_023_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 23: validator observes canonical read-only evidence and compares 4 registries against policy segment 23.",
    "bad_pattern": "bad pattern 3 in matrix 23: writer drift toward family 3, generated path reports_real/segment_23_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_23_3, boundary=bnd_matrix_23_3, switch=sw_matrix_23_3, hash_hint=1057d81ab1eb1a30"
  },
  {
    "matrix_row_id": "matrix_023_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 23: validator observes canonical read-only evidence and compares 5 registries against policy segment 23.",
    "bad_pattern": "bad pattern 4 in matrix 23: writer drift toward family 4, generated path reports_real/segment_23_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_23_4, boundary=bnd_matrix_23_4, switch=sw_matrix_23_4, hash_hint=068caa191e8d6779"
  },
  {
    "matrix_row_id": "matrix_023_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 23: validator observes canonical read-only evidence and compares 1 registries against policy segment 23.",
    "bad_pattern": "bad pattern 5 in matrix 23: writer drift toward family 5, generated path reports_real/segment_23_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_23_5, boundary=bnd_matrix_23_5, switch=sw_matrix_23_5, hash_hint=c2609ea248dd6b2d"
  },
  {
    "matrix_row_id": "matrix_023_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 23: validator observes canonical read-only evidence and compares 2 registries against policy segment 23.",
    "bad_pattern": "bad pattern 6 in matrix 23: writer drift toward family 6, generated path reports_real/segment_23_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_23_6, boundary=bnd_matrix_23_6, switch=sw_matrix_23_6, hash_hint=8ca013ca967edb69"
  },
  {
    "matrix_row_id": "matrix_023_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 23: validator observes canonical read-only evidence and compares 3 registries against policy segment 23.",
    "bad_pattern": "bad pattern 7 in matrix 23: writer drift toward family 0, generated path reports_real/segment_23_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_23_7, boundary=bnd_matrix_23_7, switch=sw_matrix_23_7, hash_hint=97c6f54f59b42ca5"
  },
  {
    "matrix_row_id": "matrix_023_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 23: validator observes canonical read-only evidence and compares 4 registries against policy segment 23.",
    "bad_pattern": "bad pattern 8 in matrix 23: writer drift toward family 1, generated path reports_real/segment_23_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_23_8, boundary=bnd_matrix_23_8, switch=sw_matrix_23_8, hash_hint=f64454fcfabff959"
  },
  {
    "matrix_row_id": "matrix_023_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 23: validator observes canonical read-only evidence and compares 5 registries against policy segment 23.",
    "bad_pattern": "bad pattern 9 in matrix 23: writer drift toward family 2, generated path reports_real/segment_23_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_23_9, boundary=bnd_matrix_23_9, switch=sw_matrix_23_9, hash_hint=5a6f074786b9f5d5"
  },
  {
    "matrix_row_id": "matrix_023_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 23: validator observes canonical read-only evidence and compares 1 registries against policy segment 23.",
    "bad_pattern": "bad pattern 10 in matrix 23: writer drift toward family 3, generated path reports_real/segment_23_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_23_10, boundary=bnd_matrix_23_10, switch=sw_matrix_23_10, hash_hint=1ca3c4aa8bb56529"
  },
  {
    "matrix_row_id": "matrix_023_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 23: validator observes canonical read-only evidence and compares 2 registries against policy segment 23.",
    "bad_pattern": "bad pattern 11 in matrix 23: writer drift toward family 4, generated path reports_real/segment_23_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_23_11, boundary=bnd_matrix_23_11, switch=sw_matrix_23_11, hash_hint=5004d51f38f58cb7"
  },
  {
    "matrix_row_id": "matrix_023_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 23: validator observes canonical read-only evidence and compares 3 registries against policy segment 23.",
    "bad_pattern": "bad pattern 12 in matrix 23: writer drift toward family 5, generated path reports_real/segment_23_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_23_12, boundary=bnd_matrix_23_12, switch=sw_matrix_23_12, hash_hint=7e478c2c115492dc"
  },
  {
    "matrix_row_id": "matrix_023_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 23: validator observes canonical read-only evidence and compares 4 registries against policy segment 23.",
    "bad_pattern": "bad pattern 13 in matrix 23: writer drift toward family 6, generated path reports_real/segment_23_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_23_13, boundary=bnd_matrix_23_13, switch=sw_matrix_23_13, hash_hint=0544011ea4dffefc"
  },
  {
    "matrix_row_id": "matrix_023_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 23: validator observes canonical read-only evidence and compares 5 registries against policy segment 23.",
    "bad_pattern": "bad pattern 14 in matrix 23: writer drift toward family 0, generated path reports_real/segment_23_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_23_14, boundary=bnd_matrix_23_14, switch=sw_matrix_23_14, hash_hint=bf1a026b929c41e4"
  },
  {
    "matrix_row_id": "matrix_023_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 23: validator observes canonical read-only evidence and compares 1 registries against policy segment 23.",
    "bad_pattern": "bad pattern 15 in matrix 23: writer drift toward family 1, generated path reports_real/segment_23_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_23_15, boundary=bnd_matrix_23_15, switch=sw_matrix_23_15, hash_hint=c1811dce20446a3f"
  },
  {
    "matrix_row_id": "matrix_023_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 23: validator observes canonical read-only evidence and compares 2 registries against policy segment 23.",
    "bad_pattern": "bad pattern 16 in matrix 23: writer drift toward family 2, generated path reports_real/segment_23_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_23_16, boundary=bnd_matrix_23_16, switch=sw_matrix_23_16, hash_hint=293d02119ca842f5"
  },
  {
    "matrix_row_id": "matrix_023_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 23: validator observes canonical read-only evidence and compares 3 registries against policy segment 23.",
    "bad_pattern": "bad pattern 17 in matrix 23: writer drift toward family 3, generated path reports_real/segment_23_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_23_17, boundary=bnd_matrix_23_17, switch=sw_matrix_23_17, hash_hint=4488ce84a530e13e"
  },
  {
    "matrix_row_id": "matrix_023_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 23: validator observes canonical read-only evidence and compares 4 registries against policy segment 23.",
    "bad_pattern": "bad pattern 18 in matrix 23: writer drift toward family 4, generated path reports_real/segment_23_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_23_18, boundary=bnd_matrix_23_18, switch=sw_matrix_23_18, hash_hint=06d15fb1e315855f"
  },
  {
    "matrix_row_id": "matrix_023_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 23: validator observes canonical read-only evidence and compares 5 registries against policy segment 23.",
    "bad_pattern": "bad pattern 19 in matrix 23: writer drift toward family 5, generated path reports_real/segment_23_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_23_19, boundary=bnd_matrix_23_19, switch=sw_matrix_23_19, hash_hint=896d4d3ca31c7cdd"
  },
  {
    "matrix_row_id": "matrix_023_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 23: validator observes canonical read-only evidence and compares 1 registries against policy segment 23.",
    "bad_pattern": "bad pattern 20 in matrix 23: writer drift toward family 6, generated path reports_real/segment_23_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_23_20, boundary=bnd_matrix_23_20, switch=sw_matrix_23_20, hash_hint=204f0f7b1bfc6c3c"
  },
  {
    "matrix_row_id": "matrix_023_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 23: validator observes canonical read-only evidence and compares 2 registries against policy segment 23.",
    "bad_pattern": "bad pattern 21 in matrix 23: writer drift toward family 0, generated path reports_real/segment_23_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_23_21, boundary=bnd_matrix_23_21, switch=sw_matrix_23_21, hash_hint=ff005433dac16607"
  },
  {
    "matrix_row_id": "matrix_023_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 23: validator observes canonical read-only evidence and compares 3 registries against policy segment 23.",
    "bad_pattern": "bad pattern 22 in matrix 23: writer drift toward family 1, generated path reports_real/segment_23_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_23_22, boundary=bnd_matrix_23_22, switch=sw_matrix_23_22, hash_hint=21f0c7c086e10f12"
  },
  {
    "matrix_row_id": "matrix_023_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 23: validator observes canonical read-only evidence and compares 4 registries against policy segment 23.",
    "bad_pattern": "bad pattern 23 in matrix 23: writer drift toward family 2, generated path reports_real/segment_23_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_23_23, boundary=bnd_matrix_23_23, switch=sw_matrix_23_23, hash_hint=840ec4c60cc49e99"
  },
  {
    "matrix_row_id": "matrix_023_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 23: validator observes canonical read-only evidence and compares 5 registries against policy segment 23.",
    "bad_pattern": "bad pattern 24 in matrix 23: writer drift toward family 3, generated path reports_real/segment_23_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_23_24, boundary=bnd_matrix_23_24, switch=sw_matrix_23_24, hash_hint=544284869324cac1"
  },
  {
    "matrix_row_id": "matrix_023_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 23: validator observes canonical read-only evidence and compares 1 registries against policy segment 23.",
    "bad_pattern": "bad pattern 25 in matrix 23: writer drift toward family 4, generated path reports_real/segment_23_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_23_25, boundary=bnd_matrix_23_25, switch=sw_matrix_23_25, hash_hint=5b7703c41f77b3cc"
  },
  {
    "matrix_row_id": "matrix_023_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 23: validator observes canonical read-only evidence and compares 2 registries against policy segment 23.",
    "bad_pattern": "bad pattern 26 in matrix 23: writer drift toward family 5, generated path reports_real/segment_23_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_23_26, boundary=bnd_matrix_23_26, switch=sw_matrix_23_26, hash_hint=96ae77f07e9d2c8c"
  },
  {
    "matrix_row_id": "matrix_023_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 23: validator observes canonical read-only evidence and compares 3 registries against policy segment 23.",
    "bad_pattern": "bad pattern 27 in matrix 23: writer drift toward family 6, generated path reports_real/segment_23_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_23_27, boundary=bnd_matrix_23_27, switch=sw_matrix_23_27, hash_hint=3e653e9d8c8ea103"
  },
  {
    "matrix_row_id": "matrix_023_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 23: validator observes canonical read-only evidence and compares 4 registries against policy segment 23.",
    "bad_pattern": "bad pattern 28 in matrix 23: writer drift toward family 0, generated path reports_real/segment_23_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_23_28, boundary=bnd_matrix_23_28, switch=sw_matrix_23_28, hash_hint=0554e772e84e8408"
  },
  {
    "matrix_row_id": "matrix_023_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 23: validator observes canonical read-only evidence and compares 5 registries against policy segment 23.",
    "bad_pattern": "bad pattern 29 in matrix 23: writer drift toward family 1, generated path reports_real/segment_23_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_23_29, boundary=bnd_matrix_23_29, switch=sw_matrix_23_29, hash_hint=137870350c0aa859"
  },
  {
    "matrix_row_id": "matrix_023_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 23: validator observes canonical read-only evidence and compares 1 registries against policy segment 23.",
    "bad_pattern": "bad pattern 30 in matrix 23: writer drift toward family 2, generated path reports_real/segment_23_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_23_30, boundary=bnd_matrix_23_30, switch=sw_matrix_23_30, hash_hint=25b10c72871664e8"
  },
  {
    "matrix_row_id": "matrix_023_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 23: validator observes canonical read-only evidence and compares 2 registries against policy segment 23.",
    "bad_pattern": "bad pattern 31 in matrix 23: writer drift toward family 3, generated path reports_real/segment_23_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_23_31, boundary=bnd_matrix_23_31, switch=sw_matrix_23_31, hash_hint=3f56635f1f7110e1"
  },
  {
    "matrix_row_id": "matrix_023_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 23: validator observes canonical read-only evidence and compares 3 registries against policy segment 23.",
    "bad_pattern": "bad pattern 32 in matrix 23: writer drift toward family 4, generated path reports_real/segment_23_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_23_32, boundary=bnd_matrix_23_32, switch=sw_matrix_23_32, hash_hint=20c4f0541f4aa83f"
  },
  {
    "matrix_row_id": "matrix_023_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 23: validator observes canonical read-only evidence and compares 4 registries against policy segment 23.",
    "bad_pattern": "bad pattern 33 in matrix 23: writer drift toward family 5, generated path reports_real/segment_23_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_23_33, boundary=bnd_matrix_23_33, switch=sw_matrix_23_33, hash_hint=c728a578fd6f89b6"
  },
  {
    "matrix_row_id": "matrix_023_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 23: validator observes canonical read-only evidence and compares 5 registries against policy segment 23.",
    "bad_pattern": "bad pattern 34 in matrix 23: writer drift toward family 6, generated path reports_real/segment_23_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_23_34, boundary=bnd_matrix_23_34, switch=sw_matrix_23_34, hash_hint=c4eef15c4a7a5c06"
  },
  {
    "matrix_row_id": "matrix_023_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 23: validator observes canonical read-only evidence and compares 1 registries against policy segment 23.",
    "bad_pattern": "bad pattern 35 in matrix 23: writer drift toward family 0, generated path reports_real/segment_23_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_23_35, boundary=bnd_matrix_23_35, switch=sw_matrix_23_35, hash_hint=cf565350bf673e72"
  },
  {
    "matrix_row_id": "matrix_023_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 23: validator observes canonical read-only evidence and compares 2 registries against policy segment 23.",
    "bad_pattern": "bad pattern 36 in matrix 23: writer drift toward family 1, generated path reports_real/segment_23_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_23_36, boundary=bnd_matrix_23_36, switch=sw_matrix_23_36, hash_hint=512da5a036cc0cc8"
  },
  {
    "matrix_row_id": "matrix_023_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 23: validator observes canonical read-only evidence and compares 3 registries against policy segment 23.",
    "bad_pattern": "bad pattern 37 in matrix 23: writer drift toward family 2, generated path reports_real/segment_23_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_23_37, boundary=bnd_matrix_23_37, switch=sw_matrix_23_37, hash_hint=8959ed52ee4bbf20"
  },
  {
    "matrix_row_id": "matrix_023_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 23: validator observes canonical read-only evidence and compares 4 registries against policy segment 23.",
    "bad_pattern": "bad pattern 38 in matrix 23: writer drift toward family 3, generated path reports_real/segment_23_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_23_38, boundary=bnd_matrix_23_38, switch=sw_matrix_23_38, hash_hint=9baeeb98329b87a7"
  },
  {
    "matrix_row_id": "matrix_023_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 23: validator observes canonical read-only evidence and compares 5 registries against policy segment 23.",
    "bad_pattern": "bad pattern 39 in matrix 23: writer drift toward family 4, generated path reports_real/segment_23_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_23_39, boundary=bnd_matrix_23_39, switch=sw_matrix_23_39, hash_hint=bddbe417db50f9cd"
  },
  {
    "matrix_row_id": "matrix_023_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 23: validator observes canonical read-only evidence and compares 1 registries against policy segment 23.",
    "bad_pattern": "bad pattern 40 in matrix 23: writer drift toward family 5, generated path reports_real/segment_23_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_23_40, boundary=bnd_matrix_23_40, switch=sw_matrix_23_40, hash_hint=182e111ac483218a"
  },
  {
    "matrix_row_id": "matrix_023_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 23: validator observes canonical read-only evidence and compares 2 registries against policy segment 23.",
    "bad_pattern": "bad pattern 41 in matrix 23: writer drift toward family 6, generated path reports_real/segment_23_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_23_41, boundary=bnd_matrix_23_41, switch=sw_matrix_23_41, hash_hint=74a5b9b233a2891a"
  },
  {
    "matrix_row_id": "matrix_023_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 23: validator observes canonical read-only evidence and compares 3 registries against policy segment 23.",
    "bad_pattern": "bad pattern 42 in matrix 23: writer drift toward family 0, generated path reports_real/segment_23_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_23_42, boundary=bnd_matrix_23_42, switch=sw_matrix_23_42, hash_hint=05e74d5b968a7a8e"
  },
  {
    "matrix_row_id": "matrix_023_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 23: validator observes canonical read-only evidence and compares 4 registries against policy segment 23.",
    "bad_pattern": "bad pattern 43 in matrix 23: writer drift toward family 1, generated path reports_real/segment_23_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_23_43, boundary=bnd_matrix_23_43, switch=sw_matrix_23_43, hash_hint=fe09ff0a7b9c4b16"
  },
  {
    "matrix_row_id": "matrix_023_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 23: validator observes canonical read-only evidence and compares 5 registries against policy segment 23.",
    "bad_pattern": "bad pattern 44 in matrix 23: writer drift toward family 2, generated path reports_real/segment_23_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_23_44, boundary=bnd_matrix_23_44, switch=sw_matrix_23_44, hash_hint=1414841c298ea12a"
  },
  {
    "matrix_row_id": "matrix_023_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 23: validator observes canonical read-only evidence and compares 1 registries against policy segment 23.",
    "bad_pattern": "bad pattern 45 in matrix 23: writer drift toward family 3, generated path reports_real/segment_23_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_23_45, boundary=bnd_matrix_23_45, switch=sw_matrix_23_45, hash_hint=0a4e21a8fe44b155"
  },
  {
    "matrix_row_id": "matrix_023_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 23: validator observes canonical read-only evidence and compares 2 registries against policy segment 23.",
    "bad_pattern": "bad pattern 46 in matrix 23: writer drift toward family 4, generated path reports_real/segment_23_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_23_46, boundary=bnd_matrix_23_46, switch=sw_matrix_23_46, hash_hint=f0684e9cec790b5d"
  },
  {
    "matrix_row_id": "matrix_023_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 23: validator observes canonical read-only evidence and compares 3 registries against policy segment 23.",
    "bad_pattern": "bad pattern 47 in matrix 23: writer drift toward family 5, generated path reports_real/segment_23_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_23_47, boundary=bnd_matrix_23_47, switch=sw_matrix_23_47, hash_hint=ec971b2303c3aa42"
  },
  {
    "matrix_row_id": "matrix_023_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 23: validator observes canonical read-only evidence and compares 4 registries against policy segment 23.",
    "bad_pattern": "bad pattern 48 in matrix 23: writer drift toward family 6, generated path reports_real/segment_23_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_23_48, boundary=bnd_matrix_23_48, switch=sw_matrix_23_48, hash_hint=604fedbefc72fb08"
  },
  {
    "matrix_row_id": "matrix_023_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 23: validator observes canonical read-only evidence and compares 5 registries against policy segment 23.",
    "bad_pattern": "bad pattern 49 in matrix 23: writer drift toward family 0, generated path reports_real/segment_23_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_23_49, boundary=bnd_matrix_23_49, switch=sw_matrix_23_49, hash_hint=a6831b24b2b866dc"
  },
  {
    "matrix_row_id": "matrix_023_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 23: validator observes canonical read-only evidence and compares 1 registries against policy segment 23.",
    "bad_pattern": "bad pattern 50 in matrix 23: writer drift toward family 1, generated path reports_real/segment_23_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_23_50, boundary=bnd_matrix_23_50, switch=sw_matrix_23_50, hash_hint=9b1b42495364041e"
  },
  {
    "matrix_row_id": "matrix_023_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 23: validator observes canonical read-only evidence and compares 2 registries against policy segment 23.",
    "bad_pattern": "bad pattern 51 in matrix 23: writer drift toward family 2, generated path reports_real/segment_23_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_23_51, boundary=bnd_matrix_23_51, switch=sw_matrix_23_51, hash_hint=950961409fe62f4e"
  },
  {
    "matrix_row_id": "matrix_023_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 23: validator observes canonical read-only evidence and compares 3 registries against policy segment 23.",
    "bad_pattern": "bad pattern 52 in matrix 23: writer drift toward family 3, generated path reports_real/segment_23_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_23_52, boundary=bnd_matrix_23_52, switch=sw_matrix_23_52, hash_hint=409f91180b2de1f6"
  },
  {
    "matrix_row_id": "matrix_023_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 23: validator observes canonical read-only evidence and compares 4 registries against policy segment 23.",
    "bad_pattern": "bad pattern 53 in matrix 23: writer drift toward family 4, generated path reports_real/segment_23_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_23_53, boundary=bnd_matrix_23_53, switch=sw_matrix_23_53, hash_hint=3e3d09dfcbc9ebba"
  },
  {
    "matrix_row_id": "matrix_023_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 23: validator observes canonical read-only evidence and compares 5 registries against policy segment 23.",
    "bad_pattern": "bad pattern 54 in matrix 23: writer drift toward family 5, generated path reports_real/segment_23_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_23_54, boundary=bnd_matrix_23_54, switch=sw_matrix_23_54, hash_hint=02b427ac96fc24d7"
  },
  {
    "matrix_row_id": "matrix_023_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 23: validator observes canonical read-only evidence and compares 1 registries against policy segment 23.",
    "bad_pattern": "bad pattern 55 in matrix 23: writer drift toward family 6, generated path reports_real/segment_23_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_23_55, boundary=bnd_matrix_23_55, switch=sw_matrix_23_55, hash_hint=0aa04e24148ac68f"
  },
  {
    "matrix_row_id": "matrix_023_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 23: validator observes canonical read-only evidence and compares 2 registries against policy segment 23.",
    "bad_pattern": "bad pattern 56 in matrix 23: writer drift toward family 0, generated path reports_real/segment_23_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_23_56, boundary=bnd_matrix_23_56, switch=sw_matrix_23_56, hash_hint=73172feec5be8b60"
  },
  {
    "matrix_row_id": "matrix_023_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 23: validator observes canonical read-only evidence and compares 3 registries against policy segment 23.",
    "bad_pattern": "bad pattern 57 in matrix 23: writer drift toward family 1, generated path reports_real/segment_23_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_23_57, boundary=bnd_matrix_23_57, switch=sw_matrix_23_57, hash_hint=88b8ed852c3f6010"
  },
  {
    "matrix_row_id": "matrix_023_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 23: validator observes canonical read-only evidence and compares 4 registries against policy segment 23.",
    "bad_pattern": "bad pattern 58 in matrix 23: writer drift toward family 2, generated path reports_real/segment_23_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_23_58, boundary=bnd_matrix_23_58, switch=sw_matrix_23_58, hash_hint=5dc808e3e3bb92c5"
  },
  {
    "matrix_row_id": "matrix_023_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 23: validator observes canonical read-only evidence and compares 5 registries against policy segment 23.",
    "bad_pattern": "bad pattern 59 in matrix 23: writer drift toward family 3, generated path reports_real/segment_23_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_23_59, boundary=bnd_matrix_23_59, switch=sw_matrix_23_59, hash_hint=f04c017cc08dabec"
  },
  {
    "matrix_row_id": "matrix_023_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 23: validator observes canonical read-only evidence and compares 1 registries against policy segment 23.",
    "bad_pattern": "bad pattern 60 in matrix 23: writer drift toward family 4, generated path reports_real/segment_23_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_23_60, boundary=bnd_matrix_23_60, switch=sw_matrix_23_60, hash_hint=a00be2745e63bc3f"
  }
]
