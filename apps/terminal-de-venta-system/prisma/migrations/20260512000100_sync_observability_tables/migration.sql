-- PRISMA sync observability tables.
-- Forward-only additive migration. Does not alter the existing OutboxEvent lifecycle migration.

CREATE TABLE IF NOT EXISTS "SyncAttempt" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "eventId" TEXT,
  "outboxEventId" TEXT,
  "idempotencyKey" TEXT,
  "source" TEXT NOT NULL,
  "deviceId" TEXT,
  "terminalId" TEXT,
  "topic" TEXT,
  "status" TEXT NOT NULL,
  "lifecycleStatus" TEXT,
  "attemptNumber" INTEGER NOT NULL DEFAULT 1,
  "receivedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "startedAt" DATETIME,
  "finishedAt" DATETIME,
  "durationMs" INTEGER,
  "errorCode" TEXT,
  "diagnosticsJson" TEXT,
  "payloadFingerprint" TEXT,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS "SyncConflict" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "eventId" TEXT,
  "outboxEventId" TEXT,
  "idempotencyKey" TEXT,
  "source" TEXT NOT NULL,
  "deviceId" TEXT,
  "terminalId" TEXT,
  "topic" TEXT,
  "aggregateId" TEXT,
  "conflictCode" TEXT NOT NULL,
  "label" TEXT NOT NULL,
  "severity" TEXT NOT NULL,
  "detail" TEXT NOT NULL,
  "status" TEXT NOT NULL DEFAULT 'open',
  "detectedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "resolvedAt" DATETIME,
  "resolution" TEXT,
  "diagnosticsJson" TEXT,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS "DeviceHeartbeat" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "deviceId" TEXT NOT NULL,
  "source" TEXT NOT NULL,
  "surface" TEXT NOT NULL,
  "runtimeMode" TEXT NOT NULL,
  "appVersion" TEXT NOT NULL,
  "schemaVersion" TEXT,
  "licenseStatus" TEXT,
  "syncStatus" TEXT,
  "health" TEXT NOT NULL,
  "status" TEXT NOT NULL,
  "outboxCount" INTEGER,
  "lastSaleAt" DATETIME,
  "lastDiagnosticAt" DATETIME,
  "lastSeenAt" DATETIME NOT NULL,
  "observedAt" DATETIME NOT NULL,
  "metadataJson" TEXT,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS "SyncCheckpoint" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "source" TEXT NOT NULL,
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
  "metadataJson" TEXT,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS "SyncOutboxStatusBucket" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "source" TEXT NOT NULL,
  "deviceId" TEXT,
  "terminalId" TEXT,
  "status" TEXT NOT NULL,
  "lifecycleStatus" TEXT,
  "topic" TEXT,
  "bucketStartAt" DATETIME NOT NULL,
  "bucketEndAt" DATETIME,
  "count" INTEGER NOT NULL DEFAULT 0,
  "oldestEventAt" DATETIME,
  "newestEventAt" DATETIME,
  "staleCount" INTEGER NOT NULL DEFAULT 0,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS "DataSourceFreshness" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "source" TEXT NOT NULL,
  "deviceId" TEXT,
  "surface" TEXT,
  "status" TEXT NOT NULL,
  "confidence" REAL,
  "freshnessSeconds" INTEGER,
  "latencyMs" INTEGER,
  "errorCount" INTEGER NOT NULL DEFAULT 0,
  "lastSeenAt" DATETIME,
  "lastEventAt" DATETIME,
  "lastCheckpointAt" DATETIME,
  "lastHeartbeatAt" DATETIME,
  "lastError" TEXT,
  "warningsJson" TEXT,
  "metadataJson" TEXT,
  "observedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS "idx_syncattempt_business_source_status_created" ON "SyncAttempt"("businessId", "source", "status", "createdAt");
CREATE INDEX IF NOT EXISTS "idx_syncattempt_business_device_created" ON "SyncAttempt"("businessId", "deviceId", "createdAt");
CREATE INDEX IF NOT EXISTS "idx_syncattempt_business_idempotency" ON "SyncAttempt"("businessId", "idempotencyKey");
CREATE INDEX IF NOT EXISTS "idx_syncattempt_status_created" ON "SyncAttempt"("status", "createdAt");
CREATE INDEX IF NOT EXISTS "idx_syncattempt_created" ON "SyncAttempt"("createdAt");
CREATE INDEX IF NOT EXISTS "idx_syncattempt_updated" ON "SyncAttempt"("updatedAt");

CREATE INDEX IF NOT EXISTS "idx_syncconflict_business_status_detected" ON "SyncConflict"("businessId", "status", "detectedAt");
CREATE INDEX IF NOT EXISTS "idx_syncconflict_business_source_severity_detected" ON "SyncConflict"("businessId", "source", "severity", "detectedAt");
CREATE INDEX IF NOT EXISTS "idx_syncconflict_business_device_status" ON "SyncConflict"("businessId", "deviceId", "status");
CREATE INDEX IF NOT EXISTS "idx_syncconflict_business_idempotency" ON "SyncConflict"("businessId", "idempotencyKey");
CREATE INDEX IF NOT EXISTS "idx_syncconflict_code_status" ON "SyncConflict"("conflictCode", "status");
CREATE INDEX IF NOT EXISTS "idx_syncconflict_created" ON "SyncConflict"("createdAt");
CREATE INDEX IF NOT EXISTS "idx_syncconflict_updated" ON "SyncConflict"("updatedAt");

CREATE INDEX IF NOT EXISTS "idx_deviceheartbeat_business_device_seen" ON "DeviceHeartbeat"("businessId", "deviceId", "lastSeenAt");
CREATE INDEX IF NOT EXISTS "idx_deviceheartbeat_business_source_status_seen" ON "DeviceHeartbeat"("businessId", "source", "status", "lastSeenAt");
CREATE INDEX IF NOT EXISTS "idx_deviceheartbeat_business_status_updated" ON "DeviceHeartbeat"("businessId", "status", "updatedAt");
CREATE INDEX IF NOT EXISTS "idx_deviceheartbeat_source_health_observed" ON "DeviceHeartbeat"("source", "health", "observedAt");
CREATE INDEX IF NOT EXISTS "idx_deviceheartbeat_created" ON "DeviceHeartbeat"("createdAt");
CREATE INDEX IF NOT EXISTS "idx_deviceheartbeat_updated" ON "DeviceHeartbeat"("updatedAt");

CREATE INDEX IF NOT EXISTS "idx_synccheckpoint_business_source_device_stream" ON "SyncCheckpoint"("businessId", "source", "deviceId", "stream");
CREATE INDEX IF NOT EXISTS "idx_synccheckpoint_business_source_status_checkpoint" ON "SyncCheckpoint"("businessId", "source", "status", "checkpointAt");
CREATE INDEX IF NOT EXISTS "idx_synccheckpoint_business_device_checkpoint" ON "SyncCheckpoint"("businessId", "deviceId", "checkpointAt");
CREATE INDEX IF NOT EXISTS "idx_synccheckpoint_status_updated" ON "SyncCheckpoint"("status", "updatedAt");
CREATE INDEX IF NOT EXISTS "idx_synccheckpoint_created" ON "SyncCheckpoint"("createdAt");
CREATE INDEX IF NOT EXISTS "idx_synccheckpoint_updated" ON "SyncCheckpoint"("updatedAt");

CREATE INDEX IF NOT EXISTS "idx_syncoutboxbucket_business_source_status_bucket" ON "SyncOutboxStatusBucket"("businessId", "source", "status", "bucketStartAt");
CREATE INDEX IF NOT EXISTS "idx_syncoutboxbucket_business_device_status" ON "SyncOutboxStatusBucket"("businessId", "deviceId", "status");
CREATE INDEX IF NOT EXISTS "idx_syncoutboxbucket_business_lifecycle_bucket" ON "SyncOutboxStatusBucket"("businessId", "lifecycleStatus", "bucketStartAt");
CREATE INDEX IF NOT EXISTS "idx_syncoutboxbucket_business_topic_status" ON "SyncOutboxStatusBucket"("businessId", "topic", "status");
CREATE INDEX IF NOT EXISTS "idx_syncoutboxbucket_bucket_start" ON "SyncOutboxStatusBucket"("bucketStartAt");
CREATE INDEX IF NOT EXISTS "idx_syncoutboxbucket_created" ON "SyncOutboxStatusBucket"("createdAt");
CREATE INDEX IF NOT EXISTS "idx_syncoutboxbucket_updated" ON "SyncOutboxStatusBucket"("updatedAt");

CREATE INDEX IF NOT EXISTS "idx_datasourcefreshness_business_source_status_updated" ON "DataSourceFreshness"("businessId", "source", "status", "updatedAt");
CREATE INDEX IF NOT EXISTS "idx_datasourcefreshness_business_device_seen" ON "DataSourceFreshness"("businessId", "deviceId", "lastSeenAt");
CREATE INDEX IF NOT EXISTS "idx_datasourcefreshness_business_status_observed" ON "DataSourceFreshness"("businessId", "status", "observedAt");
CREATE INDEX IF NOT EXISTS "idx_datasourcefreshness_source_updated" ON "DataSourceFreshness"("source", "updatedAt");
CREATE INDEX IF NOT EXISTS "idx_datasourcefreshness_freshness_seconds" ON "DataSourceFreshness"("freshnessSeconds");
CREATE INDEX IF NOT EXISTS "idx_datasourcefreshness_created" ON "DataSourceFreshness"("createdAt");
CREATE INDEX IF NOT EXISTS "idx_datasourcefreshness_updated" ON "DataSourceFreshness"("updatedAt");
