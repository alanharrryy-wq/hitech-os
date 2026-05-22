-- PRISMA_PC_TO_TABLET_CATALOG_DELTA_V1
-- Adds Tablet-local checkpoint state for inbound PC -> Tablet catalog pulls.
CREATE TABLE "SyncCheckpoint" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "source" TEXT NOT NULL,
  "scopeKey" TEXT NOT NULL,
  "deviceId" TEXT,
  "terminalId" TEXT,
  "stream" TEXT NOT NULL,
  "cursorValue" TEXT,
  "lastEventId" TEXT,
  "lastIdempotencyKey" TEXT,
  "lastAttemptId" TEXT,
  "status" TEXT NOT NULL,
  "lifecycleStatus" TEXT,
  "checkpointAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "lastAttemptedAt" DATETIME,
  "lastSuccessfulAt" DATETIME,
  "metadataJson" TEXT,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "SyncCheckpoint_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE UNIQUE INDEX "SyncCheckpoint_businessId_scopeKey_stream_key" ON "SyncCheckpoint" ("businessId", "scopeKey", "stream");
CREATE INDEX "SyncCheckpoint_businessId_source_deviceId_stream_idx" ON "SyncCheckpoint" ("businessId", "source", "deviceId", "stream");
CREATE INDEX "SyncCheckpoint_businessId_source_status_checkpointAt_idx" ON "SyncCheckpoint" ("businessId", "source", "status", "checkpointAt");
CREATE INDEX "SyncCheckpoint_businessId_terminalId_checkpointAt_idx" ON "SyncCheckpoint" ("businessId", "terminalId", "checkpointAt");
CREATE INDEX "SyncCheckpoint_status_updatedAt_idx" ON "SyncCheckpoint" ("status", "updatedAt");
CREATE INDEX "SyncCheckpoint_createdAt_idx" ON "SyncCheckpoint" ("createdAt");
CREATE INDEX "SyncCheckpoint_updatedAt_idx" ON "SyncCheckpoint" ("updatedAt");
