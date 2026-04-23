from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 1/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 1/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 1/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 1/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 1/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 1/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 1/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 1/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 1/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 1/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 1/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 1/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 1/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 1/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 1/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 1/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 1/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 1/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 1/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 1/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 1/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 1/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 1/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 1/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 1/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_001_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 1: validator observes canonical read-only evidence and compares 2 registries against policy segment 1.",
    "bad_pattern": "bad pattern 1 in matrix 1: writer drift toward family 1, generated path reports_real/segment_1_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_1_1, boundary=bnd_matrix_1_1, switch=sw_matrix_1_1, hash_hint=59510d91a04a1af4"
  },
  {
    "matrix_row_id": "matrix_001_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 1: validator observes canonical read-only evidence and compares 3 registries against policy segment 1.",
    "bad_pattern": "bad pattern 2 in matrix 1: writer drift toward family 2, generated path reports_real/segment_1_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_1_2, boundary=bnd_matrix_1_2, switch=sw_matrix_1_2, hash_hint=412a4789b02cad19"
  },
  {
    "matrix_row_id": "matrix_001_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 1: validator observes canonical read-only evidence and compares 4 registries against policy segment 1.",
    "bad_pattern": "bad pattern 3 in matrix 1: writer drift toward family 3, generated path reports_real/segment_1_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_1_3, boundary=bnd_matrix_1_3, switch=sw_matrix_1_3, hash_hint=f261d3d442c8de62"
  },
  {
    "matrix_row_id": "matrix_001_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 1: validator observes canonical read-only evidence and compares 5 registries against policy segment 1.",
    "bad_pattern": "bad pattern 4 in matrix 1: writer drift toward family 4, generated path reports_real/segment_1_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_1_4, boundary=bnd_matrix_1_4, switch=sw_matrix_1_4, hash_hint=07d3d4d89d9a4c45"
  },
  {
    "matrix_row_id": "matrix_001_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 1: validator observes canonical read-only evidence and compares 1 registries against policy segment 1.",
    "bad_pattern": "bad pattern 5 in matrix 1: writer drift toward family 5, generated path reports_real/segment_1_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_1_5, boundary=bnd_matrix_1_5, switch=sw_matrix_1_5, hash_hint=eb81b29eeb708d26"
  },
  {
    "matrix_row_id": "matrix_001_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 1: validator observes canonical read-only evidence and compares 2 registries against policy segment 1.",
    "bad_pattern": "bad pattern 6 in matrix 1: writer drift toward family 6, generated path reports_real/segment_1_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_1_6, boundary=bnd_matrix_1_6, switch=sw_matrix_1_6, hash_hint=a16dc3c3baafdebf"
  },
  {
    "matrix_row_id": "matrix_001_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 1: validator observes canonical read-only evidence and compares 3 registries against policy segment 1.",
    "bad_pattern": "bad pattern 7 in matrix 1: writer drift toward family 0, generated path reports_real/segment_1_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_1_7, boundary=bnd_matrix_1_7, switch=sw_matrix_1_7, hash_hint=3791968fee79a54b"
  },
  {
    "matrix_row_id": "matrix_001_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 1: validator observes canonical read-only evidence and compares 4 registries against policy segment 1.",
    "bad_pattern": "bad pattern 8 in matrix 1: writer drift toward family 1, generated path reports_real/segment_1_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_1_8, boundary=bnd_matrix_1_8, switch=sw_matrix_1_8, hash_hint=5e5eaaedee30d405"
  },
  {
    "matrix_row_id": "matrix_001_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 1: validator observes canonical read-only evidence and compares 5 registries against policy segment 1.",
    "bad_pattern": "bad pattern 9 in matrix 1: writer drift toward family 2, generated path reports_real/segment_1_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_1_9, boundary=bnd_matrix_1_9, switch=sw_matrix_1_9, hash_hint=18566378028a7225"
  },
  {
    "matrix_row_id": "matrix_001_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 1: validator observes canonical read-only evidence and compares 1 registries against policy segment 1.",
    "bad_pattern": "bad pattern 10 in matrix 1: writer drift toward family 3, generated path reports_real/segment_1_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_1_10, boundary=bnd_matrix_1_10, switch=sw_matrix_1_10, hash_hint=8890263da7f47fc6"
  },
  {
    "matrix_row_id": "matrix_001_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 1: validator observes canonical read-only evidence and compares 2 registries against policy segment 1.",
    "bad_pattern": "bad pattern 11 in matrix 1: writer drift toward family 4, generated path reports_real/segment_1_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_1_11, boundary=bnd_matrix_1_11, switch=sw_matrix_1_11, hash_hint=c67f9f9a1d8e65c9"
  },
  {
    "matrix_row_id": "matrix_001_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 1: validator observes canonical read-only evidence and compares 3 registries against policy segment 1.",
    "bad_pattern": "bad pattern 12 in matrix 1: writer drift toward family 5, generated path reports_real/segment_1_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_1_12, boundary=bnd_matrix_1_12, switch=sw_matrix_1_12, hash_hint=1aa38f1954c5d0be"
  },
  {
    "matrix_row_id": "matrix_001_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 1: validator observes canonical read-only evidence and compares 4 registries against policy segment 1.",
    "bad_pattern": "bad pattern 13 in matrix 1: writer drift toward family 6, generated path reports_real/segment_1_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_1_13, boundary=bnd_matrix_1_13, switch=sw_matrix_1_13, hash_hint=a59717c8acc3c9c7"
  },
  {
    "matrix_row_id": "matrix_001_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 1: validator observes canonical read-only evidence and compares 5 registries against policy segment 1.",
    "bad_pattern": "bad pattern 14 in matrix 1: writer drift toward family 0, generated path reports_real/segment_1_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_1_14, boundary=bnd_matrix_1_14, switch=sw_matrix_1_14, hash_hint=7b1f9e72175331b4"
  },
  {
    "matrix_row_id": "matrix_001_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 1: validator observes canonical read-only evidence and compares 1 registries against policy segment 1.",
    "bad_pattern": "bad pattern 15 in matrix 1: writer drift toward family 1, generated path reports_real/segment_1_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_1_15, boundary=bnd_matrix_1_15, switch=sw_matrix_1_15, hash_hint=b2017a41a3a066c8"
  },
  {
    "matrix_row_id": "matrix_001_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 1: validator observes canonical read-only evidence and compares 2 registries against policy segment 1.",
    "bad_pattern": "bad pattern 16 in matrix 1: writer drift toward family 2, generated path reports_real/segment_1_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_1_16, boundary=bnd_matrix_1_16, switch=sw_matrix_1_16, hash_hint=fc6facf81274fc32"
  },
  {
    "matrix_row_id": "matrix_001_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 1: validator observes canonical read-only evidence and compares 3 registries against policy segment 1.",
    "bad_pattern": "bad pattern 17 in matrix 1: writer drift toward family 3, generated path reports_real/segment_1_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_1_17, boundary=bnd_matrix_1_17, switch=sw_matrix_1_17, hash_hint=a65b30c5a1fdedf4"
  },
  {
    "matrix_row_id": "matrix_001_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 1: validator observes canonical read-only evidence and compares 4 registries against policy segment 1.",
    "bad_pattern": "bad pattern 18 in matrix 1: writer drift toward family 4, generated path reports_real/segment_1_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_1_18, boundary=bnd_matrix_1_18, switch=sw_matrix_1_18, hash_hint=6c3e20a0bba6d853"
  },
  {
    "matrix_row_id": "matrix_001_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 1: validator observes canonical read-only evidence and compares 5 registries against policy segment 1.",
    "bad_pattern": "bad pattern 19 in matrix 1: writer drift toward family 5, generated path reports_real/segment_1_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_1_19, boundary=bnd_matrix_1_19, switch=sw_matrix_1_19, hash_hint=8e38d62c26d4b888"
  },
  {
    "matrix_row_id": "matrix_001_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 1: validator observes canonical read-only evidence and compares 1 registries against policy segment 1.",
    "bad_pattern": "bad pattern 20 in matrix 1: writer drift toward family 6, generated path reports_real/segment_1_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_1_20, boundary=bnd_matrix_1_20, switch=sw_matrix_1_20, hash_hint=e3c3daf4c54f5bc3"
  },
  {
    "matrix_row_id": "matrix_001_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 1: validator observes canonical read-only evidence and compares 2 registries against policy segment 1.",
    "bad_pattern": "bad pattern 21 in matrix 1: writer drift toward family 0, generated path reports_real/segment_1_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_1_21, boundary=bnd_matrix_1_21, switch=sw_matrix_1_21, hash_hint=60d98dbce1d346e3"
  },
  {
    "matrix_row_id": "matrix_001_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 1: validator observes canonical read-only evidence and compares 3 registries against policy segment 1.",
    "bad_pattern": "bad pattern 22 in matrix 1: writer drift toward family 1, generated path reports_real/segment_1_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_1_22, boundary=bnd_matrix_1_22, switch=sw_matrix_1_22, hash_hint=d3c7f3d874f34fa0"
  },
  {
    "matrix_row_id": "matrix_001_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 1: validator observes canonical read-only evidence and compares 4 registries against policy segment 1.",
    "bad_pattern": "bad pattern 23 in matrix 1: writer drift toward family 2, generated path reports_real/segment_1_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_1_23, boundary=bnd_matrix_1_23, switch=sw_matrix_1_23, hash_hint=29ba6b0c81f546b8"
  },
  {
    "matrix_row_id": "matrix_001_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 1: validator observes canonical read-only evidence and compares 5 registries against policy segment 1.",
    "bad_pattern": "bad pattern 24 in matrix 1: writer drift toward family 3, generated path reports_real/segment_1_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_1_24, boundary=bnd_matrix_1_24, switch=sw_matrix_1_24, hash_hint=01b01aa5b8baefcd"
  },
  {
    "matrix_row_id": "matrix_001_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 1: validator observes canonical read-only evidence and compares 1 registries against policy segment 1.",
    "bad_pattern": "bad pattern 25 in matrix 1: writer drift toward family 4, generated path reports_real/segment_1_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_1_25, boundary=bnd_matrix_1_25, switch=sw_matrix_1_25, hash_hint=a3e79e2826cceecf"
  },
  {
    "matrix_row_id": "matrix_001_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 1: validator observes canonical read-only evidence and compares 2 registries against policy segment 1.",
    "bad_pattern": "bad pattern 26 in matrix 1: writer drift toward family 5, generated path reports_real/segment_1_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_1_26, boundary=bnd_matrix_1_26, switch=sw_matrix_1_26, hash_hint=9c04cda7c55f4b3d"
  },
  {
    "matrix_row_id": "matrix_001_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 1: validator observes canonical read-only evidence and compares 3 registries against policy segment 1.",
    "bad_pattern": "bad pattern 27 in matrix 1: writer drift toward family 6, generated path reports_real/segment_1_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_1_27, boundary=bnd_matrix_1_27, switch=sw_matrix_1_27, hash_hint=ecf3bad962e3da0c"
  },
  {
    "matrix_row_id": "matrix_001_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 1: validator observes canonical read-only evidence and compares 4 registries against policy segment 1.",
    "bad_pattern": "bad pattern 28 in matrix 1: writer drift toward family 0, generated path reports_real/segment_1_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_1_28, boundary=bnd_matrix_1_28, switch=sw_matrix_1_28, hash_hint=02f1727306e6f9c9"
  },
  {
    "matrix_row_id": "matrix_001_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 1: validator observes canonical read-only evidence and compares 5 registries against policy segment 1.",
    "bad_pattern": "bad pattern 29 in matrix 1: writer drift toward family 1, generated path reports_real/segment_1_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_1_29, boundary=bnd_matrix_1_29, switch=sw_matrix_1_29, hash_hint=1cdd73284d811ee5"
  },
  {
    "matrix_row_id": "matrix_001_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 1: validator observes canonical read-only evidence and compares 1 registries against policy segment 1.",
    "bad_pattern": "bad pattern 30 in matrix 1: writer drift toward family 2, generated path reports_real/segment_1_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_1_30, boundary=bnd_matrix_1_30, switch=sw_matrix_1_30, hash_hint=a6358d5d09fa1a14"
  },
  {
    "matrix_row_id": "matrix_001_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 1: validator observes canonical read-only evidence and compares 2 registries against policy segment 1.",
    "bad_pattern": "bad pattern 31 in matrix 1: writer drift toward family 3, generated path reports_real/segment_1_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_1_31, boundary=bnd_matrix_1_31, switch=sw_matrix_1_31, hash_hint=98e5807e4b42f9c2"
  },
  {
    "matrix_row_id": "matrix_001_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 1: validator observes canonical read-only evidence and compares 3 registries against policy segment 1.",
    "bad_pattern": "bad pattern 32 in matrix 1: writer drift toward family 4, generated path reports_real/segment_1_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_1_32, boundary=bnd_matrix_1_32, switch=sw_matrix_1_32, hash_hint=3a906fbafe2e08a5"
  },
  {
    "matrix_row_id": "matrix_001_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 1: validator observes canonical read-only evidence and compares 4 registries against policy segment 1.",
    "bad_pattern": "bad pattern 33 in matrix 1: writer drift toward family 5, generated path reports_real/segment_1_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_1_33, boundary=bnd_matrix_1_33, switch=sw_matrix_1_33, hash_hint=e9351de8b7ed3614"
  },
  {
    "matrix_row_id": "matrix_001_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 1: validator observes canonical read-only evidence and compares 5 registries against policy segment 1.",
    "bad_pattern": "bad pattern 34 in matrix 1: writer drift toward family 6, generated path reports_real/segment_1_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_1_34, boundary=bnd_matrix_1_34, switch=sw_matrix_1_34, hash_hint=5212d18ae7cfb69c"
  },
  {
    "matrix_row_id": "matrix_001_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 1: validator observes canonical read-only evidence and compares 1 registries against policy segment 1.",
    "bad_pattern": "bad pattern 35 in matrix 1: writer drift toward family 0, generated path reports_real/segment_1_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_1_35, boundary=bnd_matrix_1_35, switch=sw_matrix_1_35, hash_hint=bb10b681c0d91272"
  },
  {
    "matrix_row_id": "matrix_001_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 1: validator observes canonical read-only evidence and compares 2 registries against policy segment 1.",
    "bad_pattern": "bad pattern 36 in matrix 1: writer drift toward family 1, generated path reports_real/segment_1_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_1_36, boundary=bnd_matrix_1_36, switch=sw_matrix_1_36, hash_hint=c404b77064e7ff8b"
  },
  {
    "matrix_row_id": "matrix_001_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 1: validator observes canonical read-only evidence and compares 3 registries against policy segment 1.",
    "bad_pattern": "bad pattern 37 in matrix 1: writer drift toward family 2, generated path reports_real/segment_1_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_1_37, boundary=bnd_matrix_1_37, switch=sw_matrix_1_37, hash_hint=2a3a379f2e856df1"
  },
  {
    "matrix_row_id": "matrix_001_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 1: validator observes canonical read-only evidence and compares 4 registries against policy segment 1.",
    "bad_pattern": "bad pattern 38 in matrix 1: writer drift toward family 3, generated path reports_real/segment_1_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_1_38, boundary=bnd_matrix_1_38, switch=sw_matrix_1_38, hash_hint=516ae836a5a91519"
  },
  {
    "matrix_row_id": "matrix_001_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 1: validator observes canonical read-only evidence and compares 5 registries against policy segment 1.",
    "bad_pattern": "bad pattern 39 in matrix 1: writer drift toward family 4, generated path reports_real/segment_1_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_1_39, boundary=bnd_matrix_1_39, switch=sw_matrix_1_39, hash_hint=55bb8d9c807d5dfe"
  },
  {
    "matrix_row_id": "matrix_001_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 1: validator observes canonical read-only evidence and compares 1 registries against policy segment 1.",
    "bad_pattern": "bad pattern 40 in matrix 1: writer drift toward family 5, generated path reports_real/segment_1_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_1_40, boundary=bnd_matrix_1_40, switch=sw_matrix_1_40, hash_hint=e0bca684264c533e"
  },
  {
    "matrix_row_id": "matrix_001_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 1: validator observes canonical read-only evidence and compares 2 registries against policy segment 1.",
    "bad_pattern": "bad pattern 41 in matrix 1: writer drift toward family 6, generated path reports_real/segment_1_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_1_41, boundary=bnd_matrix_1_41, switch=sw_matrix_1_41, hash_hint=8781546c7c4b39ed"
  },
  {
    "matrix_row_id": "matrix_001_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 1: validator observes canonical read-only evidence and compares 3 registries against policy segment 1.",
    "bad_pattern": "bad pattern 42 in matrix 1: writer drift toward family 0, generated path reports_real/segment_1_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_1_42, boundary=bnd_matrix_1_42, switch=sw_matrix_1_42, hash_hint=207948f392a42e78"
  },
  {
    "matrix_row_id": "matrix_001_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 1: validator observes canonical read-only evidence and compares 4 registries against policy segment 1.",
    "bad_pattern": "bad pattern 43 in matrix 1: writer drift toward family 1, generated path reports_real/segment_1_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_1_43, boundary=bnd_matrix_1_43, switch=sw_matrix_1_43, hash_hint=0dcc26676c07e95d"
  },
  {
    "matrix_row_id": "matrix_001_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 1: validator observes canonical read-only evidence and compares 5 registries against policy segment 1.",
    "bad_pattern": "bad pattern 44 in matrix 1: writer drift toward family 2, generated path reports_real/segment_1_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_1_44, boundary=bnd_matrix_1_44, switch=sw_matrix_1_44, hash_hint=a756582742af6952"
  },
  {
    "matrix_row_id": "matrix_001_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 1: validator observes canonical read-only evidence and compares 1 registries against policy segment 1.",
    "bad_pattern": "bad pattern 45 in matrix 1: writer drift toward family 3, generated path reports_real/segment_1_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_1_45, boundary=bnd_matrix_1_45, switch=sw_matrix_1_45, hash_hint=d0dcd2552eadacc9"
  },
  {
    "matrix_row_id": "matrix_001_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 1: validator observes canonical read-only evidence and compares 2 registries against policy segment 1.",
    "bad_pattern": "bad pattern 46 in matrix 1: writer drift toward family 4, generated path reports_real/segment_1_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_1_46, boundary=bnd_matrix_1_46, switch=sw_matrix_1_46, hash_hint=c4a22b6602e111f8"
  },
  {
    "matrix_row_id": "matrix_001_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 1: validator observes canonical read-only evidence and compares 3 registries against policy segment 1.",
    "bad_pattern": "bad pattern 47 in matrix 1: writer drift toward family 5, generated path reports_real/segment_1_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_1_47, boundary=bnd_matrix_1_47, switch=sw_matrix_1_47, hash_hint=ef9b595cd7cb95c6"
  },
  {
    "matrix_row_id": "matrix_001_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 1: validator observes canonical read-only evidence and compares 4 registries against policy segment 1.",
    "bad_pattern": "bad pattern 48 in matrix 1: writer drift toward family 6, generated path reports_real/segment_1_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_1_48, boundary=bnd_matrix_1_48, switch=sw_matrix_1_48, hash_hint=94d67324f665a9c0"
  },
  {
    "matrix_row_id": "matrix_001_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 1: validator observes canonical read-only evidence and compares 5 registries against policy segment 1.",
    "bad_pattern": "bad pattern 49 in matrix 1: writer drift toward family 0, generated path reports_real/segment_1_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_1_49, boundary=bnd_matrix_1_49, switch=sw_matrix_1_49, hash_hint=a16793aa60536a57"
  },
  {
    "matrix_row_id": "matrix_001_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 1: validator observes canonical read-only evidence and compares 1 registries against policy segment 1.",
    "bad_pattern": "bad pattern 50 in matrix 1: writer drift toward family 1, generated path reports_real/segment_1_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_1_50, boundary=bnd_matrix_1_50, switch=sw_matrix_1_50, hash_hint=b5a5f370385b3f0c"
  },
  {
    "matrix_row_id": "matrix_001_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 1: validator observes canonical read-only evidence and compares 2 registries against policy segment 1.",
    "bad_pattern": "bad pattern 51 in matrix 1: writer drift toward family 2, generated path reports_real/segment_1_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_1_51, boundary=bnd_matrix_1_51, switch=sw_matrix_1_51, hash_hint=d51e6b9d7541caf0"
  },
  {
    "matrix_row_id": "matrix_001_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 1: validator observes canonical read-only evidence and compares 3 registries against policy segment 1.",
    "bad_pattern": "bad pattern 52 in matrix 1: writer drift toward family 3, generated path reports_real/segment_1_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_1_52, boundary=bnd_matrix_1_52, switch=sw_matrix_1_52, hash_hint=0814bfab0ab0799d"
  },
  {
    "matrix_row_id": "matrix_001_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 1: validator observes canonical read-only evidence and compares 4 registries against policy segment 1.",
    "bad_pattern": "bad pattern 53 in matrix 1: writer drift toward family 4, generated path reports_real/segment_1_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_1_53, boundary=bnd_matrix_1_53, switch=sw_matrix_1_53, hash_hint=c82ba629bfe9f79b"
  },
  {
    "matrix_row_id": "matrix_001_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 1: validator observes canonical read-only evidence and compares 5 registries against policy segment 1.",
    "bad_pattern": "bad pattern 54 in matrix 1: writer drift toward family 5, generated path reports_real/segment_1_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_1_54, boundary=bnd_matrix_1_54, switch=sw_matrix_1_54, hash_hint=e7f8f111fb0319c4"
  },
  {
    "matrix_row_id": "matrix_001_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 1: validator observes canonical read-only evidence and compares 1 registries against policy segment 1.",
    "bad_pattern": "bad pattern 55 in matrix 1: writer drift toward family 6, generated path reports_real/segment_1_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_1_55, boundary=bnd_matrix_1_55, switch=sw_matrix_1_55, hash_hint=69151562bdbfa1bd"
  },
  {
    "matrix_row_id": "matrix_001_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 1: validator observes canonical read-only evidence and compares 2 registries against policy segment 1.",
    "bad_pattern": "bad pattern 56 in matrix 1: writer drift toward family 0, generated path reports_real/segment_1_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_1_56, boundary=bnd_matrix_1_56, switch=sw_matrix_1_56, hash_hint=96ddb1a45fc88abf"
  },
  {
    "matrix_row_id": "matrix_001_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 1: validator observes canonical read-only evidence and compares 3 registries against policy segment 1.",
    "bad_pattern": "bad pattern 57 in matrix 1: writer drift toward family 1, generated path reports_real/segment_1_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_1_57, boundary=bnd_matrix_1_57, switch=sw_matrix_1_57, hash_hint=6fd457679c9851c2"
  },
  {
    "matrix_row_id": "matrix_001_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 1: validator observes canonical read-only evidence and compares 4 registries against policy segment 1.",
    "bad_pattern": "bad pattern 58 in matrix 1: writer drift toward family 2, generated path reports_real/segment_1_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_1_58, boundary=bnd_matrix_1_58, switch=sw_matrix_1_58, hash_hint=27deb9f0d5812e04"
  },
  {
    "matrix_row_id": "matrix_001_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 1: validator observes canonical read-only evidence and compares 5 registries against policy segment 1.",
    "bad_pattern": "bad pattern 59 in matrix 1: writer drift toward family 3, generated path reports_real/segment_1_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_1_59, boundary=bnd_matrix_1_59, switch=sw_matrix_1_59, hash_hint=e76ecc350507f3fc"
  },
  {
    "matrix_row_id": "matrix_001_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 1: validator observes canonical read-only evidence and compares 1 registries against policy segment 1.",
    "bad_pattern": "bad pattern 60 in matrix 1: writer drift toward family 4, generated path reports_real/segment_1_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_1_60, boundary=bnd_matrix_1_60, switch=sw_matrix_1_60, hash_hint=1fcda9ed89605212"
  }
]
