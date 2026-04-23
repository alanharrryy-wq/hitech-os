from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 24/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 24/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 24/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 24/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 24/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 24/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 24/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 24/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 24/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 24/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 24/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 24/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 24/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 24/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 24/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 24/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 24/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 24/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 24/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 24/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 24/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 24/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 24/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 24/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 24/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_024_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 24: validator observes canonical read-only evidence and compares 2 registries against policy segment 24.",
    "bad_pattern": "bad pattern 1 in matrix 24: writer drift toward family 1, generated path reports_real/segment_24_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_24_1, boundary=bnd_matrix_24_1, switch=sw_matrix_24_1, hash_hint=890e372db871843e"
  },
  {
    "matrix_row_id": "matrix_024_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 24: validator observes canonical read-only evidence and compares 3 registries against policy segment 24.",
    "bad_pattern": "bad pattern 2 in matrix 24: writer drift toward family 2, generated path reports_real/segment_24_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_24_2, boundary=bnd_matrix_24_2, switch=sw_matrix_24_2, hash_hint=c7266a48f4322a5d"
  },
  {
    "matrix_row_id": "matrix_024_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 24: validator observes canonical read-only evidence and compares 4 registries against policy segment 24.",
    "bad_pattern": "bad pattern 3 in matrix 24: writer drift toward family 3, generated path reports_real/segment_24_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_24_3, boundary=bnd_matrix_24_3, switch=sw_matrix_24_3, hash_hint=261762b7384036af"
  },
  {
    "matrix_row_id": "matrix_024_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 24: validator observes canonical read-only evidence and compares 5 registries against policy segment 24.",
    "bad_pattern": "bad pattern 4 in matrix 24: writer drift toward family 4, generated path reports_real/segment_24_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_24_4, boundary=bnd_matrix_24_4, switch=sw_matrix_24_4, hash_hint=33ebf4651f5eb976"
  },
  {
    "matrix_row_id": "matrix_024_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 24: validator observes canonical read-only evidence and compares 1 registries against policy segment 24.",
    "bad_pattern": "bad pattern 5 in matrix 24: writer drift toward family 5, generated path reports_real/segment_24_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_24_5, boundary=bnd_matrix_24_5, switch=sw_matrix_24_5, hash_hint=19996f79a4240a41"
  },
  {
    "matrix_row_id": "matrix_024_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 24: validator observes canonical read-only evidence and compares 2 registries against policy segment 24.",
    "bad_pattern": "bad pattern 6 in matrix 24: writer drift toward family 6, generated path reports_real/segment_24_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_24_6, boundary=bnd_matrix_24_6, switch=sw_matrix_24_6, hash_hint=4e6d455171698b27"
  },
  {
    "matrix_row_id": "matrix_024_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 24: validator observes canonical read-only evidence and compares 3 registries against policy segment 24.",
    "bad_pattern": "bad pattern 7 in matrix 24: writer drift toward family 0, generated path reports_real/segment_24_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_24_7, boundary=bnd_matrix_24_7, switch=sw_matrix_24_7, hash_hint=cf1f2398804892f4"
  },
  {
    "matrix_row_id": "matrix_024_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 24: validator observes canonical read-only evidence and compares 4 registries against policy segment 24.",
    "bad_pattern": "bad pattern 8 in matrix 24: writer drift toward family 1, generated path reports_real/segment_24_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_24_8, boundary=bnd_matrix_24_8, switch=sw_matrix_24_8, hash_hint=f1c0608f807716ba"
  },
  {
    "matrix_row_id": "matrix_024_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 24: validator observes canonical read-only evidence and compares 5 registries against policy segment 24.",
    "bad_pattern": "bad pattern 9 in matrix 24: writer drift toward family 2, generated path reports_real/segment_24_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_24_9, boundary=bnd_matrix_24_9, switch=sw_matrix_24_9, hash_hint=8892cb5551a1285a"
  },
  {
    "matrix_row_id": "matrix_024_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 24: validator observes canonical read-only evidence and compares 1 registries against policy segment 24.",
    "bad_pattern": "bad pattern 10 in matrix 24: writer drift toward family 3, generated path reports_real/segment_24_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_24_10, boundary=bnd_matrix_24_10, switch=sw_matrix_24_10, hash_hint=505c033547753717"
  },
  {
    "matrix_row_id": "matrix_024_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 24: validator observes canonical read-only evidence and compares 2 registries against policy segment 24.",
    "bad_pattern": "bad pattern 11 in matrix 24: writer drift toward family 4, generated path reports_real/segment_24_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_24_11, boundary=bnd_matrix_24_11, switch=sw_matrix_24_11, hash_hint=961450ca97c467e2"
  },
  {
    "matrix_row_id": "matrix_024_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 24: validator observes canonical read-only evidence and compares 3 registries against policy segment 24.",
    "bad_pattern": "bad pattern 12 in matrix 24: writer drift toward family 5, generated path reports_real/segment_24_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_24_12, boundary=bnd_matrix_24_12, switch=sw_matrix_24_12, hash_hint=85fbcdc60a7dae24"
  },
  {
    "matrix_row_id": "matrix_024_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 24: validator observes canonical read-only evidence and compares 4 registries against policy segment 24.",
    "bad_pattern": "bad pattern 13 in matrix 24: writer drift toward family 6, generated path reports_real/segment_24_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_24_13, boundary=bnd_matrix_24_13, switch=sw_matrix_24_13, hash_hint=30ceff514af1ef97"
  },
  {
    "matrix_row_id": "matrix_024_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 24: validator observes canonical read-only evidence and compares 5 registries against policy segment 24.",
    "bad_pattern": "bad pattern 14 in matrix 24: writer drift toward family 0, generated path reports_real/segment_24_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_24_14, boundary=bnd_matrix_24_14, switch=sw_matrix_24_14, hash_hint=60ff434804171031"
  },
  {
    "matrix_row_id": "matrix_024_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 24: validator observes canonical read-only evidence and compares 1 registries against policy segment 24.",
    "bad_pattern": "bad pattern 15 in matrix 24: writer drift toward family 1, generated path reports_real/segment_24_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_24_15, boundary=bnd_matrix_24_15, switch=sw_matrix_24_15, hash_hint=44051844ecdda848"
  },
  {
    "matrix_row_id": "matrix_024_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 24: validator observes canonical read-only evidence and compares 2 registries against policy segment 24.",
    "bad_pattern": "bad pattern 16 in matrix 24: writer drift toward family 2, generated path reports_real/segment_24_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_24_16, boundary=bnd_matrix_24_16, switch=sw_matrix_24_16, hash_hint=64506fe8e08997dc"
  },
  {
    "matrix_row_id": "matrix_024_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 24: validator observes canonical read-only evidence and compares 3 registries against policy segment 24.",
    "bad_pattern": "bad pattern 17 in matrix 24: writer drift toward family 3, generated path reports_real/segment_24_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_24_17, boundary=bnd_matrix_24_17, switch=sw_matrix_24_17, hash_hint=a8533148295121bd"
  },
  {
    "matrix_row_id": "matrix_024_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 24: validator observes canonical read-only evidence and compares 4 registries against policy segment 24.",
    "bad_pattern": "bad pattern 18 in matrix 24: writer drift toward family 4, generated path reports_real/segment_24_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_24_18, boundary=bnd_matrix_24_18, switch=sw_matrix_24_18, hash_hint=033eb23f881a2462"
  },
  {
    "matrix_row_id": "matrix_024_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 24: validator observes canonical read-only evidence and compares 5 registries against policy segment 24.",
    "bad_pattern": "bad pattern 19 in matrix 24: writer drift toward family 5, generated path reports_real/segment_24_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_24_19, boundary=bnd_matrix_24_19, switch=sw_matrix_24_19, hash_hint=953d4d2c9f19b544"
  },
  {
    "matrix_row_id": "matrix_024_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 24: validator observes canonical read-only evidence and compares 1 registries against policy segment 24.",
    "bad_pattern": "bad pattern 20 in matrix 24: writer drift toward family 6, generated path reports_real/segment_24_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_24_20, boundary=bnd_matrix_24_20, switch=sw_matrix_24_20, hash_hint=4c0e136793c77815"
  },
  {
    "matrix_row_id": "matrix_024_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 24: validator observes canonical read-only evidence and compares 2 registries against policy segment 24.",
    "bad_pattern": "bad pattern 21 in matrix 24: writer drift toward family 0, generated path reports_real/segment_24_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_24_21, boundary=bnd_matrix_24_21, switch=sw_matrix_24_21, hash_hint=781243685797edb8"
  },
  {
    "matrix_row_id": "matrix_024_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 24: validator observes canonical read-only evidence and compares 3 registries against policy segment 24.",
    "bad_pattern": "bad pattern 22 in matrix 24: writer drift toward family 1, generated path reports_real/segment_24_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_24_22, boundary=bnd_matrix_24_22, switch=sw_matrix_24_22, hash_hint=3d77932706553066"
  },
  {
    "matrix_row_id": "matrix_024_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 24: validator observes canonical read-only evidence and compares 4 registries against policy segment 24.",
    "bad_pattern": "bad pattern 23 in matrix 24: writer drift toward family 2, generated path reports_real/segment_24_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_24_23, boundary=bnd_matrix_24_23, switch=sw_matrix_24_23, hash_hint=1f08d37c9abe1b59"
  },
  {
    "matrix_row_id": "matrix_024_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 24: validator observes canonical read-only evidence and compares 5 registries against policy segment 24.",
    "bad_pattern": "bad pattern 24 in matrix 24: writer drift toward family 3, generated path reports_real/segment_24_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_24_24, boundary=bnd_matrix_24_24, switch=sw_matrix_24_24, hash_hint=31d6b9bdc38bd7ad"
  },
  {
    "matrix_row_id": "matrix_024_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 24: validator observes canonical read-only evidence and compares 1 registries against policy segment 24.",
    "bad_pattern": "bad pattern 25 in matrix 24: writer drift toward family 4, generated path reports_real/segment_24_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_24_25, boundary=bnd_matrix_24_25, switch=sw_matrix_24_25, hash_hint=76fcb0a1ddc4cb91"
  },
  {
    "matrix_row_id": "matrix_024_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 24: validator observes canonical read-only evidence and compares 2 registries against policy segment 24.",
    "bad_pattern": "bad pattern 26 in matrix 24: writer drift toward family 5, generated path reports_real/segment_24_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_24_26, boundary=bnd_matrix_24_26, switch=sw_matrix_24_26, hash_hint=31353a88eee8401a"
  },
  {
    "matrix_row_id": "matrix_024_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 24: validator observes canonical read-only evidence and compares 3 registries against policy segment 24.",
    "bad_pattern": "bad pattern 27 in matrix 24: writer drift toward family 6, generated path reports_real/segment_24_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_24_27, boundary=bnd_matrix_24_27, switch=sw_matrix_24_27, hash_hint=789a339864421d39"
  },
  {
    "matrix_row_id": "matrix_024_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 24: validator observes canonical read-only evidence and compares 4 registries against policy segment 24.",
    "bad_pattern": "bad pattern 28 in matrix 24: writer drift toward family 0, generated path reports_real/segment_24_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_24_28, boundary=bnd_matrix_24_28, switch=sw_matrix_24_28, hash_hint=e7deed12666fb27d"
  },
  {
    "matrix_row_id": "matrix_024_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 24: validator observes canonical read-only evidence and compares 5 registries against policy segment 24.",
    "bad_pattern": "bad pattern 29 in matrix 24: writer drift toward family 1, generated path reports_real/segment_24_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_24_29, boundary=bnd_matrix_24_29, switch=sw_matrix_24_29, hash_hint=ea5d2a0157f528e8"
  },
  {
    "matrix_row_id": "matrix_024_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 24: validator observes canonical read-only evidence and compares 1 registries against policy segment 24.",
    "bad_pattern": "bad pattern 30 in matrix 24: writer drift toward family 2, generated path reports_real/segment_24_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_24_30, boundary=bnd_matrix_24_30, switch=sw_matrix_24_30, hash_hint=d7ae5ed8af695d85"
  },
  {
    "matrix_row_id": "matrix_024_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 24: validator observes canonical read-only evidence and compares 2 registries against policy segment 24.",
    "bad_pattern": "bad pattern 31 in matrix 24: writer drift toward family 3, generated path reports_real/segment_24_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_24_31, boundary=bnd_matrix_24_31, switch=sw_matrix_24_31, hash_hint=ae4e7fbfd141d67f"
  },
  {
    "matrix_row_id": "matrix_024_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 24: validator observes canonical read-only evidence and compares 3 registries against policy segment 24.",
    "bad_pattern": "bad pattern 32 in matrix 24: writer drift toward family 4, generated path reports_real/segment_24_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_24_32, boundary=bnd_matrix_24_32, switch=sw_matrix_24_32, hash_hint=867ea112195ebde4"
  },
  {
    "matrix_row_id": "matrix_024_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 24: validator observes canonical read-only evidence and compares 4 registries against policy segment 24.",
    "bad_pattern": "bad pattern 33 in matrix 24: writer drift toward family 5, generated path reports_real/segment_24_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_24_33, boundary=bnd_matrix_24_33, switch=sw_matrix_24_33, hash_hint=31d703f24e4c3da3"
  },
  {
    "matrix_row_id": "matrix_024_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 24: validator observes canonical read-only evidence and compares 5 registries against policy segment 24.",
    "bad_pattern": "bad pattern 34 in matrix 24: writer drift toward family 6, generated path reports_real/segment_24_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_24_34, boundary=bnd_matrix_24_34, switch=sw_matrix_24_34, hash_hint=5ac12b271fcdd527"
  },
  {
    "matrix_row_id": "matrix_024_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 24: validator observes canonical read-only evidence and compares 1 registries against policy segment 24.",
    "bad_pattern": "bad pattern 35 in matrix 24: writer drift toward family 0, generated path reports_real/segment_24_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_24_35, boundary=bnd_matrix_24_35, switch=sw_matrix_24_35, hash_hint=a0dae8afe802dc40"
  },
  {
    "matrix_row_id": "matrix_024_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 24: validator observes canonical read-only evidence and compares 2 registries against policy segment 24.",
    "bad_pattern": "bad pattern 36 in matrix 24: writer drift toward family 1, generated path reports_real/segment_24_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_24_36, boundary=bnd_matrix_24_36, switch=sw_matrix_24_36, hash_hint=ee55c930e868a7a8"
  },
  {
    "matrix_row_id": "matrix_024_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 24: validator observes canonical read-only evidence and compares 3 registries against policy segment 24.",
    "bad_pattern": "bad pattern 37 in matrix 24: writer drift toward family 2, generated path reports_real/segment_24_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_24_37, boundary=bnd_matrix_24_37, switch=sw_matrix_24_37, hash_hint=9b5a600c05154610"
  },
  {
    "matrix_row_id": "matrix_024_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 24: validator observes canonical read-only evidence and compares 4 registries against policy segment 24.",
    "bad_pattern": "bad pattern 38 in matrix 24: writer drift toward family 3, generated path reports_real/segment_24_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_24_38, boundary=bnd_matrix_24_38, switch=sw_matrix_24_38, hash_hint=24f6769beb859657"
  },
  {
    "matrix_row_id": "matrix_024_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 24: validator observes canonical read-only evidence and compares 5 registries against policy segment 24.",
    "bad_pattern": "bad pattern 39 in matrix 24: writer drift toward family 4, generated path reports_real/segment_24_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_24_39, boundary=bnd_matrix_24_39, switch=sw_matrix_24_39, hash_hint=daab142fba824265"
  },
  {
    "matrix_row_id": "matrix_024_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 24: validator observes canonical read-only evidence and compares 1 registries against policy segment 24.",
    "bad_pattern": "bad pattern 40 in matrix 24: writer drift toward family 5, generated path reports_real/segment_24_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_24_40, boundary=bnd_matrix_24_40, switch=sw_matrix_24_40, hash_hint=57c0cc42775b25de"
  },
  {
    "matrix_row_id": "matrix_024_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 24: validator observes canonical read-only evidence and compares 2 registries against policy segment 24.",
    "bad_pattern": "bad pattern 41 in matrix 24: writer drift toward family 6, generated path reports_real/segment_24_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_24_41, boundary=bnd_matrix_24_41, switch=sw_matrix_24_41, hash_hint=85ac5a05b69e97ad"
  },
  {
    "matrix_row_id": "matrix_024_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 24: validator observes canonical read-only evidence and compares 3 registries against policy segment 24.",
    "bad_pattern": "bad pattern 42 in matrix 24: writer drift toward family 0, generated path reports_real/segment_24_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_24_42, boundary=bnd_matrix_24_42, switch=sw_matrix_24_42, hash_hint=2bae8c65d7e0fa79"
  },
  {
    "matrix_row_id": "matrix_024_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 24: validator observes canonical read-only evidence and compares 4 registries against policy segment 24.",
    "bad_pattern": "bad pattern 43 in matrix 24: writer drift toward family 1, generated path reports_real/segment_24_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_24_43, boundary=bnd_matrix_24_43, switch=sw_matrix_24_43, hash_hint=15a1946abdb7c61b"
  },
  {
    "matrix_row_id": "matrix_024_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 24: validator observes canonical read-only evidence and compares 5 registries against policy segment 24.",
    "bad_pattern": "bad pattern 44 in matrix 24: writer drift toward family 2, generated path reports_real/segment_24_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_24_44, boundary=bnd_matrix_24_44, switch=sw_matrix_24_44, hash_hint=d5df196ed54b3267"
  },
  {
    "matrix_row_id": "matrix_024_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 24: validator observes canonical read-only evidence and compares 1 registries against policy segment 24.",
    "bad_pattern": "bad pattern 45 in matrix 24: writer drift toward family 3, generated path reports_real/segment_24_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_24_45, boundary=bnd_matrix_24_45, switch=sw_matrix_24_45, hash_hint=76f8b225fe55921c"
  },
  {
    "matrix_row_id": "matrix_024_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 24: validator observes canonical read-only evidence and compares 2 registries against policy segment 24.",
    "bad_pattern": "bad pattern 46 in matrix 24: writer drift toward family 4, generated path reports_real/segment_24_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_24_46, boundary=bnd_matrix_24_46, switch=sw_matrix_24_46, hash_hint=1354fb63a0246b61"
  },
  {
    "matrix_row_id": "matrix_024_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 24: validator observes canonical read-only evidence and compares 3 registries against policy segment 24.",
    "bad_pattern": "bad pattern 47 in matrix 24: writer drift toward family 5, generated path reports_real/segment_24_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_24_47, boundary=bnd_matrix_24_47, switch=sw_matrix_24_47, hash_hint=2a862ea271c279b4"
  },
  {
    "matrix_row_id": "matrix_024_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 24: validator observes canonical read-only evidence and compares 4 registries against policy segment 24.",
    "bad_pattern": "bad pattern 48 in matrix 24: writer drift toward family 6, generated path reports_real/segment_24_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_24_48, boundary=bnd_matrix_24_48, switch=sw_matrix_24_48, hash_hint=9da0bd6e268c5457"
  },
  {
    "matrix_row_id": "matrix_024_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 24: validator observes canonical read-only evidence and compares 5 registries against policy segment 24.",
    "bad_pattern": "bad pattern 49 in matrix 24: writer drift toward family 0, generated path reports_real/segment_24_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_24_49, boundary=bnd_matrix_24_49, switch=sw_matrix_24_49, hash_hint=2829ead6f35aa155"
  },
  {
    "matrix_row_id": "matrix_024_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 24: validator observes canonical read-only evidence and compares 1 registries against policy segment 24.",
    "bad_pattern": "bad pattern 50 in matrix 24: writer drift toward family 1, generated path reports_real/segment_24_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_24_50, boundary=bnd_matrix_24_50, switch=sw_matrix_24_50, hash_hint=6ea3698688370432"
  },
  {
    "matrix_row_id": "matrix_024_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 24: validator observes canonical read-only evidence and compares 2 registries against policy segment 24.",
    "bad_pattern": "bad pattern 51 in matrix 24: writer drift toward family 2, generated path reports_real/segment_24_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_24_51, boundary=bnd_matrix_24_51, switch=sw_matrix_24_51, hash_hint=e53c83adb9910860"
  },
  {
    "matrix_row_id": "matrix_024_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 24: validator observes canonical read-only evidence and compares 3 registries against policy segment 24.",
    "bad_pattern": "bad pattern 52 in matrix 24: writer drift toward family 3, generated path reports_real/segment_24_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_24_52, boundary=bnd_matrix_24_52, switch=sw_matrix_24_52, hash_hint=3359d9a3adfbf74e"
  },
  {
    "matrix_row_id": "matrix_024_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 24: validator observes canonical read-only evidence and compares 4 registries against policy segment 24.",
    "bad_pattern": "bad pattern 53 in matrix 24: writer drift toward family 4, generated path reports_real/segment_24_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_24_53, boundary=bnd_matrix_24_53, switch=sw_matrix_24_53, hash_hint=51472213430ece7f"
  },
  {
    "matrix_row_id": "matrix_024_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 24: validator observes canonical read-only evidence and compares 5 registries against policy segment 24.",
    "bad_pattern": "bad pattern 54 in matrix 24: writer drift toward family 5, generated path reports_real/segment_24_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_24_54, boundary=bnd_matrix_24_54, switch=sw_matrix_24_54, hash_hint=c9ae7f6c5bf9ad30"
  },
  {
    "matrix_row_id": "matrix_024_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 24: validator observes canonical read-only evidence and compares 1 registries against policy segment 24.",
    "bad_pattern": "bad pattern 55 in matrix 24: writer drift toward family 6, generated path reports_real/segment_24_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_24_55, boundary=bnd_matrix_24_55, switch=sw_matrix_24_55, hash_hint=86c5e09e701c07d6"
  },
  {
    "matrix_row_id": "matrix_024_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 24: validator observes canonical read-only evidence and compares 2 registries against policy segment 24.",
    "bad_pattern": "bad pattern 56 in matrix 24: writer drift toward family 0, generated path reports_real/segment_24_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_24_56, boundary=bnd_matrix_24_56, switch=sw_matrix_24_56, hash_hint=1ec39c16afc6ad91"
  },
  {
    "matrix_row_id": "matrix_024_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 24: validator observes canonical read-only evidence and compares 3 registries against policy segment 24.",
    "bad_pattern": "bad pattern 57 in matrix 24: writer drift toward family 1, generated path reports_real/segment_24_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_24_57, boundary=bnd_matrix_24_57, switch=sw_matrix_24_57, hash_hint=d9dbc5ef7c8a664b"
  },
  {
    "matrix_row_id": "matrix_024_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 24: validator observes canonical read-only evidence and compares 4 registries against policy segment 24.",
    "bad_pattern": "bad pattern 58 in matrix 24: writer drift toward family 2, generated path reports_real/segment_24_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_24_58, boundary=bnd_matrix_24_58, switch=sw_matrix_24_58, hash_hint=3543c64d381dba18"
  },
  {
    "matrix_row_id": "matrix_024_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 24: validator observes canonical read-only evidence and compares 5 registries against policy segment 24.",
    "bad_pattern": "bad pattern 59 in matrix 24: writer drift toward family 3, generated path reports_real/segment_24_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_24_59, boundary=bnd_matrix_24_59, switch=sw_matrix_24_59, hash_hint=6bd5e54547055fee"
  },
  {
    "matrix_row_id": "matrix_024_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 24: validator observes canonical read-only evidence and compares 1 registries against policy segment 24.",
    "bad_pattern": "bad pattern 60 in matrix 24: writer drift toward family 4, generated path reports_real/segment_24_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_24_60, boundary=bnd_matrix_24_60, switch=sw_matrix_24_60, hash_hint=b3814ebb9f53fb29"
  }
]
