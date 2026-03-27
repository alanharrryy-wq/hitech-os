# Traceability Model

## Required trace chain
`idea -> homologation -> project -> run -> round -> package -> work packet -> bundle -> acceptance decision -> integrated artifact`

## Minimum metadata expectations
For any serious artifact, it should be possible to answer:
- which `project_id` it belongs to
- which `run_id` and `round_id` produced it
- which package owned it
- which higher-order artifacts authorized it
- which downstream consumers rely on it
- whether it is frozen, provisional, or superseded

## Traceability rules
- IDs must be filesystem-safe and stable
- derivative artifacts must point back to their frozen inputs
- decision records must point to the artifacts they changed
- acceptance reports must point to the bundles they judged

## Why this matters
Traceability turns “which chat changed what and why?” from a detective novel into a lookup.
