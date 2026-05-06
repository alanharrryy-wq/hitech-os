from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 12/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 12/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 12/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 12/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 12/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 12/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 12/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 12/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 12/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 12/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 12/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 12/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 12/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 12/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 12/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 12/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 12/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 12/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 12/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 12/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 12/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 12/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 12/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 12/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 12/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_012_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 12: validator observes canonical read-only evidence and compares 2 registries against policy segment 12.",
    "bad_pattern": "bad pattern 1 in matrix 12: writer drift toward family 1, generated path reports_real/segment_12_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_12_1, boundary=bnd_matrix_12_1, switch=sw_matrix_12_1, hash_hint=c9240e4858c51d1c"
  },
  {
    "matrix_row_id": "matrix_012_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 12: validator observes canonical read-only evidence and compares 3 registries against policy segment 12.",
    "bad_pattern": "bad pattern 2 in matrix 12: writer drift toward family 2, generated path reports_real/segment_12_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_12_2, boundary=bnd_matrix_12_2, switch=sw_matrix_12_2, hash_hint=c449b56c6ccbdcc9"
  },
  {
    "matrix_row_id": "matrix_012_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 12: validator observes canonical read-only evidence and compares 4 registries against policy segment 12.",
    "bad_pattern": "bad pattern 3 in matrix 12: writer drift toward family 3, generated path reports_real/segment_12_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_12_3, boundary=bnd_matrix_12_3, switch=sw_matrix_12_3, hash_hint=2c3312d02b2563e5"
  },
  {
    "matrix_row_id": "matrix_012_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 12: validator observes canonical read-only evidence and compares 5 registries against policy segment 12.",
    "bad_pattern": "bad pattern 4 in matrix 12: writer drift toward family 4, generated path reports_real/segment_12_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_12_4, boundary=bnd_matrix_12_4, switch=sw_matrix_12_4, hash_hint=ac4ab222d9ca1971"
  },
  {
    "matrix_row_id": "matrix_012_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 12: validator observes canonical read-only evidence and compares 1 registries against policy segment 12.",
    "bad_pattern": "bad pattern 5 in matrix 12: writer drift toward family 5, generated path reports_real/segment_12_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_12_5, boundary=bnd_matrix_12_5, switch=sw_matrix_12_5, hash_hint=0066dc03ac4aa334"
  },
  {
    "matrix_row_id": "matrix_012_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 12: validator observes canonical read-only evidence and compares 2 registries against policy segment 12.",
    "bad_pattern": "bad pattern 6 in matrix 12: writer drift toward family 6, generated path reports_real/segment_12_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_12_6, boundary=bnd_matrix_12_6, switch=sw_matrix_12_6, hash_hint=b9013067727c5309"
  },
  {
    "matrix_row_id": "matrix_012_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 12: validator observes canonical read-only evidence and compares 3 registries against policy segment 12.",
    "bad_pattern": "bad pattern 7 in matrix 12: writer drift toward family 0, generated path reports_real/segment_12_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_12_7, boundary=bnd_matrix_12_7, switch=sw_matrix_12_7, hash_hint=ba281cee47422936"
  },
  {
    "matrix_row_id": "matrix_012_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 12: validator observes canonical read-only evidence and compares 4 registries against policy segment 12.",
    "bad_pattern": "bad pattern 8 in matrix 12: writer drift toward family 1, generated path reports_real/segment_12_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_12_8, boundary=bnd_matrix_12_8, switch=sw_matrix_12_8, hash_hint=60c7fc15305143cc"
  },
  {
    "matrix_row_id": "matrix_012_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 12: validator observes canonical read-only evidence and compares 5 registries against policy segment 12.",
    "bad_pattern": "bad pattern 9 in matrix 12: writer drift toward family 2, generated path reports_real/segment_12_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_12_9, boundary=bnd_matrix_12_9, switch=sw_matrix_12_9, hash_hint=b101bb6e2eea32f0"
  },
  {
    "matrix_row_id": "matrix_012_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 12: validator observes canonical read-only evidence and compares 1 registries against policy segment 12.",
    "bad_pattern": "bad pattern 10 in matrix 12: writer drift toward family 3, generated path reports_real/segment_12_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_12_10, boundary=bnd_matrix_12_10, switch=sw_matrix_12_10, hash_hint=14206fd92db86c10"
  },
  {
    "matrix_row_id": "matrix_012_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 12: validator observes canonical read-only evidence and compares 2 registries against policy segment 12.",
    "bad_pattern": "bad pattern 11 in matrix 12: writer drift toward family 4, generated path reports_real/segment_12_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_12_11, boundary=bnd_matrix_12_11, switch=sw_matrix_12_11, hash_hint=822d827f25f463f1"
  },
  {
    "matrix_row_id": "matrix_012_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 12: validator observes canonical read-only evidence and compares 3 registries against policy segment 12.",
    "bad_pattern": "bad pattern 12 in matrix 12: writer drift toward family 5, generated path reports_real/segment_12_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_12_12, boundary=bnd_matrix_12_12, switch=sw_matrix_12_12, hash_hint=62c5f8ac87e64502"
  },
  {
    "matrix_row_id": "matrix_012_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 12: validator observes canonical read-only evidence and compares 4 registries against policy segment 12.",
    "bad_pattern": "bad pattern 13 in matrix 12: writer drift toward family 6, generated path reports_real/segment_12_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_12_13, boundary=bnd_matrix_12_13, switch=sw_matrix_12_13, hash_hint=01e00f616f0cfdf5"
  },
  {
    "matrix_row_id": "matrix_012_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 12: validator observes canonical read-only evidence and compares 5 registries against policy segment 12.",
    "bad_pattern": "bad pattern 14 in matrix 12: writer drift toward family 0, generated path reports_real/segment_12_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_12_14, boundary=bnd_matrix_12_14, switch=sw_matrix_12_14, hash_hint=f11f16d9782fdebe"
  },
  {
    "matrix_row_id": "matrix_012_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 12: validator observes canonical read-only evidence and compares 1 registries against policy segment 12.",
    "bad_pattern": "bad pattern 15 in matrix 12: writer drift toward family 1, generated path reports_real/segment_12_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_12_15, boundary=bnd_matrix_12_15, switch=sw_matrix_12_15, hash_hint=0bc65b800531b3d3"
  },
  {
    "matrix_row_id": "matrix_012_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 12: validator observes canonical read-only evidence and compares 2 registries against policy segment 12.",
    "bad_pattern": "bad pattern 16 in matrix 12: writer drift toward family 2, generated path reports_real/segment_12_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_12_16, boundary=bnd_matrix_12_16, switch=sw_matrix_12_16, hash_hint=6a3367fa286399c7"
  },
  {
    "matrix_row_id": "matrix_012_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 12: validator observes canonical read-only evidence and compares 3 registries against policy segment 12.",
    "bad_pattern": "bad pattern 17 in matrix 12: writer drift toward family 3, generated path reports_real/segment_12_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_12_17, boundary=bnd_matrix_12_17, switch=sw_matrix_12_17, hash_hint=78b75d539de0261b"
  },
  {
    "matrix_row_id": "matrix_012_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 12: validator observes canonical read-only evidence and compares 4 registries against policy segment 12.",
    "bad_pattern": "bad pattern 18 in matrix 12: writer drift toward family 4, generated path reports_real/segment_12_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_12_18, boundary=bnd_matrix_12_18, switch=sw_matrix_12_18, hash_hint=16d5eb5c5ed35912"
  },
  {
    "matrix_row_id": "matrix_012_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 12: validator observes canonical read-only evidence and compares 5 registries against policy segment 12.",
    "bad_pattern": "bad pattern 19 in matrix 12: writer drift toward family 5, generated path reports_real/segment_12_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_12_19, boundary=bnd_matrix_12_19, switch=sw_matrix_12_19, hash_hint=12f56830e3c13375"
  },
  {
    "matrix_row_id": "matrix_012_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 12: validator observes canonical read-only evidence and compares 1 registries against policy segment 12.",
    "bad_pattern": "bad pattern 20 in matrix 12: writer drift toward family 6, generated path reports_real/segment_12_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_12_20, boundary=bnd_matrix_12_20, switch=sw_matrix_12_20, hash_hint=4a10f7e3da71410a"
  },
  {
    "matrix_row_id": "matrix_012_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 12: validator observes canonical read-only evidence and compares 2 registries against policy segment 12.",
    "bad_pattern": "bad pattern 21 in matrix 12: writer drift toward family 0, generated path reports_real/segment_12_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_12_21, boundary=bnd_matrix_12_21, switch=sw_matrix_12_21, hash_hint=f5588823b56bc235"
  },
  {
    "matrix_row_id": "matrix_012_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 12: validator observes canonical read-only evidence and compares 3 registries against policy segment 12.",
    "bad_pattern": "bad pattern 22 in matrix 12: writer drift toward family 1, generated path reports_real/segment_12_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_12_22, boundary=bnd_matrix_12_22, switch=sw_matrix_12_22, hash_hint=e324e3cf11a74afe"
  },
  {
    "matrix_row_id": "matrix_012_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 12: validator observes canonical read-only evidence and compares 4 registries against policy segment 12.",
    "bad_pattern": "bad pattern 23 in matrix 12: writer drift toward family 2, generated path reports_real/segment_12_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_12_23, boundary=bnd_matrix_12_23, switch=sw_matrix_12_23, hash_hint=0c54361fbd41c795"
  },
  {
    "matrix_row_id": "matrix_012_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 12: validator observes canonical read-only evidence and compares 5 registries against policy segment 12.",
    "bad_pattern": "bad pattern 24 in matrix 12: writer drift toward family 3, generated path reports_real/segment_12_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_12_24, boundary=bnd_matrix_12_24, switch=sw_matrix_12_24, hash_hint=e1282b811ac24dbe"
  },
  {
    "matrix_row_id": "matrix_012_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 12: validator observes canonical read-only evidence and compares 1 registries against policy segment 12.",
    "bad_pattern": "bad pattern 25 in matrix 12: writer drift toward family 4, generated path reports_real/segment_12_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_12_25, boundary=bnd_matrix_12_25, switch=sw_matrix_12_25, hash_hint=5da4db82f8690762"
  },
  {
    "matrix_row_id": "matrix_012_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 12: validator observes canonical read-only evidence and compares 2 registries against policy segment 12.",
    "bad_pattern": "bad pattern 26 in matrix 12: writer drift toward family 5, generated path reports_real/segment_12_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_12_26, boundary=bnd_matrix_12_26, switch=sw_matrix_12_26, hash_hint=886348675a7eabab"
  },
  {
    "matrix_row_id": "matrix_012_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 12: validator observes canonical read-only evidence and compares 3 registries against policy segment 12.",
    "bad_pattern": "bad pattern 27 in matrix 12: writer drift toward family 6, generated path reports_real/segment_12_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_12_27, boundary=bnd_matrix_12_27, switch=sw_matrix_12_27, hash_hint=e2a33ffcdbb1f456"
  },
  {
    "matrix_row_id": "matrix_012_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 12: validator observes canonical read-only evidence and compares 4 registries against policy segment 12.",
    "bad_pattern": "bad pattern 28 in matrix 12: writer drift toward family 0, generated path reports_real/segment_12_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_12_28, boundary=bnd_matrix_12_28, switch=sw_matrix_12_28, hash_hint=2cc53cee4865f192"
  },
  {
    "matrix_row_id": "matrix_012_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 12: validator observes canonical read-only evidence and compares 5 registries against policy segment 12.",
    "bad_pattern": "bad pattern 29 in matrix 12: writer drift toward family 1, generated path reports_real/segment_12_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_12_29, boundary=bnd_matrix_12_29, switch=sw_matrix_12_29, hash_hint=280c169aab31fd94"
  },
  {
    "matrix_row_id": "matrix_012_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 12: validator observes canonical read-only evidence and compares 1 registries against policy segment 12.",
    "bad_pattern": "bad pattern 30 in matrix 12: writer drift toward family 2, generated path reports_real/segment_12_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_12_30, boundary=bnd_matrix_12_30, switch=sw_matrix_12_30, hash_hint=5aba0fca46ab1269"
  },
  {
    "matrix_row_id": "matrix_012_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 12: validator observes canonical read-only evidence and compares 2 registries against policy segment 12.",
    "bad_pattern": "bad pattern 31 in matrix 12: writer drift toward family 3, generated path reports_real/segment_12_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_12_31, boundary=bnd_matrix_12_31, switch=sw_matrix_12_31, hash_hint=abb4110155097846"
  },
  {
    "matrix_row_id": "matrix_012_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 12: validator observes canonical read-only evidence and compares 3 registries against policy segment 12.",
    "bad_pattern": "bad pattern 32 in matrix 12: writer drift toward family 4, generated path reports_real/segment_12_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_12_32, boundary=bnd_matrix_12_32, switch=sw_matrix_12_32, hash_hint=684138dc1a5c43ec"
  },
  {
    "matrix_row_id": "matrix_012_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 12: validator observes canonical read-only evidence and compares 4 registries against policy segment 12.",
    "bad_pattern": "bad pattern 33 in matrix 12: writer drift toward family 5, generated path reports_real/segment_12_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_12_33, boundary=bnd_matrix_12_33, switch=sw_matrix_12_33, hash_hint=7e720f2ea7637e62"
  },
  {
    "matrix_row_id": "matrix_012_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 12: validator observes canonical read-only evidence and compares 5 registries against policy segment 12.",
    "bad_pattern": "bad pattern 34 in matrix 12: writer drift toward family 6, generated path reports_real/segment_12_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_12_34, boundary=bnd_matrix_12_34, switch=sw_matrix_12_34, hash_hint=c269008f16b28d6f"
  },
  {
    "matrix_row_id": "matrix_012_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 12: validator observes canonical read-only evidence and compares 1 registries against policy segment 12.",
    "bad_pattern": "bad pattern 35 in matrix 12: writer drift toward family 0, generated path reports_real/segment_12_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_12_35, boundary=bnd_matrix_12_35, switch=sw_matrix_12_35, hash_hint=96dcc073fc9b1600"
  },
  {
    "matrix_row_id": "matrix_012_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 12: validator observes canonical read-only evidence and compares 2 registries against policy segment 12.",
    "bad_pattern": "bad pattern 36 in matrix 12: writer drift toward family 1, generated path reports_real/segment_12_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_12_36, boundary=bnd_matrix_12_36, switch=sw_matrix_12_36, hash_hint=1443fd21b7d52cc5"
  },
  {
    "matrix_row_id": "matrix_012_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 12: validator observes canonical read-only evidence and compares 3 registries against policy segment 12.",
    "bad_pattern": "bad pattern 37 in matrix 12: writer drift toward family 2, generated path reports_real/segment_12_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_12_37, boundary=bnd_matrix_12_37, switch=sw_matrix_12_37, hash_hint=8c774cc81a5b104a"
  },
  {
    "matrix_row_id": "matrix_012_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 12: validator observes canonical read-only evidence and compares 4 registries against policy segment 12.",
    "bad_pattern": "bad pattern 38 in matrix 12: writer drift toward family 3, generated path reports_real/segment_12_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_12_38, boundary=bnd_matrix_12_38, switch=sw_matrix_12_38, hash_hint=f301e3d19172b060"
  },
  {
    "matrix_row_id": "matrix_012_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 12: validator observes canonical read-only evidence and compares 5 registries against policy segment 12.",
    "bad_pattern": "bad pattern 39 in matrix 12: writer drift toward family 4, generated path reports_real/segment_12_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_12_39, boundary=bnd_matrix_12_39, switch=sw_matrix_12_39, hash_hint=ac36d2f728034a9c"
  },
  {
    "matrix_row_id": "matrix_012_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 12: validator observes canonical read-only evidence and compares 1 registries against policy segment 12.",
    "bad_pattern": "bad pattern 40 in matrix 12: writer drift toward family 5, generated path reports_real/segment_12_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_12_40, boundary=bnd_matrix_12_40, switch=sw_matrix_12_40, hash_hint=ac88ef84aabbb233"
  },
  {
    "matrix_row_id": "matrix_012_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 12: validator observes canonical read-only evidence and compares 2 registries against policy segment 12.",
    "bad_pattern": "bad pattern 41 in matrix 12: writer drift toward family 6, generated path reports_real/segment_12_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_12_41, boundary=bnd_matrix_12_41, switch=sw_matrix_12_41, hash_hint=d3cf1718476d800a"
  },
  {
    "matrix_row_id": "matrix_012_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 12: validator observes canonical read-only evidence and compares 3 registries against policy segment 12.",
    "bad_pattern": "bad pattern 42 in matrix 12: writer drift toward family 0, generated path reports_real/segment_12_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_12_42, boundary=bnd_matrix_12_42, switch=sw_matrix_12_42, hash_hint=5553dcdd2036c7fd"
  },
  {
    "matrix_row_id": "matrix_012_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 12: validator observes canonical read-only evidence and compares 4 registries against policy segment 12.",
    "bad_pattern": "bad pattern 43 in matrix 12: writer drift toward family 1, generated path reports_real/segment_12_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_12_43, boundary=bnd_matrix_12_43, switch=sw_matrix_12_43, hash_hint=4b58e54d87f8586f"
  },
  {
    "matrix_row_id": "matrix_012_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 12: validator observes canonical read-only evidence and compares 5 registries against policy segment 12.",
    "bad_pattern": "bad pattern 44 in matrix 12: writer drift toward family 2, generated path reports_real/segment_12_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_12_44, boundary=bnd_matrix_12_44, switch=sw_matrix_12_44, hash_hint=0e1250d52febe99d"
  },
  {
    "matrix_row_id": "matrix_012_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 12: validator observes canonical read-only evidence and compares 1 registries against policy segment 12.",
    "bad_pattern": "bad pattern 45 in matrix 12: writer drift toward family 3, generated path reports_real/segment_12_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_12_45, boundary=bnd_matrix_12_45, switch=sw_matrix_12_45, hash_hint=be74a4db1b6d90f2"
  },
  {
    "matrix_row_id": "matrix_012_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 12: validator observes canonical read-only evidence and compares 2 registries against policy segment 12.",
    "bad_pattern": "bad pattern 46 in matrix 12: writer drift toward family 4, generated path reports_real/segment_12_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_12_46, boundary=bnd_matrix_12_46, switch=sw_matrix_12_46, hash_hint=228884a17174f5ee"
  },
  {
    "matrix_row_id": "matrix_012_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 12: validator observes canonical read-only evidence and compares 3 registries against policy segment 12.",
    "bad_pattern": "bad pattern 47 in matrix 12: writer drift toward family 5, generated path reports_real/segment_12_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_12_47, boundary=bnd_matrix_12_47, switch=sw_matrix_12_47, hash_hint=a57d07c5a40819f6"
  },
  {
    "matrix_row_id": "matrix_012_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 12: validator observes canonical read-only evidence and compares 4 registries against policy segment 12.",
    "bad_pattern": "bad pattern 48 in matrix 12: writer drift toward family 6, generated path reports_real/segment_12_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_12_48, boundary=bnd_matrix_12_48, switch=sw_matrix_12_48, hash_hint=14cdf073ae466b78"
  },
  {
    "matrix_row_id": "matrix_012_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 12: validator observes canonical read-only evidence and compares 5 registries against policy segment 12.",
    "bad_pattern": "bad pattern 49 in matrix 12: writer drift toward family 0, generated path reports_real/segment_12_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_12_49, boundary=bnd_matrix_12_49, switch=sw_matrix_12_49, hash_hint=760836e85fc21033"
  },
  {
    "matrix_row_id": "matrix_012_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 12: validator observes canonical read-only evidence and compares 1 registries against policy segment 12.",
    "bad_pattern": "bad pattern 50 in matrix 12: writer drift toward family 1, generated path reports_real/segment_12_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_12_50, boundary=bnd_matrix_12_50, switch=sw_matrix_12_50, hash_hint=498da1831d3500f6"
  },
  {
    "matrix_row_id": "matrix_012_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 12: validator observes canonical read-only evidence and compares 2 registries against policy segment 12.",
    "bad_pattern": "bad pattern 51 in matrix 12: writer drift toward family 2, generated path reports_real/segment_12_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_12_51, boundary=bnd_matrix_12_51, switch=sw_matrix_12_51, hash_hint=01118bc46594144c"
  },
  {
    "matrix_row_id": "matrix_012_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 12: validator observes canonical read-only evidence and compares 3 registries against policy segment 12.",
    "bad_pattern": "bad pattern 52 in matrix 12: writer drift toward family 3, generated path reports_real/segment_12_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_12_52, boundary=bnd_matrix_12_52, switch=sw_matrix_12_52, hash_hint=602b0a64404c26f9"
  },
  {
    "matrix_row_id": "matrix_012_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 12: validator observes canonical read-only evidence and compares 4 registries against policy segment 12.",
    "bad_pattern": "bad pattern 53 in matrix 12: writer drift toward family 4, generated path reports_real/segment_12_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_12_53, boundary=bnd_matrix_12_53, switch=sw_matrix_12_53, hash_hint=c8eb8b43f60a9437"
  },
  {
    "matrix_row_id": "matrix_012_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 12: validator observes canonical read-only evidence and compares 5 registries against policy segment 12.",
    "bad_pattern": "bad pattern 54 in matrix 12: writer drift toward family 5, generated path reports_real/segment_12_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_12_54, boundary=bnd_matrix_12_54, switch=sw_matrix_12_54, hash_hint=6a8b3a20bce9b846"
  },
  {
    "matrix_row_id": "matrix_012_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 12: validator observes canonical read-only evidence and compares 1 registries against policy segment 12.",
    "bad_pattern": "bad pattern 55 in matrix 12: writer drift toward family 6, generated path reports_real/segment_12_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_12_55, boundary=bnd_matrix_12_55, switch=sw_matrix_12_55, hash_hint=17c19518b9b1dbcc"
  },
  {
    "matrix_row_id": "matrix_012_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 12: validator observes canonical read-only evidence and compares 2 registries against policy segment 12.",
    "bad_pattern": "bad pattern 56 in matrix 12: writer drift toward family 0, generated path reports_real/segment_12_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_12_56, boundary=bnd_matrix_12_56, switch=sw_matrix_12_56, hash_hint=8a3725632b025e00"
  },
  {
    "matrix_row_id": "matrix_012_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 12: validator observes canonical read-only evidence and compares 3 registries against policy segment 12.",
    "bad_pattern": "bad pattern 57 in matrix 12: writer drift toward family 1, generated path reports_real/segment_12_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_12_57, boundary=bnd_matrix_12_57, switch=sw_matrix_12_57, hash_hint=251c58f1652a7317"
  },
  {
    "matrix_row_id": "matrix_012_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 12: validator observes canonical read-only evidence and compares 4 registries against policy segment 12.",
    "bad_pattern": "bad pattern 58 in matrix 12: writer drift toward family 2, generated path reports_real/segment_12_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_12_58, boundary=bnd_matrix_12_58, switch=sw_matrix_12_58, hash_hint=c0f8624a23461318"
  },
  {
    "matrix_row_id": "matrix_012_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 12: validator observes canonical read-only evidence and compares 5 registries against policy segment 12.",
    "bad_pattern": "bad pattern 59 in matrix 12: writer drift toward family 3, generated path reports_real/segment_12_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_12_59, boundary=bnd_matrix_12_59, switch=sw_matrix_12_59, hash_hint=fc97d521c5c342ea"
  },
  {
    "matrix_row_id": "matrix_012_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 12: validator observes canonical read-only evidence and compares 1 registries against policy segment 12.",
    "bad_pattern": "bad pattern 60 in matrix 12: writer drift toward family 4, generated path reports_real/segment_12_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_12_60, boundary=bnd_matrix_12_60, switch=sw_matrix_12_60, hash_hint=e838706c31aea398"
  }
]
