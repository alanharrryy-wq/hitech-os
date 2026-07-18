-- ProductVariant links an existing sellable Product to a parent Product.
-- Price, stock, barcode, SaleLine, StockMovement and Tablet catalog sync remain
-- owned by the existing sellable Product; this extension only stores grouping metadata.
CREATE TABLE "ProductVariant" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "productId" TEXT NOT NULL,
  "variantProductId" TEXT NOT NULL,
  "label" TEXT NOT NULL,
  "attributesJson" TEXT,
  "sortOrder" INTEGER NOT NULL DEFAULT 0,
  "status" TEXT NOT NULL DEFAULT 'ACTIVE',
  "idempotencyKey" TEXT,
  "version" INTEGER NOT NULL DEFAULT 1,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "ProductVariant_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "ProductVariant_parent_fkey" FOREIGN KEY ("productId", "businessId") REFERENCES "Product" ("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT "ProductVariant_sellable_fkey" FOREIGN KEY ("variantProductId", "businessId") REFERENCES "Product" ("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE UNIQUE INDEX "ProductVariant_id_businessId_key" ON "ProductVariant"("id", "businessId");
CREATE UNIQUE INDEX "ProductVariant_businessId_idempotencyKey_key" ON "ProductVariant"("businessId", "idempotencyKey");
CREATE UNIQUE INDEX "ProductVariant_businessId_variantProductId_key" ON "ProductVariant"("businessId", "variantProductId");
CREATE UNIQUE INDEX "ProductVariant_businessId_productId_variantProductId_key" ON "ProductVariant"("businessId", "productId", "variantProductId");
CREATE INDEX "ProductVariant_businessId_productId_status_sortOrder_idx" ON "ProductVariant"("businessId", "productId", "status", "sortOrder");
CREATE INDEX "ProductVariant_businessId_variantProductId_idx" ON "ProductVariant"("businessId", "variantProductId");
