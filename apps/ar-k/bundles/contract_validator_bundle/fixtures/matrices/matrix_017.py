from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 17/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 17/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 17/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 17/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 17/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 17/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 17/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 17/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 17/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 17/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 17/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 17/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 17/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 17/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 17/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 17/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 17/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 17/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 17/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 17/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 17/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 17/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 17/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 17/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 17/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_017_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 17: validator observes canonical read-only evidence and compares 2 registries against policy segment 17.",
    "bad_pattern": "bad pattern 1 in matrix 17: writer drift toward family 1, generated path reports_real/segment_17_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_17_1, boundary=bnd_matrix_17_1, switch=sw_matrix_17_1, hash_hint=f7eda34efb45335a"
  },
  {
    "matrix_row_id": "matrix_017_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 17: validator observes canonical read-only evidence and compares 3 registries against policy segment 17.",
    "bad_pattern": "bad pattern 2 in matrix 17: writer drift toward family 2, generated path reports_real/segment_17_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_17_2, boundary=bnd_matrix_17_2, switch=sw_matrix_17_2, hash_hint=d7f22d0f76e5e00d"
  },
  {
    "matrix_row_id": "matrix_017_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 17: validator observes canonical read-only evidence and compares 4 registries against policy segment 17.",
    "bad_pattern": "bad pattern 3 in matrix 17: writer drift toward family 3, generated path reports_real/segment_17_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_17_3, boundary=bnd_matrix_17_3, switch=sw_matrix_17_3, hash_hint=a16d0db384753781"
  },
  {
    "matrix_row_id": "matrix_017_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 17: validator observes canonical read-only evidence and compares 5 registries against policy segment 17.",
    "bad_pattern": "bad pattern 4 in matrix 17: writer drift toward family 4, generated path reports_real/segment_17_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_17_4, boundary=bnd_matrix_17_4, switch=sw_matrix_17_4, hash_hint=1ca83e936ca78de3"
  },
  {
    "matrix_row_id": "matrix_017_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 17: validator observes canonical read-only evidence and compares 1 registries against policy segment 17.",
    "bad_pattern": "bad pattern 5 in matrix 17: writer drift toward family 5, generated path reports_real/segment_17_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_17_5, boundary=bnd_matrix_17_5, switch=sw_matrix_17_5, hash_hint=18b4c705bc854180"
  },
  {
    "matrix_row_id": "matrix_017_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 17: validator observes canonical read-only evidence and compares 2 registries against policy segment 17.",
    "bad_pattern": "bad pattern 6 in matrix 17: writer drift toward family 6, generated path reports_real/segment_17_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_17_6, boundary=bnd_matrix_17_6, switch=sw_matrix_17_6, hash_hint=e1733f3a7dc7ecdf"
  },
  {
    "matrix_row_id": "matrix_017_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 17: validator observes canonical read-only evidence and compares 3 registries against policy segment 17.",
    "bad_pattern": "bad pattern 7 in matrix 17: writer drift toward family 0, generated path reports_real/segment_17_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_17_7, boundary=bnd_matrix_17_7, switch=sw_matrix_17_7, hash_hint=6f0025cf04dd7b32"
  },
  {
    "matrix_row_id": "matrix_017_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 17: validator observes canonical read-only evidence and compares 4 registries against policy segment 17.",
    "bad_pattern": "bad pattern 8 in matrix 17: writer drift toward family 1, generated path reports_real/segment_17_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_17_8, boundary=bnd_matrix_17_8, switch=sw_matrix_17_8, hash_hint=f64e3dcca399c11d"
  },
  {
    "matrix_row_id": "matrix_017_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 17: validator observes canonical read-only evidence and compares 5 registries against policy segment 17.",
    "bad_pattern": "bad pattern 9 in matrix 17: writer drift toward family 2, generated path reports_real/segment_17_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_17_9, boundary=bnd_matrix_17_9, switch=sw_matrix_17_9, hash_hint=26fbdba20bebfa3c"
  },
  {
    "matrix_row_id": "matrix_017_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 17: validator observes canonical read-only evidence and compares 1 registries against policy segment 17.",
    "bad_pattern": "bad pattern 10 in matrix 17: writer drift toward family 3, generated path reports_real/segment_17_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_17_10, boundary=bnd_matrix_17_10, switch=sw_matrix_17_10, hash_hint=333f0452367982fd"
  },
  {
    "matrix_row_id": "matrix_017_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 17: validator observes canonical read-only evidence and compares 2 registries against policy segment 17.",
    "bad_pattern": "bad pattern 11 in matrix 17: writer drift toward family 4, generated path reports_real/segment_17_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_17_11, boundary=bnd_matrix_17_11, switch=sw_matrix_17_11, hash_hint=04d769d6ed0b9c66"
  },
  {
    "matrix_row_id": "matrix_017_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 17: validator observes canonical read-only evidence and compares 3 registries against policy segment 17.",
    "bad_pattern": "bad pattern 12 in matrix 17: writer drift toward family 5, generated path reports_real/segment_17_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_17_12, boundary=bnd_matrix_17_12, switch=sw_matrix_17_12, hash_hint=08e5846c76c4e7f8"
  },
  {
    "matrix_row_id": "matrix_017_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 17: validator observes canonical read-only evidence and compares 4 registries against policy segment 17.",
    "bad_pattern": "bad pattern 13 in matrix 17: writer drift toward family 6, generated path reports_real/segment_17_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_17_13, boundary=bnd_matrix_17_13, switch=sw_matrix_17_13, hash_hint=0f540b90d83fccb7"
  },
  {
    "matrix_row_id": "matrix_017_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 17: validator observes canonical read-only evidence and compares 5 registries against policy segment 17.",
    "bad_pattern": "bad pattern 14 in matrix 17: writer drift toward family 0, generated path reports_real/segment_17_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_17_14, boundary=bnd_matrix_17_14, switch=sw_matrix_17_14, hash_hint=9bb908dd351de273"
  },
  {
    "matrix_row_id": "matrix_017_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 17: validator observes canonical read-only evidence and compares 1 registries against policy segment 17.",
    "bad_pattern": "bad pattern 15 in matrix 17: writer drift toward family 1, generated path reports_real/segment_17_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_17_15, boundary=bnd_matrix_17_15, switch=sw_matrix_17_15, hash_hint=0bdc10d326b0e922"
  },
  {
    "matrix_row_id": "matrix_017_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 17: validator observes canonical read-only evidence and compares 2 registries against policy segment 17.",
    "bad_pattern": "bad pattern 16 in matrix 17: writer drift toward family 2, generated path reports_real/segment_17_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_17_16, boundary=bnd_matrix_17_16, switch=sw_matrix_17_16, hash_hint=fb76952898ccb304"
  },
  {
    "matrix_row_id": "matrix_017_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 17: validator observes canonical read-only evidence and compares 3 registries against policy segment 17.",
    "bad_pattern": "bad pattern 17 in matrix 17: writer drift toward family 3, generated path reports_real/segment_17_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_17_17, boundary=bnd_matrix_17_17, switch=sw_matrix_17_17, hash_hint=48b0fac096de8e34"
  },
  {
    "matrix_row_id": "matrix_017_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 17: validator observes canonical read-only evidence and compares 4 registries against policy segment 17.",
    "bad_pattern": "bad pattern 18 in matrix 17: writer drift toward family 4, generated path reports_real/segment_17_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_17_18, boundary=bnd_matrix_17_18, switch=sw_matrix_17_18, hash_hint=7faae8798974a24a"
  },
  {
    "matrix_row_id": "matrix_017_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 17: validator observes canonical read-only evidence and compares 5 registries against policy segment 17.",
    "bad_pattern": "bad pattern 19 in matrix 17: writer drift toward family 5, generated path reports_real/segment_17_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_17_19, boundary=bnd_matrix_17_19, switch=sw_matrix_17_19, hash_hint=f906ac660528f598"
  },
  {
    "matrix_row_id": "matrix_017_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 17: validator observes canonical read-only evidence and compares 1 registries against policy segment 17.",
    "bad_pattern": "bad pattern 20 in matrix 17: writer drift toward family 6, generated path reports_real/segment_17_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_17_20, boundary=bnd_matrix_17_20, switch=sw_matrix_17_20, hash_hint=d80116b4818df295"
  },
  {
    "matrix_row_id": "matrix_017_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 17: validator observes canonical read-only evidence and compares 2 registries against policy segment 17.",
    "bad_pattern": "bad pattern 21 in matrix 17: writer drift toward family 0, generated path reports_real/segment_17_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_17_21, boundary=bnd_matrix_17_21, switch=sw_matrix_17_21, hash_hint=0e084583c7ca2542"
  },
  {
    "matrix_row_id": "matrix_017_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 17: validator observes canonical read-only evidence and compares 3 registries against policy segment 17.",
    "bad_pattern": "bad pattern 22 in matrix 17: writer drift toward family 1, generated path reports_real/segment_17_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_17_22, boundary=bnd_matrix_17_22, switch=sw_matrix_17_22, hash_hint=0597fd1a47c0a2ff"
  },
  {
    "matrix_row_id": "matrix_017_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 17: validator observes canonical read-only evidence and compares 4 registries against policy segment 17.",
    "bad_pattern": "bad pattern 23 in matrix 17: writer drift toward family 2, generated path reports_real/segment_17_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_17_23, boundary=bnd_matrix_17_23, switch=sw_matrix_17_23, hash_hint=394559e1ee2692b0"
  },
  {
    "matrix_row_id": "matrix_017_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 17: validator observes canonical read-only evidence and compares 5 registries against policy segment 17.",
    "bad_pattern": "bad pattern 24 in matrix 17: writer drift toward family 3, generated path reports_real/segment_17_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_17_24, boundary=bnd_matrix_17_24, switch=sw_matrix_17_24, hash_hint=967df79c693f1b5e"
  },
  {
    "matrix_row_id": "matrix_017_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 17: validator observes canonical read-only evidence and compares 1 registries against policy segment 17.",
    "bad_pattern": "bad pattern 25 in matrix 17: writer drift toward family 4, generated path reports_real/segment_17_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_17_25, boundary=bnd_matrix_17_25, switch=sw_matrix_17_25, hash_hint=1421eaeb07cb05b0"
  },
  {
    "matrix_row_id": "matrix_017_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 17: validator observes canonical read-only evidence and compares 2 registries against policy segment 17.",
    "bad_pattern": "bad pattern 26 in matrix 17: writer drift toward family 5, generated path reports_real/segment_17_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_17_26, boundary=bnd_matrix_17_26, switch=sw_matrix_17_26, hash_hint=592228ab53a1c406"
  },
  {
    "matrix_row_id": "matrix_017_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 17: validator observes canonical read-only evidence and compares 3 registries against policy segment 17.",
    "bad_pattern": "bad pattern 27 in matrix 17: writer drift toward family 6, generated path reports_real/segment_17_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_17_27, boundary=bnd_matrix_17_27, switch=sw_matrix_17_27, hash_hint=5ae84a0d9f6a3ee9"
  },
  {
    "matrix_row_id": "matrix_017_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 17: validator observes canonical read-only evidence and compares 4 registries against policy segment 17.",
    "bad_pattern": "bad pattern 28 in matrix 17: writer drift toward family 0, generated path reports_real/segment_17_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_17_28, boundary=bnd_matrix_17_28, switch=sw_matrix_17_28, hash_hint=d760f36ef11c2747"
  },
  {
    "matrix_row_id": "matrix_017_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 17: validator observes canonical read-only evidence and compares 5 registries against policy segment 17.",
    "bad_pattern": "bad pattern 29 in matrix 17: writer drift toward family 1, generated path reports_real/segment_17_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_17_29, boundary=bnd_matrix_17_29, switch=sw_matrix_17_29, hash_hint=29f124b543f557aa"
  },
  {
    "matrix_row_id": "matrix_017_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 17: validator observes canonical read-only evidence and compares 1 registries against policy segment 17.",
    "bad_pattern": "bad pattern 30 in matrix 17: writer drift toward family 2, generated path reports_real/segment_17_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_17_30, boundary=bnd_matrix_17_30, switch=sw_matrix_17_30, hash_hint=8b1516debafe302f"
  },
  {
    "matrix_row_id": "matrix_017_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 17: validator observes canonical read-only evidence and compares 2 registries against policy segment 17.",
    "bad_pattern": "bad pattern 31 in matrix 17: writer drift toward family 3, generated path reports_real/segment_17_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_17_31, boundary=bnd_matrix_17_31, switch=sw_matrix_17_31, hash_hint=fc8f739534d5a5b4"
  },
  {
    "matrix_row_id": "matrix_017_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 17: validator observes canonical read-only evidence and compares 3 registries against policy segment 17.",
    "bad_pattern": "bad pattern 32 in matrix 17: writer drift toward family 4, generated path reports_real/segment_17_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_17_32, boundary=bnd_matrix_17_32, switch=sw_matrix_17_32, hash_hint=1292b496af8c31b9"
  },
  {
    "matrix_row_id": "matrix_017_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 17: validator observes canonical read-only evidence and compares 4 registries against policy segment 17.",
    "bad_pattern": "bad pattern 33 in matrix 17: writer drift toward family 5, generated path reports_real/segment_17_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_17_33, boundary=bnd_matrix_17_33, switch=sw_matrix_17_33, hash_hint=fd0dd61e99e563c7"
  },
  {
    "matrix_row_id": "matrix_017_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 17: validator observes canonical read-only evidence and compares 5 registries against policy segment 17.",
    "bad_pattern": "bad pattern 34 in matrix 17: writer drift toward family 6, generated path reports_real/segment_17_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_17_34, boundary=bnd_matrix_17_34, switch=sw_matrix_17_34, hash_hint=07e87c396820d7bd"
  },
  {
    "matrix_row_id": "matrix_017_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 17: validator observes canonical read-only evidence and compares 1 registries against policy segment 17.",
    "bad_pattern": "bad pattern 35 in matrix 17: writer drift toward family 0, generated path reports_real/segment_17_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_17_35, boundary=bnd_matrix_17_35, switch=sw_matrix_17_35, hash_hint=ad52258391664493"
  },
  {
    "matrix_row_id": "matrix_017_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 17: validator observes canonical read-only evidence and compares 2 registries against policy segment 17.",
    "bad_pattern": "bad pattern 36 in matrix 17: writer drift toward family 1, generated path reports_real/segment_17_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_17_36, boundary=bnd_matrix_17_36, switch=sw_matrix_17_36, hash_hint=525903d71cb87d86"
  },
  {
    "matrix_row_id": "matrix_017_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 17: validator observes canonical read-only evidence and compares 3 registries against policy segment 17.",
    "bad_pattern": "bad pattern 37 in matrix 17: writer drift toward family 2, generated path reports_real/segment_17_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_17_37, boundary=bnd_matrix_17_37, switch=sw_matrix_17_37, hash_hint=94c64bb037610f58"
  },
  {
    "matrix_row_id": "matrix_017_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 17: validator observes canonical read-only evidence and compares 4 registries against policy segment 17.",
    "bad_pattern": "bad pattern 38 in matrix 17: writer drift toward family 3, generated path reports_real/segment_17_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_17_38, boundary=bnd_matrix_17_38, switch=sw_matrix_17_38, hash_hint=7f42eb831b52a0f3"
  },
  {
    "matrix_row_id": "matrix_017_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 17: validator observes canonical read-only evidence and compares 5 registries against policy segment 17.",
    "bad_pattern": "bad pattern 39 in matrix 17: writer drift toward family 4, generated path reports_real/segment_17_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_17_39, boundary=bnd_matrix_17_39, switch=sw_matrix_17_39, hash_hint=5b2054b52eba3065"
  },
  {
    "matrix_row_id": "matrix_017_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 17: validator observes canonical read-only evidence and compares 1 registries against policy segment 17.",
    "bad_pattern": "bad pattern 40 in matrix 17: writer drift toward family 5, generated path reports_real/segment_17_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_17_40, boundary=bnd_matrix_17_40, switch=sw_matrix_17_40, hash_hint=5ed64e58fc43acbb"
  },
  {
    "matrix_row_id": "matrix_017_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 17: validator observes canonical read-only evidence and compares 2 registries against policy segment 17.",
    "bad_pattern": "bad pattern 41 in matrix 17: writer drift toward family 6, generated path reports_real/segment_17_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_17_41, boundary=bnd_matrix_17_41, switch=sw_matrix_17_41, hash_hint=ff1b6477b7a6abd9"
  },
  {
    "matrix_row_id": "matrix_017_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 17: validator observes canonical read-only evidence and compares 3 registries against policy segment 17.",
    "bad_pattern": "bad pattern 42 in matrix 17: writer drift toward family 0, generated path reports_real/segment_17_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_17_42, boundary=bnd_matrix_17_42, switch=sw_matrix_17_42, hash_hint=ba1bbbd5420f38d1"
  },
  {
    "matrix_row_id": "matrix_017_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 17: validator observes canonical read-only evidence and compares 4 registries against policy segment 17.",
    "bad_pattern": "bad pattern 43 in matrix 17: writer drift toward family 1, generated path reports_real/segment_17_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_17_43, boundary=bnd_matrix_17_43, switch=sw_matrix_17_43, hash_hint=832b25608027ed39"
  },
  {
    "matrix_row_id": "matrix_017_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 17: validator observes canonical read-only evidence and compares 5 registries against policy segment 17.",
    "bad_pattern": "bad pattern 44 in matrix 17: writer drift toward family 2, generated path reports_real/segment_17_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_17_44, boundary=bnd_matrix_17_44, switch=sw_matrix_17_44, hash_hint=cc931037b97564bf"
  },
  {
    "matrix_row_id": "matrix_017_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 17: validator observes canonical read-only evidence and compares 1 registries against policy segment 17.",
    "bad_pattern": "bad pattern 45 in matrix 17: writer drift toward family 3, generated path reports_real/segment_17_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_17_45, boundary=bnd_matrix_17_45, switch=sw_matrix_17_45, hash_hint=e9f7b0d59db670d2"
  },
  {
    "matrix_row_id": "matrix_017_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 17: validator observes canonical read-only evidence and compares 2 registries against policy segment 17.",
    "bad_pattern": "bad pattern 46 in matrix 17: writer drift toward family 4, generated path reports_real/segment_17_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_17_46, boundary=bnd_matrix_17_46, switch=sw_matrix_17_46, hash_hint=c1a1e153922e33a1"
  },
  {
    "matrix_row_id": "matrix_017_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 17: validator observes canonical read-only evidence and compares 3 registries against policy segment 17.",
    "bad_pattern": "bad pattern 47 in matrix 17: writer drift toward family 5, generated path reports_real/segment_17_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_17_47, boundary=bnd_matrix_17_47, switch=sw_matrix_17_47, hash_hint=a3fcdb72524210cb"
  },
  {
    "matrix_row_id": "matrix_017_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 17: validator observes canonical read-only evidence and compares 4 registries against policy segment 17.",
    "bad_pattern": "bad pattern 48 in matrix 17: writer drift toward family 6, generated path reports_real/segment_17_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_17_48, boundary=bnd_matrix_17_48, switch=sw_matrix_17_48, hash_hint=129ae9724662d7a2"
  },
  {
    "matrix_row_id": "matrix_017_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 17: validator observes canonical read-only evidence and compares 5 registries against policy segment 17.",
    "bad_pattern": "bad pattern 49 in matrix 17: writer drift toward family 0, generated path reports_real/segment_17_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_17_49, boundary=bnd_matrix_17_49, switch=sw_matrix_17_49, hash_hint=4e85ab00a8392e36"
  },
  {
    "matrix_row_id": "matrix_017_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 17: validator observes canonical read-only evidence and compares 1 registries against policy segment 17.",
    "bad_pattern": "bad pattern 50 in matrix 17: writer drift toward family 1, generated path reports_real/segment_17_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_17_50, boundary=bnd_matrix_17_50, switch=sw_matrix_17_50, hash_hint=cf77f23e2557bd0f"
  },
  {
    "matrix_row_id": "matrix_017_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 17: validator observes canonical read-only evidence and compares 2 registries against policy segment 17.",
    "bad_pattern": "bad pattern 51 in matrix 17: writer drift toward family 2, generated path reports_real/segment_17_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_17_51, boundary=bnd_matrix_17_51, switch=sw_matrix_17_51, hash_hint=a0677e7b50de91a5"
  },
  {
    "matrix_row_id": "matrix_017_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 17: validator observes canonical read-only evidence and compares 3 registries against policy segment 17.",
    "bad_pattern": "bad pattern 52 in matrix 17: writer drift toward family 3, generated path reports_real/segment_17_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_17_52, boundary=bnd_matrix_17_52, switch=sw_matrix_17_52, hash_hint=e7092b9c62e0c457"
  },
  {
    "matrix_row_id": "matrix_017_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 17: validator observes canonical read-only evidence and compares 4 registries against policy segment 17.",
    "bad_pattern": "bad pattern 53 in matrix 17: writer drift toward family 4, generated path reports_real/segment_17_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_17_53, boundary=bnd_matrix_17_53, switch=sw_matrix_17_53, hash_hint=65e2bac7b8d518eb"
  },
  {
    "matrix_row_id": "matrix_017_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 17: validator observes canonical read-only evidence and compares 5 registries against policy segment 17.",
    "bad_pattern": "bad pattern 54 in matrix 17: writer drift toward family 5, generated path reports_real/segment_17_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_17_54, boundary=bnd_matrix_17_54, switch=sw_matrix_17_54, hash_hint=1c1449dee6043158"
  },
  {
    "matrix_row_id": "matrix_017_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 17: validator observes canonical read-only evidence and compares 1 registries against policy segment 17.",
    "bad_pattern": "bad pattern 55 in matrix 17: writer drift toward family 6, generated path reports_real/segment_17_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_17_55, boundary=bnd_matrix_17_55, switch=sw_matrix_17_55, hash_hint=445b3b839d354289"
  },
  {
    "matrix_row_id": "matrix_017_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 17: validator observes canonical read-only evidence and compares 2 registries against policy segment 17.",
    "bad_pattern": "bad pattern 56 in matrix 17: writer drift toward family 0, generated path reports_real/segment_17_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_17_56, boundary=bnd_matrix_17_56, switch=sw_matrix_17_56, hash_hint=923c58ef289c1823"
  },
  {
    "matrix_row_id": "matrix_017_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 17: validator observes canonical read-only evidence and compares 3 registries against policy segment 17.",
    "bad_pattern": "bad pattern 57 in matrix 17: writer drift toward family 1, generated path reports_real/segment_17_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_17_57, boundary=bnd_matrix_17_57, switch=sw_matrix_17_57, hash_hint=5a2a7b3b530bb35b"
  },
  {
    "matrix_row_id": "matrix_017_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 17: validator observes canonical read-only evidence and compares 4 registries against policy segment 17.",
    "bad_pattern": "bad pattern 58 in matrix 17: writer drift toward family 2, generated path reports_real/segment_17_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_17_58, boundary=bnd_matrix_17_58, switch=sw_matrix_17_58, hash_hint=db86bda43ba50206"
  },
  {
    "matrix_row_id": "matrix_017_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 17: validator observes canonical read-only evidence and compares 5 registries against policy segment 17.",
    "bad_pattern": "bad pattern 59 in matrix 17: writer drift toward family 3, generated path reports_real/segment_17_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_17_59, boundary=bnd_matrix_17_59, switch=sw_matrix_17_59, hash_hint=26c4f0574bc1c488"
  },
  {
    "matrix_row_id": "matrix_017_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 17: validator observes canonical read-only evidence and compares 1 registries against policy segment 17.",
    "bad_pattern": "bad pattern 60 in matrix 17: writer drift toward family 4, generated path reports_real/segment_17_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_17_60, boundary=bnd_matrix_17_60, switch=sw_matrix_17_60, hash_hint=bdbf3cb818bac27f"
  }
]
