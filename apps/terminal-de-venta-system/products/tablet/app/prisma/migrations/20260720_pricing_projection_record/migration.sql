-- PRISMA_PRICING_OWNER_V1
CREATE TABLE "PricingProjectionRecord" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "entityType" TEXT NOT NULL,
  "entityId" TEXT NOT NULL,
  "version" INTEGER NOT NULL DEFAULT 1,
  "status" TEXT NOT NULL DEFAULT 'ACTIVE',
  "startsAt" DATETIME,
  "endsAt" DATETIME,
  "payloadJson" TEXT NOT NULL,
  "sourceCursor" TEXT,
  "sourceOccurredAt" DATETIME,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "PricingProjectionRecord_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE UNIQUE INDEX "PricingProjectionRecord_businessId_entityType_entityId_key" ON "PricingProjectionRecord"("businessId", "entityType", "entityId");
CREATE INDEX "PricingProjectionRecord_businessId_status_entityType_idx" ON "PricingProjectionRecord"("businessId", "status", "entityType");
CREATE INDEX "PricingProjectionRecord_businessId_startsAt_endsAt_idx" ON "PricingProjectionRecord"("businessId", "startsAt", "endsAt");
