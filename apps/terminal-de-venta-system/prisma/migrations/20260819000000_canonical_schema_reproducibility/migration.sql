-- CreateTable
CREATE TABLE "ProductSupplier" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "businessId" TEXT NOT NULL,
    "productId" TEXT NOT NULL,
    "supplierId" TEXT NOT NULL,
    "isPrimary" BOOLEAN NOT NULL DEFAULT false,
    "status" TEXT NOT NULL DEFAULT 'ACTIVE',
    "leadTimeDays" INTEGER,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "ProductSupplier_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "ProductSupplier_productId_businessId_fkey" FOREIGN KEY ("productId", "businessId") REFERENCES "Product" ("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "ProductSupplier_supplierId_businessId_fkey" FOREIGN KEY ("supplierId", "businessId") REFERENCES "Supplier" ("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "DropdownCatalog" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "businessId" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "label" TEXT NOT NULL,
    "description" TEXT,
    "status" TEXT NOT NULL DEFAULT 'ACTIVE',
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "DropdownCatalog_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "DropdownOption" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "businessId" TEXT NOT NULL,
    "catalogId" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "label" TEXT NOT NULL,
    "sortOrder" INTEGER NOT NULL DEFAULT 0,
    "isDefault" BOOLEAN NOT NULL DEFAULT false,
    "status" TEXT NOT NULL DEFAULT 'ACTIVE',
    "metadataJson" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "DropdownOption_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "DropdownOption_catalogId_businessId_fkey" FOREIGN KEY ("catalogId", "businessId") REFERENCES "DropdownCatalog" ("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "CashAdjustment" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "businessId" TEXT NOT NULL,
    "cashSessionId" TEXT NOT NULL,
    "cashMovementId" TEXT,
    "actorId" TEXT,
    "adjustmentType" TEXT NOT NULL,
    "amountCents" INTEGER NOT NULL,
    "reason" TEXT NOT NULL,
    "evidenceJson" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "CashAdjustment_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "CashAdjustment_cashSessionId_businessId_fkey" FOREIGN KEY ("cashSessionId", "businessId") REFERENCES "CashSession" ("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "CashAdjustment_cashMovementId_fkey" FOREIGN KEY ("cashMovementId") REFERENCES "CashMovement" ("id") ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT "CashAdjustment_actorId_fkey" FOREIGN KEY ("actorId") REFERENCES "User" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "SalePaymentTender" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "businessId" TEXT NOT NULL,
    "saleId" TEXT NOT NULL,
    "tenderType" TEXT NOT NULL,
    "amountCents" INTEGER NOT NULL,
    "reference" TEXT,
    "metadataJson" TEXT,
    "recordedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "SalePaymentTender_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "SalePaymentTender_saleId_businessId_fkey" FOREIGN KEY ("saleId", "businessId") REFERENCES "Sale" ("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "SaleReturnLine" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "businessId" TEXT NOT NULL,
    "saleReturnId" TEXT NOT NULL,
    "saleId" TEXT,
    "saleLineId" TEXT,
    "productId" TEXT NOT NULL,
    "sku" TEXT NOT NULL,
    "productName" TEXT NOT NULL,
    "qty" INTEGER NOT NULL,
    "amountCents" INTEGER NOT NULL,
    "restoreStock" BOOLEAN NOT NULL DEFAULT true,
    "stockMovementId" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "SaleReturnLine_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "SaleReturnLine_saleReturnId_businessId_fkey" FOREIGN KEY ("saleReturnId", "businessId") REFERENCES "SaleReturn" ("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "SaleReturnLine_saleId_fkey" FOREIGN KEY ("saleId") REFERENCES "Sale" ("id") ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT "SaleReturnLine_saleLineId_fkey" FOREIGN KEY ("saleLineId") REFERENCES "SaleLine" ("id") ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT "SaleReturnLine_productId_businessId_fkey" FOREIGN KEY ("productId", "businessId") REFERENCES "Product" ("id", "businessId") ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT "SaleReturnLine_stockMovementId_fkey" FOREIGN KEY ("stockMovementId") REFERENCES "StockMovement" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "User" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "businessId" TEXT NOT NULL,
    "displayName" TEXT NOT NULL,
    "email" TEXT,
    "status" TEXT NOT NULL DEFAULT 'ACTIVE',
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "User_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "Role" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "businessId" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "label" TEXT NOT NULL,
    "description" TEXT,
    "status" TEXT NOT NULL DEFAULT 'ACTIVE',
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "Role_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "Permission" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "businessId" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "label" TEXT NOT NULL,
    "description" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "Permission_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "AuditEvent" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "businessId" TEXT NOT NULL,
    "actorId" TEXT,
    "topic" TEXT NOT NULL,
    "entityType" TEXT NOT NULL,
    "entityId" TEXT,
    "summary" TEXT NOT NULL,
    "beforeJson" TEXT,
    "afterJson" TEXT,
    "metadataJson" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "AuditEvent_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "AuditEvent_actorId_fkey" FOREIGN KEY ("actorId") REFERENCES "User" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "SupportIncident" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "businessId" TEXT NOT NULL,
    "openedById" TEXT,
    "assignedToId" TEXT,
    "title" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'open',
    "severity" TEXT NOT NULL DEFAULT 'normal',
    "source" TEXT NOT NULL DEFAULT 'local',
    "description" TEXT,
    "evidenceJson" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "resolvedAt" DATETIME,
    CONSTRAINT "SupportIncident_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "SupportIncident_openedById_fkey" FOREIGN KEY ("openedById") REFERENCES "User" ("id") ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT "SupportIncident_assignedToId_fkey" FOREIGN KEY ("assignedToId") REFERENCES "User" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "_RoleToUser" (
    "A" TEXT NOT NULL,
    "B" TEXT NOT NULL,
    CONSTRAINT "_RoleToUser_A_fkey" FOREIGN KEY ("A") REFERENCES "Role" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "_RoleToUser_B_fkey" FOREIGN KEY ("B") REFERENCES "User" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "_PermissionToRole" (
    "A" TEXT NOT NULL,
    "B" TEXT NOT NULL,
    CONSTRAINT "_PermissionToRole_A_fkey" FOREIGN KEY ("A") REFERENCES "Permission" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "_PermissionToRole_B_fkey" FOREIGN KEY ("B") REFERENCES "Role" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- RedefineTables
PRAGMA defer_foreign_keys=ON;
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_OperationalTask" (
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
INSERT INTO "new_OperationalTask" ("area", "assignedToId", "businessId", "cancelledAt", "completedAt", "createdAt", "createdById", "description", "dueAt", "href", "id", "idempotencyKey", "priority", "source", "status", "title", "updatedAt", "version") SELECT "area", "assignedToId", "businessId", "cancelledAt", "completedAt", "createdAt", "createdById", "description", "dueAt", "href", "id", "idempotencyKey", "priority", "source", "status", "title", "updatedAt", "version" FROM "OperationalTask";
DROP TABLE "OperationalTask";
ALTER TABLE "new_OperationalTask" RENAME TO "OperationalTask";
CREATE INDEX "OperationalTask_businessId_status_priority_idx" ON "OperationalTask"("businessId", "status", "priority");
CREATE INDEX "OperationalTask_businessId_assignedToId_updatedAt_idx" ON "OperationalTask"("businessId", "assignedToId", "updatedAt");
CREATE INDEX "OperationalTask_businessId_createdAt_idx" ON "OperationalTask"("businessId", "createdAt");
CREATE UNIQUE INDEX "OperationalTask_id_businessId_key" ON "OperationalTask"("id", "businessId");
CREATE UNIQUE INDEX "OperationalTask_businessId_idempotencyKey_key" ON "OperationalTask"("businessId", "idempotencyKey");
CREATE TABLE "new_Product" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "businessId" TEXT NOT NULL,
    "sku" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "category" TEXT NOT NULL,
    "brandId" TEXT,
    "priceCents" INTEGER NOT NULL,
    "costCents" INTEGER NOT NULL,
    "stockOnHand" INTEGER NOT NULL DEFAULT 0,
    "taxRateId" TEXT,
    "mediaRef" TEXT,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "Product_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "Product_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand" ("id") ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT "Product_taxRateId_fkey" FOREIGN KEY ("taxRateId") REFERENCES "TaxRate" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);
INSERT INTO "new_Product" ("brandId", "businessId", "category", "costCents", "createdAt", "id", "isActive", "mediaRef", "name", "priceCents", "sku", "stockOnHand", "taxRateId", "updatedAt") SELECT "brandId", "businessId", "category", "costCents", "createdAt", "id", "isActive", "mediaRef", "name", "priceCents", "sku", "stockOnHand", "taxRateId", "updatedAt" FROM "Product";
DROP TABLE "Product";
ALTER TABLE "new_Product" RENAME TO "Product";
CREATE INDEX "Product_businessId_brandId_idx" ON "Product"("businessId", "brandId");
CREATE INDEX "Product_businessId_isActive_idx" ON "Product"("businessId", "isActive");
CREATE INDEX "Product_businessId_category_idx" ON "Product"("businessId", "category");
CREATE UNIQUE INDEX "Product_businessId_sku_key" ON "Product"("businessId", "sku");
CREATE UNIQUE INDEX "Product_id_businessId_key" ON "Product"("id", "businessId");
CREATE TABLE "new_Sale" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "businessId" TEXT NOT NULL,
    "terminalId" TEXT NOT NULL,
    "cashSessionId" TEXT,
    "customerId" TEXT,
    "folio" TEXT NOT NULL,
    "cashier" TEXT NOT NULL,
    "totalCents" INTEGER NOT NULL,
    "status" TEXT NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "Sale_businessId_fkey" FOREIGN KEY ("businessId") REFERENCES "Business" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "Sale_terminalId_businessId_fkey" FOREIGN KEY ("terminalId", "businessId") REFERENCES "Terminal" ("id", "businessId") ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT "Sale_cashSessionId_fkey" FOREIGN KEY ("cashSessionId") REFERENCES "CashSession" ("id") ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT "Sale_customerId_businessId_fkey" FOREIGN KEY ("customerId", "businessId") REFERENCES "Customer" ("id", "businessId") ON DELETE RESTRICT ON UPDATE CASCADE
);
INSERT INTO "new_Sale" ("businessId", "cashSessionId", "cashier", "createdAt", "customerId", "folio", "id", "status", "terminalId", "totalCents") SELECT "businessId", "cashSessionId", "cashier", "createdAt", "customerId", "folio", "id", "status", "terminalId", "totalCents" FROM "Sale";
DROP TABLE "Sale";
ALTER TABLE "new_Sale" RENAME TO "Sale";
CREATE INDEX "Sale_businessId_createdAt_idx" ON "Sale"("businessId", "createdAt");
CREATE INDEX "Sale_businessId_customerId_idx" ON "Sale"("businessId", "customerId");
CREATE UNIQUE INDEX "Sale_businessId_folio_key" ON "Sale"("businessId", "folio");
CREATE UNIQUE INDEX "Sale_id_businessId_key" ON "Sale"("id", "businessId");
PRAGMA foreign_keys=ON;
PRAGMA defer_foreign_keys=OFF;

-- CreateIndex
CREATE INDEX "ProductSupplier_businessId_productId_isPrimary_idx" ON "ProductSupplier"("businessId", "productId", "isPrimary");

-- CreateIndex
CREATE INDEX "ProductSupplier_businessId_supplierId_status_idx" ON "ProductSupplier"("businessId", "supplierId", "status");

-- CreateIndex
CREATE UNIQUE INDEX "ProductSupplier_businessId_productId_supplierId_key" ON "ProductSupplier"("businessId", "productId", "supplierId");

-- CreateIndex
CREATE INDEX "DropdownCatalog_businessId_status_idx" ON "DropdownCatalog"("businessId", "status");

-- CreateIndex
CREATE UNIQUE INDEX "DropdownCatalog_businessId_code_key" ON "DropdownCatalog"("businessId", "code");

-- CreateIndex
CREATE UNIQUE INDEX "DropdownCatalog_id_businessId_key" ON "DropdownCatalog"("id", "businessId");

-- CreateIndex
CREATE INDEX "DropdownOption_businessId_catalogId_sortOrder_idx" ON "DropdownOption"("businessId", "catalogId", "sortOrder");

-- CreateIndex
CREATE INDEX "DropdownOption_businessId_status_idx" ON "DropdownOption"("businessId", "status");

-- CreateIndex
CREATE UNIQUE INDEX "DropdownOption_businessId_catalogId_code_key" ON "DropdownOption"("businessId", "catalogId", "code");

-- CreateIndex
CREATE INDEX "CashAdjustment_businessId_cashSessionId_createdAt_idx" ON "CashAdjustment"("businessId", "cashSessionId", "createdAt");

-- CreateIndex
CREATE INDEX "CashAdjustment_businessId_adjustmentType_createdAt_idx" ON "CashAdjustment"("businessId", "adjustmentType", "createdAt");

-- CreateIndex
CREATE UNIQUE INDEX "CashAdjustment_id_businessId_key" ON "CashAdjustment"("id", "businessId");

-- CreateIndex
CREATE INDEX "SalePaymentTender_businessId_saleId_idx" ON "SalePaymentTender"("businessId", "saleId");

-- CreateIndex
CREATE INDEX "SalePaymentTender_businessId_tenderType_recordedAt_idx" ON "SalePaymentTender"("businessId", "tenderType", "recordedAt");

-- CreateIndex
CREATE UNIQUE INDEX "SalePaymentTender_id_businessId_key" ON "SalePaymentTender"("id", "businessId");

-- CreateIndex
CREATE INDEX "SaleReturnLine_businessId_saleReturnId_idx" ON "SaleReturnLine"("businessId", "saleReturnId");

-- CreateIndex
CREATE INDEX "SaleReturnLine_businessId_productId_idx" ON "SaleReturnLine"("businessId", "productId");

-- CreateIndex
CREATE INDEX "SaleReturnLine_businessId_restoreStock_idx" ON "SaleReturnLine"("businessId", "restoreStock");

-- CreateIndex
CREATE UNIQUE INDEX "SaleReturnLine_id_businessId_key" ON "SaleReturnLine"("id", "businessId");

-- CreateIndex
CREATE INDEX "User_businessId_status_idx" ON "User"("businessId", "status");

-- CreateIndex
CREATE UNIQUE INDEX "User_businessId_email_key" ON "User"("businessId", "email");

-- CreateIndex
CREATE UNIQUE INDEX "User_id_businessId_key" ON "User"("id", "businessId");

-- CreateIndex
CREATE INDEX "Role_businessId_status_idx" ON "Role"("businessId", "status");

-- CreateIndex
CREATE UNIQUE INDEX "Role_businessId_code_key" ON "Role"("businessId", "code");

-- CreateIndex
CREATE UNIQUE INDEX "Role_id_businessId_key" ON "Role"("id", "businessId");

-- CreateIndex
CREATE UNIQUE INDEX "Permission_businessId_code_key" ON "Permission"("businessId", "code");

-- CreateIndex
CREATE UNIQUE INDEX "Permission_id_businessId_key" ON "Permission"("id", "businessId");

-- CreateIndex
CREATE INDEX "AuditEvent_businessId_topic_createdAt_idx" ON "AuditEvent"("businessId", "topic", "createdAt");

-- CreateIndex
CREATE INDEX "AuditEvent_businessId_entityType_entityId_idx" ON "AuditEvent"("businessId", "entityType", "entityId");

-- CreateIndex
CREATE UNIQUE INDEX "AuditEvent_id_businessId_key" ON "AuditEvent"("id", "businessId");

-- CreateIndex
CREATE INDEX "SupportIncident_businessId_status_severity_idx" ON "SupportIncident"("businessId", "status", "severity");

-- CreateIndex
CREATE INDEX "SupportIncident_businessId_createdAt_idx" ON "SupportIncident"("businessId", "createdAt");

-- CreateIndex
CREATE UNIQUE INDEX "SupportIncident_id_businessId_key" ON "SupportIncident"("id", "businessId");

-- CreateIndex
CREATE UNIQUE INDEX "_RoleToUser_AB_unique" ON "_RoleToUser"("A", "B");

-- CreateIndex
CREATE INDEX "_RoleToUser_B_index" ON "_RoleToUser"("B");

-- CreateIndex
CREATE UNIQUE INDEX "_PermissionToRole_AB_unique" ON "_PermissionToRole"("A", "B");

-- CreateIndex
CREATE INDEX "_PermissionToRole_B_index" ON "_PermissionToRole"("B");

-- CreateIndex
CREATE UNIQUE INDEX "DiscountPolicy_id_businessId_key" ON "DiscountPolicy"("id", "businessId");

-- CreateIndex
CREATE UNIQUE INDEX "PricingAuthorizationRequest_id_businessId_key" ON "PricingAuthorizationRequest"("id", "businessId");

-- CreateIndex
CREATE UNIQUE INDEX "PromotionRule_id_businessId_key" ON "PromotionRule"("id", "businessId");

-- CreateIndex
CREATE UNIQUE INDEX "SaleReturn_id_businessId_key" ON "SaleReturn"("id", "businessId");
