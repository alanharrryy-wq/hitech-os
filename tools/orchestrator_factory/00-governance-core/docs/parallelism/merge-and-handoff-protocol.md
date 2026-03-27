# Merge and Handoff Protocol

## Purpose
Parallel work only scales if handoffs are deterministic and merges are explainable.

## Required handoff packet fields
- package ID
- `project_id`
- `run_id`
- `round_id`
- docs or bundle IDs included
- freeze level per artifact
- upstream artifacts consumed
- downstream consumers affected
- unresolved issues
- reviewer status
- conditions on integration, if any

## Merge order
1. constitutional updates if needed
2. package-local outputs freeze
3. acceptance decision
4. integration in dependency order
5. downstream notification of newly frozen interfaces

## Forbidden merge behavior
- silent replacement of a frozen contract
- hidden edits to another package folder
- path widening without decision record
- integrating rejected bundles
- treating a retry bundle as if it superseded the old bundle without recording version and status
