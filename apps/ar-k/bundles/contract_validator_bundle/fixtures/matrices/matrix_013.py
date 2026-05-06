from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 13/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 13/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 13/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 13/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 13/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 13/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 13/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 13/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 13/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 13/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 13/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 13/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 13/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 13/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 13/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 13/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 13/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 13/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 13/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 13/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 13/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 13/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 13/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 13/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 13/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_013_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 13: validator observes canonical read-only evidence and compares 2 registries against policy segment 13.",
    "bad_pattern": "bad pattern 1 in matrix 13: writer drift toward family 1, generated path reports_real/segment_13_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_13_1, boundary=bnd_matrix_13_1, switch=sw_matrix_13_1, hash_hint=fb7460786a8266cb"
  },
  {
    "matrix_row_id": "matrix_013_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 13: validator observes canonical read-only evidence and compares 3 registries against policy segment 13.",
    "bad_pattern": "bad pattern 2 in matrix 13: writer drift toward family 2, generated path reports_real/segment_13_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_13_2, boundary=bnd_matrix_13_2, switch=sw_matrix_13_2, hash_hint=5b4829fcff2cff1f"
  },
  {
    "matrix_row_id": "matrix_013_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 13: validator observes canonical read-only evidence and compares 4 registries against policy segment 13.",
    "bad_pattern": "bad pattern 3 in matrix 13: writer drift toward family 3, generated path reports_real/segment_13_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_13_3, boundary=bnd_matrix_13_3, switch=sw_matrix_13_3, hash_hint=2a227c710d442238"
  },
  {
    "matrix_row_id": "matrix_013_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 13: validator observes canonical read-only evidence and compares 5 registries against policy segment 13.",
    "bad_pattern": "bad pattern 4 in matrix 13: writer drift toward family 4, generated path reports_real/segment_13_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_13_4, boundary=bnd_matrix_13_4, switch=sw_matrix_13_4, hash_hint=c4cdaaf1b5e61180"
  },
  {
    "matrix_row_id": "matrix_013_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 13: validator observes canonical read-only evidence and compares 1 registries against policy segment 13.",
    "bad_pattern": "bad pattern 5 in matrix 13: writer drift toward family 5, generated path reports_real/segment_13_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_13_5, boundary=bnd_matrix_13_5, switch=sw_matrix_13_5, hash_hint=b987ef1216da82bd"
  },
  {
    "matrix_row_id": "matrix_013_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 13: validator observes canonical read-only evidence and compares 2 registries against policy segment 13.",
    "bad_pattern": "bad pattern 6 in matrix 13: writer drift toward family 6, generated path reports_real/segment_13_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_13_6, boundary=bnd_matrix_13_6, switch=sw_matrix_13_6, hash_hint=28dfb3821827f821"
  },
  {
    "matrix_row_id": "matrix_013_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 13: validator observes canonical read-only evidence and compares 3 registries against policy segment 13.",
    "bad_pattern": "bad pattern 7 in matrix 13: writer drift toward family 0, generated path reports_real/segment_13_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_13_7, boundary=bnd_matrix_13_7, switch=sw_matrix_13_7, hash_hint=1d103b43d7c881d2"
  },
  {
    "matrix_row_id": "matrix_013_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 13: validator observes canonical read-only evidence and compares 4 registries against policy segment 13.",
    "bad_pattern": "bad pattern 8 in matrix 13: writer drift toward family 1, generated path reports_real/segment_13_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_13_8, boundary=bnd_matrix_13_8, switch=sw_matrix_13_8, hash_hint=3f967d1610e58406"
  },
  {
    "matrix_row_id": "matrix_013_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 13: validator observes canonical read-only evidence and compares 5 registries against policy segment 13.",
    "bad_pattern": "bad pattern 9 in matrix 13: writer drift toward family 2, generated path reports_real/segment_13_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_13_9, boundary=bnd_matrix_13_9, switch=sw_matrix_13_9, hash_hint=f5f2d1815014328b"
  },
  {
    "matrix_row_id": "matrix_013_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 13: validator observes canonical read-only evidence and compares 1 registries against policy segment 13.",
    "bad_pattern": "bad pattern 10 in matrix 13: writer drift toward family 3, generated path reports_real/segment_13_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_13_10, boundary=bnd_matrix_13_10, switch=sw_matrix_13_10, hash_hint=eb1798700f29784c"
  },
  {
    "matrix_row_id": "matrix_013_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 13: validator observes canonical read-only evidence and compares 2 registries against policy segment 13.",
    "bad_pattern": "bad pattern 11 in matrix 13: writer drift toward family 4, generated path reports_real/segment_13_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_13_11, boundary=bnd_matrix_13_11, switch=sw_matrix_13_11, hash_hint=fdb41387dfc9f730"
  },
  {
    "matrix_row_id": "matrix_013_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 13: validator observes canonical read-only evidence and compares 3 registries against policy segment 13.",
    "bad_pattern": "bad pattern 12 in matrix 13: writer drift toward family 5, generated path reports_real/segment_13_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_13_12, boundary=bnd_matrix_13_12, switch=sw_matrix_13_12, hash_hint=12f4274a2afd80b2"
  },
  {
    "matrix_row_id": "matrix_013_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 13: validator observes canonical read-only evidence and compares 4 registries against policy segment 13.",
    "bad_pattern": "bad pattern 13 in matrix 13: writer drift toward family 6, generated path reports_real/segment_13_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_13_13, boundary=bnd_matrix_13_13, switch=sw_matrix_13_13, hash_hint=98a815bc7d40f153"
  },
  {
    "matrix_row_id": "matrix_013_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 13: validator observes canonical read-only evidence and compares 5 registries against policy segment 13.",
    "bad_pattern": "bad pattern 14 in matrix 13: writer drift toward family 0, generated path reports_real/segment_13_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_13_14, boundary=bnd_matrix_13_14, switch=sw_matrix_13_14, hash_hint=77d4c73da710f294"
  },
  {
    "matrix_row_id": "matrix_013_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 13: validator observes canonical read-only evidence and compares 1 registries against policy segment 13.",
    "bad_pattern": "bad pattern 15 in matrix 13: writer drift toward family 1, generated path reports_real/segment_13_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_13_15, boundary=bnd_matrix_13_15, switch=sw_matrix_13_15, hash_hint=22fd0c07c7a1136f"
  },
  {
    "matrix_row_id": "matrix_013_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 13: validator observes canonical read-only evidence and compares 2 registries against policy segment 13.",
    "bad_pattern": "bad pattern 16 in matrix 13: writer drift toward family 2, generated path reports_real/segment_13_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_13_16, boundary=bnd_matrix_13_16, switch=sw_matrix_13_16, hash_hint=3c369ff351de7b1a"
  },
  {
    "matrix_row_id": "matrix_013_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 13: validator observes canonical read-only evidence and compares 3 registries against policy segment 13.",
    "bad_pattern": "bad pattern 17 in matrix 13: writer drift toward family 3, generated path reports_real/segment_13_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_13_17, boundary=bnd_matrix_13_17, switch=sw_matrix_13_17, hash_hint=900803cdee2f5822"
  },
  {
    "matrix_row_id": "matrix_013_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 13: validator observes canonical read-only evidence and compares 4 registries against policy segment 13.",
    "bad_pattern": "bad pattern 18 in matrix 13: writer drift toward family 4, generated path reports_real/segment_13_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_13_18, boundary=bnd_matrix_13_18, switch=sw_matrix_13_18, hash_hint=02c2cf0ccedce10e"
  },
  {
    "matrix_row_id": "matrix_013_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 13: validator observes canonical read-only evidence and compares 5 registries against policy segment 13.",
    "bad_pattern": "bad pattern 19 in matrix 13: writer drift toward family 5, generated path reports_real/segment_13_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_13_19, boundary=bnd_matrix_13_19, switch=sw_matrix_13_19, hash_hint=144426de0b0eb3f7"
  },
  {
    "matrix_row_id": "matrix_013_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 13: validator observes canonical read-only evidence and compares 1 registries against policy segment 13.",
    "bad_pattern": "bad pattern 20 in matrix 13: writer drift toward family 6, generated path reports_real/segment_13_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_13_20, boundary=bnd_matrix_13_20, switch=sw_matrix_13_20, hash_hint=60b191990ade077f"
  },
  {
    "matrix_row_id": "matrix_013_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 13: validator observes canonical read-only evidence and compares 2 registries against policy segment 13.",
    "bad_pattern": "bad pattern 21 in matrix 13: writer drift toward family 0, generated path reports_real/segment_13_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_13_21, boundary=bnd_matrix_13_21, switch=sw_matrix_13_21, hash_hint=8ba02b6c4de95971"
  },
  {
    "matrix_row_id": "matrix_013_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 13: validator observes canonical read-only evidence and compares 3 registries against policy segment 13.",
    "bad_pattern": "bad pattern 22 in matrix 13: writer drift toward family 1, generated path reports_real/segment_13_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_13_22, boundary=bnd_matrix_13_22, switch=sw_matrix_13_22, hash_hint=f4110707bfb769f3"
  },
  {
    "matrix_row_id": "matrix_013_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 13: validator observes canonical read-only evidence and compares 4 registries against policy segment 13.",
    "bad_pattern": "bad pattern 23 in matrix 13: writer drift toward family 2, generated path reports_real/segment_13_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_13_23, boundary=bnd_matrix_13_23, switch=sw_matrix_13_23, hash_hint=960715d0cfe3704a"
  },
  {
    "matrix_row_id": "matrix_013_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 13: validator observes canonical read-only evidence and compares 5 registries against policy segment 13.",
    "bad_pattern": "bad pattern 24 in matrix 13: writer drift toward family 3, generated path reports_real/segment_13_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_13_24, boundary=bnd_matrix_13_24, switch=sw_matrix_13_24, hash_hint=df143e535ab05c3d"
  },
  {
    "matrix_row_id": "matrix_013_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 13: validator observes canonical read-only evidence and compares 1 registries against policy segment 13.",
    "bad_pattern": "bad pattern 25 in matrix 13: writer drift toward family 4, generated path reports_real/segment_13_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_13_25, boundary=bnd_matrix_13_25, switch=sw_matrix_13_25, hash_hint=e1ec1133db44c505"
  },
  {
    "matrix_row_id": "matrix_013_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 13: validator observes canonical read-only evidence and compares 2 registries against policy segment 13.",
    "bad_pattern": "bad pattern 26 in matrix 13: writer drift toward family 5, generated path reports_real/segment_13_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_13_26, boundary=bnd_matrix_13_26, switch=sw_matrix_13_26, hash_hint=8f793b52ec140c1d"
  },
  {
    "matrix_row_id": "matrix_013_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 13: validator observes canonical read-only evidence and compares 3 registries against policy segment 13.",
    "bad_pattern": "bad pattern 27 in matrix 13: writer drift toward family 6, generated path reports_real/segment_13_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_13_27, boundary=bnd_matrix_13_27, switch=sw_matrix_13_27, hash_hint=8d7a682c512a7f45"
  },
  {
    "matrix_row_id": "matrix_013_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 13: validator observes canonical read-only evidence and compares 4 registries against policy segment 13.",
    "bad_pattern": "bad pattern 28 in matrix 13: writer drift toward family 0, generated path reports_real/segment_13_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_13_28, boundary=bnd_matrix_13_28, switch=sw_matrix_13_28, hash_hint=114b046478efb9b7"
  },
  {
    "matrix_row_id": "matrix_013_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 13: validator observes canonical read-only evidence and compares 5 registries against policy segment 13.",
    "bad_pattern": "bad pattern 29 in matrix 13: writer drift toward family 1, generated path reports_real/segment_13_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_13_29, boundary=bnd_matrix_13_29, switch=sw_matrix_13_29, hash_hint=cfda0aca0652bfa7"
  },
  {
    "matrix_row_id": "matrix_013_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 13: validator observes canonical read-only evidence and compares 1 registries against policy segment 13.",
    "bad_pattern": "bad pattern 30 in matrix 13: writer drift toward family 2, generated path reports_real/segment_13_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_13_30, boundary=bnd_matrix_13_30, switch=sw_matrix_13_30, hash_hint=60b1793ab1950540"
  },
  {
    "matrix_row_id": "matrix_013_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 13: validator observes canonical read-only evidence and compares 2 registries against policy segment 13.",
    "bad_pattern": "bad pattern 31 in matrix 13: writer drift toward family 3, generated path reports_real/segment_13_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_13_31, boundary=bnd_matrix_13_31, switch=sw_matrix_13_31, hash_hint=79956cc610a37872"
  },
  {
    "matrix_row_id": "matrix_013_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 13: validator observes canonical read-only evidence and compares 3 registries against policy segment 13.",
    "bad_pattern": "bad pattern 32 in matrix 13: writer drift toward family 4, generated path reports_real/segment_13_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_13_32, boundary=bnd_matrix_13_32, switch=sw_matrix_13_32, hash_hint=7e3702db9c355709"
  },
  {
    "matrix_row_id": "matrix_013_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 13: validator observes canonical read-only evidence and compares 4 registries against policy segment 13.",
    "bad_pattern": "bad pattern 33 in matrix 13: writer drift toward family 5, generated path reports_real/segment_13_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_13_33, boundary=bnd_matrix_13_33, switch=sw_matrix_13_33, hash_hint=1da47bff0ff1365e"
  },
  {
    "matrix_row_id": "matrix_013_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 13: validator observes canonical read-only evidence and compares 5 registries against policy segment 13.",
    "bad_pattern": "bad pattern 34 in matrix 13: writer drift toward family 6, generated path reports_real/segment_13_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_13_34, boundary=bnd_matrix_13_34, switch=sw_matrix_13_34, hash_hint=956752fbd9ae7edd"
  },
  {
    "matrix_row_id": "matrix_013_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 13: validator observes canonical read-only evidence and compares 1 registries against policy segment 13.",
    "bad_pattern": "bad pattern 35 in matrix 13: writer drift toward family 0, generated path reports_real/segment_13_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_13_35, boundary=bnd_matrix_13_35, switch=sw_matrix_13_35, hash_hint=aa3425160eb6fdee"
  },
  {
    "matrix_row_id": "matrix_013_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 13: validator observes canonical read-only evidence and compares 2 registries against policy segment 13.",
    "bad_pattern": "bad pattern 36 in matrix 13: writer drift toward family 1, generated path reports_real/segment_13_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_13_36, boundary=bnd_matrix_13_36, switch=sw_matrix_13_36, hash_hint=5f7d6cee4f3aa9e7"
  },
  {
    "matrix_row_id": "matrix_013_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 13: validator observes canonical read-only evidence and compares 3 registries against policy segment 13.",
    "bad_pattern": "bad pattern 37 in matrix 13: writer drift toward family 2, generated path reports_real/segment_13_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_13_37, boundary=bnd_matrix_13_37, switch=sw_matrix_13_37, hash_hint=e83d62e16188c55d"
  },
  {
    "matrix_row_id": "matrix_013_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 13: validator observes canonical read-only evidence and compares 4 registries against policy segment 13.",
    "bad_pattern": "bad pattern 38 in matrix 13: writer drift toward family 3, generated path reports_real/segment_13_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_13_38, boundary=bnd_matrix_13_38, switch=sw_matrix_13_38, hash_hint=2bb30b0eb2b71e81"
  },
  {
    "matrix_row_id": "matrix_013_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 13: validator observes canonical read-only evidence and compares 5 registries against policy segment 13.",
    "bad_pattern": "bad pattern 39 in matrix 13: writer drift toward family 4, generated path reports_real/segment_13_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_13_39, boundary=bnd_matrix_13_39, switch=sw_matrix_13_39, hash_hint=f0ff0714e2d44e8f"
  },
  {
    "matrix_row_id": "matrix_013_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 13: validator observes canonical read-only evidence and compares 1 registries against policy segment 13.",
    "bad_pattern": "bad pattern 40 in matrix 13: writer drift toward family 5, generated path reports_real/segment_13_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_13_40, boundary=bnd_matrix_13_40, switch=sw_matrix_13_40, hash_hint=36bd721280129e19"
  },
  {
    "matrix_row_id": "matrix_013_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 13: validator observes canonical read-only evidence and compares 2 registries against policy segment 13.",
    "bad_pattern": "bad pattern 41 in matrix 13: writer drift toward family 6, generated path reports_real/segment_13_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_13_41, boundary=bnd_matrix_13_41, switch=sw_matrix_13_41, hash_hint=0ac5d029711f8a8a"
  },
  {
    "matrix_row_id": "matrix_013_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 13: validator observes canonical read-only evidence and compares 3 registries against policy segment 13.",
    "bad_pattern": "bad pattern 42 in matrix 13: writer drift toward family 0, generated path reports_real/segment_13_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_13_42, boundary=bnd_matrix_13_42, switch=sw_matrix_13_42, hash_hint=c675f91143eec386"
  },
  {
    "matrix_row_id": "matrix_013_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 13: validator observes canonical read-only evidence and compares 4 registries against policy segment 13.",
    "bad_pattern": "bad pattern 43 in matrix 13: writer drift toward family 1, generated path reports_real/segment_13_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_13_43, boundary=bnd_matrix_13_43, switch=sw_matrix_13_43, hash_hint=0ef3e15088595560"
  },
  {
    "matrix_row_id": "matrix_013_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 13: validator observes canonical read-only evidence and compares 5 registries against policy segment 13.",
    "bad_pattern": "bad pattern 44 in matrix 13: writer drift toward family 2, generated path reports_real/segment_13_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_13_44, boundary=bnd_matrix_13_44, switch=sw_matrix_13_44, hash_hint=7591fe1ae322095d"
  },
  {
    "matrix_row_id": "matrix_013_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 13: validator observes canonical read-only evidence and compares 1 registries against policy segment 13.",
    "bad_pattern": "bad pattern 45 in matrix 13: writer drift toward family 3, generated path reports_real/segment_13_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_13_45, boundary=bnd_matrix_13_45, switch=sw_matrix_13_45, hash_hint=50bd78a7ce44721e"
  },
  {
    "matrix_row_id": "matrix_013_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 13: validator observes canonical read-only evidence and compares 2 registries against policy segment 13.",
    "bad_pattern": "bad pattern 46 in matrix 13: writer drift toward family 4, generated path reports_real/segment_13_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_13_46, boundary=bnd_matrix_13_46, switch=sw_matrix_13_46, hash_hint=66411a4a9edb1194"
  },
  {
    "matrix_row_id": "matrix_013_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 13: validator observes canonical read-only evidence and compares 3 registries against policy segment 13.",
    "bad_pattern": "bad pattern 47 in matrix 13: writer drift toward family 5, generated path reports_real/segment_13_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_13_47, boundary=bnd_matrix_13_47, switch=sw_matrix_13_47, hash_hint=b3edc93bf764b57f"
  },
  {
    "matrix_row_id": "matrix_013_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 13: validator observes canonical read-only evidence and compares 4 registries against policy segment 13.",
    "bad_pattern": "bad pattern 48 in matrix 13: writer drift toward family 6, generated path reports_real/segment_13_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_13_48, boundary=bnd_matrix_13_48, switch=sw_matrix_13_48, hash_hint=0a6862bd7ac0634f"
  },
  {
    "matrix_row_id": "matrix_013_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 13: validator observes canonical read-only evidence and compares 5 registries against policy segment 13.",
    "bad_pattern": "bad pattern 49 in matrix 13: writer drift toward family 0, generated path reports_real/segment_13_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_13_49, boundary=bnd_matrix_13_49, switch=sw_matrix_13_49, hash_hint=0f843d4665bd782e"
  },
  {
    "matrix_row_id": "matrix_013_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 13: validator observes canonical read-only evidence and compares 1 registries against policy segment 13.",
    "bad_pattern": "bad pattern 50 in matrix 13: writer drift toward family 1, generated path reports_real/segment_13_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_13_50, boundary=bnd_matrix_13_50, switch=sw_matrix_13_50, hash_hint=06dd7a1fcde2c3a7"
  },
  {
    "matrix_row_id": "matrix_013_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 13: validator observes canonical read-only evidence and compares 2 registries against policy segment 13.",
    "bad_pattern": "bad pattern 51 in matrix 13: writer drift toward family 2, generated path reports_real/segment_13_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_13_51, boundary=bnd_matrix_13_51, switch=sw_matrix_13_51, hash_hint=57113c34dff0a38c"
  },
  {
    "matrix_row_id": "matrix_013_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 13: validator observes canonical read-only evidence and compares 3 registries against policy segment 13.",
    "bad_pattern": "bad pattern 52 in matrix 13: writer drift toward family 3, generated path reports_real/segment_13_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_13_52, boundary=bnd_matrix_13_52, switch=sw_matrix_13_52, hash_hint=c385567e9baf2e20"
  },
  {
    "matrix_row_id": "matrix_013_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 13: validator observes canonical read-only evidence and compares 4 registries against policy segment 13.",
    "bad_pattern": "bad pattern 53 in matrix 13: writer drift toward family 4, generated path reports_real/segment_13_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_13_53, boundary=bnd_matrix_13_53, switch=sw_matrix_13_53, hash_hint=4f78cffc18039508"
  },
  {
    "matrix_row_id": "matrix_013_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 13: validator observes canonical read-only evidence and compares 5 registries against policy segment 13.",
    "bad_pattern": "bad pattern 54 in matrix 13: writer drift toward family 5, generated path reports_real/segment_13_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_13_54, boundary=bnd_matrix_13_54, switch=sw_matrix_13_54, hash_hint=786b4c51da410777"
  },
  {
    "matrix_row_id": "matrix_013_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 13: validator observes canonical read-only evidence and compares 1 registries against policy segment 13.",
    "bad_pattern": "bad pattern 55 in matrix 13: writer drift toward family 6, generated path reports_real/segment_13_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_13_55, boundary=bnd_matrix_13_55, switch=sw_matrix_13_55, hash_hint=01bfcc218fbb460e"
  },
  {
    "matrix_row_id": "matrix_013_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 13: validator observes canonical read-only evidence and compares 2 registries against policy segment 13.",
    "bad_pattern": "bad pattern 56 in matrix 13: writer drift toward family 0, generated path reports_real/segment_13_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_13_56, boundary=bnd_matrix_13_56, switch=sw_matrix_13_56, hash_hint=21152f70a4fdd259"
  },
  {
    "matrix_row_id": "matrix_013_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 13: validator observes canonical read-only evidence and compares 3 registries against policy segment 13.",
    "bad_pattern": "bad pattern 57 in matrix 13: writer drift toward family 1, generated path reports_real/segment_13_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_13_57, boundary=bnd_matrix_13_57, switch=sw_matrix_13_57, hash_hint=4281de2d623ba2f5"
  },
  {
    "matrix_row_id": "matrix_013_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 13: validator observes canonical read-only evidence and compares 4 registries against policy segment 13.",
    "bad_pattern": "bad pattern 58 in matrix 13: writer drift toward family 2, generated path reports_real/segment_13_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_13_58, boundary=bnd_matrix_13_58, switch=sw_matrix_13_58, hash_hint=94084223ae7beb49"
  },
  {
    "matrix_row_id": "matrix_013_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 13: validator observes canonical read-only evidence and compares 5 registries against policy segment 13.",
    "bad_pattern": "bad pattern 59 in matrix 13: writer drift toward family 3, generated path reports_real/segment_13_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_13_59, boundary=bnd_matrix_13_59, switch=sw_matrix_13_59, hash_hint=e0c6ca193823a0b1"
  },
  {
    "matrix_row_id": "matrix_013_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 13: validator observes canonical read-only evidence and compares 1 registries against policy segment 13.",
    "bad_pattern": "bad pattern 60 in matrix 13: writer drift toward family 4, generated path reports_real/segment_13_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_13_60, boundary=bnd_matrix_13_60, switch=sw_matrix_13_60, hash_hint=1abf2755d9289b47"
  }
]
