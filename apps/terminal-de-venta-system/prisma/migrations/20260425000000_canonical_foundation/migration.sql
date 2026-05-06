PRAGMA foreign_keys=ON;

CREATE TABLE "Business" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "name" TEXT NOT NULL,
  "taxId" TEXT,
  "currency" TEXT NOT NULL DEFAULT 'MXN',
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "Store" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "code" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE ("businessId", "code"),
  UNIQUE ("id", "businessId"),
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "Terminal" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "storeId" TEXT NOT NULL,
  "code" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "isActive" BOOLEAN NOT NULL DEFAULT 1,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE ("businessId", "code"),
  UNIQUE ("id", "businessId"),
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("storeId", "businessId") REFERENCES "Store"("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "TaxRate" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "rateBps" INTEGER NOT NULL,
  "isDefault" BOOLEAN NOT NULL DEFAULT 0,
  "isActive" BOOLEAN NOT NULL DEFAULT 1,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE ("businessId", "name"),
  UNIQUE ("id", "businessId"),
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "Product" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "sku" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "category" TEXT NOT NULL,
  "priceCents" INTEGER NOT NULL,
  "costCents" INTEGER NOT NULL,
  "stockOnHand" INTEGER NOT NULL DEFAULT 0,
  "taxRateId" TEXT,
  "isActive" BOOLEAN NOT NULL DEFAULT 1,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE ("businessId", "sku"),
  UNIQUE ("id", "businessId"),
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("taxRateId") REFERENCES "TaxRate"("id") ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE "Barcode" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "productId" TEXT NOT NULL,
  "code" TEXT NOT NULL,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE ("businessId", "code"),
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("productId", "businessId") REFERENCES "Product"("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "PriceList" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "currency" TEXT NOT NULL DEFAULT 'MXN',
  "isDefault" BOOLEAN NOT NULL DEFAULT 0,
  "isActive" BOOLEAN NOT NULL DEFAULT 1,
  "startsAt" DATETIME NOT NULL,
  "endsAt" DATETIME,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE ("businessId", "name"),
  UNIQUE ("id", "businessId"),
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "PriceListItem" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "priceListId" TEXT NOT NULL,
  "productId" TEXT NOT NULL,
  "priceCents" INTEGER NOT NULL,
  "startsAt" DATETIME NOT NULL,
  "endsAt" DATETIME,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE ("businessId", "priceListId", "productId", "startsAt"),
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("priceListId", "businessId") REFERENCES "PriceList"("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("productId", "businessId") REFERENCES "Product"("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "StockSnapshot" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "productId" TEXT NOT NULL,
  "location" TEXT NOT NULL,
  "onHand" INTEGER NOT NULL,
  "reserved" INTEGER NOT NULL,
  "available" INTEGER NOT NULL,
  "daysCover" REAL NOT NULL,
  "snapshotAt" DATETIME NOT NULL,
  UNIQUE ("businessId", "productId", "location"),
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("productId", "businessId") REFERENCES "Product"("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "StockMovement" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "productId" TEXT NOT NULL,
  "movement" TEXT NOT NULL,
  "qty" INTEGER NOT NULL,
  "reason" TEXT NOT NULL,
  "location" TEXT NOT NULL,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("productId", "businessId") REFERENCES "Product"("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "Supplier" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "status" TEXT NOT NULL DEFAULT 'ACTIVE',
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE ("businessId", "name"),
  UNIQUE ("id", "businessId"),
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "PurchaseOrder" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "supplierId" TEXT NOT NULL,
  "folio" TEXT NOT NULL,
  "status" TEXT NOT NULL,
  "createdAt" DATETIME NOT NULL,
  "expectedAt" DATETIME NOT NULL,
  "subtotalCents" INTEGER NOT NULL,
  "taxCents" INTEGER NOT NULL,
  "totalCents" INTEGER NOT NULL,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE ("businessId", "folio"),
  UNIQUE ("id", "businessId"),
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("supplierId", "businessId") REFERENCES "Supplier"("id", "businessId") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE "PurchaseOrderLine" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "purchaseOrderId" TEXT NOT NULL,
  "productId" TEXT NOT NULL,
  "sku" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "qtyOrdered" INTEGER NOT NULL,
  "unitCostCents" INTEGER NOT NULL,
  "lineSubtotalCents" INTEGER NOT NULL,
  "lineTaxCents" INTEGER NOT NULL,
  "lineTotalCents" INTEGER NOT NULL,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("purchaseOrderId", "businessId") REFERENCES "PurchaseOrder"("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("productId", "businessId") REFERENCES "Product"("id", "businessId") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE "GoodsReceipt" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "purchaseOrderId" TEXT NOT NULL,
  "supplierId" TEXT NOT NULL,
  "folio" TEXT NOT NULL,
  "status" TEXT NOT NULL,
  "receivedAt" DATETIME NOT NULL,
  "subtotalCents" INTEGER NOT NULL,
  "taxCents" INTEGER NOT NULL,
  "totalCents" INTEGER NOT NULL,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE ("businessId", "folio"),
  UNIQUE ("id", "businessId"),
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("purchaseOrderId", "businessId") REFERENCES "PurchaseOrder"("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("supplierId", "businessId") REFERENCES "Supplier"("id", "businessId") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE "GoodsReceiptLine" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "goodsReceiptId" TEXT NOT NULL,
  "purchaseOrderLineId" TEXT,
  "productId" TEXT NOT NULL,
  "sku" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "qtyReceived" INTEGER NOT NULL,
  "unitCostCents" INTEGER NOT NULL,
  "lineSubtotalCents" INTEGER NOT NULL,
  "lineTaxCents" INTEGER NOT NULL,
  "lineTotalCents" INTEGER NOT NULL,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("goodsReceiptId", "businessId") REFERENCES "GoodsReceipt"("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("productId", "businessId") REFERENCES "Product"("id", "businessId") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE "ReplenishmentSignal" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "productId" TEXT NOT NULL,
  "location" TEXT NOT NULL,
  "suggestedQty" INTEGER NOT NULL,
  "priority" TEXT NOT NULL,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("productId", "businessId") REFERENCES "Product"("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "CashSession" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "storeId" TEXT NOT NULL,
  "terminalId" TEXT NOT NULL,
  "cashierId" TEXT NOT NULL,
  "cashier" TEXT NOT NULL,
  "openedAt" DATETIME NOT NULL,
  "closedAt" DATETIME,
  "cashStartCents" INTEGER NOT NULL,
  "cashEndCents" INTEGER,
  "expectedCashCents" INTEGER,
  "varianceCents" INTEGER,
  "status" TEXT NOT NULL,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE ("id", "businessId"),
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("storeId", "businessId") REFERENCES "Store"("id", "businessId") ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY ("terminalId", "businessId") REFERENCES "Terminal"("id", "businessId") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE "CashMovement" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "cashSessionId" TEXT NOT NULL,
  "movement" TEXT NOT NULL,
  "amountCents" INTEGER NOT NULL,
  "reason" TEXT NOT NULL,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("cashSessionId", "businessId") REFERENCES "CashSession"("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "Sale" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "terminalId" TEXT NOT NULL,
  "cashSessionId" TEXT,
  "folio" TEXT NOT NULL,
  "cashier" TEXT NOT NULL,
  "totalCents" INTEGER NOT NULL,
  "status" TEXT NOT NULL,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE ("businessId", "folio"),
  UNIQUE ("id", "businessId"),
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("terminalId", "businessId") REFERENCES "Terminal"("id", "businessId") ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY ("cashSessionId") REFERENCES "CashSession"("id") ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE "SaleLine" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "saleId" TEXT NOT NULL,
  "productId" TEXT NOT NULL,
  "sku" TEXT NOT NULL,
  "productName" TEXT NOT NULL,
  "qty" INTEGER NOT NULL,
  "priceCents" INTEGER NOT NULL,
  "totalCents" INTEGER NOT NULL,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("saleId", "businessId") REFERENCES "Sale"("id", "businessId") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("productId", "businessId") REFERENCES "Product"("id", "businessId") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE "SaleReturn" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "saleFolio" TEXT NOT NULL,
  "reason" TEXT NOT NULL,
  "amountCents" INTEGER NOT NULL,
  "status" TEXT NOT NULL,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "cashier" TEXT NOT NULL,
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "AuditCount" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "location" TEXT NOT NULL,
  "countedBy" TEXT NOT NULL,
  "variance" INTEGER NOT NULL,
  "status" TEXT NOT NULL,
  "countedAt" DATETIME NOT NULL,
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "OutboxEvent" (
  "id" TEXT NOT NULL PRIMARY KEY,
  "businessId" TEXT NOT NULL,
  "topic" TEXT NOT NULL,
  "aggregateId" TEXT NOT NULL,
  "payloadJson" TEXT NOT NULL,
  "status" TEXT NOT NULL,
  "attempts" INTEGER NOT NULL DEFAULT 0,
  "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "sentAt" DATETIME,
  "lastError" TEXT,
  FOREIGN KEY ("businessId") REFERENCES "Business"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX "idx_store_business" ON "Store"("businessId");
CREATE INDEX "idx_terminal_business_store" ON "Terminal"("businessId", "storeId");
CREATE INDEX "idx_taxrate_business_default" ON "TaxRate"("businessId", "isDefault");
CREATE INDEX "idx_pricelist_business_default" ON "PriceList"("businessId", "isDefault");
CREATE INDEX "idx_product_business_active" ON "Product"("businessId", "isActive");
CREATE INDEX "idx_product_business_category" ON "Product"("businessId", "category");
CREATE INDEX "idx_barcode_business_product" ON "Barcode"("businessId", "productId");
CREATE INDEX "idx_pricelistitem_business_product" ON "PriceListItem"("businessId", "productId");
CREATE INDEX "idx_stocksnapshot_business_days" ON "StockSnapshot"("businessId", "daysCover");
CREATE INDEX "idx_stockmovement_business_product_created" ON "StockMovement"("businessId", "productId", "createdAt");
CREATE INDEX "idx_supplier_business_status" ON "Supplier"("businessId", "status");
CREATE INDEX "idx_purchaseorder_business_status_created" ON "PurchaseOrder"("businessId", "status", "createdAt");
CREATE INDEX "idx_purchaseorderline_business_order" ON "PurchaseOrderLine"("businessId", "purchaseOrderId");
CREATE INDEX "idx_purchaseorderline_business_product" ON "PurchaseOrderLine"("businessId", "productId");
CREATE INDEX "idx_goodsreceipt_business_status_received" ON "GoodsReceipt"("businessId", "status", "receivedAt");
CREATE INDEX "idx_goodsreceiptline_business_receipt" ON "GoodsReceiptLine"("businessId", "goodsReceiptId");
CREATE INDEX "idx_goodsreceiptline_business_product" ON "GoodsReceiptLine"("businessId", "productId");
CREATE INDEX "idx_replenishmentsignal_business_priority_created" ON "ReplenishmentSignal"("businessId", "priority", "createdAt");
CREATE INDEX "idx_cashsession_business_terminal_status" ON "CashSession"("businessId", "terminalId", "status");
CREATE INDEX "idx_cashmovement_business_session_created" ON "CashMovement"("businessId", "cashSessionId", "createdAt");
CREATE INDEX "idx_sale_business_created" ON "Sale"("businessId", "createdAt");
CREATE INDEX "idx_saleline_business_sale" ON "SaleLine"("businessId", "saleId");
CREATE INDEX "idx_saleline_business_product" ON "SaleLine"("businessId", "productId");
CREATE INDEX "idx_salereturn_business_created" ON "SaleReturn"("businessId", "createdAt");
CREATE INDEX "idx_auditcount_business_status_counted" ON "AuditCount"("businessId", "status", "countedAt");
CREATE INDEX "idx_outboxevent_business_status_created" ON "OutboxEvent"("businessId", "status", "createdAt");
CREATE INDEX "idx_outboxevent_business_topic" ON "OutboxEvent"("businessId", "topic");

CREATE UNIQUE INDEX "uq_pricelist_single_default_per_business"
  ON "PriceList"("businessId")
  WHERE "isDefault" = 1;

CREATE UNIQUE INDEX "uq_taxrate_single_default_per_business"
  ON "TaxRate"("businessId")
  WHERE "isDefault" = 1;

CREATE UNIQUE INDEX "uq_cashsession_single_open_per_terminal"
  ON "CashSession"("businessId", "terminalId")
  WHERE "status" = 'OPEN';

CREATE TRIGGER "trg_purchase_order_line_ai"
AFTER INSERT ON "PurchaseOrderLine"
BEGIN
  UPDATE "PurchaseOrder"
  SET
    "subtotalCents" = (SELECT COALESCE(SUM("lineSubtotalCents"), 0) FROM "PurchaseOrderLine" WHERE "purchaseOrderId" = NEW."purchaseOrderId"),
    "taxCents" = (SELECT COALESCE(SUM("lineTaxCents"), 0) FROM "PurchaseOrderLine" WHERE "purchaseOrderId" = NEW."purchaseOrderId"),
    "totalCents" = (SELECT COALESCE(SUM("lineTotalCents"), 0) FROM "PurchaseOrderLine" WHERE "purchaseOrderId" = NEW."purchaseOrderId")
  WHERE "id" = NEW."purchaseOrderId";
END;

CREATE TRIGGER "trg_purchase_order_line_au"
AFTER UPDATE ON "PurchaseOrderLine"
BEGIN
  UPDATE "PurchaseOrder"
  SET
    "subtotalCents" = (SELECT COALESCE(SUM("lineSubtotalCents"), 0) FROM "PurchaseOrderLine" WHERE "purchaseOrderId" = OLD."purchaseOrderId"),
    "taxCents" = (SELECT COALESCE(SUM("lineTaxCents"), 0) FROM "PurchaseOrderLine" WHERE "purchaseOrderId" = OLD."purchaseOrderId"),
    "totalCents" = (SELECT COALESCE(SUM("lineTotalCents"), 0) FROM "PurchaseOrderLine" WHERE "purchaseOrderId" = OLD."purchaseOrderId")
  WHERE "id" = OLD."purchaseOrderId";

  UPDATE "PurchaseOrder"
  SET
    "subtotalCents" = (SELECT COALESCE(SUM("lineSubtotalCents"), 0) FROM "PurchaseOrderLine" WHERE "purchaseOrderId" = NEW."purchaseOrderId"),
    "taxCents" = (SELECT COALESCE(SUM("lineTaxCents"), 0) FROM "PurchaseOrderLine" WHERE "purchaseOrderId" = NEW."purchaseOrderId"),
    "totalCents" = (SELECT COALESCE(SUM("lineTotalCents"), 0) FROM "PurchaseOrderLine" WHERE "purchaseOrderId" = NEW."purchaseOrderId")
  WHERE "id" = NEW."purchaseOrderId";
END;

CREATE TRIGGER "trg_purchase_order_line_ad"
AFTER DELETE ON "PurchaseOrderLine"
BEGIN
  UPDATE "PurchaseOrder"
  SET
    "subtotalCents" = (SELECT COALESCE(SUM("lineSubtotalCents"), 0) FROM "PurchaseOrderLine" WHERE "purchaseOrderId" = OLD."purchaseOrderId"),
    "taxCents" = (SELECT COALESCE(SUM("lineTaxCents"), 0) FROM "PurchaseOrderLine" WHERE "purchaseOrderId" = OLD."purchaseOrderId"),
    "totalCents" = (SELECT COALESCE(SUM("lineTotalCents"), 0) FROM "PurchaseOrderLine" WHERE "purchaseOrderId" = OLD."purchaseOrderId")
  WHERE "id" = OLD."purchaseOrderId";
END;

CREATE TRIGGER "trg_purchase_order_totals_guard"
BEFORE UPDATE OF "subtotalCents", "taxCents", "totalCents" ON "PurchaseOrder"
WHEN
  (SELECT COUNT(*) FROM "PurchaseOrderLine" WHERE "purchaseOrderId" = NEW."id") > 0
  AND (
    NEW."subtotalCents" != (SELECT COALESCE(SUM("lineSubtotalCents"), 0) FROM "PurchaseOrderLine" WHERE "purchaseOrderId" = NEW."id")
    OR NEW."taxCents" != (SELECT COALESCE(SUM("lineTaxCents"), 0) FROM "PurchaseOrderLine" WHERE "purchaseOrderId" = NEW."id")
    OR NEW."totalCents" != (SELECT COALESCE(SUM("lineTotalCents"), 0) FROM "PurchaseOrderLine" WHERE "purchaseOrderId" = NEW."id")
  )
BEGIN
  SELECT RAISE(ABORT, 'PurchaseOrder totals must match line sums');
END;

CREATE TRIGGER "trg_goods_receipt_line_ai"
AFTER INSERT ON "GoodsReceiptLine"
BEGIN
  UPDATE "GoodsReceipt"
  SET
    "subtotalCents" = (SELECT COALESCE(SUM("lineSubtotalCents"), 0) FROM "GoodsReceiptLine" WHERE "goodsReceiptId" = NEW."goodsReceiptId"),
    "taxCents" = (SELECT COALESCE(SUM("lineTaxCents"), 0) FROM "GoodsReceiptLine" WHERE "goodsReceiptId" = NEW."goodsReceiptId"),
    "totalCents" = (SELECT COALESCE(SUM("lineTotalCents"), 0) FROM "GoodsReceiptLine" WHERE "goodsReceiptId" = NEW."goodsReceiptId")
  WHERE "id" = NEW."goodsReceiptId";
END;

CREATE TRIGGER "trg_goods_receipt_line_au"
AFTER UPDATE ON "GoodsReceiptLine"
BEGIN
  UPDATE "GoodsReceipt"
  SET
    "subtotalCents" = (SELECT COALESCE(SUM("lineSubtotalCents"), 0) FROM "GoodsReceiptLine" WHERE "goodsReceiptId" = OLD."goodsReceiptId"),
    "taxCents" = (SELECT COALESCE(SUM("lineTaxCents"), 0) FROM "GoodsReceiptLine" WHERE "goodsReceiptId" = OLD."goodsReceiptId"),
    "totalCents" = (SELECT COALESCE(SUM("lineTotalCents"), 0) FROM "GoodsReceiptLine" WHERE "goodsReceiptId" = OLD."goodsReceiptId")
  WHERE "id" = OLD."goodsReceiptId";

  UPDATE "GoodsReceipt"
  SET
    "subtotalCents" = (SELECT COALESCE(SUM("lineSubtotalCents"), 0) FROM "GoodsReceiptLine" WHERE "goodsReceiptId" = NEW."goodsReceiptId"),
    "taxCents" = (SELECT COALESCE(SUM("lineTaxCents"), 0) FROM "GoodsReceiptLine" WHERE "goodsReceiptId" = NEW."goodsReceiptId"),
    "totalCents" = (SELECT COALESCE(SUM("lineTotalCents"), 0) FROM "GoodsReceiptLine" WHERE "goodsReceiptId" = NEW."goodsReceiptId")
  WHERE "id" = NEW."goodsReceiptId";
END;

CREATE TRIGGER "trg_goods_receipt_line_ad"
AFTER DELETE ON "GoodsReceiptLine"
BEGIN
  UPDATE "GoodsReceipt"
  SET
    "subtotalCents" = (SELECT COALESCE(SUM("lineSubtotalCents"), 0) FROM "GoodsReceiptLine" WHERE "goodsReceiptId" = OLD."goodsReceiptId"),
    "taxCents" = (SELECT COALESCE(SUM("lineTaxCents"), 0) FROM "GoodsReceiptLine" WHERE "goodsReceiptId" = OLD."goodsReceiptId"),
    "totalCents" = (SELECT COALESCE(SUM("lineTotalCents"), 0) FROM "GoodsReceiptLine" WHERE "goodsReceiptId" = OLD."goodsReceiptId")
  WHERE "id" = OLD."goodsReceiptId";
END;

CREATE TRIGGER "trg_goods_receipt_totals_guard"
BEFORE UPDATE OF "subtotalCents", "taxCents", "totalCents" ON "GoodsReceipt"
WHEN
  (SELECT COUNT(*) FROM "GoodsReceiptLine" WHERE "goodsReceiptId" = NEW."id") > 0
  AND (
    NEW."subtotalCents" != (SELECT COALESCE(SUM("lineSubtotalCents"), 0) FROM "GoodsReceiptLine" WHERE "goodsReceiptId" = NEW."id")
    OR NEW."taxCents" != (SELECT COALESCE(SUM("lineTaxCents"), 0) FROM "GoodsReceiptLine" WHERE "goodsReceiptId" = NEW."id")
    OR NEW."totalCents" != (SELECT COALESCE(SUM("lineTotalCents"), 0) FROM "GoodsReceiptLine" WHERE "goodsReceiptId" = NEW."id")
  )
BEGIN
  SELECT RAISE(ABORT, 'GoodsReceipt totals must match line sums');
END;
