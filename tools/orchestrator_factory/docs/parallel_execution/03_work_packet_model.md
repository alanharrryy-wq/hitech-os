
# Work Packet Model

A work packet is the tactical contract for one package in one round.

## Minimum fields
- `project_id`
- `run_id`
- `round_id`
- `package_id`
- objective
- dependencies
- allowed paths
- forbidden paths
- required outputs
- frozen input references
- rules

## Recommended additive fields
- `baseline_refs`
- `contract_refs`
- `waiver_refs`
- `communication_rules`

## Work packet rules
- work packets narrow active work, they do not replace constitutional ownership
- work packets may not widen ownership beyond homologated path policy
- if a packet becomes stale because a canonical source changed, regenerate it
- if a packet references a contract version, the bundle should echo that version in its manifest or report
