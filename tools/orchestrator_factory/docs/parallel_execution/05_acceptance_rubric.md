# Acceptance Rubric

A bundle is acceptable when:
- structure is valid
- required manifests exist
- report and manifest are coherent
- every payload path is declared
- no forbidden paths are touched
- no exact-path conflicts exist with accepted peers
- consumed scope stays inside allowed ownership

## Possible statuses
- `accept`
- `accept_with_conditions`
- `reject`

## Typical rejection reasons
- structure or schema failure
- ownership violation
- payload mismatch
- exact path conflict
- stale bundle version or wrong run identifiers
