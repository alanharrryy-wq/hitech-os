from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 18/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 18/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 18/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 18/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 18/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 18/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 18/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 18/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 18/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 18/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 18/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 18/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 18/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 18/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 18/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 18/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 18/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 18/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 18/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 18/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 18/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 18/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 18/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 18/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 18/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_018_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 18: validator observes canonical read-only evidence and compares 2 registries against policy segment 18.",
    "bad_pattern": "bad pattern 1 in matrix 18: writer drift toward family 1, generated path reports_real/segment_18_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_18_1, boundary=bnd_matrix_18_1, switch=sw_matrix_18_1, hash_hint=ffc96b0440a64774"
  },
  {
    "matrix_row_id": "matrix_018_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 18: validator observes canonical read-only evidence and compares 3 registries against policy segment 18.",
    "bad_pattern": "bad pattern 2 in matrix 18: writer drift toward family 2, generated path reports_real/segment_18_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_18_2, boundary=bnd_matrix_18_2, switch=sw_matrix_18_2, hash_hint=f530d665a20290e0"
  },
  {
    "matrix_row_id": "matrix_018_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 18: validator observes canonical read-only evidence and compares 4 registries against policy segment 18.",
    "bad_pattern": "bad pattern 3 in matrix 18: writer drift toward family 3, generated path reports_real/segment_18_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_18_3, boundary=bnd_matrix_18_3, switch=sw_matrix_18_3, hash_hint=2f142c53db28c434"
  },
  {
    "matrix_row_id": "matrix_018_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 18: validator observes canonical read-only evidence and compares 5 registries against policy segment 18.",
    "bad_pattern": "bad pattern 4 in matrix 18: writer drift toward family 4, generated path reports_real/segment_18_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_18_4, boundary=bnd_matrix_18_4, switch=sw_matrix_18_4, hash_hint=c439ade72222618e"
  },
  {
    "matrix_row_id": "matrix_018_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 18: validator observes canonical read-only evidence and compares 1 registries against policy segment 18.",
    "bad_pattern": "bad pattern 5 in matrix 18: writer drift toward family 5, generated path reports_real/segment_18_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_18_5, boundary=bnd_matrix_18_5, switch=sw_matrix_18_5, hash_hint=48da059f82c3c2e9"
  },
  {
    "matrix_row_id": "matrix_018_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 18: validator observes canonical read-only evidence and compares 2 registries against policy segment 18.",
    "bad_pattern": "bad pattern 6 in matrix 18: writer drift toward family 6, generated path reports_real/segment_18_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_18_6, boundary=bnd_matrix_18_6, switch=sw_matrix_18_6, hash_hint=228420fa02a5841e"
  },
  {
    "matrix_row_id": "matrix_018_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 18: validator observes canonical read-only evidence and compares 3 registries against policy segment 18.",
    "bad_pattern": "bad pattern 7 in matrix 18: writer drift toward family 0, generated path reports_real/segment_18_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_18_7, boundary=bnd_matrix_18_7, switch=sw_matrix_18_7, hash_hint=ac805be273303116"
  },
  {
    "matrix_row_id": "matrix_018_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 18: validator observes canonical read-only evidence and compares 4 registries against policy segment 18.",
    "bad_pattern": "bad pattern 8 in matrix 18: writer drift toward family 1, generated path reports_real/segment_18_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_18_8, boundary=bnd_matrix_18_8, switch=sw_matrix_18_8, hash_hint=41388e739ac722f9"
  },
  {
    "matrix_row_id": "matrix_018_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 18: validator observes canonical read-only evidence and compares 5 registries against policy segment 18.",
    "bad_pattern": "bad pattern 9 in matrix 18: writer drift toward family 2, generated path reports_real/segment_18_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_18_9, boundary=bnd_matrix_18_9, switch=sw_matrix_18_9, hash_hint=e4dca4daa7a36506"
  },
  {
    "matrix_row_id": "matrix_018_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 18: validator observes canonical read-only evidence and compares 1 registries against policy segment 18.",
    "bad_pattern": "bad pattern 10 in matrix 18: writer drift toward family 3, generated path reports_real/segment_18_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_18_10, boundary=bnd_matrix_18_10, switch=sw_matrix_18_10, hash_hint=787385e4c717c6cb"
  },
  {
    "matrix_row_id": "matrix_018_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 18: validator observes canonical read-only evidence and compares 2 registries against policy segment 18.",
    "bad_pattern": "bad pattern 11 in matrix 18: writer drift toward family 4, generated path reports_real/segment_18_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_18_11, boundary=bnd_matrix_18_11, switch=sw_matrix_18_11, hash_hint=8682099c24162724"
  },
  {
    "matrix_row_id": "matrix_018_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 18: validator observes canonical read-only evidence and compares 3 registries against policy segment 18.",
    "bad_pattern": "bad pattern 12 in matrix 18: writer drift toward family 5, generated path reports_real/segment_18_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_18_12, boundary=bnd_matrix_18_12, switch=sw_matrix_18_12, hash_hint=327d4621220a2208"
  },
  {
    "matrix_row_id": "matrix_018_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 18: validator observes canonical read-only evidence and compares 4 registries against policy segment 18.",
    "bad_pattern": "bad pattern 13 in matrix 18: writer drift toward family 6, generated path reports_real/segment_18_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_18_13, boundary=bnd_matrix_18_13, switch=sw_matrix_18_13, hash_hint=c54ac87fac127aa0"
  },
  {
    "matrix_row_id": "matrix_018_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 18: validator observes canonical read-only evidence and compares 5 registries against policy segment 18.",
    "bad_pattern": "bad pattern 14 in matrix 18: writer drift toward family 0, generated path reports_real/segment_18_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_18_14, boundary=bnd_matrix_18_14, switch=sw_matrix_18_14, hash_hint=2bc9e1ba2f628b9f"
  },
  {
    "matrix_row_id": "matrix_018_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 18: validator observes canonical read-only evidence and compares 1 registries against policy segment 18.",
    "bad_pattern": "bad pattern 15 in matrix 18: writer drift toward family 1, generated path reports_real/segment_18_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_18_15, boundary=bnd_matrix_18_15, switch=sw_matrix_18_15, hash_hint=7ae2e16bce4d1201"
  },
  {
    "matrix_row_id": "matrix_018_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 18: validator observes canonical read-only evidence and compares 2 registries against policy segment 18.",
    "bad_pattern": "bad pattern 16 in matrix 18: writer drift toward family 2, generated path reports_real/segment_18_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_18_16, boundary=bnd_matrix_18_16, switch=sw_matrix_18_16, hash_hint=37369cb59364c730"
  },
  {
    "matrix_row_id": "matrix_018_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 18: validator observes canonical read-only evidence and compares 3 registries against policy segment 18.",
    "bad_pattern": "bad pattern 17 in matrix 18: writer drift toward family 3, generated path reports_real/segment_18_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_18_17, boundary=bnd_matrix_18_17, switch=sw_matrix_18_17, hash_hint=a9aa1eb80c1df532"
  },
  {
    "matrix_row_id": "matrix_018_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 18: validator observes canonical read-only evidence and compares 4 registries against policy segment 18.",
    "bad_pattern": "bad pattern 18 in matrix 18: writer drift toward family 4, generated path reports_real/segment_18_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_18_18, boundary=bnd_matrix_18_18, switch=sw_matrix_18_18, hash_hint=cedd556b6198f425"
  },
  {
    "matrix_row_id": "matrix_018_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 18: validator observes canonical read-only evidence and compares 5 registries against policy segment 18.",
    "bad_pattern": "bad pattern 19 in matrix 18: writer drift toward family 5, generated path reports_real/segment_18_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_18_19, boundary=bnd_matrix_18_19, switch=sw_matrix_18_19, hash_hint=5f4f15b50f4ceb0e"
  },
  {
    "matrix_row_id": "matrix_018_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 18: validator observes canonical read-only evidence and compares 1 registries against policy segment 18.",
    "bad_pattern": "bad pattern 20 in matrix 18: writer drift toward family 6, generated path reports_real/segment_18_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_18_20, boundary=bnd_matrix_18_20, switch=sw_matrix_18_20, hash_hint=d8c4bdc7d625c66e"
  },
  {
    "matrix_row_id": "matrix_018_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 18: validator observes canonical read-only evidence and compares 2 registries against policy segment 18.",
    "bad_pattern": "bad pattern 21 in matrix 18: writer drift toward family 0, generated path reports_real/segment_18_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_18_21, boundary=bnd_matrix_18_21, switch=sw_matrix_18_21, hash_hint=0d117be7130f149b"
  },
  {
    "matrix_row_id": "matrix_018_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 18: validator observes canonical read-only evidence and compares 3 registries against policy segment 18.",
    "bad_pattern": "bad pattern 22 in matrix 18: writer drift toward family 1, generated path reports_real/segment_18_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_18_22, boundary=bnd_matrix_18_22, switch=sw_matrix_18_22, hash_hint=98ededeab8db33fc"
  },
  {
    "matrix_row_id": "matrix_018_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 18: validator observes canonical read-only evidence and compares 4 registries against policy segment 18.",
    "bad_pattern": "bad pattern 23 in matrix 18: writer drift toward family 2, generated path reports_real/segment_18_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_18_23, boundary=bnd_matrix_18_23, switch=sw_matrix_18_23, hash_hint=693d2759049706ac"
  },
  {
    "matrix_row_id": "matrix_018_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 18: validator observes canonical read-only evidence and compares 5 registries against policy segment 18.",
    "bad_pattern": "bad pattern 24 in matrix 18: writer drift toward family 3, generated path reports_real/segment_18_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_18_24, boundary=bnd_matrix_18_24, switch=sw_matrix_18_24, hash_hint=3deeb5924bd47f3b"
  },
  {
    "matrix_row_id": "matrix_018_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 18: validator observes canonical read-only evidence and compares 1 registries against policy segment 18.",
    "bad_pattern": "bad pattern 25 in matrix 18: writer drift toward family 4, generated path reports_real/segment_18_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_18_25, boundary=bnd_matrix_18_25, switch=sw_matrix_18_25, hash_hint=a5c92816e325214a"
  },
  {
    "matrix_row_id": "matrix_018_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 18: validator observes canonical read-only evidence and compares 2 registries against policy segment 18.",
    "bad_pattern": "bad pattern 26 in matrix 18: writer drift toward family 5, generated path reports_real/segment_18_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_18_26, boundary=bnd_matrix_18_26, switch=sw_matrix_18_26, hash_hint=bb714df797a726de"
  },
  {
    "matrix_row_id": "matrix_018_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 18: validator observes canonical read-only evidence and compares 3 registries against policy segment 18.",
    "bad_pattern": "bad pattern 27 in matrix 18: writer drift toward family 6, generated path reports_real/segment_18_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_18_27, boundary=bnd_matrix_18_27, switch=sw_matrix_18_27, hash_hint=a4a4872a2a63dcca"
  },
  {
    "matrix_row_id": "matrix_018_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 18: validator observes canonical read-only evidence and compares 4 registries against policy segment 18.",
    "bad_pattern": "bad pattern 28 in matrix 18: writer drift toward family 0, generated path reports_real/segment_18_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_18_28, boundary=bnd_matrix_18_28, switch=sw_matrix_18_28, hash_hint=91d70cf8683a92ea"
  },
  {
    "matrix_row_id": "matrix_018_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 18: validator observes canonical read-only evidence and compares 5 registries against policy segment 18.",
    "bad_pattern": "bad pattern 29 in matrix 18: writer drift toward family 1, generated path reports_real/segment_18_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_18_29, boundary=bnd_matrix_18_29, switch=sw_matrix_18_29, hash_hint=c5e0a7855d2ccd8e"
  },
  {
    "matrix_row_id": "matrix_018_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 18: validator observes canonical read-only evidence and compares 1 registries against policy segment 18.",
    "bad_pattern": "bad pattern 30 in matrix 18: writer drift toward family 2, generated path reports_real/segment_18_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_18_30, boundary=bnd_matrix_18_30, switch=sw_matrix_18_30, hash_hint=5f128e1b69bffffe"
  },
  {
    "matrix_row_id": "matrix_018_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 18: validator observes canonical read-only evidence and compares 2 registries against policy segment 18.",
    "bad_pattern": "bad pattern 31 in matrix 18: writer drift toward family 3, generated path reports_real/segment_18_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_18_31, boundary=bnd_matrix_18_31, switch=sw_matrix_18_31, hash_hint=a85298eca78b549a"
  },
  {
    "matrix_row_id": "matrix_018_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 18: validator observes canonical read-only evidence and compares 3 registries against policy segment 18.",
    "bad_pattern": "bad pattern 32 in matrix 18: writer drift toward family 4, generated path reports_real/segment_18_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_18_32, boundary=bnd_matrix_18_32, switch=sw_matrix_18_32, hash_hint=545f84df1c1c240f"
  },
  {
    "matrix_row_id": "matrix_018_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 18: validator observes canonical read-only evidence and compares 4 registries against policy segment 18.",
    "bad_pattern": "bad pattern 33 in matrix 18: writer drift toward family 5, generated path reports_real/segment_18_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_18_33, boundary=bnd_matrix_18_33, switch=sw_matrix_18_33, hash_hint=c2b0b8f77416ab1a"
  },
  {
    "matrix_row_id": "matrix_018_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 18: validator observes canonical read-only evidence and compares 5 registries against policy segment 18.",
    "bad_pattern": "bad pattern 34 in matrix 18: writer drift toward family 6, generated path reports_real/segment_18_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_18_34, boundary=bnd_matrix_18_34, switch=sw_matrix_18_34, hash_hint=c2a9a875dc2b195a"
  },
  {
    "matrix_row_id": "matrix_018_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 18: validator observes canonical read-only evidence and compares 1 registries against policy segment 18.",
    "bad_pattern": "bad pattern 35 in matrix 18: writer drift toward family 0, generated path reports_real/segment_18_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_18_35, boundary=bnd_matrix_18_35, switch=sw_matrix_18_35, hash_hint=b44efd1e785f6931"
  },
  {
    "matrix_row_id": "matrix_018_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 18: validator observes canonical read-only evidence and compares 2 registries against policy segment 18.",
    "bad_pattern": "bad pattern 36 in matrix 18: writer drift toward family 1, generated path reports_real/segment_18_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_18_36, boundary=bnd_matrix_18_36, switch=sw_matrix_18_36, hash_hint=9c2eca1dfa252380"
  },
  {
    "matrix_row_id": "matrix_018_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 18: validator observes canonical read-only evidence and compares 3 registries against policy segment 18.",
    "bad_pattern": "bad pattern 37 in matrix 18: writer drift toward family 2, generated path reports_real/segment_18_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_18_37, boundary=bnd_matrix_18_37, switch=sw_matrix_18_37, hash_hint=d215f9e7f1bf5986"
  },
  {
    "matrix_row_id": "matrix_018_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 18: validator observes canonical read-only evidence and compares 4 registries against policy segment 18.",
    "bad_pattern": "bad pattern 38 in matrix 18: writer drift toward family 3, generated path reports_real/segment_18_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_18_38, boundary=bnd_matrix_18_38, switch=sw_matrix_18_38, hash_hint=87d914402ec2b621"
  },
  {
    "matrix_row_id": "matrix_018_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 18: validator observes canonical read-only evidence and compares 5 registries against policy segment 18.",
    "bad_pattern": "bad pattern 39 in matrix 18: writer drift toward family 4, generated path reports_real/segment_18_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_18_39, boundary=bnd_matrix_18_39, switch=sw_matrix_18_39, hash_hint=87845922893531ae"
  },
  {
    "matrix_row_id": "matrix_018_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 18: validator observes canonical read-only evidence and compares 1 registries against policy segment 18.",
    "bad_pattern": "bad pattern 40 in matrix 18: writer drift toward family 5, generated path reports_real/segment_18_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_18_40, boundary=bnd_matrix_18_40, switch=sw_matrix_18_40, hash_hint=6aa5440745f8dbc6"
  },
  {
    "matrix_row_id": "matrix_018_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 18: validator observes canonical read-only evidence and compares 2 registries against policy segment 18.",
    "bad_pattern": "bad pattern 41 in matrix 18: writer drift toward family 6, generated path reports_real/segment_18_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_18_41, boundary=bnd_matrix_18_41, switch=sw_matrix_18_41, hash_hint=ff564fa69a1addf1"
  },
  {
    "matrix_row_id": "matrix_018_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 18: validator observes canonical read-only evidence and compares 3 registries against policy segment 18.",
    "bad_pattern": "bad pattern 42 in matrix 18: writer drift toward family 0, generated path reports_real/segment_18_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_18_42, boundary=bnd_matrix_18_42, switch=sw_matrix_18_42, hash_hint=dd0304c26d9d3a65"
  },
  {
    "matrix_row_id": "matrix_018_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 18: validator observes canonical read-only evidence and compares 4 registries against policy segment 18.",
    "bad_pattern": "bad pattern 43 in matrix 18: writer drift toward family 1, generated path reports_real/segment_18_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_18_43, boundary=bnd_matrix_18_43, switch=sw_matrix_18_43, hash_hint=e42800f3b2f58890"
  },
  {
    "matrix_row_id": "matrix_018_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 18: validator observes canonical read-only evidence and compares 5 registries against policy segment 18.",
    "bad_pattern": "bad pattern 44 in matrix 18: writer drift toward family 2, generated path reports_real/segment_18_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_18_44, boundary=bnd_matrix_18_44, switch=sw_matrix_18_44, hash_hint=59e2e9fa4b65aee3"
  },
  {
    "matrix_row_id": "matrix_018_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 18: validator observes canonical read-only evidence and compares 1 registries against policy segment 18.",
    "bad_pattern": "bad pattern 45 in matrix 18: writer drift toward family 3, generated path reports_real/segment_18_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_18_45, boundary=bnd_matrix_18_45, switch=sw_matrix_18_45, hash_hint=a9962c6e3694f4d6"
  },
  {
    "matrix_row_id": "matrix_018_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 18: validator observes canonical read-only evidence and compares 2 registries against policy segment 18.",
    "bad_pattern": "bad pattern 46 in matrix 18: writer drift toward family 4, generated path reports_real/segment_18_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_18_46, boundary=bnd_matrix_18_46, switch=sw_matrix_18_46, hash_hint=c210ff07c0c04e52"
  },
  {
    "matrix_row_id": "matrix_018_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 18: validator observes canonical read-only evidence and compares 3 registries against policy segment 18.",
    "bad_pattern": "bad pattern 47 in matrix 18: writer drift toward family 5, generated path reports_real/segment_18_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_18_47, boundary=bnd_matrix_18_47, switch=sw_matrix_18_47, hash_hint=5f0df331413b6b56"
  },
  {
    "matrix_row_id": "matrix_018_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 18: validator observes canonical read-only evidence and compares 4 registries against policy segment 18.",
    "bad_pattern": "bad pattern 48 in matrix 18: writer drift toward family 6, generated path reports_real/segment_18_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_18_48, boundary=bnd_matrix_18_48, switch=sw_matrix_18_48, hash_hint=31469ead3ab9271d"
  },
  {
    "matrix_row_id": "matrix_018_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 18: validator observes canonical read-only evidence and compares 5 registries against policy segment 18.",
    "bad_pattern": "bad pattern 49 in matrix 18: writer drift toward family 0, generated path reports_real/segment_18_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_18_49, boundary=bnd_matrix_18_49, switch=sw_matrix_18_49, hash_hint=4aeba1ea5388a06a"
  },
  {
    "matrix_row_id": "matrix_018_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 18: validator observes canonical read-only evidence and compares 1 registries against policy segment 18.",
    "bad_pattern": "bad pattern 50 in matrix 18: writer drift toward family 1, generated path reports_real/segment_18_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_18_50, boundary=bnd_matrix_18_50, switch=sw_matrix_18_50, hash_hint=3093f9f7add8f494"
  },
  {
    "matrix_row_id": "matrix_018_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 18: validator observes canonical read-only evidence and compares 2 registries against policy segment 18.",
    "bad_pattern": "bad pattern 51 in matrix 18: writer drift toward family 2, generated path reports_real/segment_18_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_18_51, boundary=bnd_matrix_18_51, switch=sw_matrix_18_51, hash_hint=a0f4f1070ef5b7d8"
  },
  {
    "matrix_row_id": "matrix_018_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 18: validator observes canonical read-only evidence and compares 3 registries against policy segment 18.",
    "bad_pattern": "bad pattern 52 in matrix 18: writer drift toward family 3, generated path reports_real/segment_18_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_18_52, boundary=bnd_matrix_18_52, switch=sw_matrix_18_52, hash_hint=8dd2655f3c5dd71b"
  },
  {
    "matrix_row_id": "matrix_018_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 18: validator observes canonical read-only evidence and compares 4 registries against policy segment 18.",
    "bad_pattern": "bad pattern 53 in matrix 18: writer drift toward family 4, generated path reports_real/segment_18_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_18_53, boundary=bnd_matrix_18_53, switch=sw_matrix_18_53, hash_hint=2e1848d861f5efbc"
  },
  {
    "matrix_row_id": "matrix_018_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 18: validator observes canonical read-only evidence and compares 5 registries against policy segment 18.",
    "bad_pattern": "bad pattern 54 in matrix 18: writer drift toward family 5, generated path reports_real/segment_18_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_18_54, boundary=bnd_matrix_18_54, switch=sw_matrix_18_54, hash_hint=383283624e582b2f"
  },
  {
    "matrix_row_id": "matrix_018_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 18: validator observes canonical read-only evidence and compares 1 registries against policy segment 18.",
    "bad_pattern": "bad pattern 55 in matrix 18: writer drift toward family 6, generated path reports_real/segment_18_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_18_55, boundary=bnd_matrix_18_55, switch=sw_matrix_18_55, hash_hint=60abd583fff81861"
  },
  {
    "matrix_row_id": "matrix_018_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 18: validator observes canonical read-only evidence and compares 2 registries against policy segment 18.",
    "bad_pattern": "bad pattern 56 in matrix 18: writer drift toward family 0, generated path reports_real/segment_18_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_18_56, boundary=bnd_matrix_18_56, switch=sw_matrix_18_56, hash_hint=31c7d7884e572de1"
  },
  {
    "matrix_row_id": "matrix_018_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 18: validator observes canonical read-only evidence and compares 3 registries against policy segment 18.",
    "bad_pattern": "bad pattern 57 in matrix 18: writer drift toward family 1, generated path reports_real/segment_18_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_18_57, boundary=bnd_matrix_18_57, switch=sw_matrix_18_57, hash_hint=abdc4b81d95723b7"
  },
  {
    "matrix_row_id": "matrix_018_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 18: validator observes canonical read-only evidence and compares 4 registries against policy segment 18.",
    "bad_pattern": "bad pattern 58 in matrix 18: writer drift toward family 2, generated path reports_real/segment_18_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_18_58, boundary=bnd_matrix_18_58, switch=sw_matrix_18_58, hash_hint=b04ea5b6c1c0bd9e"
  },
  {
    "matrix_row_id": "matrix_018_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 18: validator observes canonical read-only evidence and compares 5 registries against policy segment 18.",
    "bad_pattern": "bad pattern 59 in matrix 18: writer drift toward family 3, generated path reports_real/segment_18_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_18_59, boundary=bnd_matrix_18_59, switch=sw_matrix_18_59, hash_hint=4bee77a63577388e"
  },
  {
    "matrix_row_id": "matrix_018_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 18: validator observes canonical read-only evidence and compares 1 registries against policy segment 18.",
    "bad_pattern": "bad pattern 60 in matrix 18: writer drift toward family 4, generated path reports_real/segment_18_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_18_60, boundary=bnd_matrix_18_60, switch=sw_matrix_18_60, hash_hint=920f2ce5b4a5d75d"
  }
]
