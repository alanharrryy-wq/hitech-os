# Risks

Blocking risks: none.

Non-blocking observation: historical live Tablet DB rows with `status=acked` use `syncedAt`; `ackedAt` and remote metadata columns exist but old rows were not backfilled because DB inspection was read-only and destructive/data-rewrite repair was out of scope.
Current proof is the temp Tablet verifier plus dispatcher/ACK gates: new/current metadata columns and indexes are asserted, and PC remains optional for the basic sale flow.
