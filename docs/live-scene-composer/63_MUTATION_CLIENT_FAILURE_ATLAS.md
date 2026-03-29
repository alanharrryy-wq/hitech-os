# 63_MUTATION_CLIENT_FAILURE_ATLAS

## Expected failure classes
- missing target
- stale revision
- policy rejection
- unsupported adapter
- preview session mismatch
- commit without preview lineage
- revert scope ambiguity
- diagnostics sink failure

## Desired behavior
- fail clearly
- fail locally
- preserve baseline/draft integrity
- preserve enough diagnostics to reproduce
