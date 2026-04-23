from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 28/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 28/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 28/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 28/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 28/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 28/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 28/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 28/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 28/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 28/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 28/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 28/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 28/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 28/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 28/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 28/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 28/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 28/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 28/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 28/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 28/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 28/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 28/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 28/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 28/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_028_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 28: validator observes canonical read-only evidence and compares 2 registries against policy segment 28.",
    "bad_pattern": "bad pattern 1 in matrix 28: writer drift toward family 1, generated path reports_real/segment_28_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_28_1, boundary=bnd_matrix_28_1, switch=sw_matrix_28_1, hash_hint=9c165994151aa989"
  },
  {
    "matrix_row_id": "matrix_028_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 28: validator observes canonical read-only evidence and compares 3 registries against policy segment 28.",
    "bad_pattern": "bad pattern 2 in matrix 28: writer drift toward family 2, generated path reports_real/segment_28_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_28_2, boundary=bnd_matrix_28_2, switch=sw_matrix_28_2, hash_hint=9ab24d674ff58a14"
  },
  {
    "matrix_row_id": "matrix_028_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 28: validator observes canonical read-only evidence and compares 4 registries against policy segment 28.",
    "bad_pattern": "bad pattern 3 in matrix 28: writer drift toward family 3, generated path reports_real/segment_28_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_28_3, boundary=bnd_matrix_28_3, switch=sw_matrix_28_3, hash_hint=3721763798c50e06"
  },
  {
    "matrix_row_id": "matrix_028_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 28: validator observes canonical read-only evidence and compares 5 registries against policy segment 28.",
    "bad_pattern": "bad pattern 4 in matrix 28: writer drift toward family 4, generated path reports_real/segment_28_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_28_4, boundary=bnd_matrix_28_4, switch=sw_matrix_28_4, hash_hint=23f9c062f5df6a42"
  },
  {
    "matrix_row_id": "matrix_028_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 28: validator observes canonical read-only evidence and compares 1 registries against policy segment 28.",
    "bad_pattern": "bad pattern 5 in matrix 28: writer drift toward family 5, generated path reports_real/segment_28_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_28_5, boundary=bnd_matrix_28_5, switch=sw_matrix_28_5, hash_hint=6cec28006dd0b837"
  },
  {
    "matrix_row_id": "matrix_028_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 28: validator observes canonical read-only evidence and compares 2 registries against policy segment 28.",
    "bad_pattern": "bad pattern 6 in matrix 28: writer drift toward family 6, generated path reports_real/segment_28_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_28_6, boundary=bnd_matrix_28_6, switch=sw_matrix_28_6, hash_hint=0e445ed3c8c26554"
  },
  {
    "matrix_row_id": "matrix_028_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 28: validator observes canonical read-only evidence and compares 3 registries against policy segment 28.",
    "bad_pattern": "bad pattern 7 in matrix 28: writer drift toward family 0, generated path reports_real/segment_28_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_28_7, boundary=bnd_matrix_28_7, switch=sw_matrix_28_7, hash_hint=ba797e6f5f075aee"
  },
  {
    "matrix_row_id": "matrix_028_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 28: validator observes canonical read-only evidence and compares 4 registries against policy segment 28.",
    "bad_pattern": "bad pattern 8 in matrix 28: writer drift toward family 1, generated path reports_real/segment_28_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_28_8, boundary=bnd_matrix_28_8, switch=sw_matrix_28_8, hash_hint=5a7438bc72055f5b"
  },
  {
    "matrix_row_id": "matrix_028_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 28: validator observes canonical read-only evidence and compares 5 registries against policy segment 28.",
    "bad_pattern": "bad pattern 9 in matrix 28: writer drift toward family 2, generated path reports_real/segment_28_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_28_9, boundary=bnd_matrix_28_9, switch=sw_matrix_28_9, hash_hint=f6f27f718938251c"
  },
  {
    "matrix_row_id": "matrix_028_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 28: validator observes canonical read-only evidence and compares 1 registries against policy segment 28.",
    "bad_pattern": "bad pattern 10 in matrix 28: writer drift toward family 3, generated path reports_real/segment_28_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_28_10, boundary=bnd_matrix_28_10, switch=sw_matrix_28_10, hash_hint=252ea2952d7d953d"
  },
  {
    "matrix_row_id": "matrix_028_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 28: validator observes canonical read-only evidence and compares 2 registries against policy segment 28.",
    "bad_pattern": "bad pattern 11 in matrix 28: writer drift toward family 4, generated path reports_real/segment_28_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_28_11, boundary=bnd_matrix_28_11, switch=sw_matrix_28_11, hash_hint=788b53bf2bd513ff"
  },
  {
    "matrix_row_id": "matrix_028_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 28: validator observes canonical read-only evidence and compares 3 registries against policy segment 28.",
    "bad_pattern": "bad pattern 12 in matrix 28: writer drift toward family 5, generated path reports_real/segment_28_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_28_12, boundary=bnd_matrix_28_12, switch=sw_matrix_28_12, hash_hint=8945e076dbcc3d87"
  },
  {
    "matrix_row_id": "matrix_028_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 28: validator observes canonical read-only evidence and compares 4 registries against policy segment 28.",
    "bad_pattern": "bad pattern 13 in matrix 28: writer drift toward family 6, generated path reports_real/segment_28_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_28_13, boundary=bnd_matrix_28_13, switch=sw_matrix_28_13, hash_hint=90432680fb57596c"
  },
  {
    "matrix_row_id": "matrix_028_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 28: validator observes canonical read-only evidence and compares 5 registries against policy segment 28.",
    "bad_pattern": "bad pattern 14 in matrix 28: writer drift toward family 0, generated path reports_real/segment_28_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_28_14, boundary=bnd_matrix_28_14, switch=sw_matrix_28_14, hash_hint=4214bd8cf15b94d6"
  },
  {
    "matrix_row_id": "matrix_028_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 28: validator observes canonical read-only evidence and compares 1 registries against policy segment 28.",
    "bad_pattern": "bad pattern 15 in matrix 28: writer drift toward family 1, generated path reports_real/segment_28_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_28_15, boundary=bnd_matrix_28_15, switch=sw_matrix_28_15, hash_hint=36048d3c9d0cd992"
  },
  {
    "matrix_row_id": "matrix_028_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 28: validator observes canonical read-only evidence and compares 2 registries against policy segment 28.",
    "bad_pattern": "bad pattern 16 in matrix 28: writer drift toward family 2, generated path reports_real/segment_28_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_28_16, boundary=bnd_matrix_28_16, switch=sw_matrix_28_16, hash_hint=c27ae6a2164ebca8"
  },
  {
    "matrix_row_id": "matrix_028_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 28: validator observes canonical read-only evidence and compares 3 registries against policy segment 28.",
    "bad_pattern": "bad pattern 17 in matrix 28: writer drift toward family 3, generated path reports_real/segment_28_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_28_17, boundary=bnd_matrix_28_17, switch=sw_matrix_28_17, hash_hint=2097e6f49c82cc2a"
  },
  {
    "matrix_row_id": "matrix_028_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 28: validator observes canonical read-only evidence and compares 4 registries against policy segment 28.",
    "bad_pattern": "bad pattern 18 in matrix 28: writer drift toward family 4, generated path reports_real/segment_28_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_28_18, boundary=bnd_matrix_28_18, switch=sw_matrix_28_18, hash_hint=4b0b341771c4168a"
  },
  {
    "matrix_row_id": "matrix_028_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 28: validator observes canonical read-only evidence and compares 5 registries against policy segment 28.",
    "bad_pattern": "bad pattern 19 in matrix 28: writer drift toward family 5, generated path reports_real/segment_28_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_28_19, boundary=bnd_matrix_28_19, switch=sw_matrix_28_19, hash_hint=4b7131f8e7a5918f"
  },
  {
    "matrix_row_id": "matrix_028_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 28: validator observes canonical read-only evidence and compares 1 registries against policy segment 28.",
    "bad_pattern": "bad pattern 20 in matrix 28: writer drift toward family 6, generated path reports_real/segment_28_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_28_20, boundary=bnd_matrix_28_20, switch=sw_matrix_28_20, hash_hint=5935ec6358d234f3"
  },
  {
    "matrix_row_id": "matrix_028_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 28: validator observes canonical read-only evidence and compares 2 registries against policy segment 28.",
    "bad_pattern": "bad pattern 21 in matrix 28: writer drift toward family 0, generated path reports_real/segment_28_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_28_21, boundary=bnd_matrix_28_21, switch=sw_matrix_28_21, hash_hint=a4e16b83695a1b41"
  },
  {
    "matrix_row_id": "matrix_028_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 28: validator observes canonical read-only evidence and compares 3 registries against policy segment 28.",
    "bad_pattern": "bad pattern 22 in matrix 28: writer drift toward family 1, generated path reports_real/segment_28_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_28_22, boundary=bnd_matrix_28_22, switch=sw_matrix_28_22, hash_hint=b8e383750dca8b32"
  },
  {
    "matrix_row_id": "matrix_028_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 28: validator observes canonical read-only evidence and compares 4 registries against policy segment 28.",
    "bad_pattern": "bad pattern 23 in matrix 28: writer drift toward family 2, generated path reports_real/segment_28_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_28_23, boundary=bnd_matrix_28_23, switch=sw_matrix_28_23, hash_hint=556776324fe78690"
  },
  {
    "matrix_row_id": "matrix_028_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 28: validator observes canonical read-only evidence and compares 5 registries against policy segment 28.",
    "bad_pattern": "bad pattern 24 in matrix 28: writer drift toward family 3, generated path reports_real/segment_28_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_28_24, boundary=bnd_matrix_28_24, switch=sw_matrix_28_24, hash_hint=17f144f51de60006"
  },
  {
    "matrix_row_id": "matrix_028_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 28: validator observes canonical read-only evidence and compares 1 registries against policy segment 28.",
    "bad_pattern": "bad pattern 25 in matrix 28: writer drift toward family 4, generated path reports_real/segment_28_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_28_25, boundary=bnd_matrix_28_25, switch=sw_matrix_28_25, hash_hint=94654102df8e45c5"
  },
  {
    "matrix_row_id": "matrix_028_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 28: validator observes canonical read-only evidence and compares 2 registries against policy segment 28.",
    "bad_pattern": "bad pattern 26 in matrix 28: writer drift toward family 5, generated path reports_real/segment_28_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_28_26, boundary=bnd_matrix_28_26, switch=sw_matrix_28_26, hash_hint=6fb264c546aee675"
  },
  {
    "matrix_row_id": "matrix_028_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 28: validator observes canonical read-only evidence and compares 3 registries against policy segment 28.",
    "bad_pattern": "bad pattern 27 in matrix 28: writer drift toward family 6, generated path reports_real/segment_28_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_28_27, boundary=bnd_matrix_28_27, switch=sw_matrix_28_27, hash_hint=61b516e754ede564"
  },
  {
    "matrix_row_id": "matrix_028_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 28: validator observes canonical read-only evidence and compares 4 registries against policy segment 28.",
    "bad_pattern": "bad pattern 28 in matrix 28: writer drift toward family 0, generated path reports_real/segment_28_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_28_28, boundary=bnd_matrix_28_28, switch=sw_matrix_28_28, hash_hint=13b35491decbe6a3"
  },
  {
    "matrix_row_id": "matrix_028_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 28: validator observes canonical read-only evidence and compares 5 registries against policy segment 28.",
    "bad_pattern": "bad pattern 29 in matrix 28: writer drift toward family 1, generated path reports_real/segment_28_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_28_29, boundary=bnd_matrix_28_29, switch=sw_matrix_28_29, hash_hint=05ea9837ffd9cd27"
  },
  {
    "matrix_row_id": "matrix_028_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 28: validator observes canonical read-only evidence and compares 1 registries against policy segment 28.",
    "bad_pattern": "bad pattern 30 in matrix 28: writer drift toward family 2, generated path reports_real/segment_28_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_28_30, boundary=bnd_matrix_28_30, switch=sw_matrix_28_30, hash_hint=16808b65dfc4be7a"
  },
  {
    "matrix_row_id": "matrix_028_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 28: validator observes canonical read-only evidence and compares 2 registries against policy segment 28.",
    "bad_pattern": "bad pattern 31 in matrix 28: writer drift toward family 3, generated path reports_real/segment_28_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_28_31, boundary=bnd_matrix_28_31, switch=sw_matrix_28_31, hash_hint=28c5d9d6c9deecce"
  },
  {
    "matrix_row_id": "matrix_028_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 28: validator observes canonical read-only evidence and compares 3 registries against policy segment 28.",
    "bad_pattern": "bad pattern 32 in matrix 28: writer drift toward family 4, generated path reports_real/segment_28_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_28_32, boundary=bnd_matrix_28_32, switch=sw_matrix_28_32, hash_hint=f1768b8bc9eca94c"
  },
  {
    "matrix_row_id": "matrix_028_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 28: validator observes canonical read-only evidence and compares 4 registries against policy segment 28.",
    "bad_pattern": "bad pattern 33 in matrix 28: writer drift toward family 5, generated path reports_real/segment_28_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_28_33, boundary=bnd_matrix_28_33, switch=sw_matrix_28_33, hash_hint=d19268bdb3ee85a4"
  },
  {
    "matrix_row_id": "matrix_028_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 28: validator observes canonical read-only evidence and compares 5 registries against policy segment 28.",
    "bad_pattern": "bad pattern 34 in matrix 28: writer drift toward family 6, generated path reports_real/segment_28_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_28_34, boundary=bnd_matrix_28_34, switch=sw_matrix_28_34, hash_hint=acbccbc5d06174d5"
  },
  {
    "matrix_row_id": "matrix_028_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 28: validator observes canonical read-only evidence and compares 1 registries against policy segment 28.",
    "bad_pattern": "bad pattern 35 in matrix 28: writer drift toward family 0, generated path reports_real/segment_28_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_28_35, boundary=bnd_matrix_28_35, switch=sw_matrix_28_35, hash_hint=94ff203c550c631b"
  },
  {
    "matrix_row_id": "matrix_028_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 28: validator observes canonical read-only evidence and compares 2 registries against policy segment 28.",
    "bad_pattern": "bad pattern 36 in matrix 28: writer drift toward family 1, generated path reports_real/segment_28_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_28_36, boundary=bnd_matrix_28_36, switch=sw_matrix_28_36, hash_hint=354d751d49f35d74"
  },
  {
    "matrix_row_id": "matrix_028_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 28: validator observes canonical read-only evidence and compares 3 registries against policy segment 28.",
    "bad_pattern": "bad pattern 37 in matrix 28: writer drift toward family 2, generated path reports_real/segment_28_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_28_37, boundary=bnd_matrix_28_37, switch=sw_matrix_28_37, hash_hint=70963041fd48c010"
  },
  {
    "matrix_row_id": "matrix_028_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 28: validator observes canonical read-only evidence and compares 4 registries against policy segment 28.",
    "bad_pattern": "bad pattern 38 in matrix 28: writer drift toward family 3, generated path reports_real/segment_28_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_28_38, boundary=bnd_matrix_28_38, switch=sw_matrix_28_38, hash_hint=75bc1b3ad073131f"
  },
  {
    "matrix_row_id": "matrix_028_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 28: validator observes canonical read-only evidence and compares 5 registries against policy segment 28.",
    "bad_pattern": "bad pattern 39 in matrix 28: writer drift toward family 4, generated path reports_real/segment_28_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_28_39, boundary=bnd_matrix_28_39, switch=sw_matrix_28_39, hash_hint=490ec3ed3a417659"
  },
  {
    "matrix_row_id": "matrix_028_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 28: validator observes canonical read-only evidence and compares 1 registries against policy segment 28.",
    "bad_pattern": "bad pattern 40 in matrix 28: writer drift toward family 5, generated path reports_real/segment_28_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_28_40, boundary=bnd_matrix_28_40, switch=sw_matrix_28_40, hash_hint=e075311ab3de13b6"
  },
  {
    "matrix_row_id": "matrix_028_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 28: validator observes canonical read-only evidence and compares 2 registries against policy segment 28.",
    "bad_pattern": "bad pattern 41 in matrix 28: writer drift toward family 6, generated path reports_real/segment_28_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_28_41, boundary=bnd_matrix_28_41, switch=sw_matrix_28_41, hash_hint=edcd9b3267c61864"
  },
  {
    "matrix_row_id": "matrix_028_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 28: validator observes canonical read-only evidence and compares 3 registries against policy segment 28.",
    "bad_pattern": "bad pattern 42 in matrix 28: writer drift toward family 0, generated path reports_real/segment_28_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_28_42, boundary=bnd_matrix_28_42, switch=sw_matrix_28_42, hash_hint=1e8905fc5fa77c42"
  },
  {
    "matrix_row_id": "matrix_028_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 28: validator observes canonical read-only evidence and compares 4 registries against policy segment 28.",
    "bad_pattern": "bad pattern 43 in matrix 28: writer drift toward family 1, generated path reports_real/segment_28_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_28_43, boundary=bnd_matrix_28_43, switch=sw_matrix_28_43, hash_hint=bc426c378c1076c4"
  },
  {
    "matrix_row_id": "matrix_028_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 28: validator observes canonical read-only evidence and compares 5 registries against policy segment 28.",
    "bad_pattern": "bad pattern 44 in matrix 28: writer drift toward family 2, generated path reports_real/segment_28_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_28_44, boundary=bnd_matrix_28_44, switch=sw_matrix_28_44, hash_hint=5f0c3f5d06b0fb58"
  },
  {
    "matrix_row_id": "matrix_028_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 28: validator observes canonical read-only evidence and compares 1 registries against policy segment 28.",
    "bad_pattern": "bad pattern 45 in matrix 28: writer drift toward family 3, generated path reports_real/segment_28_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_28_45, boundary=bnd_matrix_28_45, switch=sw_matrix_28_45, hash_hint=3552662dc2972d51"
  },
  {
    "matrix_row_id": "matrix_028_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 28: validator observes canonical read-only evidence and compares 2 registries against policy segment 28.",
    "bad_pattern": "bad pattern 46 in matrix 28: writer drift toward family 4, generated path reports_real/segment_28_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_28_46, boundary=bnd_matrix_28_46, switch=sw_matrix_28_46, hash_hint=5250bc3e4dea4d38"
  },
  {
    "matrix_row_id": "matrix_028_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 28: validator observes canonical read-only evidence and compares 3 registries against policy segment 28.",
    "bad_pattern": "bad pattern 47 in matrix 28: writer drift toward family 5, generated path reports_real/segment_28_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_28_47, boundary=bnd_matrix_28_47, switch=sw_matrix_28_47, hash_hint=ae251580423311bc"
  },
  {
    "matrix_row_id": "matrix_028_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 28: validator observes canonical read-only evidence and compares 4 registries against policy segment 28.",
    "bad_pattern": "bad pattern 48 in matrix 28: writer drift toward family 6, generated path reports_real/segment_28_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_28_48, boundary=bnd_matrix_28_48, switch=sw_matrix_28_48, hash_hint=8ed96a9eaa0e1647"
  },
  {
    "matrix_row_id": "matrix_028_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 28: validator observes canonical read-only evidence and compares 5 registries against policy segment 28.",
    "bad_pattern": "bad pattern 49 in matrix 28: writer drift toward family 0, generated path reports_real/segment_28_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_28_49, boundary=bnd_matrix_28_49, switch=sw_matrix_28_49, hash_hint=be71a6d1e442bf1a"
  },
  {
    "matrix_row_id": "matrix_028_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 28: validator observes canonical read-only evidence and compares 1 registries against policy segment 28.",
    "bad_pattern": "bad pattern 50 in matrix 28: writer drift toward family 1, generated path reports_real/segment_28_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_28_50, boundary=bnd_matrix_28_50, switch=sw_matrix_28_50, hash_hint=5293fba511004983"
  },
  {
    "matrix_row_id": "matrix_028_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 28: validator observes canonical read-only evidence and compares 2 registries against policy segment 28.",
    "bad_pattern": "bad pattern 51 in matrix 28: writer drift toward family 2, generated path reports_real/segment_28_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_28_51, boundary=bnd_matrix_28_51, switch=sw_matrix_28_51, hash_hint=42be281d5de6c92e"
  },
  {
    "matrix_row_id": "matrix_028_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 28: validator observes canonical read-only evidence and compares 3 registries against policy segment 28.",
    "bad_pattern": "bad pattern 52 in matrix 28: writer drift toward family 3, generated path reports_real/segment_28_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_28_52, boundary=bnd_matrix_28_52, switch=sw_matrix_28_52, hash_hint=7e18ffb520667c94"
  },
  {
    "matrix_row_id": "matrix_028_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 28: validator observes canonical read-only evidence and compares 4 registries against policy segment 28.",
    "bad_pattern": "bad pattern 53 in matrix 28: writer drift toward family 4, generated path reports_real/segment_28_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_28_53, boundary=bnd_matrix_28_53, switch=sw_matrix_28_53, hash_hint=bc99a3603e077ca4"
  },
  {
    "matrix_row_id": "matrix_028_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 28: validator observes canonical read-only evidence and compares 5 registries against policy segment 28.",
    "bad_pattern": "bad pattern 54 in matrix 28: writer drift toward family 5, generated path reports_real/segment_28_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_28_54, boundary=bnd_matrix_28_54, switch=sw_matrix_28_54, hash_hint=23f315bb89f83b03"
  },
  {
    "matrix_row_id": "matrix_028_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 28: validator observes canonical read-only evidence and compares 1 registries against policy segment 28.",
    "bad_pattern": "bad pattern 55 in matrix 28: writer drift toward family 6, generated path reports_real/segment_28_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_28_55, boundary=bnd_matrix_28_55, switch=sw_matrix_28_55, hash_hint=ba7a7d0e63d14560"
  },
  {
    "matrix_row_id": "matrix_028_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 28: validator observes canonical read-only evidence and compares 2 registries against policy segment 28.",
    "bad_pattern": "bad pattern 56 in matrix 28: writer drift toward family 0, generated path reports_real/segment_28_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_28_56, boundary=bnd_matrix_28_56, switch=sw_matrix_28_56, hash_hint=98bf1e047daa89c3"
  },
  {
    "matrix_row_id": "matrix_028_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 28: validator observes canonical read-only evidence and compares 3 registries against policy segment 28.",
    "bad_pattern": "bad pattern 57 in matrix 28: writer drift toward family 1, generated path reports_real/segment_28_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_28_57, boundary=bnd_matrix_28_57, switch=sw_matrix_28_57, hash_hint=cb1e00529173eeb5"
  },
  {
    "matrix_row_id": "matrix_028_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 28: validator observes canonical read-only evidence and compares 4 registries against policy segment 28.",
    "bad_pattern": "bad pattern 58 in matrix 28: writer drift toward family 2, generated path reports_real/segment_28_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_28_58, boundary=bnd_matrix_28_58, switch=sw_matrix_28_58, hash_hint=09d042b84f68f2bf"
  },
  {
    "matrix_row_id": "matrix_028_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 28: validator observes canonical read-only evidence and compares 5 registries against policy segment 28.",
    "bad_pattern": "bad pattern 59 in matrix 28: writer drift toward family 3, generated path reports_real/segment_28_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_28_59, boundary=bnd_matrix_28_59, switch=sw_matrix_28_59, hash_hint=5df4d4b4e440da34"
  },
  {
    "matrix_row_id": "matrix_028_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 28: validator observes canonical read-only evidence and compares 1 registries against policy segment 28.",
    "bad_pattern": "bad pattern 60 in matrix 28: writer drift toward family 4, generated path reports_real/segment_28_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_28_60, boundary=bnd_matrix_28_60, switch=sw_matrix_28_60, hash_hint=33cbd8916af8d3f8"
  }
]
