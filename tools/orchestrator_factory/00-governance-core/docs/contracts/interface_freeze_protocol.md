
# Interface Freeze Protocol

## Freeze levels

### Draft
The concept exists but is not safe for downstream execution.

### Provisional
The shape is defined enough for downstream drafting, but not safe for irreversible implementation or integration.

### Frozen
Safe for downstream production work and bounded execution tasks.

### Superseded
No longer valid. Must point to the replacing interface or decision record.

## Freeze requirements
To mark an interface frozen:
- owner package identified
- consumers identified
- canonical terms approved
- acceptance criteria written
- version recorded according to `contract_versioning_policy.md`
- open contradictions closed or explicitly bounded
- supersession path clear if replacing an older interface

## Freeze discipline
- frozen interfaces do not change silently
- any frozen change needs a decision record
- derivative prompts and packets must be regenerated after frozen changes
