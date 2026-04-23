from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 14/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 14/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 14/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 14/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 14/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 14/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 14/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 14/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 14/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 14/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 14/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 14/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 14/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 14/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 14/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 14/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 14/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 14/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 14/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 14/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 14/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 14/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 14/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 14/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 14/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_014_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 14: validator observes canonical read-only evidence and compares 2 registries against policy segment 14.",
    "bad_pattern": "bad pattern 1 in matrix 14: writer drift toward family 1, generated path reports_real/segment_14_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_14_1, boundary=bnd_matrix_14_1, switch=sw_matrix_14_1, hash_hint=108049760e4b0cdf"
  },
  {
    "matrix_row_id": "matrix_014_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 14: validator observes canonical read-only evidence and compares 3 registries against policy segment 14.",
    "bad_pattern": "bad pattern 2 in matrix 14: writer drift toward family 2, generated path reports_real/segment_14_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_14_2, boundary=bnd_matrix_14_2, switch=sw_matrix_14_2, hash_hint=2eaf76153e4886cf"
  },
  {
    "matrix_row_id": "matrix_014_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 14: validator observes canonical read-only evidence and compares 4 registries against policy segment 14.",
    "bad_pattern": "bad pattern 3 in matrix 14: writer drift toward family 3, generated path reports_real/segment_14_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_14_3, boundary=bnd_matrix_14_3, switch=sw_matrix_14_3, hash_hint=504f46992c39541e"
  },
  {
    "matrix_row_id": "matrix_014_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 14: validator observes canonical read-only evidence and compares 5 registries against policy segment 14.",
    "bad_pattern": "bad pattern 4 in matrix 14: writer drift toward family 4, generated path reports_real/segment_14_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_14_4, boundary=bnd_matrix_14_4, switch=sw_matrix_14_4, hash_hint=ab4b85d34e2828f6"
  },
  {
    "matrix_row_id": "matrix_014_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 14: validator observes canonical read-only evidence and compares 1 registries against policy segment 14.",
    "bad_pattern": "bad pattern 5 in matrix 14: writer drift toward family 5, generated path reports_real/segment_14_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_14_5, boundary=bnd_matrix_14_5, switch=sw_matrix_14_5, hash_hint=a2059022e2b213c7"
  },
  {
    "matrix_row_id": "matrix_014_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 14: validator observes canonical read-only evidence and compares 2 registries against policy segment 14.",
    "bad_pattern": "bad pattern 6 in matrix 14: writer drift toward family 6, generated path reports_real/segment_14_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_14_6, boundary=bnd_matrix_14_6, switch=sw_matrix_14_6, hash_hint=861acd8d70099dcf"
  },
  {
    "matrix_row_id": "matrix_014_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 14: validator observes canonical read-only evidence and compares 3 registries against policy segment 14.",
    "bad_pattern": "bad pattern 7 in matrix 14: writer drift toward family 0, generated path reports_real/segment_14_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_14_7, boundary=bnd_matrix_14_7, switch=sw_matrix_14_7, hash_hint=9dce1464156c906d"
  },
  {
    "matrix_row_id": "matrix_014_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 14: validator observes canonical read-only evidence and compares 4 registries against policy segment 14.",
    "bad_pattern": "bad pattern 8 in matrix 14: writer drift toward family 1, generated path reports_real/segment_14_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_14_8, boundary=bnd_matrix_14_8, switch=sw_matrix_14_8, hash_hint=a41530a133824b2c"
  },
  {
    "matrix_row_id": "matrix_014_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 14: validator observes canonical read-only evidence and compares 5 registries against policy segment 14.",
    "bad_pattern": "bad pattern 9 in matrix 14: writer drift toward family 2, generated path reports_real/segment_14_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_14_9, boundary=bnd_matrix_14_9, switch=sw_matrix_14_9, hash_hint=da7de8dcf5c776c5"
  },
  {
    "matrix_row_id": "matrix_014_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 14: validator observes canonical read-only evidence and compares 1 registries against policy segment 14.",
    "bad_pattern": "bad pattern 10 in matrix 14: writer drift toward family 3, generated path reports_real/segment_14_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_14_10, boundary=bnd_matrix_14_10, switch=sw_matrix_14_10, hash_hint=a47666027926faa6"
  },
  {
    "matrix_row_id": "matrix_014_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 14: validator observes canonical read-only evidence and compares 2 registries against policy segment 14.",
    "bad_pattern": "bad pattern 11 in matrix 14: writer drift toward family 4, generated path reports_real/segment_14_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_14_11, boundary=bnd_matrix_14_11, switch=sw_matrix_14_11, hash_hint=4cc5fe37aad69ff6"
  },
  {
    "matrix_row_id": "matrix_014_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 14: validator observes canonical read-only evidence and compares 3 registries against policy segment 14.",
    "bad_pattern": "bad pattern 12 in matrix 14: writer drift toward family 5, generated path reports_real/segment_14_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_14_12, boundary=bnd_matrix_14_12, switch=sw_matrix_14_12, hash_hint=ff0324ccf4cad5a1"
  },
  {
    "matrix_row_id": "matrix_014_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 14: validator observes canonical read-only evidence and compares 4 registries against policy segment 14.",
    "bad_pattern": "bad pattern 13 in matrix 14: writer drift toward family 6, generated path reports_real/segment_14_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_14_13, boundary=bnd_matrix_14_13, switch=sw_matrix_14_13, hash_hint=0e704c11c5acaa0b"
  },
  {
    "matrix_row_id": "matrix_014_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 14: validator observes canonical read-only evidence and compares 5 registries against policy segment 14.",
    "bad_pattern": "bad pattern 14 in matrix 14: writer drift toward family 0, generated path reports_real/segment_14_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_14_14, boundary=bnd_matrix_14_14, switch=sw_matrix_14_14, hash_hint=f88a97eca22e5950"
  },
  {
    "matrix_row_id": "matrix_014_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 14: validator observes canonical read-only evidence and compares 1 registries against policy segment 14.",
    "bad_pattern": "bad pattern 15 in matrix 14: writer drift toward family 1, generated path reports_real/segment_14_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_14_15, boundary=bnd_matrix_14_15, switch=sw_matrix_14_15, hash_hint=c4c6e655fc2bcb4d"
  },
  {
    "matrix_row_id": "matrix_014_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 14: validator observes canonical read-only evidence and compares 2 registries against policy segment 14.",
    "bad_pattern": "bad pattern 16 in matrix 14: writer drift toward family 2, generated path reports_real/segment_14_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_14_16, boundary=bnd_matrix_14_16, switch=sw_matrix_14_16, hash_hint=88c3343adef521d7"
  },
  {
    "matrix_row_id": "matrix_014_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 14: validator observes canonical read-only evidence and compares 3 registries against policy segment 14.",
    "bad_pattern": "bad pattern 17 in matrix 14: writer drift toward family 3, generated path reports_real/segment_14_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_14_17, boundary=bnd_matrix_14_17, switch=sw_matrix_14_17, hash_hint=bf4dc444a644290a"
  },
  {
    "matrix_row_id": "matrix_014_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 14: validator observes canonical read-only evidence and compares 4 registries against policy segment 14.",
    "bad_pattern": "bad pattern 18 in matrix 14: writer drift toward family 4, generated path reports_real/segment_14_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_14_18, boundary=bnd_matrix_14_18, switch=sw_matrix_14_18, hash_hint=23a0166a2e29dc50"
  },
  {
    "matrix_row_id": "matrix_014_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 14: validator observes canonical read-only evidence and compares 5 registries against policy segment 14.",
    "bad_pattern": "bad pattern 19 in matrix 14: writer drift toward family 5, generated path reports_real/segment_14_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_14_19, boundary=bnd_matrix_14_19, switch=sw_matrix_14_19, hash_hint=e3509d10b3cfe93b"
  },
  {
    "matrix_row_id": "matrix_014_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 14: validator observes canonical read-only evidence and compares 1 registries against policy segment 14.",
    "bad_pattern": "bad pattern 20 in matrix 14: writer drift toward family 6, generated path reports_real/segment_14_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_14_20, boundary=bnd_matrix_14_20, switch=sw_matrix_14_20, hash_hint=733fae0f5cc54b43"
  },
  {
    "matrix_row_id": "matrix_014_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 14: validator observes canonical read-only evidence and compares 2 registries against policy segment 14.",
    "bad_pattern": "bad pattern 21 in matrix 14: writer drift toward family 0, generated path reports_real/segment_14_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_14_21, boundary=bnd_matrix_14_21, switch=sw_matrix_14_21, hash_hint=7cdfb6b32c4c012a"
  },
  {
    "matrix_row_id": "matrix_014_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 14: validator observes canonical read-only evidence and compares 3 registries against policy segment 14.",
    "bad_pattern": "bad pattern 22 in matrix 14: writer drift toward family 1, generated path reports_real/segment_14_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_14_22, boundary=bnd_matrix_14_22, switch=sw_matrix_14_22, hash_hint=4b52c5f0b4d86da5"
  },
  {
    "matrix_row_id": "matrix_014_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 14: validator observes canonical read-only evidence and compares 4 registries against policy segment 14.",
    "bad_pattern": "bad pattern 23 in matrix 14: writer drift toward family 2, generated path reports_real/segment_14_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_14_23, boundary=bnd_matrix_14_23, switch=sw_matrix_14_23, hash_hint=8ed872da4708039c"
  },
  {
    "matrix_row_id": "matrix_014_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 14: validator observes canonical read-only evidence and compares 5 registries against policy segment 14.",
    "bad_pattern": "bad pattern 24 in matrix 14: writer drift toward family 3, generated path reports_real/segment_14_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_14_24, boundary=bnd_matrix_14_24, switch=sw_matrix_14_24, hash_hint=408e8396745019f1"
  },
  {
    "matrix_row_id": "matrix_014_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 14: validator observes canonical read-only evidence and compares 1 registries against policy segment 14.",
    "bad_pattern": "bad pattern 25 in matrix 14: writer drift toward family 4, generated path reports_real/segment_14_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_14_25, boundary=bnd_matrix_14_25, switch=sw_matrix_14_25, hash_hint=0afc4bdbf7b66e3c"
  },
  {
    "matrix_row_id": "matrix_014_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 14: validator observes canonical read-only evidence and compares 2 registries against policy segment 14.",
    "bad_pattern": "bad pattern 26 in matrix 14: writer drift toward family 5, generated path reports_real/segment_14_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_14_26, boundary=bnd_matrix_14_26, switch=sw_matrix_14_26, hash_hint=4199bcd31564cf6f"
  },
  {
    "matrix_row_id": "matrix_014_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 14: validator observes canonical read-only evidence and compares 3 registries against policy segment 14.",
    "bad_pattern": "bad pattern 27 in matrix 14: writer drift toward family 6, generated path reports_real/segment_14_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_14_27, boundary=bnd_matrix_14_27, switch=sw_matrix_14_27, hash_hint=1482cdcdcb156910"
  },
  {
    "matrix_row_id": "matrix_014_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 14: validator observes canonical read-only evidence and compares 4 registries against policy segment 14.",
    "bad_pattern": "bad pattern 28 in matrix 14: writer drift toward family 0, generated path reports_real/segment_14_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_14_28, boundary=bnd_matrix_14_28, switch=sw_matrix_14_28, hash_hint=d78dbf81f5a46eb5"
  },
  {
    "matrix_row_id": "matrix_014_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 14: validator observes canonical read-only evidence and compares 5 registries against policy segment 14.",
    "bad_pattern": "bad pattern 29 in matrix 14: writer drift toward family 1, generated path reports_real/segment_14_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_14_29, boundary=bnd_matrix_14_29, switch=sw_matrix_14_29, hash_hint=023f652f5045889b"
  },
  {
    "matrix_row_id": "matrix_014_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 14: validator observes canonical read-only evidence and compares 1 registries against policy segment 14.",
    "bad_pattern": "bad pattern 30 in matrix 14: writer drift toward family 2, generated path reports_real/segment_14_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_14_30, boundary=bnd_matrix_14_30, switch=sw_matrix_14_30, hash_hint=e7ecf4173ef8ecdf"
  },
  {
    "matrix_row_id": "matrix_014_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 14: validator observes canonical read-only evidence and compares 2 registries against policy segment 14.",
    "bad_pattern": "bad pattern 31 in matrix 14: writer drift toward family 3, generated path reports_real/segment_14_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_14_31, boundary=bnd_matrix_14_31, switch=sw_matrix_14_31, hash_hint=fe0270894de08a4d"
  },
  {
    "matrix_row_id": "matrix_014_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 14: validator observes canonical read-only evidence and compares 3 registries against policy segment 14.",
    "bad_pattern": "bad pattern 32 in matrix 14: writer drift toward family 4, generated path reports_real/segment_14_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_14_32, boundary=bnd_matrix_14_32, switch=sw_matrix_14_32, hash_hint=65b9381fed3db25b"
  },
  {
    "matrix_row_id": "matrix_014_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 14: validator observes canonical read-only evidence and compares 4 registries against policy segment 14.",
    "bad_pattern": "bad pattern 33 in matrix 14: writer drift toward family 5, generated path reports_real/segment_14_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_14_33, boundary=bnd_matrix_14_33, switch=sw_matrix_14_33, hash_hint=ae040d83a4769c81"
  },
  {
    "matrix_row_id": "matrix_014_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 14: validator observes canonical read-only evidence and compares 5 registries against policy segment 14.",
    "bad_pattern": "bad pattern 34 in matrix 14: writer drift toward family 6, generated path reports_real/segment_14_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_14_34, boundary=bnd_matrix_14_34, switch=sw_matrix_14_34, hash_hint=398ace81f607492f"
  },
  {
    "matrix_row_id": "matrix_014_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 14: validator observes canonical read-only evidence and compares 1 registries against policy segment 14.",
    "bad_pattern": "bad pattern 35 in matrix 14: writer drift toward family 0, generated path reports_real/segment_14_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_14_35, boundary=bnd_matrix_14_35, switch=sw_matrix_14_35, hash_hint=8d5a2203f4e1fb8b"
  },
  {
    "matrix_row_id": "matrix_014_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 14: validator observes canonical read-only evidence and compares 2 registries against policy segment 14.",
    "bad_pattern": "bad pattern 36 in matrix 14: writer drift toward family 1, generated path reports_real/segment_14_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_14_36, boundary=bnd_matrix_14_36, switch=sw_matrix_14_36, hash_hint=5ceb6197a808bcd0"
  },
  {
    "matrix_row_id": "matrix_014_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 14: validator observes canonical read-only evidence and compares 3 registries against policy segment 14.",
    "bad_pattern": "bad pattern 37 in matrix 14: writer drift toward family 2, generated path reports_real/segment_14_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_14_37, boundary=bnd_matrix_14_37, switch=sw_matrix_14_37, hash_hint=9f1ce1294ccef8c7"
  },
  {
    "matrix_row_id": "matrix_014_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 14: validator observes canonical read-only evidence and compares 4 registries against policy segment 14.",
    "bad_pattern": "bad pattern 38 in matrix 14: writer drift toward family 3, generated path reports_real/segment_14_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_14_38, boundary=bnd_matrix_14_38, switch=sw_matrix_14_38, hash_hint=2af4ac382efd4459"
  },
  {
    "matrix_row_id": "matrix_014_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 14: validator observes canonical read-only evidence and compares 5 registries against policy segment 14.",
    "bad_pattern": "bad pattern 39 in matrix 14: writer drift toward family 4, generated path reports_real/segment_14_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_14_39, boundary=bnd_matrix_14_39, switch=sw_matrix_14_39, hash_hint=0ac21b27c3ddef36"
  },
  {
    "matrix_row_id": "matrix_014_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 14: validator observes canonical read-only evidence and compares 1 registries against policy segment 14.",
    "bad_pattern": "bad pattern 40 in matrix 14: writer drift toward family 5, generated path reports_real/segment_14_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_14_40, boundary=bnd_matrix_14_40, switch=sw_matrix_14_40, hash_hint=bdca47c52be7e695"
  },
  {
    "matrix_row_id": "matrix_014_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 14: validator observes canonical read-only evidence and compares 2 registries against policy segment 14.",
    "bad_pattern": "bad pattern 41 in matrix 14: writer drift toward family 6, generated path reports_real/segment_14_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_14_41, boundary=bnd_matrix_14_41, switch=sw_matrix_14_41, hash_hint=bb38835618d6a7a3"
  },
  {
    "matrix_row_id": "matrix_014_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 14: validator observes canonical read-only evidence and compares 3 registries against policy segment 14.",
    "bad_pattern": "bad pattern 42 in matrix 14: writer drift toward family 0, generated path reports_real/segment_14_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_14_42, boundary=bnd_matrix_14_42, switch=sw_matrix_14_42, hash_hint=5e833cb393234442"
  },
  {
    "matrix_row_id": "matrix_014_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 14: validator observes canonical read-only evidence and compares 4 registries against policy segment 14.",
    "bad_pattern": "bad pattern 43 in matrix 14: writer drift toward family 1, generated path reports_real/segment_14_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_14_43, boundary=bnd_matrix_14_43, switch=sw_matrix_14_43, hash_hint=0d981340ba0edd6f"
  },
  {
    "matrix_row_id": "matrix_014_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 14: validator observes canonical read-only evidence and compares 5 registries against policy segment 14.",
    "bad_pattern": "bad pattern 44 in matrix 14: writer drift toward family 2, generated path reports_real/segment_14_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_14_44, boundary=bnd_matrix_14_44, switch=sw_matrix_14_44, hash_hint=ef61dbeec1d1d4e1"
  },
  {
    "matrix_row_id": "matrix_014_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 14: validator observes canonical read-only evidence and compares 1 registries against policy segment 14.",
    "bad_pattern": "bad pattern 45 in matrix 14: writer drift toward family 3, generated path reports_real/segment_14_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_14_45, boundary=bnd_matrix_14_45, switch=sw_matrix_14_45, hash_hint=29db0cc8e2819a17"
  },
  {
    "matrix_row_id": "matrix_014_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 14: validator observes canonical read-only evidence and compares 2 registries against policy segment 14.",
    "bad_pattern": "bad pattern 46 in matrix 14: writer drift toward family 4, generated path reports_real/segment_14_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_14_46, boundary=bnd_matrix_14_46, switch=sw_matrix_14_46, hash_hint=c2bed7f205f08ff6"
  },
  {
    "matrix_row_id": "matrix_014_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 14: validator observes canonical read-only evidence and compares 3 registries against policy segment 14.",
    "bad_pattern": "bad pattern 47 in matrix 14: writer drift toward family 5, generated path reports_real/segment_14_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_14_47, boundary=bnd_matrix_14_47, switch=sw_matrix_14_47, hash_hint=11bc0329bcdd64d6"
  },
  {
    "matrix_row_id": "matrix_014_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 14: validator observes canonical read-only evidence and compares 4 registries against policy segment 14.",
    "bad_pattern": "bad pattern 48 in matrix 14: writer drift toward family 6, generated path reports_real/segment_14_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_14_48, boundary=bnd_matrix_14_48, switch=sw_matrix_14_48, hash_hint=f758a19becd1f6ab"
  },
  {
    "matrix_row_id": "matrix_014_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 14: validator observes canonical read-only evidence and compares 5 registries against policy segment 14.",
    "bad_pattern": "bad pattern 49 in matrix 14: writer drift toward family 0, generated path reports_real/segment_14_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_14_49, boundary=bnd_matrix_14_49, switch=sw_matrix_14_49, hash_hint=6af2318292a59fa7"
  },
  {
    "matrix_row_id": "matrix_014_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 14: validator observes canonical read-only evidence and compares 1 registries against policy segment 14.",
    "bad_pattern": "bad pattern 50 in matrix 14: writer drift toward family 1, generated path reports_real/segment_14_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_14_50, boundary=bnd_matrix_14_50, switch=sw_matrix_14_50, hash_hint=46ac2f0ad8c397e4"
  },
  {
    "matrix_row_id": "matrix_014_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 14: validator observes canonical read-only evidence and compares 2 registries against policy segment 14.",
    "bad_pattern": "bad pattern 51 in matrix 14: writer drift toward family 2, generated path reports_real/segment_14_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_14_51, boundary=bnd_matrix_14_51, switch=sw_matrix_14_51, hash_hint=acc938ae38aff350"
  },
  {
    "matrix_row_id": "matrix_014_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 14: validator observes canonical read-only evidence and compares 3 registries against policy segment 14.",
    "bad_pattern": "bad pattern 52 in matrix 14: writer drift toward family 3, generated path reports_real/segment_14_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_14_52, boundary=bnd_matrix_14_52, switch=sw_matrix_14_52, hash_hint=ce1182542c4a7d64"
  },
  {
    "matrix_row_id": "matrix_014_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 14: validator observes canonical read-only evidence and compares 4 registries against policy segment 14.",
    "bad_pattern": "bad pattern 53 in matrix 14: writer drift toward family 4, generated path reports_real/segment_14_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_14_53, boundary=bnd_matrix_14_53, switch=sw_matrix_14_53, hash_hint=aff40319b087177e"
  },
  {
    "matrix_row_id": "matrix_014_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 14: validator observes canonical read-only evidence and compares 5 registries against policy segment 14.",
    "bad_pattern": "bad pattern 54 in matrix 14: writer drift toward family 5, generated path reports_real/segment_14_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_14_54, boundary=bnd_matrix_14_54, switch=sw_matrix_14_54, hash_hint=347b2c2854913c36"
  },
  {
    "matrix_row_id": "matrix_014_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 14: validator observes canonical read-only evidence and compares 1 registries against policy segment 14.",
    "bad_pattern": "bad pattern 55 in matrix 14: writer drift toward family 6, generated path reports_real/segment_14_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_14_55, boundary=bnd_matrix_14_55, switch=sw_matrix_14_55, hash_hint=9cc3e75ca5673246"
  },
  {
    "matrix_row_id": "matrix_014_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 14: validator observes canonical read-only evidence and compares 2 registries against policy segment 14.",
    "bad_pattern": "bad pattern 56 in matrix 14: writer drift toward family 0, generated path reports_real/segment_14_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_14_56, boundary=bnd_matrix_14_56, switch=sw_matrix_14_56, hash_hint=83649e4027ed7caa"
  },
  {
    "matrix_row_id": "matrix_014_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 14: validator observes canonical read-only evidence and compares 3 registries against policy segment 14.",
    "bad_pattern": "bad pattern 57 in matrix 14: writer drift toward family 1, generated path reports_real/segment_14_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_14_57, boundary=bnd_matrix_14_57, switch=sw_matrix_14_57, hash_hint=9e8bb22460e864ee"
  },
  {
    "matrix_row_id": "matrix_014_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 14: validator observes canonical read-only evidence and compares 4 registries against policy segment 14.",
    "bad_pattern": "bad pattern 58 in matrix 14: writer drift toward family 2, generated path reports_real/segment_14_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_14_58, boundary=bnd_matrix_14_58, switch=sw_matrix_14_58, hash_hint=2d498ee239484346"
  },
  {
    "matrix_row_id": "matrix_014_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 14: validator observes canonical read-only evidence and compares 5 registries against policy segment 14.",
    "bad_pattern": "bad pattern 59 in matrix 14: writer drift toward family 3, generated path reports_real/segment_14_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_14_59, boundary=bnd_matrix_14_59, switch=sw_matrix_14_59, hash_hint=0b6aa698787ef657"
  },
  {
    "matrix_row_id": "matrix_014_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 14: validator observes canonical read-only evidence and compares 1 registries against policy segment 14.",
    "bad_pattern": "bad pattern 60 in matrix 14: writer drift toward family 4, generated path reports_real/segment_14_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_14_60, boundary=bnd_matrix_14_60, switch=sw_matrix_14_60, hash_hint=7a8969fe0bde68fb"
  }
]
