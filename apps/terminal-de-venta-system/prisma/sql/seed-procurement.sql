-- Canonical procurement seed excerpt.
-- Guarded by apps/terminal-de-venta-system/tooling/scripts/validate_prisma_canonical.py.

INSERT INTO "PurchaseOrder" (
  "id", "businessId", "supplierId", "folio", "status", "createdAt", "expectedAt",
  "subtotalCents", "taxCents", "totalCents", "updatedAt"
) VALUES (
  'po_demo_001', 'biz_hitech_default', 'sup_bebidas_centro', 'PO-240418-001', 'ordered',
  '2026-04-18T09:00:00.000Z', '2026-04-20T09:00:00.000Z', 56400, 9024, 65424,
  CURRENT_TIMESTAMP
);

INSERT INTO "PurchaseOrderLine" (
  "id", "businessId", "purchaseOrderId", "productId", "sku", "name", "qtyOrdered",
  "unitCostCents", "lineSubtotalCents", "lineTaxCents", "lineTotalCents", "createdAt"
) VALUES
  (
    'pol_demo_001', 'biz_hitech_default', 'po_demo_001', 'prd_ref_355', 'REF-355ML',
    'Refresco 355 ml', 24, 1250, 30000, 4800, 34800, CURRENT_TIMESTAMP
  ),
  (
    'pol_demo_002', 'biz_hitech_default', 'po_demo_001', 'prd_pap_adobo', 'PAP-ADOBO',
    'Papas adobadas', 12, 2200, 26400, 4224, 30624, CURRENT_TIMESTAMP
  );

INSERT INTO "GoodsReceipt" (
  "id", "businessId", "purchaseOrderId", "supplierId", "folio", "status", "receivedAt",
  "subtotalCents", "taxCents", "totalCents", "updatedAt"
) VALUES (
  'gr_demo_001', 'biz_hitech_default', 'po_demo_001', 'sup_bebidas_centro',
  'GR-240418-001', 'posted', '2026-04-19T10:30:00.000Z', 47000, 7520, 54520,
  CURRENT_TIMESTAMP
);

INSERT INTO "GoodsReceiptLine" (
  "id", "businessId", "goodsReceiptId", "purchaseOrderLineId", "productId", "sku", "name",
  "qtyReceived", "unitCostCents", "lineSubtotalCents", "lineTaxCents", "lineTotalCents", "createdAt"
) VALUES
  (
    'grl_demo_001', 'biz_hitech_default', 'gr_demo_001', 'pol_demo_001', 'prd_ref_355',
    'REF-355ML', 'Refresco 355 ml', 20, 1250, 25000, 4000, 29000, CURRENT_TIMESTAMP
  ),
  (
    'grl_demo_002', 'biz_hitech_default', 'gr_demo_001', 'pol_demo_002', 'prd_pap_adobo',
    'PAP-ADOBO', 'Papas adobadas', 10, 2200, 22000, 3520, 25520, CURRENT_TIMESTAMP
  );
