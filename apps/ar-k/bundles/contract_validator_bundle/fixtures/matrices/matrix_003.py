from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 3/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 3/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 3/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 3/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 3/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 3/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 3/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 3/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 3/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 3/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 3/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 3/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 3/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 3/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 3/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 3/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 3/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 3/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 3/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 3/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 3/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 3/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 3/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 3/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 3/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_003_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 3: validator observes canonical read-only evidence and compares 2 registries against policy segment 3.",
    "bad_pattern": "bad pattern 1 in matrix 3: writer drift toward family 1, generated path reports_real/segment_3_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_3_1, boundary=bnd_matrix_3_1, switch=sw_matrix_3_1, hash_hint=73e23b443f02b5ee"
  },
  {
    "matrix_row_id": "matrix_003_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 3: validator observes canonical read-only evidence and compares 3 registries against policy segment 3.",
    "bad_pattern": "bad pattern 2 in matrix 3: writer drift toward family 2, generated path reports_real/segment_3_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_3_2, boundary=bnd_matrix_3_2, switch=sw_matrix_3_2, hash_hint=cd7da774aa7f1d6b"
  },
  {
    "matrix_row_id": "matrix_003_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 3: validator observes canonical read-only evidence and compares 4 registries against policy segment 3.",
    "bad_pattern": "bad pattern 3 in matrix 3: writer drift toward family 3, generated path reports_real/segment_3_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_3_3, boundary=bnd_matrix_3_3, switch=sw_matrix_3_3, hash_hint=2b51daa5c1d79aed"
  },
  {
    "matrix_row_id": "matrix_003_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 3: validator observes canonical read-only evidence and compares 5 registries against policy segment 3.",
    "bad_pattern": "bad pattern 4 in matrix 3: writer drift toward family 4, generated path reports_real/segment_3_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_3_4, boundary=bnd_matrix_3_4, switch=sw_matrix_3_4, hash_hint=79c9552083128c66"
  },
  {
    "matrix_row_id": "matrix_003_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 3: validator observes canonical read-only evidence and compares 1 registries against policy segment 3.",
    "bad_pattern": "bad pattern 5 in matrix 3: writer drift toward family 5, generated path reports_real/segment_3_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_3_5, boundary=bnd_matrix_3_5, switch=sw_matrix_3_5, hash_hint=1ba709d2440f09ec"
  },
  {
    "matrix_row_id": "matrix_003_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 3: validator observes canonical read-only evidence and compares 2 registries against policy segment 3.",
    "bad_pattern": "bad pattern 6 in matrix 3: writer drift toward family 6, generated path reports_real/segment_3_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_3_6, boundary=bnd_matrix_3_6, switch=sw_matrix_3_6, hash_hint=8076e13abb7444c0"
  },
  {
    "matrix_row_id": "matrix_003_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 3: validator observes canonical read-only evidence and compares 3 registries against policy segment 3.",
    "bad_pattern": "bad pattern 7 in matrix 3: writer drift toward family 0, generated path reports_real/segment_3_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_3_7, boundary=bnd_matrix_3_7, switch=sw_matrix_3_7, hash_hint=3f02b514c5cfedf5"
  },
  {
    "matrix_row_id": "matrix_003_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 3: validator observes canonical read-only evidence and compares 4 registries against policy segment 3.",
    "bad_pattern": "bad pattern 8 in matrix 3: writer drift toward family 1, generated path reports_real/segment_3_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_3_8, boundary=bnd_matrix_3_8, switch=sw_matrix_3_8, hash_hint=9e9747e409835eee"
  },
  {
    "matrix_row_id": "matrix_003_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 3: validator observes canonical read-only evidence and compares 5 registries against policy segment 3.",
    "bad_pattern": "bad pattern 9 in matrix 3: writer drift toward family 2, generated path reports_real/segment_3_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_3_9, boundary=bnd_matrix_3_9, switch=sw_matrix_3_9, hash_hint=88f7f4b97a775d98"
  },
  {
    "matrix_row_id": "matrix_003_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 3: validator observes canonical read-only evidence and compares 1 registries against policy segment 3.",
    "bad_pattern": "bad pattern 10 in matrix 3: writer drift toward family 3, generated path reports_real/segment_3_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_3_10, boundary=bnd_matrix_3_10, switch=sw_matrix_3_10, hash_hint=22b904a323c39f42"
  },
  {
    "matrix_row_id": "matrix_003_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 3: validator observes canonical read-only evidence and compares 2 registries against policy segment 3.",
    "bad_pattern": "bad pattern 11 in matrix 3: writer drift toward family 4, generated path reports_real/segment_3_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_3_11, boundary=bnd_matrix_3_11, switch=sw_matrix_3_11, hash_hint=78a4f87d6da9f01b"
  },
  {
    "matrix_row_id": "matrix_003_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 3: validator observes canonical read-only evidence and compares 3 registries against policy segment 3.",
    "bad_pattern": "bad pattern 12 in matrix 3: writer drift toward family 5, generated path reports_real/segment_3_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_3_12, boundary=bnd_matrix_3_12, switch=sw_matrix_3_12, hash_hint=58cae2cf293c4148"
  },
  {
    "matrix_row_id": "matrix_003_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 3: validator observes canonical read-only evidence and compares 4 registries against policy segment 3.",
    "bad_pattern": "bad pattern 13 in matrix 3: writer drift toward family 6, generated path reports_real/segment_3_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_3_13, boundary=bnd_matrix_3_13, switch=sw_matrix_3_13, hash_hint=644b4f294005b101"
  },
  {
    "matrix_row_id": "matrix_003_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 3: validator observes canonical read-only evidence and compares 5 registries against policy segment 3.",
    "bad_pattern": "bad pattern 14 in matrix 3: writer drift toward family 0, generated path reports_real/segment_3_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_3_14, boundary=bnd_matrix_3_14, switch=sw_matrix_3_14, hash_hint=cb5c86d39a4f4542"
  },
  {
    "matrix_row_id": "matrix_003_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 3: validator observes canonical read-only evidence and compares 1 registries against policy segment 3.",
    "bad_pattern": "bad pattern 15 in matrix 3: writer drift toward family 1, generated path reports_real/segment_3_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_3_15, boundary=bnd_matrix_3_15, switch=sw_matrix_3_15, hash_hint=2576581c93f48bee"
  },
  {
    "matrix_row_id": "matrix_003_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 3: validator observes canonical read-only evidence and compares 2 registries against policy segment 3.",
    "bad_pattern": "bad pattern 16 in matrix 3: writer drift toward family 2, generated path reports_real/segment_3_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_3_16, boundary=bnd_matrix_3_16, switch=sw_matrix_3_16, hash_hint=257e203cadb78667"
  },
  {
    "matrix_row_id": "matrix_003_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 3: validator observes canonical read-only evidence and compares 3 registries against policy segment 3.",
    "bad_pattern": "bad pattern 17 in matrix 3: writer drift toward family 3, generated path reports_real/segment_3_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_3_17, boundary=bnd_matrix_3_17, switch=sw_matrix_3_17, hash_hint=bd7169096040433a"
  },
  {
    "matrix_row_id": "matrix_003_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 3: validator observes canonical read-only evidence and compares 4 registries against policy segment 3.",
    "bad_pattern": "bad pattern 18 in matrix 3: writer drift toward family 4, generated path reports_real/segment_3_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_3_18, boundary=bnd_matrix_3_18, switch=sw_matrix_3_18, hash_hint=65c649a856edfb20"
  },
  {
    "matrix_row_id": "matrix_003_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 3: validator observes canonical read-only evidence and compares 5 registries against policy segment 3.",
    "bad_pattern": "bad pattern 19 in matrix 3: writer drift toward family 5, generated path reports_real/segment_3_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_3_19, boundary=bnd_matrix_3_19, switch=sw_matrix_3_19, hash_hint=23ce1299a96a4e65"
  },
  {
    "matrix_row_id": "matrix_003_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 3: validator observes canonical read-only evidence and compares 1 registries against policy segment 3.",
    "bad_pattern": "bad pattern 20 in matrix 3: writer drift toward family 6, generated path reports_real/segment_3_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_3_20, boundary=bnd_matrix_3_20, switch=sw_matrix_3_20, hash_hint=cb0236f738ea4ff8"
  },
  {
    "matrix_row_id": "matrix_003_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 3: validator observes canonical read-only evidence and compares 2 registries against policy segment 3.",
    "bad_pattern": "bad pattern 21 in matrix 3: writer drift toward family 0, generated path reports_real/segment_3_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_3_21, boundary=bnd_matrix_3_21, switch=sw_matrix_3_21, hash_hint=43b9b143a59e8f0e"
  },
  {
    "matrix_row_id": "matrix_003_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 3: validator observes canonical read-only evidence and compares 3 registries against policy segment 3.",
    "bad_pattern": "bad pattern 22 in matrix 3: writer drift toward family 1, generated path reports_real/segment_3_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_3_22, boundary=bnd_matrix_3_22, switch=sw_matrix_3_22, hash_hint=3a43de451690efa0"
  },
  {
    "matrix_row_id": "matrix_003_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 3: validator observes canonical read-only evidence and compares 4 registries against policy segment 3.",
    "bad_pattern": "bad pattern 23 in matrix 3: writer drift toward family 2, generated path reports_real/segment_3_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_3_23, boundary=bnd_matrix_3_23, switch=sw_matrix_3_23, hash_hint=c03be96afec5cfc2"
  },
  {
    "matrix_row_id": "matrix_003_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 3: validator observes canonical read-only evidence and compares 5 registries against policy segment 3.",
    "bad_pattern": "bad pattern 24 in matrix 3: writer drift toward family 3, generated path reports_real/segment_3_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_3_24, boundary=bnd_matrix_3_24, switch=sw_matrix_3_24, hash_hint=8e0eb884b949733e"
  },
  {
    "matrix_row_id": "matrix_003_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 3: validator observes canonical read-only evidence and compares 1 registries against policy segment 3.",
    "bad_pattern": "bad pattern 25 in matrix 3: writer drift toward family 4, generated path reports_real/segment_3_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_3_25, boundary=bnd_matrix_3_25, switch=sw_matrix_3_25, hash_hint=3f1073dd168e92b9"
  },
  {
    "matrix_row_id": "matrix_003_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 3: validator observes canonical read-only evidence and compares 2 registries against policy segment 3.",
    "bad_pattern": "bad pattern 26 in matrix 3: writer drift toward family 5, generated path reports_real/segment_3_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_3_26, boundary=bnd_matrix_3_26, switch=sw_matrix_3_26, hash_hint=5828cd70308dad80"
  },
  {
    "matrix_row_id": "matrix_003_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 3: validator observes canonical read-only evidence and compares 3 registries against policy segment 3.",
    "bad_pattern": "bad pattern 27 in matrix 3: writer drift toward family 6, generated path reports_real/segment_3_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_3_27, boundary=bnd_matrix_3_27, switch=sw_matrix_3_27, hash_hint=5ff31aa5774a24c0"
  },
  {
    "matrix_row_id": "matrix_003_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 3: validator observes canonical read-only evidence and compares 4 registries against policy segment 3.",
    "bad_pattern": "bad pattern 28 in matrix 3: writer drift toward family 0, generated path reports_real/segment_3_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_3_28, boundary=bnd_matrix_3_28, switch=sw_matrix_3_28, hash_hint=3a577b9809011f23"
  },
  {
    "matrix_row_id": "matrix_003_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 3: validator observes canonical read-only evidence and compares 5 registries against policy segment 3.",
    "bad_pattern": "bad pattern 29 in matrix 3: writer drift toward family 1, generated path reports_real/segment_3_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_3_29, boundary=bnd_matrix_3_29, switch=sw_matrix_3_29, hash_hint=244d6aab33a9bd58"
  },
  {
    "matrix_row_id": "matrix_003_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 3: validator observes canonical read-only evidence and compares 1 registries against policy segment 3.",
    "bad_pattern": "bad pattern 30 in matrix 3: writer drift toward family 2, generated path reports_real/segment_3_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_3_30, boundary=bnd_matrix_3_30, switch=sw_matrix_3_30, hash_hint=0faa61c5831c55b2"
  },
  {
    "matrix_row_id": "matrix_003_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 3: validator observes canonical read-only evidence and compares 2 registries against policy segment 3.",
    "bad_pattern": "bad pattern 31 in matrix 3: writer drift toward family 3, generated path reports_real/segment_3_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_3_31, boundary=bnd_matrix_3_31, switch=sw_matrix_3_31, hash_hint=d64048dd7f81bca7"
  },
  {
    "matrix_row_id": "matrix_003_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 3: validator observes canonical read-only evidence and compares 3 registries against policy segment 3.",
    "bad_pattern": "bad pattern 32 in matrix 3: writer drift toward family 4, generated path reports_real/segment_3_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_3_32, boundary=bnd_matrix_3_32, switch=sw_matrix_3_32, hash_hint=251c6cc5c3d77b66"
  },
  {
    "matrix_row_id": "matrix_003_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 3: validator observes canonical read-only evidence and compares 4 registries against policy segment 3.",
    "bad_pattern": "bad pattern 33 in matrix 3: writer drift toward family 5, generated path reports_real/segment_3_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_3_33, boundary=bnd_matrix_3_33, switch=sw_matrix_3_33, hash_hint=ac9bc4345a61544d"
  },
  {
    "matrix_row_id": "matrix_003_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 3: validator observes canonical read-only evidence and compares 5 registries against policy segment 3.",
    "bad_pattern": "bad pattern 34 in matrix 3: writer drift toward family 6, generated path reports_real/segment_3_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_3_34, boundary=bnd_matrix_3_34, switch=sw_matrix_3_34, hash_hint=b30a99641382498c"
  },
  {
    "matrix_row_id": "matrix_003_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 3: validator observes canonical read-only evidence and compares 1 registries against policy segment 3.",
    "bad_pattern": "bad pattern 35 in matrix 3: writer drift toward family 0, generated path reports_real/segment_3_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_3_35, boundary=bnd_matrix_3_35, switch=sw_matrix_3_35, hash_hint=642e45fc2e52257a"
  },
  {
    "matrix_row_id": "matrix_003_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 3: validator observes canonical read-only evidence and compares 2 registries against policy segment 3.",
    "bad_pattern": "bad pattern 36 in matrix 3: writer drift toward family 1, generated path reports_real/segment_3_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_3_36, boundary=bnd_matrix_3_36, switch=sw_matrix_3_36, hash_hint=ccad795dde381db6"
  },
  {
    "matrix_row_id": "matrix_003_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 3: validator observes canonical read-only evidence and compares 3 registries against policy segment 3.",
    "bad_pattern": "bad pattern 37 in matrix 3: writer drift toward family 2, generated path reports_real/segment_3_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_3_37, boundary=bnd_matrix_3_37, switch=sw_matrix_3_37, hash_hint=df649ed13c375b1b"
  },
  {
    "matrix_row_id": "matrix_003_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 3: validator observes canonical read-only evidence and compares 4 registries against policy segment 3.",
    "bad_pattern": "bad pattern 38 in matrix 3: writer drift toward family 3, generated path reports_real/segment_3_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_3_38, boundary=bnd_matrix_3_38, switch=sw_matrix_3_38, hash_hint=7893e4b6c77a000f"
  },
  {
    "matrix_row_id": "matrix_003_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 3: validator observes canonical read-only evidence and compares 5 registries against policy segment 3.",
    "bad_pattern": "bad pattern 39 in matrix 3: writer drift toward family 4, generated path reports_real/segment_3_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_3_39, boundary=bnd_matrix_3_39, switch=sw_matrix_3_39, hash_hint=0f011dae7905ca22"
  },
  {
    "matrix_row_id": "matrix_003_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 3: validator observes canonical read-only evidence and compares 1 registries against policy segment 3.",
    "bad_pattern": "bad pattern 40 in matrix 3: writer drift toward family 5, generated path reports_real/segment_3_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_3_40, boundary=bnd_matrix_3_40, switch=sw_matrix_3_40, hash_hint=428648c86b2f96bb"
  },
  {
    "matrix_row_id": "matrix_003_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 3: validator observes canonical read-only evidence and compares 2 registries against policy segment 3.",
    "bad_pattern": "bad pattern 41 in matrix 3: writer drift toward family 6, generated path reports_real/segment_3_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_3_41, boundary=bnd_matrix_3_41, switch=sw_matrix_3_41, hash_hint=d3264cce91a22170"
  },
  {
    "matrix_row_id": "matrix_003_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 3: validator observes canonical read-only evidence and compares 3 registries against policy segment 3.",
    "bad_pattern": "bad pattern 42 in matrix 3: writer drift toward family 0, generated path reports_real/segment_3_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_3_42, boundary=bnd_matrix_3_42, switch=sw_matrix_3_42, hash_hint=c5156bf357e1010b"
  },
  {
    "matrix_row_id": "matrix_003_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 3: validator observes canonical read-only evidence and compares 4 registries against policy segment 3.",
    "bad_pattern": "bad pattern 43 in matrix 3: writer drift toward family 1, generated path reports_real/segment_3_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_3_43, boundary=bnd_matrix_3_43, switch=sw_matrix_3_43, hash_hint=2f689778afe4f7a6"
  },
  {
    "matrix_row_id": "matrix_003_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 3: validator observes canonical read-only evidence and compares 5 registries against policy segment 3.",
    "bad_pattern": "bad pattern 44 in matrix 3: writer drift toward family 2, generated path reports_real/segment_3_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_3_44, boundary=bnd_matrix_3_44, switch=sw_matrix_3_44, hash_hint=054768e70361afa3"
  },
  {
    "matrix_row_id": "matrix_003_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 3: validator observes canonical read-only evidence and compares 1 registries against policy segment 3.",
    "bad_pattern": "bad pattern 45 in matrix 3: writer drift toward family 3, generated path reports_real/segment_3_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_3_45, boundary=bnd_matrix_3_45, switch=sw_matrix_3_45, hash_hint=bacf6ba8cd288aa2"
  },
  {
    "matrix_row_id": "matrix_003_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 3: validator observes canonical read-only evidence and compares 2 registries against policy segment 3.",
    "bad_pattern": "bad pattern 46 in matrix 3: writer drift toward family 4, generated path reports_real/segment_3_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_3_46, boundary=bnd_matrix_3_46, switch=sw_matrix_3_46, hash_hint=bab322f7d8ac629c"
  },
  {
    "matrix_row_id": "matrix_003_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 3: validator observes canonical read-only evidence and compares 3 registries against policy segment 3.",
    "bad_pattern": "bad pattern 47 in matrix 3: writer drift toward family 5, generated path reports_real/segment_3_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_3_47, boundary=bnd_matrix_3_47, switch=sw_matrix_3_47, hash_hint=91855c9a6e7b46b1"
  },
  {
    "matrix_row_id": "matrix_003_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 3: validator observes canonical read-only evidence and compares 4 registries against policy segment 3.",
    "bad_pattern": "bad pattern 48 in matrix 3: writer drift toward family 6, generated path reports_real/segment_3_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_3_48, boundary=bnd_matrix_3_48, switch=sw_matrix_3_48, hash_hint=085ded2e1155a4e8"
  },
  {
    "matrix_row_id": "matrix_003_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 3: validator observes canonical read-only evidence and compares 5 registries against policy segment 3.",
    "bad_pattern": "bad pattern 49 in matrix 3: writer drift toward family 0, generated path reports_real/segment_3_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_3_49, boundary=bnd_matrix_3_49, switch=sw_matrix_3_49, hash_hint=b9fd07a611db91ba"
  },
  {
    "matrix_row_id": "matrix_003_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 3: validator observes canonical read-only evidence and compares 1 registries against policy segment 3.",
    "bad_pattern": "bad pattern 50 in matrix 3: writer drift toward family 1, generated path reports_real/segment_3_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_3_50, boundary=bnd_matrix_3_50, switch=sw_matrix_3_50, hash_hint=25f1289cbc0239dd"
  },
  {
    "matrix_row_id": "matrix_003_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 3: validator observes canonical read-only evidence and compares 2 registries against policy segment 3.",
    "bad_pattern": "bad pattern 51 in matrix 3: writer drift toward family 2, generated path reports_real/segment_3_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_3_51, boundary=bnd_matrix_3_51, switch=sw_matrix_3_51, hash_hint=7b051108b07e1845"
  },
  {
    "matrix_row_id": "matrix_003_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 3: validator observes canonical read-only evidence and compares 3 registries against policy segment 3.",
    "bad_pattern": "bad pattern 52 in matrix 3: writer drift toward family 3, generated path reports_real/segment_3_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_3_52, boundary=bnd_matrix_3_52, switch=sw_matrix_3_52, hash_hint=6afd636371e7bab6"
  },
  {
    "matrix_row_id": "matrix_003_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 3: validator observes canonical read-only evidence and compares 4 registries against policy segment 3.",
    "bad_pattern": "bad pattern 53 in matrix 3: writer drift toward family 4, generated path reports_real/segment_3_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_3_53, boundary=bnd_matrix_3_53, switch=sw_matrix_3_53, hash_hint=e03a608e4125b0a4"
  },
  {
    "matrix_row_id": "matrix_003_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 3: validator observes canonical read-only evidence and compares 5 registries against policy segment 3.",
    "bad_pattern": "bad pattern 54 in matrix 3: writer drift toward family 5, generated path reports_real/segment_3_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_3_54, boundary=bnd_matrix_3_54, switch=sw_matrix_3_54, hash_hint=e4ae9d1668f83192"
  },
  {
    "matrix_row_id": "matrix_003_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 3: validator observes canonical read-only evidence and compares 1 registries against policy segment 3.",
    "bad_pattern": "bad pattern 55 in matrix 3: writer drift toward family 6, generated path reports_real/segment_3_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_3_55, boundary=bnd_matrix_3_55, switch=sw_matrix_3_55, hash_hint=8c3cc7cd74a2ee2d"
  },
  {
    "matrix_row_id": "matrix_003_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 3: validator observes canonical read-only evidence and compares 2 registries against policy segment 3.",
    "bad_pattern": "bad pattern 56 in matrix 3: writer drift toward family 0, generated path reports_real/segment_3_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_3_56, boundary=bnd_matrix_3_56, switch=sw_matrix_3_56, hash_hint=a29833ade08e9c02"
  },
  {
    "matrix_row_id": "matrix_003_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 3: validator observes canonical read-only evidence and compares 3 registries against policy segment 3.",
    "bad_pattern": "bad pattern 57 in matrix 3: writer drift toward family 1, generated path reports_real/segment_3_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_3_57, boundary=bnd_matrix_3_57, switch=sw_matrix_3_57, hash_hint=67357559dd951c57"
  },
  {
    "matrix_row_id": "matrix_003_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 3: validator observes canonical read-only evidence and compares 4 registries against policy segment 3.",
    "bad_pattern": "bad pattern 58 in matrix 3: writer drift toward family 2, generated path reports_real/segment_3_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_3_58, boundary=bnd_matrix_3_58, switch=sw_matrix_3_58, hash_hint=8c6c1ca663b42f6b"
  },
  {
    "matrix_row_id": "matrix_003_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 3: validator observes canonical read-only evidence and compares 5 registries against policy segment 3.",
    "bad_pattern": "bad pattern 59 in matrix 3: writer drift toward family 3, generated path reports_real/segment_3_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_3_59, boundary=bnd_matrix_3_59, switch=sw_matrix_3_59, hash_hint=4dfd382ba3ec14a6"
  },
  {
    "matrix_row_id": "matrix_003_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 3: validator observes canonical read-only evidence and compares 1 registries against policy segment 3.",
    "bad_pattern": "bad pattern 60 in matrix 3: writer drift toward family 4, generated path reports_real/segment_3_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_3_60, boundary=bnd_matrix_3_60, switch=sw_matrix_3_60, hash_hint=852c27ff8a80c93e"
  }
]
