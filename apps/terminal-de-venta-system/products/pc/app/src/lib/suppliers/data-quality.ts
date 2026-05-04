import type {
  SmartPurchaseRecommendation,
  SupplierAccount,
  SupplierDashboardSnapshot,
  SupplierPayable,
  SupplierProductLink,
  SupplierPurchaseOrder,
  SupplierReceivingReceipt
} from "./types";

export type SupplierDataQualitySeverity = "ok" | "info" | "warning" | "blocked";
export type SupplierDataQualityArea =
  | "supplier_master"
  | "supplier_calendar"
  | "supplier_contact"
  | "product_link"
  | "smart_purchase"
  | "purchase_order"
  | "receiving"
  | "payable"
  | "cash"
  | "audit"
  | "surface_boundary";

export interface SupplierDataQualityFinding {
  id: string;
  area: SupplierDataQualityArea;
  severity: SupplierDataQualitySeverity;
  title: string;
  description: string;
  evidence: string;
  recommendedAction: string;
  owner: "dueno" | "administrador" | "encargado" | "auditor" | "sistema";
}

export interface SupplierDataQualityMetric {
  id: string;
  label: string;
  value: number;
  unit: "conteo" | "porcentaje" | "centavos" | "dias";
  interpretation: string;
}

export interface SupplierDataQualityReport {
  status: "ready" | "warning" | "blocked";
  score: number;
  generatedAt: string;
  metrics: SupplierDataQualityMetric[];
  findings: SupplierDataQualityFinding[];
  sections: {
    title: string;
    status: "ready" | "warning" | "blocked";
    summary: string;
    findingIds: string[];
  }[];
  nextActions: string[];
}

const MS_PER_DAY = 86400000;
const WARNING_COST_AGE_DAYS = 15;

export function buildSupplierDataQualityReport(snapshot: SupplierDashboardSnapshot): SupplierDataQualityReport {
  const findings: SupplierDataQualityFinding[] = [];
  findings.push(...inspectSupplierMaster(snapshot.suppliers));
  findings.push(...inspectSupplierCalendars(snapshot.suppliers));
  findings.push(...inspectProductLinks(snapshot.productLinks, snapshot.suppliers));
  findings.push(...inspectRecommendations(snapshot.recommendations, snapshot.productLinks, snapshot.suppliers));
  findings.push(...inspectPurchaseOrders(snapshot.openOrders, snapshot.recommendations));
  findings.push(...inspectReceiving(snapshot.receivingQueue, snapshot.openOrders));
  findings.push(...inspectPayables(snapshot.payables, snapshot.openOrders));
  findings.push(...inspectAuditAndBoundaries(snapshot));

  const metrics = buildMetrics(snapshot, findings);
  const counters = countFindings(findings);
  const score = computeScore(findings, metrics);
  const status = counters.blocked > 0 ? "blocked" : counters.warning > 0 ? "warning" : "ready";
  const sections = buildSections(findings);
  const nextActions = buildNextActions(findings);
  return { status, score, generatedAt: snapshot.generatedAt, metrics, findings, sections, nextActions };
}

function inspectSupplierMaster(suppliers: SupplierAccount[]): SupplierDataQualityFinding[] {
  const findings: SupplierDataQualityFinding[] = [];
  const normalizedNames = new Map<string, SupplierAccount[]>();
  for (const supplier of suppliers) {
    const key = normalize(supplier.tradeName);
    normalizedNames.set(key, [...(normalizedNames.get(key) ?? []), supplier]);
    if (!supplier.tradeName.trim()) findings.push(finding(`supplier.${supplier.id}.name`, "supplier_master", "blocked", "Proveedor sin nombre", "No se puede operar calendario, pedido ni pago sin nombre comercial.", supplier.id, "Capturar nombre comercial.", "administrador"));
    if (supplier.status === "blocked") findings.push(finding(`supplier.${supplier.id}.blocked`, "supplier_master", "info", "Proveedor bloqueado", "Proveedor bloqueado queda fuera de pedidos nuevos y recomendaciones.", supplier.tradeName, "Mantener motivo visible y revisar si debe reactivarse.", "dueno"));
    if (supplier.terms.minimumOrderCents < 0) findings.push(finding(`supplier.${supplier.id}.minimum`, "supplier_master", "blocked", "Monto minimo invalido", "El monto minimo de pedido no puede ser negativo.", supplier.tradeName, "Corregir terminos comerciales.", "administrador"));
    if (supplier.terms.creditDays < 0) findings.push(finding(`supplier.${supplier.id}.credit_days`, "supplier_master", "blocked", "Dias de credito invalidos", "Dias de credito negativos rompen cuentas por pagar y caja.", supplier.tradeName, "Corregir condicion de pago.", "administrador"));
    if (supplier.terms.creditLimitCents > 0 && supplier.terms.minimumOrderCents > supplier.terms.creditLimitCents) findings.push(finding(`supplier.${supplier.id}.minimum_vs_limit`, "supplier_master", "warning", "Minimo mayor que limite", "El pedido minimo rebasa el limite de credito configurado.", supplier.tradeName, "Ajustar minimo o limite de credito.", "dueno"));
  }
  for (const [key, group] of normalizedNames) {
    if (key && group.length > 1) findings.push(finding(`supplier.duplicate.${key}`, "supplier_master", "warning", "Proveedor posiblemente duplicado", "Hay mas de un proveedor con nombre comercial equivalente.", group.map((item) => item.tradeName).join(", "), "Fusionar, archivar o diferenciar proveedores.", "administrador"));
  }
  return findings;
}

function inspectSupplierCalendars(suppliers: SupplierAccount[]): SupplierDataQualityFinding[] {
  const findings: SupplierDataQualityFinding[] = [];
  for (const supplier of suppliers) {
    if (!supplier.visitRule) {
      if (supplier.status === "active") findings.push(finding(`supplier.${supplier.id}.calendar_missing`, "supplier_calendar", "warning", "Proveedor activo sin calendario", "Sin calendario Compra Inteligente no sabe cuando pedir, recibir o pagar.", supplier.tradeName, "Configurar visita, corte y tiempo de entrega.", "encargado"));
      continue;
    }
    if (!supplier.visitRule.weekdays.length) findings.push(finding(`supplier.${supplier.id}.weekdays`, "supplier_calendar", "blocked", "Calendario sin dias", "Un proveedor con calendario debe tener dias de visita.", supplier.tradeName, "Elegir al menos un dia habitual.", "encargado"));
    if (supplier.visitRule.leadTimeDays < 0) findings.push(finding(`supplier.${supplier.id}.lead_time`, "supplier_calendar", "blocked", "Tiempo de entrega invalido", "El tiempo de entrega no puede ser negativo.", supplier.tradeName, "Corregir tiempo estimado de entrega.", "encargado"));
    if (!looksLikeTime(supplier.visitRule.approximateTime) || !looksLikeTime(supplier.visitRule.orderCutoffTime)) findings.push(finding(`supplier.${supplier.id}.time_format`, "supplier_calendar", "warning", "Horario con formato raro", "Los horarios deben ser legibles para evitar pedidos fuera de corte.", supplier.tradeName, "Usar formato HH:mm.", "encargado"));
  }
  return findings;
}

function inspectProductLinks(links: SupplierProductLink[], suppliers: SupplierAccount[]): SupplierDataQualityFinding[] {
  const findings: SupplierDataQualityFinding[] = [];
  const suppliersById = new Map(suppliers.map((supplier) => [supplier.id, supplier]));
  const primaryByProduct = new Map<string, SupplierProductLink[]>();
  const duplicateSkuBySupplier = new Map<string, SupplierProductLink[]>();
  for (const link of links) {
    if (link.isPrimary) primaryByProduct.set(link.productId, [...(primaryByProduct.get(link.productId) ?? []), link]);
    duplicateSkuBySupplier.set(`${link.supplierId}:${normalize(link.sku)}`, [...(duplicateSkuBySupplier.get(`${link.supplierId}:${normalize(link.sku)}`) ?? []), link]);
    const supplier = suppliersById.get(link.supplierId);
    if (!supplier) findings.push(finding(`link.${link.id}.supplier_missing`, "product_link", "blocked", "Producto con proveedor inexistente", "La relacion producto-proveedor apunta a un proveedor que no existe.", `${link.sku} ${link.supplierId}`, "Corregir proveedor asociado.", "administrador"));
    if (supplier?.status === "blocked" && link.isPrimary) findings.push(finding(`link.${link.id}.blocked_primary`, "product_link", "warning", "Proveedor principal bloqueado", "El producto tiene como principal un proveedor que no debe recibir pedidos.", `${link.sku} ${supplier.tradeName}`, "Asignar proveedor alterno o reactivar con motivo.", "administrador"));
    if (link.packageSize <= 0) findings.push(finding(`link.${link.id}.package`, "product_link", "blocked", "Presentacion invalida", "La presentacion/caja debe ser mayor a cero para calcular paquetes sugeridos.", link.sku, "Corregir packageSize.", "administrador"));
    if (link.minPurchaseUnits <= 0) findings.push(finding(`link.${link.id}.minimum_units`, "product_link", "warning", "Minimo de compra ausente", "Sin minimo, el pedido sugerido puede quedar poco realista.", link.sku, "Capturar minimo de compra.", "encargado"));
    if (link.recentCostCents <= 0) findings.push(finding(`link.${link.id}.cost`, "product_link", "blocked", "Costo faltante", "Sin costo no se puede estimar impacto en caja.", link.sku, "Capturar costo reciente.", "administrador"));
    if (link.averageDailySalesUnits < 0) findings.push(finding(`link.${link.id}.sales`, "product_link", "blocked", "Venta promedio invalida", "La venta promedio no puede ser negativa.", link.sku, "Recalcular ventas promedio.", "sistema"));
    const costAge = ageInDays(link.lastCostUpdateAt, "2026-05-02T16:30:00.000Z");
    if (costAge > WARNING_COST_AGE_DAYS) findings.push(finding(`link.${link.id}.cost_stale`, "product_link", "warning", "Costo viejo", "Costo antiguo puede deformar margen y caja.", `${link.sku}: ${costAge} dias`, "Revisar ultimo costo recibido.", "administrador"));
  }
  for (const [productId, group] of primaryByProduct) {
    if (group.length > 1) findings.push(finding(`link.${productId}.many_primary`, "product_link", "warning", "Mas de un proveedor principal", "Un producto puede tener alternos, pero debe quedar claro cual manda para recomendaciones.", group.map((item) => `${item.sku}/${item.supplierName}`).join(", "), "Elegir un proveedor principal.", "administrador"));
  }
  for (const [key, group] of duplicateSkuBySupplier) {
    if (group.length > 1) findings.push(finding(`link.duplicate.${key}`, "product_link", "warning", "SKU duplicado con proveedor", "Puede generar compras dobles o costos confundidos.", group.map((item) => item.id).join(", "), "Depurar asociaciones duplicadas.", "administrador"));
  }
  return findings;
}

function inspectRecommendations(recommendations: SmartPurchaseRecommendation[], links: SupplierProductLink[], suppliers: SupplierAccount[]): SupplierDataQualityFinding[] {
  const findings: SupplierDataQualityFinding[] = [];
  const linksByProduct = new Map(links.map((link) => [link.productId, link]));
  const suppliersById = new Map(suppliers.map((supplier) => [supplier.id, supplier]));
  if (!recommendations.length) findings.push(finding("recommendations.empty", "smart_purchase", "blocked", "Sin recomendaciones ni estado claro", "Compra Inteligente necesita recomendaciones o un vacio honesto.", "0 recomendaciones", "Generar corrida o mostrar requisitos.", "sistema"));
  for (const recommendation of recommendations) {
    if (!recommendation.reasons.length) findings.push(finding(`recommendation.${recommendation.id}.reasons`, "smart_purchase", "blocked", "Recomendacion sin razones", "Una recomendacion sin explicacion parece horoscopo con dashboard.", recommendation.title, "Guardar razones visibles.", "sistema"));
    if (recommendation.supplierId) {
      const supplier = suppliersById.get(recommendation.supplierId);
      if (!supplier) findings.push(finding(`recommendation.${recommendation.id}.supplier_missing`, "smart_purchase", "blocked", "Proveedor sugerido inexistente", "No se puede crear pedido si el proveedor no existe.", recommendation.supplierName, "Corregir supplierId.", "sistema"));
      if (supplier?.status === "blocked" && recommendation.action === "create_order") findings.push(finding(`recommendation.${recommendation.id}.blocked_supplier`, "smart_purchase", "blocked", "Recomienda proveedor bloqueado", "Proveedor bloqueado no puede ser opcion activa de pedido.", supplier.tradeName, "Bloquear recomendacion o cambiar proveedor.", "sistema"));
    }
    if (recommendation.cashImpact === "blocked" && recommendation.action === "create_order") findings.push(finding(`recommendation.${recommendation.id}.cash`, "smart_purchase", "blocked", "Caja bloqueada con accion de crear", "Si caja bloquea, la accion debe ser simular o ajustar, no crear pedido.", recommendation.title, "Cambiar CTA y exigir simulacion.", "sistema"));
    if (recommendation.estimatedTotalCents > recommendation.safeBudgetCents && recommendation.cashImpact === "safe") findings.push(finding(`recommendation.${recommendation.id}.cash_label`, "smart_purchase", "warning", "Etiqueta de caja optimista", "La compra rebasa presupuesto seguro pero se muestra segura.", recommendation.title, "Reclasificar impacto de caja.", "sistema"));
    for (const line of recommendation.lines) {
      const link = linksByProduct.get(line.productId);
      if (!link) findings.push(finding(`recommendation.${recommendation.id}.${line.id}.link_missing`, "smart_purchase", "blocked", "Linea sin relacion producto-proveedor", "La linea recomendada debe poder convertirse a pedido con proveedor y costo.", line.sku, "Crear SupplierProductLink.", "sistema"));
      if (!line.reasons.length) findings.push(finding(`recommendation.${recommendation.id}.${line.id}.line_reasons`, "smart_purchase", "warning", "Linea sin razones", "Cada producto recomendado debe explicar su urgencia.", line.sku, "Guardar razones por linea.", "sistema"));
      if (line.coverageDaysAfter < line.coverageDaysBefore && line.action === "create_order") findings.push(finding(`recommendation.${recommendation.id}.${line.id}.coverage`, "smart_purchase", "warning", "Cobertura empeora", "La compra sugerida no deberia reducir cobertura estimada.", line.sku, "Revisar formula de cobertura.", "sistema"));
    }
  }
  return findings;
}

function inspectPurchaseOrders(orders: SupplierPurchaseOrder[], recommendations: SmartPurchaseRecommendation[]): SupplierDataQualityFinding[] {
  const findings: SupplierDataQualityFinding[] = [];
  const recommendationSupplierNames = new Set(recommendations.map((item) => item.supplierName));
  for (const order of orders) {
    if (!order.lines.length) findings.push(finding(`order.${order.id}.empty`, "purchase_order", "blocked", "Pedido sin productos", "No se puede aprobar ni enviar un pedido vacio.", order.folio, "Agregar lineas o cancelar borrador.", "encargado"));
    const linesTotal = order.lines.reduce((sum, line) => sum + line.expectedTotalCents, 0);
    if (Math.abs(linesTotal - order.totalCents) > 1) findings.push(finding(`order.${order.id}.total_mismatch`, "purchase_order", "blocked", "Total no cuadra", "El total del pedido no coincide con sus lineas.", `${order.folio}: ${order.totalCents} vs ${linesTotal}`, "Recalcular totales antes de aprobar.", "sistema"));
    if (order.source === "smart_purchase" && !recommendationSupplierNames.has(order.supplierName)) findings.push(finding(`order.${order.id}.source_trace`, "purchase_order", "warning", "Pedido sugerido sin recomendacion visible", "El pedido debe conservar el origen de Compra Inteligente.", order.folio, "Guardar recommendationId o evento de conversion.", "sistema"));
    for (const line of order.lines) {
      if (line.orderedUnits <= 0) findings.push(finding(`order.${order.id}.${line.id}.units`, "purchase_order", "blocked", "Cantidad invalida", "La cantidad pedida debe ser mayor a cero.", `${order.folio} ${line.sku}`, "Corregir cantidad.", "encargado"));
      if (line.receivedUnits > line.orderedUnits && order.status !== "partially_received") findings.push(finding(`order.${order.id}.${line.id}.over_received`, "purchase_order", "warning", "Sobre-recepcion no marcada", "Si llego mas de lo pedido debe quedar diferencia o autorizacion.", `${line.sku}: ${line.receivedUnits}/${line.orderedUnits}`, "Registrar diferencia.", "encargado"));
    }
  }
  return findings;
}

function inspectReceiving(receipts: SupplierReceivingReceipt[], orders: SupplierPurchaseOrder[]): SupplierDataQualityFinding[] {
  const findings: SupplierDataQualityFinding[] = [];
  const ordersById = new Map(orders.map((order) => [order.id, order]));
  for (const receipt of receipts) {
    if (receipt.orderId && !ordersById.has(receipt.orderId)) findings.push(finding(`receipt.${receipt.id}.order_missing`, "receiving", "warning", "Recepcion sin pedido encontrado", "Puede ser recepcion libre, pero debe declararse.", receipt.id, "Vincular pedido o marcar libre.", "encargado"));
    if (receipt.status === "with_differences" && !receipt.differences.length) findings.push(finding(`receipt.${receipt.id}.diff_empty`, "receiving", "blocked", "Recepcion con diferencia sin detalle", "La diferencia necesita producto, cantidad y motivo.", receipt.id, "Capturar diferencias.", "encargado"));
    for (const difference of receipt.differences) {
      if (difference.receivedUnits < 0) findings.push(finding(`receipt.${receipt.id}.${difference.sku}.negative`, "receiving", "blocked", "Cantidad negativa", "Una recepcion no puede capturar negativos.", difference.sku, "Corregir cantidad recibida.", "encargado"));
      if (!difference.note || difference.note.trim().length < 5) findings.push(finding(`receipt.${receipt.id}.${difference.sku}.note`, "receiving", "blocked", "Diferencia sin motivo", "Las diferencias no se barren debajo del tapete, aunque el tapete sea premium.", difference.sku, "Capturar motivo claro.", "encargado"));
    }
  }
  return findings;
}

function inspectPayables(payables: SupplierPayable[], orders: SupplierPurchaseOrder[]): SupplierDataQualityFinding[] {
  const findings: SupplierDataQualityFinding[] = [];
  const orderIds = new Set(orders.map((order) => order.id));
  for (const payable of payables) {
    if (payable.amountCents <= 0 && payable.status !== "paid") findings.push(finding(`payable.${payable.id}.amount`, "payable", "blocked", "Cuenta por pagar sin monto", "Una obligacion pendiente debe tener monto positivo.", payable.supplierName, "Corregir monto o cerrar cuenta.", "administrador"));
    if (payable.orderId && !orderIds.has(payable.orderId)) findings.push(finding(`payable.${payable.id}.origin`, "payable", "warning", "Cuenta sin pedido visible", "Debe rastrearse de que pedido o recepcion nace la deuda.", payable.supplierName, "Vincular origen.", "auditor"));
    if (payable.status === "overdue") findings.push(finding(`payable.${payable.id}.overdue`, "payable", "warning", "Pago vencido", "Pagos vencidos deben pesar en presupuesto seguro antes de comprar mas.", payable.supplierName, "Registrar pago, acuerdo o bloqueo temporal.", "dueno"));
  }
  return findings;
}

function inspectAuditAndBoundaries(snapshot: SupplierDashboardSnapshot): SupplierDataQualityFinding[] {
  const findings: SupplierDataQualityFinding[] = [];
  const auditEvents = snapshot.lifecycle.auditEvents;
  if (!auditEvents.length) findings.push(finding("audit.empty", "audit", "blocked", "Sin auditoria", "Acciones sensibles sin rastro son la antesala del chisme contable.", "0 eventos", "Registrar eventos con actor, motivo y antes/despues.", "auditor"));
  for (const event of auditEvents) {
    if (!event.actor.id) findings.push(finding(`audit.${event.id}.actor`, "audit", "blocked", "Evento sin actor", "No basta saber que algo paso; importa quien lo hizo.", event.topic, "Guardar actor.", "sistema"));
    if (event.requiresReview && (!event.reason || event.reason.trim().length < 5)) findings.push(finding(`audit.${event.id}.reason`, "audit", "warning", "Revision sin motivo claro", "Una accion sensible debe explicar por que se hizo.", event.topic, "Capturar motivo.", "auditor"));
  }
  const tabletSignals = snapshot.lifecycle.surfaceSignals.filter((signal) => signal.surface === "tablet");
  const forbiddenHeavyTablet = tabletSignals.filter((signal) => /aprobar|cuentas|calendario|configurar|proveedor/i.test(signal.allowedAction));
  if (forbiddenHeavyTablet.length) findings.push(finding("surface.tablet.heavy", "surface_boundary", "blocked", "Tablet cargada de gobierno", "Tablet solo debe ver señales ligeras, no administrar proveedores.", forbiddenHeavyTablet.map((signal) => signal.title).join(", "), "Mover accion pesada a PC.", "sistema"));
  if (snapshot.lifecycle.readiness.some((gate) => gate.id.includes("sync") && gate.status !== "ready") && snapshot.lifecycle.counters.warningGates === 0 && snapshot.lifecycle.counters.blockedGates === 0) findings.push(finding("sync.pending.message", "surface_boundary", "warning", "Sincronizacion pendiente sin aviso", "Si hay ventas pendientes, Compra Inteligente debe marcar que puede cambiar.", "gates sin aviso", "Agregar aviso visible.", "sistema"));
  return findings;
}

function buildMetrics(snapshot: SupplierDashboardSnapshot, findings: SupplierDataQualityFinding[]): SupplierDataQualityMetric[] {
  const activeSuppliers = snapshot.suppliers.filter((supplier) => supplier.status === "active").length;
  const scheduledSuppliers = snapshot.suppliers.filter((supplier) => supplier.visitRule).length;
  const linkedProducts = snapshot.productLinks.length;
  const recommendationLines = snapshot.recommendations.reduce((sum, recommendation) => sum + recommendation.lines.length, 0);
  const payablesAtRisk = snapshot.payables.filter((payable) => payable.status === "due_soon" || payable.status === "overdue").length;
  const receiptsWithDiff = snapshot.receivingQueue.filter((receipt) => receipt.status === "with_differences").length;
  const counters = countFindings(findings);
  return [
    metric("active_suppliers", "Proveedores activos", activeSuppliers, "conteo", "Base disponible para calendario, pedidos y compra inteligente."),
    metric("calendar_coverage", "Cobertura de calendario", percentage(scheduledSuppliers, Math.max(1, snapshot.suppliers.length)), "porcentaje", "Mientras mas alto, menos compras al tanteo."),
    metric("linked_products", "Productos asociados", linkedProducts, "conteo", "Productos con proveedor, costo y presentacion para convertir recomendacion en pedido."),
    metric("recommendation_lines", "Lineas recomendables", recommendationLines, "conteo", "Lineas que Compra Inteligente puede explicar o bloquear honestamente."),
    metric("payables_at_risk", "Pagos en riesgo", payablesAtRisk, "conteo", "Pagos proximos o vencidos que deben cuidar caja."),
    metric("receipts_with_differences", "Recepciones con diferencia", receiptsWithDiff, "conteo", "Diferencias que afectan inventario y deben auditarse."),
    metric("blocked_findings", "Bloqueos de calidad", counters.blocked, "conteo", "Hallazgos que impiden declarar READY."),
    metric("warning_findings", "Advertencias de calidad", counters.warning, "conteo", "Hallazgos que permiten operar con cuidado.")
  ];
}

function buildSections(findings: SupplierDataQualityFinding[]): SupplierDataQualityReport["sections"] {
  const definitions: { title: string; areas: SupplierDataQualityArea[] }[] = [
    { title: "Maestro de proveedores", areas: ["supplier_master", "supplier_calendar", "supplier_contact"] },
    { title: "Producto y costo", areas: ["product_link", "smart_purchase"] },
    { title: "Pedido y recepcion", areas: ["purchase_order", "receiving"] },
    { title: "Caja y cuentas por pagar", areas: ["payable", "cash"] },
    { title: "Auditoria y frontera Tablet", areas: ["audit", "surface_boundary"] }
  ];
  return definitions.map((definition) => {
    const sectionFindings = findings.filter((finding) => definition.areas.includes(finding.area));
    const status = sectionFindings.some((item) => item.severity === "blocked") ? "blocked" : sectionFindings.some((item) => item.severity === "warning") ? "warning" : "ready";
    return {
      title: definition.title,
      status,
      summary: sectionFindings.length ? `${sectionFindings.length} hallazgos detectados.` : "Sin hallazgos bloqueantes.",
      findingIds: sectionFindings.map((item) => item.id)
    };
  });
}

function buildNextActions(findings: SupplierDataQualityFinding[]): string[] {
  const severe = findings.filter((item) => item.severity === "blocked" || item.severity === "warning");
  if (!severe.length) return ["Mantener monitoreo de calendario, recepciones y cuentas por pagar."];
  const seen = new Set<string>();
  const actions: string[] = [];
  for (const finding of severe) {
    const action = `${finding.owner}: ${finding.recommendedAction}`;
    if (!seen.has(action)) {
      seen.add(action);
      actions.push(action);
    }
    if (actions.length >= 6) break;
  }
  return actions;
}

function computeScore(findings: SupplierDataQualityFinding[], metrics: SupplierDataQualityMetric[]): number {
  let score = 100;
  for (const finding of findings) {
    if (finding.severity === "blocked") score -= 12;
    if (finding.severity === "warning") score -= 5;
    if (finding.severity === "info") score -= 1;
  }
  const calendar = metrics.find((item) => item.id === "calendar_coverage")?.value ?? 0;
  if (calendar < 60) score -= 8;
  return Math.max(0, Math.min(100, Math.round(score)));
}

function countFindings(findings: SupplierDataQualityFinding[]) {
  return {
    ok: findings.filter((item) => item.severity === "ok").length,
    info: findings.filter((item) => item.severity === "info").length,
    warning: findings.filter((item) => item.severity === "warning").length,
    blocked: findings.filter((item) => item.severity === "blocked").length
  };
}

function finding(id: string, area: SupplierDataQualityArea, severity: SupplierDataQualitySeverity, title: string, description: string, evidence: string, recommendedAction: string, owner: SupplierDataQualityFinding["owner"]): SupplierDataQualityFinding {
  return { id, area, severity, title, description, evidence, recommendedAction, owner };
}

function metric(id: string, label: string, value: number, unit: SupplierDataQualityMetric["unit"], interpretation: string): SupplierDataQualityMetric {
  return { id, label, value, unit, interpretation };
}

function percentage(numerator: number, denominator: number): number {
  if (denominator <= 0) return 0;
  return Math.round((numerator / denominator) * 100);
}

function normalize(value: string): string {
  return value.trim().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, " ");
}

function looksLikeTime(value: string): boolean {
  return /^\d{2}:\d{2}$/.test(value);
}

function ageInDays(value: string, now: string): number {
  const delta = new Date(now).getTime() - new Date(value).getTime();
  if (!Number.isFinite(delta)) return 999;
  return Math.max(0, Math.floor(delta / MS_PER_DAY));
}
