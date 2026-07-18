-- Tablet receives a privacy-minimal Customer projection for POS selection only.
-- Full contacts, fiscal records, credit and merge state remain PC-canonical.
CREATE TABLE "Customer" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "displayName" TEXT NOT NULL,
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
CREATE INDEX "Customer_businessId_updatedAt_idx" ON "Customer"("businessId", "updatedAt");
CREATE INDEX "Customer_businessId_tombstoneAt_idx" ON "Customer"("businessId", "tombstoneAt");
CREATE INDEX "Sale_businessId_customerId_idx" ON "Sale"("businessId", "customerId");
