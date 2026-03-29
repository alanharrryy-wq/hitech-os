# Conflict Resolution and Escalation

## Conflict classes
- terminology conflict
- path ownership conflict
- contract shape conflict
- dependency sequencing conflict
- bundle overlap conflict
- canonical-source conflict
- acceptance dispute

## Resolution path

### Level 1: package-local clarification
Use when the issue is inside one package and does not change shared rules.

### Level 2: cross-package governance decision
Use when two packages define the same concept differently, need the same runtime path, or disagree on a shared contract.

### Level 3: run-blocking escalation
Use when a conflict blocks the active run or invalidates already-generated packets.

### Level 4: operator escalation
Use when scope, risk, or business priority changes enough to require operator judgment.

## Mandatory escalation triggers
- new shared term needed
- runtime path ownership must widen
- frozen interface must change
- accepted bundle conflicts with canonical source
- a prompt or packet grants unauthorized behavior
- two upstream packages block each other

## Escalation output
Every escalation must identify:
- conflict type
- artifacts in conflict
- proposed options
- recommended decision
- downstream impact
