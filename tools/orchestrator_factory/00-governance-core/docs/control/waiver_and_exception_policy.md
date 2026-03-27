
# Waiver and Exception Policy

## Purpose
A waiver is a controlled exception to the normal framework rules. It exists to contain risk, not to erase it.

## Waiver types
- path ownership exception
- urgent override
- partial acceptance
- emergency corrective integration
- contract freeze exception

## Approval rule
No waiver is active until it is written, approved, and stored as a decision artifact.

## Required fields
- `waiver_id`
- `project_id`
- `run_id`
- `round_id` when applicable
- waiver type
- requester
- approving authority
- exact rule being waived
- allowed action
- affected paths or artifacts
- risk introduced
- conditions and compensating controls
- expiry trigger or expiry date
- rollback or reversal path
- status

## Storage
Run-scoped waivers live under:
`ops/runs/<run_id>/decisions/`

The waiver record should sit beside the decision trail that justified it.

## Waiver discipline
- waivers are narrow, not blanket permissions
- waivers expire
- expired waivers do not authorize future bundles
- a new round does not inherit a waiver automatically
- every bundle or integration action that relies on a waiver must reference that waiver

## Common cases
### Path ownership exception
Used only when a package must touch a path outside default ownership and governance determines that the risk is lower than blocking the round.

### Partial acceptance
Used when a bundle is usable but integration depends on tracked conditions. It is not a silent downgrade of a rejection.

### Emergency corrective integration
Used when an urgent fix must be integrated to restore safety or continuity. The waiver must still record who approved the emergency path and how normal governance will be restored.
