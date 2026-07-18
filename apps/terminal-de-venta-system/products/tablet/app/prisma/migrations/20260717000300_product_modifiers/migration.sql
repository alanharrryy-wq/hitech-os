-- Local Tablet projection of PC-owned modifier catalog and immutable ticket snapshots.
CREATE TABLE "ModifierGroup" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "minSelections" INTEGER NOT NULL DEFAULT 0,
  "maxSelections" INTEGER NOT NULL DEFAULT 1,
  "status" TEXT NOT NULL DEFAULT 'ACTIVE',
  "sortOrder" INTEGER NOT NULL DEFAULT 0,
  "idempotencyKey" TEXT,
  "version" INTEGER NOT NULL DEFAULT 1,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "ModifierGroup_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "ModifierOption" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "modifierGroupId" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "priceDeltaCents" INTEGER NOT NULL DEFAULT 0,
  "isDefault" BOOLEAN NOT NULL DEFAULT false,
  "status" TEXT NOT NULL DEFAULT 'ACTIVE',
  "sortOrder" INTEGER NOT NULL DEFAULT 0,
  "idempotencyKey" TEXT,
  "version" INTEGER NOT NULL DEFAULT 1,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "ModifierOption_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "ModifierOption_group_fkey" FOREIGN KEY ("modifierGroupId", "businessId") REFERENCES "ModifierGroup" ("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "ProductModifierGroup" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "productId" TEXT NOT NULL,
  "modifierGroupId" TEXT NOT NULL,
  "required" BOOLEAN NOT NULL DEFAULT false,
  "sortOrder" INTEGER NOT NULL DEFAULT 0,
  "status" TEXT NOT NULL DEFAULT 'ACTIVE',
  "idempotencyKey" TEXT,
  "version" INTEGER NOT NULL DEFAULT 1,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "ProductModifierGroup_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "ProductModifierGroup_product_fkey" FOREIGN KEY ("productId", "businessId") REFERENCES "Product" ("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "ProductModifierGroup_group_fkey" FOREIGN KEY ("modifierGroupId", "businessId") REFERENCES "ModifierGroup" ("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE
);

ALTER TABLE "SaleLine" ADD COLUMN "modifierSnapshotJson" TEXT;

CREATE UNIQUE INDEX "ModifierGroup_id_businessId_key" ON "ModifierGroup"("id", "businessId");
CREATE UNIQUE INDEX "ModifierGroup_businessId_name_key" ON "ModifierGroup"("businessId", "name");
CREATE UNIQUE INDEX "ModifierGroup_businessId_idempotencyKey_key" ON "ModifierGroup"("businessId", "idempotencyKey");
CREATE INDEX "ModifierGroup_businessId_status_sortOrder_idx" ON "ModifierGroup"("businessId", "status", "sortOrder");
CREATE UNIQUE INDEX "ModifierOption_id_businessId_key" ON "ModifierOption"("id", "businessId");
CREATE UNIQUE INDEX "ModifierOption_businessId_modifierGroupId_name_key" ON "ModifierOption"("businessId", "modifierGroupId", "name");
CREATE UNIQUE INDEX "ModifierOption_businessId_idempotencyKey_key" ON "ModifierOption"("businessId", "idempotencyKey");
CREATE INDEX "ModifierOption_businessId_modifierGroupId_status_sortOrder_idx" ON "ModifierOption"("businessId", "modifierGroupId", "status", "sortOrder");
CREATE UNIQUE INDEX "ProductModifierGroup_id_businessId_key" ON "ProductModifierGroup"("id", "businessId");
CREATE UNIQUE INDEX "ProductModifierGroup_businessId_productId_modifierGroupId_key" ON "ProductModifierGroup"("businessId", "productId", "modifierGroupId");
CREATE UNIQUE INDEX "ProductModifierGroup_businessId_idempotencyKey_key" ON "ProductModifierGroup"("businessId", "idempotencyKey");
CREATE INDEX "ProductModifierGroup_businessId_productId_status_sortOrder_idx" ON "ProductModifierGroup"("businessId", "productId", "status", "sortOrder");
CREATE INDEX "ProductModifierGroup_businessId_modifierGroupId_status_idx" ON "ProductModifierGroup"("businessId", "modifierGroupId", "status");
