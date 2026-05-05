import type {
  ConfirmReceivingInput,
  CreateSuggestedOrderInput,
  RegisterSupplierPaymentInput,
  SmartPurchaseRecommendation,
  SupplierAccount,
  SupplierActionResult,
  SupplierAuditEvent,
  SupplierPayable,
  SupplierProductLink,
  SupplierPurchaseOrder,
  SupplierReceivingReceipt
} from "./types";

export interface SupplierRepositoryReadModel {
  suppliers: SupplierAccount[];
  supplierProductLinks: SupplierProductLink[];
  recommendations: SmartPurchaseRecommendation[];
  orders: SupplierPurchaseOrder[];
  receivingReceipts: SupplierReceivingReceipt[];
  payables: SupplierPayable[];
  auditEvents: SupplierAuditEvent[];
}

export interface SupplierRepositoryQuery {
  supplierId?: string;
  status?: string;
  from?: string;
  to?: string;
  limit?: number;
}

export interface SupplierRepositoryMutationContext {
  requestId: string;
  actorId: string;
  reason: string;
  source: "pc.suppliers" | "pc.smart_purchase" | "pc.receiving" | "pc.payables";
}

export interface SupplierRepository {
  listSuppliers(query?: SupplierRepositoryQuery): Promise<SupplierAccount[]>;
  listSupplierProductLinks(query?: SupplierRepositoryQuery): Promise<SupplierProductLink[]>;
  listRecommendations(query?: SupplierRepositoryQuery): Promise<SmartPurchaseRecommendation[]>;
  listOrders(query?: SupplierRepositoryQuery): Promise<SupplierPurchaseOrder[]>;
  listReceipts(query?: SupplierRepositoryQuery): Promise<SupplierReceivingReceipt[]>;
  listPayables(query?: SupplierRepositoryQuery): Promise<SupplierPayable[]>;
  listAuditEvents(query?: SupplierRepositoryQuery): Promise<SupplierAuditEvent[]>;
  getReadModel(): Promise<SupplierRepositoryReadModel>;
  createSuggestedOrder(input: CreateSuggestedOrderInput, context: SupplierRepositoryMutationContext): Promise<SupplierActionResult<{ order: SupplierPurchaseOrder }>>;
  confirmReceiving(input: ConfirmReceivingInput, context: SupplierRepositoryMutationContext): Promise<SupplierActionResult<{ receipt: SupplierReceivingReceipt }>>;
  registerPayment(input: RegisterSupplierPaymentInput, context: SupplierRepositoryMutationContext): Promise<SupplierActionResult<{ payable: SupplierPayable }>>;
  appendAuditEvents(events: SupplierAuditEvent[], context: SupplierRepositoryMutationContext): Promise<void>;
}

export function applyQueryLimit<T>(items: T[], query?: SupplierRepositoryQuery): T[] {
  const limit = query?.limit && query.limit > 0 ? Math.min(query.limit, 250) : items.length;
  return items.slice(0, limit);
}

export function filterBySupplier<T extends { supplierId?: string }>(items: T[], query?: SupplierRepositoryQuery): T[] {
  if (!query?.supplierId) return items;
  return items.filter((item) => item.supplierId === query.supplierId);
}

export function makeMutationContext(source: SupplierRepositoryMutationContext["source"], actorId: string, reason: string): SupplierRepositoryMutationContext {
  return { requestId: `req_${source}_${Date.now()}`, actorId, reason, source };
}
