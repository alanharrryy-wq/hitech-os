from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 5/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 5/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 5/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 5/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 5/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 5/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 5/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 5/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 5/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 5/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 5/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 5/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 5/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 5/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 5/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 5/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 5/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 5/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 5/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 5/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 5/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 5/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 5/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 5/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 5/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_005_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 5: validator observes canonical read-only evidence and compares 2 registries against policy segment 5.",
    "bad_pattern": "bad pattern 1 in matrix 5: writer drift toward family 1, generated path reports_real/segment_5_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_5_1, boundary=bnd_matrix_5_1, switch=sw_matrix_5_1, hash_hint=ae5dd0c8f5769cc5"
  },
  {
    "matrix_row_id": "matrix_005_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 5: validator observes canonical read-only evidence and compares 3 registries against policy segment 5.",
    "bad_pattern": "bad pattern 2 in matrix 5: writer drift toward family 2, generated path reports_real/segment_5_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_5_2, boundary=bnd_matrix_5_2, switch=sw_matrix_5_2, hash_hint=ff24aa1d961a006d"
  },
  {
    "matrix_row_id": "matrix_005_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 5: validator observes canonical read-only evidence and compares 4 registries against policy segment 5.",
    "bad_pattern": "bad pattern 3 in matrix 5: writer drift toward family 3, generated path reports_real/segment_5_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_5_3, boundary=bnd_matrix_5_3, switch=sw_matrix_5_3, hash_hint=962538260cc17575"
  },
  {
    "matrix_row_id": "matrix_005_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 5: validator observes canonical read-only evidence and compares 5 registries against policy segment 5.",
    "bad_pattern": "bad pattern 4 in matrix 5: writer drift toward family 4, generated path reports_real/segment_5_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_5_4, boundary=bnd_matrix_5_4, switch=sw_matrix_5_4, hash_hint=1bcef002ce389c49"
  },
  {
    "matrix_row_id": "matrix_005_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 5: validator observes canonical read-only evidence and compares 1 registries against policy segment 5.",
    "bad_pattern": "bad pattern 5 in matrix 5: writer drift toward family 5, generated path reports_real/segment_5_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_5_5, boundary=bnd_matrix_5_5, switch=sw_matrix_5_5, hash_hint=6a0eed5fb570965c"
  },
  {
    "matrix_row_id": "matrix_005_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 5: validator observes canonical read-only evidence and compares 2 registries against policy segment 5.",
    "bad_pattern": "bad pattern 6 in matrix 5: writer drift toward family 6, generated path reports_real/segment_5_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_5_6, boundary=bnd_matrix_5_6, switch=sw_matrix_5_6, hash_hint=a991feb67f4a5bc9"
  },
  {
    "matrix_row_id": "matrix_005_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 5: validator observes canonical read-only evidence and compares 3 registries against policy segment 5.",
    "bad_pattern": "bad pattern 7 in matrix 5: writer drift toward family 0, generated path reports_real/segment_5_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_5_7, boundary=bnd_matrix_5_7, switch=sw_matrix_5_7, hash_hint=cb680831cd7c0994"
  },
  {
    "matrix_row_id": "matrix_005_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 5: validator observes canonical read-only evidence and compares 4 registries against policy segment 5.",
    "bad_pattern": "bad pattern 8 in matrix 5: writer drift toward family 1, generated path reports_real/segment_5_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_5_8, boundary=bnd_matrix_5_8, switch=sw_matrix_5_8, hash_hint=5a2d77725763c730"
  },
  {
    "matrix_row_id": "matrix_005_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 5: validator observes canonical read-only evidence and compares 5 registries against policy segment 5.",
    "bad_pattern": "bad pattern 9 in matrix 5: writer drift toward family 2, generated path reports_real/segment_5_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_5_9, boundary=bnd_matrix_5_9, switch=sw_matrix_5_9, hash_hint=e5fd0517a0387e48"
  },
  {
    "matrix_row_id": "matrix_005_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 5: validator observes canonical read-only evidence and compares 1 registries against policy segment 5.",
    "bad_pattern": "bad pattern 10 in matrix 5: writer drift toward family 3, generated path reports_real/segment_5_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_5_10, boundary=bnd_matrix_5_10, switch=sw_matrix_5_10, hash_hint=53ebb9803f553d43"
  },
  {
    "matrix_row_id": "matrix_005_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 5: validator observes canonical read-only evidence and compares 2 registries against policy segment 5.",
    "bad_pattern": "bad pattern 11 in matrix 5: writer drift toward family 4, generated path reports_real/segment_5_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_5_11, boundary=bnd_matrix_5_11, switch=sw_matrix_5_11, hash_hint=4c4b1ddfff0f18c6"
  },
  {
    "matrix_row_id": "matrix_005_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 5: validator observes canonical read-only evidence and compares 3 registries against policy segment 5.",
    "bad_pattern": "bad pattern 12 in matrix 5: writer drift toward family 5, generated path reports_real/segment_5_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_5_12, boundary=bnd_matrix_5_12, switch=sw_matrix_5_12, hash_hint=a8b5679e6e92cae6"
  },
  {
    "matrix_row_id": "matrix_005_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 5: validator observes canonical read-only evidence and compares 4 registries against policy segment 5.",
    "bad_pattern": "bad pattern 13 in matrix 5: writer drift toward family 6, generated path reports_real/segment_5_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_5_13, boundary=bnd_matrix_5_13, switch=sw_matrix_5_13, hash_hint=2753fbd7c8e27dd6"
  },
  {
    "matrix_row_id": "matrix_005_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 5: validator observes canonical read-only evidence and compares 5 registries against policy segment 5.",
    "bad_pattern": "bad pattern 14 in matrix 5: writer drift toward family 0, generated path reports_real/segment_5_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_5_14, boundary=bnd_matrix_5_14, switch=sw_matrix_5_14, hash_hint=3918c5b4e44a5847"
  },
  {
    "matrix_row_id": "matrix_005_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 5: validator observes canonical read-only evidence and compares 1 registries against policy segment 5.",
    "bad_pattern": "bad pattern 15 in matrix 5: writer drift toward family 1, generated path reports_real/segment_5_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_5_15, boundary=bnd_matrix_5_15, switch=sw_matrix_5_15, hash_hint=64834ba7f5393da9"
  },
  {
    "matrix_row_id": "matrix_005_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 5: validator observes canonical read-only evidence and compares 2 registries against policy segment 5.",
    "bad_pattern": "bad pattern 16 in matrix 5: writer drift toward family 2, generated path reports_real/segment_5_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_5_16, boundary=bnd_matrix_5_16, switch=sw_matrix_5_16, hash_hint=f128db472236d515"
  },
  {
    "matrix_row_id": "matrix_005_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 5: validator observes canonical read-only evidence and compares 3 registries against policy segment 5.",
    "bad_pattern": "bad pattern 17 in matrix 5: writer drift toward family 3, generated path reports_real/segment_5_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_5_17, boundary=bnd_matrix_5_17, switch=sw_matrix_5_17, hash_hint=f97ef0ae5ea296b8"
  },
  {
    "matrix_row_id": "matrix_005_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 5: validator observes canonical read-only evidence and compares 4 registries against policy segment 5.",
    "bad_pattern": "bad pattern 18 in matrix 5: writer drift toward family 4, generated path reports_real/segment_5_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_5_18, boundary=bnd_matrix_5_18, switch=sw_matrix_5_18, hash_hint=22c9548a812f6931"
  },
  {
    "matrix_row_id": "matrix_005_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 5: validator observes canonical read-only evidence and compares 5 registries against policy segment 5.",
    "bad_pattern": "bad pattern 19 in matrix 5: writer drift toward family 5, generated path reports_real/segment_5_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_5_19, boundary=bnd_matrix_5_19, switch=sw_matrix_5_19, hash_hint=a0c5dcb764f194c0"
  },
  {
    "matrix_row_id": "matrix_005_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 5: validator observes canonical read-only evidence and compares 1 registries against policy segment 5.",
    "bad_pattern": "bad pattern 20 in matrix 5: writer drift toward family 6, generated path reports_real/segment_5_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_5_20, boundary=bnd_matrix_5_20, switch=sw_matrix_5_20, hash_hint=2b2ac3f97b7235ce"
  },
  {
    "matrix_row_id": "matrix_005_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 5: validator observes canonical read-only evidence and compares 2 registries against policy segment 5.",
    "bad_pattern": "bad pattern 21 in matrix 5: writer drift toward family 0, generated path reports_real/segment_5_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_5_21, boundary=bnd_matrix_5_21, switch=sw_matrix_5_21, hash_hint=bb51ee2fecfdf220"
  },
  {
    "matrix_row_id": "matrix_005_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 5: validator observes canonical read-only evidence and compares 3 registries against policy segment 5.",
    "bad_pattern": "bad pattern 22 in matrix 5: writer drift toward family 1, generated path reports_real/segment_5_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_5_22, boundary=bnd_matrix_5_22, switch=sw_matrix_5_22, hash_hint=ed38ff6bbaa4b294"
  },
  {
    "matrix_row_id": "matrix_005_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 5: validator observes canonical read-only evidence and compares 4 registries against policy segment 5.",
    "bad_pattern": "bad pattern 23 in matrix 5: writer drift toward family 2, generated path reports_real/segment_5_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_5_23, boundary=bnd_matrix_5_23, switch=sw_matrix_5_23, hash_hint=b3a88c64205961d0"
  },
  {
    "matrix_row_id": "matrix_005_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 5: validator observes canonical read-only evidence and compares 5 registries against policy segment 5.",
    "bad_pattern": "bad pattern 24 in matrix 5: writer drift toward family 3, generated path reports_real/segment_5_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_5_24, boundary=bnd_matrix_5_24, switch=sw_matrix_5_24, hash_hint=7454b61139b3b580"
  },
  {
    "matrix_row_id": "matrix_005_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 5: validator observes canonical read-only evidence and compares 1 registries against policy segment 5.",
    "bad_pattern": "bad pattern 25 in matrix 5: writer drift toward family 4, generated path reports_real/segment_5_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_5_25, boundary=bnd_matrix_5_25, switch=sw_matrix_5_25, hash_hint=b722e4b08dd40161"
  },
  {
    "matrix_row_id": "matrix_005_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 5: validator observes canonical read-only evidence and compares 2 registries against policy segment 5.",
    "bad_pattern": "bad pattern 26 in matrix 5: writer drift toward family 5, generated path reports_real/segment_5_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_5_26, boundary=bnd_matrix_5_26, switch=sw_matrix_5_26, hash_hint=fe4fb8cc74f188cf"
  },
  {
    "matrix_row_id": "matrix_005_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 5: validator observes canonical read-only evidence and compares 3 registries against policy segment 5.",
    "bad_pattern": "bad pattern 27 in matrix 5: writer drift toward family 6, generated path reports_real/segment_5_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_5_27, boundary=bnd_matrix_5_27, switch=sw_matrix_5_27, hash_hint=66ba9dbad54d209d"
  },
  {
    "matrix_row_id": "matrix_005_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 5: validator observes canonical read-only evidence and compares 4 registries against policy segment 5.",
    "bad_pattern": "bad pattern 28 in matrix 5: writer drift toward family 0, generated path reports_real/segment_5_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_5_28, boundary=bnd_matrix_5_28, switch=sw_matrix_5_28, hash_hint=9fbd5f821dd8436a"
  },
  {
    "matrix_row_id": "matrix_005_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 5: validator observes canonical read-only evidence and compares 5 registries against policy segment 5.",
    "bad_pattern": "bad pattern 29 in matrix 5: writer drift toward family 1, generated path reports_real/segment_5_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_5_29, boundary=bnd_matrix_5_29, switch=sw_matrix_5_29, hash_hint=bf772beee001537f"
  },
  {
    "matrix_row_id": "matrix_005_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 5: validator observes canonical read-only evidence and compares 1 registries against policy segment 5.",
    "bad_pattern": "bad pattern 30 in matrix 5: writer drift toward family 2, generated path reports_real/segment_5_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_5_30, boundary=bnd_matrix_5_30, switch=sw_matrix_5_30, hash_hint=f746fc69bab48418"
  },
  {
    "matrix_row_id": "matrix_005_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 5: validator observes canonical read-only evidence and compares 2 registries against policy segment 5.",
    "bad_pattern": "bad pattern 31 in matrix 5: writer drift toward family 3, generated path reports_real/segment_5_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_5_31, boundary=bnd_matrix_5_31, switch=sw_matrix_5_31, hash_hint=480346e520a993b2"
  },
  {
    "matrix_row_id": "matrix_005_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 5: validator observes canonical read-only evidence and compares 3 registries against policy segment 5.",
    "bad_pattern": "bad pattern 32 in matrix 5: writer drift toward family 4, generated path reports_real/segment_5_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_5_32, boundary=bnd_matrix_5_32, switch=sw_matrix_5_32, hash_hint=fb842ba7d8049519"
  },
  {
    "matrix_row_id": "matrix_005_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 5: validator observes canonical read-only evidence and compares 4 registries against policy segment 5.",
    "bad_pattern": "bad pattern 33 in matrix 5: writer drift toward family 5, generated path reports_real/segment_5_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_5_33, boundary=bnd_matrix_5_33, switch=sw_matrix_5_33, hash_hint=c79b12db0f764a42"
  },
  {
    "matrix_row_id": "matrix_005_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 5: validator observes canonical read-only evidence and compares 5 registries against policy segment 5.",
    "bad_pattern": "bad pattern 34 in matrix 5: writer drift toward family 6, generated path reports_real/segment_5_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_5_34, boundary=bnd_matrix_5_34, switch=sw_matrix_5_34, hash_hint=109ca650b3eeb7de"
  },
  {
    "matrix_row_id": "matrix_005_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 5: validator observes canonical read-only evidence and compares 1 registries against policy segment 5.",
    "bad_pattern": "bad pattern 35 in matrix 5: writer drift toward family 0, generated path reports_real/segment_5_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_5_35, boundary=bnd_matrix_5_35, switch=sw_matrix_5_35, hash_hint=9336bae3a55d0ea8"
  },
  {
    "matrix_row_id": "matrix_005_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 5: validator observes canonical read-only evidence and compares 2 registries against policy segment 5.",
    "bad_pattern": "bad pattern 36 in matrix 5: writer drift toward family 1, generated path reports_real/segment_5_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_5_36, boundary=bnd_matrix_5_36, switch=sw_matrix_5_36, hash_hint=20d249745ade5c0e"
  },
  {
    "matrix_row_id": "matrix_005_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 5: validator observes canonical read-only evidence and compares 3 registries against policy segment 5.",
    "bad_pattern": "bad pattern 37 in matrix 5: writer drift toward family 2, generated path reports_real/segment_5_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_5_37, boundary=bnd_matrix_5_37, switch=sw_matrix_5_37, hash_hint=b2612241cb1eaa12"
  },
  {
    "matrix_row_id": "matrix_005_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 5: validator observes canonical read-only evidence and compares 4 registries against policy segment 5.",
    "bad_pattern": "bad pattern 38 in matrix 5: writer drift toward family 3, generated path reports_real/segment_5_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_5_38, boundary=bnd_matrix_5_38, switch=sw_matrix_5_38, hash_hint=17ec164d4072935a"
  },
  {
    "matrix_row_id": "matrix_005_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 5: validator observes canonical read-only evidence and compares 5 registries against policy segment 5.",
    "bad_pattern": "bad pattern 39 in matrix 5: writer drift toward family 4, generated path reports_real/segment_5_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_5_39, boundary=bnd_matrix_5_39, switch=sw_matrix_5_39, hash_hint=9b597beed5fcd7b4"
  },
  {
    "matrix_row_id": "matrix_005_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 5: validator observes canonical read-only evidence and compares 1 registries against policy segment 5.",
    "bad_pattern": "bad pattern 40 in matrix 5: writer drift toward family 5, generated path reports_real/segment_5_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_5_40, boundary=bnd_matrix_5_40, switch=sw_matrix_5_40, hash_hint=24568bd35db9a5c3"
  },
  {
    "matrix_row_id": "matrix_005_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 5: validator observes canonical read-only evidence and compares 2 registries against policy segment 5.",
    "bad_pattern": "bad pattern 41 in matrix 5: writer drift toward family 6, generated path reports_real/segment_5_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_5_41, boundary=bnd_matrix_5_41, switch=sw_matrix_5_41, hash_hint=289805a68a4dac20"
  },
  {
    "matrix_row_id": "matrix_005_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 5: validator observes canonical read-only evidence and compares 3 registries against policy segment 5.",
    "bad_pattern": "bad pattern 42 in matrix 5: writer drift toward family 0, generated path reports_real/segment_5_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_5_42, boundary=bnd_matrix_5_42, switch=sw_matrix_5_42, hash_hint=90565118049caecc"
  },
  {
    "matrix_row_id": "matrix_005_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 5: validator observes canonical read-only evidence and compares 4 registries against policy segment 5.",
    "bad_pattern": "bad pattern 43 in matrix 5: writer drift toward family 1, generated path reports_real/segment_5_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_5_43, boundary=bnd_matrix_5_43, switch=sw_matrix_5_43, hash_hint=446c80bb49763300"
  },
  {
    "matrix_row_id": "matrix_005_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 5: validator observes canonical read-only evidence and compares 5 registries against policy segment 5.",
    "bad_pattern": "bad pattern 44 in matrix 5: writer drift toward family 2, generated path reports_real/segment_5_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_5_44, boundary=bnd_matrix_5_44, switch=sw_matrix_5_44, hash_hint=cbc91e4ca0dfc132"
  },
  {
    "matrix_row_id": "matrix_005_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 5: validator observes canonical read-only evidence and compares 1 registries against policy segment 5.",
    "bad_pattern": "bad pattern 45 in matrix 5: writer drift toward family 3, generated path reports_real/segment_5_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_5_45, boundary=bnd_matrix_5_45, switch=sw_matrix_5_45, hash_hint=cf167bdb01565085"
  },
  {
    "matrix_row_id": "matrix_005_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 5: validator observes canonical read-only evidence and compares 2 registries against policy segment 5.",
    "bad_pattern": "bad pattern 46 in matrix 5: writer drift toward family 4, generated path reports_real/segment_5_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_5_46, boundary=bnd_matrix_5_46, switch=sw_matrix_5_46, hash_hint=eb1c05950be4b395"
  },
  {
    "matrix_row_id": "matrix_005_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 5: validator observes canonical read-only evidence and compares 3 registries against policy segment 5.",
    "bad_pattern": "bad pattern 47 in matrix 5: writer drift toward family 5, generated path reports_real/segment_5_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_5_47, boundary=bnd_matrix_5_47, switch=sw_matrix_5_47, hash_hint=0532e83f98b4c830"
  },
  {
    "matrix_row_id": "matrix_005_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 5: validator observes canonical read-only evidence and compares 4 registries against policy segment 5.",
    "bad_pattern": "bad pattern 48 in matrix 5: writer drift toward family 6, generated path reports_real/segment_5_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_5_48, boundary=bnd_matrix_5_48, switch=sw_matrix_5_48, hash_hint=df234e35c41b793e"
  },
  {
    "matrix_row_id": "matrix_005_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 5: validator observes canonical read-only evidence and compares 5 registries against policy segment 5.",
    "bad_pattern": "bad pattern 49 in matrix 5: writer drift toward family 0, generated path reports_real/segment_5_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_5_49, boundary=bnd_matrix_5_49, switch=sw_matrix_5_49, hash_hint=7782efc422e76b6e"
  },
  {
    "matrix_row_id": "matrix_005_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 5: validator observes canonical read-only evidence and compares 1 registries against policy segment 5.",
    "bad_pattern": "bad pattern 50 in matrix 5: writer drift toward family 1, generated path reports_real/segment_5_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_5_50, boundary=bnd_matrix_5_50, switch=sw_matrix_5_50, hash_hint=d5580ff12246e052"
  },
  {
    "matrix_row_id": "matrix_005_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 5: validator observes canonical read-only evidence and compares 2 registries against policy segment 5.",
    "bad_pattern": "bad pattern 51 in matrix 5: writer drift toward family 2, generated path reports_real/segment_5_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_5_51, boundary=bnd_matrix_5_51, switch=sw_matrix_5_51, hash_hint=e167a42400b501aa"
  },
  {
    "matrix_row_id": "matrix_005_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 5: validator observes canonical read-only evidence and compares 3 registries against policy segment 5.",
    "bad_pattern": "bad pattern 52 in matrix 5: writer drift toward family 3, generated path reports_real/segment_5_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_5_52, boundary=bnd_matrix_5_52, switch=sw_matrix_5_52, hash_hint=56f5e84eb60044b9"
  },
  {
    "matrix_row_id": "matrix_005_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 5: validator observes canonical read-only evidence and compares 4 registries against policy segment 5.",
    "bad_pattern": "bad pattern 53 in matrix 5: writer drift toward family 4, generated path reports_real/segment_5_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_5_53, boundary=bnd_matrix_5_53, switch=sw_matrix_5_53, hash_hint=ef4ee8ce96a29584"
  },
  {
    "matrix_row_id": "matrix_005_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 5: validator observes canonical read-only evidence and compares 5 registries against policy segment 5.",
    "bad_pattern": "bad pattern 54 in matrix 5: writer drift toward family 5, generated path reports_real/segment_5_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_5_54, boundary=bnd_matrix_5_54, switch=sw_matrix_5_54, hash_hint=efa03a06260ecf3e"
  },
  {
    "matrix_row_id": "matrix_005_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 5: validator observes canonical read-only evidence and compares 1 registries against policy segment 5.",
    "bad_pattern": "bad pattern 55 in matrix 5: writer drift toward family 6, generated path reports_real/segment_5_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_5_55, boundary=bnd_matrix_5_55, switch=sw_matrix_5_55, hash_hint=afbcefa2274651a7"
  },
  {
    "matrix_row_id": "matrix_005_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 5: validator observes canonical read-only evidence and compares 2 registries against policy segment 5.",
    "bad_pattern": "bad pattern 56 in matrix 5: writer drift toward family 0, generated path reports_real/segment_5_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_5_56, boundary=bnd_matrix_5_56, switch=sw_matrix_5_56, hash_hint=6473bd84a2aa8ef2"
  },
  {
    "matrix_row_id": "matrix_005_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 5: validator observes canonical read-only evidence and compares 3 registries against policy segment 5.",
    "bad_pattern": "bad pattern 57 in matrix 5: writer drift toward family 1, generated path reports_real/segment_5_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_5_57, boundary=bnd_matrix_5_57, switch=sw_matrix_5_57, hash_hint=3ca9fac89ab9db1d"
  },
  {
    "matrix_row_id": "matrix_005_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 5: validator observes canonical read-only evidence and compares 4 registries against policy segment 5.",
    "bad_pattern": "bad pattern 58 in matrix 5: writer drift toward family 2, generated path reports_real/segment_5_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_5_58, boundary=bnd_matrix_5_58, switch=sw_matrix_5_58, hash_hint=21a7cf82046e33b0"
  },
  {
    "matrix_row_id": "matrix_005_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 5: validator observes canonical read-only evidence and compares 5 registries against policy segment 5.",
    "bad_pattern": "bad pattern 59 in matrix 5: writer drift toward family 3, generated path reports_real/segment_5_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_5_59, boundary=bnd_matrix_5_59, switch=sw_matrix_5_59, hash_hint=927b51a0287fd2b7"
  },
  {
    "matrix_row_id": "matrix_005_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 5: validator observes canonical read-only evidence and compares 1 registries against policy segment 5.",
    "bad_pattern": "bad pattern 60 in matrix 5: writer drift toward family 4, generated path reports_real/segment_5_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_5_60, boundary=bnd_matrix_5_60, switch=sw_matrix_5_60, hash_hint=b98d1552f19a8acd"
  }
]
