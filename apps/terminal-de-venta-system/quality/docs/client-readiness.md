# Client Readiness

`client-readiness` answers one question: can this build be promoted to a customer without embarrassing the operator or breaking the PRISMA operating rule?

It checks repo shape, contracts, Tablet sovereignty, outbox/idempotency signals, secret safety, automation catalog health, customer docs, support-pack readiness, upgrade readiness, drift, and evidence.

A green claim is valid only when `QUALITY_DECISION.json` is parseable and blockerCount is zero.
