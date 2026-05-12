-- PRISMA Tablet local outbox idempotency promotion.
-- Additive-only: stores the event envelope idempotencyKey as a queryable column.

ALTER TABLE "OutboxEvent" ADD COLUMN "idempotencyKey" TEXT;

CREATE INDEX "idx_tablet_outboxevent_business_idempotency"
  ON "OutboxEvent"("businessId", "idempotencyKey");
