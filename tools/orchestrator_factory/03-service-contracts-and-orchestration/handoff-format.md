# Handoff Format for 03-service-contracts-and-orchestration

## Required packet fields
- `project_id`
- `run_id`
- `round_id`
- `package_id`
- handoff date
- artifacts included
- freeze level per artifact
- upstream artifacts consumed
- unresolved issues
- downstream packages impacted
- reviewer notes

## Handoff rule
Handoffs must never include hidden changes to another package's folder. If another package needs information, hand off the frozen contract or report, not a cross-folder edit.
