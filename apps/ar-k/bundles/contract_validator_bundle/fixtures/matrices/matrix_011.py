from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 11/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 11/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 11/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 11/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 11/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 11/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 11/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 11/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 11/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 11/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 11/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 11/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 11/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 11/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 11/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 11/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 11/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 11/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 11/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 11/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 11/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 11/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 11/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 11/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 11/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_011_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 11: validator observes canonical read-only evidence and compares 2 registries against policy segment 11.",
    "bad_pattern": "bad pattern 1 in matrix 11: writer drift toward family 1, generated path reports_real/segment_11_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_11_1, boundary=bnd_matrix_11_1, switch=sw_matrix_11_1, hash_hint=4ab6a0ad4b50df2e"
  },
  {
    "matrix_row_id": "matrix_011_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 11: validator observes canonical read-only evidence and compares 3 registries against policy segment 11.",
    "bad_pattern": "bad pattern 2 in matrix 11: writer drift toward family 2, generated path reports_real/segment_11_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_11_2, boundary=bnd_matrix_11_2, switch=sw_matrix_11_2, hash_hint=87a5225e6c3fcfe8"
  },
  {
    "matrix_row_id": "matrix_011_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 11: validator observes canonical read-only evidence and compares 4 registries against policy segment 11.",
    "bad_pattern": "bad pattern 3 in matrix 11: writer drift toward family 3, generated path reports_real/segment_11_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_11_3, boundary=bnd_matrix_11_3, switch=sw_matrix_11_3, hash_hint=54012f629dd8f777"
  },
  {
    "matrix_row_id": "matrix_011_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 11: validator observes canonical read-only evidence and compares 5 registries against policy segment 11.",
    "bad_pattern": "bad pattern 4 in matrix 11: writer drift toward family 4, generated path reports_real/segment_11_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_11_4, boundary=bnd_matrix_11_4, switch=sw_matrix_11_4, hash_hint=476816350fa1e891"
  },
  {
    "matrix_row_id": "matrix_011_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 11: validator observes canonical read-only evidence and compares 1 registries against policy segment 11.",
    "bad_pattern": "bad pattern 5 in matrix 11: writer drift toward family 5, generated path reports_real/segment_11_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_11_5, boundary=bnd_matrix_11_5, switch=sw_matrix_11_5, hash_hint=d3025b31250a5f5d"
  },
  {
    "matrix_row_id": "matrix_011_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 11: validator observes canonical read-only evidence and compares 2 registries against policy segment 11.",
    "bad_pattern": "bad pattern 6 in matrix 11: writer drift toward family 6, generated path reports_real/segment_11_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_11_6, boundary=bnd_matrix_11_6, switch=sw_matrix_11_6, hash_hint=daa9eba5d3593f38"
  },
  {
    "matrix_row_id": "matrix_011_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 11: validator observes canonical read-only evidence and compares 3 registries against policy segment 11.",
    "bad_pattern": "bad pattern 7 in matrix 11: writer drift toward family 0, generated path reports_real/segment_11_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_11_7, boundary=bnd_matrix_11_7, switch=sw_matrix_11_7, hash_hint=a345e92d3b3398fd"
  },
  {
    "matrix_row_id": "matrix_011_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 11: validator observes canonical read-only evidence and compares 4 registries against policy segment 11.",
    "bad_pattern": "bad pattern 8 in matrix 11: writer drift toward family 1, generated path reports_real/segment_11_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_11_8, boundary=bnd_matrix_11_8, switch=sw_matrix_11_8, hash_hint=9c83431d75073fa2"
  },
  {
    "matrix_row_id": "matrix_011_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 11: validator observes canonical read-only evidence and compares 5 registries against policy segment 11.",
    "bad_pattern": "bad pattern 9 in matrix 11: writer drift toward family 2, generated path reports_real/segment_11_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_11_9, boundary=bnd_matrix_11_9, switch=sw_matrix_11_9, hash_hint=d05113ee90f30db5"
  },
  {
    "matrix_row_id": "matrix_011_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 11: validator observes canonical read-only evidence and compares 1 registries against policy segment 11.",
    "bad_pattern": "bad pattern 10 in matrix 11: writer drift toward family 3, generated path reports_real/segment_11_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_11_10, boundary=bnd_matrix_11_10, switch=sw_matrix_11_10, hash_hint=0aee25d9fd6d2c53"
  },
  {
    "matrix_row_id": "matrix_011_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 11: validator observes canonical read-only evidence and compares 2 registries against policy segment 11.",
    "bad_pattern": "bad pattern 11 in matrix 11: writer drift toward family 4, generated path reports_real/segment_11_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_11_11, boundary=bnd_matrix_11_11, switch=sw_matrix_11_11, hash_hint=5e5c0a43cf1c7ed1"
  },
  {
    "matrix_row_id": "matrix_011_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 11: validator observes canonical read-only evidence and compares 3 registries against policy segment 11.",
    "bad_pattern": "bad pattern 12 in matrix 11: writer drift toward family 5, generated path reports_real/segment_11_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_11_12, boundary=bnd_matrix_11_12, switch=sw_matrix_11_12, hash_hint=c56918c131dafc49"
  },
  {
    "matrix_row_id": "matrix_011_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 11: validator observes canonical read-only evidence and compares 4 registries against policy segment 11.",
    "bad_pattern": "bad pattern 13 in matrix 11: writer drift toward family 6, generated path reports_real/segment_11_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_11_13, boundary=bnd_matrix_11_13, switch=sw_matrix_11_13, hash_hint=95170bc42371b9d6"
  },
  {
    "matrix_row_id": "matrix_011_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 11: validator observes canonical read-only evidence and compares 5 registries against policy segment 11.",
    "bad_pattern": "bad pattern 14 in matrix 11: writer drift toward family 0, generated path reports_real/segment_11_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_11_14, boundary=bnd_matrix_11_14, switch=sw_matrix_11_14, hash_hint=c2a7f21cb79a18b4"
  },
  {
    "matrix_row_id": "matrix_011_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 11: validator observes canonical read-only evidence and compares 1 registries against policy segment 11.",
    "bad_pattern": "bad pattern 15 in matrix 11: writer drift toward family 1, generated path reports_real/segment_11_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_11_15, boundary=bnd_matrix_11_15, switch=sw_matrix_11_15, hash_hint=be5671df55f9ace5"
  },
  {
    "matrix_row_id": "matrix_011_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 11: validator observes canonical read-only evidence and compares 2 registries against policy segment 11.",
    "bad_pattern": "bad pattern 16 in matrix 11: writer drift toward family 2, generated path reports_real/segment_11_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_11_16, boundary=bnd_matrix_11_16, switch=sw_matrix_11_16, hash_hint=1d9e42e6c2e94356"
  },
  {
    "matrix_row_id": "matrix_011_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 11: validator observes canonical read-only evidence and compares 3 registries against policy segment 11.",
    "bad_pattern": "bad pattern 17 in matrix 11: writer drift toward family 3, generated path reports_real/segment_11_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_11_17, boundary=bnd_matrix_11_17, switch=sw_matrix_11_17, hash_hint=f7a956df55b6dc3a"
  },
  {
    "matrix_row_id": "matrix_011_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 11: validator observes canonical read-only evidence and compares 4 registries against policy segment 11.",
    "bad_pattern": "bad pattern 18 in matrix 11: writer drift toward family 4, generated path reports_real/segment_11_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_11_18, boundary=bnd_matrix_11_18, switch=sw_matrix_11_18, hash_hint=58b1b525957bdc4d"
  },
  {
    "matrix_row_id": "matrix_011_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 11: validator observes canonical read-only evidence and compares 5 registries against policy segment 11.",
    "bad_pattern": "bad pattern 19 in matrix 11: writer drift toward family 5, generated path reports_real/segment_11_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_11_19, boundary=bnd_matrix_11_19, switch=sw_matrix_11_19, hash_hint=a58ce9d511b02c6f"
  },
  {
    "matrix_row_id": "matrix_011_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 11: validator observes canonical read-only evidence and compares 1 registries against policy segment 11.",
    "bad_pattern": "bad pattern 20 in matrix 11: writer drift toward family 6, generated path reports_real/segment_11_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_11_20, boundary=bnd_matrix_11_20, switch=sw_matrix_11_20, hash_hint=09c81a54ecc05950"
  },
  {
    "matrix_row_id": "matrix_011_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 11: validator observes canonical read-only evidence and compares 2 registries against policy segment 11.",
    "bad_pattern": "bad pattern 21 in matrix 11: writer drift toward family 0, generated path reports_real/segment_11_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_11_21, boundary=bnd_matrix_11_21, switch=sw_matrix_11_21, hash_hint=72230fbf7388b105"
  },
  {
    "matrix_row_id": "matrix_011_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 11: validator observes canonical read-only evidence and compares 3 registries against policy segment 11.",
    "bad_pattern": "bad pattern 22 in matrix 11: writer drift toward family 1, generated path reports_real/segment_11_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_11_22, boundary=bnd_matrix_11_22, switch=sw_matrix_11_22, hash_hint=b669a1d744274e34"
  },
  {
    "matrix_row_id": "matrix_011_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 11: validator observes canonical read-only evidence and compares 4 registries against policy segment 11.",
    "bad_pattern": "bad pattern 23 in matrix 11: writer drift toward family 2, generated path reports_real/segment_11_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_11_23, boundary=bnd_matrix_11_23, switch=sw_matrix_11_23, hash_hint=fd4110cca49a4548"
  },
  {
    "matrix_row_id": "matrix_011_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 11: validator observes canonical read-only evidence and compares 5 registries against policy segment 11.",
    "bad_pattern": "bad pattern 24 in matrix 11: writer drift toward family 3, generated path reports_real/segment_11_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_11_24, boundary=bnd_matrix_11_24, switch=sw_matrix_11_24, hash_hint=ba8b32d3cfb74725"
  },
  {
    "matrix_row_id": "matrix_011_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 11: validator observes canonical read-only evidence and compares 1 registries against policy segment 11.",
    "bad_pattern": "bad pattern 25 in matrix 11: writer drift toward family 4, generated path reports_real/segment_11_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_11_25, boundary=bnd_matrix_11_25, switch=sw_matrix_11_25, hash_hint=d12265d683ca55dd"
  },
  {
    "matrix_row_id": "matrix_011_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 11: validator observes canonical read-only evidence and compares 2 registries against policy segment 11.",
    "bad_pattern": "bad pattern 26 in matrix 11: writer drift toward family 5, generated path reports_real/segment_11_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_11_26, boundary=bnd_matrix_11_26, switch=sw_matrix_11_26, hash_hint=fb549a44def3a2ec"
  },
  {
    "matrix_row_id": "matrix_011_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 11: validator observes canonical read-only evidence and compares 3 registries against policy segment 11.",
    "bad_pattern": "bad pattern 27 in matrix 11: writer drift toward family 6, generated path reports_real/segment_11_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_11_27, boundary=bnd_matrix_11_27, switch=sw_matrix_11_27, hash_hint=1f20be6766bd7c21"
  },
  {
    "matrix_row_id": "matrix_011_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 11: validator observes canonical read-only evidence and compares 4 registries against policy segment 11.",
    "bad_pattern": "bad pattern 28 in matrix 11: writer drift toward family 0, generated path reports_real/segment_11_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_11_28, boundary=bnd_matrix_11_28, switch=sw_matrix_11_28, hash_hint=5c0bb240132a7305"
  },
  {
    "matrix_row_id": "matrix_011_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 11: validator observes canonical read-only evidence and compares 5 registries against policy segment 11.",
    "bad_pattern": "bad pattern 29 in matrix 11: writer drift toward family 1, generated path reports_real/segment_11_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_11_29, boundary=bnd_matrix_11_29, switch=sw_matrix_11_29, hash_hint=a90266e6e316f655"
  },
  {
    "matrix_row_id": "matrix_011_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 11: validator observes canonical read-only evidence and compares 1 registries against policy segment 11.",
    "bad_pattern": "bad pattern 30 in matrix 11: writer drift toward family 2, generated path reports_real/segment_11_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_11_30, boundary=bnd_matrix_11_30, switch=sw_matrix_11_30, hash_hint=9d87a1f63c22fcf2"
  },
  {
    "matrix_row_id": "matrix_011_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 11: validator observes canonical read-only evidence and compares 2 registries against policy segment 11.",
    "bad_pattern": "bad pattern 31 in matrix 11: writer drift toward family 3, generated path reports_real/segment_11_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_11_31, boundary=bnd_matrix_11_31, switch=sw_matrix_11_31, hash_hint=de1973ae5c5c5934"
  },
  {
    "matrix_row_id": "matrix_011_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 11: validator observes canonical read-only evidence and compares 3 registries against policy segment 11.",
    "bad_pattern": "bad pattern 32 in matrix 11: writer drift toward family 4, generated path reports_real/segment_11_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_11_32, boundary=bnd_matrix_11_32, switch=sw_matrix_11_32, hash_hint=d8f2ee9dbec8c883"
  },
  {
    "matrix_row_id": "matrix_011_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 11: validator observes canonical read-only evidence and compares 4 registries against policy segment 11.",
    "bad_pattern": "bad pattern 33 in matrix 11: writer drift toward family 5, generated path reports_real/segment_11_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_11_33, boundary=bnd_matrix_11_33, switch=sw_matrix_11_33, hash_hint=d5fb00e0ae7e00f1"
  },
  {
    "matrix_row_id": "matrix_011_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 11: validator observes canonical read-only evidence and compares 5 registries against policy segment 11.",
    "bad_pattern": "bad pattern 34 in matrix 11: writer drift toward family 6, generated path reports_real/segment_11_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_11_34, boundary=bnd_matrix_11_34, switch=sw_matrix_11_34, hash_hint=073d386841df9c32"
  },
  {
    "matrix_row_id": "matrix_011_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 11: validator observes canonical read-only evidence and compares 1 registries against policy segment 11.",
    "bad_pattern": "bad pattern 35 in matrix 11: writer drift toward family 0, generated path reports_real/segment_11_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_11_35, boundary=bnd_matrix_11_35, switch=sw_matrix_11_35, hash_hint=27c5c15489d81035"
  },
  {
    "matrix_row_id": "matrix_011_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 11: validator observes canonical read-only evidence and compares 2 registries against policy segment 11.",
    "bad_pattern": "bad pattern 36 in matrix 11: writer drift toward family 1, generated path reports_real/segment_11_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_11_36, boundary=bnd_matrix_11_36, switch=sw_matrix_11_36, hash_hint=0ac1dd86c0ffe1da"
  },
  {
    "matrix_row_id": "matrix_011_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 11: validator observes canonical read-only evidence and compares 3 registries against policy segment 11.",
    "bad_pattern": "bad pattern 37 in matrix 11: writer drift toward family 2, generated path reports_real/segment_11_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_11_37, boundary=bnd_matrix_11_37, switch=sw_matrix_11_37, hash_hint=12776d91b239bf76"
  },
  {
    "matrix_row_id": "matrix_011_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 11: validator observes canonical read-only evidence and compares 4 registries against policy segment 11.",
    "bad_pattern": "bad pattern 38 in matrix 11: writer drift toward family 3, generated path reports_real/segment_11_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_11_38, boundary=bnd_matrix_11_38, switch=sw_matrix_11_38, hash_hint=fd278c2d38575f73"
  },
  {
    "matrix_row_id": "matrix_011_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 11: validator observes canonical read-only evidence and compares 5 registries against policy segment 11.",
    "bad_pattern": "bad pattern 39 in matrix 11: writer drift toward family 4, generated path reports_real/segment_11_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_11_39, boundary=bnd_matrix_11_39, switch=sw_matrix_11_39, hash_hint=70b53c22f9f6688e"
  },
  {
    "matrix_row_id": "matrix_011_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 11: validator observes canonical read-only evidence and compares 1 registries against policy segment 11.",
    "bad_pattern": "bad pattern 40 in matrix 11: writer drift toward family 5, generated path reports_real/segment_11_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_11_40, boundary=bnd_matrix_11_40, switch=sw_matrix_11_40, hash_hint=a14f6d15f673b583"
  },
  {
    "matrix_row_id": "matrix_011_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 11: validator observes canonical read-only evidence and compares 2 registries against policy segment 11.",
    "bad_pattern": "bad pattern 41 in matrix 11: writer drift toward family 6, generated path reports_real/segment_11_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_11_41, boundary=bnd_matrix_11_41, switch=sw_matrix_11_41, hash_hint=444eeffbc233834d"
  },
  {
    "matrix_row_id": "matrix_011_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 11: validator observes canonical read-only evidence and compares 3 registries against policy segment 11.",
    "bad_pattern": "bad pattern 42 in matrix 11: writer drift toward family 0, generated path reports_real/segment_11_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_11_42, boundary=bnd_matrix_11_42, switch=sw_matrix_11_42, hash_hint=b0396a65496e9b81"
  },
  {
    "matrix_row_id": "matrix_011_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 11: validator observes canonical read-only evidence and compares 4 registries against policy segment 11.",
    "bad_pattern": "bad pattern 43 in matrix 11: writer drift toward family 1, generated path reports_real/segment_11_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_11_43, boundary=bnd_matrix_11_43, switch=sw_matrix_11_43, hash_hint=069c324774cc566e"
  },
  {
    "matrix_row_id": "matrix_011_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 11: validator observes canonical read-only evidence and compares 5 registries against policy segment 11.",
    "bad_pattern": "bad pattern 44 in matrix 11: writer drift toward family 2, generated path reports_real/segment_11_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_11_44, boundary=bnd_matrix_11_44, switch=sw_matrix_11_44, hash_hint=bb58e7e1959eae45"
  },
  {
    "matrix_row_id": "matrix_011_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 11: validator observes canonical read-only evidence and compares 1 registries against policy segment 11.",
    "bad_pattern": "bad pattern 45 in matrix 11: writer drift toward family 3, generated path reports_real/segment_11_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_11_45, boundary=bnd_matrix_11_45, switch=sw_matrix_11_45, hash_hint=4c6dd8c02326941e"
  },
  {
    "matrix_row_id": "matrix_011_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 11: validator observes canonical read-only evidence and compares 2 registries against policy segment 11.",
    "bad_pattern": "bad pattern 46 in matrix 11: writer drift toward family 4, generated path reports_real/segment_11_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_11_46, boundary=bnd_matrix_11_46, switch=sw_matrix_11_46, hash_hint=dc31bd9a49e863b2"
  },
  {
    "matrix_row_id": "matrix_011_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 11: validator observes canonical read-only evidence and compares 3 registries against policy segment 11.",
    "bad_pattern": "bad pattern 47 in matrix 11: writer drift toward family 5, generated path reports_real/segment_11_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_11_47, boundary=bnd_matrix_11_47, switch=sw_matrix_11_47, hash_hint=6feb6c02565a5fc4"
  },
  {
    "matrix_row_id": "matrix_011_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 11: validator observes canonical read-only evidence and compares 4 registries against policy segment 11.",
    "bad_pattern": "bad pattern 48 in matrix 11: writer drift toward family 6, generated path reports_real/segment_11_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_11_48, boundary=bnd_matrix_11_48, switch=sw_matrix_11_48, hash_hint=629f28e9c88c0b0d"
  },
  {
    "matrix_row_id": "matrix_011_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 11: validator observes canonical read-only evidence and compares 5 registries against policy segment 11.",
    "bad_pattern": "bad pattern 49 in matrix 11: writer drift toward family 0, generated path reports_real/segment_11_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_11_49, boundary=bnd_matrix_11_49, switch=sw_matrix_11_49, hash_hint=5b2a408af095512f"
  },
  {
    "matrix_row_id": "matrix_011_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 11: validator observes canonical read-only evidence and compares 1 registries against policy segment 11.",
    "bad_pattern": "bad pattern 50 in matrix 11: writer drift toward family 1, generated path reports_real/segment_11_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_11_50, boundary=bnd_matrix_11_50, switch=sw_matrix_11_50, hash_hint=8a770760a76bbfed"
  },
  {
    "matrix_row_id": "matrix_011_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 11: validator observes canonical read-only evidence and compares 2 registries against policy segment 11.",
    "bad_pattern": "bad pattern 51 in matrix 11: writer drift toward family 2, generated path reports_real/segment_11_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_11_51, boundary=bnd_matrix_11_51, switch=sw_matrix_11_51, hash_hint=0c3599592eb87b14"
  },
  {
    "matrix_row_id": "matrix_011_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 11: validator observes canonical read-only evidence and compares 3 registries against policy segment 11.",
    "bad_pattern": "bad pattern 52 in matrix 11: writer drift toward family 3, generated path reports_real/segment_11_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_11_52, boundary=bnd_matrix_11_52, switch=sw_matrix_11_52, hash_hint=276e2de9a862de1a"
  },
  {
    "matrix_row_id": "matrix_011_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 11: validator observes canonical read-only evidence and compares 4 registries against policy segment 11.",
    "bad_pattern": "bad pattern 53 in matrix 11: writer drift toward family 4, generated path reports_real/segment_11_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_11_53, boundary=bnd_matrix_11_53, switch=sw_matrix_11_53, hash_hint=854594418de42d23"
  },
  {
    "matrix_row_id": "matrix_011_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 11: validator observes canonical read-only evidence and compares 5 registries against policy segment 11.",
    "bad_pattern": "bad pattern 54 in matrix 11: writer drift toward family 5, generated path reports_real/segment_11_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_11_54, boundary=bnd_matrix_11_54, switch=sw_matrix_11_54, hash_hint=699cb2a6dd4853a4"
  },
  {
    "matrix_row_id": "matrix_011_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 11: validator observes canonical read-only evidence and compares 1 registries against policy segment 11.",
    "bad_pattern": "bad pattern 55 in matrix 11: writer drift toward family 6, generated path reports_real/segment_11_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_11_55, boundary=bnd_matrix_11_55, switch=sw_matrix_11_55, hash_hint=671d9bb1b2efa5f9"
  },
  {
    "matrix_row_id": "matrix_011_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 11: validator observes canonical read-only evidence and compares 2 registries against policy segment 11.",
    "bad_pattern": "bad pattern 56 in matrix 11: writer drift toward family 0, generated path reports_real/segment_11_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_11_56, boundary=bnd_matrix_11_56, switch=sw_matrix_11_56, hash_hint=74bf7826be6958d6"
  },
  {
    "matrix_row_id": "matrix_011_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 11: validator observes canonical read-only evidence and compares 3 registries against policy segment 11.",
    "bad_pattern": "bad pattern 57 in matrix 11: writer drift toward family 1, generated path reports_real/segment_11_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_11_57, boundary=bnd_matrix_11_57, switch=sw_matrix_11_57, hash_hint=bd4e134d8c8fb634"
  },
  {
    "matrix_row_id": "matrix_011_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 11: validator observes canonical read-only evidence and compares 4 registries against policy segment 11.",
    "bad_pattern": "bad pattern 58 in matrix 11: writer drift toward family 2, generated path reports_real/segment_11_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_11_58, boundary=bnd_matrix_11_58, switch=sw_matrix_11_58, hash_hint=a2ced414e050d97a"
  },
  {
    "matrix_row_id": "matrix_011_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 11: validator observes canonical read-only evidence and compares 5 registries against policy segment 11.",
    "bad_pattern": "bad pattern 59 in matrix 11: writer drift toward family 3, generated path reports_real/segment_11_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_11_59, boundary=bnd_matrix_11_59, switch=sw_matrix_11_59, hash_hint=66897fa9cb5ce99b"
  },
  {
    "matrix_row_id": "matrix_011_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 11: validator observes canonical read-only evidence and compares 1 registries against policy segment 11.",
    "bad_pattern": "bad pattern 60 in matrix 11: writer drift toward family 4, generated path reports_real/segment_11_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_11_60, boundary=bnd_matrix_11_60, switch=sw_matrix_11_60, hash_hint=500f993550df2098"
  }
]
