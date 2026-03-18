# 61_MUTATION_CLIENT_FIELD_MANUAL

## Operator checklist
- verify target ids are explicit
- verify mode is correct
- verify preview scope is intentional
- verify commit path is distinct
- verify diagnostics show approval/rejection clearly
- verify discard does not mutate baseline
- verify revert is scoped
- verify adapters did not become policy owners

## Smell list
- hidden side effects
- target inferred from stale UI only
- one function handling preview and commit interchangeably
- silent fallback to direct runtime write
