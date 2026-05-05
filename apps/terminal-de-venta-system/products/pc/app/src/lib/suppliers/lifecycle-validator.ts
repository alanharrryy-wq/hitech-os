import type {
  ConfirmReceivingInput,
  CreateSuggestedOrderInput,
  RegisterSupplierPaymentInput,
  SmartPurchaseRecommendation,
  SupplierAccount,
  SupplierActionResult,
  SupplierActor,
  SupplierAuditEvent,
  SupplierLifecycleSnapshot,
  SupplierPayable,
  SupplierPurchaseOrder,
  SupplierReceivingReceipt
} from "./types";

export type SupplierValidationSeverity = "info" | "warning" | "blocked";
export type SupplierValidationArea = "supplier" | "recommendation" | "order" | "receiving" | "payable" | "audit" | "surface" | "sync" | "permissions";

export interface SupplierValidationFinding {
  id: string;
  area: SupplierValidationArea;
  severity: SupplierValidationSeverity;
  title: string;
  description: string;
  evidence: string;
  action: string;
}

export interface SupplierValidationReport {
  status: "ready" | "warning" | "blocked";
  findings: SupplierValidationFinding[];
  counters: {
    info: number;
    warning: number;
    blocked: number;
  };
  summary: string;
}

const ROLE_MATRIX: Record<string, string[]> = {
  Cajero: ["supplier.signal.view", "tablet.signal.view"],
  Encargado: ["supplier.view", "purchase_order.create", "receiving.create", "receiving.complete"],
  Administrador: ["supplier.view", "supplier.update", "purchase_order.create", "purchase_order.approve", "purchase_order.send", "receiving.complete", "supplier_payable.pay", "smart_purchase.convert_to_order"],
  Dueño: ["supplier.view", "supplier.update", "supplier.block", "purchase_order.approve", "receiving.revert", "supplier_payable.pay", "smart_purchase.configure", "smart_purchase.convert_to_order"],
  Auditor: ["supplier.view", "audit.view"]
};

export function validateSupplierLifecycleSnapshot(input: {
  suppliers: SupplierAccount[];
  recommendations: SmartPurchaseRecommendation[];
  openOrders: SupplierPurchaseOrder[];
  receivingQueue: SupplierReceivingReceipt[];
  payables: SupplierPayable[];
  lifecycle: SupplierLifecycleSnapshot;
}): SupplierValidationReport {
  const findings: SupplierValidationFinding[] = [];
  findings.push(...validateSuppliers(input.suppliers));
  findings.push(...validateRecommendations(input.recommendations, input.suppliers));
  findings.push(...validateOrders(input.openOrders, input.recommendations));
  findings.push(...validateReceivings(input.receivingQueue, input.openOrders));
  findings.push(...validatePayables(input.payables, input.openOrders));
  findings.push(...validateAudit(input.lifecycle.auditEvents));
  findings.push(...validateSurfaceSignals(input.lifecycle));
  findings.push(...validateReadiness(input.lifecycle));
  return finalizeReport(findings);
}

export function validateCreateSuggestedOrderInput(input: Partial<CreateSuggestedOrderInput>): SupplierValidationReport {
  const findings: SupplierValidationFinding[] = [];
  if (!input.recommendationId) findings.push(finding("create_order.recommendation", "recommendation", "blocked", "Falta recomendacion", "No se puede crear pedido sin recommendationId.", "recommendationId ausente", "Enviar recommendationId."));
  if (!input.reason || input.reason.trim().length < 8) findings.push(finding("create_order.reason", "audit", "blocked", "Motivo insuficiente", "Convertir recomendacion en pedido deja rastro y requiere motivo claro.", `reason=${input.reason ?? ""}`, "Capturar motivo de al menos 8 caracteres."));
  findings.push(...validateActor(input.actor, "smart_purchase.convert_to_order"));
  return finalizeReport(findings);
}

export function validateConfirmReceivingInput(input: Partial<ConfirmReceivingInput>): SupplierValidationReport {
  const findings: SupplierValidationFinding[] = [];
  if (!input.orderId) findings.push(finding("receiving.order", "receiving", "blocked", "Falta pedido", "No se puede confirmar recepcion sin pedido origen.", "orderId ausente", "Enviar orderId."));
  if (!input.reason || input.reason.trim().length < 8) findings.push(finding("receiving.reason", "audit", "blocked", "Motivo insuficiente", "La recepcion afecta inventario y requiere referencia o motivo.", `reason=${input.reason ?? ""}`, "Capturar motivo o folio de factura."));
  if (!input.receivedUnitsByLineId || Object.keys(input.receivedUnitsByLineId).length === 0) findings.push(finding("receiving.lines", "receiving", "warning", "Cantidades no declaradas", "Sin cantidades explicitas se asume lo ordenado; conviene confirmar por linea.", "receivedUnitsByLineId vacio", "Mandar cantidades recibidas por linea."));
  findings.push(...validateActor(input.actor, "receiving.complete"));
  return finalizeReport(findings);
}

export function validateRegisterPaymentInput(input: Partial<RegisterSupplierPaymentInput>): SupplierValidationReport {
  const findings: SupplierValidationFinding[] = [];
  if (!input.payableId) findings.push(finding("payment.payable", "payable", "blocked", "Falta cuenta por pagar", "No se puede registrar pago sin cuenta origen.", "payableId ausente", "Enviar payableId."));
  if (!Number.isFinite(input.amountCents) || Number(input.amountCents) <= 0) findings.push(finding("payment.amount", "payable", "blocked", "Monto invalido", "El pago debe ser mayor a cero.", `amountCents=${input.amountCents ?? ""}`, "Enviar amountCents positivo."));
  if (!input.reason || input.reason.trim().length < 8) findings.push(finding("payment.reason", "audit", "blocked", "Motivo insuficiente", "Registrar pago afecta dinero y requiere referencia.", `reason=${input.reason ?? ""}`, "Capturar referencia de pago."));
  findings.push(...validateActor(input.actor, "supplier_payable.pay"));
  return finalizeReport(findings);
}

export function hasPermission(actor: SupplierActor | undefined, permission: string): boolean {
  if (!actor) return false;
  return (ROLE_MATRIX[actor.role] ?? []).includes(permission);
}

export function summarizeValidation(report: SupplierValidationReport): string {
  if (report.status === "ready") return "READY: Proveedores lifecycle no tiene bloqueos detectados.";
  if (report.status === "warning") return `WARNING: ${report.counters.warning} advertencias requieren revision antes de demo fuerte.`;
  return `BLOCKED: ${report.counters.blocked} bloqueos deben corregirse antes de declarar listo.`;
}

function validateSuppliers(suppliers: SupplierAccount[]): SupplierValidationFinding[] {
  const findings: SupplierValidationFinding[] = [];
  if (!suppliers.length) findings.push(finding("suppliers.empty", "supplier", "blocked", "Sin proveedores", "Compra Inteligente no debe operar sin proveedores.", "0 proveedores", "Agregar proveedor."));
  const active = suppliers.filter((supplier) => supplier.status === "active");
  if (!active.length) findings.push(finding("suppliers.no_active", "supplier", "blocked", "Sin proveedores activos", "No hay proveedor usable para pedidos.", `${suppliers.length} proveedores, 0 activos`, "Activar proveedor o crear uno nuevo."));
  for (const supplier of suppliers) {
    if (supplier.status === "active" && !supplier.visitRule) findings.push(finding(`supplier.${supplier.id}.calendar`, "supplier", "warning", "Proveedor sin calendario", "El calendario mejora fechas de pedido, recepcion y pago.", supplier.tradeName, "Configurar calendario."));
    if (!supplier.contacts.some((contact) => contact.isPrimary)) findings.push(finding(`supplier.${supplier.id}.contact`, "supplier", "warning", "Sin contacto principal", "Conviene tener telefono o WhatsApp principal.", supplier.tradeName, "Marcar contacto principal."));
    if (supplier.status === "blocked") findings.push(finding(`supplier.${supplier.id}.blocked`, "supplier", "info", "Proveedor bloqueado", "Proveedor bloqueado no debe recibir pedidos nuevos.", supplier.tradeName, "Revisar motivo antes de reactivar."));
  }
  return findings;
}

function validateRecommendations(recommendations: SmartPurchaseRecommendation[], suppliers: SupplierAccount[]): SupplierValidationFinding[] {
  const findings: SupplierValidationFinding[] = [];
  const suppliersById = new Map(suppliers.map((supplier) => [supplier.id, supplier]));
  if (!recommendations.length) findings.push(finding("recommendations.empty", "recommendation", "blocked", "Sin recomendaciones", "Compra Inteligente debe generar al menos una recomendacion o un estado vacio honesto.", "0 recomendaciones", "Generar corrida o mostrar requisitos."));
  for (const recommendation of recommendations) {
    if (!recommendation.reasons.length) findings.push(finding(`recommendation.${recommendation.id}.reasons`, "recommendation", "blocked", "Recomendacion sin razones", "Ninguna sugerencia debe sonar a magia.", recommendation.title, "Guardar razones explicables."));
    if (recommendation.action === "create_order" && !recommendation.lines.length) findings.push(finding(`recommendation.${recommendation.id}.lines`, "recommendation", "blocked", "Sin lineas", "No se puede crear pedido vacio.", recommendation.title, "Agregar lineas o bloquear recomendacion."));
    if (recommendation.supplierId) {
      const supplier = suppliersById.get(recommendation.supplierId);
      if (supplier?.status === "blocked" && recommendation.action === "create_order") findings.push(finding(`recommendation.${recommendation.id}.blocked_supplier`, "recommendation", "blocked", "Usa proveedor bloqueado", "Proveedor bloqueado no puede recibir pedido nuevo.", supplier.tradeName, "Cambiar proveedor o bloquear recomendacion."));
    }
    if (recommendation.cashImpact === "blocked" && recommendation.action === "create_order") findings.push(finding(`recommendation.${recommendation.id}.cash`, "recommendation", "blocked", "Compra bloqueada con accion de crear", "No debe mostrarse crear pedido cuando caja bloquea compra.", recommendation.title, "Cambiar accion a simular o bloquear."));
  }
  return findings;
}

function validateOrders(orders: SupplierPurchaseOrder[], recommendations: SmartPurchaseRecommendation[]): SupplierValidationFinding[] {
  const findings: SupplierValidationFinding[] = [];
  const recommendationSupplierNames = new Set(recommendations.map((item) => item.supplierName));
  for (const order of orders) {
    if (!order.supplierId || !order.supplierName) findings.push(finding(`order.${order.id}.supplier`, "order", "blocked", "Pedido sin proveedor", "Un pedido aprobado no puede quedar sin proveedor.", order.folio, "Asignar proveedor."));
    if (!order.lines.length) findings.push(finding(`order.${order.id}.lines`, "order", "blocked", "Pedido sin lineas", "No se puede aprobar ni enviar pedido vacio.", order.folio, "Agregar productos."));
    if (order.totalCents <= 0) findings.push(finding(`order.${order.id}.total`, "order", "blocked", "Total invalido", "El total debe ser mayor a cero.", order.folio, "Recalcular lineas."));
    if (order.source === "smart_purchase" && !recommendationSupplierNames.has(order.supplierName)) findings.push(finding(`order.${order.id}.origin`, "order", "warning", "Pedido inteligente sin recomendacion visible", "El pedido debe conservar origen rastreable.", order.folio, "Guardar recommendationId en auditoria."));
    for (const line of order.lines) {
      if (line.orderedUnits <= 0) findings.push(finding(`order.${order.id}.${line.id}.units`, "order", "blocked", "Linea sin unidades", "La cantidad ordenada debe ser positiva.", `${order.folio} ${line.sku}`, "Corregir cantidad."));
      if (line.unitCostCents < 0) findings.push(finding(`order.${order.id}.${line.id}.cost`, "order", "blocked", "Costo negativo", "El costo unitario no puede ser negativo.", `${order.folio} ${line.sku}`, "Corregir costo."));
    }
  }
  return findings;
}

function validateReceivings(receipts: SupplierReceivingReceipt[], orders: SupplierPurchaseOrder[]): SupplierValidationFinding[] {
  const findings: SupplierValidationFinding[] = [];
  const orderIds = new Set(orders.map((order) => order.id));
  for (const receipt of receipts) {
    if (receipt.orderId && !orderIds.has(receipt.orderId)) findings.push(finding(`receipt.${receipt.id}.order`, "receiving", "warning", "Recepcion sin pedido encontrado", "Puede ser recepcion libre, pero debe explicarse.", receipt.id, "Vincular pedido o marcar recepcion libre."));
    if (receipt.status === "with_differences" && !receipt.differences.length) findings.push(finding(`receipt.${receipt.id}.diff_empty`, "receiving", "blocked", "Estado de diferencia sin detalle", "Las diferencias deben listar producto, cantidades y motivo.", receipt.id, "Capturar diferencias."));
    for (const difference of receipt.differences) {
      if (!difference.note || difference.note.trim().length < 5) findings.push(finding(`receipt.${receipt.id}.${difference.sku}.note`, "receiving", "blocked", "Diferencia sin nota", "Una diferencia requiere motivo visible.", difference.sku, "Capturar nota de diferencia."));
      if (difference.receivedUnits < 0) findings.push(finding(`receipt.${receipt.id}.${difference.sku}.negative`, "receiving", "blocked", "Cantidad recibida negativa", "La recepcion no puede registrar unidades negativas.", difference.sku, "Corregir cantidad."));
    }
  }
  return findings;
}

function validatePayables(payables: SupplierPayable[], orders: SupplierPurchaseOrder[]): SupplierValidationFinding[] {
  const findings: SupplierValidationFinding[] = [];
  const orderIds = new Set(orders.map((order) => order.id));
  for (const payable of payables) {
    if (payable.amountCents <= 0 && payable.status !== "paid") findings.push(finding(`payable.${payable.id}.amount`, "payable", "blocked", "Cuenta por pagar sin monto", "Una cuenta pendiente debe conservar monto valido.", payable.supplierName, "Corregir monto o marcar pagada."));
    if (payable.orderId && !orderIds.has(payable.orderId)) findings.push(finding(`payable.${payable.id}.origin`, "payable", "warning", "Cuenta sin pedido visible", "Debe existir origen rastreable: pedido, recepcion o captura manual.", payable.supplierName, "Vincular origen."));
    if (payable.status === "overdue") findings.push(finding(`payable.${payable.id}.overdue`, "payable", "warning", "Pago vencido", "Pagos vencidos deben descontarse mentalmente del presupuesto seguro.", payable.supplierName, "Pagar, negociar o bloquear compras nuevas."));
  }
  return findings;
}

function validateAudit(events: SupplierAuditEvent[]): SupplierValidationFinding[] {
  const findings: SupplierValidationFinding[] = [];
  if (!events.length) findings.push(finding("audit.empty", "audit", "blocked", "Sin auditoria", "Toda accion sensible debe dejar rastro.", "0 eventos", "Generar eventos de auditoria."));
  for (const event of events) {
    if (!event.actor?.id) findings.push(finding(`audit.${event.id}.actor`, "audit", "blocked", "Evento sin actor", "Auditoria sin responsable es chisme con timestamp.", event.topic, "Guardar actor."));
    if (!event.reason || event.reason.trim().length < 5) findings.push(finding(`audit.${event.id}.reason`, "audit", "warning", "Evento sin motivo suficiente", "Acciones sensibles deben explicar por que ocurrieron.", event.topic, "Guardar motivo."));
    if (!event.visibleSummary) findings.push(finding(`audit.${event.id}.summary`, "audit", "warning", "Evento sin resumen visible", "Auditoria debe leerse como negocio, no como log crudo.", event.topic, "Agregar resumen."));
  }
  return findings;
}

function validateSurfaceSignals(lifecycle: SupplierLifecycleSnapshot): SupplierValidationFinding[] {
  const findings: SupplierValidationFinding[] = [];
  const tabletSignals = lifecycle.surfaceSignals.filter((signal) => signal.surface === "tablet");
  const mobileSignals = lifecycle.surfaceSignals.filter((signal) => signal.surface === "mobile");
  if (!tabletSignals.length) findings.push(finding("surface.tablet.empty", "surface", "warning", "Sin señales Tablet", "Tablet debe poder mostrar avisos ligeros sin administrar proveedores.", "0 señales", "Generar señales de proveedor esperado, producto critico o recepcion pendiente."));
  if (!mobileSignals.length) findings.push(finding("surface.mobile.empty", "surface", "warning", "Sin alertas App movil", "App movil debe funcionar como radar, no como mini backoffice.", "0 señales", "Generar alertas de compra, pago o caja."));
  for (const signal of lifecycle.surfaceSignals) {
    if (signal.forbiddenAction.toLowerCase().includes("proveedor") && signal.surface === "tablet") {
      // Este hallazgo es informativo: queremos que la frontera quede explicita en la UI.
      findings.push(finding(`surface.${signal.id}.boundary`, "surface", "info", "Frontera Tablet explicita", "La señal deja claro que Tablet no administra proveedores.", signal.title, "Mantener frontera visible."));
    }
  }
  return findings;
}

function validateReadiness(lifecycle: SupplierLifecycleSnapshot): SupplierValidationFinding[] {
  const findings: SupplierValidationFinding[] = [];
  for (const gate of lifecycle.readiness) {
    if (gate.status === "blocked") findings.push(finding(`gate.${gate.id}`, "sync", "blocked", gate.label, gate.description, gate.evidence, gate.actionLabel));
    if (gate.status === "warning") findings.push(finding(`gate.${gate.id}`, "sync", "warning", gate.label, gate.description, gate.evidence, gate.actionLabel));
  }
  return findings;
}

function validateActor(actor: SupplierActor | undefined, permission: string): SupplierValidationFinding[] {
  if (!actor) return [finding(`permission.${permission}.actor`, "permissions", "blocked", "Actor requerido", "La accion sensible necesita responsable.", "actor ausente", "Enviar actor.")];
  if (!hasPermission(actor, permission)) return [finding(`permission.${permission}.denied`, "permissions", "blocked", "Permiso insuficiente", `${actor.role} no tiene permiso ${permission}.`, actor.name, "Usar rol autorizado o solicitar aprobacion.")];
  return [];
}

function finalizeReport(findings: SupplierValidationFinding[]): SupplierValidationReport {
  const counters = {
    info: findings.filter((item) => item.severity === "info").length,
    warning: findings.filter((item) => item.severity === "warning").length,
    blocked: findings.filter((item) => item.severity === "blocked").length
  };
  const status: SupplierValidationReport["status"] = counters.blocked > 0 ? "blocked" : counters.warning > 0 ? "warning" : "ready";
  return { status, findings, counters, summary: status === "ready" ? "Sin bloqueos ni advertencias criticas." : status === "warning" ? "Hay advertencias operativas por revisar." : "Hay bloqueos que impiden declarar READY." };
}

function finding(id: string, area: SupplierValidationArea, severity: SupplierValidationSeverity, title: string, description: string, evidence: string, action: string): SupplierValidationFinding {
  return { id, area, severity, title, description, evidence, action };
}
