import { confirmSupplierReceiving, createSuggestedOrderFromRecommendation, registerSupplierPayment } from "./lifecycle-engine";
import { buildSmartPurchaseOutput } from "./smart-purchase-engine";
import { receivingQueue, supplierAccounts, supplierLifecycleFixtures, supplierOrders, supplierPayables, supplierProductLinks } from "./fixtures";
import { applyQueryLimit, filterBySupplier, type SupplierRepository, type SupplierRepositoryMutationContext, type SupplierRepositoryQuery, type SupplierRepositoryReadModel } from "./repository-contract";
import type { ConfirmReceivingInput, CreateSuggestedOrderInput, RegisterSupplierPaymentInput, SmartPurchaseRecommendation, SupplierAccount, SupplierActionResult, SupplierAuditEvent, SupplierPayable, SupplierProductLink, SupplierPurchaseOrder, SupplierReceivingReceipt } from "./types";

export class InMemorySupplierRepository implements SupplierRepository {
  private suppliers: SupplierAccount[] = [...supplierAccounts];
  private productLinks: SupplierProductLink[] = [...supplierProductLinks];
  private orders: SupplierPurchaseOrder[] = [...supplierOrders];
  private receipts: SupplierReceivingReceipt[] = [...receivingQueue];
  private payables: SupplierPayable[] = [...supplierPayables];
  private auditEvents: SupplierAuditEvent[] = [];
  private recommendations: SmartPurchaseRecommendation[];

  constructor(now = "2026-05-02T16:30:00.000Z") {
    this.recommendations = buildSmartPurchaseOutput({ now, availableCashCents: supplierLifecycleFixtures.cashPolicy.availableCashCents, reserveCashCents: supplierLifecycleFixtures.cashPolicy.reserveCashCents, suppliers: this.suppliers, productLinks: this.productLinks, payables: this.payables }).recommendations;
  }

  async listSuppliers(query?: SupplierRepositoryQuery): Promise<SupplierAccount[]> {
    let items = [...this.suppliers];
    if (query?.status) items = items.filter((supplier) => supplier.status === query.status);
    return applyQueryLimit(items, query);
  }

  async listSupplierProductLinks(query?: SupplierRepositoryQuery): Promise<SupplierProductLink[]> {
    return applyQueryLimit(filterBySupplier([...this.productLinks], query), query);
  }

  async listRecommendations(query?: SupplierRepositoryQuery): Promise<SmartPurchaseRecommendation[]> {
    return applyQueryLimit(filterBySupplier([...this.recommendations], query), query);
  }

  async listOrders(query?: SupplierRepositoryQuery): Promise<SupplierPurchaseOrder[]> {
    let items = filterBySupplier([...this.orders], query);
    if (query?.status) items = items.filter((order) => order.status === query.status);
    return applyQueryLimit(items, query);
  }

  async listReceipts(query?: SupplierRepositoryQuery): Promise<SupplierReceivingReceipt[]> {
    let items = filterBySupplier([...this.receipts], query);
    if (query?.status) items = items.filter((receipt) => receipt.status === query.status);
    return applyQueryLimit(items, query);
  }

  async listPayables(query?: SupplierRepositoryQuery): Promise<SupplierPayable[]> {
    let items = filterBySupplier([...this.payables], query);
    if (query?.status) items = items.filter((payable) => payable.status === query.status);
    return applyQueryLimit(items, query);
  }

  async listAuditEvents(query?: SupplierRepositoryQuery): Promise<SupplierAuditEvent[]> {
    let items = filterBySupplier([...this.auditEvents], query);
    if (query?.from) items = items.filter((event) => event.createdAt >= query.from!);
    if (query?.to) items = items.filter((event) => event.createdAt <= query.to!);
    return applyQueryLimit(items, query);
  }

  async getReadModel(): Promise<SupplierRepositoryReadModel> {
    return { suppliers: [...this.suppliers], supplierProductLinks: [...this.productLinks], recommendations: [...this.recommendations], orders: [...this.orders], receivingReceipts: [...this.receipts], payables: [...this.payables], auditEvents: [...this.auditEvents] };
  }

  async createSuggestedOrder(input: CreateSuggestedOrderInput, context: SupplierRepositoryMutationContext): Promise<SupplierActionResult<{ order: SupplierPurchaseOrder }>> {
    const snapshot = this.snapshot();
    const result = createSuggestedOrderFromRecommendation(input, snapshot);
    if (result.ok && result.data?.order) this.orders = [result.data.order, ...this.orders];
    await this.appendAuditEvents(result.auditEvents, context);
    return { ...result, data: result.data ? { order: result.data.order } : undefined };
  }

  async confirmReceiving(input: ConfirmReceivingInput, context: SupplierRepositoryMutationContext): Promise<SupplierActionResult<{ receipt: SupplierReceivingReceipt }>> {
    const result = confirmSupplierReceiving(input, this.snapshot());
    if (result.ok && result.data?.receipt) {
      this.receipts = [result.data.receipt, ...this.receipts.filter((receipt) => receipt.id !== result.data?.receipt.id)];
      if (result.data.payable) this.payables = [result.data.payable, ...this.payables];
    }
    await this.appendAuditEvents(result.auditEvents, context);
    return { ...result, data: result.data ? { receipt: result.data.receipt } : undefined };
  }

  async registerPayment(input: RegisterSupplierPaymentInput, context: SupplierRepositoryMutationContext): Promise<SupplierActionResult<{ payable: SupplierPayable }>> {
    const result = registerSupplierPayment(input, this.snapshot());
    if (result.ok && result.data?.payable) this.payables = [result.data.payable, ...this.payables.filter((payable) => payable.id !== result.data?.payable.id)];
    await this.appendAuditEvents(result.auditEvents, context);
    return { ...result, data: result.data ? { payable: result.data.payable } : undefined };
  }

  async appendAuditEvents(events: SupplierAuditEvent[], _context: SupplierRepositoryMutationContext): Promise<void> {
    this.auditEvents = [...events, ...this.auditEvents];
  }

  private snapshot() {
    return { generatedAt: "2026-05-02T16:30:00.000Z", suppliers: this.suppliers, productLinks: this.productLinks, signals: [], recommendations: this.recommendations, openOrders: this.orders, receivingQueue: this.receipts, payables: this.payables, lifecycle: { generatedAt: "2026-05-02T16:30:00.000Z", readiness: [], calendar: [], orderWorkflow: [], movementPreview: [], payablePlan: [], auditEvents: this.auditEvents, surfaceSignals: [], counters: { readyGates: 0, warningGates: 0, blockedGates: 0, calendarEvents: 0, ordersNeedingAction: 0, receivingsWithDifferences: 0, auditEvents: this.auditEvents.length } } };
  }
}
