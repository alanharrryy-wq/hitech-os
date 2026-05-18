CREATE TABLE "Brand" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "description" TEXT,
  "status" TEXT NOT NULL DEFAULT 'ACTIVE',
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE ("businessId", "name"),
  UNIQUE ("id", "businessId"),
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

ALTER TABLE "Product" ADD COLUMN "brandId" TEXT;

CREATE INDEX "idx_brand_business_status" ON "Brand"("businessId", "status");
CREATE INDEX "idx_product_business_brand" ON "Product"("businessId", "brandId");
