# 56_MUTATION_REJECTION_AND_DIAGNOSTICS

## Rejection expectations

Rejected mutations must fail clearly.

A good rejection includes:
- mutation id
- request summary
- failing rule or policy id
- target summary
- source summary
- whether preview session remains intact
- whether retry is reasonable

## Diagnostics expectations
The mutation client should emit structured diagnostics for:
- request created
- shallow validation failed
- bridge preview approved
- bridge preview rejected
- commit approved
- commit rejected
- discard executed
- revert plan applied

Diagnostics should be good enough to explain what happened without opening five unrelated code paths.
