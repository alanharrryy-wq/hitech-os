# ERROR BOUNDARIES

- Product action faults are isolated to product runtime.
- Host receives contract error envelope, not raw internals.
- Timeout and disposal failures are surfaced as contract errors.