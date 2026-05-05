import type {
  SupplierAuditEvent,
  SupplierDashboardSnapshot,
  SupplierPayable,
  SupplierPurchaseOrder,
  SupplierReceivingReceipt,
  SmartPurchaseRecommendation
} from "./types";

export interface SupplierExportFile {
  filename: string;
  mimeType: "text/csv" | "application/json";
  description: string;
  rows: number;
  content: string;
}

type ExportRow = Record<string, string | number | boolean>;

export interface SupplierExportBundle {
  generatedAt: string;
  files: SupplierExportFile[];
  summary: {
    orders: number;
    receipts: number;
    payables: number;
    recommendations: number;
    auditEvents: number;
  };
}

export function buildSupplierExportBundle(snapshot: SupplierDashboardSnapshot): SupplierExportBundle {
  const files: SupplierExportFile[] = [
    buildOrdersCsv(snapshot.openOrders),
    buildReceivingsCsv(snapshot.receivingQueue),
    buildPayablesCsv(snapshot.payables),
    buildRecommendationsCsv(snapshot.recommendations),
    buildAuditCsv(snapshot.lifecycle.auditEvents),
    buildSurfaceSignalsCsv(snapshot)
  ];
  return {
    generatedAt: snapshot.generatedAt,
    files,
    summary: {
      orders: snapshot.openOrders.length,
      receipts: snapshot.receivingQueue.length,
      payables: snapshot.payables.length,
      recommendations: snapshot.recommendations.length,
      auditEvents: snapshot.lifecycle.auditEvents.length
    }
  };
}

export function buildOrdersCsv(orders: SupplierPurchaseOrder[]): SupplierExportFile {
  const rows = orders.flatMap((order) => order.lines.map((line) => ({
    folio: order.folio,
    proveedor: order.supplierName,
    estado: order.status,
    fuente: order.source,
    fecha_creacion: order.createdAt,
    recepcion_esperada: order.expectedReceptionDate,
    pago_estimado: order.expectedPaymentDate,
    sku: line.sku,
    producto: line.name,
    unidades_pedidas: line.orderedUnits,
    unidades_recibidas: line.receivedUnits,
    costo_unitario: money(line.unitCostCents),
    total_linea: money(line.expectedTotalCents),
    total_pedido: money(order.totalCents)
  })));
  return csvFile("proveedores_pedidos.csv", "Pedidos y lineas para revision operativa.", rows);
}

export function buildReceivingsCsv(receipts: SupplierReceivingReceipt[]): SupplierExportFile {
  const rows: ExportRow[] = receipts.flatMap((receipt): ExportRow[] => {
    if (!receipt.differences.length) return [{
      recepcion: receipt.id,
      pedido: receipt.orderId ?? "recepcion libre",
      proveedor: receipt.supplierName,
      estado: receipt.status,
      esperada: receipt.expectedAt,
      recibida: receipt.receivedAt ?? "pendiente",
      sku: "",
      producto: "",
      esperado: 0,
      recibido: 0,
      diferencia: 0,
      motivo: "",
      nota: ""
    }];
    return receipt.differences.map((difference) => ({
      recepcion: receipt.id,
      pedido: receipt.orderId ?? "recepcion libre",
      proveedor: receipt.supplierName,
      estado: receipt.status,
      esperada: receipt.expectedAt,
      recibida: receipt.receivedAt ?? "pendiente",
      sku: difference.sku,
      producto: difference.name,
      esperado: difference.expectedUnits,
      recibido: difference.receivedUnits,
      diferencia: difference.receivedUnits - difference.expectedUnits,
      motivo: difference.reason,
      nota: difference.note
    }));
  });
  return csvFile("proveedores_recepciones.csv", "Recepciones, diferencias y motivos visibles.", rows);
}

export function buildPayablesCsv(payables: SupplierPayable[]): SupplierExportFile {
  const rows = payables.map((payable) => ({
    cuenta: payable.id,
    proveedor: payable.supplierName,
    pedido: payable.orderId ?? "sin pedido",
    vencimiento: payable.dueDate,
    monto: money(payable.amountCents),
    estado: payable.status,
    notas: payable.notes ?? ""
  }));
  return csvFile("proveedores_cuentas_por_pagar.csv", "Cuentas por pagar, vencimientos e impacto de caja.", rows);
}

export function buildRecommendationsCsv(recommendations: SmartPurchaseRecommendation[]): SupplierExportFile {
  const rows: ExportRow[] = recommendations.flatMap((recommendation): ExportRow[] => recommendation.lines.length ? recommendation.lines.map((line): ExportRow => ({
    recomendacion: recommendation.id,
    proveedor: recommendation.supplierName,
    prioridad: recommendation.priority,
    accion: recommendation.action,
    impacto_caja: recommendation.cashImpact,
    compra_estimado: money(recommendation.estimatedTotalCents),
    presupuesto_seguro: money(recommendation.safeBudgetCents),
    caja_despues: money(recommendation.cashAfterPurchaseCents),
    sku: line.sku,
    producto: line.productName,
    unidades_sugeridas: line.suggestedUnits,
    paquetes_sugeridos: line.suggestedPackages,
    cobertura_antes: line.coverageDaysBefore,
    cobertura_despues: line.coverageDaysAfter,
    razones: line.reasons.join(" | "),
    riesgo_si_no_compra: line.riskIfSkipped,
    riesgo_si_compra_de_mas: line.riskIfOverbought
  })) : [{
    recomendacion: recommendation.id,
    proveedor: recommendation.supplierName,
    prioridad: recommendation.priority,
    accion: recommendation.action,
    impacto_caja: recommendation.cashImpact,
    compra_estimado: money(recommendation.estimatedTotalCents),
    presupuesto_seguro: money(recommendation.safeBudgetCents),
    caja_despues: money(recommendation.cashAfterPurchaseCents),
    sku: "",
    producto: recommendation.title,
    unidades_sugeridas: 0,
    paquetes_sugeridos: 0,
    cobertura_antes: 0,
    cobertura_despues: 0,
    razones: recommendation.reasons.join(" | "),
    riesgo_si_no_compra: recommendation.summary,
    riesgo_si_compra_de_mas: recommendation.blockedReason ?? ""
  }]);
  return csvFile("proveedores_compra_inteligente.csv", "Recomendaciones explicables y lineas sugeridas.", rows);
}

export function buildAuditCsv(events: SupplierAuditEvent[]): SupplierExportFile {
  const rows = events.map((event) => ({
    fecha: event.createdAt,
    tema: event.topic,
    actor: event.actor.name,
    rol: event.actor.role,
    entidad: event.entityType,
    entidad_id: event.entityId,
    proveedor: event.supplierName ?? "",
    motivo: event.reason,
    origen: event.source,
    requiere_revision: event.requiresReview ? "si" : "no",
    resumen: event.visibleSummary
  }));
  return csvFile("proveedores_auditoria.csv", "Rastro visible de acciones sensibles.", rows);
}

export function buildSurfaceSignalsCsv(snapshot: SupplierDashboardSnapshot): SupplierExportFile {
  const rows = snapshot.lifecycle.surfaceSignals.map((signal) => ({
    superficie: signal.surface,
    titulo: signal.title,
    mensaje: signal.message,
    severidad: signal.severity,
    accion: signal.allowedAction,
    accion_prohibida: signal.forbiddenAction
  }));
  return csvFile("proveedores_senales_tablet_app.csv", "Senales ligeras para Tablet y App movil sin backoffice pesado.", rows);
}

export function toCsv(rows: ExportRow[]): string {
  if (!rows.length) return "";
  const headers = Object.keys(rows[0]);
  const lines = [headers.join(",")];
  for (const row of rows) lines.push(headers.map((header) => escapeCsv(row[header])).join(","));
  return `${lines.join("\n")}\n`;
}

function csvFile(filename: string, description: string, rows: ExportRow[]): SupplierExportFile {
  return { filename, mimeType: "text/csv", description, rows: rows.length, content: toCsv(rows) };
}

function escapeCsv(value: unknown): string {
  const raw = value == null ? "" : String(value);
  if (!/[",\n]/.test(raw)) return raw;
  return `"${raw.replace(/"/g, '""')}"`;
}

function money(cents: number): string {
  return (cents / 100).toFixed(2);
}
