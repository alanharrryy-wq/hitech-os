-- Durable PC operational tasks. This is deliberately separate from support incidents:
-- incidents record support cases; tasks coordinate normal business operations.
CREATE TABLE "OperationalTask" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "createdById" TEXT,
  "assignedToId" TEXT,
  "title" TEXT NOT NULL,
  "description" TEXT,
  "area" TEXT NOT NULL,
  "priority" TEXT NOT NULL DEFAULT 'medium',
  "status" TEXT NOT NULL DEFAULT 'open',
  "href" TEXT,
  "source" TEXT NOT NULL DEFAULT 'manual',
  "idempotencyKey" TEXT,
  "version" INTEGER NOT NULL DEFAULT 1,
  "dueAt" DATETIME,
  "completedAt" DATETIME,
  "cancelledAt" DATETIME,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "OperationalTask_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "OperationalTask_createdById_fkey" FOREIGN KEY ("createdById") REFERENCES "User" ("id") ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT "OperationalTask_assignedToId_fkey" FOREIGN KEY ("assignedToId") REFERENCES "User" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE UNIQUE INDEX "OperationalTask_id_businessId_key" ON "OperationalTask"("id", "businessId");
CREATE UNIQUE INDEX "OperationalTask_businessId_idempotencyKey_key" ON "OperationalTask"("businessId", "idempotencyKey");
CREATE INDEX "OperationalTask_businessId_status_priority_idx" ON "OperationalTask"("businessId", "status", "priority");
CREATE INDEX "OperationalTask_businessId_assignedToId_updatedAt_idx" ON "OperationalTask"("businessId", "assignedToId", "updatedAt");
CREATE INDEX "OperationalTask_businessId_createdAt_idx" ON "OperationalTask"("businessId", "createdAt");
