from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 6/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 6/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 6/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 6/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 6/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 6/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 6/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 6/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 6/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 6/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 6/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 6/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 6/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 6/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 6/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 6/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 6/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 6/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 6/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 6/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 6/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 6/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 6/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 6/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 6/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_006_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 6: validator observes canonical read-only evidence and compares 2 registries against policy segment 6.",
    "bad_pattern": "bad pattern 1 in matrix 6: writer drift toward family 1, generated path reports_real/segment_6_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_6_1, boundary=bnd_matrix_6_1, switch=sw_matrix_6_1, hash_hint=c19f98d87a551217"
  },
  {
    "matrix_row_id": "matrix_006_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 6: validator observes canonical read-only evidence and compares 3 registries against policy segment 6.",
    "bad_pattern": "bad pattern 2 in matrix 6: writer drift toward family 2, generated path reports_real/segment_6_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_6_2, boundary=bnd_matrix_6_2, switch=sw_matrix_6_2, hash_hint=3254289f54b12adc"
  },
  {
    "matrix_row_id": "matrix_006_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 6: validator observes canonical read-only evidence and compares 4 registries against policy segment 6.",
    "bad_pattern": "bad pattern 3 in matrix 6: writer drift toward family 3, generated path reports_real/segment_6_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_6_3, boundary=bnd_matrix_6_3, switch=sw_matrix_6_3, hash_hint=90cddac96f703d56"
  },
  {
    "matrix_row_id": "matrix_006_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 6: validator observes canonical read-only evidence and compares 5 registries against policy segment 6.",
    "bad_pattern": "bad pattern 4 in matrix 6: writer drift toward family 4, generated path reports_real/segment_6_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_6_4, boundary=bnd_matrix_6_4, switch=sw_matrix_6_4, hash_hint=13bfb5f01b6e4ef4"
  },
  {
    "matrix_row_id": "matrix_006_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 6: validator observes canonical read-only evidence and compares 1 registries against policy segment 6.",
    "bad_pattern": "bad pattern 5 in matrix 6: writer drift toward family 5, generated path reports_real/segment_6_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_6_5, boundary=bnd_matrix_6_5, switch=sw_matrix_6_5, hash_hint=49486453e3c4ce9b"
  },
  {
    "matrix_row_id": "matrix_006_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 6: validator observes canonical read-only evidence and compares 2 registries against policy segment 6.",
    "bad_pattern": "bad pattern 6 in matrix 6: writer drift toward family 6, generated path reports_real/segment_6_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_6_6, boundary=bnd_matrix_6_6, switch=sw_matrix_6_6, hash_hint=45b6aa393e8e0ad7"
  },
  {
    "matrix_row_id": "matrix_006_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 6: validator observes canonical read-only evidence and compares 3 registries against policy segment 6.",
    "bad_pattern": "bad pattern 7 in matrix 6: writer drift toward family 0, generated path reports_real/segment_6_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_6_7, boundary=bnd_matrix_6_7, switch=sw_matrix_6_7, hash_hint=191b402adf1104b4"
  },
  {
    "matrix_row_id": "matrix_006_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 6: validator observes canonical read-only evidence and compares 4 registries against policy segment 6.",
    "bad_pattern": "bad pattern 8 in matrix 6: writer drift toward family 1, generated path reports_real/segment_6_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_6_8, boundary=bnd_matrix_6_8, switch=sw_matrix_6_8, hash_hint=742595dc2605b1b9"
  },
  {
    "matrix_row_id": "matrix_006_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 6: validator observes canonical read-only evidence and compares 5 registries against policy segment 6.",
    "bad_pattern": "bad pattern 9 in matrix 6: writer drift toward family 2, generated path reports_real/segment_6_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_6_9, boundary=bnd_matrix_6_9, switch=sw_matrix_6_9, hash_hint=59b0c787b63af221"
  },
  {
    "matrix_row_id": "matrix_006_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 6: validator observes canonical read-only evidence and compares 1 registries against policy segment 6.",
    "bad_pattern": "bad pattern 10 in matrix 6: writer drift toward family 3, generated path reports_real/segment_6_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_6_10, boundary=bnd_matrix_6_10, switch=sw_matrix_6_10, hash_hint=a500f0b29b75b08b"
  },
  {
    "matrix_row_id": "matrix_006_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 6: validator observes canonical read-only evidence and compares 2 registries against policy segment 6.",
    "bad_pattern": "bad pattern 11 in matrix 6: writer drift toward family 4, generated path reports_real/segment_6_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_6_11, boundary=bnd_matrix_6_11, switch=sw_matrix_6_11, hash_hint=0a0c90d4b8b012fa"
  },
  {
    "matrix_row_id": "matrix_006_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 6: validator observes canonical read-only evidence and compares 3 registries against policy segment 6.",
    "bad_pattern": "bad pattern 12 in matrix 6: writer drift toward family 5, generated path reports_real/segment_6_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_6_12, boundary=bnd_matrix_6_12, switch=sw_matrix_6_12, hash_hint=9908441a54809d63"
  },
  {
    "matrix_row_id": "matrix_006_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 6: validator observes canonical read-only evidence and compares 4 registries against policy segment 6.",
    "bad_pattern": "bad pattern 13 in matrix 6: writer drift toward family 6, generated path reports_real/segment_6_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_6_13, boundary=bnd_matrix_6_13, switch=sw_matrix_6_13, hash_hint=538cdde4e3c0a8d5"
  },
  {
    "matrix_row_id": "matrix_006_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 6: validator observes canonical read-only evidence and compares 5 registries against policy segment 6.",
    "bad_pattern": "bad pattern 14 in matrix 6: writer drift toward family 0, generated path reports_real/segment_6_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_6_14, boundary=bnd_matrix_6_14, switch=sw_matrix_6_14, hash_hint=e133ae5b79941d70"
  },
  {
    "matrix_row_id": "matrix_006_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 6: validator observes canonical read-only evidence and compares 1 registries against policy segment 6.",
    "bad_pattern": "bad pattern 15 in matrix 6: writer drift toward family 1, generated path reports_real/segment_6_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_6_15, boundary=bnd_matrix_6_15, switch=sw_matrix_6_15, hash_hint=0c7d921bc6cebdcb"
  },
  {
    "matrix_row_id": "matrix_006_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 6: validator observes canonical read-only evidence and compares 2 registries against policy segment 6.",
    "bad_pattern": "bad pattern 16 in matrix 6: writer drift toward family 2, generated path reports_real/segment_6_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_6_16, boundary=bnd_matrix_6_16, switch=sw_matrix_6_16, hash_hint=1109e69f75b95dc1"
  },
  {
    "matrix_row_id": "matrix_006_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 6: validator observes canonical read-only evidence and compares 3 registries against policy segment 6.",
    "bad_pattern": "bad pattern 17 in matrix 6: writer drift toward family 3, generated path reports_real/segment_6_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_6_17, boundary=bnd_matrix_6_17, switch=sw_matrix_6_17, hash_hint=968d876e29906682"
  },
  {
    "matrix_row_id": "matrix_006_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 6: validator observes canonical read-only evidence and compares 4 registries against policy segment 6.",
    "bad_pattern": "bad pattern 18 in matrix 6: writer drift toward family 4, generated path reports_real/segment_6_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_6_18, boundary=bnd_matrix_6_18, switch=sw_matrix_6_18, hash_hint=76fcc000d1c16fc3"
  },
  {
    "matrix_row_id": "matrix_006_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 6: validator observes canonical read-only evidence and compares 5 registries against policy segment 6.",
    "bad_pattern": "bad pattern 19 in matrix 6: writer drift toward family 5, generated path reports_real/segment_6_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_6_19, boundary=bnd_matrix_6_19, switch=sw_matrix_6_19, hash_hint=9216a664731c5e22"
  },
  {
    "matrix_row_id": "matrix_006_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 6: validator observes canonical read-only evidence and compares 1 registries against policy segment 6.",
    "bad_pattern": "bad pattern 20 in matrix 6: writer drift toward family 6, generated path reports_real/segment_6_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_6_20, boundary=bnd_matrix_6_20, switch=sw_matrix_6_20, hash_hint=3f62e7b6beedb12b"
  },
  {
    "matrix_row_id": "matrix_006_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 6: validator observes canonical read-only evidence and compares 2 registries against policy segment 6.",
    "bad_pattern": "bad pattern 21 in matrix 6: writer drift toward family 0, generated path reports_real/segment_6_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_6_21, boundary=bnd_matrix_6_21, switch=sw_matrix_6_21, hash_hint=49078babac41cff8"
  },
  {
    "matrix_row_id": "matrix_006_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 6: validator observes canonical read-only evidence and compares 3 registries against policy segment 6.",
    "bad_pattern": "bad pattern 22 in matrix 6: writer drift toward family 1, generated path reports_real/segment_6_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_6_22, boundary=bnd_matrix_6_22, switch=sw_matrix_6_22, hash_hint=485ba4d154a711b0"
  },
  {
    "matrix_row_id": "matrix_006_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 6: validator observes canonical read-only evidence and compares 4 registries against policy segment 6.",
    "bad_pattern": "bad pattern 23 in matrix 6: writer drift toward family 2, generated path reports_real/segment_6_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_6_23, boundary=bnd_matrix_6_23, switch=sw_matrix_6_23, hash_hint=83b0f59129619c53"
  },
  {
    "matrix_row_id": "matrix_006_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 6: validator observes canonical read-only evidence and compares 5 registries against policy segment 6.",
    "bad_pattern": "bad pattern 24 in matrix 6: writer drift toward family 3, generated path reports_real/segment_6_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_6_24, boundary=bnd_matrix_6_24, switch=sw_matrix_6_24, hash_hint=b1010dba61f47e99"
  },
  {
    "matrix_row_id": "matrix_006_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 6: validator observes canonical read-only evidence and compares 1 registries against policy segment 6.",
    "bad_pattern": "bad pattern 25 in matrix 6: writer drift toward family 4, generated path reports_real/segment_6_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_6_25, boundary=bnd_matrix_6_25, switch=sw_matrix_6_25, hash_hint=c87d4c5afddd4be7"
  },
  {
    "matrix_row_id": "matrix_006_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 6: validator observes canonical read-only evidence and compares 2 registries against policy segment 6.",
    "bad_pattern": "bad pattern 26 in matrix 6: writer drift toward family 5, generated path reports_real/segment_6_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_6_26, boundary=bnd_matrix_6_26, switch=sw_matrix_6_26, hash_hint=90473c49d20826cb"
  },
  {
    "matrix_row_id": "matrix_006_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 6: validator observes canonical read-only evidence and compares 3 registries against policy segment 6.",
    "bad_pattern": "bad pattern 27 in matrix 6: writer drift toward family 6, generated path reports_real/segment_6_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_6_27, boundary=bnd_matrix_6_27, switch=sw_matrix_6_27, hash_hint=b633a2fa9e7ba13f"
  },
  {
    "matrix_row_id": "matrix_006_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 6: validator observes canonical read-only evidence and compares 4 registries against policy segment 6.",
    "bad_pattern": "bad pattern 28 in matrix 6: writer drift toward family 0, generated path reports_real/segment_6_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_6_28, boundary=bnd_matrix_6_28, switch=sw_matrix_6_28, hash_hint=7c7fbf149600a927"
  },
  {
    "matrix_row_id": "matrix_006_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 6: validator observes canonical read-only evidence and compares 5 registries against policy segment 6.",
    "bad_pattern": "bad pattern 29 in matrix 6: writer drift toward family 1, generated path reports_real/segment_6_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_6_29, boundary=bnd_matrix_6_29, switch=sw_matrix_6_29, hash_hint=3a438a956717f5c0"
  },
  {
    "matrix_row_id": "matrix_006_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 6: validator observes canonical read-only evidence and compares 1 registries against policy segment 6.",
    "bad_pattern": "bad pattern 30 in matrix 6: writer drift toward family 2, generated path reports_real/segment_6_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_6_30, boundary=bnd_matrix_6_30, switch=sw_matrix_6_30, hash_hint=101c1ed04ad185ae"
  },
  {
    "matrix_row_id": "matrix_006_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 6: validator observes canonical read-only evidence and compares 2 registries against policy segment 6.",
    "bad_pattern": "bad pattern 31 in matrix 6: writer drift toward family 3, generated path reports_real/segment_6_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_6_31, boundary=bnd_matrix_6_31, switch=sw_matrix_6_31, hash_hint=35736c6670aa4b6e"
  },
  {
    "matrix_row_id": "matrix_006_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 6: validator observes canonical read-only evidence and compares 3 registries against policy segment 6.",
    "bad_pattern": "bad pattern 32 in matrix 6: writer drift toward family 4, generated path reports_real/segment_6_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_6_32, boundary=bnd_matrix_6_32, switch=sw_matrix_6_32, hash_hint=961fd3c9567a265b"
  },
  {
    "matrix_row_id": "matrix_006_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 6: validator observes canonical read-only evidence and compares 4 registries against policy segment 6.",
    "bad_pattern": "bad pattern 33 in matrix 6: writer drift toward family 5, generated path reports_real/segment_6_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_6_33, boundary=bnd_matrix_6_33, switch=sw_matrix_6_33, hash_hint=05c495505e858c24"
  },
  {
    "matrix_row_id": "matrix_006_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 6: validator observes canonical read-only evidence and compares 5 registries against policy segment 6.",
    "bad_pattern": "bad pattern 34 in matrix 6: writer drift toward family 6, generated path reports_real/segment_6_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_6_34, boundary=bnd_matrix_6_34, switch=sw_matrix_6_34, hash_hint=c382428dd38a3711"
  },
  {
    "matrix_row_id": "matrix_006_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 6: validator observes canonical read-only evidence and compares 1 registries against policy segment 6.",
    "bad_pattern": "bad pattern 35 in matrix 6: writer drift toward family 0, generated path reports_real/segment_6_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_6_35, boundary=bnd_matrix_6_35, switch=sw_matrix_6_35, hash_hint=61f29bf8a01261da"
  },
  {
    "matrix_row_id": "matrix_006_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 6: validator observes canonical read-only evidence and compares 2 registries against policy segment 6.",
    "bad_pattern": "bad pattern 36 in matrix 6: writer drift toward family 1, generated path reports_real/segment_6_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_6_36, boundary=bnd_matrix_6_36, switch=sw_matrix_6_36, hash_hint=be21379ea4f111fa"
  },
  {
    "matrix_row_id": "matrix_006_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 6: validator observes canonical read-only evidence and compares 3 registries against policy segment 6.",
    "bad_pattern": "bad pattern 37 in matrix 6: writer drift toward family 2, generated path reports_real/segment_6_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_6_37, boundary=bnd_matrix_6_37, switch=sw_matrix_6_37, hash_hint=fb0bc26d339f1c35"
  },
  {
    "matrix_row_id": "matrix_006_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 6: validator observes canonical read-only evidence and compares 4 registries against policy segment 6.",
    "bad_pattern": "bad pattern 38 in matrix 6: writer drift toward family 3, generated path reports_real/segment_6_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_6_38, boundary=bnd_matrix_6_38, switch=sw_matrix_6_38, hash_hint=40468c7b0594b2e2"
  },
  {
    "matrix_row_id": "matrix_006_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 6: validator observes canonical read-only evidence and compares 5 registries against policy segment 6.",
    "bad_pattern": "bad pattern 39 in matrix 6: writer drift toward family 4, generated path reports_real/segment_6_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_6_39, boundary=bnd_matrix_6_39, switch=sw_matrix_6_39, hash_hint=b05a9b7968d13a54"
  },
  {
    "matrix_row_id": "matrix_006_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 6: validator observes canonical read-only evidence and compares 1 registries against policy segment 6.",
    "bad_pattern": "bad pattern 40 in matrix 6: writer drift toward family 5, generated path reports_real/segment_6_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_6_40, boundary=bnd_matrix_6_40, switch=sw_matrix_6_40, hash_hint=191fe29af35a263e"
  },
  {
    "matrix_row_id": "matrix_006_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 6: validator observes canonical read-only evidence and compares 2 registries against policy segment 6.",
    "bad_pattern": "bad pattern 41 in matrix 6: writer drift toward family 6, generated path reports_real/segment_6_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_6_41, boundary=bnd_matrix_6_41, switch=sw_matrix_6_41, hash_hint=3a9c900bd709e2b3"
  },
  {
    "matrix_row_id": "matrix_006_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 6: validator observes canonical read-only evidence and compares 3 registries against policy segment 6.",
    "bad_pattern": "bad pattern 42 in matrix 6: writer drift toward family 0, generated path reports_real/segment_6_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_6_42, boundary=bnd_matrix_6_42, switch=sw_matrix_6_42, hash_hint=8a8cbfdad855f96e"
  },
  {
    "matrix_row_id": "matrix_006_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 6: validator observes canonical read-only evidence and compares 4 registries against policy segment 6.",
    "bad_pattern": "bad pattern 43 in matrix 6: writer drift toward family 1, generated path reports_real/segment_6_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_6_43, boundary=bnd_matrix_6_43, switch=sw_matrix_6_43, hash_hint=0fee417d633210fe"
  },
  {
    "matrix_row_id": "matrix_006_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 6: validator observes canonical read-only evidence and compares 5 registries against policy segment 6.",
    "bad_pattern": "bad pattern 44 in matrix 6: writer drift toward family 2, generated path reports_real/segment_6_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_6_44, boundary=bnd_matrix_6_44, switch=sw_matrix_6_44, hash_hint=792a529a59dba66c"
  },
  {
    "matrix_row_id": "matrix_006_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 6: validator observes canonical read-only evidence and compares 1 registries against policy segment 6.",
    "bad_pattern": "bad pattern 45 in matrix 6: writer drift toward family 3, generated path reports_real/segment_6_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_6_45, boundary=bnd_matrix_6_45, switch=sw_matrix_6_45, hash_hint=51f0d4adc0604a58"
  },
  {
    "matrix_row_id": "matrix_006_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 6: validator observes canonical read-only evidence and compares 2 registries against policy segment 6.",
    "bad_pattern": "bad pattern 46 in matrix 6: writer drift toward family 4, generated path reports_real/segment_6_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_6_46, boundary=bnd_matrix_6_46, switch=sw_matrix_6_46, hash_hint=df31cbf5c8a8bceb"
  },
  {
    "matrix_row_id": "matrix_006_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 6: validator observes canonical read-only evidence and compares 3 registries against policy segment 6.",
    "bad_pattern": "bad pattern 47 in matrix 6: writer drift toward family 5, generated path reports_real/segment_6_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_6_47, boundary=bnd_matrix_6_47, switch=sw_matrix_6_47, hash_hint=c9fcf081111227c1"
  },
  {
    "matrix_row_id": "matrix_006_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 6: validator observes canonical read-only evidence and compares 4 registries against policy segment 6.",
    "bad_pattern": "bad pattern 48 in matrix 6: writer drift toward family 6, generated path reports_real/segment_6_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_6_48, boundary=bnd_matrix_6_48, switch=sw_matrix_6_48, hash_hint=09b150e8bf11a782"
  },
  {
    "matrix_row_id": "matrix_006_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 6: validator observes canonical read-only evidence and compares 5 registries against policy segment 6.",
    "bad_pattern": "bad pattern 49 in matrix 6: writer drift toward family 0, generated path reports_real/segment_6_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_6_49, boundary=bnd_matrix_6_49, switch=sw_matrix_6_49, hash_hint=cbbe4137ac865fd9"
  },
  {
    "matrix_row_id": "matrix_006_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 6: validator observes canonical read-only evidence and compares 1 registries against policy segment 6.",
    "bad_pattern": "bad pattern 50 in matrix 6: writer drift toward family 1, generated path reports_real/segment_6_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_6_50, boundary=bnd_matrix_6_50, switch=sw_matrix_6_50, hash_hint=ef2c91d60ceb015d"
  },
  {
    "matrix_row_id": "matrix_006_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 6: validator observes canonical read-only evidence and compares 2 registries against policy segment 6.",
    "bad_pattern": "bad pattern 51 in matrix 6: writer drift toward family 2, generated path reports_real/segment_6_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_6_51, boundary=bnd_matrix_6_51, switch=sw_matrix_6_51, hash_hint=179c383914aef6e2"
  },
  {
    "matrix_row_id": "matrix_006_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 6: validator observes canonical read-only evidence and compares 3 registries against policy segment 6.",
    "bad_pattern": "bad pattern 52 in matrix 6: writer drift toward family 3, generated path reports_real/segment_6_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_6_52, boundary=bnd_matrix_6_52, switch=sw_matrix_6_52, hash_hint=1d265d0104a6909e"
  },
  {
    "matrix_row_id": "matrix_006_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 6: validator observes canonical read-only evidence and compares 4 registries against policy segment 6.",
    "bad_pattern": "bad pattern 53 in matrix 6: writer drift toward family 4, generated path reports_real/segment_6_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_6_53, boundary=bnd_matrix_6_53, switch=sw_matrix_6_53, hash_hint=738f05eed81a3b30"
  },
  {
    "matrix_row_id": "matrix_006_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 6: validator observes canonical read-only evidence and compares 5 registries against policy segment 6.",
    "bad_pattern": "bad pattern 54 in matrix 6: writer drift toward family 5, generated path reports_real/segment_6_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_6_54, boundary=bnd_matrix_6_54, switch=sw_matrix_6_54, hash_hint=92153bc9561ae0dc"
  },
  {
    "matrix_row_id": "matrix_006_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 6: validator observes canonical read-only evidence and compares 1 registries against policy segment 6.",
    "bad_pattern": "bad pattern 55 in matrix 6: writer drift toward family 6, generated path reports_real/segment_6_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_6_55, boundary=bnd_matrix_6_55, switch=sw_matrix_6_55, hash_hint=cf82f64706488cd5"
  },
  {
    "matrix_row_id": "matrix_006_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 6: validator observes canonical read-only evidence and compares 2 registries against policy segment 6.",
    "bad_pattern": "bad pattern 56 in matrix 6: writer drift toward family 0, generated path reports_real/segment_6_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_6_56, boundary=bnd_matrix_6_56, switch=sw_matrix_6_56, hash_hint=117f1acf71666621"
  },
  {
    "matrix_row_id": "matrix_006_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 6: validator observes canonical read-only evidence and compares 3 registries against policy segment 6.",
    "bad_pattern": "bad pattern 57 in matrix 6: writer drift toward family 1, generated path reports_real/segment_6_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_6_57, boundary=bnd_matrix_6_57, switch=sw_matrix_6_57, hash_hint=06cec09d45018e71"
  },
  {
    "matrix_row_id": "matrix_006_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 6: validator observes canonical read-only evidence and compares 4 registries against policy segment 6.",
    "bad_pattern": "bad pattern 58 in matrix 6: writer drift toward family 2, generated path reports_real/segment_6_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_6_58, boundary=bnd_matrix_6_58, switch=sw_matrix_6_58, hash_hint=583f697b21f9876c"
  },
  {
    "matrix_row_id": "matrix_006_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 6: validator observes canonical read-only evidence and compares 5 registries against policy segment 6.",
    "bad_pattern": "bad pattern 59 in matrix 6: writer drift toward family 3, generated path reports_real/segment_6_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_6_59, boundary=bnd_matrix_6_59, switch=sw_matrix_6_59, hash_hint=2d2b6354dbee9828"
  },
  {
    "matrix_row_id": "matrix_006_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 6: validator observes canonical read-only evidence and compares 1 registries against policy segment 6.",
    "bad_pattern": "bad pattern 60 in matrix 6: writer drift toward family 4, generated path reports_real/segment_6_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_6_60, boundary=bnd_matrix_6_60, switch=sw_matrix_6_60, hash_hint=4b4598afaa104bf9"
  }
]
