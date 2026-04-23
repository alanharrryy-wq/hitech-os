from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 19/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 19/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 19/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 19/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 19/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 19/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 19/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 19/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 19/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 19/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 19/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 19/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 19/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 19/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 19/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 19/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 19/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 19/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 19/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 19/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 19/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 19/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 19/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 19/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 19/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_019_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 19: validator observes canonical read-only evidence and compares 2 registries against policy segment 19.",
    "bad_pattern": "bad pattern 1 in matrix 19: writer drift toward family 1, generated path reports_real/segment_19_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_19_1, boundary=bnd_matrix_19_1, switch=sw_matrix_19_1, hash_hint=955d493abc2c6d57"
  },
  {
    "matrix_row_id": "matrix_019_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 19: validator observes canonical read-only evidence and compares 3 registries against policy segment 19.",
    "bad_pattern": "bad pattern 2 in matrix 19: writer drift toward family 2, generated path reports_real/segment_19_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_19_2, boundary=bnd_matrix_19_2, switch=sw_matrix_19_2, hash_hint=f20a1e8b6846a3b2"
  },
  {
    "matrix_row_id": "matrix_019_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 19: validator observes canonical read-only evidence and compares 4 registries against policy segment 19.",
    "bad_pattern": "bad pattern 3 in matrix 19: writer drift toward family 3, generated path reports_real/segment_19_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_19_3, boundary=bnd_matrix_19_3, switch=sw_matrix_19_3, hash_hint=59b98f002022539a"
  },
  {
    "matrix_row_id": "matrix_019_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 19: validator observes canonical read-only evidence and compares 5 registries against policy segment 19.",
    "bad_pattern": "bad pattern 4 in matrix 19: writer drift toward family 4, generated path reports_real/segment_19_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_19_4, boundary=bnd_matrix_19_4, switch=sw_matrix_19_4, hash_hint=e11b3e81f08c3595"
  },
  {
    "matrix_row_id": "matrix_019_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 19: validator observes canonical read-only evidence and compares 1 registries against policy segment 19.",
    "bad_pattern": "bad pattern 5 in matrix 19: writer drift toward family 5, generated path reports_real/segment_19_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_19_5, boundary=bnd_matrix_19_5, switch=sw_matrix_19_5, hash_hint=23d71b053ee8df07"
  },
  {
    "matrix_row_id": "matrix_019_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 19: validator observes canonical read-only evidence and compares 2 registries against policy segment 19.",
    "bad_pattern": "bad pattern 6 in matrix 19: writer drift toward family 6, generated path reports_real/segment_19_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_19_6, boundary=bnd_matrix_19_6, switch=sw_matrix_19_6, hash_hint=376548c7e6a48dae"
  },
  {
    "matrix_row_id": "matrix_019_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 19: validator observes canonical read-only evidence and compares 3 registries against policy segment 19.",
    "bad_pattern": "bad pattern 7 in matrix 19: writer drift toward family 0, generated path reports_real/segment_19_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_19_7, boundary=bnd_matrix_19_7, switch=sw_matrix_19_7, hash_hint=45aa3f6877570bd9"
  },
  {
    "matrix_row_id": "matrix_019_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 19: validator observes canonical read-only evidence and compares 4 registries against policy segment 19.",
    "bad_pattern": "bad pattern 8 in matrix 19: writer drift toward family 1, generated path reports_real/segment_19_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_19_8, boundary=bnd_matrix_19_8, switch=sw_matrix_19_8, hash_hint=8d9696a76009b75c"
  },
  {
    "matrix_row_id": "matrix_019_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 19: validator observes canonical read-only evidence and compares 5 registries against policy segment 19.",
    "bad_pattern": "bad pattern 9 in matrix 19: writer drift toward family 2, generated path reports_real/segment_19_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_19_9, boundary=bnd_matrix_19_9, switch=sw_matrix_19_9, hash_hint=9c73f2dd3515f744"
  },
  {
    "matrix_row_id": "matrix_019_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 19: validator observes canonical read-only evidence and compares 1 registries against policy segment 19.",
    "bad_pattern": "bad pattern 10 in matrix 19: writer drift toward family 3, generated path reports_real/segment_19_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_19_10, boundary=bnd_matrix_19_10, switch=sw_matrix_19_10, hash_hint=08b677eb57395bd7"
  },
  {
    "matrix_row_id": "matrix_019_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 19: validator observes canonical read-only evidence and compares 2 registries against policy segment 19.",
    "bad_pattern": "bad pattern 11 in matrix 19: writer drift toward family 4, generated path reports_real/segment_19_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_19_11, boundary=bnd_matrix_19_11, switch=sw_matrix_19_11, hash_hint=d9f3b2e173d8124b"
  },
  {
    "matrix_row_id": "matrix_019_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 19: validator observes canonical read-only evidence and compares 3 registries against policy segment 19.",
    "bad_pattern": "bad pattern 12 in matrix 19: writer drift toward family 5, generated path reports_real/segment_19_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_19_12, boundary=bnd_matrix_19_12, switch=sw_matrix_19_12, hash_hint=8519598ff184567d"
  },
  {
    "matrix_row_id": "matrix_019_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 19: validator observes canonical read-only evidence and compares 4 registries against policy segment 19.",
    "bad_pattern": "bad pattern 13 in matrix 19: writer drift toward family 6, generated path reports_real/segment_19_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_19_13, boundary=bnd_matrix_19_13, switch=sw_matrix_19_13, hash_hint=279a2086b2bc7239"
  },
  {
    "matrix_row_id": "matrix_019_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 19: validator observes canonical read-only evidence and compares 5 registries against policy segment 19.",
    "bad_pattern": "bad pattern 14 in matrix 19: writer drift toward family 0, generated path reports_real/segment_19_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_19_14, boundary=bnd_matrix_19_14, switch=sw_matrix_19_14, hash_hint=bf1f54a2c10dcfbd"
  },
  {
    "matrix_row_id": "matrix_019_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 19: validator observes canonical read-only evidence and compares 1 registries against policy segment 19.",
    "bad_pattern": "bad pattern 15 in matrix 19: writer drift toward family 1, generated path reports_real/segment_19_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_19_15, boundary=bnd_matrix_19_15, switch=sw_matrix_19_15, hash_hint=5ba1f23dd5bcc75e"
  },
  {
    "matrix_row_id": "matrix_019_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 19: validator observes canonical read-only evidence and compares 2 registries against policy segment 19.",
    "bad_pattern": "bad pattern 16 in matrix 19: writer drift toward family 2, generated path reports_real/segment_19_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_19_16, boundary=bnd_matrix_19_16, switch=sw_matrix_19_16, hash_hint=1b03c86ab1f227fa"
  },
  {
    "matrix_row_id": "matrix_019_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 19: validator observes canonical read-only evidence and compares 3 registries against policy segment 19.",
    "bad_pattern": "bad pattern 17 in matrix 19: writer drift toward family 3, generated path reports_real/segment_19_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_19_17, boundary=bnd_matrix_19_17, switch=sw_matrix_19_17, hash_hint=6dffc55ea907ff5d"
  },
  {
    "matrix_row_id": "matrix_019_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 19: validator observes canonical read-only evidence and compares 4 registries against policy segment 19.",
    "bad_pattern": "bad pattern 18 in matrix 19: writer drift toward family 4, generated path reports_real/segment_19_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_19_18, boundary=bnd_matrix_19_18, switch=sw_matrix_19_18, hash_hint=4ea877c2772f116a"
  },
  {
    "matrix_row_id": "matrix_019_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 19: validator observes canonical read-only evidence and compares 5 registries against policy segment 19.",
    "bad_pattern": "bad pattern 19 in matrix 19: writer drift toward family 5, generated path reports_real/segment_19_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_19_19, boundary=bnd_matrix_19_19, switch=sw_matrix_19_19, hash_hint=ef80c8b4afee2d49"
  },
  {
    "matrix_row_id": "matrix_019_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 19: validator observes canonical read-only evidence and compares 1 registries against policy segment 19.",
    "bad_pattern": "bad pattern 20 in matrix 19: writer drift toward family 6, generated path reports_real/segment_19_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_19_20, boundary=bnd_matrix_19_20, switch=sw_matrix_19_20, hash_hint=3e8a987cc1aa0b99"
  },
  {
    "matrix_row_id": "matrix_019_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 19: validator observes canonical read-only evidence and compares 2 registries against policy segment 19.",
    "bad_pattern": "bad pattern 21 in matrix 19: writer drift toward family 0, generated path reports_real/segment_19_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_19_21, boundary=bnd_matrix_19_21, switch=sw_matrix_19_21, hash_hint=f5251ca5e10829e1"
  },
  {
    "matrix_row_id": "matrix_019_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 19: validator observes canonical read-only evidence and compares 3 registries against policy segment 19.",
    "bad_pattern": "bad pattern 22 in matrix 19: writer drift toward family 1, generated path reports_real/segment_19_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_19_22, boundary=bnd_matrix_19_22, switch=sw_matrix_19_22, hash_hint=9224f8987a6392a3"
  },
  {
    "matrix_row_id": "matrix_019_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 19: validator observes canonical read-only evidence and compares 4 registries against policy segment 19.",
    "bad_pattern": "bad pattern 23 in matrix 19: writer drift toward family 2, generated path reports_real/segment_19_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_19_23, boundary=bnd_matrix_19_23, switch=sw_matrix_19_23, hash_hint=9aa2bf4633ffa0f5"
  },
  {
    "matrix_row_id": "matrix_019_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 19: validator observes canonical read-only evidence and compares 5 registries against policy segment 19.",
    "bad_pattern": "bad pattern 24 in matrix 19: writer drift toward family 3, generated path reports_real/segment_19_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_19_24, boundary=bnd_matrix_19_24, switch=sw_matrix_19_24, hash_hint=f8f5ab97b9a7aecf"
  },
  {
    "matrix_row_id": "matrix_019_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 19: validator observes canonical read-only evidence and compares 1 registries against policy segment 19.",
    "bad_pattern": "bad pattern 25 in matrix 19: writer drift toward family 4, generated path reports_real/segment_19_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_19_25, boundary=bnd_matrix_19_25, switch=sw_matrix_19_25, hash_hint=6748cc04140c66ae"
  },
  {
    "matrix_row_id": "matrix_019_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 19: validator observes canonical read-only evidence and compares 2 registries against policy segment 19.",
    "bad_pattern": "bad pattern 26 in matrix 19: writer drift toward family 5, generated path reports_real/segment_19_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_19_26, boundary=bnd_matrix_19_26, switch=sw_matrix_19_26, hash_hint=bf7c6381f1e38fe5"
  },
  {
    "matrix_row_id": "matrix_019_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 19: validator observes canonical read-only evidence and compares 3 registries against policy segment 19.",
    "bad_pattern": "bad pattern 27 in matrix 19: writer drift toward family 6, generated path reports_real/segment_19_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_19_27, boundary=bnd_matrix_19_27, switch=sw_matrix_19_27, hash_hint=fe134bdc3cb95b24"
  },
  {
    "matrix_row_id": "matrix_019_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 19: validator observes canonical read-only evidence and compares 4 registries against policy segment 19.",
    "bad_pattern": "bad pattern 28 in matrix 19: writer drift toward family 0, generated path reports_real/segment_19_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_19_28, boundary=bnd_matrix_19_28, switch=sw_matrix_19_28, hash_hint=8076e9ab741e75d8"
  },
  {
    "matrix_row_id": "matrix_019_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 19: validator observes canonical read-only evidence and compares 5 registries against policy segment 19.",
    "bad_pattern": "bad pattern 29 in matrix 19: writer drift toward family 1, generated path reports_real/segment_19_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_19_29, boundary=bnd_matrix_19_29, switch=sw_matrix_19_29, hash_hint=3beea7311a443f8b"
  },
  {
    "matrix_row_id": "matrix_019_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 19: validator observes canonical read-only evidence and compares 1 registries against policy segment 19.",
    "bad_pattern": "bad pattern 30 in matrix 19: writer drift toward family 2, generated path reports_real/segment_19_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_19_30, boundary=bnd_matrix_19_30, switch=sw_matrix_19_30, hash_hint=42cffad17953dcd3"
  },
  {
    "matrix_row_id": "matrix_019_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 19: validator observes canonical read-only evidence and compares 2 registries against policy segment 19.",
    "bad_pattern": "bad pattern 31 in matrix 19: writer drift toward family 3, generated path reports_real/segment_19_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_19_31, boundary=bnd_matrix_19_31, switch=sw_matrix_19_31, hash_hint=9dff747ee742aabd"
  },
  {
    "matrix_row_id": "matrix_019_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 19: validator observes canonical read-only evidence and compares 3 registries against policy segment 19.",
    "bad_pattern": "bad pattern 32 in matrix 19: writer drift toward family 4, generated path reports_real/segment_19_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_19_32, boundary=bnd_matrix_19_32, switch=sw_matrix_19_32, hash_hint=502f677037a97267"
  },
  {
    "matrix_row_id": "matrix_019_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 19: validator observes canonical read-only evidence and compares 4 registries against policy segment 19.",
    "bad_pattern": "bad pattern 33 in matrix 19: writer drift toward family 5, generated path reports_real/segment_19_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_19_33, boundary=bnd_matrix_19_33, switch=sw_matrix_19_33, hash_hint=2b633ff035e2baee"
  },
  {
    "matrix_row_id": "matrix_019_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 19: validator observes canonical read-only evidence and compares 5 registries against policy segment 19.",
    "bad_pattern": "bad pattern 34 in matrix 19: writer drift toward family 6, generated path reports_real/segment_19_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_19_34, boundary=bnd_matrix_19_34, switch=sw_matrix_19_34, hash_hint=95b361f7ecd7c867"
  },
  {
    "matrix_row_id": "matrix_019_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 19: validator observes canonical read-only evidence and compares 1 registries against policy segment 19.",
    "bad_pattern": "bad pattern 35 in matrix 19: writer drift toward family 0, generated path reports_real/segment_19_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_19_35, boundary=bnd_matrix_19_35, switch=sw_matrix_19_35, hash_hint=8446ac0c002484c1"
  },
  {
    "matrix_row_id": "matrix_019_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 19: validator observes canonical read-only evidence and compares 2 registries against policy segment 19.",
    "bad_pattern": "bad pattern 36 in matrix 19: writer drift toward family 1, generated path reports_real/segment_19_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_19_36, boundary=bnd_matrix_19_36, switch=sw_matrix_19_36, hash_hint=ac9a002a04b89c45"
  },
  {
    "matrix_row_id": "matrix_019_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 19: validator observes canonical read-only evidence and compares 3 registries against policy segment 19.",
    "bad_pattern": "bad pattern 37 in matrix 19: writer drift toward family 2, generated path reports_real/segment_19_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_19_37, boundary=bnd_matrix_19_37, switch=sw_matrix_19_37, hash_hint=0a6aafa36867cb31"
  },
  {
    "matrix_row_id": "matrix_019_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 19: validator observes canonical read-only evidence and compares 4 registries against policy segment 19.",
    "bad_pattern": "bad pattern 38 in matrix 19: writer drift toward family 3, generated path reports_real/segment_19_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_19_38, boundary=bnd_matrix_19_38, switch=sw_matrix_19_38, hash_hint=394150dd88c0927e"
  },
  {
    "matrix_row_id": "matrix_019_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 19: validator observes canonical read-only evidence and compares 5 registries against policy segment 19.",
    "bad_pattern": "bad pattern 39 in matrix 19: writer drift toward family 4, generated path reports_real/segment_19_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_19_39, boundary=bnd_matrix_19_39, switch=sw_matrix_19_39, hash_hint=cdb4853079fc214b"
  },
  {
    "matrix_row_id": "matrix_019_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 19: validator observes canonical read-only evidence and compares 1 registries against policy segment 19.",
    "bad_pattern": "bad pattern 40 in matrix 19: writer drift toward family 5, generated path reports_real/segment_19_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_19_40, boundary=bnd_matrix_19_40, switch=sw_matrix_19_40, hash_hint=bb5bfe2f09428342"
  },
  {
    "matrix_row_id": "matrix_019_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 19: validator observes canonical read-only evidence and compares 2 registries against policy segment 19.",
    "bad_pattern": "bad pattern 41 in matrix 19: writer drift toward family 6, generated path reports_real/segment_19_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_19_41, boundary=bnd_matrix_19_41, switch=sw_matrix_19_41, hash_hint=624643901525200e"
  },
  {
    "matrix_row_id": "matrix_019_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 19: validator observes canonical read-only evidence and compares 3 registries against policy segment 19.",
    "bad_pattern": "bad pattern 42 in matrix 19: writer drift toward family 0, generated path reports_real/segment_19_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_19_42, boundary=bnd_matrix_19_42, switch=sw_matrix_19_42, hash_hint=9035a6aba73d9a9c"
  },
  {
    "matrix_row_id": "matrix_019_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 19: validator observes canonical read-only evidence and compares 4 registries against policy segment 19.",
    "bad_pattern": "bad pattern 43 in matrix 19: writer drift toward family 1, generated path reports_real/segment_19_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_19_43, boundary=bnd_matrix_19_43, switch=sw_matrix_19_43, hash_hint=053b505dd0342377"
  },
  {
    "matrix_row_id": "matrix_019_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 19: validator observes canonical read-only evidence and compares 5 registries against policy segment 19.",
    "bad_pattern": "bad pattern 44 in matrix 19: writer drift toward family 2, generated path reports_real/segment_19_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_19_44, boundary=bnd_matrix_19_44, switch=sw_matrix_19_44, hash_hint=c64f18f2b8dcbc74"
  },
  {
    "matrix_row_id": "matrix_019_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 19: validator observes canonical read-only evidence and compares 1 registries against policy segment 19.",
    "bad_pattern": "bad pattern 45 in matrix 19: writer drift toward family 3, generated path reports_real/segment_19_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_19_45, boundary=bnd_matrix_19_45, switch=sw_matrix_19_45, hash_hint=6dc8fe1b29d1490f"
  },
  {
    "matrix_row_id": "matrix_019_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 19: validator observes canonical read-only evidence and compares 2 registries against policy segment 19.",
    "bad_pattern": "bad pattern 46 in matrix 19: writer drift toward family 4, generated path reports_real/segment_19_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_19_46, boundary=bnd_matrix_19_46, switch=sw_matrix_19_46, hash_hint=4c062eb85cdd244f"
  },
  {
    "matrix_row_id": "matrix_019_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 19: validator observes canonical read-only evidence and compares 3 registries against policy segment 19.",
    "bad_pattern": "bad pattern 47 in matrix 19: writer drift toward family 5, generated path reports_real/segment_19_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_19_47, boundary=bnd_matrix_19_47, switch=sw_matrix_19_47, hash_hint=b5fdc7c4aaa6d5a8"
  },
  {
    "matrix_row_id": "matrix_019_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 19: validator observes canonical read-only evidence and compares 4 registries against policy segment 19.",
    "bad_pattern": "bad pattern 48 in matrix 19: writer drift toward family 6, generated path reports_real/segment_19_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_19_48, boundary=bnd_matrix_19_48, switch=sw_matrix_19_48, hash_hint=6b336cd61240d735"
  },
  {
    "matrix_row_id": "matrix_019_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 19: validator observes canonical read-only evidence and compares 5 registries against policy segment 19.",
    "bad_pattern": "bad pattern 49 in matrix 19: writer drift toward family 0, generated path reports_real/segment_19_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_19_49, boundary=bnd_matrix_19_49, switch=sw_matrix_19_49, hash_hint=b30aacdd8b283ad8"
  },
  {
    "matrix_row_id": "matrix_019_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 19: validator observes canonical read-only evidence and compares 1 registries against policy segment 19.",
    "bad_pattern": "bad pattern 50 in matrix 19: writer drift toward family 1, generated path reports_real/segment_19_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_19_50, boundary=bnd_matrix_19_50, switch=sw_matrix_19_50, hash_hint=a70ef361acd7dfe4"
  },
  {
    "matrix_row_id": "matrix_019_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 19: validator observes canonical read-only evidence and compares 2 registries against policy segment 19.",
    "bad_pattern": "bad pattern 51 in matrix 19: writer drift toward family 2, generated path reports_real/segment_19_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_19_51, boundary=bnd_matrix_19_51, switch=sw_matrix_19_51, hash_hint=831619dd63499726"
  },
  {
    "matrix_row_id": "matrix_019_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 19: validator observes canonical read-only evidence and compares 3 registries against policy segment 19.",
    "bad_pattern": "bad pattern 52 in matrix 19: writer drift toward family 3, generated path reports_real/segment_19_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_19_52, boundary=bnd_matrix_19_52, switch=sw_matrix_19_52, hash_hint=0e0137b434dc1acc"
  },
  {
    "matrix_row_id": "matrix_019_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 19: validator observes canonical read-only evidence and compares 4 registries against policy segment 19.",
    "bad_pattern": "bad pattern 53 in matrix 19: writer drift toward family 4, generated path reports_real/segment_19_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_19_53, boundary=bnd_matrix_19_53, switch=sw_matrix_19_53, hash_hint=ca1359c09d8c76cb"
  },
  {
    "matrix_row_id": "matrix_019_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 19: validator observes canonical read-only evidence and compares 5 registries against policy segment 19.",
    "bad_pattern": "bad pattern 54 in matrix 19: writer drift toward family 5, generated path reports_real/segment_19_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_19_54, boundary=bnd_matrix_19_54, switch=sw_matrix_19_54, hash_hint=209d51a5d64090a3"
  },
  {
    "matrix_row_id": "matrix_019_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 19: validator observes canonical read-only evidence and compares 1 registries against policy segment 19.",
    "bad_pattern": "bad pattern 55 in matrix 19: writer drift toward family 6, generated path reports_real/segment_19_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_19_55, boundary=bnd_matrix_19_55, switch=sw_matrix_19_55, hash_hint=fa3c8699fa0f7d4a"
  },
  {
    "matrix_row_id": "matrix_019_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 19: validator observes canonical read-only evidence and compares 2 registries against policy segment 19.",
    "bad_pattern": "bad pattern 56 in matrix 19: writer drift toward family 0, generated path reports_real/segment_19_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_19_56, boundary=bnd_matrix_19_56, switch=sw_matrix_19_56, hash_hint=0289aec6af43855d"
  },
  {
    "matrix_row_id": "matrix_019_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 19: validator observes canonical read-only evidence and compares 3 registries against policy segment 19.",
    "bad_pattern": "bad pattern 57 in matrix 19: writer drift toward family 1, generated path reports_real/segment_19_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_19_57, boundary=bnd_matrix_19_57, switch=sw_matrix_19_57, hash_hint=ff7f5d3aeb0ed38c"
  },
  {
    "matrix_row_id": "matrix_019_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 19: validator observes canonical read-only evidence and compares 4 registries against policy segment 19.",
    "bad_pattern": "bad pattern 58 in matrix 19: writer drift toward family 2, generated path reports_real/segment_19_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_19_58, boundary=bnd_matrix_19_58, switch=sw_matrix_19_58, hash_hint=f9d399ab3ed8b6fe"
  },
  {
    "matrix_row_id": "matrix_019_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 19: validator observes canonical read-only evidence and compares 5 registries against policy segment 19.",
    "bad_pattern": "bad pattern 59 in matrix 19: writer drift toward family 3, generated path reports_real/segment_19_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_19_59, boundary=bnd_matrix_19_59, switch=sw_matrix_19_59, hash_hint=6e141700bde7ff70"
  },
  {
    "matrix_row_id": "matrix_019_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 19: validator observes canonical read-only evidence and compares 1 registries against policy segment 19.",
    "bad_pattern": "bad pattern 60 in matrix 19: writer drift toward family 4, generated path reports_real/segment_19_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_19_60, boundary=bnd_matrix_19_60, switch=sw_matrix_19_60, hash_hint=68806da85ed9bc44"
  }
]
