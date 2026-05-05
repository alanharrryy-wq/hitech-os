from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 15/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 15/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 15/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 15/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 15/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 15/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 15/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 15/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 15/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 15/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 15/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 15/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 15/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 15/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 15/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 15/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 15/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 15/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 15/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 15/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 15/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 15/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 15/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 15/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 15/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_015_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 15: validator observes canonical read-only evidence and compares 2 registries against policy segment 15.",
    "bad_pattern": "bad pattern 1 in matrix 15: writer drift toward family 1, generated path reports_real/segment_15_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_15_1, boundary=bnd_matrix_15_1, switch=sw_matrix_15_1, hash_hint=a89e566afb0ec10f"
  },
  {
    "matrix_row_id": "matrix_015_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 15: validator observes canonical read-only evidence and compares 3 registries against policy segment 15.",
    "bad_pattern": "bad pattern 2 in matrix 15: writer drift toward family 2, generated path reports_real/segment_15_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_15_2, boundary=bnd_matrix_15_2, switch=sw_matrix_15_2, hash_hint=71af1055a2a16f74"
  },
  {
    "matrix_row_id": "matrix_015_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 15: validator observes canonical read-only evidence and compares 4 registries against policy segment 15.",
    "bad_pattern": "bad pattern 3 in matrix 15: writer drift toward family 3, generated path reports_real/segment_15_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_15_3, boundary=bnd_matrix_15_3, switch=sw_matrix_15_3, hash_hint=2cc9f044b6b8ec99"
  },
  {
    "matrix_row_id": "matrix_015_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 15: validator observes canonical read-only evidence and compares 5 registries against policy segment 15.",
    "bad_pattern": "bad pattern 4 in matrix 15: writer drift toward family 4, generated path reports_real/segment_15_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_15_4, boundary=bnd_matrix_15_4, switch=sw_matrix_15_4, hash_hint=8ae40dec68b1a109"
  },
  {
    "matrix_row_id": "matrix_015_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 15: validator observes canonical read-only evidence and compares 1 registries against policy segment 15.",
    "bad_pattern": "bad pattern 5 in matrix 15: writer drift toward family 5, generated path reports_real/segment_15_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_15_5, boundary=bnd_matrix_15_5, switch=sw_matrix_15_5, hash_hint=9f79c494daf99888"
  },
  {
    "matrix_row_id": "matrix_015_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 15: validator observes canonical read-only evidence and compares 2 registries against policy segment 15.",
    "bad_pattern": "bad pattern 6 in matrix 15: writer drift toward family 6, generated path reports_real/segment_15_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_15_6, boundary=bnd_matrix_15_6, switch=sw_matrix_15_6, hash_hint=6eb78e9ac32c5a64"
  },
  {
    "matrix_row_id": "matrix_015_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 15: validator observes canonical read-only evidence and compares 3 registries against policy segment 15.",
    "bad_pattern": "bad pattern 7 in matrix 15: writer drift toward family 0, generated path reports_real/segment_15_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_15_7, boundary=bnd_matrix_15_7, switch=sw_matrix_15_7, hash_hint=2feaeed397cbf41c"
  },
  {
    "matrix_row_id": "matrix_015_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 15: validator observes canonical read-only evidence and compares 4 registries against policy segment 15.",
    "bad_pattern": "bad pattern 8 in matrix 15: writer drift toward family 1, generated path reports_real/segment_15_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_15_8, boundary=bnd_matrix_15_8, switch=sw_matrix_15_8, hash_hint=2d538106ca0d4a92"
  },
  {
    "matrix_row_id": "matrix_015_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 15: validator observes canonical read-only evidence and compares 5 registries against policy segment 15.",
    "bad_pattern": "bad pattern 9 in matrix 15: writer drift toward family 2, generated path reports_real/segment_15_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_15_9, boundary=bnd_matrix_15_9, switch=sw_matrix_15_9, hash_hint=44d8e7de4ef53497"
  },
  {
    "matrix_row_id": "matrix_015_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 15: validator observes canonical read-only evidence and compares 1 registries against policy segment 15.",
    "bad_pattern": "bad pattern 10 in matrix 15: writer drift toward family 3, generated path reports_real/segment_15_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_15_10, boundary=bnd_matrix_15_10, switch=sw_matrix_15_10, hash_hint=7cff2ff3057b7345"
  },
  {
    "matrix_row_id": "matrix_015_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 15: validator observes canonical read-only evidence and compares 2 registries against policy segment 15.",
    "bad_pattern": "bad pattern 11 in matrix 15: writer drift toward family 4, generated path reports_real/segment_15_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_15_11, boundary=bnd_matrix_15_11, switch=sw_matrix_15_11, hash_hint=d483a53e6c2a343d"
  },
  {
    "matrix_row_id": "matrix_015_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 15: validator observes canonical read-only evidence and compares 3 registries against policy segment 15.",
    "bad_pattern": "bad pattern 12 in matrix 15: writer drift toward family 5, generated path reports_real/segment_15_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_15_12, boundary=bnd_matrix_15_12, switch=sw_matrix_15_12, hash_hint=4bedab7930d06411"
  },
  {
    "matrix_row_id": "matrix_015_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 15: validator observes canonical read-only evidence and compares 4 registries against policy segment 15.",
    "bad_pattern": "bad pattern 13 in matrix 15: writer drift toward family 6, generated path reports_real/segment_15_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_15_13, boundary=bnd_matrix_15_13, switch=sw_matrix_15_13, hash_hint=f3b509bd2ae382bd"
  },
  {
    "matrix_row_id": "matrix_015_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 15: validator observes canonical read-only evidence and compares 5 registries against policy segment 15.",
    "bad_pattern": "bad pattern 14 in matrix 15: writer drift toward family 0, generated path reports_real/segment_15_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_15_14, boundary=bnd_matrix_15_14, switch=sw_matrix_15_14, hash_hint=d5c97d3390ebaf81"
  },
  {
    "matrix_row_id": "matrix_015_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 15: validator observes canonical read-only evidence and compares 1 registries against policy segment 15.",
    "bad_pattern": "bad pattern 15 in matrix 15: writer drift toward family 1, generated path reports_real/segment_15_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_15_15, boundary=bnd_matrix_15_15, switch=sw_matrix_15_15, hash_hint=d572cc219583e30e"
  },
  {
    "matrix_row_id": "matrix_015_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 15: validator observes canonical read-only evidence and compares 2 registries against policy segment 15.",
    "bad_pattern": "bad pattern 16 in matrix 15: writer drift toward family 2, generated path reports_real/segment_15_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_15_16, boundary=bnd_matrix_15_16, switch=sw_matrix_15_16, hash_hint=950fe8340b0d1757"
  },
  {
    "matrix_row_id": "matrix_015_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 15: validator observes canonical read-only evidence and compares 3 registries against policy segment 15.",
    "bad_pattern": "bad pattern 17 in matrix 15: writer drift toward family 3, generated path reports_real/segment_15_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_15_17, boundary=bnd_matrix_15_17, switch=sw_matrix_15_17, hash_hint=b6abe229b8438975"
  },
  {
    "matrix_row_id": "matrix_015_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 15: validator observes canonical read-only evidence and compares 4 registries against policy segment 15.",
    "bad_pattern": "bad pattern 18 in matrix 15: writer drift toward family 4, generated path reports_real/segment_15_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_15_18, boundary=bnd_matrix_15_18, switch=sw_matrix_15_18, hash_hint=526be271e640ac83"
  },
  {
    "matrix_row_id": "matrix_015_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 15: validator observes canonical read-only evidence and compares 5 registries against policy segment 15.",
    "bad_pattern": "bad pattern 19 in matrix 15: writer drift toward family 5, generated path reports_real/segment_15_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_15_19, boundary=bnd_matrix_15_19, switch=sw_matrix_15_19, hash_hint=f9332933aea71ddc"
  },
  {
    "matrix_row_id": "matrix_015_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 15: validator observes canonical read-only evidence and compares 1 registries against policy segment 15.",
    "bad_pattern": "bad pattern 20 in matrix 15: writer drift toward family 6, generated path reports_real/segment_15_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_15_20, boundary=bnd_matrix_15_20, switch=sw_matrix_15_20, hash_hint=1f474d8c2d5ac589"
  },
  {
    "matrix_row_id": "matrix_015_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 15: validator observes canonical read-only evidence and compares 2 registries against policy segment 15.",
    "bad_pattern": "bad pattern 21 in matrix 15: writer drift toward family 0, generated path reports_real/segment_15_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_15_21, boundary=bnd_matrix_15_21, switch=sw_matrix_15_21, hash_hint=9b56cdbffb75d421"
  },
  {
    "matrix_row_id": "matrix_015_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 15: validator observes canonical read-only evidence and compares 3 registries against policy segment 15.",
    "bad_pattern": "bad pattern 22 in matrix 15: writer drift toward family 1, generated path reports_real/segment_15_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_15_22, boundary=bnd_matrix_15_22, switch=sw_matrix_15_22, hash_hint=249d8e23b052f8ec"
  },
  {
    "matrix_row_id": "matrix_015_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 15: validator observes canonical read-only evidence and compares 4 registries against policy segment 15.",
    "bad_pattern": "bad pattern 23 in matrix 15: writer drift toward family 2, generated path reports_real/segment_15_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_15_23, boundary=bnd_matrix_15_23, switch=sw_matrix_15_23, hash_hint=a5e670a67e4b207a"
  },
  {
    "matrix_row_id": "matrix_015_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 15: validator observes canonical read-only evidence and compares 5 registries against policy segment 15.",
    "bad_pattern": "bad pattern 24 in matrix 15: writer drift toward family 3, generated path reports_real/segment_15_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_15_24, boundary=bnd_matrix_15_24, switch=sw_matrix_15_24, hash_hint=f36eec8935f46c50"
  },
  {
    "matrix_row_id": "matrix_015_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 15: validator observes canonical read-only evidence and compares 1 registries against policy segment 15.",
    "bad_pattern": "bad pattern 25 in matrix 15: writer drift toward family 4, generated path reports_real/segment_15_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_15_25, boundary=bnd_matrix_15_25, switch=sw_matrix_15_25, hash_hint=6f0e6ca3562ff4c0"
  },
  {
    "matrix_row_id": "matrix_015_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 15: validator observes canonical read-only evidence and compares 2 registries against policy segment 15.",
    "bad_pattern": "bad pattern 26 in matrix 15: writer drift toward family 5, generated path reports_real/segment_15_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_15_26, boundary=bnd_matrix_15_26, switch=sw_matrix_15_26, hash_hint=2dfabe11766fa0b9"
  },
  {
    "matrix_row_id": "matrix_015_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 15: validator observes canonical read-only evidence and compares 3 registries against policy segment 15.",
    "bad_pattern": "bad pattern 27 in matrix 15: writer drift toward family 6, generated path reports_real/segment_15_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_15_27, boundary=bnd_matrix_15_27, switch=sw_matrix_15_27, hash_hint=ea6cdc2f08efac90"
  },
  {
    "matrix_row_id": "matrix_015_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 15: validator observes canonical read-only evidence and compares 4 registries against policy segment 15.",
    "bad_pattern": "bad pattern 28 in matrix 15: writer drift toward family 0, generated path reports_real/segment_15_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_15_28, boundary=bnd_matrix_15_28, switch=sw_matrix_15_28, hash_hint=7063c229ab68ae08"
  },
  {
    "matrix_row_id": "matrix_015_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 15: validator observes canonical read-only evidence and compares 5 registries against policy segment 15.",
    "bad_pattern": "bad pattern 29 in matrix 15: writer drift toward family 1, generated path reports_real/segment_15_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_15_29, boundary=bnd_matrix_15_29, switch=sw_matrix_15_29, hash_hint=5fddfdec705641aa"
  },
  {
    "matrix_row_id": "matrix_015_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 15: validator observes canonical read-only evidence and compares 1 registries against policy segment 15.",
    "bad_pattern": "bad pattern 30 in matrix 15: writer drift toward family 2, generated path reports_real/segment_15_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_15_30, boundary=bnd_matrix_15_30, switch=sw_matrix_15_30, hash_hint=f8e4f1332570f589"
  },
  {
    "matrix_row_id": "matrix_015_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 15: validator observes canonical read-only evidence and compares 2 registries against policy segment 15.",
    "bad_pattern": "bad pattern 31 in matrix 15: writer drift toward family 3, generated path reports_real/segment_15_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_15_31, boundary=bnd_matrix_15_31, switch=sw_matrix_15_31, hash_hint=54185312ee8ede2a"
  },
  {
    "matrix_row_id": "matrix_015_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 15: validator observes canonical read-only evidence and compares 3 registries against policy segment 15.",
    "bad_pattern": "bad pattern 32 in matrix 15: writer drift toward family 4, generated path reports_real/segment_15_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_15_32, boundary=bnd_matrix_15_32, switch=sw_matrix_15_32, hash_hint=0a0d01909c471f7e"
  },
  {
    "matrix_row_id": "matrix_015_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 15: validator observes canonical read-only evidence and compares 4 registries against policy segment 15.",
    "bad_pattern": "bad pattern 33 in matrix 15: writer drift toward family 5, generated path reports_real/segment_15_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_15_33, boundary=bnd_matrix_15_33, switch=sw_matrix_15_33, hash_hint=d1dc8b3fd971fd06"
  },
  {
    "matrix_row_id": "matrix_015_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 15: validator observes canonical read-only evidence and compares 5 registries against policy segment 15.",
    "bad_pattern": "bad pattern 34 in matrix 15: writer drift toward family 6, generated path reports_real/segment_15_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_15_34, boundary=bnd_matrix_15_34, switch=sw_matrix_15_34, hash_hint=771a655c2f67acfd"
  },
  {
    "matrix_row_id": "matrix_015_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 15: validator observes canonical read-only evidence and compares 1 registries against policy segment 15.",
    "bad_pattern": "bad pattern 35 in matrix 15: writer drift toward family 0, generated path reports_real/segment_15_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_15_35, boundary=bnd_matrix_15_35, switch=sw_matrix_15_35, hash_hint=b5359136a62d5768"
  },
  {
    "matrix_row_id": "matrix_015_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 15: validator observes canonical read-only evidence and compares 2 registries against policy segment 15.",
    "bad_pattern": "bad pattern 36 in matrix 15: writer drift toward family 1, generated path reports_real/segment_15_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_15_36, boundary=bnd_matrix_15_36, switch=sw_matrix_15_36, hash_hint=5b256ed1909b9f1b"
  },
  {
    "matrix_row_id": "matrix_015_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 15: validator observes canonical read-only evidence and compares 3 registries against policy segment 15.",
    "bad_pattern": "bad pattern 37 in matrix 15: writer drift toward family 2, generated path reports_real/segment_15_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_15_37, boundary=bnd_matrix_15_37, switch=sw_matrix_15_37, hash_hint=aaf3ddbab6fd2d6c"
  },
  {
    "matrix_row_id": "matrix_015_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 15: validator observes canonical read-only evidence and compares 4 registries against policy segment 15.",
    "bad_pattern": "bad pattern 38 in matrix 15: writer drift toward family 3, generated path reports_real/segment_15_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_15_38, boundary=bnd_matrix_15_38, switch=sw_matrix_15_38, hash_hint=a1a59b4b5ad7e72c"
  },
  {
    "matrix_row_id": "matrix_015_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 15: validator observes canonical read-only evidence and compares 5 registries against policy segment 15.",
    "bad_pattern": "bad pattern 39 in matrix 15: writer drift toward family 4, generated path reports_real/segment_15_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_15_39, boundary=bnd_matrix_15_39, switch=sw_matrix_15_39, hash_hint=b3ab4d1fbde0e444"
  },
  {
    "matrix_row_id": "matrix_015_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 15: validator observes canonical read-only evidence and compares 1 registries against policy segment 15.",
    "bad_pattern": "bad pattern 40 in matrix 15: writer drift toward family 5, generated path reports_real/segment_15_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_15_40, boundary=bnd_matrix_15_40, switch=sw_matrix_15_40, hash_hint=144ce26a6cea9288"
  },
  {
    "matrix_row_id": "matrix_015_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 15: validator observes canonical read-only evidence and compares 2 registries against policy segment 15.",
    "bad_pattern": "bad pattern 41 in matrix 15: writer drift toward family 6, generated path reports_real/segment_15_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_15_41, boundary=bnd_matrix_15_41, switch=sw_matrix_15_41, hash_hint=711d7e775ea4ab78"
  },
  {
    "matrix_row_id": "matrix_015_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 15: validator observes canonical read-only evidence and compares 3 registries against policy segment 15.",
    "bad_pattern": "bad pattern 42 in matrix 15: writer drift toward family 0, generated path reports_real/segment_15_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_15_42, boundary=bnd_matrix_15_42, switch=sw_matrix_15_42, hash_hint=0a3569f766b37e9a"
  },
  {
    "matrix_row_id": "matrix_015_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 15: validator observes canonical read-only evidence and compares 4 registries against policy segment 15.",
    "bad_pattern": "bad pattern 43 in matrix 15: writer drift toward family 1, generated path reports_real/segment_15_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_15_43, boundary=bnd_matrix_15_43, switch=sw_matrix_15_43, hash_hint=f01242115483c47b"
  },
  {
    "matrix_row_id": "matrix_015_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 15: validator observes canonical read-only evidence and compares 5 registries against policy segment 15.",
    "bad_pattern": "bad pattern 44 in matrix 15: writer drift toward family 2, generated path reports_real/segment_15_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_15_44, boundary=bnd_matrix_15_44, switch=sw_matrix_15_44, hash_hint=22de35b9292f7857"
  },
  {
    "matrix_row_id": "matrix_015_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 15: validator observes canonical read-only evidence and compares 1 registries against policy segment 15.",
    "bad_pattern": "bad pattern 45 in matrix 15: writer drift toward family 3, generated path reports_real/segment_15_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_15_45, boundary=bnd_matrix_15_45, switch=sw_matrix_15_45, hash_hint=e2e8afa1daf55d4f"
  },
  {
    "matrix_row_id": "matrix_015_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 15: validator observes canonical read-only evidence and compares 2 registries against policy segment 15.",
    "bad_pattern": "bad pattern 46 in matrix 15: writer drift toward family 4, generated path reports_real/segment_15_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_15_46, boundary=bnd_matrix_15_46, switch=sw_matrix_15_46, hash_hint=056497af93f182f6"
  },
  {
    "matrix_row_id": "matrix_015_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 15: validator observes canonical read-only evidence and compares 3 registries against policy segment 15.",
    "bad_pattern": "bad pattern 47 in matrix 15: writer drift toward family 5, generated path reports_real/segment_15_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_15_47, boundary=bnd_matrix_15_47, switch=sw_matrix_15_47, hash_hint=48a45c8d199d1a98"
  },
  {
    "matrix_row_id": "matrix_015_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 15: validator observes canonical read-only evidence and compares 4 registries against policy segment 15.",
    "bad_pattern": "bad pattern 48 in matrix 15: writer drift toward family 6, generated path reports_real/segment_15_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_15_48, boundary=bnd_matrix_15_48, switch=sw_matrix_15_48, hash_hint=47ba6907cee85c6a"
  },
  {
    "matrix_row_id": "matrix_015_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 15: validator observes canonical read-only evidence and compares 5 registries against policy segment 15.",
    "bad_pattern": "bad pattern 49 in matrix 15: writer drift toward family 0, generated path reports_real/segment_15_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_15_49, boundary=bnd_matrix_15_49, switch=sw_matrix_15_49, hash_hint=63e083e70daec9c6"
  },
  {
    "matrix_row_id": "matrix_015_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 15: validator observes canonical read-only evidence and compares 1 registries against policy segment 15.",
    "bad_pattern": "bad pattern 50 in matrix 15: writer drift toward family 1, generated path reports_real/segment_15_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_15_50, boundary=bnd_matrix_15_50, switch=sw_matrix_15_50, hash_hint=1b1fbe9929eaa71d"
  },
  {
    "matrix_row_id": "matrix_015_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 15: validator observes canonical read-only evidence and compares 2 registries against policy segment 15.",
    "bad_pattern": "bad pattern 51 in matrix 15: writer drift toward family 2, generated path reports_real/segment_15_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_15_51, boundary=bnd_matrix_15_51, switch=sw_matrix_15_51, hash_hint=14af6633c5ef207c"
  },
  {
    "matrix_row_id": "matrix_015_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 15: validator observes canonical read-only evidence and compares 3 registries against policy segment 15.",
    "bad_pattern": "bad pattern 52 in matrix 15: writer drift toward family 3, generated path reports_real/segment_15_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_15_52, boundary=bnd_matrix_15_52, switch=sw_matrix_15_52, hash_hint=7181e28150750139"
  },
  {
    "matrix_row_id": "matrix_015_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 15: validator observes canonical read-only evidence and compares 4 registries against policy segment 15.",
    "bad_pattern": "bad pattern 53 in matrix 15: writer drift toward family 4, generated path reports_real/segment_15_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_15_53, boundary=bnd_matrix_15_53, switch=sw_matrix_15_53, hash_hint=199e03ee03f893d3"
  },
  {
    "matrix_row_id": "matrix_015_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 15: validator observes canonical read-only evidence and compares 5 registries against policy segment 15.",
    "bad_pattern": "bad pattern 54 in matrix 15: writer drift toward family 5, generated path reports_real/segment_15_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_15_54, boundary=bnd_matrix_15_54, switch=sw_matrix_15_54, hash_hint=4497f946f45849e6"
  },
  {
    "matrix_row_id": "matrix_015_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 15: validator observes canonical read-only evidence and compares 1 registries against policy segment 15.",
    "bad_pattern": "bad pattern 55 in matrix 15: writer drift toward family 6, generated path reports_real/segment_15_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_15_55, boundary=bnd_matrix_15_55, switch=sw_matrix_15_55, hash_hint=fd9a633b319ea7e1"
  },
  {
    "matrix_row_id": "matrix_015_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 15: validator observes canonical read-only evidence and compares 2 registries against policy segment 15.",
    "bad_pattern": "bad pattern 56 in matrix 15: writer drift toward family 0, generated path reports_real/segment_15_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_15_56, boundary=bnd_matrix_15_56, switch=sw_matrix_15_56, hash_hint=6a8c3d58d20cf8f6"
  },
  {
    "matrix_row_id": "matrix_015_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 15: validator observes canonical read-only evidence and compares 3 registries against policy segment 15.",
    "bad_pattern": "bad pattern 57 in matrix 15: writer drift toward family 1, generated path reports_real/segment_15_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_15_57, boundary=bnd_matrix_15_57, switch=sw_matrix_15_57, hash_hint=b77d8b01d3d121b1"
  },
  {
    "matrix_row_id": "matrix_015_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 15: validator observes canonical read-only evidence and compares 4 registries against policy segment 15.",
    "bad_pattern": "bad pattern 58 in matrix 15: writer drift toward family 2, generated path reports_real/segment_15_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_15_58, boundary=bnd_matrix_15_58, switch=sw_matrix_15_58, hash_hint=9c4b8d16fc40e1ce"
  },
  {
    "matrix_row_id": "matrix_015_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 15: validator observes canonical read-only evidence and compares 5 registries against policy segment 15.",
    "bad_pattern": "bad pattern 59 in matrix 15: writer drift toward family 3, generated path reports_real/segment_15_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_15_59, boundary=bnd_matrix_15_59, switch=sw_matrix_15_59, hash_hint=a17fe328e18648a0"
  },
  {
    "matrix_row_id": "matrix_015_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 15: validator observes canonical read-only evidence and compares 1 registries against policy segment 15.",
    "bad_pattern": "bad pattern 60 in matrix 15: writer drift toward family 4, generated path reports_real/segment_15_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_15_60, boundary=bnd_matrix_15_60, switch=sw_matrix_15_60, hash_hint=fb3c9a57f5e21bb9"
  }
]
