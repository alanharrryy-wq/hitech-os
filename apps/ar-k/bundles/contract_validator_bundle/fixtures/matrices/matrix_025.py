from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 25/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 25/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 25/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 25/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 25/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 25/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 25/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 25/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 25/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 25/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 25/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 25/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 25/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 25/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 25/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 25/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 25/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 25/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 25/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 25/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 25/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 25/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 25/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 25/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 25/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_025_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 25: validator observes canonical read-only evidence and compares 2 registries against policy segment 25.",
    "bad_pattern": "bad pattern 1 in matrix 25: writer drift toward family 1, generated path reports_real/segment_25_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_25_1, boundary=bnd_matrix_25_1, switch=sw_matrix_25_1, hash_hint=b9638ec5c046f5db"
  },
  {
    "matrix_row_id": "matrix_025_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 25: validator observes canonical read-only evidence and compares 3 registries against policy segment 25.",
    "bad_pattern": "bad pattern 2 in matrix 25: writer drift toward family 2, generated path reports_real/segment_25_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_25_2, boundary=bnd_matrix_25_2, switch=sw_matrix_25_2, hash_hint=79807d7071d6dc0c"
  },
  {
    "matrix_row_id": "matrix_025_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 25: validator observes canonical read-only evidence and compares 4 registries against policy segment 25.",
    "bad_pattern": "bad pattern 3 in matrix 25: writer drift toward family 3, generated path reports_real/segment_25_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_25_3, boundary=bnd_matrix_25_3, switch=sw_matrix_25_3, hash_hint=8c05fc02a95e5da3"
  },
  {
    "matrix_row_id": "matrix_025_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 25: validator observes canonical read-only evidence and compares 5 registries against policy segment 25.",
    "bad_pattern": "bad pattern 4 in matrix 25: writer drift toward family 4, generated path reports_real/segment_25_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_25_4, boundary=bnd_matrix_25_4, switch=sw_matrix_25_4, hash_hint=3bbb6bffa5d71fd0"
  },
  {
    "matrix_row_id": "matrix_025_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 25: validator observes canonical read-only evidence and compares 1 registries against policy segment 25.",
    "bad_pattern": "bad pattern 5 in matrix 25: writer drift toward family 5, generated path reports_real/segment_25_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_25_5, boundary=bnd_matrix_25_5, switch=sw_matrix_25_5, hash_hint=9fca919ce5232786"
  },
  {
    "matrix_row_id": "matrix_025_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 25: validator observes canonical read-only evidence and compares 2 registries against policy segment 25.",
    "bad_pattern": "bad pattern 6 in matrix 25: writer drift toward family 6, generated path reports_real/segment_25_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_25_6, boundary=bnd_matrix_25_6, switch=sw_matrix_25_6, hash_hint=1c210f203a707481"
  },
  {
    "matrix_row_id": "matrix_025_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 25: validator observes canonical read-only evidence and compares 3 registries against policy segment 25.",
    "bad_pattern": "bad pattern 7 in matrix 25: writer drift toward family 0, generated path reports_real/segment_25_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_25_7, boundary=bnd_matrix_25_7, switch=sw_matrix_25_7, hash_hint=db755d7a1fa3e5d5"
  },
  {
    "matrix_row_id": "matrix_025_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 25: validator observes canonical read-only evidence and compares 4 registries against policy segment 25.",
    "bad_pattern": "bad pattern 8 in matrix 25: writer drift toward family 1, generated path reports_real/segment_25_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_25_8, boundary=bnd_matrix_25_8, switch=sw_matrix_25_8, hash_hint=f7328b8160b87b96"
  },
  {
    "matrix_row_id": "matrix_025_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 25: validator observes canonical read-only evidence and compares 5 registries against policy segment 25.",
    "bad_pattern": "bad pattern 9 in matrix 25: writer drift toward family 2, generated path reports_real/segment_25_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_25_9, boundary=bnd_matrix_25_9, switch=sw_matrix_25_9, hash_hint=11286217257852bb"
  },
  {
    "matrix_row_id": "matrix_025_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 25: validator observes canonical read-only evidence and compares 1 registries against policy segment 25.",
    "bad_pattern": "bad pattern 10 in matrix 25: writer drift toward family 3, generated path reports_real/segment_25_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_25_10, boundary=bnd_matrix_25_10, switch=sw_matrix_25_10, hash_hint=e99d24b097a0488b"
  },
  {
    "matrix_row_id": "matrix_025_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 25: validator observes canonical read-only evidence and compares 2 registries against policy segment 25.",
    "bad_pattern": "bad pattern 11 in matrix 25: writer drift toward family 4, generated path reports_real/segment_25_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_25_11, boundary=bnd_matrix_25_11, switch=sw_matrix_25_11, hash_hint=f705277d4f183393"
  },
  {
    "matrix_row_id": "matrix_025_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 25: validator observes canonical read-only evidence and compares 3 registries against policy segment 25.",
    "bad_pattern": "bad pattern 12 in matrix 25: writer drift toward family 5, generated path reports_real/segment_25_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_25_12, boundary=bnd_matrix_25_12, switch=sw_matrix_25_12, hash_hint=7f963f9df04bc0c0"
  },
  {
    "matrix_row_id": "matrix_025_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 25: validator observes canonical read-only evidence and compares 4 registries against policy segment 25.",
    "bad_pattern": "bad pattern 13 in matrix 25: writer drift toward family 6, generated path reports_real/segment_25_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_25_13, boundary=bnd_matrix_25_13, switch=sw_matrix_25_13, hash_hint=0af2e901566a400c"
  },
  {
    "matrix_row_id": "matrix_025_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 25: validator observes canonical read-only evidence and compares 5 registries against policy segment 25.",
    "bad_pattern": "bad pattern 14 in matrix 25: writer drift toward family 0, generated path reports_real/segment_25_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_25_14, boundary=bnd_matrix_25_14, switch=sw_matrix_25_14, hash_hint=4cf67093d42c4cb3"
  },
  {
    "matrix_row_id": "matrix_025_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 25: validator observes canonical read-only evidence and compares 1 registries against policy segment 25.",
    "bad_pattern": "bad pattern 15 in matrix 25: writer drift toward family 1, generated path reports_real/segment_25_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_25_15, boundary=bnd_matrix_25_15, switch=sw_matrix_25_15, hash_hint=c3cef843a73aabde"
  },
  {
    "matrix_row_id": "matrix_025_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 25: validator observes canonical read-only evidence and compares 2 registries against policy segment 25.",
    "bad_pattern": "bad pattern 16 in matrix 25: writer drift toward family 2, generated path reports_real/segment_25_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_25_16, boundary=bnd_matrix_25_16, switch=sw_matrix_25_16, hash_hint=9acabf783dcc44e9"
  },
  {
    "matrix_row_id": "matrix_025_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 25: validator observes canonical read-only evidence and compares 3 registries against policy segment 25.",
    "bad_pattern": "bad pattern 17 in matrix 25: writer drift toward family 3, generated path reports_real/segment_25_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_25_17, boundary=bnd_matrix_25_17, switch=sw_matrix_25_17, hash_hint=88dadb7cb4b8d7bd"
  },
  {
    "matrix_row_id": "matrix_025_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 25: validator observes canonical read-only evidence and compares 4 registries against policy segment 25.",
    "bad_pattern": "bad pattern 18 in matrix 25: writer drift toward family 4, generated path reports_real/segment_25_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_25_18, boundary=bnd_matrix_25_18, switch=sw_matrix_25_18, hash_hint=6a69e6a4d77733a7"
  },
  {
    "matrix_row_id": "matrix_025_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 25: validator observes canonical read-only evidence and compares 5 registries against policy segment 25.",
    "bad_pattern": "bad pattern 19 in matrix 25: writer drift toward family 5, generated path reports_real/segment_25_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_25_19, boundary=bnd_matrix_25_19, switch=sw_matrix_25_19, hash_hint=b5c13e3dc4f3dba9"
  },
  {
    "matrix_row_id": "matrix_025_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 25: validator observes canonical read-only evidence and compares 1 registries against policy segment 25.",
    "bad_pattern": "bad pattern 20 in matrix 25: writer drift toward family 6, generated path reports_real/segment_25_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_25_20, boundary=bnd_matrix_25_20, switch=sw_matrix_25_20, hash_hint=037ec039c6080cd2"
  },
  {
    "matrix_row_id": "matrix_025_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 25: validator observes canonical read-only evidence and compares 2 registries against policy segment 25.",
    "bad_pattern": "bad pattern 21 in matrix 25: writer drift toward family 0, generated path reports_real/segment_25_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_25_21, boundary=bnd_matrix_25_21, switch=sw_matrix_25_21, hash_hint=173dfacedb485cd5"
  },
  {
    "matrix_row_id": "matrix_025_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 25: validator observes canonical read-only evidence and compares 3 registries against policy segment 25.",
    "bad_pattern": "bad pattern 22 in matrix 25: writer drift toward family 1, generated path reports_real/segment_25_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_25_22, boundary=bnd_matrix_25_22, switch=sw_matrix_25_22, hash_hint=ea2f1ada3d3576de"
  },
  {
    "matrix_row_id": "matrix_025_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 25: validator observes canonical read-only evidence and compares 4 registries against policy segment 25.",
    "bad_pattern": "bad pattern 23 in matrix 25: writer drift toward family 2, generated path reports_real/segment_25_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_25_23, boundary=bnd_matrix_25_23, switch=sw_matrix_25_23, hash_hint=027ff77569d68fa8"
  },
  {
    "matrix_row_id": "matrix_025_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 25: validator observes canonical read-only evidence and compares 5 registries against policy segment 25.",
    "bad_pattern": "bad pattern 24 in matrix 25: writer drift toward family 3, generated path reports_real/segment_25_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_25_24, boundary=bnd_matrix_25_24, switch=sw_matrix_25_24, hash_hint=fea6130de71c650c"
  },
  {
    "matrix_row_id": "matrix_025_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 25: validator observes canonical read-only evidence and compares 1 registries against policy segment 25.",
    "bad_pattern": "bad pattern 25 in matrix 25: writer drift toward family 4, generated path reports_real/segment_25_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_25_25, boundary=bnd_matrix_25_25, switch=sw_matrix_25_25, hash_hint=1261671fa289b420"
  },
  {
    "matrix_row_id": "matrix_025_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 25: validator observes canonical read-only evidence and compares 2 registries against policy segment 25.",
    "bad_pattern": "bad pattern 26 in matrix 25: writer drift toward family 5, generated path reports_real/segment_25_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_25_26, boundary=bnd_matrix_25_26, switch=sw_matrix_25_26, hash_hint=8b91855ad371492c"
  },
  {
    "matrix_row_id": "matrix_025_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 25: validator observes canonical read-only evidence and compares 3 registries against policy segment 25.",
    "bad_pattern": "bad pattern 27 in matrix 25: writer drift toward family 6, generated path reports_real/segment_25_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_25_27, boundary=bnd_matrix_25_27, switch=sw_matrix_25_27, hash_hint=3b1fc289b12b644e"
  },
  {
    "matrix_row_id": "matrix_025_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 25: validator observes canonical read-only evidence and compares 4 registries against policy segment 25.",
    "bad_pattern": "bad pattern 28 in matrix 25: writer drift toward family 0, generated path reports_real/segment_25_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_25_28, boundary=bnd_matrix_25_28, switch=sw_matrix_25_28, hash_hint=87c7380a110e6516"
  },
  {
    "matrix_row_id": "matrix_025_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 25: validator observes canonical read-only evidence and compares 5 registries against policy segment 25.",
    "bad_pattern": "bad pattern 29 in matrix 25: writer drift toward family 1, generated path reports_real/segment_25_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_25_29, boundary=bnd_matrix_25_29, switch=sw_matrix_25_29, hash_hint=39dca468b1c2c3c2"
  },
  {
    "matrix_row_id": "matrix_025_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 25: validator observes canonical read-only evidence and compares 1 registries against policy segment 25.",
    "bad_pattern": "bad pattern 30 in matrix 25: writer drift toward family 2, generated path reports_real/segment_25_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_25_30, boundary=bnd_matrix_25_30, switch=sw_matrix_25_30, hash_hint=b9c5f7db012b4590"
  },
  {
    "matrix_row_id": "matrix_025_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 25: validator observes canonical read-only evidence and compares 2 registries against policy segment 25.",
    "bad_pattern": "bad pattern 31 in matrix 25: writer drift toward family 3, generated path reports_real/segment_25_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_25_31, boundary=bnd_matrix_25_31, switch=sw_matrix_25_31, hash_hint=8104d11e9bf829e3"
  },
  {
    "matrix_row_id": "matrix_025_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 25: validator observes canonical read-only evidence and compares 3 registries against policy segment 25.",
    "bad_pattern": "bad pattern 32 in matrix 25: writer drift toward family 4, generated path reports_real/segment_25_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_25_32, boundary=bnd_matrix_25_32, switch=sw_matrix_25_32, hash_hint=298160a5770cd1f7"
  },
  {
    "matrix_row_id": "matrix_025_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 25: validator observes canonical read-only evidence and compares 4 registries against policy segment 25.",
    "bad_pattern": "bad pattern 33 in matrix 25: writer drift toward family 5, generated path reports_real/segment_25_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_25_33, boundary=bnd_matrix_25_33, switch=sw_matrix_25_33, hash_hint=8cb7f405bd67430e"
  },
  {
    "matrix_row_id": "matrix_025_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 25: validator observes canonical read-only evidence and compares 5 registries against policy segment 25.",
    "bad_pattern": "bad pattern 34 in matrix 25: writer drift toward family 6, generated path reports_real/segment_25_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_25_34, boundary=bnd_matrix_25_34, switch=sw_matrix_25_34, hash_hint=79184663fb7ec91e"
  },
  {
    "matrix_row_id": "matrix_025_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 25: validator observes canonical read-only evidence and compares 1 registries against policy segment 25.",
    "bad_pattern": "bad pattern 35 in matrix 25: writer drift toward family 0, generated path reports_real/segment_25_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_25_35, boundary=bnd_matrix_25_35, switch=sw_matrix_25_35, hash_hint=ef9486d1b76f28e1"
  },
  {
    "matrix_row_id": "matrix_025_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 25: validator observes canonical read-only evidence and compares 2 registries against policy segment 25.",
    "bad_pattern": "bad pattern 36 in matrix 25: writer drift toward family 1, generated path reports_real/segment_25_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_25_36, boundary=bnd_matrix_25_36, switch=sw_matrix_25_36, hash_hint=18fd8debabad0438"
  },
  {
    "matrix_row_id": "matrix_025_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 25: validator observes canonical read-only evidence and compares 3 registries against policy segment 25.",
    "bad_pattern": "bad pattern 37 in matrix 25: writer drift toward family 2, generated path reports_real/segment_25_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_25_37, boundary=bnd_matrix_25_37, switch=sw_matrix_25_37, hash_hint=bbb445ff9fb0d677"
  },
  {
    "matrix_row_id": "matrix_025_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 25: validator observes canonical read-only evidence and compares 4 registries against policy segment 25.",
    "bad_pattern": "bad pattern 38 in matrix 25: writer drift toward family 3, generated path reports_real/segment_25_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_25_38, boundary=bnd_matrix_25_38, switch=sw_matrix_25_38, hash_hint=44f1e57d80b51c04"
  },
  {
    "matrix_row_id": "matrix_025_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 25: validator observes canonical read-only evidence and compares 5 registries against policy segment 25.",
    "bad_pattern": "bad pattern 39 in matrix 25: writer drift toward family 4, generated path reports_real/segment_25_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_25_39, boundary=bnd_matrix_25_39, switch=sw_matrix_25_39, hash_hint=239b6882a65badb3"
  },
  {
    "matrix_row_id": "matrix_025_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 25: validator observes canonical read-only evidence and compares 1 registries against policy segment 25.",
    "bad_pattern": "bad pattern 40 in matrix 25: writer drift toward family 5, generated path reports_real/segment_25_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_25_40, boundary=bnd_matrix_25_40, switch=sw_matrix_25_40, hash_hint=c7a41e4ae81ba997"
  },
  {
    "matrix_row_id": "matrix_025_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 25: validator observes canonical read-only evidence and compares 2 registries against policy segment 25.",
    "bad_pattern": "bad pattern 41 in matrix 25: writer drift toward family 6, generated path reports_real/segment_25_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_25_41, boundary=bnd_matrix_25_41, switch=sw_matrix_25_41, hash_hint=900cb5dcadf1d7cc"
  },
  {
    "matrix_row_id": "matrix_025_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 25: validator observes canonical read-only evidence and compares 3 registries against policy segment 25.",
    "bad_pattern": "bad pattern 42 in matrix 25: writer drift toward family 0, generated path reports_real/segment_25_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_25_42, boundary=bnd_matrix_25_42, switch=sw_matrix_25_42, hash_hint=20301490e7823cf7"
  },
  {
    "matrix_row_id": "matrix_025_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 25: validator observes canonical read-only evidence and compares 4 registries against policy segment 25.",
    "bad_pattern": "bad pattern 43 in matrix 25: writer drift toward family 1, generated path reports_real/segment_25_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_25_43, boundary=bnd_matrix_25_43, switch=sw_matrix_25_43, hash_hint=644a4671be669258"
  },
  {
    "matrix_row_id": "matrix_025_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 25: validator observes canonical read-only evidence and compares 5 registries against policy segment 25.",
    "bad_pattern": "bad pattern 44 in matrix 25: writer drift toward family 2, generated path reports_real/segment_25_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_25_44, boundary=bnd_matrix_25_44, switch=sw_matrix_25_44, hash_hint=75453346b5a926ee"
  },
  {
    "matrix_row_id": "matrix_025_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 25: validator observes canonical read-only evidence and compares 1 registries against policy segment 25.",
    "bad_pattern": "bad pattern 45 in matrix 25: writer drift toward family 3, generated path reports_real/segment_25_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_25_45, boundary=bnd_matrix_25_45, switch=sw_matrix_25_45, hash_hint=9bc6fcaa0347021c"
  },
  {
    "matrix_row_id": "matrix_025_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 25: validator observes canonical read-only evidence and compares 2 registries against policy segment 25.",
    "bad_pattern": "bad pattern 46 in matrix 25: writer drift toward family 4, generated path reports_real/segment_25_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_25_46, boundary=bnd_matrix_25_46, switch=sw_matrix_25_46, hash_hint=e35a20c1f694d3be"
  },
  {
    "matrix_row_id": "matrix_025_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 25: validator observes canonical read-only evidence and compares 3 registries against policy segment 25.",
    "bad_pattern": "bad pattern 47 in matrix 25: writer drift toward family 5, generated path reports_real/segment_25_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_25_47, boundary=bnd_matrix_25_47, switch=sw_matrix_25_47, hash_hint=f30bf3e5a17a6c69"
  },
  {
    "matrix_row_id": "matrix_025_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 25: validator observes canonical read-only evidence and compares 4 registries against policy segment 25.",
    "bad_pattern": "bad pattern 48 in matrix 25: writer drift toward family 6, generated path reports_real/segment_25_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_25_48, boundary=bnd_matrix_25_48, switch=sw_matrix_25_48, hash_hint=c926be4a0169f9f8"
  },
  {
    "matrix_row_id": "matrix_025_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 25: validator observes canonical read-only evidence and compares 5 registries against policy segment 25.",
    "bad_pattern": "bad pattern 49 in matrix 25: writer drift toward family 0, generated path reports_real/segment_25_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_25_49, boundary=bnd_matrix_25_49, switch=sw_matrix_25_49, hash_hint=29206cef7518071d"
  },
  {
    "matrix_row_id": "matrix_025_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 25: validator observes canonical read-only evidence and compares 1 registries against policy segment 25.",
    "bad_pattern": "bad pattern 50 in matrix 25: writer drift toward family 1, generated path reports_real/segment_25_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_25_50, boundary=bnd_matrix_25_50, switch=sw_matrix_25_50, hash_hint=c68baddda0099a49"
  },
  {
    "matrix_row_id": "matrix_025_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 25: validator observes canonical read-only evidence and compares 2 registries against policy segment 25.",
    "bad_pattern": "bad pattern 51 in matrix 25: writer drift toward family 2, generated path reports_real/segment_25_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_25_51, boundary=bnd_matrix_25_51, switch=sw_matrix_25_51, hash_hint=f8ed4ab3c80ec42e"
  },
  {
    "matrix_row_id": "matrix_025_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 25: validator observes canonical read-only evidence and compares 3 registries against policy segment 25.",
    "bad_pattern": "bad pattern 52 in matrix 25: writer drift toward family 3, generated path reports_real/segment_25_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_25_52, boundary=bnd_matrix_25_52, switch=sw_matrix_25_52, hash_hint=3c3b2a52aff3dc36"
  },
  {
    "matrix_row_id": "matrix_025_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 25: validator observes canonical read-only evidence and compares 4 registries against policy segment 25.",
    "bad_pattern": "bad pattern 53 in matrix 25: writer drift toward family 4, generated path reports_real/segment_25_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_25_53, boundary=bnd_matrix_25_53, switch=sw_matrix_25_53, hash_hint=37ee0ae4f6e24c72"
  },
  {
    "matrix_row_id": "matrix_025_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 25: validator observes canonical read-only evidence and compares 5 registries against policy segment 25.",
    "bad_pattern": "bad pattern 54 in matrix 25: writer drift toward family 5, generated path reports_real/segment_25_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_25_54, boundary=bnd_matrix_25_54, switch=sw_matrix_25_54, hash_hint=d52b7cece4b57d88"
  },
  {
    "matrix_row_id": "matrix_025_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 25: validator observes canonical read-only evidence and compares 1 registries against policy segment 25.",
    "bad_pattern": "bad pattern 55 in matrix 25: writer drift toward family 6, generated path reports_real/segment_25_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_25_55, boundary=bnd_matrix_25_55, switch=sw_matrix_25_55, hash_hint=dc11a31b7779d03a"
  },
  {
    "matrix_row_id": "matrix_025_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 25: validator observes canonical read-only evidence and compares 2 registries against policy segment 25.",
    "bad_pattern": "bad pattern 56 in matrix 25: writer drift toward family 0, generated path reports_real/segment_25_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_25_56, boundary=bnd_matrix_25_56, switch=sw_matrix_25_56, hash_hint=b7ccfc9561e7702e"
  },
  {
    "matrix_row_id": "matrix_025_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 25: validator observes canonical read-only evidence and compares 3 registries against policy segment 25.",
    "bad_pattern": "bad pattern 57 in matrix 25: writer drift toward family 1, generated path reports_real/segment_25_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_25_57, boundary=bnd_matrix_25_57, switch=sw_matrix_25_57, hash_hint=296afcccda30a7e8"
  },
  {
    "matrix_row_id": "matrix_025_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 25: validator observes canonical read-only evidence and compares 4 registries against policy segment 25.",
    "bad_pattern": "bad pattern 58 in matrix 25: writer drift toward family 2, generated path reports_real/segment_25_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_25_58, boundary=bnd_matrix_25_58, switch=sw_matrix_25_58, hash_hint=729ccda980f17344"
  },
  {
    "matrix_row_id": "matrix_025_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 25: validator observes canonical read-only evidence and compares 5 registries against policy segment 25.",
    "bad_pattern": "bad pattern 59 in matrix 25: writer drift toward family 3, generated path reports_real/segment_25_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_25_59, boundary=bnd_matrix_25_59, switch=sw_matrix_25_59, hash_hint=da089c7980ede630"
  },
  {
    "matrix_row_id": "matrix_025_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 25: validator observes canonical read-only evidence and compares 1 registries against policy segment 25.",
    "bad_pattern": "bad pattern 60 in matrix 25: writer drift toward family 4, generated path reports_real/segment_25_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_25_60, boundary=bnd_matrix_25_60, switch=sw_matrix_25_60, hash_hint=b156509692693353"
  }
]
