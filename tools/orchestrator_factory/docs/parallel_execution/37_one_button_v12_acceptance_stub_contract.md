# One-Button v1.2 Acceptance Stub Contract

## Document Status
- Status: Frozen
- Version: v1.2
- Scope: `round/reports/acceptance_report.json`

## 1. Purpose
The session zip must always contain `round/reports/acceptance_report.json`. In early or incomplete session states, real integration bundles may not exist yet. The solution is a schema-valid acceptance stub that communicates "not evaluated yet" without breaking the contract.

## 2. Alignment requirement
The stub must remain aligned with the real schema file:
`F:\repos\hitech-os\tools\orchestrator_factory\schemas\execution_framework\acceptance_result.schema.json`

Required real fields from that schema:
- `schema_version`
- `project_id`
- `run_id`
- `round_id`
- `generated_at_utc`
- `overall_status`
- `package_results`

## 3. Required stub payload
When no bundles are present at export time, emit this minimum valid structure:

```json
{
  "schema_version": "1.0",
  "project_id": "<project_id>",
  "run_id": "<run_id>",
  "round_id": "<round_id>",
  "generated_at_utc": "<ISO8601 UTC>",
  "overall_status": "pending",
  "package_results": [],
  "has_bundles": false,
  "accepted_bundles": [],
  "rejected_bundles": [],
  "notes": [
    "Acceptance report stub emitted because no integration bundles were present at session export time."
  ]
}
```

## 4. Why `overall_status = pending`
The session can still be `ready_for_dispatch` even when acceptance is pending. This is not a contradiction:
- the session bundle may be structurally ready,
- coordination state may be valid,
- but integration acceptance may not have happened yet.

Using `pending` avoids the two common mistakes:
1. lying with `pass`,
2. overstating failure with `fail`.

## 5. Required behavior
### Must exist always
`acceptance_report.json` is always required in the zip, regardless of whether real package acceptance happened.

### Must remain schema-valid
The stub may add informative fields, but it must not omit required schema fields.

### Must be deterministic
Given the same project/run/round at export time without bundles, the stub should be identical except for timestamps and derived session metadata.

## 6. Transition to real acceptance report
When actual bundles or package results exist, the implementation may replace the stub with a real acceptance report, but:
- required schema fields remain mandatory,
- the output path does not change,
- `package_results` should reflect real results,
- notes may document whether the report is real or stubbed.

## 7. Relationship to manifest and issues
If the acceptance report is a stub, this fact should be transparent in:
- `session_manifest.issues[]` as a warning or informational issue,
- `session_summary.md` if helpful to the operator.

The stub must not be treated as a contract failure.

## 8. Examples of valid status interpretation
### Valid
- session status `ready_for_dispatch`
- acceptance report `overall_status = pending`

### Invalid
- session status `ready_for_dispatch`
- missing `acceptance_report.json`

### Potentially valid
- session status `blocked`
- acceptance report still emitted as stub to preserve export completeness if the implementation decides to package partial diagnostic state

## 9. Acceptance criteria
The acceptance stub contract is met when:
1. the file always exists,
2. it validates against the acceptance result schema,
3. `overall_status` is `pending` when no bundles exist,
4. missing bundles do not break session zip validation.
