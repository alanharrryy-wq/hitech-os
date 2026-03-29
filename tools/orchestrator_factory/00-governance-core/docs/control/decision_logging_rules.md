
# Decision Logging Rules

## When a decision record is mandatory
Create a decision record when changing:
- package topology
- path ownership
- canonical terminology
- source precedence
- acceptance gates
- freeze level or version of a shared interface
- a run objective after the run has opened
- an integration exception or merge waiver
- an active waiver status, scope, or expiry

## Decision record minimum fields
- `decision_id`
- date and authoring authority
- problem statement
- options considered
- decision taken
- reasons
- affected files and packages
- risk introduced
- rollback or reversal conditions
- supersedes and superseded-by references

## Storage
Store run-scoped decisions under:
`ops/runs/<run_id>/decisions/`

Store cross-run constitutional decisions in governance-owned docs or a governance decision register referenced by the affected docs.

## Decision quality rules
- no vague rationale
- no invisible oral history
- no “temporary” exception without an expiry trigger
- no topology change without downstream impact notes
- no waiver without exact scope and exact expiry logic
