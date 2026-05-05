export type PosCartLineInput = {
  productId?: string;
  sku?: string;
  barcode?: string;
  qty: number;
};

export type PosPaymentMethod = "cash" | "card" | "transfer";

export type CompleteLocalSaleInput = {
  businessId?: string;
  terminalId?: string;
  cashSessionId?: string | null;
  cashier?: string;
  location?: string;
  allowNegativeStock?: boolean;
  lowStockThreshold?: number;
  lines: PosCartLineInput[];
  clientRequestId?: string;
  paymentMethod?: PosPaymentMethod;
  cashReceivedCents?: number | null;
  changeCents?: number | null;
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
};

export type PosEngineEvent = {
  eventId: string;
  topic: string;
  businessId: string;
  terminalId: string;
  actorId: string;
  source: string;
  occurredAt: string;
  aggregateId: string;
  schemaVersion: string;
  payload: Record<string, unknown>;
};

export type CompleteLocalSaleResult = {
  saleId: string;
  folio: string;
  businessId: string;
  terminalId: string;
  cashSessionId: string | null;
  cashier: string;
  totalCents: number;
  paymentMethod: PosPaymentMethod;
  cashReceivedCents: number | null;
  changeCents: number;
  status: "COMPLETED";
  createdAt: Date;
  lines: PosSaleLineResult[];
  events: PosEngineEvent[];
};

export type PosEngineRepository = {
  completeLocalSale(input: CompleteLocalSaleInput): Promise<CompleteLocalSaleResult>;
};
