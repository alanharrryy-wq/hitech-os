# 55_PREVIEW_DIFF_AND_BASELINE_COMPARE

## Why diff exists

Preview without explainability erodes trust.
The mutation client should provide a compact diff summary between baseline, draft, and staged preview.

## Minimum diff summary
- added entities
- removed entities
- moved entities
- changed props fields
- changed style fields
- warnings for policy-sensitive changes
- whether commit is available

## Compare rules
- baseline remains the accepted anchor
- draft remains mutable working state
- preview stays a projection over that working state
- compare output should be deterministic for the same session inputs
