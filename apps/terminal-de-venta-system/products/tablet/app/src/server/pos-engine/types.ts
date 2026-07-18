export type PosCartLineInput = {
  productId?: string;
  sku?: string;
  barcode?: string;
  qty: number;
  modifierSelections?: PosModifierSelectionInput[];
};

export type PosModifierSelectionInput = {
  modifierGroupId: string;
  optionIds: string[];
};

export type PosModifierSelectionSnapshot = {
  modifierGroupId: string;
  groupName: string;
  options: Array<{ optionId: string; name: string; priceDeltaCents: number }>;
};

export type PosPaymentMethod = "cash" | "card" | "transfer";
export type PosSalePaymentMethod = PosPaymentMethod | "mixed";

export type SalePaymentTenderInput = {
  tenderType: PosPaymentMethod;
  amountCents: number;
  reference?: string | null;
};

export type SalePaymentTenderResult = SalePaymentTenderInput & {
  id: string;
  recordedAt: Date;
};

export type CompleteLocalSaleInput = {
  businessId?: string;
  terminalId?: string;
  cashSessionId?: string | null;
  customerId?: string | null;
  cashier?: string;
  location?: string;
  allowNegativeStock?: boolean;
  lowStockThreshold?: number;
  lines: PosCartLineInput[];
  clientRequestId?: string;
  paymentMethod?: PosSalePaymentMethod;
  cashReceivedCents?: number | null;
  changeCents?: number | null;
  paymentTenders?: SalePaymentTenderInput[];
};

export type PosResolvedProduct = {
  id: string;
  businessId: string;
  sku: string;
  name: string;
  category: string;
  priceCents: number;
  stockOnHand: number;
  isActive: boolean;
};

export type PosSaleLineResult = {
  id: string;
  productId: string;
  sku: string;
  productName: string;
  qty: number;
  priceCents: number;
  totalCents: number;
  stockBefore: number;
  stockAfter: number;
  modifierSelections: PosModifierSelectionSnapshot[];
};

export type PosEngineEvent = {
  eventId: string;
  source: string;
  subject: string;
  eventType: string;
  topic: string;
  eventVersion: string;
  schemaVersion: string;
  tenantId: string;
  customerId?: string;
  businessId: string;
  storeId: string;
  terminalId: string;
  deviceId: string;
  actorId: string;
  aggregateId: string;
  originRecordId: string;
  idempotencyKey: string;
  sequence: number;
  correlationId: string;
  causationId: string;
  traceId: string;
  occurredAt: string;
  capturedAt: string;
  payloadHash: string;
  payload: Record<string, unknown>;
};

export type CompleteLocalSaleResult = {
  saleId: string;
  folio: string;
  businessId: string;
  terminalId: string;
  cashSessionId: string | null;
  customerId: string | null;
  clientRequestId: string | null;
  cashier: string;
  subtotalCents: number;
  discountCents: number;
  totalCents: number;
  paymentMethod: PosSalePaymentMethod;
  cashReceivedCents: number | null;
  changeCents: number;
  paymentTenders: SalePaymentTenderResult[];
  status: "COMPLETED";
  createdAt: Date;
  completedAt: Date | null;
  lines: PosSaleLineResult[];
  events: PosEngineEvent[];
};

export type PosEngineRepository = {
  completeLocalSale(input: CompleteLocalSaleInput): Promise<CompleteLocalSaleResult>;
};
