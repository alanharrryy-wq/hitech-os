from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 27/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 27/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 27/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 27/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 27/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 27/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 27/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 27/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 27/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 27/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 27/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 27/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 27/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 27/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 27/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 27/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 27/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 27/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 27/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 27/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 27/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 27/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 27/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 27/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 27/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_027_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 27: validator observes canonical read-only evidence and compares 2 registries against policy segment 27.",
    "bad_pattern": "bad pattern 1 in matrix 27: writer drift toward family 1, generated path reports_real/segment_27_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_27_1, boundary=bnd_matrix_27_1, switch=sw_matrix_27_1, hash_hint=f3d35c91c9326e2f"
  },
  {
    "matrix_row_id": "matrix_027_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 27: validator observes canonical read-only evidence and compares 3 registries against policy segment 27.",
    "bad_pattern": "bad pattern 2 in matrix 27: writer drift toward family 2, generated path reports_real/segment_27_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_27_2, boundary=bnd_matrix_27_2, switch=sw_matrix_27_2, hash_hint=9a51775e37aa05bd"
  },
  {
    "matrix_row_id": "matrix_027_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 27: validator observes canonical read-only evidence and compares 4 registries against policy segment 27.",
    "bad_pattern": "bad pattern 3 in matrix 27: writer drift toward family 3, generated path reports_real/segment_27_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_27_3, boundary=bnd_matrix_27_3, switch=sw_matrix_27_3, hash_hint=efd3daa5e6212feb"
  },
  {
    "matrix_row_id": "matrix_027_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 27: validator observes canonical read-only evidence and compares 5 registries against policy segment 27.",
    "bad_pattern": "bad pattern 4 in matrix 27: writer drift toward family 4, generated path reports_real/segment_27_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_27_4, boundary=bnd_matrix_27_4, switch=sw_matrix_27_4, hash_hint=612cbb90a5daece1"
  },
  {
    "matrix_row_id": "matrix_027_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 27: validator observes canonical read-only evidence and compares 1 registries against policy segment 27.",
    "bad_pattern": "bad pattern 5 in matrix 27: writer drift toward family 5, generated path reports_real/segment_27_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_27_5, boundary=bnd_matrix_27_5, switch=sw_matrix_27_5, hash_hint=ee80494522157ed8"
  },
  {
    "matrix_row_id": "matrix_027_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 27: validator observes canonical read-only evidence and compares 2 registries against policy segment 27.",
    "bad_pattern": "bad pattern 6 in matrix 27: writer drift toward family 6, generated path reports_real/segment_27_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_27_6, boundary=bnd_matrix_27_6, switch=sw_matrix_27_6, hash_hint=1d460826c279e98e"
  },
  {
    "matrix_row_id": "matrix_027_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 27: validator observes canonical read-only evidence and compares 3 registries against policy segment 27.",
    "bad_pattern": "bad pattern 7 in matrix 27: writer drift toward family 0, generated path reports_real/segment_27_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_27_7, boundary=bnd_matrix_27_7, switch=sw_matrix_27_7, hash_hint=9e204315d9a9e479"
  },
  {
    "matrix_row_id": "matrix_027_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 27: validator observes canonical read-only evidence and compares 4 registries against policy segment 27.",
    "bad_pattern": "bad pattern 8 in matrix 27: writer drift toward family 1, generated path reports_real/segment_27_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_27_8, boundary=bnd_matrix_27_8, switch=sw_matrix_27_8, hash_hint=99ad98fee1fba35e"
  },
  {
    "matrix_row_id": "matrix_027_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 27: validator observes canonical read-only evidence and compares 5 registries against policy segment 27.",
    "bad_pattern": "bad pattern 9 in matrix 27: writer drift toward family 2, generated path reports_real/segment_27_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_27_9, boundary=bnd_matrix_27_9, switch=sw_matrix_27_9, hash_hint=243f150f2dca1cba"
  },
  {
    "matrix_row_id": "matrix_027_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 27: validator observes canonical read-only evidence and compares 1 registries against policy segment 27.",
    "bad_pattern": "bad pattern 10 in matrix 27: writer drift toward family 3, generated path reports_real/segment_27_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_27_10, boundary=bnd_matrix_27_10, switch=sw_matrix_27_10, hash_hint=41c9d4fd3547ca7b"
  },
  {
    "matrix_row_id": "matrix_027_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 27: validator observes canonical read-only evidence and compares 2 registries against policy segment 27.",
    "bad_pattern": "bad pattern 11 in matrix 27: writer drift toward family 4, generated path reports_real/segment_27_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_27_11, boundary=bnd_matrix_27_11, switch=sw_matrix_27_11, hash_hint=fb38c12af334c659"
  },
  {
    "matrix_row_id": "matrix_027_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 27: validator observes canonical read-only evidence and compares 3 registries against policy segment 27.",
    "bad_pattern": "bad pattern 12 in matrix 27: writer drift toward family 5, generated path reports_real/segment_27_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_27_12, boundary=bnd_matrix_27_12, switch=sw_matrix_27_12, hash_hint=0a0ba109f71d4ca3"
  },
  {
    "matrix_row_id": "matrix_027_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 27: validator observes canonical read-only evidence and compares 4 registries against policy segment 27.",
    "bad_pattern": "bad pattern 13 in matrix 27: writer drift toward family 6, generated path reports_real/segment_27_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_27_13, boundary=bnd_matrix_27_13, switch=sw_matrix_27_13, hash_hint=3f3222ff674e21fc"
  },
  {
    "matrix_row_id": "matrix_027_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 27: validator observes canonical read-only evidence and compares 5 registries against policy segment 27.",
    "bad_pattern": "bad pattern 14 in matrix 27: writer drift toward family 0, generated path reports_real/segment_27_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_27_14, boundary=bnd_matrix_27_14, switch=sw_matrix_27_14, hash_hint=e429894a2dd5d8ea"
  },
  {
    "matrix_row_id": "matrix_027_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 27: validator observes canonical read-only evidence and compares 1 registries against policy segment 27.",
    "bad_pattern": "bad pattern 15 in matrix 27: writer drift toward family 1, generated path reports_real/segment_27_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_27_15, boundary=bnd_matrix_27_15, switch=sw_matrix_27_15, hash_hint=82c6335d27a205f3"
  },
  {
    "matrix_row_id": "matrix_027_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 27: validator observes canonical read-only evidence and compares 2 registries against policy segment 27.",
    "bad_pattern": "bad pattern 16 in matrix 27: writer drift toward family 2, generated path reports_real/segment_27_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_27_16, boundary=bnd_matrix_27_16, switch=sw_matrix_27_16, hash_hint=399e61ffb3b03348"
  },
  {
    "matrix_row_id": "matrix_027_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 27: validator observes canonical read-only evidence and compares 3 registries against policy segment 27.",
    "bad_pattern": "bad pattern 17 in matrix 27: writer drift toward family 3, generated path reports_real/segment_27_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_27_17, boundary=bnd_matrix_27_17, switch=sw_matrix_27_17, hash_hint=595454b90e6ad448"
  },
  {
    "matrix_row_id": "matrix_027_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 27: validator observes canonical read-only evidence and compares 4 registries against policy segment 27.",
    "bad_pattern": "bad pattern 18 in matrix 27: writer drift toward family 4, generated path reports_real/segment_27_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_27_18, boundary=bnd_matrix_27_18, switch=sw_matrix_27_18, hash_hint=c7ca0bc62788a162"
  },
  {
    "matrix_row_id": "matrix_027_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 27: validator observes canonical read-only evidence and compares 5 registries against policy segment 27.",
    "bad_pattern": "bad pattern 19 in matrix 27: writer drift toward family 5, generated path reports_real/segment_27_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_27_19, boundary=bnd_matrix_27_19, switch=sw_matrix_27_19, hash_hint=59a38d29a7d11372"
  },
  {
    "matrix_row_id": "matrix_027_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 27: validator observes canonical read-only evidence and compares 1 registries against policy segment 27.",
    "bad_pattern": "bad pattern 20 in matrix 27: writer drift toward family 6, generated path reports_real/segment_27_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_27_20, boundary=bnd_matrix_27_20, switch=sw_matrix_27_20, hash_hint=6ac192d6af770668"
  },
  {
    "matrix_row_id": "matrix_027_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 27: validator observes canonical read-only evidence and compares 2 registries against policy segment 27.",
    "bad_pattern": "bad pattern 21 in matrix 27: writer drift toward family 0, generated path reports_real/segment_27_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_27_21, boundary=bnd_matrix_27_21, switch=sw_matrix_27_21, hash_hint=a7ae6da7cfe097bd"
  },
  {
    "matrix_row_id": "matrix_027_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 27: validator observes canonical read-only evidence and compares 3 registries against policy segment 27.",
    "bad_pattern": "bad pattern 22 in matrix 27: writer drift toward family 1, generated path reports_real/segment_27_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_27_22, boundary=bnd_matrix_27_22, switch=sw_matrix_27_22, hash_hint=b620ed0eee6db4cd"
  },
  {
    "matrix_row_id": "matrix_027_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 27: validator observes canonical read-only evidence and compares 4 registries against policy segment 27.",
    "bad_pattern": "bad pattern 23 in matrix 27: writer drift toward family 2, generated path reports_real/segment_27_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_27_23, boundary=bnd_matrix_27_23, switch=sw_matrix_27_23, hash_hint=8a81435b6399714b"
  },
  {
    "matrix_row_id": "matrix_027_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 27: validator observes canonical read-only evidence and compares 5 registries against policy segment 27.",
    "bad_pattern": "bad pattern 24 in matrix 27: writer drift toward family 3, generated path reports_real/segment_27_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_27_24, boundary=bnd_matrix_27_24, switch=sw_matrix_27_24, hash_hint=6f355a0139008812"
  },
  {
    "matrix_row_id": "matrix_027_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 27: validator observes canonical read-only evidence and compares 1 registries against policy segment 27.",
    "bad_pattern": "bad pattern 25 in matrix 27: writer drift toward family 4, generated path reports_real/segment_27_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_27_25, boundary=bnd_matrix_27_25, switch=sw_matrix_27_25, hash_hint=b588bc94850ebe78"
  },
  {
    "matrix_row_id": "matrix_027_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 27: validator observes canonical read-only evidence and compares 2 registries against policy segment 27.",
    "bad_pattern": "bad pattern 26 in matrix 27: writer drift toward family 5, generated path reports_real/segment_27_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_27_26, boundary=bnd_matrix_27_26, switch=sw_matrix_27_26, hash_hint=aafe8c994f90c0e4"
  },
  {
    "matrix_row_id": "matrix_027_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 27: validator observes canonical read-only evidence and compares 3 registries against policy segment 27.",
    "bad_pattern": "bad pattern 27 in matrix 27: writer drift toward family 6, generated path reports_real/segment_27_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_27_27, boundary=bnd_matrix_27_27, switch=sw_matrix_27_27, hash_hint=b6e03984a17cb73d"
  },
  {
    "matrix_row_id": "matrix_027_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 27: validator observes canonical read-only evidence and compares 4 registries against policy segment 27.",
    "bad_pattern": "bad pattern 28 in matrix 27: writer drift toward family 0, generated path reports_real/segment_27_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_27_28, boundary=bnd_matrix_27_28, switch=sw_matrix_27_28, hash_hint=eb12f0b920ac9065"
  },
  {
    "matrix_row_id": "matrix_027_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 27: validator observes canonical read-only evidence and compares 5 registries against policy segment 27.",
    "bad_pattern": "bad pattern 29 in matrix 27: writer drift toward family 1, generated path reports_real/segment_27_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_27_29, boundary=bnd_matrix_27_29, switch=sw_matrix_27_29, hash_hint=c9ce81c72bd7f4cd"
  },
  {
    "matrix_row_id": "matrix_027_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 27: validator observes canonical read-only evidence and compares 1 registries against policy segment 27.",
    "bad_pattern": "bad pattern 30 in matrix 27: writer drift toward family 2, generated path reports_real/segment_27_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_27_30, boundary=bnd_matrix_27_30, switch=sw_matrix_27_30, hash_hint=28d737d464ca6a3a"
  },
  {
    "matrix_row_id": "matrix_027_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 27: validator observes canonical read-only evidence and compares 2 registries against policy segment 27.",
    "bad_pattern": "bad pattern 31 in matrix 27: writer drift toward family 3, generated path reports_real/segment_27_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_27_31, boundary=bnd_matrix_27_31, switch=sw_matrix_27_31, hash_hint=a20b7f76c16e6b44"
  },
  {
    "matrix_row_id": "matrix_027_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 27: validator observes canonical read-only evidence and compares 3 registries against policy segment 27.",
    "bad_pattern": "bad pattern 32 in matrix 27: writer drift toward family 4, generated path reports_real/segment_27_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_27_32, boundary=bnd_matrix_27_32, switch=sw_matrix_27_32, hash_hint=70dd84280cc922f1"
  },
  {
    "matrix_row_id": "matrix_027_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 27: validator observes canonical read-only evidence and compares 4 registries against policy segment 27.",
    "bad_pattern": "bad pattern 33 in matrix 27: writer drift toward family 5, generated path reports_real/segment_27_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_27_33, boundary=bnd_matrix_27_33, switch=sw_matrix_27_33, hash_hint=844790e4731c7dd4"
  },
  {
    "matrix_row_id": "matrix_027_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 27: validator observes canonical read-only evidence and compares 5 registries against policy segment 27.",
    "bad_pattern": "bad pattern 34 in matrix 27: writer drift toward family 6, generated path reports_real/segment_27_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_27_34, boundary=bnd_matrix_27_34, switch=sw_matrix_27_34, hash_hint=f47e156a5f5271df"
  },
  {
    "matrix_row_id": "matrix_027_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 27: validator observes canonical read-only evidence and compares 1 registries against policy segment 27.",
    "bad_pattern": "bad pattern 35 in matrix 27: writer drift toward family 0, generated path reports_real/segment_27_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_27_35, boundary=bnd_matrix_27_35, switch=sw_matrix_27_35, hash_hint=2b47716b982257d5"
  },
  {
    "matrix_row_id": "matrix_027_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 27: validator observes canonical read-only evidence and compares 2 registries against policy segment 27.",
    "bad_pattern": "bad pattern 36 in matrix 27: writer drift toward family 1, generated path reports_real/segment_27_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_27_36, boundary=bnd_matrix_27_36, switch=sw_matrix_27_36, hash_hint=2f22d63f6700037e"
  },
  {
    "matrix_row_id": "matrix_027_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 27: validator observes canonical read-only evidence and compares 3 registries against policy segment 27.",
    "bad_pattern": "bad pattern 37 in matrix 27: writer drift toward family 2, generated path reports_real/segment_27_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_27_37, boundary=bnd_matrix_27_37, switch=sw_matrix_27_37, hash_hint=54110a4718fff965"
  },
  {
    "matrix_row_id": "matrix_027_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 27: validator observes canonical read-only evidence and compares 4 registries against policy segment 27.",
    "bad_pattern": "bad pattern 38 in matrix 27: writer drift toward family 3, generated path reports_real/segment_27_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_27_38, boundary=bnd_matrix_27_38, switch=sw_matrix_27_38, hash_hint=49edb754a1a5e2cc"
  },
  {
    "matrix_row_id": "matrix_027_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 27: validator observes canonical read-only evidence and compares 5 registries against policy segment 27.",
    "bad_pattern": "bad pattern 39 in matrix 27: writer drift toward family 4, generated path reports_real/segment_27_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_27_39, boundary=bnd_matrix_27_39, switch=sw_matrix_27_39, hash_hint=9d6ccbd7e6c1bdd5"
  },
  {
    "matrix_row_id": "matrix_027_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 27: validator observes canonical read-only evidence and compares 1 registries against policy segment 27.",
    "bad_pattern": "bad pattern 40 in matrix 27: writer drift toward family 5, generated path reports_real/segment_27_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_27_40, boundary=bnd_matrix_27_40, switch=sw_matrix_27_40, hash_hint=f9cf8cdd966a4689"
  },
  {
    "matrix_row_id": "matrix_027_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 27: validator observes canonical read-only evidence and compares 2 registries against policy segment 27.",
    "bad_pattern": "bad pattern 41 in matrix 27: writer drift toward family 6, generated path reports_real/segment_27_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_27_41, boundary=bnd_matrix_27_41, switch=sw_matrix_27_41, hash_hint=5abc4baf8a6b0dc1"
  },
  {
    "matrix_row_id": "matrix_027_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 27: validator observes canonical read-only evidence and compares 3 registries against policy segment 27.",
    "bad_pattern": "bad pattern 42 in matrix 27: writer drift toward family 0, generated path reports_real/segment_27_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_27_42, boundary=bnd_matrix_27_42, switch=sw_matrix_27_42, hash_hint=57bef01874b4e074"
  },
  {
    "matrix_row_id": "matrix_027_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 27: validator observes canonical read-only evidence and compares 4 registries against policy segment 27.",
    "bad_pattern": "bad pattern 43 in matrix 27: writer drift toward family 1, generated path reports_real/segment_27_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_27_43, boundary=bnd_matrix_27_43, switch=sw_matrix_27_43, hash_hint=1d661ee721041e28"
  },
  {
    "matrix_row_id": "matrix_027_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 27: validator observes canonical read-only evidence and compares 5 registries against policy segment 27.",
    "bad_pattern": "bad pattern 44 in matrix 27: writer drift toward family 2, generated path reports_real/segment_27_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_27_44, boundary=bnd_matrix_27_44, switch=sw_matrix_27_44, hash_hint=34bc195b611a248b"
  },
  {
    "matrix_row_id": "matrix_027_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 27: validator observes canonical read-only evidence and compares 1 registries against policy segment 27.",
    "bad_pattern": "bad pattern 45 in matrix 27: writer drift toward family 3, generated path reports_real/segment_27_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_27_45, boundary=bnd_matrix_27_45, switch=sw_matrix_27_45, hash_hint=bfbde0dda3e0131d"
  },
  {
    "matrix_row_id": "matrix_027_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 27: validator observes canonical read-only evidence and compares 2 registries against policy segment 27.",
    "bad_pattern": "bad pattern 46 in matrix 27: writer drift toward family 4, generated path reports_real/segment_27_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_27_46, boundary=bnd_matrix_27_46, switch=sw_matrix_27_46, hash_hint=8572ba1f3d67fb0c"
  },
  {
    "matrix_row_id": "matrix_027_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 27: validator observes canonical read-only evidence and compares 3 registries against policy segment 27.",
    "bad_pattern": "bad pattern 47 in matrix 27: writer drift toward family 5, generated path reports_real/segment_27_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_27_47, boundary=bnd_matrix_27_47, switch=sw_matrix_27_47, hash_hint=36d827c04b6257e9"
  },
  {
    "matrix_row_id": "matrix_027_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 27: validator observes canonical read-only evidence and compares 4 registries against policy segment 27.",
    "bad_pattern": "bad pattern 48 in matrix 27: writer drift toward family 6, generated path reports_real/segment_27_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_27_48, boundary=bnd_matrix_27_48, switch=sw_matrix_27_48, hash_hint=77bcc62293fdf19c"
  },
  {
    "matrix_row_id": "matrix_027_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 27: validator observes canonical read-only evidence and compares 5 registries against policy segment 27.",
    "bad_pattern": "bad pattern 49 in matrix 27: writer drift toward family 0, generated path reports_real/segment_27_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_27_49, boundary=bnd_matrix_27_49, switch=sw_matrix_27_49, hash_hint=d026b8c1219e6f64"
  },
  {
    "matrix_row_id": "matrix_027_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 27: validator observes canonical read-only evidence and compares 1 registries against policy segment 27.",
    "bad_pattern": "bad pattern 50 in matrix 27: writer drift toward family 1, generated path reports_real/segment_27_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_27_50, boundary=bnd_matrix_27_50, switch=sw_matrix_27_50, hash_hint=48c340ff4b93d158"
  },
  {
    "matrix_row_id": "matrix_027_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 27: validator observes canonical read-only evidence and compares 2 registries against policy segment 27.",
    "bad_pattern": "bad pattern 51 in matrix 27: writer drift toward family 2, generated path reports_real/segment_27_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_27_51, boundary=bnd_matrix_27_51, switch=sw_matrix_27_51, hash_hint=a14a8095d8d708e9"
  },
  {
    "matrix_row_id": "matrix_027_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 27: validator observes canonical read-only evidence and compares 3 registries against policy segment 27.",
    "bad_pattern": "bad pattern 52 in matrix 27: writer drift toward family 3, generated path reports_real/segment_27_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_27_52, boundary=bnd_matrix_27_52, switch=sw_matrix_27_52, hash_hint=5085036bed872cb3"
  },
  {
    "matrix_row_id": "matrix_027_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 27: validator observes canonical read-only evidence and compares 4 registries against policy segment 27.",
    "bad_pattern": "bad pattern 53 in matrix 27: writer drift toward family 4, generated path reports_real/segment_27_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_27_53, boundary=bnd_matrix_27_53, switch=sw_matrix_27_53, hash_hint=3c5612198c02f05f"
  },
  {
    "matrix_row_id": "matrix_027_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 27: validator observes canonical read-only evidence and compares 5 registries against policy segment 27.",
    "bad_pattern": "bad pattern 54 in matrix 27: writer drift toward family 5, generated path reports_real/segment_27_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_27_54, boundary=bnd_matrix_27_54, switch=sw_matrix_27_54, hash_hint=797ec964616986e9"
  },
  {
    "matrix_row_id": "matrix_027_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 27: validator observes canonical read-only evidence and compares 1 registries against policy segment 27.",
    "bad_pattern": "bad pattern 55 in matrix 27: writer drift toward family 6, generated path reports_real/segment_27_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_27_55, boundary=bnd_matrix_27_55, switch=sw_matrix_27_55, hash_hint=2e4bfb87d641c7c1"
  },
  {
    "matrix_row_id": "matrix_027_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 27: validator observes canonical read-only evidence and compares 2 registries against policy segment 27.",
    "bad_pattern": "bad pattern 56 in matrix 27: writer drift toward family 0, generated path reports_real/segment_27_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_27_56, boundary=bnd_matrix_27_56, switch=sw_matrix_27_56, hash_hint=eed29fccdcae4079"
  },
  {
    "matrix_row_id": "matrix_027_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 27: validator observes canonical read-only evidence and compares 3 registries against policy segment 27.",
    "bad_pattern": "bad pattern 57 in matrix 27: writer drift toward family 1, generated path reports_real/segment_27_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_27_57, boundary=bnd_matrix_27_57, switch=sw_matrix_27_57, hash_hint=218f03b23de7bc9b"
  },
  {
    "matrix_row_id": "matrix_027_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 27: validator observes canonical read-only evidence and compares 4 registries against policy segment 27.",
    "bad_pattern": "bad pattern 58 in matrix 27: writer drift toward family 2, generated path reports_real/segment_27_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_27_58, boundary=bnd_matrix_27_58, switch=sw_matrix_27_58, hash_hint=6ee91b32ca1684d8"
  },
  {
    "matrix_row_id": "matrix_027_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 27: validator observes canonical read-only evidence and compares 5 registries against policy segment 27.",
    "bad_pattern": "bad pattern 59 in matrix 27: writer drift toward family 3, generated path reports_real/segment_27_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_27_59, boundary=bnd_matrix_27_59, switch=sw_matrix_27_59, hash_hint=acfe94a014d67a4e"
  },
  {
    "matrix_row_id": "matrix_027_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 27: validator observes canonical read-only evidence and compares 1 registries against policy segment 27.",
    "bad_pattern": "bad pattern 60 in matrix 27: writer drift toward family 4, generated path reports_real/segment_27_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_27_60, boundary=bnd_matrix_27_60, switch=sw_matrix_27_60, hash_hint=4f3842b183f6911d"
  }
]
