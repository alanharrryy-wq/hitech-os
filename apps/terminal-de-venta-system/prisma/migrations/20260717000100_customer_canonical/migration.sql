-- Canonical customer projection shared by PC administration and Tablet local reads.
-- Additive only: existing sales remain valid with a NULL customerId.
CREATE TABLE "Customer" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "displayName" TEXT NOT NULL,
  "phone" TEXT,
  "email" TEXT,
  "fiscalDataJson" TEXT,
  "segment" TEXT,
  "creditCents" INTEGER NOT NULL DEFAULT 0,
  "isActive" BOOLEAN NOT NULL DEFAULT true,
  "version" INTEGER NOT NULL DEFAULT 1,
  "sourceSurface" TEXT NOT NULL DEFAULT 'pc',
  "tombstoneAt" DATETIME,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "Customer_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

ALTER TABLE "Sale" ADD COLUMN "customerId" TEXT;

CREATE UNIQUE INDEX "Customer_id_businessId_key" ON "Customer"("id", "businessId");
CREATE INDEX "Customer_businessId_displayName_idx" ON "Customer"("businessId", "displayName");
CREATE INDEX "Customer_businessId_email_idx" ON "Customer"("businessId", "email");
CREATE INDEX "Customer_businessId_updatedAt_idx" ON "Customer"("businessId", "updatedAt");
CREATE INDEX "Customer_businessId_tombstoneAt_idx" ON "Customer"("businessId", "tombstoneAt");
CREATE INDEX "Sale_businessId_customerId_idx" ON "Sale"("businessId", "customerId");

CREATE TABLE "CustomerContact" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "customerId" TEXT NOT NULL,
  "label" TEXT NOT NULL,
  "channel" TEXT NOT NULL,
  "value" TEXT NOT NULL,
  "isPrimary" BOOLEAN NOT NULL DEFAULT false,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "CustomerContact_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "CustomerContact_customerId_businessId_fkey" FOREIGN KEY ("customerId", "businessId") REFERENCES "Customer" ("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "CustomerFiscalProfile" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "customerId" TEXT NOT NULL,
  "legalName" TEXT NOT NULL,
  "rfc" TEXT,
  "taxRegime" TEXT,
  "postalCode" TEXT,
  "usageCode" TEXT,
  "invoicingEmail" TEXT,
  "isPrimary" BOOLEAN NOT NULL DEFAULT true,
  "version" INTEGER NOT NULL DEFAULT 1,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "CustomerFiscalProfile_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "CustomerFiscalProfile_customerId_businessId_fkey" FOREIGN KEY ("customerId", "businessId") REFERENCES "Customer" ("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "CustomerSegment" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "color" TEXT,
  "isActive" BOOLEAN NOT NULL DEFAULT true,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "CustomerSegment_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "CustomerSegmentMembership" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "customerId" TEXT NOT NULL,
  "segmentId" TEXT NOT NULL,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "CustomerSegmentMembership_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "CustomerSegmentMembership_customerId_businessId_fkey" FOREIGN KEY ("customerId", "businessId") REFERENCES "Customer" ("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "CustomerSegmentMembership_segmentId_businessId_fkey" FOREIGN KEY ("segmentId", "businessId") REFERENCES "CustomerSegment" ("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "CustomerCreditEntry" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "customerId" TEXT NOT NULL,
  "saleId" TEXT,
  "entryType" TEXT NOT NULL,
  "amountCents" INTEGER NOT NULL,
  "balanceAfterCents" INTEGER NOT NULL,
  "reason" TEXT,
  "idempotencyKey" TEXT,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "CustomerCreditEntry_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "CustomerCreditEntry_customerId_businessId_fkey" FOREIGN KEY ("customerId", "businessId") REFERENCES "Customer" ("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "CustomerCreditEntry_saleId_businessId_fkey" FOREIGN KEY ("saleId", "businessId") REFERENCES "Sale" ("id", "businessId") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE "CustomerMergeCase" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "sourceCustomerId" TEXT NOT NULL,
  "targetCustomerId" TEXT NOT NULL,
  "status" TEXT NOT NULL DEFAULT 'open',
  "reason" TEXT,
  "requestedBy" TEXT,
  "approvedBy" TEXT,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "resolvedAt" DATETIME,
  CONSTRAINT "CustomerMergeCase_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "CustomerMergeCase_sourceCustomerId_businessId_fkey" FOREIGN KEY ("sourceCustomerId", "businessId") REFERENCES "Customer" ("id", "businessId") ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT "CustomerMergeCase_targetCustomerId_businessId_fkey" FOREIGN KEY ("targetCustomerId", "businessId") REFERENCES "Customer" ("id", "businessId") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE UNIQUE INDEX "CustomerContact_id_businessId_key" ON "CustomerContact"("id", "businessId");
CREATE UNIQUE INDEX "CustomerContact_businessId_customerId_channel_value_key" ON "CustomerContact"("businessId", "customerId", "channel", "value");
CREATE INDEX "CustomerContact_businessId_customerId_isPrimary_idx" ON "CustomerContact"("businessId", "customerId", "isPrimary");
CREATE UNIQUE INDEX "CustomerFiscalProfile_id_businessId_key" ON "CustomerFiscalProfile"("id", "businessId");
CREATE INDEX "CustomerFiscalProfile_businessId_customerId_isPrimary_idx" ON "CustomerFiscalProfile"("businessId", "customerId", "isPrimary");
CREATE INDEX "CustomerFiscalProfile_businessId_rfc_idx" ON "CustomerFiscalProfile"("businessId", "rfc");
CREATE UNIQUE INDEX "CustomerSegment_id_businessId_key" ON "CustomerSegment"("id", "businessId");
CREATE UNIQUE INDEX "CustomerSegment_businessId_name_key" ON "CustomerSegment"("businessId", "name");
CREATE INDEX "CustomerSegment_businessId_isActive_name_idx" ON "CustomerSegment"("businessId", "isActive", "name");
CREATE UNIQUE INDEX "CustomerSegmentMembership_businessId_customerId_segmentId_key" ON "CustomerSegmentMembership"("businessId", "customerId", "segmentId");
CREATE INDEX "CustomerSegmentMembership_businessId_segmentId_idx" ON "CustomerSegmentMembership"("businessId", "segmentId");
CREATE UNIQUE INDEX "CustomerCreditEntry_id_businessId_key" ON "CustomerCreditEntry"("id", "businessId");
CREATE UNIQUE INDEX "CustomerCreditEntry_businessId_customerId_idempotencyKey_key" ON "CustomerCreditEntry"("businessId", "customerId", "idempotencyKey");
CREATE INDEX "CustomerCreditEntry_businessId_customerId_createdAt_idx" ON "CustomerCreditEntry"("businessId", "customerId", "createdAt");
CREATE INDEX "CustomerCreditEntry_businessId_saleId_idx" ON "CustomerCreditEntry"("businessId", "saleId");
CREATE UNIQUE INDEX "CustomerMergeCase_id_businessId_key" ON "CustomerMergeCase"("id", "businessId");
CREATE INDEX "CustomerMergeCase_businessId_status_createdAt_idx" ON "CustomerMergeCase"("businessId", "status", "createdAt");
CREATE INDEX "CustomerMergeCase_businessId_sourceCustomerId_idx" ON "CustomerMergeCase"("businessId", "sourceCustomerId");
CREATE INDEX "CustomerMergeCase_businessId_targetCustomerId_idx" ON "CustomerMergeCase"("businessId", "targetCustomerId");
