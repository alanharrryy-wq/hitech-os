from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 10/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 10/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 10/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 10/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 10/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 10/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 10/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 10/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 10/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 10/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 10/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 10/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 10/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 10/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 10/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 10/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 10/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 10/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 10/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 10/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 10/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 10/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 10/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 10/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 10/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_010_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 10: validator observes canonical read-only evidence and compares 2 registries against policy segment 10.",
    "bad_pattern": "bad pattern 1 in matrix 10: writer drift toward family 1, generated path reports_real/segment_10_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_10_1, boundary=bnd_matrix_10_1, switch=sw_matrix_10_1, hash_hint=34fa1bd4097c6e05"
  },
  {
    "matrix_row_id": "matrix_010_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 10: validator observes canonical read-only evidence and compares 3 registries against policy segment 10.",
    "bad_pattern": "bad pattern 2 in matrix 10: writer drift toward family 2, generated path reports_real/segment_10_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_10_2, boundary=bnd_matrix_10_2, switch=sw_matrix_10_2, hash_hint=f7f945300491d86d"
  },
  {
    "matrix_row_id": "matrix_010_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 10: validator observes canonical read-only evidence and compares 4 registries against policy segment 10.",
    "bad_pattern": "bad pattern 3 in matrix 10: writer drift toward family 3, generated path reports_real/segment_10_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_10_3, boundary=bnd_matrix_10_3, switch=sw_matrix_10_3, hash_hint=2f0305aa95aa8374"
  },
  {
    "matrix_row_id": "matrix_010_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 10: validator observes canonical read-only evidence and compares 5 registries against policy segment 10.",
    "bad_pattern": "bad pattern 4 in matrix 10: writer drift toward family 4, generated path reports_real/segment_10_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_10_4, boundary=bnd_matrix_10_4, switch=sw_matrix_10_4, hash_hint=c77c559684cb6c5b"
  },
  {
    "matrix_row_id": "matrix_010_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 10: validator observes canonical read-only evidence and compares 1 registries against policy segment 10.",
    "bad_pattern": "bad pattern 5 in matrix 10: writer drift toward family 5, generated path reports_real/segment_10_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_10_5, boundary=bnd_matrix_10_5, switch=sw_matrix_10_5, hash_hint=0dde5d0e9bcc6bd7"
  },
  {
    "matrix_row_id": "matrix_010_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 10: validator observes canonical read-only evidence and compares 2 registries against policy segment 10.",
    "bad_pattern": "bad pattern 6 in matrix 10: writer drift toward family 6, generated path reports_real/segment_10_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_10_6, boundary=bnd_matrix_10_6, switch=sw_matrix_10_6, hash_hint=4b040f122144fb1a"
  },
  {
    "matrix_row_id": "matrix_010_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 10: validator observes canonical read-only evidence and compares 3 registries against policy segment 10.",
    "bad_pattern": "bad pattern 7 in matrix 10: writer drift toward family 0, generated path reports_real/segment_10_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_10_7, boundary=bnd_matrix_10_7, switch=sw_matrix_10_7, hash_hint=e100c8b17a2219ab"
  },
  {
    "matrix_row_id": "matrix_010_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 10: validator observes canonical read-only evidence and compares 4 registries against policy segment 10.",
    "bad_pattern": "bad pattern 8 in matrix 10: writer drift toward family 1, generated path reports_real/segment_10_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_10_8, boundary=bnd_matrix_10_8, switch=sw_matrix_10_8, hash_hint=927c527c2206c6dd"
  },
  {
    "matrix_row_id": "matrix_010_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 10: validator observes canonical read-only evidence and compares 5 registries against policy segment 10.",
    "bad_pattern": "bad pattern 9 in matrix 10: writer drift toward family 2, generated path reports_real/segment_10_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_10_9, boundary=bnd_matrix_10_9, switch=sw_matrix_10_9, hash_hint=e7a8e40def191cbb"
  },
  {
    "matrix_row_id": "matrix_010_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 10: validator observes canonical read-only evidence and compares 1 registries against policy segment 10.",
    "bad_pattern": "bad pattern 10 in matrix 10: writer drift toward family 3, generated path reports_real/segment_10_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_10_10, boundary=bnd_matrix_10_10, switch=sw_matrix_10_10, hash_hint=f2e070bea1a8296f"
  },
  {
    "matrix_row_id": "matrix_010_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 10: validator observes canonical read-only evidence and compares 2 registries against policy segment 10.",
    "bad_pattern": "bad pattern 11 in matrix 10: writer drift toward family 4, generated path reports_real/segment_10_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_10_11, boundary=bnd_matrix_10_11, switch=sw_matrix_10_11, hash_hint=45da1b666c9edd5a"
  },
  {
    "matrix_row_id": "matrix_010_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 10: validator observes canonical read-only evidence and compares 3 registries against policy segment 10.",
    "bad_pattern": "bad pattern 12 in matrix 10: writer drift toward family 5, generated path reports_real/segment_10_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_10_12, boundary=bnd_matrix_10_12, switch=sw_matrix_10_12, hash_hint=a26003943b87356c"
  },
  {
    "matrix_row_id": "matrix_010_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 10: validator observes canonical read-only evidence and compares 4 registries against policy segment 10.",
    "bad_pattern": "bad pattern 13 in matrix 10: writer drift toward family 6, generated path reports_real/segment_10_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_10_13, boundary=bnd_matrix_10_13, switch=sw_matrix_10_13, hash_hint=0d4bddd65c4c9b10"
  },
  {
    "matrix_row_id": "matrix_010_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 10: validator observes canonical read-only evidence and compares 5 registries against policy segment 10.",
    "bad_pattern": "bad pattern 14 in matrix 10: writer drift toward family 0, generated path reports_real/segment_10_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_10_14, boundary=bnd_matrix_10_14, switch=sw_matrix_10_14, hash_hint=18df583fbd69d5a2"
  },
  {
    "matrix_row_id": "matrix_010_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 10: validator observes canonical read-only evidence and compares 1 registries against policy segment 10.",
    "bad_pattern": "bad pattern 15 in matrix 10: writer drift toward family 1, generated path reports_real/segment_10_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_10_15, boundary=bnd_matrix_10_15, switch=sw_matrix_10_15, hash_hint=c3f1f4d000861fda"
  },
  {
    "matrix_row_id": "matrix_010_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 10: validator observes canonical read-only evidence and compares 2 registries against policy segment 10.",
    "bad_pattern": "bad pattern 16 in matrix 10: writer drift toward family 2, generated path reports_real/segment_10_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_10_16, boundary=bnd_matrix_10_16, switch=sw_matrix_10_16, hash_hint=dbb965f35b0b1cd1"
  },
  {
    "matrix_row_id": "matrix_010_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 10: validator observes canonical read-only evidence and compares 3 registries against policy segment 10.",
    "bad_pattern": "bad pattern 17 in matrix 10: writer drift toward family 3, generated path reports_real/segment_10_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_10_17, boundary=bnd_matrix_10_17, switch=sw_matrix_10_17, hash_hint=75ef72ac256b70f9"
  },
  {
    "matrix_row_id": "matrix_010_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 10: validator observes canonical read-only evidence and compares 4 registries against policy segment 10.",
    "bad_pattern": "bad pattern 18 in matrix 10: writer drift toward family 4, generated path reports_real/segment_10_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_10_18, boundary=bnd_matrix_10_18, switch=sw_matrix_10_18, hash_hint=69d85fd6e56c2fd2"
  },
  {
    "matrix_row_id": "matrix_010_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 10: validator observes canonical read-only evidence and compares 5 registries against policy segment 10.",
    "bad_pattern": "bad pattern 19 in matrix 10: writer drift toward family 5, generated path reports_real/segment_10_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_10_19, boundary=bnd_matrix_10_19, switch=sw_matrix_10_19, hash_hint=c7bad5513e192780"
  },
  {
    "matrix_row_id": "matrix_010_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 10: validator observes canonical read-only evidence and compares 1 registries against policy segment 10.",
    "bad_pattern": "bad pattern 20 in matrix 10: writer drift toward family 6, generated path reports_real/segment_10_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_10_20, boundary=bnd_matrix_10_20, switch=sw_matrix_10_20, hash_hint=0096ce93d667b7fd"
  },
  {
    "matrix_row_id": "matrix_010_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 10: validator observes canonical read-only evidence and compares 2 registries against policy segment 10.",
    "bad_pattern": "bad pattern 21 in matrix 10: writer drift toward family 0, generated path reports_real/segment_10_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_10_21, boundary=bnd_matrix_10_21, switch=sw_matrix_10_21, hash_hint=6f026ced2a7b7d61"
  },
  {
    "matrix_row_id": "matrix_010_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 10: validator observes canonical read-only evidence and compares 3 registries against policy segment 10.",
    "bad_pattern": "bad pattern 22 in matrix 10: writer drift toward family 1, generated path reports_real/segment_10_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_10_22, boundary=bnd_matrix_10_22, switch=sw_matrix_10_22, hash_hint=db49b60e83e0946a"
  },
  {
    "matrix_row_id": "matrix_010_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 10: validator observes canonical read-only evidence and compares 4 registries against policy segment 10.",
    "bad_pattern": "bad pattern 23 in matrix 10: writer drift toward family 2, generated path reports_real/segment_10_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_10_23, boundary=bnd_matrix_10_23, switch=sw_matrix_10_23, hash_hint=bd2d4735b6844209"
  },
  {
    "matrix_row_id": "matrix_010_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 10: validator observes canonical read-only evidence and compares 5 registries against policy segment 10.",
    "bad_pattern": "bad pattern 24 in matrix 10: writer drift toward family 3, generated path reports_real/segment_10_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_10_24, boundary=bnd_matrix_10_24, switch=sw_matrix_10_24, hash_hint=b019157cb071d2ae"
  },
  {
    "matrix_row_id": "matrix_010_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 10: validator observes canonical read-only evidence and compares 1 registries against policy segment 10.",
    "bad_pattern": "bad pattern 25 in matrix 10: writer drift toward family 4, generated path reports_real/segment_10_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_10_25, boundary=bnd_matrix_10_25, switch=sw_matrix_10_25, hash_hint=0b29e79b7bba4d8b"
  },
  {
    "matrix_row_id": "matrix_010_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 10: validator observes canonical read-only evidence and compares 2 registries against policy segment 10.",
    "bad_pattern": "bad pattern 26 in matrix 10: writer drift toward family 5, generated path reports_real/segment_10_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_10_26, boundary=bnd_matrix_10_26, switch=sw_matrix_10_26, hash_hint=214762444fc75e23"
  },
  {
    "matrix_row_id": "matrix_010_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 10: validator observes canonical read-only evidence and compares 3 registries against policy segment 10.",
    "bad_pattern": "bad pattern 27 in matrix 10: writer drift toward family 6, generated path reports_real/segment_10_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_10_27, boundary=bnd_matrix_10_27, switch=sw_matrix_10_27, hash_hint=f448c6407467af4d"
  },
  {
    "matrix_row_id": "matrix_010_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 10: validator observes canonical read-only evidence and compares 4 registries against policy segment 10.",
    "bad_pattern": "bad pattern 28 in matrix 10: writer drift toward family 0, generated path reports_real/segment_10_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_10_28, boundary=bnd_matrix_10_28, switch=sw_matrix_10_28, hash_hint=6ada94ba74452c64"
  },
  {
    "matrix_row_id": "matrix_010_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 10: validator observes canonical read-only evidence and compares 5 registries against policy segment 10.",
    "bad_pattern": "bad pattern 29 in matrix 10: writer drift toward family 1, generated path reports_real/segment_10_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_10_29, boundary=bnd_matrix_10_29, switch=sw_matrix_10_29, hash_hint=6e4baed9cc8f396d"
  },
  {
    "matrix_row_id": "matrix_010_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 10: validator observes canonical read-only evidence and compares 1 registries against policy segment 10.",
    "bad_pattern": "bad pattern 30 in matrix 10: writer drift toward family 2, generated path reports_real/segment_10_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_10_30, boundary=bnd_matrix_10_30, switch=sw_matrix_10_30, hash_hint=c839754017a2a3fa"
  },
  {
    "matrix_row_id": "matrix_010_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 10: validator observes canonical read-only evidence and compares 2 registries against policy segment 10.",
    "bad_pattern": "bad pattern 31 in matrix 10: writer drift toward family 3, generated path reports_real/segment_10_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_10_31, boundary=bnd_matrix_10_31, switch=sw_matrix_10_31, hash_hint=a44a7402f60cd079"
  },
  {
    "matrix_row_id": "matrix_010_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 10: validator observes canonical read-only evidence and compares 3 registries against policy segment 10.",
    "bad_pattern": "bad pattern 32 in matrix 10: writer drift toward family 4, generated path reports_real/segment_10_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_10_32, boundary=bnd_matrix_10_32, switch=sw_matrix_10_32, hash_hint=1424b1deb92bf383"
  },
  {
    "matrix_row_id": "matrix_010_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 10: validator observes canonical read-only evidence and compares 4 registries against policy segment 10.",
    "bad_pattern": "bad pattern 33 in matrix 10: writer drift toward family 5, generated path reports_real/segment_10_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_10_33, boundary=bnd_matrix_10_33, switch=sw_matrix_10_33, hash_hint=9319609a5f479a0d"
  },
  {
    "matrix_row_id": "matrix_010_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 10: validator observes canonical read-only evidence and compares 5 registries against policy segment 10.",
    "bad_pattern": "bad pattern 34 in matrix 10: writer drift toward family 6, generated path reports_real/segment_10_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_10_34, boundary=bnd_matrix_10_34, switch=sw_matrix_10_34, hash_hint=2fa37f0ed302896f"
  },
  {
    "matrix_row_id": "matrix_010_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 10: validator observes canonical read-only evidence and compares 1 registries against policy segment 10.",
    "bad_pattern": "bad pattern 35 in matrix 10: writer drift toward family 0, generated path reports_real/segment_10_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_10_35, boundary=bnd_matrix_10_35, switch=sw_matrix_10_35, hash_hint=9e133cb3bbbbdadc"
  },
  {
    "matrix_row_id": "matrix_010_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 10: validator observes canonical read-only evidence and compares 2 registries against policy segment 10.",
    "bad_pattern": "bad pattern 36 in matrix 10: writer drift toward family 1, generated path reports_real/segment_10_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_10_36, boundary=bnd_matrix_10_36, switch=sw_matrix_10_36, hash_hint=cb3ff2952907ddb3"
  },
  {
    "matrix_row_id": "matrix_010_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 10: validator observes canonical read-only evidence and compares 3 registries against policy segment 10.",
    "bad_pattern": "bad pattern 37 in matrix 10: writer drift toward family 2, generated path reports_real/segment_10_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_10_37, boundary=bnd_matrix_10_37, switch=sw_matrix_10_37, hash_hint=5ca36f4b0439bc08"
  },
  {
    "matrix_row_id": "matrix_010_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 10: validator observes canonical read-only evidence and compares 4 registries against policy segment 10.",
    "bad_pattern": "bad pattern 38 in matrix 10: writer drift toward family 3, generated path reports_real/segment_10_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_10_38, boundary=bnd_matrix_10_38, switch=sw_matrix_10_38, hash_hint=94e3715f885924b2"
  },
  {
    "matrix_row_id": "matrix_010_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 10: validator observes canonical read-only evidence and compares 5 registries against policy segment 10.",
    "bad_pattern": "bad pattern 39 in matrix 10: writer drift toward family 4, generated path reports_real/segment_10_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_10_39, boundary=bnd_matrix_10_39, switch=sw_matrix_10_39, hash_hint=37b4877a7f4a8ad4"
  },
  {
    "matrix_row_id": "matrix_010_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 10: validator observes canonical read-only evidence and compares 1 registries against policy segment 10.",
    "bad_pattern": "bad pattern 40 in matrix 10: writer drift toward family 5, generated path reports_real/segment_10_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_10_40, boundary=bnd_matrix_10_40, switch=sw_matrix_10_40, hash_hint=c9e027f325858c52"
  },
  {
    "matrix_row_id": "matrix_010_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 10: validator observes canonical read-only evidence and compares 2 registries against policy segment 10.",
    "bad_pattern": "bad pattern 41 in matrix 10: writer drift toward family 6, generated path reports_real/segment_10_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_10_41, boundary=bnd_matrix_10_41, switch=sw_matrix_10_41, hash_hint=0fe46b075d8be857"
  },
  {
    "matrix_row_id": "matrix_010_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 10: validator observes canonical read-only evidence and compares 3 registries against policy segment 10.",
    "bad_pattern": "bad pattern 42 in matrix 10: writer drift toward family 0, generated path reports_real/segment_10_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_10_42, boundary=bnd_matrix_10_42, switch=sw_matrix_10_42, hash_hint=141acf3afa468541"
  },
  {
    "matrix_row_id": "matrix_010_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 10: validator observes canonical read-only evidence and compares 4 registries against policy segment 10.",
    "bad_pattern": "bad pattern 43 in matrix 10: writer drift toward family 1, generated path reports_real/segment_10_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_10_43, boundary=bnd_matrix_10_43, switch=sw_matrix_10_43, hash_hint=40d17c6c99510027"
  },
  {
    "matrix_row_id": "matrix_010_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 10: validator observes canonical read-only evidence and compares 5 registries against policy segment 10.",
    "bad_pattern": "bad pattern 44 in matrix 10: writer drift toward family 2, generated path reports_real/segment_10_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_10_44, boundary=bnd_matrix_10_44, switch=sw_matrix_10_44, hash_hint=a79e5634f6d99df4"
  },
  {
    "matrix_row_id": "matrix_010_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 10: validator observes canonical read-only evidence and compares 1 registries against policy segment 10.",
    "bad_pattern": "bad pattern 45 in matrix 10: writer drift toward family 3, generated path reports_real/segment_10_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_10_45, boundary=bnd_matrix_10_45, switch=sw_matrix_10_45, hash_hint=ffd4a8fcae8d6bc6"
  },
  {
    "matrix_row_id": "matrix_010_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 10: validator observes canonical read-only evidence and compares 2 registries against policy segment 10.",
    "bad_pattern": "bad pattern 46 in matrix 10: writer drift toward family 4, generated path reports_real/segment_10_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_10_46, boundary=bnd_matrix_10_46, switch=sw_matrix_10_46, hash_hint=413c86d2a6a84e27"
  },
  {
    "matrix_row_id": "matrix_010_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 10: validator observes canonical read-only evidence and compares 3 registries against policy segment 10.",
    "bad_pattern": "bad pattern 47 in matrix 10: writer drift toward family 5, generated path reports_real/segment_10_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_10_47, boundary=bnd_matrix_10_47, switch=sw_matrix_10_47, hash_hint=029308c20dc59af1"
  },
  {
    "matrix_row_id": "matrix_010_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 10: validator observes canonical read-only evidence and compares 4 registries against policy segment 10.",
    "bad_pattern": "bad pattern 48 in matrix 10: writer drift toward family 6, generated path reports_real/segment_10_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_10_48, boundary=bnd_matrix_10_48, switch=sw_matrix_10_48, hash_hint=263eba21f412ba4a"
  },
  {
    "matrix_row_id": "matrix_010_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 10: validator observes canonical read-only evidence and compares 5 registries against policy segment 10.",
    "bad_pattern": "bad pattern 49 in matrix 10: writer drift toward family 0, generated path reports_real/segment_10_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_10_49, boundary=bnd_matrix_10_49, switch=sw_matrix_10_49, hash_hint=5362bb16829dc072"
  },
  {
    "matrix_row_id": "matrix_010_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 10: validator observes canonical read-only evidence and compares 1 registries against policy segment 10.",
    "bad_pattern": "bad pattern 50 in matrix 10: writer drift toward family 1, generated path reports_real/segment_10_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_10_50, boundary=bnd_matrix_10_50, switch=sw_matrix_10_50, hash_hint=9366a12c418085a8"
  },
  {
    "matrix_row_id": "matrix_010_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 10: validator observes canonical read-only evidence and compares 2 registries against policy segment 10.",
    "bad_pattern": "bad pattern 51 in matrix 10: writer drift toward family 2, generated path reports_real/segment_10_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_10_51, boundary=bnd_matrix_10_51, switch=sw_matrix_10_51, hash_hint=0daca394ce5dcd7b"
  },
  {
    "matrix_row_id": "matrix_010_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 10: validator observes canonical read-only evidence and compares 3 registries against policy segment 10.",
    "bad_pattern": "bad pattern 52 in matrix 10: writer drift toward family 3, generated path reports_real/segment_10_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_10_52, boundary=bnd_matrix_10_52, switch=sw_matrix_10_52, hash_hint=4e6c142be57b822b"
  },
  {
    "matrix_row_id": "matrix_010_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 10: validator observes canonical read-only evidence and compares 4 registries against policy segment 10.",
    "bad_pattern": "bad pattern 53 in matrix 10: writer drift toward family 4, generated path reports_real/segment_10_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_10_53, boundary=bnd_matrix_10_53, switch=sw_matrix_10_53, hash_hint=a3c805b4e8b8820b"
  },
  {
    "matrix_row_id": "matrix_010_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 10: validator observes canonical read-only evidence and compares 5 registries against policy segment 10.",
    "bad_pattern": "bad pattern 54 in matrix 10: writer drift toward family 5, generated path reports_real/segment_10_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_10_54, boundary=bnd_matrix_10_54, switch=sw_matrix_10_54, hash_hint=eac9c80f7bbd44a5"
  },
  {
    "matrix_row_id": "matrix_010_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 10: validator observes canonical read-only evidence and compares 1 registries against policy segment 10.",
    "bad_pattern": "bad pattern 55 in matrix 10: writer drift toward family 6, generated path reports_real/segment_10_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_10_55, boundary=bnd_matrix_10_55, switch=sw_matrix_10_55, hash_hint=99d0aff5fb77acc6"
  },
  {
    "matrix_row_id": "matrix_010_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 10: validator observes canonical read-only evidence and compares 2 registries against policy segment 10.",
    "bad_pattern": "bad pattern 56 in matrix 10: writer drift toward family 0, generated path reports_real/segment_10_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_10_56, boundary=bnd_matrix_10_56, switch=sw_matrix_10_56, hash_hint=123b3bcd1d5efed7"
  },
  {
    "matrix_row_id": "matrix_010_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 10: validator observes canonical read-only evidence and compares 3 registries against policy segment 10.",
    "bad_pattern": "bad pattern 57 in matrix 10: writer drift toward family 1, generated path reports_real/segment_10_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_10_57, boundary=bnd_matrix_10_57, switch=sw_matrix_10_57, hash_hint=a67757c1303ed100"
  },
  {
    "matrix_row_id": "matrix_010_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 10: validator observes canonical read-only evidence and compares 4 registries against policy segment 10.",
    "bad_pattern": "bad pattern 58 in matrix 10: writer drift toward family 2, generated path reports_real/segment_10_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_10_58, boundary=bnd_matrix_10_58, switch=sw_matrix_10_58, hash_hint=bb6c4d06214c08cf"
  },
  {
    "matrix_row_id": "matrix_010_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 10: validator observes canonical read-only evidence and compares 5 registries against policy segment 10.",
    "bad_pattern": "bad pattern 59 in matrix 10: writer drift toward family 3, generated path reports_real/segment_10_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_10_59, boundary=bnd_matrix_10_59, switch=sw_matrix_10_59, hash_hint=ec8a151050dc5e51"
  },
  {
    "matrix_row_id": "matrix_010_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 10: validator observes canonical read-only evidence and compares 1 registries against policy segment 10.",
    "bad_pattern": "bad pattern 60 in matrix 10: writer drift toward family 4, generated path reports_real/segment_10_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_10_60, boundary=bnd_matrix_10_60, switch=sw_matrix_10_60, hash_hint=1b7b3f773efb67f1"
  }
]
