-- PRISMA Tablet sync dispatcher metadata.
-- Additive only. Apply only after DB backup and duplicate idempotency preflight.

ALTER TABLE "OutboxEvent" ADD COLUMN "lastAttemptAt" DATETIME;
ALTER TABLE "OutboxEvent" ADD COLUMN "nextRetryAt" DATETIME;
ALTER TABLE "OutboxEvent" ADD COLUMN "ackedAt" DATETIME;
ALTER TABLE "OutboxEvent" ADD COLUMN "failedAt" DATETIME;
ALTER TABLE "OutboxEvent" ADD COLUMN "conflictedAt" DATETIME;
ALTER TABLE "OutboxEvent" ADD COLUMN "deadLetterAt" DATETIME;
ALTER TABLE "OutboxEvent" ADD COLUMN "remoteEventId" TEXT;
ALTER TABLE "OutboxEvent" ADD COLUMN "remoteLedgerId" TEXT;
ALTER TABLE "OutboxEvent" ADD COLUMN "remoteLifecycleStatus" TEXT;
ALTER TABLE "OutboxEvent" ADD COLUMN "remoteDiagnosticsJson" TEXT;
ALTER TABLE "OutboxEvent" ADD COLUMN "remoteConflictCode" TEXT;
ALTER TABLE "OutboxEvent" ADD COLUMN "remoteRejectedReason" TEXT;

CREATE INDEX IF NOT EXISTS "OutboxEvent_businessId_status_nextRetryAt_idx" ON "OutboxEvent"("businessId", "status", "nextRetryAt");
CREATE INDEX IF NOT EXISTS "OutboxEvent_businessId_remoteLedgerId_idx" ON "OutboxEvent"("businessId", "remoteLedgerId");
CREATE UNIQUE INDEX IF NOT EXISTS "OutboxEvent_businessId_idempotencyKey_key" ON "OutboxEvent"("businessId", "idempotencyKey");
