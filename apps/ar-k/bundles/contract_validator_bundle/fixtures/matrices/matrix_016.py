from __future__ import annotations

"""Meaningful decision matrix corpus for homologation evidence.

- matrix note 1: validator row pack 16/1 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 2: validator row pack 16/2 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 3: validator row pack 16/3 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 4: validator row pack 16/4 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 5: validator row pack 16/5 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 6: validator row pack 16/6 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 7: validator row pack 16/7 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 8: validator row pack 16/8 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 9: validator row pack 16/9 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 10: validator row pack 16/10 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 11: validator row pack 16/11 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 12: validator row pack 16/12 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 13: validator row pack 16/13 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 14: validator row pack 16/14 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 15: validator row pack 16/15 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 16: validator row pack 16/16 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 17: validator row pack 16/17 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 18: validator row pack 16/18 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 19: validator row pack 16/19 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 20: validator row pack 16/20 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 21: validator row pack 16/21 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 22: validator row pack 16/22 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 23: validator row pack 16/23 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 24: validator row pack 16/24 stresses handoff economics, canon alignment, and executable gate semantics.
- matrix note 25: validator row pack 16/25 stresses handoff economics, canon alignment, and executable gate semantics.
"""

MATRIX = [
  {
    "matrix_row_id": "matrix_016_row_001",
    "gate_family": "ownership",
    "precondition": "precondition 1 for matrix 16: validator observes canonical read-only evidence and compares 2 registries against policy segment 16.",
    "bad_pattern": "bad pattern 1 in matrix 16: writer drift toward family 1, generated path reports_real/segment_16_1, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 1: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 1: module=mod_matrix_16_1, boundary=bnd_matrix_16_1, switch=sw_matrix_16_1, hash_hint=f3a2577b1df83f1c"
  },
  {
    "matrix_row_id": "matrix_016_row_002",
    "gate_family": "artifact_naming",
    "precondition": "precondition 2 for matrix 16: validator observes canonical read-only evidence and compares 3 registries against policy segment 16.",
    "bad_pattern": "bad pattern 2 in matrix 16: writer drift toward family 2, generated path reports_real/segment_16_2, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 2: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 2: module=mod_matrix_16_2, boundary=bnd_matrix_16_2, switch=sw_matrix_16_2, hash_hint=7a0bd3847526d7b9"
  },
  {
    "matrix_row_id": "matrix_016_row_003",
    "gate_family": "exclusions",
    "precondition": "precondition 3 for matrix 16: validator observes canonical read-only evidence and compares 4 registries against policy segment 16.",
    "bad_pattern": "bad pattern 3 in matrix 16: writer drift toward family 3, generated path reports_real/segment_16_3, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 3: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 3: module=mod_matrix_16_3, boundary=bnd_matrix_16_3, switch=sw_matrix_16_3, hash_hint=3d4109bcd77813a9"
  },
  {
    "matrix_row_id": "matrix_016_row_004",
    "gate_family": "write_limits",
    "precondition": "precondition 4 for matrix 16: validator observes canonical read-only evidence and compares 5 registries against policy segment 16.",
    "bad_pattern": "bad pattern 4 in matrix 16: writer drift toward family 4, generated path reports_real/segment_16_4, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 4: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 4: module=mod_matrix_16_4, boundary=bnd_matrix_16_4, switch=sw_matrix_16_4, hash_hint=0f93aee6cd0da6c0"
  },
  {
    "matrix_row_id": "matrix_016_row_005",
    "gate_family": "promotion_policy",
    "precondition": "precondition 5 for matrix 16: validator observes canonical read-only evidence and compares 1 registries against policy segment 16.",
    "bad_pattern": "bad pattern 5 in matrix 16: writer drift toward family 5, generated path reports_real/segment_16_5, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 5: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 5: module=mod_matrix_16_5, boundary=bnd_matrix_16_5, switch=sw_matrix_16_5, hash_hint=c6274541fabf5004"
  },
  {
    "matrix_row_id": "matrix_016_row_006",
    "gate_family": "cross_reference",
    "precondition": "precondition 6 for matrix 16: validator observes canonical read-only evidence and compares 2 registries against policy segment 16.",
    "bad_pattern": "bad pattern 6 in matrix 16: writer drift toward family 6, generated path reports_real/segment_16_6, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 6: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 6: module=mod_matrix_16_6, boundary=bnd_matrix_16_6, switch=sw_matrix_16_6, hash_hint=3724974c571f04e4"
  },
  {
    "matrix_row_id": "matrix_016_row_007",
    "gate_family": "done_criteria",
    "precondition": "precondition 7 for matrix 16: validator observes canonical read-only evidence and compares 3 registries against policy segment 16.",
    "bad_pattern": "bad pattern 7 in matrix 16: writer drift toward family 0, generated path reports_real/segment_16_7, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 7: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 7: module=mod_matrix_16_7, boundary=bnd_matrix_16_7, switch=sw_matrix_16_7, hash_hint=ca20006bc2e338c1"
  },
  {
    "matrix_row_id": "matrix_016_row_008",
    "gate_family": "stage_order",
    "precondition": "precondition 8 for matrix 16: validator observes canonical read-only evidence and compares 4 registries against policy segment 16.",
    "bad_pattern": "bad pattern 8 in matrix 16: writer drift toward family 1, generated path reports_real/segment_16_8, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 8: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 8: module=mod_matrix_16_8, boundary=bnd_matrix_16_8, switch=sw_matrix_16_8, hash_hint=d299aa70e4119d0d"
  },
  {
    "matrix_row_id": "matrix_016_row_009",
    "gate_family": "ownership",
    "precondition": "precondition 9 for matrix 16: validator observes canonical read-only evidence and compares 5 registries against policy segment 16.",
    "bad_pattern": "bad pattern 9 in matrix 16: writer drift toward family 2, generated path reports_real/segment_16_9, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 9: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 9: module=mod_matrix_16_9, boundary=bnd_matrix_16_9, switch=sw_matrix_16_9, hash_hint=afebba469ddd567c"
  },
  {
    "matrix_row_id": "matrix_016_row_010",
    "gate_family": "artifact_naming",
    "precondition": "precondition 10 for matrix 16: validator observes canonical read-only evidence and compares 1 registries against policy segment 16.",
    "bad_pattern": "bad pattern 10 in matrix 16: writer drift toward family 3, generated path reports_real/segment_16_10, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 10: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 10: module=mod_matrix_16_10, boundary=bnd_matrix_16_10, switch=sw_matrix_16_10, hash_hint=1036110736cda2b7"
  },
  {
    "matrix_row_id": "matrix_016_row_011",
    "gate_family": "exclusions",
    "precondition": "precondition 11 for matrix 16: validator observes canonical read-only evidence and compares 2 registries against policy segment 16.",
    "bad_pattern": "bad pattern 11 in matrix 16: writer drift toward family 4, generated path reports_real/segment_16_11, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 11: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 11: module=mod_matrix_16_11, boundary=bnd_matrix_16_11, switch=sw_matrix_16_11, hash_hint=637daee2722b9ea2"
  },
  {
    "matrix_row_id": "matrix_016_row_012",
    "gate_family": "write_limits",
    "precondition": "precondition 12 for matrix 16: validator observes canonical read-only evidence and compares 3 registries against policy segment 16.",
    "bad_pattern": "bad pattern 12 in matrix 16: writer drift toward family 5, generated path reports_real/segment_16_12, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 12: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 12: module=mod_matrix_16_12, boundary=bnd_matrix_16_12, switch=sw_matrix_16_12, hash_hint=6ab76f2412f45951"
  },
  {
    "matrix_row_id": "matrix_016_row_013",
    "gate_family": "promotion_policy",
    "precondition": "precondition 13 for matrix 16: validator observes canonical read-only evidence and compares 4 registries against policy segment 16.",
    "bad_pattern": "bad pattern 13 in matrix 16: writer drift toward family 6, generated path reports_real/segment_16_13, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 13: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 13: module=mod_matrix_16_13, boundary=bnd_matrix_16_13, switch=sw_matrix_16_13, hash_hint=e313ea3e8db6a112"
  },
  {
    "matrix_row_id": "matrix_016_row_014",
    "gate_family": "cross_reference",
    "precondition": "precondition 14 for matrix 16: validator observes canonical read-only evidence and compares 5 registries against policy segment 16.",
    "bad_pattern": "bad pattern 14 in matrix 16: writer drift toward family 0, generated path reports_real/segment_16_14, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 14: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 14: module=mod_matrix_16_14, boundary=bnd_matrix_16_14, switch=sw_matrix_16_14, hash_hint=fb3e02849e06ea2b"
  },
  {
    "matrix_row_id": "matrix_016_row_015",
    "gate_family": "done_criteria",
    "precondition": "precondition 15 for matrix 16: validator observes canonical read-only evidence and compares 1 registries against policy segment 16.",
    "bad_pattern": "bad pattern 15 in matrix 16: writer drift toward family 1, generated path reports_real/segment_16_15, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 15: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 15: module=mod_matrix_16_15, boundary=bnd_matrix_16_15, switch=sw_matrix_16_15, hash_hint=191e16537dbace61"
  },
  {
    "matrix_row_id": "matrix_016_row_016",
    "gate_family": "stage_order",
    "precondition": "precondition 16 for matrix 16: validator observes canonical read-only evidence and compares 2 registries against policy segment 16.",
    "bad_pattern": "bad pattern 16 in matrix 16: writer drift toward family 2, generated path reports_real/segment_16_16, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 16: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 16: module=mod_matrix_16_16, boundary=bnd_matrix_16_16, switch=sw_matrix_16_16, hash_hint=309252eba4747b9f"
  },
  {
    "matrix_row_id": "matrix_016_row_017",
    "gate_family": "ownership",
    "precondition": "precondition 17 for matrix 16: validator observes canonical read-only evidence and compares 3 registries against policy segment 16.",
    "bad_pattern": "bad pattern 17 in matrix 16: writer drift toward family 3, generated path reports_real/segment_16_17, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 17: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 17: module=mod_matrix_16_17, boundary=bnd_matrix_16_17, switch=sw_matrix_16_17, hash_hint=15e52135b564d5c7"
  },
  {
    "matrix_row_id": "matrix_016_row_018",
    "gate_family": "artifact_naming",
    "precondition": "precondition 18 for matrix 16: validator observes canonical read-only evidence and compares 4 registries against policy segment 16.",
    "bad_pattern": "bad pattern 18 in matrix 16: writer drift toward family 4, generated path reports_real/segment_16_18, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 18: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 18: module=mod_matrix_16_18, boundary=bnd_matrix_16_18, switch=sw_matrix_16_18, hash_hint=d222ca8d6e0dbd31"
  },
  {
    "matrix_row_id": "matrix_016_row_019",
    "gate_family": "exclusions",
    "precondition": "precondition 19 for matrix 16: validator observes canonical read-only evidence and compares 5 registries against policy segment 16.",
    "bad_pattern": "bad pattern 19 in matrix 16: writer drift toward family 5, generated path reports_real/segment_16_19, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 19: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 19: module=mod_matrix_16_19, boundary=bnd_matrix_16_19, switch=sw_matrix_16_19, hash_hint=a1678784c91abfc4"
  },
  {
    "matrix_row_id": "matrix_016_row_020",
    "gate_family": "write_limits",
    "precondition": "precondition 20 for matrix 16: validator observes canonical read-only evidence and compares 1 registries against policy segment 16.",
    "bad_pattern": "bad pattern 20 in matrix 16: writer drift toward family 6, generated path reports_real/segment_16_20, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 20: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 20: module=mod_matrix_16_20, boundary=bnd_matrix_16_20, switch=sw_matrix_16_20, hash_hint=5cd1bd3e874e9261"
  },
  {
    "matrix_row_id": "matrix_016_row_021",
    "gate_family": "promotion_policy",
    "precondition": "precondition 21 for matrix 16: validator observes canonical read-only evidence and compares 2 registries against policy segment 16.",
    "bad_pattern": "bad pattern 21 in matrix 16: writer drift toward family 0, generated path reports_real/segment_16_21, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 21: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 21: module=mod_matrix_16_21, boundary=bnd_matrix_16_21, switch=sw_matrix_16_21, hash_hint=64fb6886f7909647"
  },
  {
    "matrix_row_id": "matrix_016_row_022",
    "gate_family": "cross_reference",
    "precondition": "precondition 22 for matrix 16: validator observes canonical read-only evidence and compares 3 registries against policy segment 16.",
    "bad_pattern": "bad pattern 22 in matrix 16: writer drift toward family 1, generated path reports_real/segment_16_22, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 22: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 22: module=mod_matrix_16_22, boundary=bnd_matrix_16_22, switch=sw_matrix_16_22, hash_hint=3ede10ccc13e16c1"
  },
  {
    "matrix_row_id": "matrix_016_row_023",
    "gate_family": "done_criteria",
    "precondition": "precondition 23 for matrix 16: validator observes canonical read-only evidence and compares 4 registries against policy segment 16.",
    "bad_pattern": "bad pattern 23 in matrix 16: writer drift toward family 2, generated path reports_real/segment_16_23, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 23: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 23: module=mod_matrix_16_23, boundary=bnd_matrix_16_23, switch=sw_matrix_16_23, hash_hint=c5934688324fed2f"
  },
  {
    "matrix_row_id": "matrix_016_row_024",
    "gate_family": "stage_order",
    "precondition": "precondition 24 for matrix 16: validator observes canonical read-only evidence and compares 5 registries against policy segment 16.",
    "bad_pattern": "bad pattern 24 in matrix 16: writer drift toward family 3, generated path reports_real/segment_16_24, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 24: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 24: module=mod_matrix_16_24, boundary=bnd_matrix_16_24, switch=sw_matrix_16_24, hash_hint=9a607bbcc71bb6fd"
  },
  {
    "matrix_row_id": "matrix_016_row_025",
    "gate_family": "ownership",
    "precondition": "precondition 25 for matrix 16: validator observes canonical read-only evidence and compares 1 registries against policy segment 16.",
    "bad_pattern": "bad pattern 25 in matrix 16: writer drift toward family 4, generated path reports_real/segment_16_25, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 25: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 25: module=mod_matrix_16_25, boundary=bnd_matrix_16_25, switch=sw_matrix_16_25, hash_hint=cb19164c16e512f0"
  },
  {
    "matrix_row_id": "matrix_016_row_026",
    "gate_family": "artifact_naming",
    "precondition": "precondition 26 for matrix 16: validator observes canonical read-only evidence and compares 2 registries against policy segment 16.",
    "bad_pattern": "bad pattern 26 in matrix 16: writer drift toward family 5, generated path reports_real/segment_16_26, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 26: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 26: module=mod_matrix_16_26, boundary=bnd_matrix_16_26, switch=sw_matrix_16_26, hash_hint=bcf15cc76f2e7739"
  },
  {
    "matrix_row_id": "matrix_016_row_027",
    "gate_family": "exclusions",
    "precondition": "precondition 27 for matrix 16: validator observes canonical read-only evidence and compares 3 registries against policy segment 16.",
    "bad_pattern": "bad pattern 27 in matrix 16: writer drift toward family 6, generated path reports_real/segment_16_27, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 27: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 27: module=mod_matrix_16_27, boundary=bnd_matrix_16_27, switch=sw_matrix_16_27, hash_hint=1e8383c5ba6e0e29"
  },
  {
    "matrix_row_id": "matrix_016_row_028",
    "gate_family": "write_limits",
    "precondition": "precondition 28 for matrix 16: validator observes canonical read-only evidence and compares 4 registries against policy segment 16.",
    "bad_pattern": "bad pattern 28 in matrix 16: writer drift toward family 0, generated path reports_real/segment_16_28, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 28: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 28: module=mod_matrix_16_28, boundary=bnd_matrix_16_28, switch=sw_matrix_16_28, hash_hint=e5cb1042c3d8fbfe"
  },
  {
    "matrix_row_id": "matrix_016_row_029",
    "gate_family": "promotion_policy",
    "precondition": "precondition 29 for matrix 16: validator observes canonical read-only evidence and compares 5 registries against policy segment 16.",
    "bad_pattern": "bad pattern 29 in matrix 16: writer drift toward family 1, generated path reports_real/segment_16_29, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 29: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 29: module=mod_matrix_16_29, boundary=bnd_matrix_16_29, switch=sw_matrix_16_29, hash_hint=6e4130698ff2b080"
  },
  {
    "matrix_row_id": "matrix_016_row_030",
    "gate_family": "cross_reference",
    "precondition": "precondition 30 for matrix 16: validator observes canonical read-only evidence and compares 1 registries against policy segment 16.",
    "bad_pattern": "bad pattern 30 in matrix 16: writer drift toward family 2, generated path reports_real/segment_16_30, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 30: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 30: module=mod_matrix_16_30, boundary=bnd_matrix_16_30, switch=sw_matrix_16_30, hash_hint=be1b16673da2b77f"
  },
  {
    "matrix_row_id": "matrix_016_row_031",
    "gate_family": "done_criteria",
    "precondition": "precondition 31 for matrix 16: validator observes canonical read-only evidence and compares 2 registries against policy segment 16.",
    "bad_pattern": "bad pattern 31 in matrix 16: writer drift toward family 3, generated path reports_real/segment_16_31, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 31: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 31: module=mod_matrix_16_31, boundary=bnd_matrix_16_31, switch=sw_matrix_16_31, hash_hint=c09d1ca46761f31d"
  },
  {
    "matrix_row_id": "matrix_016_row_032",
    "gate_family": "stage_order",
    "precondition": "precondition 32 for matrix 16: validator observes canonical read-only evidence and compares 3 registries against policy segment 16.",
    "bad_pattern": "bad pattern 32 in matrix 16: writer drift toward family 4, generated path reports_real/segment_16_32, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 32: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 32: module=mod_matrix_16_32, boundary=bnd_matrix_16_32, switch=sw_matrix_16_32, hash_hint=6e152e310508feef"
  },
  {
    "matrix_row_id": "matrix_016_row_033",
    "gate_family": "ownership",
    "precondition": "precondition 33 for matrix 16: validator observes canonical read-only evidence and compares 4 registries against policy segment 16.",
    "bad_pattern": "bad pattern 33 in matrix 16: writer drift toward family 5, generated path reports_real/segment_16_33, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 33: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 33: module=mod_matrix_16_33, boundary=bnd_matrix_16_33, switch=sw_matrix_16_33, hash_hint=0b6624b36dd8fea9"
  },
  {
    "matrix_row_id": "matrix_016_row_034",
    "gate_family": "artifact_naming",
    "precondition": "precondition 34 for matrix 16: validator observes canonical read-only evidence and compares 5 registries against policy segment 16.",
    "bad_pattern": "bad pattern 34 in matrix 16: writer drift toward family 6, generated path reports_real/segment_16_34, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 34: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 34: module=mod_matrix_16_34, boundary=bnd_matrix_16_34, switch=sw_matrix_16_34, hash_hint=51b9b801c8b5be6e"
  },
  {
    "matrix_row_id": "matrix_016_row_035",
    "gate_family": "exclusions",
    "precondition": "precondition 35 for matrix 16: validator observes canonical read-only evidence and compares 1 registries against policy segment 16.",
    "bad_pattern": "bad pattern 35 in matrix 16: writer drift toward family 0, generated path reports_real/segment_16_35, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 35: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 35: module=mod_matrix_16_35, boundary=bnd_matrix_16_35, switch=sw_matrix_16_35, hash_hint=ef114a0bee3c1f4e"
  },
  {
    "matrix_row_id": "matrix_016_row_036",
    "gate_family": "write_limits",
    "precondition": "precondition 36 for matrix 16: validator observes canonical read-only evidence and compares 2 registries against policy segment 16.",
    "bad_pattern": "bad pattern 36 in matrix 16: writer drift toward family 1, generated path reports_real/segment_16_36, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 36: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 36: module=mod_matrix_16_36, boundary=bnd_matrix_16_36, switch=sw_matrix_16_36, hash_hint=6807b0871cd2f9d5"
  },
  {
    "matrix_row_id": "matrix_016_row_037",
    "gate_family": "promotion_policy",
    "precondition": "precondition 37 for matrix 16: validator observes canonical read-only evidence and compares 3 registries against policy segment 16.",
    "bad_pattern": "bad pattern 37 in matrix 16: writer drift toward family 2, generated path reports_real/segment_16_37, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 37: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 37: module=mod_matrix_16_37, boundary=bnd_matrix_16_37, switch=sw_matrix_16_37, hash_hint=8b263f218474e062"
  },
  {
    "matrix_row_id": "matrix_016_row_038",
    "gate_family": "cross_reference",
    "precondition": "precondition 38 for matrix 16: validator observes canonical read-only evidence and compares 4 registries against policy segment 16.",
    "bad_pattern": "bad pattern 38 in matrix 16: writer drift toward family 3, generated path reports_real/segment_16_38, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 38: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 38: module=mod_matrix_16_38, boundary=bnd_matrix_16_38, switch=sw_matrix_16_38, hash_hint=45c262c4a2c390eb"
  },
  {
    "matrix_row_id": "matrix_016_row_039",
    "gate_family": "done_criteria",
    "precondition": "precondition 39 for matrix 16: validator observes canonical read-only evidence and compares 5 registries against policy segment 16.",
    "bad_pattern": "bad pattern 39 in matrix 16: writer drift toward family 4, generated path reports_real/segment_16_39, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 39: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 39: module=mod_matrix_16_39, boundary=bnd_matrix_16_39, switch=sw_matrix_16_39, hash_hint=690c37aa1715659d"
  },
  {
    "matrix_row_id": "matrix_016_row_040",
    "gate_family": "stage_order",
    "precondition": "precondition 40 for matrix 16: validator observes canonical read-only evidence and compares 1 registries against policy segment 16.",
    "bad_pattern": "bad pattern 40 in matrix 16: writer drift toward family 5, generated path reports_real/segment_16_40, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 40: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 40: module=mod_matrix_16_40, boundary=bnd_matrix_16_40, switch=sw_matrix_16_40, hash_hint=4e6b185ae0375ef6"
  },
  {
    "matrix_row_id": "matrix_016_row_041",
    "gate_family": "ownership",
    "precondition": "precondition 41 for matrix 16: validator observes canonical read-only evidence and compares 2 registries against policy segment 16.",
    "bad_pattern": "bad pattern 41 in matrix 16: writer drift toward family 6, generated path reports_real/segment_16_41, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 41: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 41: module=mod_matrix_16_41, boundary=bnd_matrix_16_41, switch=sw_matrix_16_41, hash_hint=460d7265d4e5c2f6"
  },
  {
    "matrix_row_id": "matrix_016_row_042",
    "gate_family": "artifact_naming",
    "precondition": "precondition 42 for matrix 16: validator observes canonical read-only evidence and compares 3 registries against policy segment 16.",
    "bad_pattern": "bad pattern 42 in matrix 16: writer drift toward family 0, generated path reports_real/segment_16_42, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 42: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 42: module=mod_matrix_16_42, boundary=bnd_matrix_16_42, switch=sw_matrix_16_42, hash_hint=0bce9b75a2d21399"
  },
  {
    "matrix_row_id": "matrix_016_row_043",
    "gate_family": "exclusions",
    "precondition": "precondition 43 for matrix 16: validator observes canonical read-only evidence and compares 4 registries against policy segment 16.",
    "bad_pattern": "bad pattern 43 in matrix 16: writer drift toward family 1, generated path reports_real/segment_16_43, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 43: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 43: module=mod_matrix_16_43, boundary=bnd_matrix_16_43, switch=sw_matrix_16_43, hash_hint=188faeffafb2c9a8"
  },
  {
    "matrix_row_id": "matrix_016_row_044",
    "gate_family": "write_limits",
    "precondition": "precondition 44 for matrix 16: validator observes canonical read-only evidence and compares 5 registries against policy segment 16.",
    "bad_pattern": "bad pattern 44 in matrix 16: writer drift toward family 2, generated path reports_real/segment_16_44, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 44: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 44: module=mod_matrix_16_44, boundary=bnd_matrix_16_44, switch=sw_matrix_16_44, hash_hint=e16276ba68096b4b"
  },
  {
    "matrix_row_id": "matrix_016_row_045",
    "gate_family": "promotion_policy",
    "precondition": "precondition 45 for matrix 16: validator observes canonical read-only evidence and compares 1 registries against policy segment 16.",
    "bad_pattern": "bad pattern 45 in matrix 16: writer drift toward family 3, generated path reports_real/segment_16_45, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 45: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 45: module=mod_matrix_16_45, boundary=bnd_matrix_16_45, switch=sw_matrix_16_45, hash_hint=fec02b1e3874aa81"
  },
  {
    "matrix_row_id": "matrix_016_row_046",
    "gate_family": "cross_reference",
    "precondition": "precondition 46 for matrix 16: validator observes canonical read-only evidence and compares 2 registries against policy segment 16.",
    "bad_pattern": "bad pattern 46 in matrix 16: writer drift toward family 4, generated path reports_real/segment_16_46, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 46: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 46: module=mod_matrix_16_46, boundary=bnd_matrix_16_46, switch=sw_matrix_16_46, hash_hint=43eb5de8051c4f7f"
  },
  {
    "matrix_row_id": "matrix_016_row_047",
    "gate_family": "done_criteria",
    "precondition": "precondition 47 for matrix 16: validator observes canonical read-only evidence and compares 3 registries against policy segment 16.",
    "bad_pattern": "bad pattern 47 in matrix 16: writer drift toward family 5, generated path reports_real/segment_16_47, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 47: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 47: module=mod_matrix_16_47, boundary=bnd_matrix_16_47, switch=sw_matrix_16_47, hash_hint=db826a16f0021399"
  },
  {
    "matrix_row_id": "matrix_016_row_048",
    "gate_family": "stage_order",
    "precondition": "precondition 48 for matrix 16: validator observes canonical read-only evidence and compares 4 registries against policy segment 16.",
    "bad_pattern": "bad pattern 48 in matrix 16: writer drift toward family 6, generated path reports_real/segment_16_48, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 48: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 48: module=mod_matrix_16_48, boundary=bnd_matrix_16_48, switch=sw_matrix_16_48, hash_hint=922d13e0b40d70d0"
  },
  {
    "matrix_row_id": "matrix_016_row_049",
    "gate_family": "ownership",
    "precondition": "precondition 49 for matrix 16: validator observes canonical read-only evidence and compares 5 registries against policy segment 16.",
    "bad_pattern": "bad pattern 49 in matrix 16: writer drift toward family 0, generated path reports_real/segment_16_49, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 49: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 49: module=mod_matrix_16_49, boundary=bnd_matrix_16_49, switch=sw_matrix_16_49, hash_hint=d9433363637b8f6b"
  },
  {
    "matrix_row_id": "matrix_016_row_050",
    "gate_family": "artifact_naming",
    "precondition": "precondition 50 for matrix 16: validator observes canonical read-only evidence and compares 1 registries against policy segment 16.",
    "bad_pattern": "bad pattern 50 in matrix 16: writer drift toward family 1, generated path reports_real/segment_16_50, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 50: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 50: module=mod_matrix_16_50, boundary=bnd_matrix_16_50, switch=sw_matrix_16_50, hash_hint=c717520c6ff48761"
  },
  {
    "matrix_row_id": "matrix_016_row_051",
    "gate_family": "exclusions",
    "precondition": "precondition 51 for matrix 16: validator observes canonical read-only evidence and compares 2 registries against policy segment 16.",
    "bad_pattern": "bad pattern 51 in matrix 16: writer drift toward family 2, generated path reports_real/segment_16_51, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 51: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 51: module=mod_matrix_16_51, boundary=bnd_matrix_16_51, switch=sw_matrix_16_51, hash_hint=db8d331d1878088e"
  },
  {
    "matrix_row_id": "matrix_016_row_052",
    "gate_family": "write_limits",
    "precondition": "precondition 52 for matrix 16: validator observes canonical read-only evidence and compares 3 registries against policy segment 16.",
    "bad_pattern": "bad pattern 52 in matrix 16: writer drift toward family 3, generated path reports_real/segment_16_52, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 52: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 52: module=mod_matrix_16_52, boundary=bnd_matrix_16_52, switch=sw_matrix_16_52, hash_hint=5f3ef83d96f1a8be"
  },
  {
    "matrix_row_id": "matrix_016_row_053",
    "gate_family": "promotion_policy",
    "precondition": "precondition 53 for matrix 16: validator observes canonical read-only evidence and compares 4 registries against policy segment 16.",
    "bad_pattern": "bad pattern 53 in matrix 16: writer drift toward family 4, generated path reports_real/segment_16_53, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 53: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 53: module=mod_matrix_16_53, boundary=bnd_matrix_16_53, switch=sw_matrix_16_53, hash_hint=0d75c9f2ac80af26"
  },
  {
    "matrix_row_id": "matrix_016_row_054",
    "gate_family": "cross_reference",
    "precondition": "precondition 54 for matrix 16: validator observes canonical read-only evidence and compares 5 registries against policy segment 16.",
    "bad_pattern": "bad pattern 54 in matrix 16: writer drift toward family 5, generated path reports_real/segment_16_54, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 54: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 54: module=mod_matrix_16_54, boundary=bnd_matrix_16_54, switch=sw_matrix_16_54, hash_hint=0428c22b6bf1ff41"
  },
  {
    "matrix_row_id": "matrix_016_row_055",
    "gate_family": "done_criteria",
    "precondition": "precondition 55 for matrix 16: validator observes canonical read-only evidence and compares 1 registries against policy segment 16.",
    "bad_pattern": "bad pattern 55 in matrix 16: writer drift toward family 6, generated path reports_real/segment_16_55, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 55: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 55: module=mod_matrix_16_55, boundary=bnd_matrix_16_55, switch=sw_matrix_16_55, hash_hint=de3edc7770345255"
  },
  {
    "matrix_row_id": "matrix_016_row_056",
    "gate_family": "stage_order",
    "precondition": "precondition 56 for matrix 16: validator observes canonical read-only evidence and compares 2 registries against policy segment 16.",
    "bad_pattern": "bad pattern 56 in matrix 16: writer drift toward family 0, generated path reports_real/segment_16_56, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 56: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 56: module=mod_matrix_16_56, boundary=bnd_matrix_16_56, switch=sw_matrix_16_56, hash_hint=6aa97d6c9bd61714"
  },
  {
    "matrix_row_id": "matrix_016_row_057",
    "gate_family": "ownership",
    "precondition": "precondition 57 for matrix 16: validator observes canonical read-only evidence and compares 3 registries against policy segment 16.",
    "bad_pattern": "bad pattern 57 in matrix 16: writer drift toward family 1, generated path reports_real/segment_16_57, or naming spill into query_index alias without shim.",
    "expected_gate": "WARNING",
    "expected_severity": "warning",
    "remediation": "remediation 57: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 57: module=mod_matrix_16_57, boundary=bnd_matrix_16_57, switch=sw_matrix_16_57, hash_hint=6ea1001995beedb1"
  },
  {
    "matrix_row_id": "matrix_016_row_058",
    "gate_family": "artifact_naming",
    "precondition": "precondition 58 for matrix 16: validator observes canonical read-only evidence and compares 4 registries against policy segment 16.",
    "bad_pattern": "bad pattern 58 in matrix 16: writer drift toward family 2, generated path reports_real/segment_16_58, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 58: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 58: module=mod_matrix_16_58, boundary=bnd_matrix_16_58, switch=sw_matrix_16_58, hash_hint=7e25f4212fb8a730"
  },
  {
    "matrix_row_id": "matrix_016_row_059",
    "gate_family": "exclusions",
    "precondition": "precondition 59 for matrix 16: validator observes canonical read-only evidence and compares 5 registries against policy segment 16.",
    "bad_pattern": "bad pattern 59 in matrix 16: writer drift toward family 3, generated path reports_real/segment_16_59, or naming spill into query_index alias without shim.",
    "expected_gate": "READY",
    "expected_severity": "info",
    "remediation": "remediation 59: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 59: module=mod_matrix_16_59, boundary=bnd_matrix_16_59, switch=sw_matrix_16_59, hash_hint=90c98b5ab059216a"
  },
  {
    "matrix_row_id": "matrix_016_row_060",
    "gate_family": "write_limits",
    "precondition": "precondition 60 for matrix 16: validator observes canonical read-only evidence and compares 1 registries against policy segment 16.",
    "bad_pattern": "bad pattern 60 in matrix 16: writer drift toward family 4, generated path reports_real/segment_16_60, or naming spill into query_index alias without shim.",
    "expected_gate": "BLOCKED",
    "expected_severity": "critical",
    "remediation": "remediation 60: re-anchor install root, restore single-writer law, keep validator inside example_runtime/validator_outputs, and preserve registry_index.json portability.",
    "trace_note": "trace 60: module=mod_matrix_16_60, boundary=bnd_matrix_16_60, switch=sw_matrix_16_60, hash_hint=ab859d1e0be03123"
  }
]
