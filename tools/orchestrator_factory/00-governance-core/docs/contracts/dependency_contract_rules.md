# Dependency Contract Rules

## Principle
Dependencies must be explicit, directional, and reviewable. Hidden dependency is a form of scope creep.

## Rules
- every package declares upstream dependencies
- every dependency names the specific artifacts consumed
- downstream packages may not silently redefine upstream outputs
- provisional inputs must be labeled as provisional
- a package may depend on governance plus any justified upstream packages, but never on a sibling's private notes

## Dependency changes
Changing dependencies requires:
- updated package docs
- dependency graph update if the graph changes
- downstream impact notes
- possible work-packet regeneration for active rounds
