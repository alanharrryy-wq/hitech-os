from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 30/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 30/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 30/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 30/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 30/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 30/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 30/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 30/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 30/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 30/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 30/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 30/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 30/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 30/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 30/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 30/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 30/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 30/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 30/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 30/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 30/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 30/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 30/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 30/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 30/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_030_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 30: validator observes canonical read-only evidence and compares 2 registries against policy segment 30.",
    "bad_pattern": "bad pattern 1 in matrix 30: writer drift toward family 1, generated path reports_real/segment_30_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_30_1, boundary=bnd_matrix_30_1, switch=sw_matrix_30_1, hash_hint=68c52c38214af126"
  },
  {
    "matrix_row_id": "matrix_030_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 30: validator observes canonical read-only evidence and compares 3 registries against policy segment 30.",
    "bad_pattern": "bad pattern 2 in matrix 30: writer drift toward family 2, generated path reports_real/segment_30_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_30_2, boundary=bnd_matrix_30_2, switch=sw_matrix_30_2, hash_hint=d126327ad54f5fe7"
  },
  {
    "matrix_row_id": "matrix_030_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 30: validator observes canonical read-only evidence and compares 4 registries against policy segment 30.",
    "bad_pattern": "bad pattern 3 in matrix 30: writer drift toward family 3, generated path reports_real/segment_30_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_30_3, boundary=bnd_matrix_30_3, switch=sw_matrix_30_3, hash_hint=42e5da0d7cd775c3"
  },
  {
    "matrix_row_id": "matrix_030_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 30: validator observes canonical read-only evidence and compares 5 registries against policy segment 30.",
    "bad_pattern": "bad pattern 4 in matrix 30: writer drift toward family 4, generated path reports_real/segment_30_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_30_4, boundary=bnd_matrix_30_4, switch=sw_matrix_30_4, hash_hint=5e9f57f747d7a250"
  },
  {
    "matrix_row_id": "matrix_030_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 30: validator observes canonical read-only evidence and compares 1 registries against policy segment 30.",
    "bad_pattern": "bad pattern 5 in matrix 30: writer drift toward family 5, generated path reports_real/segment_30_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_30_5, boundary=bnd_matrix_30_5, switch=sw_matrix_30_5, hash_hint=ffa661cf7fb54f52"
  },
  {
    "matrix_row_id": "matrix_030_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 30: validator observes canonical read-only evidence and compares 2 registries against policy segment 30.",
    "bad_pattern": "bad pattern 6 in matrix 30: writer drift toward family 6, generated path reports_real/segment_30_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_30_6, boundary=bnd_matrix_30_6, switch=sw_matrix_30_6, hash_hint=445dcea0e36a1104"
  },
  {
    "matrix_row_id": "matrix_030_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 30: validator observes canonical read-only evidence and compares 3 registries against policy segment 30.",
    "bad_pattern": "bad pattern 7 in matrix 30: writer drift toward family 0, generated path reports_real/segment_30_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_30_7, boundary=bnd_matrix_30_7, switch=sw_matrix_30_7, hash_hint=1befb65f63588eb1"
  },
  {
    "matrix_row_id": "matrix_030_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 30: validator observes canonical read-only evidence and compares 4 registries against policy segment 30.",
    "bad_pattern": "bad pattern 8 in matrix 30: writer drift toward family 1, generated path reports_real/segment_30_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_30_8, boundary=bnd_matrix_30_8, switch=sw_matrix_30_8, hash_hint=033296b6360d424d"
  },
  {
    "matrix_row_id": "matrix_030_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 30: validator observes canonical read-only evidence and compares 5 registries against policy segment 30.",
    "bad_pattern": "bad pattern 9 in matrix 30: writer drift toward family 2, generated path reports_real/segment_30_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_30_9, boundary=bnd_matrix_30_9, switch=sw_matrix_30_9, hash_hint=638f1b07a094b7f3"
  },
  {
    "matrix_row_id": "matrix_030_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 30: validator observes canonical read-only evidence and compares 1 registries against policy segment 30.",
    "bad_pattern": "bad pattern 10 in matrix 30: writer drift toward family 3, generated path reports_real/segment_30_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_30_10, boundary=bnd_matrix_30_10, switch=sw_matrix_30_10, hash_hint=1c71ee940b3f6467"
  },
  {
    "matrix_row_id": "matrix_030_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 30: validator observes canonical read-only evidence and compares 2 registries against policy segment 30.",
    "bad_pattern": "bad pattern 11 in matrix 30: writer drift toward family 4, generated path reports_real/segment_30_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_30_11, boundary=bnd_matrix_30_11, switch=sw_matrix_30_11, hash_hint=6262c59951e05a6f"
  },
  {
    "matrix_row_id": "matrix_030_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 30: validator observes canonical read-only evidence and compares 3 registries against policy segment 30.",
    "bad_pattern": "bad pattern 12 in matrix 30: writer drift toward family 5, generated path reports_real/segment_30_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_30_12, boundary=bnd_matrix_30_12, switch=sw_matrix_30_12, hash_hint=36ababa46cbb0be5"
  },
  {
    "matrix_row_id": "matrix_030_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 30: validator observes canonical read-only evidence and compares 4 registries against policy segment 30.",
    "bad_pattern": "bad pattern 13 in matrix 30: writer drift toward family 6, generated path reports_real/segment_30_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_30_13, boundary=bnd_matrix_30_13, switch=sw_matrix_30_13, hash_hint=7ef28d3ea189bb19"
  },
  {
    "matrix_row_id": "matrix_030_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 30: validator observes canonical read-only evidence and compares 5 registries against policy segment 30.",
    "bad_pattern": "bad pattern 14 in matrix 30: writer drift toward family 0, generated path reports_real/segment_30_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_30_14, boundary=bnd_matrix_30_14, switch=sw_matrix_30_14, hash_hint=eb58a308504f8f68"
  },
  {
    "matrix_row_id": "matrix_030_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 30: validator observes canonical read-only evidence and compares 1 registries against policy segment 30.",
    "bad_pattern": "bad pattern 15 in matrix 30: writer drift toward family 1, generated path reports_real/segment_30_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_30_15, boundary=bnd_matrix_30_15, switch=sw_matrix_30_15, hash_hint=7bf62c406b7d88ae"
  },
  {
    "matrix_row_id": "matrix_030_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 30: validator observes canonical read-only evidence and compares 2 registries against policy segment 30.",
    "bad_pattern": "bad pattern 16 in matrix 30: writer drift toward family 2, generated path reports_real/segment_30_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_30_16, boundary=bnd_matrix_30_16, switch=sw_matrix_30_16, hash_hint=30714c2649bbcc95"
  },
  {
    "matrix_row_id": "matrix_030_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 30: validator observes canonical read-only evidence and compares 3 registries against policy segment 30.",
    "bad_pattern": "bad pattern 17 in matrix 30: writer drift toward family 3, generated path reports_real/segment_30_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_30_17, boundary=bnd_matrix_30_17, switch=sw_matrix_30_17, hash_hint=1352416d4d8c5d93"
  },
  {
    "matrix_row_id": "matrix_030_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 30: validator observes canonical read-only evidence and compares 4 registries against policy segment 30.",
    "bad_pattern": "bad pattern 18 in matrix 30: writer drift toward family 4, generated path reports_real/segment_30_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_30_18, boundary=bnd_matrix_30_18, switch=sw_matrix_30_18, hash_hint=37e60da02806d5a2"
  },
  {
    "matrix_row_id": "matrix_030_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 30: validator observes canonical read-only evidence and compares 5 registries against policy segment 30.",
    "bad_pattern": "bad pattern 19 in matrix 30: writer drift toward family 5, generated path reports_real/segment_30_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_30_19, boundary=bnd_matrix_30_19, switch=sw_matrix_30_19, hash_hint=02d2b96cdfa7008a"
  },
  {
    "matrix_row_id": "matrix_030_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 30: validator observes canonical read-only evidence and compares 1 registries against policy segment 30.",
    "bad_pattern": "bad pattern 20 in matrix 30: writer drift toward family 6, generated path reports_real/segment_30_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_30_20, boundary=bnd_matrix_30_20, switch=sw_matrix_30_20, hash_hint=ad1b1047a45fdd39"
  },
  {
    "matrix_row_id": "matrix_030_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 30: validator observes canonical read-only evidence and compares 2 registries against policy segment 30.",
    "bad_pattern": "bad pattern 21 in matrix 30: writer drift toward family 0, generated path reports_real/segment_30_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_30_21, boundary=bnd_matrix_30_21, switch=sw_matrix_30_21, hash_hint=aec3a059c3905561"
  },
  {
    "matrix_row_id": "matrix_030_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 30: validator observes canonical read-only evidence and compares 3 registries against policy segment 30.",
    "bad_pattern": "bad pattern 22 in matrix 30: writer drift toward family 1, generated path reports_real/segment_30_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_30_22, boundary=bnd_matrix_30_22, switch=sw_matrix_30_22, hash_hint=efa342f1dd2356eb"
  },
  {
    "matrix_row_id": "matrix_030_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 30: validator observes canonical read-only evidence and compares 4 registries against policy segment 30.",
    "bad_pattern": "bad pattern 23 in matrix 30: writer drift toward family 2, generated path reports_real/segment_30_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_30_23, boundary=bnd_matrix_30_23, switch=sw_matrix_30_23, hash_hint=7960a9b6d6187ee1"
  },
  {
    "matrix_row_id": "matrix_030_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 30: validator observes canonical read-only evidence and compares 5 registries against policy segment 30.",
    "bad_pattern": "bad pattern 24 in matrix 30: writer drift toward family 3, generated path reports_real/segment_30_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_30_24, boundary=bnd_matrix_30_24, switch=sw_matrix_30_24, hash_hint=b397be1fcde1df07"
  },
  {
    "matrix_row_id": "matrix_030_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 30: validator observes canonical read-only evidence and compares 1 registries against policy segment 30.",
    "bad_pattern": "bad pattern 25 in matrix 30: writer drift toward family 4, generated path reports_real/segment_30_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_30_25, boundary=bnd_matrix_30_25, switch=sw_matrix_30_25, hash_hint=c07de11f94f87b68"
  },
  {
    "matrix_row_id": "matrix_030_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 30: validator observes canonical read-only evidence and compares 2 registries against policy segment 30.",
    "bad_pattern": "bad pattern 26 in matrix 30: writer drift toward family 5, generated path reports_real/segment_30_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_30_26, boundary=bnd_matrix_30_26, switch=sw_matrix_30_26, hash_hint=fef77abb7f5cfd2d"
  },
  {
    "matrix_row_id": "matrix_030_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 30: validator observes canonical read-only evidence and compares 3 registries against policy segment 30.",
    "bad_pattern": "bad pattern 27 in matrix 30: writer drift toward family 6, generated path reports_real/segment_30_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_30_27, boundary=bnd_matrix_30_27, switch=sw_matrix_30_27, hash_hint=6c7a0f58c68d4b86"
  },
  {
    "matrix_row_id": "matrix_030_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 30: validator observes canonical read-only evidence and compares 4 registries against policy segment 30.",
    "bad_pattern": "bad pattern 28 in matrix 30: writer drift toward family 0, generated path reports_real/segment_30_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_30_28, boundary=bnd_matrix_30_28, switch=sw_matrix_30_28, hash_hint=b5133d0c1b13ffac"
  },
  {
    "matrix_row_id": "matrix_030_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 30: validator observes canonical read-only evidence and compares 5 registries against policy segment 30.",
    "bad_pattern": "bad pattern 29 in matrix 30: writer drift toward family 1, generated path reports_real/segment_30_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_30_29, boundary=bnd_matrix_30_29, switch=sw_matrix_30_29, hash_hint=a6d71caa9faa0970"
  },
  {
    "matrix_row_id": "matrix_030_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 30: validator observes canonical read-only evidence and compares 1 registries against policy segment 30.",
    "bad_pattern": "bad pattern 30 in matrix 30: writer drift toward family 2, generated path reports_real/segment_30_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_30_30, boundary=bnd_matrix_30_30, switch=sw_matrix_30_30, hash_hint=c5eac0ffa93ba09e"
  },
  {
    "matrix_row_id": "matrix_030_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 30: validator observes canonical read-only evidence and compares 2 registries against policy segment 30.",
    "bad_pattern": "bad pattern 31 in matrix 30: writer drift toward family 3, generated path reports_real/segment_30_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_30_31, boundary=bnd_matrix_30_31, switch=sw_matrix_30_31, hash_hint=d33852e6d7369484"
  },
  {
    "matrix_row_id": "matrix_030_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 30: validator observes canonical read-only evidence and compares 3 registries against policy segment 30.",
    "bad_pattern": "bad pattern 32 in matrix 30: writer drift toward family 4, generated path reports_real/segment_30_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_30_32, boundary=bnd_matrix_30_32, switch=sw_matrix_30_32, hash_hint=995f468911ecf845"
  },
  {
    "matrix_row_id": "matrix_030_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 30: validator observes canonical read-only evidence and compares 4 registries against policy segment 30.",
    "bad_pattern": "bad pattern 33 in matrix 30: writer drift toward family 5, generated path reports_real/segment_30_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_30_33, boundary=bnd_matrix_30_33, switch=sw_matrix_30_33, hash_hint=721a03c5d39a1a36"
  },
  {
    "matrix_row_id": "matrix_030_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 30: validator observes canonical read-only evidence and compares 5 registries against policy segment 30.",
    "bad_pattern": "bad pattern 34 in matrix 30: writer drift toward family 6, generated path reports_real/segment_30_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_30_34, boundary=bnd_matrix_30_34, switch=sw_matrix_30_34, hash_hint=409159f1415416b0"
  },
  {
    "matrix_row_id": "matrix_030_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 30: validator observes canonical read-only evidence and compares 1 registries against policy segment 30.",
    "bad_pattern": "bad pattern 35 in matrix 30: writer drift toward family 0, generated path reports_real/segment_30_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_30_35, boundary=bnd_matrix_30_35, switch=sw_matrix_30_35, hash_hint=6303e72422e363d3"
  },
  {
    "matrix_row_id": "matrix_030_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 30: validator observes canonical read-only evidence and compares 2 registries against policy segment 30.",
    "bad_pattern": "bad pattern 36 in matrix 30: writer drift toward family 1, generated path reports_real/segment_30_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_30_36, boundary=bnd_matrix_30_36, switch=sw_matrix_30_36, hash_hint=809a3fce1b0a1284"
  },
  {
    "matrix_row_id": "matrix_030_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 30: validator observes canonical read-only evidence and compares 3 registries against policy segment 30.",
    "bad_pattern": "bad pattern 37 in matrix 30: writer drift toward family 2, generated path reports_real/segment_30_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_30_37, boundary=bnd_matrix_30_37, switch=sw_matrix_30_37, hash_hint=c7e074b382f3f5c4"
  },
  {
    "matrix_row_id": "matrix_030_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 30: validator observes canonical read-only evidence and compares 4 registries against policy segment 30.",
    "bad_pattern": "bad pattern 38 in matrix 30: writer drift toward family 3, generated path reports_real/segment_30_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_30_38, boundary=bnd_matrix_30_38, switch=sw_matrix_30_38, hash_hint=1eddc8e2fc4436dc"
  },
  {
    "matrix_row_id": "matrix_030_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 30: validator observes canonical read-only evidence and compares 5 registries against policy segment 30.",
    "bad_pattern": "bad pattern 39 in matrix 30: writer drift toward family 4, generated path reports_real/segment_30_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_30_39, boundary=bnd_matrix_30_39, switch=sw_matrix_30_39, hash_hint=d190d1b55ac5d217"
  },
  {
    "matrix_row_id": "matrix_030_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 30: validator observes canonical read-only evidence and compares 1 registries against policy segment 30.",
    "bad_pattern": "bad pattern 40 in matrix 30: writer drift toward family 5, generated path reports_real/segment_30_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_30_40, boundary=bnd_matrix_30_40, switch=sw_matrix_30_40, hash_hint=274ea9b8874a0ffb"
  },
  {
    "matrix_row_id": "matrix_030_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 30: validator observes canonical read-only evidence and compares 2 registries against policy segment 30.",
    "bad_pattern": "bad pattern 41 in matrix 30: writer drift toward family 6, generated path reports_real/segment_30_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_30_41, boundary=bnd_matrix_30_41, switch=sw_matrix_30_41, hash_hint=14e4213a352fbaf5"
  },
  {
    "matrix_row_id": "matrix_030_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 30: validator observes canonical read-only evidence and compares 3 registries against policy segment 30.",
    "bad_pattern": "bad pattern 42 in matrix 30: writer drift toward family 0, generated path reports_real/segment_30_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_30_42, boundary=bnd_matrix_30_42, switch=sw_matrix_30_42, hash_hint=be9b604d7070187a"
  },
  {
    "matrix_row_id": "matrix_030_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 30: validator observes canonical read-only evidence and compares 4 registries against policy segment 30.",
    "bad_pattern": "bad pattern 43 in matrix 30: writer drift toward family 1, generated path reports_real/segment_30_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_30_43, boundary=bnd_matrix_30_43, switch=sw_matrix_30_43, hash_hint=1185064d3fe2227e"
  },
  {
    "matrix_row_id": "matrix_030_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 30: validator observes canonical read-only evidence and compares 5 registries against policy segment 30.",
    "bad_pattern": "bad pattern 44 in matrix 30: writer drift toward family 2, generated path reports_real/segment_30_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_30_44, boundary=bnd_matrix_30_44, switch=sw_matrix_30_44, hash_hint=a8a3c768ba475089"
  },
  {
    "matrix_row_id": "matrix_030_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 30: validator observes canonical read-only evidence and compares 1 registries against policy segment 30.",
    "bad_pattern": "bad pattern 45 in matrix 30: writer drift toward family 3, generated path reports_real/segment_30_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_30_45, boundary=bnd_matrix_30_45, switch=sw_matrix_30_45, hash_hint=053cbfde3ae95dbd"
  },
  {
    "matrix_row_id": "matrix_030_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 30: validator observes canonical read-only evidence and compares 2 registries against policy segment 30.",
    "bad_pattern": "bad pattern 46 in matrix 30: writer drift toward family 4, generated path reports_real/segment_30_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_30_46, boundary=bnd_matrix_30_46, switch=sw_matrix_30_46, hash_hint=1bd45db6b1792f1f"
  },
  {
    "matrix_row_id": "matrix_030_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 30: validator observes canonical read-only evidence and compares 3 registries against policy segment 30.",
    "bad_pattern": "bad pattern 47 in matrix 30: writer drift toward family 5, generated path reports_real/segment_30_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_30_47, boundary=bnd_matrix_30_47, switch=sw_matrix_30_47, hash_hint=d7f3750ddeb5249f"
  },
  {
    "matrix_row_id": "matrix_030_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 30: validator observes canonical read-only evidence and compares 4 registries against policy segment 30.",
    "bad_pattern": "bad pattern 48 in matrix 30: writer drift toward family 6, generated path reports_real/segment_30_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_30_48, boundary=bnd_matrix_30_48, switch=sw_matrix_30_48, hash_hint=45c123ba7bab4b94"
  },
  {
    "matrix_row_id": "matrix_030_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 30: validator observes canonical read-only evidence and compares 5 registries against policy segment 30.",
    "bad_pattern": "bad pattern 49 in matrix 30: writer drift toward family 0, generated path reports_real/segment_30_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_30_49, boundary=bnd_matrix_30_49, switch=sw_matrix_30_49, hash_hint=d0ce19bbf2416ecb"
  },
  {
    "matrix_row_id": "matrix_030_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 30: validator observes canonical read-only evidence and compares 1 registries against policy segment 30.",
    "bad_pattern": "bad pattern 50 in matrix 30: writer drift toward family 1, generated path reports_real/segment_30_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_30_50, boundary=bnd_matrix_30_50, switch=sw_matrix_30_50, hash_hint=fdc21822fa8e068d"
  },
  {
    "matrix_row_id": "matrix_030_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 30: validator observes canonical read-only evidence and compares 2 registries against policy segment 30.",
    "bad_pattern": "bad pattern 51 in matrix 30: writer drift toward family 2, generated path reports_real/segment_30_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_30_51, boundary=bnd_matrix_30_51, switch=sw_matrix_30_51, hash_hint=8d5bd86ba1b098a8"
  },
  {
    "matrix_row_id": "matrix_030_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 30: validator observes canonical read-only evidence and compares 3 registries against policy segment 30.",
    "bad_pattern": "bad pattern 52 in matrix 30: writer drift toward family 3, generated path reports_real/segment_30_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_30_52, boundary=bnd_matrix_30_52, switch=sw_matrix_30_52, hash_hint=85bbfd0f2197cef9"
  },
  {
    "matrix_row_id": "matrix_030_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 30: validator observes canonical read-only evidence and compares 4 registries against policy segment 30.",
    "bad_pattern": "bad pattern 53 in matrix 30: writer drift toward family 4, generated path reports_real/segment_30_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_30_53, boundary=bnd_matrix_30_53, switch=sw_matrix_30_53, hash_hint=d4c62b706d1682c8"
  },
  {
    "matrix_row_id": "matrix_030_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 30: validator observes canonical read-only evidence and compares 5 registries against policy segment 30.",
    "bad_pattern": "bad pattern 54 in matrix 30: writer drift toward family 5, generated path reports_real/segment_30_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_30_54, boundary=bnd_matrix_30_54, switch=sw_matrix_30_54, hash_hint=22b53ffd76dcf18b"
  },
  {
    "matrix_row_id": "matrix_030_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 30: validator observes canonical read-only evidence and compares 1 registries against policy segment 30.",
    "bad_pattern": "bad pattern 55 in matrix 30: writer drift toward family 6, generated path reports_real/segment_30_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_30_55, boundary=bnd_matrix_30_55, switch=sw_matrix_30_55, hash_hint=2fb9575efc01b510"
  },
  {
    "matrix_row_id": "matrix_030_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 30: validator observes canonical read-only evidence and compares 2 registries against policy segment 30.",
    "bad_pattern": "bad pattern 56 in matrix 30: writer drift toward family 0, generated path reports_real/segment_30_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_30_56, boundary=bnd_matrix_30_56, switch=sw_matrix_30_56, hash_hint=a48ea4eb05f814f7"
  },
  {
    "matrix_row_id": "matrix_030_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 30: validator observes canonical read-only evidence and compares 3 registries against policy segment 30.",
    "bad_pattern": "bad pattern 57 in matrix 30: writer drift toward family 1, generated path reports_real/segment_30_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_30_57, boundary=bnd_matrix_30_57, switch=sw_matrix_30_57, hash_hint=3dc5391eb206d802"
  },
  {
    "matrix_row_id": "matrix_030_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 30: validator observes canonical read-only evidence and compares 4 registries against policy segment 30.",
    "bad_pattern": "bad pattern 58 in matrix 30: writer drift toward family 2, generated path reports_real/segment_30_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_30_58, boundary=bnd_matrix_30_58, switch=sw_matrix_30_58, hash_hint=47b5ff422675c38b"
  },
  {
    "matrix_row_id": "matrix_030_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 30: validator observes canonical read-only evidence and compares 5 registries against policy segment 30.",
    "bad_pattern": "bad pattern 59 in matrix 30: writer drift toward family 3, generated path reports_real/segment_30_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_30_59, boundary=bnd_matrix_30_59, switch=sw_matrix_30_59, hash_hint=43eb60e048c70167"
  },
  {
    "matrix_row_id": "matrix_030_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 30: validator observes canonical read-only evidence and compares 1 registries against policy segment 30.",
    "bad_pattern": "bad pattern 60 in matrix 30: writer drift toward family 4, generated path reports_real/segment_30_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_30_60, boundary=bnd_matrix_30_60, switch=sw_matrix_30_60, hash_hint=cd3c043e6768fb64"
  }
]
