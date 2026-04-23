from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 21/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 21/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 21/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 21/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 21/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 21/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 21/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 21/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 21/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 21/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 21/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 21/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 21/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 21/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 21/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 21/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 21/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 21/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 21/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 21/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 21/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 21/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 21/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 21/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 21/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_021_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 21: validator observes canonical read-only evidence and compares 2 registries against policy segment 21.",
    "bad_pattern": "bad pattern 1 in matrix 21: writer drift toward family 1, generated path reports_real/segment_21_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_21_1, boundary=bnd_matrix_21_1, switch=sw_matrix_21_1, hash_hint=1f0d872857cdc8be"
  },
  {
    "matrix_row_id": "matrix_021_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 21: validator observes canonical read-only evidence and compares 3 registries against policy segment 21.",
    "bad_pattern": "bad pattern 2 in matrix 21: writer drift toward family 2, generated path reports_real/segment_21_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_21_2, boundary=bnd_matrix_21_2, switch=sw_matrix_21_2, hash_hint=ab99d77b0f98ca9a"
  },
  {
    "matrix_row_id": "matrix_021_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 21: validator observes canonical read-only evidence and compares 4 registries against policy segment 21.",
    "bad_pattern": "bad pattern 3 in matrix 21: writer drift toward family 3, generated path reports_real/segment_21_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_21_3, boundary=bnd_matrix_21_3, switch=sw_matrix_21_3, hash_hint=2da4e26368702a26"
  },
  {
    "matrix_row_id": "matrix_021_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 21: validator observes canonical read-only evidence and compares 5 registries against policy segment 21.",
    "bad_pattern": "bad pattern 4 in matrix 21: writer drift toward family 4, generated path reports_real/segment_21_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_21_4, boundary=bnd_matrix_21_4, switch=sw_matrix_21_4, hash_hint=afdee041443a98d1"
  },
  {
    "matrix_row_id": "matrix_021_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 21: validator observes canonical read-only evidence and compares 1 registries against policy segment 21.",
    "bad_pattern": "bad pattern 5 in matrix 21: writer drift toward family 5, generated path reports_real/segment_21_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_21_5, boundary=bnd_matrix_21_5, switch=sw_matrix_21_5, hash_hint=39070f2c5bf888b2"
  },
  {
    "matrix_row_id": "matrix_021_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 21: validator observes canonical read-only evidence and compares 2 registries against policy segment 21.",
    "bad_pattern": "bad pattern 6 in matrix 21: writer drift toward family 6, generated path reports_real/segment_21_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_21_6, boundary=bnd_matrix_21_6, switch=sw_matrix_21_6, hash_hint=7b32a5010521dddf"
  },
  {
    "matrix_row_id": "matrix_021_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 21: validator observes canonical read-only evidence and compares 3 registries against policy segment 21.",
    "bad_pattern": "bad pattern 7 in matrix 21: writer drift toward family 0, generated path reports_real/segment_21_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_21_7, boundary=bnd_matrix_21_7, switch=sw_matrix_21_7, hash_hint=4f6f8747bd82aca1"
  },
  {
    "matrix_row_id": "matrix_021_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 21: validator observes canonical read-only evidence and compares 4 registries against policy segment 21.",
    "bad_pattern": "bad pattern 8 in matrix 21: writer drift toward family 1, generated path reports_real/segment_21_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_21_8, boundary=bnd_matrix_21_8, switch=sw_matrix_21_8, hash_hint=9f807ea6c18bd5ce"
  },
  {
    "matrix_row_id": "matrix_021_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 21: validator observes canonical read-only evidence and compares 5 registries against policy segment 21.",
    "bad_pattern": "bad pattern 9 in matrix 21: writer drift toward family 2, generated path reports_real/segment_21_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_21_9, boundary=bnd_matrix_21_9, switch=sw_matrix_21_9, hash_hint=c7f24f66afcae835"
  },
  {
    "matrix_row_id": "matrix_021_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 21: validator observes canonical read-only evidence and compares 1 registries against policy segment 21.",
    "bad_pattern": "bad pattern 10 in matrix 21: writer drift toward family 3, generated path reports_real/segment_21_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_21_10, boundary=bnd_matrix_21_10, switch=sw_matrix_21_10, hash_hint=6b71151220c8d880"
  },
  {
    "matrix_row_id": "matrix_021_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 21: validator observes canonical read-only evidence and compares 2 registries against policy segment 21.",
    "bad_pattern": "bad pattern 11 in matrix 21: writer drift toward family 4, generated path reports_real/segment_21_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_21_11, boundary=bnd_matrix_21_11, switch=sw_matrix_21_11, hash_hint=73b60a7f84c44670"
  },
  {
    "matrix_row_id": "matrix_021_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 21: validator observes canonical read-only evidence and compares 3 registries against policy segment 21.",
    "bad_pattern": "bad pattern 12 in matrix 21: writer drift toward family 5, generated path reports_real/segment_21_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_21_12, boundary=bnd_matrix_21_12, switch=sw_matrix_21_12, hash_hint=7094efe3e74a3791"
  },
  {
    "matrix_row_id": "matrix_021_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 21: validator observes canonical read-only evidence and compares 4 registries against policy segment 21.",
    "bad_pattern": "bad pattern 13 in matrix 21: writer drift toward family 6, generated path reports_real/segment_21_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_21_13, boundary=bnd_matrix_21_13, switch=sw_matrix_21_13, hash_hint=fc18c1ec76ef4438"
  },
  {
    "matrix_row_id": "matrix_021_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 21: validator observes canonical read-only evidence and compares 5 registries against policy segment 21.",
    "bad_pattern": "bad pattern 14 in matrix 21: writer drift toward family 0, generated path reports_real/segment_21_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_21_14, boundary=bnd_matrix_21_14, switch=sw_matrix_21_14, hash_hint=c0a039ca051838fa"
  },
  {
    "matrix_row_id": "matrix_021_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 21: validator observes canonical read-only evidence and compares 1 registries against policy segment 21.",
    "bad_pattern": "bad pattern 15 in matrix 21: writer drift toward family 1, generated path reports_real/segment_21_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_21_15, boundary=bnd_matrix_21_15, switch=sw_matrix_21_15, hash_hint=da3bb09852f3092e"
  },
  {
    "matrix_row_id": "matrix_021_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 21: validator observes canonical read-only evidence and compares 2 registries against policy segment 21.",
    "bad_pattern": "bad pattern 16 in matrix 21: writer drift toward family 2, generated path reports_real/segment_21_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_21_16, boundary=bnd_matrix_21_16, switch=sw_matrix_21_16, hash_hint=93411def7bcfa604"
  },
  {
    "matrix_row_id": "matrix_021_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 21: validator observes canonical read-only evidence and compares 3 registries against policy segment 21.",
    "bad_pattern": "bad pattern 17 in matrix 21: writer drift toward family 3, generated path reports_real/segment_21_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_21_17, boundary=bnd_matrix_21_17, switch=sw_matrix_21_17, hash_hint=8b89bdc76e5cc6df"
  },
  {
    "matrix_row_id": "matrix_021_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 21: validator observes canonical read-only evidence and compares 4 registries against policy segment 21.",
    "bad_pattern": "bad pattern 18 in matrix 21: writer drift toward family 4, generated path reports_real/segment_21_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_21_18, boundary=bnd_matrix_21_18, switch=sw_matrix_21_18, hash_hint=0db7cdf225dcefce"
  },
  {
    "matrix_row_id": "matrix_021_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 21: validator observes canonical read-only evidence and compares 5 registries against policy segment 21.",
    "bad_pattern": "bad pattern 19 in matrix 21: writer drift toward family 5, generated path reports_real/segment_21_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_21_19, boundary=bnd_matrix_21_19, switch=sw_matrix_21_19, hash_hint=0aacc50fcd34e48e"
  },
  {
    "matrix_row_id": "matrix_021_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 21: validator observes canonical read-only evidence and compares 1 registries against policy segment 21.",
    "bad_pattern": "bad pattern 20 in matrix 21: writer drift toward family 6, generated path reports_real/segment_21_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_21_20, boundary=bnd_matrix_21_20, switch=sw_matrix_21_20, hash_hint=45805c0078c606d4"
  },
  {
    "matrix_row_id": "matrix_021_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 21: validator observes canonical read-only evidence and compares 2 registries against policy segment 21.",
    "bad_pattern": "bad pattern 21 in matrix 21: writer drift toward family 0, generated path reports_real/segment_21_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_21_21, boundary=bnd_matrix_21_21, switch=sw_matrix_21_21, hash_hint=73a0d3c377ca8311"
  },
  {
    "matrix_row_id": "matrix_021_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 21: validator observes canonical read-only evidence and compares 3 registries against policy segment 21.",
    "bad_pattern": "bad pattern 22 in matrix 21: writer drift toward family 1, generated path reports_real/segment_21_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_21_22, boundary=bnd_matrix_21_22, switch=sw_matrix_21_22, hash_hint=8052249c934a46b2"
  },
  {
    "matrix_row_id": "matrix_021_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 21: validator observes canonical read-only evidence and compares 4 registries against policy segment 21.",
    "bad_pattern": "bad pattern 23 in matrix 21: writer drift toward family 2, generated path reports_real/segment_21_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_21_23, boundary=bnd_matrix_21_23, switch=sw_matrix_21_23, hash_hint=4d5df2780acf2be0"
  },
  {
    "matrix_row_id": "matrix_021_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 21: validator observes canonical read-only evidence and compares 5 registries against policy segment 21.",
    "bad_pattern": "bad pattern 24 in matrix 21: writer drift toward family 3, generated path reports_real/segment_21_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_21_24, boundary=bnd_matrix_21_24, switch=sw_matrix_21_24, hash_hint=05aac51b42fb3008"
  },
  {
    "matrix_row_id": "matrix_021_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 21: validator observes canonical read-only evidence and compares 1 registries against policy segment 21.",
    "bad_pattern": "bad pattern 25 in matrix 21: writer drift toward family 4, generated path reports_real/segment_21_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_21_25, boundary=bnd_matrix_21_25, switch=sw_matrix_21_25, hash_hint=76223a923dc9b6e6"
  },
  {
    "matrix_row_id": "matrix_021_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 21: validator observes canonical read-only evidence and compares 2 registries against policy segment 21.",
    "bad_pattern": "bad pattern 26 in matrix 21: writer drift toward family 5, generated path reports_real/segment_21_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_21_26, boundary=bnd_matrix_21_26, switch=sw_matrix_21_26, hash_hint=58dc28b7ee98a60c"
  },
  {
    "matrix_row_id": "matrix_021_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 21: validator observes canonical read-only evidence and compares 3 registries against policy segment 21.",
    "bad_pattern": "bad pattern 27 in matrix 21: writer drift toward family 6, generated path reports_real/segment_21_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_21_27, boundary=bnd_matrix_21_27, switch=sw_matrix_21_27, hash_hint=5ec235779fede5c5"
  },
  {
    "matrix_row_id": "matrix_021_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 21: validator observes canonical read-only evidence and compares 4 registries against policy segment 21.",
    "bad_pattern": "bad pattern 28 in matrix 21: writer drift toward family 0, generated path reports_real/segment_21_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_21_28, boundary=bnd_matrix_21_28, switch=sw_matrix_21_28, hash_hint=779eabb890bf2a8a"
  },
  {
    "matrix_row_id": "matrix_021_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 21: validator observes canonical read-only evidence and compares 5 registries against policy segment 21.",
    "bad_pattern": "bad pattern 29 in matrix 21: writer drift toward family 1, generated path reports_real/segment_21_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_21_29, boundary=bnd_matrix_21_29, switch=sw_matrix_21_29, hash_hint=ddc093f2a554a2f7"
  },
  {
    "matrix_row_id": "matrix_021_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 21: validator observes canonical read-only evidence and compares 1 registries against policy segment 21.",
    "bad_pattern": "bad pattern 30 in matrix 21: writer drift toward family 2, generated path reports_real/segment_21_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_21_30, boundary=bnd_matrix_21_30, switch=sw_matrix_21_30, hash_hint=87c04efd356a935c"
  },
  {
    "matrix_row_id": "matrix_021_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 21: validator observes canonical read-only evidence and compares 2 registries against policy segment 21.",
    "bad_pattern": "bad pattern 31 in matrix 21: writer drift toward family 3, generated path reports_real/segment_21_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_21_31, boundary=bnd_matrix_21_31, switch=sw_matrix_21_31, hash_hint=98c6834ef5ccb727"
  },
  {
    "matrix_row_id": "matrix_021_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 21: validator observes canonical read-only evidence and compares 3 registries against policy segment 21.",
    "bad_pattern": "bad pattern 32 in matrix 21: writer drift toward family 4, generated path reports_real/segment_21_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_21_32, boundary=bnd_matrix_21_32, switch=sw_matrix_21_32, hash_hint=25b7734d7536191f"
  },
  {
    "matrix_row_id": "matrix_021_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 21: validator observes canonical read-only evidence and compares 4 registries against policy segment 21.",
    "bad_pattern": "bad pattern 33 in matrix 21: writer drift toward family 5, generated path reports_real/segment_21_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_21_33, boundary=bnd_matrix_21_33, switch=sw_matrix_21_33, hash_hint=95c7c09e3f81b471"
  },
  {
    "matrix_row_id": "matrix_021_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 21: validator observes canonical read-only evidence and compares 5 registries against policy segment 21.",
    "bad_pattern": "bad pattern 34 in matrix 21: writer drift toward family 6, generated path reports_real/segment_21_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_21_34, boundary=bnd_matrix_21_34, switch=sw_matrix_21_34, hash_hint=806b345f953bcdbd"
  },
  {
    "matrix_row_id": "matrix_021_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 21: validator observes canonical read-only evidence and compares 1 registries against policy segment 21.",
    "bad_pattern": "bad pattern 35 in matrix 21: writer drift toward family 0, generated path reports_real/segment_21_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_21_35, boundary=bnd_matrix_21_35, switch=sw_matrix_21_35, hash_hint=87616247d4de7627"
  },
  {
    "matrix_row_id": "matrix_021_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 21: validator observes canonical read-only evidence and compares 2 registries against policy segment 21.",
    "bad_pattern": "bad pattern 36 in matrix 21: writer drift toward family 1, generated path reports_real/segment_21_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_21_36, boundary=bnd_matrix_21_36, switch=sw_matrix_21_36, hash_hint=2ceb55761c3a4d95"
  },
  {
    "matrix_row_id": "matrix_021_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 21: validator observes canonical read-only evidence and compares 3 registries against policy segment 21.",
    "bad_pattern": "bad pattern 37 in matrix 21: writer drift toward family 2, generated path reports_real/segment_21_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_21_37, boundary=bnd_matrix_21_37, switch=sw_matrix_21_37, hash_hint=6e04eac6073022ac"
  },
  {
    "matrix_row_id": "matrix_021_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 21: validator observes canonical read-only evidence and compares 4 registries against policy segment 21.",
    "bad_pattern": "bad pattern 38 in matrix 21: writer drift toward family 3, generated path reports_real/segment_21_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_21_38, boundary=bnd_matrix_21_38, switch=sw_matrix_21_38, hash_hint=3935fa54a6b361d9"
  },
  {
    "matrix_row_id": "matrix_021_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 21: validator observes canonical read-only evidence and compares 5 registries against policy segment 21.",
    "bad_pattern": "bad pattern 39 in matrix 21: writer drift toward family 4, generated path reports_real/segment_21_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_21_39, boundary=bnd_matrix_21_39, switch=sw_matrix_21_39, hash_hint=4687d87001e2e330"
  },
  {
    "matrix_row_id": "matrix_021_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 21: validator observes canonical read-only evidence and compares 1 registries against policy segment 21.",
    "bad_pattern": "bad pattern 40 in matrix 21: writer drift toward family 5, generated path reports_real/segment_21_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_21_40, boundary=bnd_matrix_21_40, switch=sw_matrix_21_40, hash_hint=0a611884b90b0580"
  },
  {
    "matrix_row_id": "matrix_021_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 21: validator observes canonical read-only evidence and compares 2 registries against policy segment 21.",
    "bad_pattern": "bad pattern 41 in matrix 21: writer drift toward family 6, generated path reports_real/segment_21_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_21_41, boundary=bnd_matrix_21_41, switch=sw_matrix_21_41, hash_hint=f57e19e1a39e2edc"
  },
  {
    "matrix_row_id": "matrix_021_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 21: validator observes canonical read-only evidence and compares 3 registries against policy segment 21.",
    "bad_pattern": "bad pattern 42 in matrix 21: writer drift toward family 0, generated path reports_real/segment_21_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_21_42, boundary=bnd_matrix_21_42, switch=sw_matrix_21_42, hash_hint=1cf92d53a334fcf5"
  },
  {
    "matrix_row_id": "matrix_021_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 21: validator observes canonical read-only evidence and compares 4 registries against policy segment 21.",
    "bad_pattern": "bad pattern 43 in matrix 21: writer drift toward family 1, generated path reports_real/segment_21_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_21_43, boundary=bnd_matrix_21_43, switch=sw_matrix_21_43, hash_hint=20a70ab44a84fdaf"
  },
  {
    "matrix_row_id": "matrix_021_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 21: validator observes canonical read-only evidence and compares 5 registries against policy segment 21.",
    "bad_pattern": "bad pattern 44 in matrix 21: writer drift toward family 2, generated path reports_real/segment_21_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_21_44, boundary=bnd_matrix_21_44, switch=sw_matrix_21_44, hash_hint=94873ea026af68fa"
  },
  {
    "matrix_row_id": "matrix_021_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 21: validator observes canonical read-only evidence and compares 1 registries against policy segment 21.",
    "bad_pattern": "bad pattern 45 in matrix 21: writer drift toward family 3, generated path reports_real/segment_21_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_21_45, boundary=bnd_matrix_21_45, switch=sw_matrix_21_45, hash_hint=c54c9edd7799c861"
  },
  {
    "matrix_row_id": "matrix_021_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 21: validator observes canonical read-only evidence and compares 2 registries against policy segment 21.",
    "bad_pattern": "bad pattern 46 in matrix 21: writer drift toward family 4, generated path reports_real/segment_21_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_21_46, boundary=bnd_matrix_21_46, switch=sw_matrix_21_46, hash_hint=cce8d0c7d193ad61"
  },
  {
    "matrix_row_id": "matrix_021_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 21: validator observes canonical read-only evidence and compares 3 registries against policy segment 21.",
    "bad_pattern": "bad pattern 47 in matrix 21: writer drift toward family 5, generated path reports_real/segment_21_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_21_47, boundary=bnd_matrix_21_47, switch=sw_matrix_21_47, hash_hint=0b6a1aa0c5a82d35"
  },
  {
    "matrix_row_id": "matrix_021_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 21: validator observes canonical read-only evidence and compares 4 registries against policy segment 21.",
    "bad_pattern": "bad pattern 48 in matrix 21: writer drift toward family 6, generated path reports_real/segment_21_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_21_48, boundary=bnd_matrix_21_48, switch=sw_matrix_21_48, hash_hint=936a0d532eef86f0"
  },
  {
    "matrix_row_id": "matrix_021_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 21: validator observes canonical read-only evidence and compares 5 registries against policy segment 21.",
    "bad_pattern": "bad pattern 49 in matrix 21: writer drift toward family 0, generated path reports_real/segment_21_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_21_49, boundary=bnd_matrix_21_49, switch=sw_matrix_21_49, hash_hint=5d020f2ffe9a8203"
  },
  {
    "matrix_row_id": "matrix_021_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 21: validator observes canonical read-only evidence and compares 1 registries against policy segment 21.",
    "bad_pattern": "bad pattern 50 in matrix 21: writer drift toward family 1, generated path reports_real/segment_21_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_21_50, boundary=bnd_matrix_21_50, switch=sw_matrix_21_50, hash_hint=5eb87a3c7e37894c"
  },
  {
    "matrix_row_id": "matrix_021_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 21: validator observes canonical read-only evidence and compares 2 registries against policy segment 21.",
    "bad_pattern": "bad pattern 51 in matrix 21: writer drift toward family 2, generated path reports_real/segment_21_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_21_51, boundary=bnd_matrix_21_51, switch=sw_matrix_21_51, hash_hint=2a745b4fa9bbc44c"
  },
  {
    "matrix_row_id": "matrix_021_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 21: validator observes canonical read-only evidence and compares 3 registries against policy segment 21.",
    "bad_pattern": "bad pattern 52 in matrix 21: writer drift toward family 3, generated path reports_real/segment_21_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_21_52, boundary=bnd_matrix_21_52, switch=sw_matrix_21_52, hash_hint=95fafc9f73760606"
  },
  {
    "matrix_row_id": "matrix_021_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 21: validator observes canonical read-only evidence and compares 4 registries against policy segment 21.",
    "bad_pattern": "bad pattern 53 in matrix 21: writer drift toward family 4, generated path reports_real/segment_21_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_21_53, boundary=bnd_matrix_21_53, switch=sw_matrix_21_53, hash_hint=b0045b54767588c6"
  },
  {
    "matrix_row_id": "matrix_021_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 21: validator observes canonical read-only evidence and compares 5 registries against policy segment 21.",
    "bad_pattern": "bad pattern 54 in matrix 21: writer drift toward family 5, generated path reports_real/segment_21_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_21_54, boundary=bnd_matrix_21_54, switch=sw_matrix_21_54, hash_hint=17bac089e68d4013"
  },
  {
    "matrix_row_id": "matrix_021_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 21: validator observes canonical read-only evidence and compares 1 registries against policy segment 21.",
    "bad_pattern": "bad pattern 55 in matrix 21: writer drift toward family 6, generated path reports_real/segment_21_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_21_55, boundary=bnd_matrix_21_55, switch=sw_matrix_21_55, hash_hint=62aadafbd2c1dd9a"
  },
  {
    "matrix_row_id": "matrix_021_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 21: validator observes canonical read-only evidence and compares 2 registries against policy segment 21.",
    "bad_pattern": "bad pattern 56 in matrix 21: writer drift toward family 0, generated path reports_real/segment_21_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_21_56, boundary=bnd_matrix_21_56, switch=sw_matrix_21_56, hash_hint=324ed0f628deef77"
  },
  {
    "matrix_row_id": "matrix_021_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 21: validator observes canonical read-only evidence and compares 3 registries against policy segment 21.",
    "bad_pattern": "bad pattern 57 in matrix 21: writer drift toward family 1, generated path reports_real/segment_21_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_21_57, boundary=bnd_matrix_21_57, switch=sw_matrix_21_57, hash_hint=1e5a1ddfbf8aeb26"
  },
  {
    "matrix_row_id": "matrix_021_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 21: validator observes canonical read-only evidence and compares 4 registries against policy segment 21.",
    "bad_pattern": "bad pattern 58 in matrix 21: writer drift toward family 2, generated path reports_real/segment_21_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_21_58, boundary=bnd_matrix_21_58, switch=sw_matrix_21_58, hash_hint=f629de37b89ae4e5"
  },
  {
    "matrix_row_id": "matrix_021_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 21: validator observes canonical read-only evidence and compares 5 registries against policy segment 21.",
    "bad_pattern": "bad pattern 59 in matrix 21: writer drift toward family 3, generated path reports_real/segment_21_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_21_59, boundary=bnd_matrix_21_59, switch=sw_matrix_21_59, hash_hint=95651003e2b2d1a0"
  },
  {
    "matrix_row_id": "matrix_021_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 21: validator observes canonical read-only evidence and compares 1 registries against policy segment 21.",
    "bad_pattern": "bad pattern 60 in matrix 21: writer drift toward family 4, generated path reports_real/segment_21_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_21_60, boundary=bnd_matrix_21_60, switch=sw_matrix_21_60, hash_hint=c54ed924d1fa983b"
  }
]
