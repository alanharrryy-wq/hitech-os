from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 29/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 29/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 29/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 29/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 29/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 29/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 29/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 29/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 29/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 29/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 29/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 29/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 29/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 29/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 29/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 29/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 29/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 29/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 29/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 29/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 29/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 29/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 29/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 29/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 29/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_029_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 29: validator observes canonical read-only evidence and compares 2 registries against policy segment 29.",
    "bad_pattern": "bad pattern 1 in matrix 29: writer drift toward family 1, generated path reports_real/segment_29_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_29_1, boundary=bnd_matrix_29_1, switch=sw_matrix_29_1, hash_hint=0b2364cee0117c0c"
  },
  {
    "matrix_row_id": "matrix_029_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 29: validator observes canonical read-only evidence and compares 3 registries against policy segment 29.",
    "bad_pattern": "bad pattern 2 in matrix 29: writer drift toward family 2, generated path reports_real/segment_29_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_29_2, boundary=bnd_matrix_29_2, switch=sw_matrix_29_2, hash_hint=ae51097f09db3b93"
  },
  {
    "matrix_row_id": "matrix_029_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 29: validator observes canonical read-only evidence and compares 4 registries against policy segment 29.",
    "bad_pattern": "bad pattern 3 in matrix 29: writer drift toward family 3, generated path reports_real/segment_29_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_29_3, boundary=bnd_matrix_29_3, switch=sw_matrix_29_3, hash_hint=59f67dcaf04270a1"
  },
  {
    "matrix_row_id": "matrix_029_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 29: validator observes canonical read-only evidence and compares 5 registries against policy segment 29.",
    "bad_pattern": "bad pattern 4 in matrix 29: writer drift toward family 4, generated path reports_real/segment_29_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_29_4, boundary=bnd_matrix_29_4, switch=sw_matrix_29_4, hash_hint=68c1061adc3d8777"
  },
  {
    "matrix_row_id": "matrix_029_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 29: validator observes canonical read-only evidence and compares 1 registries against policy segment 29.",
    "bad_pattern": "bad pattern 5 in matrix 29: writer drift toward family 5, generated path reports_real/segment_29_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_29_5, boundary=bnd_matrix_29_5, switch=sw_matrix_29_5, hash_hint=08884545f1c1949c"
  },
  {
    "matrix_row_id": "matrix_029_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 29: validator observes canonical read-only evidence and compares 2 registries against policy segment 29.",
    "bad_pattern": "bad pattern 6 in matrix 29: writer drift toward family 6, generated path reports_real/segment_29_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_29_6, boundary=bnd_matrix_29_6, switch=sw_matrix_29_6, hash_hint=f4c58df615fceee8"
  },
  {
    "matrix_row_id": "matrix_029_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 29: validator observes canonical read-only evidence and compares 3 registries against policy segment 29.",
    "bad_pattern": "bad pattern 7 in matrix 29: writer drift toward family 0, generated path reports_real/segment_29_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_29_7, boundary=bnd_matrix_29_7, switch=sw_matrix_29_7, hash_hint=b9404fad865fbcf0"
  },
  {
    "matrix_row_id": "matrix_029_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 29: validator observes canonical read-only evidence and compares 4 registries against policy segment 29.",
    "bad_pattern": "bad pattern 8 in matrix 29: writer drift toward family 1, generated path reports_real/segment_29_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_29_8, boundary=bnd_matrix_29_8, switch=sw_matrix_29_8, hash_hint=6ed42f345960ac80"
  },
  {
    "matrix_row_id": "matrix_029_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 29: validator observes canonical read-only evidence and compares 5 registries against policy segment 29.",
    "bad_pattern": "bad pattern 9 in matrix 29: writer drift toward family 2, generated path reports_real/segment_29_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_29_9, boundary=bnd_matrix_29_9, switch=sw_matrix_29_9, hash_hint=3dd779e0baaa14e7"
  },
  {
    "matrix_row_id": "matrix_029_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 29: validator observes canonical read-only evidence and compares 1 registries against policy segment 29.",
    "bad_pattern": "bad pattern 10 in matrix 29: writer drift toward family 3, generated path reports_real/segment_29_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_29_10, boundary=bnd_matrix_29_10, switch=sw_matrix_29_10, hash_hint=4bda239407a13be6"
  },
  {
    "matrix_row_id": "matrix_029_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 29: validator observes canonical read-only evidence and compares 2 registries against policy segment 29.",
    "bad_pattern": "bad pattern 11 in matrix 29: writer drift toward family 4, generated path reports_real/segment_29_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_29_11, boundary=bnd_matrix_29_11, switch=sw_matrix_29_11, hash_hint=eb3aac639356f62d"
  },
  {
    "matrix_row_id": "matrix_029_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 29: validator observes canonical read-only evidence and compares 3 registries against policy segment 29.",
    "bad_pattern": "bad pattern 12 in matrix 29: writer drift toward family 5, generated path reports_real/segment_29_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_29_12, boundary=bnd_matrix_29_12, switch=sw_matrix_29_12, hash_hint=4156880f52292a86"
  },
  {
    "matrix_row_id": "matrix_029_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 29: validator observes canonical read-only evidence and compares 4 registries against policy segment 29.",
    "bad_pattern": "bad pattern 13 in matrix 29: writer drift toward family 6, generated path reports_real/segment_29_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_29_13, boundary=bnd_matrix_29_13, switch=sw_matrix_29_13, hash_hint=d0ea23e317c6b8a0"
  },
  {
    "matrix_row_id": "matrix_029_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 29: validator observes canonical read-only evidence and compares 5 registries against policy segment 29.",
    "bad_pattern": "bad pattern 14 in matrix 29: writer drift toward family 0, generated path reports_real/segment_29_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_29_14, boundary=bnd_matrix_29_14, switch=sw_matrix_29_14, hash_hint=cc53579a7e7db376"
  },
  {
    "matrix_row_id": "matrix_029_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 29: validator observes canonical read-only evidence and compares 1 registries against policy segment 29.",
    "bad_pattern": "bad pattern 15 in matrix 29: writer drift toward family 1, generated path reports_real/segment_29_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_29_15, boundary=bnd_matrix_29_15, switch=sw_matrix_29_15, hash_hint=c751e3887d6ffac0"
  },
  {
    "matrix_row_id": "matrix_029_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 29: validator observes canonical read-only evidence and compares 2 registries against policy segment 29.",
    "bad_pattern": "bad pattern 16 in matrix 29: writer drift toward family 2, generated path reports_real/segment_29_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_29_16, boundary=bnd_matrix_29_16, switch=sw_matrix_29_16, hash_hint=e0f6e77e5e5a4c62"
  },
  {
    "matrix_row_id": "matrix_029_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 29: validator observes canonical read-only evidence and compares 3 registries against policy segment 29.",
    "bad_pattern": "bad pattern 17 in matrix 29: writer drift toward family 3, generated path reports_real/segment_29_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_29_17, boundary=bnd_matrix_29_17, switch=sw_matrix_29_17, hash_hint=6eca6f7f07203eed"
  },
  {
    "matrix_row_id": "matrix_029_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 29: validator observes canonical read-only evidence and compares 4 registries against policy segment 29.",
    "bad_pattern": "bad pattern 18 in matrix 29: writer drift toward family 4, generated path reports_real/segment_29_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_29_18, boundary=bnd_matrix_29_18, switch=sw_matrix_29_18, hash_hint=da07a02539141b3a"
  },
  {
    "matrix_row_id": "matrix_029_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 29: validator observes canonical read-only evidence and compares 5 registries against policy segment 29.",
    "bad_pattern": "bad pattern 19 in matrix 29: writer drift toward family 5, generated path reports_real/segment_29_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_29_19, boundary=bnd_matrix_29_19, switch=sw_matrix_29_19, hash_hint=2510cbe7c2a89866"
  },
  {
    "matrix_row_id": "matrix_029_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 29: validator observes canonical read-only evidence and compares 1 registries against policy segment 29.",
    "bad_pattern": "bad pattern 20 in matrix 29: writer drift toward family 6, generated path reports_real/segment_29_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_29_20, boundary=bnd_matrix_29_20, switch=sw_matrix_29_20, hash_hint=126152e924818cfa"
  },
  {
    "matrix_row_id": "matrix_029_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 29: validator observes canonical read-only evidence and compares 2 registries against policy segment 29.",
    "bad_pattern": "bad pattern 21 in matrix 29: writer drift toward family 0, generated path reports_real/segment_29_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_29_21, boundary=bnd_matrix_29_21, switch=sw_matrix_29_21, hash_hint=6bc50797cd9661bc"
  },
  {
    "matrix_row_id": "matrix_029_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 29: validator observes canonical read-only evidence and compares 3 registries against policy segment 29.",
    "bad_pattern": "bad pattern 22 in matrix 29: writer drift toward family 1, generated path reports_real/segment_29_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_29_22, boundary=bnd_matrix_29_22, switch=sw_matrix_29_22, hash_hint=f55d1aaf31f2e257"
  },
  {
    "matrix_row_id": "matrix_029_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 29: validator observes canonical read-only evidence and compares 4 registries against policy segment 29.",
    "bad_pattern": "bad pattern 23 in matrix 29: writer drift toward family 2, generated path reports_real/segment_29_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_29_23, boundary=bnd_matrix_29_23, switch=sw_matrix_29_23, hash_hint=28ac12e9991f02a6"
  },
  {
    "matrix_row_id": "matrix_029_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 29: validator observes canonical read-only evidence and compares 5 registries against policy segment 29.",
    "bad_pattern": "bad pattern 24 in matrix 29: writer drift toward family 3, generated path reports_real/segment_29_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_29_24, boundary=bnd_matrix_29_24, switch=sw_matrix_29_24, hash_hint=e890c1f4478cf982"
  },
  {
    "matrix_row_id": "matrix_029_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 29: validator observes canonical read-only evidence and compares 1 registries against policy segment 29.",
    "bad_pattern": "bad pattern 25 in matrix 29: writer drift toward family 4, generated path reports_real/segment_29_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_29_25, boundary=bnd_matrix_29_25, switch=sw_matrix_29_25, hash_hint=67610fb2852b48ab"
  },
  {
    "matrix_row_id": "matrix_029_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 29: validator observes canonical read-only evidence and compares 2 registries against policy segment 29.",
    "bad_pattern": "bad pattern 26 in matrix 29: writer drift toward family 5, generated path reports_real/segment_29_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_29_26, boundary=bnd_matrix_29_26, switch=sw_matrix_29_26, hash_hint=a438bbbc85ccaf9d"
  },
  {
    "matrix_row_id": "matrix_029_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 29: validator observes canonical read-only evidence and compares 3 registries against policy segment 29.",
    "bad_pattern": "bad pattern 27 in matrix 29: writer drift toward family 6, generated path reports_real/segment_29_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_29_27, boundary=bnd_matrix_29_27, switch=sw_matrix_29_27, hash_hint=0dbc9ae0e9228665"
  },
  {
    "matrix_row_id": "matrix_029_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 29: validator observes canonical read-only evidence and compares 4 registries against policy segment 29.",
    "bad_pattern": "bad pattern 28 in matrix 29: writer drift toward family 0, generated path reports_real/segment_29_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_29_28, boundary=bnd_matrix_29_28, switch=sw_matrix_29_28, hash_hint=748ee7c2bb5c3703"
  },
  {
    "matrix_row_id": "matrix_029_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 29: validator observes canonical read-only evidence and compares 5 registries against policy segment 29.",
    "bad_pattern": "bad pattern 29 in matrix 29: writer drift toward family 1, generated path reports_real/segment_29_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_29_29, boundary=bnd_matrix_29_29, switch=sw_matrix_29_29, hash_hint=a7fee5ad7aad1827"
  },
  {
    "matrix_row_id": "matrix_029_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 29: validator observes canonical read-only evidence and compares 1 registries against policy segment 29.",
    "bad_pattern": "bad pattern 30 in matrix 29: writer drift toward family 2, generated path reports_real/segment_29_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_29_30, boundary=bnd_matrix_29_30, switch=sw_matrix_29_30, hash_hint=a309065ac5c0b479"
  },
  {
    "matrix_row_id": "matrix_029_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 29: validator observes canonical read-only evidence and compares 2 registries against policy segment 29.",
    "bad_pattern": "bad pattern 31 in matrix 29: writer drift toward family 3, generated path reports_real/segment_29_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_29_31, boundary=bnd_matrix_29_31, switch=sw_matrix_29_31, hash_hint=a1a5606b804e5017"
  },
  {
    "matrix_row_id": "matrix_029_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 29: validator observes canonical read-only evidence and compares 3 registries against policy segment 29.",
    "bad_pattern": "bad pattern 32 in matrix 29: writer drift toward family 4, generated path reports_real/segment_29_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_29_32, boundary=bnd_matrix_29_32, switch=sw_matrix_29_32, hash_hint=843ee25ff2cc1b24"
  },
  {
    "matrix_row_id": "matrix_029_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 29: validator observes canonical read-only evidence and compares 4 registries against policy segment 29.",
    "bad_pattern": "bad pattern 33 in matrix 29: writer drift toward family 5, generated path reports_real/segment_29_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_29_33, boundary=bnd_matrix_29_33, switch=sw_matrix_29_33, hash_hint=4e31c21bdf1511f8"
  },
  {
    "matrix_row_id": "matrix_029_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 29: validator observes canonical read-only evidence and compares 5 registries against policy segment 29.",
    "bad_pattern": "bad pattern 34 in matrix 29: writer drift toward family 6, generated path reports_real/segment_29_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_29_34, boundary=bnd_matrix_29_34, switch=sw_matrix_29_34, hash_hint=db13304c907daaad"
  },
  {
    "matrix_row_id": "matrix_029_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 29: validator observes canonical read-only evidence and compares 1 registries against policy segment 29.",
    "bad_pattern": "bad pattern 35 in matrix 29: writer drift toward family 0, generated path reports_real/segment_29_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_29_35, boundary=bnd_matrix_29_35, switch=sw_matrix_29_35, hash_hint=93a124f69c456278"
  },
  {
    "matrix_row_id": "matrix_029_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 29: validator observes canonical read-only evidence and compares 2 registries against policy segment 29.",
    "bad_pattern": "bad pattern 36 in matrix 29: writer drift toward family 1, generated path reports_real/segment_29_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_29_36, boundary=bnd_matrix_29_36, switch=sw_matrix_29_36, hash_hint=5001cfca9e3029fc"
  },
  {
    "matrix_row_id": "matrix_029_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 29: validator observes canonical read-only evidence and compares 3 registries against policy segment 29.",
    "bad_pattern": "bad pattern 37 in matrix 29: writer drift toward family 2, generated path reports_real/segment_29_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_29_37, boundary=bnd_matrix_29_37, switch=sw_matrix_29_37, hash_hint=060d494948fd1e88"
  },
  {
    "matrix_row_id": "matrix_029_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 29: validator observes canonical read-only evidence and compares 4 registries against policy segment 29.",
    "bad_pattern": "bad pattern 38 in matrix 29: writer drift toward family 3, generated path reports_real/segment_29_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_29_38, boundary=bnd_matrix_29_38, switch=sw_matrix_29_38, hash_hint=c7f0b8da811e3837"
  },
  {
    "matrix_row_id": "matrix_029_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 29: validator observes canonical read-only evidence and compares 5 registries against policy segment 29.",
    "bad_pattern": "bad pattern 39 in matrix 29: writer drift toward family 4, generated path reports_real/segment_29_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_29_39, boundary=bnd_matrix_29_39, switch=sw_matrix_29_39, hash_hint=43a669059c4f5b18"
  },
  {
    "matrix_row_id": "matrix_029_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 29: validator observes canonical read-only evidence and compares 1 registries against policy segment 29.",
    "bad_pattern": "bad pattern 40 in matrix 29: writer drift toward family 5, generated path reports_real/segment_29_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_29_40, boundary=bnd_matrix_29_40, switch=sw_matrix_29_40, hash_hint=17b9b9af98999d67"
  },
  {
    "matrix_row_id": "matrix_029_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 29: validator observes canonical read-only evidence and compares 2 registries against policy segment 29.",
    "bad_pattern": "bad pattern 41 in matrix 29: writer drift toward family 6, generated path reports_real/segment_29_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_29_41, boundary=bnd_matrix_29_41, switch=sw_matrix_29_41, hash_hint=a9acacae9b8b2d9c"
  },
  {
    "matrix_row_id": "matrix_029_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 29: validator observes canonical read-only evidence and compares 3 registries against policy segment 29.",
    "bad_pattern": "bad pattern 42 in matrix 29: writer drift toward family 0, generated path reports_real/segment_29_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_29_42, boundary=bnd_matrix_29_42, switch=sw_matrix_29_42, hash_hint=e82fa69fdcc41023"
  },
  {
    "matrix_row_id": "matrix_029_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 29: validator observes canonical read-only evidence and compares 4 registries against policy segment 29.",
    "bad_pattern": "bad pattern 43 in matrix 29: writer drift toward family 1, generated path reports_real/segment_29_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_29_43, boundary=bnd_matrix_29_43, switch=sw_matrix_29_43, hash_hint=de672cde3b37ab52"
  },
  {
    "matrix_row_id": "matrix_029_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 29: validator observes canonical read-only evidence and compares 5 registries against policy segment 29.",
    "bad_pattern": "bad pattern 44 in matrix 29: writer drift toward family 2, generated path reports_real/segment_29_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_29_44, boundary=bnd_matrix_29_44, switch=sw_matrix_29_44, hash_hint=9d404f5eda1714f6"
  },
  {
    "matrix_row_id": "matrix_029_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 29: validator observes canonical read-only evidence and compares 1 registries against policy segment 29.",
    "bad_pattern": "bad pattern 45 in matrix 29: writer drift toward family 3, generated path reports_real/segment_29_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_29_45, boundary=bnd_matrix_29_45, switch=sw_matrix_29_45, hash_hint=80e3181b47e58433"
  },
  {
    "matrix_row_id": "matrix_029_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 29: validator observes canonical read-only evidence and compares 2 registries against policy segment 29.",
    "bad_pattern": "bad pattern 46 in matrix 29: writer drift toward family 4, generated path reports_real/segment_29_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_29_46, boundary=bnd_matrix_29_46, switch=sw_matrix_29_46, hash_hint=a3355d5242a8325e"
  },
  {
    "matrix_row_id": "matrix_029_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 29: validator observes canonical read-only evidence and compares 3 registries against policy segment 29.",
    "bad_pattern": "bad pattern 47 in matrix 29: writer drift toward family 5, generated path reports_real/segment_29_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_29_47, boundary=bnd_matrix_29_47, switch=sw_matrix_29_47, hash_hint=3da3683ad0d82666"
  },
  {
    "matrix_row_id": "matrix_029_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 29: validator observes canonical read-only evidence and compares 4 registries against policy segment 29.",
    "bad_pattern": "bad pattern 48 in matrix 29: writer drift toward family 6, generated path reports_real/segment_29_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_29_48, boundary=bnd_matrix_29_48, switch=sw_matrix_29_48, hash_hint=746a03a10c4c69a5"
  },
  {
    "matrix_row_id": "matrix_029_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 29: validator observes canonical read-only evidence and compares 5 registries against policy segment 29.",
    "bad_pattern": "bad pattern 49 in matrix 29: writer drift toward family 0, generated path reports_real/segment_29_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_29_49, boundary=bnd_matrix_29_49, switch=sw_matrix_29_49, hash_hint=c464e52550535922"
  },
  {
    "matrix_row_id": "matrix_029_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 29: validator observes canonical read-only evidence and compares 1 registries against policy segment 29.",
    "bad_pattern": "bad pattern 50 in matrix 29: writer drift toward family 1, generated path reports_real/segment_29_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_29_50, boundary=bnd_matrix_29_50, switch=sw_matrix_29_50, hash_hint=e19713573f8fcfa5"
  },
  {
    "matrix_row_id": "matrix_029_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 29: validator observes canonical read-only evidence and compares 2 registries against policy segment 29.",
    "bad_pattern": "bad pattern 51 in matrix 29: writer drift toward family 2, generated path reports_real/segment_29_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_29_51, boundary=bnd_matrix_29_51, switch=sw_matrix_29_51, hash_hint=274139662274d8eb"
  },
  {
    "matrix_row_id": "matrix_029_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 29: validator observes canonical read-only evidence and compares 3 registries against policy segment 29.",
    "bad_pattern": "bad pattern 52 in matrix 29: writer drift toward family 3, generated path reports_real/segment_29_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_29_52, boundary=bnd_matrix_29_52, switch=sw_matrix_29_52, hash_hint=fc570be93a92d809"
  },
  {
    "matrix_row_id": "matrix_029_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 29: validator observes canonical read-only evidence and compares 4 registries against policy segment 29.",
    "bad_pattern": "bad pattern 53 in matrix 29: writer drift toward family 4, generated path reports_real/segment_29_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_29_53, boundary=bnd_matrix_29_53, switch=sw_matrix_29_53, hash_hint=3995d6ecd00d2c1a"
  },
  {
    "matrix_row_id": "matrix_029_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 29: validator observes canonical read-only evidence and compares 5 registries against policy segment 29.",
    "bad_pattern": "bad pattern 54 in matrix 29: writer drift toward family 5, generated path reports_real/segment_29_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_29_54, boundary=bnd_matrix_29_54, switch=sw_matrix_29_54, hash_hint=ffe5327de594e254"
  },
  {
    "matrix_row_id": "matrix_029_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 29: validator observes canonical read-only evidence and compares 1 registries against policy segment 29.",
    "bad_pattern": "bad pattern 55 in matrix 29: writer drift toward family 6, generated path reports_real/segment_29_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_29_55, boundary=bnd_matrix_29_55, switch=sw_matrix_29_55, hash_hint=8b21136b034f9a16"
  },
  {
    "matrix_row_id": "matrix_029_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 29: validator observes canonical read-only evidence and compares 2 registries against policy segment 29.",
    "bad_pattern": "bad pattern 56 in matrix 29: writer drift toward family 0, generated path reports_real/segment_29_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_29_56, boundary=bnd_matrix_29_56, switch=sw_matrix_29_56, hash_hint=eac8aac9e70ce02e"
  },
  {
    "matrix_row_id": "matrix_029_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 29: validator observes canonical read-only evidence and compares 3 registries against policy segment 29.",
    "bad_pattern": "bad pattern 57 in matrix 29: writer drift toward family 1, generated path reports_real/segment_29_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_29_57, boundary=bnd_matrix_29_57, switch=sw_matrix_29_57, hash_hint=518e1a691ee1676d"
  },
  {
    "matrix_row_id": "matrix_029_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 29: validator observes canonical read-only evidence and compares 4 registries against policy segment 29.",
    "bad_pattern": "bad pattern 58 in matrix 29: writer drift toward family 2, generated path reports_real/segment_29_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_29_58, boundary=bnd_matrix_29_58, switch=sw_matrix_29_58, hash_hint=afb94ecfa2ba8a33"
  },
  {
    "matrix_row_id": "matrix_029_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 29: validator observes canonical read-only evidence and compares 5 registries against policy segment 29.",
    "bad_pattern": "bad pattern 59 in matrix 29: writer drift toward family 3, generated path reports_real/segment_29_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_29_59, boundary=bnd_matrix_29_59, switch=sw_matrix_29_59, hash_hint=65d1b3097a01a78e"
  },
  {
    "matrix_row_id": "matrix_029_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 29: validator observes canonical read-only evidence and compares 1 registries against policy segment 29.",
    "bad_pattern": "bad pattern 60 in matrix 29: writer drift toward family 4, generated path reports_real/segment_29_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_29_60, boundary=bnd_matrix_29_60, switch=sw_matrix_29_60, hash_hint=2b15ba303e9dc2ab"
  }
]
