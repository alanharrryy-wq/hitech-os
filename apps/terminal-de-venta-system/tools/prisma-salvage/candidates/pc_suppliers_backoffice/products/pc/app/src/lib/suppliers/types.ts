export type MoneyCents = number;
export type IsoDate = string;

export type SupplierStatus = "active" | "paused" | "blocked";
export type SupplierCategory = "bebidas" | "snacks" | "lacteos" | "abarrotes" | "limpieza" | "farmacia" | "panaderia" | "otros";
export type PaymentCondition = "cash" | "credit_7" | "credit_15" | "credit_30" | "consignment";
export type Weekday = "lunes" | "martes" | "miercoles" | "jueves" | "viernes" | "sabado" | "domingo";

export type PurchaseRecommendationPriority = "critical" | "high" | "safe" | "wait" | "blocked" | "configure";
export type PurchaseRecommendationAction = "create_order" | "simulate" | "wait" | "configure_supplier" | "review_cost" | "block_purchase";
export type PurchaseOrderStatus = "draft" | "suggested" | "approved" | "sent" | "partially_received" | "received" | "cancelled" | "closed";
export type ReceivingStatus = "pending" | "capturing" | "complete" | "with_differences" | "cancelled" | "reverted" | "needs_review";
export type PayableStatus = "scheduled" | "due_soon" | "overdue" | "paid" | "disputed";
export type CashImpact = "safe" | "careful" | "tight" | "blocked";

export interface SupplierContact {
  id: string;
  name: string;
  role: string;
  phone?: string;
  whatsapp?: string;
  email?: string;
  isPrimary: boolean;
}

export interface SupplierVisitRule {
  cadence: "weekly" | "biweekly" | "monthly" | "on_demand";
  weekdays: Weekday[];
  approximateTime: string;
  orderCutoffWeekday: Weekday;
  orderCutoffTime: string;
  leadTimeDays: number;
  nextVisitDate: IsoDate;
  nextOrderCutoff: IsoDate;
}

export interface SupplierCommercialTerms {
  paymentCondition: PaymentCondition;
  creditDays: number;
  minimumOrderCents: MoneyCents;
  creditLimitCents: MoneyCents;
  usualDiscountBps: number;
  shippingCostCents: MoneyCents;
  returnPolicy: string;
}

export interface SupplierProductLink {
  id: string;
  productId: string;
  sku: string;
  name: string;
  category: string;
  supplierId: string;
  supplierName: string;
  isPrimary: boolean;
  packageSize: number;
  minPurchaseUnits: number;
  recentCostCents: MoneyCents;
  currentStockUnits: number;
  lowStockThresholdUnits: number;
  averageDailySalesUnits: number;
  grossMarginBps: number;
  lastCostUpdateAt: IsoDate;
}

export interface SupplierAccount {
  id: string;
  legalName?: string;
  tradeName: string;
  category: SupplierCategory;
  status: SupplierStatus;
  notes?: string;
  contacts: SupplierContact[];
  visitRule?: SupplierVisitRule;
  terms: SupplierCommercialTerms;
  createdAt: IsoDate;
  updatedAt: IsoDate;
}

export interface SmartPurchaseSignal {
  id: string;
  supplierId?: string;
  productId: string;
  sku: string;
  productName: string;
  signal: "stockout_risk" | "low_coverage" | "supplier_soon" | "cash_pressure" | "slow_rotation" | "missing_supplier" | "cost_stale" | "promotion";
  severity: "critical" | "high" | "medium" | "low";
  evidence: string;
  detectedAt: IsoDate;
}

export interface SmartPurchaseLine {
  id: string;
  productId: string;
  sku: string;
  productName: string;
  supplierId?: string;
  supplierName?: string;
  suggestedUnits: number;
  packageSize: number;
  suggestedPackages: number;
  currentStockUnits: number;
  averageDailySalesUnits: number;
  coverageDaysBefore: number;
  coverageDaysAfter: number;
  unitCostCents: MoneyCents;
  estimatedCostCents: MoneyCents;
  marginBps: number;
  priority: PurchaseRecommendationPriority;
  reasons: string[];
  riskIfSkipped: string;
  riskIfOverbought: string;
  action: PurchaseRecommendationAction;
}

export interface SmartPurchaseRecommendation {
  id: string;
  supplierId?: string;
  supplierName: string;
  priority: PurchaseRecommendationPriority;
  action: PurchaseRecommendationAction;
  cashImpact: CashImpact;
  title: string;
  summary: string;
  generatedAt: IsoDate;
  idealOrderDate: IsoDate;
  expectedReceptionDate: IsoDate;
  expectedPaymentDate: IsoDate;
  estimatedTotalCents: MoneyCents;
  safeBudgetCents: MoneyCents;
  cashAfterPurchaseCents: MoneyCents;
  lines: SmartPurchaseLine[];
  reasons: string[];
  auditRequired: boolean;
  blockedReason?: string;
}

export interface PurchaseSimulationInput {
  recommendationId: string;
  budgetCents: MoneyCents;
  excludedLineIds: string[];
  quantityOverrides: Record<string, number>;
}

export interface PurchaseSimulationResult {
  recommendationId: string;
  includedLines: SmartPurchaseLine[];
  excludedLines: SmartPurchaseLine[];
  originalTotalCents: MoneyCents;
  simulatedTotalCents: MoneyCents;
  cashAfterPurchaseCents: MoneyCents;
  cashImpact: CashImpact;
  warnings: string[];
  coverageSummary: string;
  canCreateOrder: boolean;
}

export interface SupplierDashboardSnapshot {
  generatedAt: IsoDate;
  suppliers: SupplierAccount[];
  productLinks: SupplierProductLink[];
  signals: SmartPurchaseSignal[];
  recommendations: SmartPurchaseRecommendation[];
  openOrders: SupplierPurchaseOrder[];
  receivingQueue: SupplierReceivingReceipt[];
  payables: SupplierPayable[];
  lifecycle: SupplierLifecycleSnapshot;
  inventoryBridge?: SupplierInventoryBridgeSnapshot;
}

export interface SupplierPurchaseOrderLine {
  id: string;
  productId: string;
  sku: string;
  name: string;
  orderedUnits: number;
  receivedUnits: number;
  unitCostCents: MoneyCents;
  expectedTotalCents: MoneyCents;
}

export interface SupplierPurchaseOrder {
  id: string;
  folio: string;
  supplierId: string;
  supplierName: string;
  source: "manual" | "smart_purchase" | "calendar" | "critical_product";
  status: PurchaseOrderStatus;
  createdAt: IsoDate;
  expectedReceptionDate: IsoDate;
  expectedPaymentDate: IsoDate;
  totalCents: MoneyCents;
  lines: SupplierPurchaseOrderLine[];
  auditTrail: string[];
}

export interface SupplierReceivingReceipt {
  id: string;
  orderId?: string;
  supplierId: string;
  supplierName: string;
  status: ReceivingStatus;
  expectedAt: IsoDate;
  receivedAt?: IsoDate;
  differences: SupplierReceivingDifference[];
}

export interface SupplierReceivingDifference {
  productId: string;
  sku: string;
  name: string;
  expectedUnits: number;
  receivedUnits: number;
  reason: "missing" | "extra" | "wrong_product" | "cost_changed" | "damaged" | "short_expiry" | "partial" | "capture_error" | "other";
  note: string;
}

export interface SupplierPayable {
  id: string;
  supplierId: string;
  supplierName: string;
  orderId?: string;
  dueDate: IsoDate;
  amountCents: MoneyCents;
  status: PayableStatus;
  notes?: string;
}

export type SupplierLifecycleEventTopic =
  | "purchase_order.created"
  | "purchase_order.suggested"
  | "purchase_order.approved"
  | "purchase_order.sent"
  | "purchase_order.cancelled"
  | "purchase_order.converted_from_recommendation"
  | "receiving.completed"
  | "receiving.completed_with_differences"
  | "receiving.reverted"
  | "stock.increased_from_receiving"
  | "stock.reverted_from_receiving"
  | "supplier_payable.created"
  | "supplier_payable.partial_paid"
  | "supplier_payable.paid"
  | "smart_purchase.recommendation.simulated"
  | "smart_purchase.recommendation.converted_to_order"
  | "smart_purchase.recommendation.rejected";

export interface SupplierActor {
  id: string;
  name: string;
  role: "Cajero" | "Encargado" | "Administrador" | "Dueño" | "Auditor" | string;
}

export interface SupplierAuditEvent {
  id: string;
  topic: SupplierLifecycleEventTopic;
  actor: SupplierActor;
  entityType: "supplier" | "purchase_order" | "receiving" | "payable" | "smart_purchase" | "stock_movement";
  entityId: string;
  supplierId?: string;
  supplierName?: string;
  before?: Record<string, unknown>;
  after?: Record<string, unknown>;
  reason: string;
  createdAt: IsoDate;
  source: "pc.suppliers" | "pc.smart_purchase" | "pc.receiving" | "pc.payables";
  visibleSummary: string;
  requiresReview: boolean;
}

export interface SupplierCalendarEvent {
  id: string;
  supplierId: string;
  supplierName: string;
  kind: "visit" | "order_cutoff" | "expected_receiving" | "payment_due" | "recommendation";
  title: string;
  startsAt: IsoDate;
  severity: "critical" | "high" | "medium" | "low";
  actionLabel: string;
  actionHref: string;
}

export interface SupplierReadinessGate {
  id: string;
  label: string;
  status: "ready" | "warning" | "blocked";
  description: string;
  evidence: string;
  actionLabel: string;
}

export interface SupplierInventoryBridgeItem {
  id: string;
  productId: string;
  sku: string;
  productName: string;
  supplierId?: string;
  supplierName?: string;
  currentStockUnits: number;
  availableUnits: number;
  lowStockThresholdUnits: number;
  coverageDays: number;
  suggestedQty: number;
  priority: "critical" | "high" | "medium" | "low";
  source: "inventario_consolidado" | "datos_de_proveedores";
  evidence: string;
  actionLabel: string;
  tone: "urgent" | "high" | "warn" | "ok";
}

export interface SupplierInventoryBridgeSnapshot {
  generatedAt: IsoDate;
  source: "inventario_consolidado" | "datos_de_proveedores";
  sourceLabel: string;
  connectedProducts: number;
  linkedProducts: number;
  criticalProducts: number;
  lowStockProducts: number;
  overstockProducts: number;
  averageCoverageDays: number;
  warnings: string[];
  items: SupplierInventoryBridgeItem[];
}

export interface SupplierInventoryMovementPreview {
  id: string;
  productId: string;
  sku: string;
  productName: string;
  beforeQty: number;
  deltaQty: number;
  afterQty: number;
  reason: "receiving" | "receiving_reversal";
  sourceId: string;
  sourceLabel: string;
}

export interface SupplierPayablePlan {
  payableId: string;
  supplierId: string;
  supplierName: string;
  dueDate: IsoDate;
  amountCents: MoneyCents;
  status: PayableStatus;
  cashPressure: CashImpact;
  recommendedAction: string;
  auditRequired: boolean;
}

export interface SupplierOrderWorkflowStep {
  id: string;
  label: string;
  status: "done" | "current" | "next" | "blocked";
  description: string;
}

export interface SupplierOrderWorkflowCard {
  orderId: string;
  folio: string;
  supplierName: string;
  status: PurchaseOrderStatus;
  source: SupplierPurchaseOrder["source"];
  totalCents: MoneyCents;
  expectedReceptionDate: IsoDate;
  expectedPaymentDate: IsoDate;
  nextAction: string;
  risk: string;
  steps: SupplierOrderWorkflowStep[];
}

export interface SupplierSurfaceSignal {
  id: string;
  surface: "tablet" | "mobile";
  title: string;
  message: string;
  severity: "critical" | "high" | "medium" | "low";
  allowedAction: string;
  forbiddenAction: string;
}

export interface SupplierLifecycleSnapshot {
  generatedAt: IsoDate;
  readiness: SupplierReadinessGate[];
  calendar: SupplierCalendarEvent[];
  orderWorkflow: SupplierOrderWorkflowCard[];
  movementPreview: SupplierInventoryMovementPreview[];
  payablePlan: SupplierPayablePlan[];
  auditEvents: SupplierAuditEvent[];
  surfaceSignals: SupplierSurfaceSignal[];
  counters: {
    readyGates: number;
    warningGates: number;
    blockedGates: number;
    calendarEvents: number;
    ordersNeedingAction: number;
    receivingsWithDifferences: number;
    auditEvents: number;
  };
}

export interface CreateSuggestedOrderInput {
  recommendationId: string;
  actor: SupplierActor;
  reason: string;
  budgetCents?: number;
  excludedLineIds?: string[];
  quantityOverrides?: Record<string, number>;
}

export interface ConfirmReceivingInput {
  orderId: string;
  actor: SupplierActor;
  reason: string;
  receivedUnitsByLineId: Record<string, number>;
  receivedAt?: IsoDate;
}

export interface RegisterSupplierPaymentInput {
  payableId: string;
  actor: SupplierActor;
  amountCents: number;
  reason: string;
  paidAt?: IsoDate;
}

export interface SupplierActionResult<TPayload> {
  ok: boolean;
  code: string;
  message: string;
  data?: TPayload;
  warnings: string[];
  auditEvents: SupplierAuditEvent[];
}
