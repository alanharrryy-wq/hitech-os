from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 8/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 8/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 8/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 8/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 8/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 8/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 8/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 8/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 8/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 8/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 8/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 8/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 8/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 8/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 8/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 8/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 8/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 8/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 8/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 8/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 8/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 8/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 8/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 8/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 8/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_008_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 8: validator observes canonical read-only evidence and compares 2 registries against policy segment 8.",
    "bad_pattern": "bad pattern 1 in matrix 8: writer drift toward family 1, generated path reports_real/segment_8_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_8_1, boundary=bnd_matrix_8_1, switch=sw_matrix_8_1, hash_hint=cee2e005c64d7f4c"
  },
  {
    "matrix_row_id": "matrix_008_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 8: validator observes canonical read-only evidence and compares 3 registries against policy segment 8.",
    "bad_pattern": "bad pattern 2 in matrix 8: writer drift toward family 2, generated path reports_real/segment_8_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_8_2, boundary=bnd_matrix_8_2, switch=sw_matrix_8_2, hash_hint=821bdccb6a71a7eb"
  },
  {
    "matrix_row_id": "matrix_008_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 8: validator observes canonical read-only evidence and compares 4 registries against policy segment 8.",
    "bad_pattern": "bad pattern 3 in matrix 8: writer drift toward family 3, generated path reports_real/segment_8_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_8_3, boundary=bnd_matrix_8_3, switch=sw_matrix_8_3, hash_hint=e832f777d3f74f6f"
  },
  {
    "matrix_row_id": "matrix_008_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 8: validator observes canonical read-only evidence and compares 5 registries against policy segment 8.",
    "bad_pattern": "bad pattern 4 in matrix 8: writer drift toward family 4, generated path reports_real/segment_8_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_8_4, boundary=bnd_matrix_8_4, switch=sw_matrix_8_4, hash_hint=a375eb49b5a81c30"
  },
  {
    "matrix_row_id": "matrix_008_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 8: validator observes canonical read-only evidence and compares 1 registries against policy segment 8.",
    "bad_pattern": "bad pattern 5 in matrix 8: writer drift toward family 5, generated path reports_real/segment_8_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_8_5, boundary=bnd_matrix_8_5, switch=sw_matrix_8_5, hash_hint=f2d874cf2a3f7341"
  },
  {
    "matrix_row_id": "matrix_008_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 8: validator observes canonical read-only evidence and compares 2 registries against policy segment 8.",
    "bad_pattern": "bad pattern 6 in matrix 8: writer drift toward family 6, generated path reports_real/segment_8_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_8_6, boundary=bnd_matrix_8_6, switch=sw_matrix_8_6, hash_hint=fdb616d3ef2550b5"
  },
  {
    "matrix_row_id": "matrix_008_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 8: validator observes canonical read-only evidence and compares 3 registries against policy segment 8.",
    "bad_pattern": "bad pattern 7 in matrix 8: writer drift toward family 0, generated path reports_real/segment_8_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_8_7, boundary=bnd_matrix_8_7, switch=sw_matrix_8_7, hash_hint=e7cf3de0796ff1af"
  },
  {
    "matrix_row_id": "matrix_008_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 8: validator observes canonical read-only evidence and compares 4 registries against policy segment 8.",
    "bad_pattern": "bad pattern 8 in matrix 8: writer drift toward family 1, generated path reports_real/segment_8_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_8_8, boundary=bnd_matrix_8_8, switch=sw_matrix_8_8, hash_hint=3b1e20a3d4ee9911"
  },
  {
    "matrix_row_id": "matrix_008_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 8: validator observes canonical read-only evidence and compares 5 registries against policy segment 8.",
    "bad_pattern": "bad pattern 9 in matrix 8: writer drift toward family 2, generated path reports_real/segment_8_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_8_9, boundary=bnd_matrix_8_9, switch=sw_matrix_8_9, hash_hint=16c4b6b5193bba56"
  },
  {
    "matrix_row_id": "matrix_008_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 8: validator observes canonical read-only evidence and compares 1 registries against policy segment 8.",
    "bad_pattern": "bad pattern 10 in matrix 8: writer drift toward family 3, generated path reports_real/segment_8_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_8_10, boundary=bnd_matrix_8_10, switch=sw_matrix_8_10, hash_hint=5548a9c2b453add1"
  },
  {
    "matrix_row_id": "matrix_008_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 8: validator observes canonical read-only evidence and compares 2 registries against policy segment 8.",
    "bad_pattern": "bad pattern 11 in matrix 8: writer drift toward family 4, generated path reports_real/segment_8_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_8_11, boundary=bnd_matrix_8_11, switch=sw_matrix_8_11, hash_hint=fb6613e0abb2807b"
  },
  {
    "matrix_row_id": "matrix_008_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 8: validator observes canonical read-only evidence and compares 3 registries against policy segment 8.",
    "bad_pattern": "bad pattern 12 in matrix 8: writer drift toward family 5, generated path reports_real/segment_8_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_8_12, boundary=bnd_matrix_8_12, switch=sw_matrix_8_12, hash_hint=ee381ceba19db987"
  },
  {
    "matrix_row_id": "matrix_008_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 8: validator observes canonical read-only evidence and compares 4 registries against policy segment 8.",
    "bad_pattern": "bad pattern 13 in matrix 8: writer drift toward family 6, generated path reports_real/segment_8_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_8_13, boundary=bnd_matrix_8_13, switch=sw_matrix_8_13, hash_hint=cb4b2a415ad7421f"
  },
  {
    "matrix_row_id": "matrix_008_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 8: validator observes canonical read-only evidence and compares 5 registries against policy segment 8.",
    "bad_pattern": "bad pattern 14 in matrix 8: writer drift toward family 0, generated path reports_real/segment_8_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_8_14, boundary=bnd_matrix_8_14, switch=sw_matrix_8_14, hash_hint=7cad8c00d738dfbf"
  },
  {
    "matrix_row_id": "matrix_008_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 8: validator observes canonical read-only evidence and compares 1 registries against policy segment 8.",
    "bad_pattern": "bad pattern 15 in matrix 8: writer drift toward family 1, generated path reports_real/segment_8_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_8_15, boundary=bnd_matrix_8_15, switch=sw_matrix_8_15, hash_hint=3ac532bd3848ce82"
  },
  {
    "matrix_row_id": "matrix_008_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 8: validator observes canonical read-only evidence and compares 2 registries against policy segment 8.",
    "bad_pattern": "bad pattern 16 in matrix 8: writer drift toward family 2, generated path reports_real/segment_8_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_8_16, boundary=bnd_matrix_8_16, switch=sw_matrix_8_16, hash_hint=9f7504081591018f"
  },
  {
    "matrix_row_id": "matrix_008_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 8: validator observes canonical read-only evidence and compares 3 registries against policy segment 8.",
    "bad_pattern": "bad pattern 17 in matrix 8: writer drift toward family 3, generated path reports_real/segment_8_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_8_17, boundary=bnd_matrix_8_17, switch=sw_matrix_8_17, hash_hint=0f81ac7daf0de0e0"
  },
  {
    "matrix_row_id": "matrix_008_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 8: validator observes canonical read-only evidence and compares 4 registries against policy segment 8.",
    "bad_pattern": "bad pattern 18 in matrix 8: writer drift toward family 4, generated path reports_real/segment_8_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_8_18, boundary=bnd_matrix_8_18, switch=sw_matrix_8_18, hash_hint=9504806e484705cc"
  },
  {
    "matrix_row_id": "matrix_008_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 8: validator observes canonical read-only evidence and compares 5 registries against policy segment 8.",
    "bad_pattern": "bad pattern 19 in matrix 8: writer drift toward family 5, generated path reports_real/segment_8_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_8_19, boundary=bnd_matrix_8_19, switch=sw_matrix_8_19, hash_hint=497ec3d851598088"
  },
  {
    "matrix_row_id": "matrix_008_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 8: validator observes canonical read-only evidence and compares 1 registries against policy segment 8.",
    "bad_pattern": "bad pattern 20 in matrix 8: writer drift toward family 6, generated path reports_real/segment_8_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_8_20, boundary=bnd_matrix_8_20, switch=sw_matrix_8_20, hash_hint=d9a55005c19a759d"
  },
  {
    "matrix_row_id": "matrix_008_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 8: validator observes canonical read-only evidence and compares 2 registries against policy segment 8.",
    "bad_pattern": "bad pattern 21 in matrix 8: writer drift toward family 0, generated path reports_real/segment_8_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_8_21, boundary=bnd_matrix_8_21, switch=sw_matrix_8_21, hash_hint=0fb3f082c40ef073"
  },
  {
    "matrix_row_id": "matrix_008_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 8: validator observes canonical read-only evidence and compares 3 registries against policy segment 8.",
    "bad_pattern": "bad pattern 22 in matrix 8: writer drift toward family 1, generated path reports_real/segment_8_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_8_22, boundary=bnd_matrix_8_22, switch=sw_matrix_8_22, hash_hint=2c578757ae86d412"
  },
  {
    "matrix_row_id": "matrix_008_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 8: validator observes canonical read-only evidence and compares 4 registries against policy segment 8.",
    "bad_pattern": "bad pattern 23 in matrix 8: writer drift toward family 2, generated path reports_real/segment_8_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_8_23, boundary=bnd_matrix_8_23, switch=sw_matrix_8_23, hash_hint=3a1fa98cd7dace90"
  },
  {
    "matrix_row_id": "matrix_008_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 8: validator observes canonical read-only evidence and compares 5 registries against policy segment 8.",
    "bad_pattern": "bad pattern 24 in matrix 8: writer drift toward family 3, generated path reports_real/segment_8_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_8_24, boundary=bnd_matrix_8_24, switch=sw_matrix_8_24, hash_hint=ce9c35fac2619678"
  },
  {
    "matrix_row_id": "matrix_008_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 8: validator observes canonical read-only evidence and compares 1 registries against policy segment 8.",
    "bad_pattern": "bad pattern 25 in matrix 8: writer drift toward family 4, generated path reports_real/segment_8_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_8_25, boundary=bnd_matrix_8_25, switch=sw_matrix_8_25, hash_hint=aec11cefd8be9197"
  },
  {
    "matrix_row_id": "matrix_008_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 8: validator observes canonical read-only evidence and compares 2 registries against policy segment 8.",
    "bad_pattern": "bad pattern 26 in matrix 8: writer drift toward family 5, generated path reports_real/segment_8_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_8_26, boundary=bnd_matrix_8_26, switch=sw_matrix_8_26, hash_hint=5c4a7800557dfea3"
  },
  {
    "matrix_row_id": "matrix_008_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 8: validator observes canonical read-only evidence and compares 3 registries against policy segment 8.",
    "bad_pattern": "bad pattern 27 in matrix 8: writer drift toward family 6, generated path reports_real/segment_8_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_8_27, boundary=bnd_matrix_8_27, switch=sw_matrix_8_27, hash_hint=ba49a0e486767394"
  },
  {
    "matrix_row_id": "matrix_008_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 8: validator observes canonical read-only evidence and compares 4 registries against policy segment 8.",
    "bad_pattern": "bad pattern 28 in matrix 8: writer drift toward family 0, generated path reports_real/segment_8_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_8_28, boundary=bnd_matrix_8_28, switch=sw_matrix_8_28, hash_hint=f0fbaee9b0c4e3a8"
  },
  {
    "matrix_row_id": "matrix_008_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 8: validator observes canonical read-only evidence and compares 5 registries against policy segment 8.",
    "bad_pattern": "bad pattern 29 in matrix 8: writer drift toward family 1, generated path reports_real/segment_8_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_8_29, boundary=bnd_matrix_8_29, switch=sw_matrix_8_29, hash_hint=524cc5373a0e6480"
  },
  {
    "matrix_row_id": "matrix_008_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 8: validator observes canonical read-only evidence and compares 1 registries against policy segment 8.",
    "bad_pattern": "bad pattern 30 in matrix 8: writer drift toward family 2, generated path reports_real/segment_8_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_8_30, boundary=bnd_matrix_8_30, switch=sw_matrix_8_30, hash_hint=c23d988af13ef3ad"
  },
  {
    "matrix_row_id": "matrix_008_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 8: validator observes canonical read-only evidence and compares 2 registries against policy segment 8.",
    "bad_pattern": "bad pattern 31 in matrix 8: writer drift toward family 3, generated path reports_real/segment_8_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_8_31, boundary=bnd_matrix_8_31, switch=sw_matrix_8_31, hash_hint=0fb7f3f457077eab"
  },
  {
    "matrix_row_id": "matrix_008_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 8: validator observes canonical read-only evidence and compares 3 registries against policy segment 8.",
    "bad_pattern": "bad pattern 32 in matrix 8: writer drift toward family 4, generated path reports_real/segment_8_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_8_32, boundary=bnd_matrix_8_32, switch=sw_matrix_8_32, hash_hint=3c5081ef457b5baa"
  },
  {
    "matrix_row_id": "matrix_008_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 8: validator observes canonical read-only evidence and compares 4 registries against policy segment 8.",
    "bad_pattern": "bad pattern 33 in matrix 8: writer drift toward family 5, generated path reports_real/segment_8_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_8_33, boundary=bnd_matrix_8_33, switch=sw_matrix_8_33, hash_hint=53e7a6ea31f784e3"
  },
  {
    "matrix_row_id": "matrix_008_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 8: validator observes canonical read-only evidence and compares 5 registries against policy segment 8.",
    "bad_pattern": "bad pattern 34 in matrix 8: writer drift toward family 6, generated path reports_real/segment_8_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_8_34, boundary=bnd_matrix_8_34, switch=sw_matrix_8_34, hash_hint=980f4fb254e736b0"
  },
  {
    "matrix_row_id": "matrix_008_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 8: validator observes canonical read-only evidence and compares 1 registries against policy segment 8.",
    "bad_pattern": "bad pattern 35 in matrix 8: writer drift toward family 0, generated path reports_real/segment_8_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_8_35, boundary=bnd_matrix_8_35, switch=sw_matrix_8_35, hash_hint=0ac701cf6d7ac831"
  },
  {
    "matrix_row_id": "matrix_008_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 8: validator observes canonical read-only evidence and compares 2 registries against policy segment 8.",
    "bad_pattern": "bad pattern 36 in matrix 8: writer drift toward family 1, generated path reports_real/segment_8_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_8_36, boundary=bnd_matrix_8_36, switch=sw_matrix_8_36, hash_hint=84662cce822c240a"
  },
  {
    "matrix_row_id": "matrix_008_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 8: validator observes canonical read-only evidence and compares 3 registries against policy segment 8.",
    "bad_pattern": "bad pattern 37 in matrix 8: writer drift toward family 2, generated path reports_real/segment_8_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_8_37, boundary=bnd_matrix_8_37, switch=sw_matrix_8_37, hash_hint=09e986c4047cd9a5"
  },
  {
    "matrix_row_id": "matrix_008_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 8: validator observes canonical read-only evidence and compares 4 registries against policy segment 8.",
    "bad_pattern": "bad pattern 38 in matrix 8: writer drift toward family 3, generated path reports_real/segment_8_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_8_38, boundary=bnd_matrix_8_38, switch=sw_matrix_8_38, hash_hint=644fafcb42031aab"
  },
  {
    "matrix_row_id": "matrix_008_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 8: validator observes canonical read-only evidence and compares 5 registries against policy segment 8.",
    "bad_pattern": "bad pattern 39 in matrix 8: writer drift toward family 4, generated path reports_real/segment_8_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_8_39, boundary=bnd_matrix_8_39, switch=sw_matrix_8_39, hash_hint=7b4bfe2daace7e85"
  },
  {
    "matrix_row_id": "matrix_008_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 8: validator observes canonical read-only evidence and compares 1 registries against policy segment 8.",
    "bad_pattern": "bad pattern 40 in matrix 8: writer drift toward family 5, generated path reports_real/segment_8_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_8_40, boundary=bnd_matrix_8_40, switch=sw_matrix_8_40, hash_hint=4478b162f6f30ea6"
  },
  {
    "matrix_row_id": "matrix_008_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 8: validator observes canonical read-only evidence and compares 2 registries against policy segment 8.",
    "bad_pattern": "bad pattern 41 in matrix 8: writer drift toward family 6, generated path reports_real/segment_8_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_8_41, boundary=bnd_matrix_8_41, switch=sw_matrix_8_41, hash_hint=d9aca46868183175"
  },
  {
    "matrix_row_id": "matrix_008_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 8: validator observes canonical read-only evidence and compares 3 registries against policy segment 8.",
    "bad_pattern": "bad pattern 42 in matrix 8: writer drift toward family 0, generated path reports_real/segment_8_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_8_42, boundary=bnd_matrix_8_42, switch=sw_matrix_8_42, hash_hint=d0af88cd482bfcc4"
  },
  {
    "matrix_row_id": "matrix_008_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 8: validator observes canonical read-only evidence and compares 4 registries against policy segment 8.",
    "bad_pattern": "bad pattern 43 in matrix 8: writer drift toward family 1, generated path reports_real/segment_8_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_8_43, boundary=bnd_matrix_8_43, switch=sw_matrix_8_43, hash_hint=f16c0e941f1ab383"
  },
  {
    "matrix_row_id": "matrix_008_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 8: validator observes canonical read-only evidence and compares 5 registries against policy segment 8.",
    "bad_pattern": "bad pattern 44 in matrix 8: writer drift toward family 2, generated path reports_real/segment_8_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_8_44, boundary=bnd_matrix_8_44, switch=sw_matrix_8_44, hash_hint=88d0dfed13c6cde6"
  },
  {
    "matrix_row_id": "matrix_008_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 8: validator observes canonical read-only evidence and compares 1 registries against policy segment 8.",
    "bad_pattern": "bad pattern 45 in matrix 8: writer drift toward family 3, generated path reports_real/segment_8_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_8_45, boundary=bnd_matrix_8_45, switch=sw_matrix_8_45, hash_hint=17a8304a869fd4f8"
  },
  {
    "matrix_row_id": "matrix_008_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 8: validator observes canonical read-only evidence and compares 2 registries against policy segment 8.",
    "bad_pattern": "bad pattern 46 in matrix 8: writer drift toward family 4, generated path reports_real/segment_8_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_8_46, boundary=bnd_matrix_8_46, switch=sw_matrix_8_46, hash_hint=b590d10c34f38ed2"
  },
  {
    "matrix_row_id": "matrix_008_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 8: validator observes canonical read-only evidence and compares 3 registries against policy segment 8.",
    "bad_pattern": "bad pattern 47 in matrix 8: writer drift toward family 5, generated path reports_real/segment_8_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_8_47, boundary=bnd_matrix_8_47, switch=sw_matrix_8_47, hash_hint=17821e41f526cc92"
  },
  {
    "matrix_row_id": "matrix_008_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 8: validator observes canonical read-only evidence and compares 4 registries against policy segment 8.",
    "bad_pattern": "bad pattern 48 in matrix 8: writer drift toward family 6, generated path reports_real/segment_8_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_8_48, boundary=bnd_matrix_8_48, switch=sw_matrix_8_48, hash_hint=ab5d982732954413"
  },
  {
    "matrix_row_id": "matrix_008_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 8: validator observes canonical read-only evidence and compares 5 registries against policy segment 8.",
    "bad_pattern": "bad pattern 49 in matrix 8: writer drift toward family 0, generated path reports_real/segment_8_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_8_49, boundary=bnd_matrix_8_49, switch=sw_matrix_8_49, hash_hint=ba7e01d0b6e444f9"
  },
  {
    "matrix_row_id": "matrix_008_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 8: validator observes canonical read-only evidence and compares 1 registries against policy segment 8.",
    "bad_pattern": "bad pattern 50 in matrix 8: writer drift toward family 1, generated path reports_real/segment_8_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_8_50, boundary=bnd_matrix_8_50, switch=sw_matrix_8_50, hash_hint=3db1d9b9ae6036dc"
  },
  {
    "matrix_row_id": "matrix_008_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 8: validator observes canonical read-only evidence and compares 2 registries against policy segment 8.",
    "bad_pattern": "bad pattern 51 in matrix 8: writer drift toward family 2, generated path reports_real/segment_8_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_8_51, boundary=bnd_matrix_8_51, switch=sw_matrix_8_51, hash_hint=a3a57eb798aadb3c"
  },
  {
    "matrix_row_id": "matrix_008_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 8: validator observes canonical read-only evidence and compares 3 registries against policy segment 8.",
    "bad_pattern": "bad pattern 52 in matrix 8: writer drift toward family 3, generated path reports_real/segment_8_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_8_52, boundary=bnd_matrix_8_52, switch=sw_matrix_8_52, hash_hint=166726c5f282b0e3"
  },
  {
    "matrix_row_id": "matrix_008_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 8: validator observes canonical read-only evidence and compares 4 registries against policy segment 8.",
    "bad_pattern": "bad pattern 53 in matrix 8: writer drift toward family 4, generated path reports_real/segment_8_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_8_53, boundary=bnd_matrix_8_53, switch=sw_matrix_8_53, hash_hint=858340b215a2c9ff"
  },
  {
    "matrix_row_id": "matrix_008_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 8: validator observes canonical read-only evidence and compares 5 registries against policy segment 8.",
    "bad_pattern": "bad pattern 54 in matrix 8: writer drift toward family 5, generated path reports_real/segment_8_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_8_54, boundary=bnd_matrix_8_54, switch=sw_matrix_8_54, hash_hint=a072a47d48f67c13"
  },
  {
    "matrix_row_id": "matrix_008_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 8: validator observes canonical read-only evidence and compares 1 registries against policy segment 8.",
    "bad_pattern": "bad pattern 55 in matrix 8: writer drift toward family 6, generated path reports_real/segment_8_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_8_55, boundary=bnd_matrix_8_55, switch=sw_matrix_8_55, hash_hint=d6d8ceb9686c37c4"
  },
  {
    "matrix_row_id": "matrix_008_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 8: validator observes canonical read-only evidence and compares 2 registries against policy segment 8.",
    "bad_pattern": "bad pattern 56 in matrix 8: writer drift toward family 0, generated path reports_real/segment_8_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_8_56, boundary=bnd_matrix_8_56, switch=sw_matrix_8_56, hash_hint=eb007a0ae946abf7"
  },
  {
    "matrix_row_id": "matrix_008_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 8: validator observes canonical read-only evidence and compares 3 registries against policy segment 8.",
    "bad_pattern": "bad pattern 57 in matrix 8: writer drift toward family 1, generated path reports_real/segment_8_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_8_57, boundary=bnd_matrix_8_57, switch=sw_matrix_8_57, hash_hint=bed9d0cd9a729da0"
  },
  {
    "matrix_row_id": "matrix_008_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 8: validator observes canonical read-only evidence and compares 4 registries against policy segment 8.",
    "bad_pattern": "bad pattern 58 in matrix 8: writer drift toward family 2, generated path reports_real/segment_8_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_8_58, boundary=bnd_matrix_8_58, switch=sw_matrix_8_58, hash_hint=42a0c1bcb7875a6d"
  },
  {
    "matrix_row_id": "matrix_008_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 8: validator observes canonical read-only evidence and compares 5 registries against policy segment 8.",
    "bad_pattern": "bad pattern 59 in matrix 8: writer drift toward family 3, generated path reports_real/segment_8_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_8_59, boundary=bnd_matrix_8_59, switch=sw_matrix_8_59, hash_hint=c22f74ab4cf683f8"
  },
  {
    "matrix_row_id": "matrix_008_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 8: validator observes canonical read-only evidence and compares 1 registries against policy segment 8.",
    "bad_pattern": "bad pattern 60 in matrix 8: writer drift toward family 4, generated path reports_real/segment_8_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_8_60, boundary=bnd_matrix_8_60, switch=sw_matrix_8_60, hash_hint=c23b3591243ed719"
  }
]
