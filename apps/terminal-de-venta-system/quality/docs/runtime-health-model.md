# Runtime Health Model

Runtime health is evidence. PQOS records local PRISMA port reachability and HTTP health responses without starting services.

A service that is down is not automatically a product blocker in Phase 2. It is a signal:

- optional down service: S3 diagnostic
- required down service: S1 blocker
- 5xx response: S2
- generic Next.js port in manifest: configuration blocker
