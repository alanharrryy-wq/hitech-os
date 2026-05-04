import type {
  CashImpact,
  PurchaseRecommendationAction,
  PurchaseRecommendationPriority,
  PurchaseSimulationInput,
  PurchaseSimulationResult,
  SmartPurchaseLine,
  SmartPurchaseRecommendation,
  SmartPurchaseSignal,
  SupplierAccount,
  SupplierPayable,
  SupplierProductLink
} from "./types";

const DAY_MS = 24 * 60 * 60 * 1000;

export interface SmartPurchaseEngineInput {
  now: string;
  availableCashCents: number;
  reserveCashCents: number;
  suppliers: SupplierAccount[];
  productLinks: SupplierProductLink[];
  payables: SupplierPayable[];
}

export interface SmartPurchaseEngineOutput {
  signals: SmartPurchaseSignal[];
  recommendations: SmartPurchaseRecommendation[];
}

export function buildSmartPurchaseOutput(input: SmartPurchaseEngineInput): SmartPurchaseEngineOutput {
  const suppliersById = new Map(input.suppliers.map((supplier) => [supplier.id, supplier]));
  const payablesSoon = input.payables.filter((payable) => payable.status === "due_soon" || payable.status === "overdue");
  const signals: SmartPurchaseSignal[] = [];
  const linesBySupplier = new Map<string, SmartPurchaseLine[]>();

  for (const link of input.productLinks) {
    const supplier = suppliersById.get(link.supplierId);
    const coverageBefore = calculateCoverageDays(link.currentStockUnits, link.averageDailySalesUnits);
    const targetCoverageDays = supplier?.visitRule ? Math.max(5, supplier.visitRule.leadTimeDays + 5) : 5;
    const suggestedUnitsRaw = Math.max(0, Math.ceil(link.averageDailySalesUnits * targetCoverageDays - link.currentStockUnits));
    const suggestedPackages = suggestedUnitsRaw > 0 ? Math.max(1, Math.ceil(suggestedUnitsRaw / Math.max(1, link.packageSize))) : 0;
    const suggestedUnits = suggestedPackages * Math.max(1, link.packageSize);
    const coverageAfter = calculateCoverageDays(link.currentStockUnits + suggestedUnits, link.averageDailySalesUnits);
    const estimatedCostCents = suggestedUnits * link.recentCostCents;
    const reasons: string[] = [];

    let priority: PurchaseRecommendationPriority = "safe";
    let action: PurchaseRecommendationAction = "create_order";

    if (!supplier) {
      priority = "configure";
      action = "configure_supplier";
      reasons.push("El producto no tiene proveedor asociado; no se recomienda comprar a ciegas.");
      signals.push(signal(link, "missing_supplier", "high", "Producto sin proveedor asociado.", input.now));
    } else if (supplier.status === "blocked") {
      priority = "blocked";
      action = "block_purchase";
      reasons.push("Proveedor bloqueado; no debe usarse para pedidos hasta revisar motivo.");
    } else if (supplier.status === "paused") {
      priority = "blocked";
      action = "simulate";
      reasons.push("Proveedor pausado; revisar pagos, condiciones o proveedor alterno.");
    }

    if (coverageBefore <= 1.5) {
      priority = priority === "blocked" ? priority : "critical";
      reasons.push("Cobertura menor a dos días; riesgo claro de quiebre.");
      signals.push(signal(link, "stockout_risk", "critical", `${link.name} tiene ${coverageBefore.toFixed(1)} días de cobertura.`, input.now));
    } else if (coverageBefore <= 3) {
      priority = priority === "blocked" ? priority : "high";
      reasons.push("Cobertura baja contra venta promedio diaria.");
      signals.push(signal(link, "low_coverage", "high", `${link.name} está debajo de cobertura cómoda.`, input.now));
    } else if (coverageBefore >= 9) {
      priority = priority === "blocked" ? priority : "wait";
      action = "wait";
      reasons.push("Cobertura alta; comprar ahora puede enterrar caja en producto lento.");
      signals.push(signal(link, "slow_rotation", "medium", `${link.name} tiene cobertura alta.`, input.now));
    }

    if (supplier?.visitRule && daysUntil(input.now, supplier.visitRule.nextVisitDate) <= 2 && priority !== "wait" && priority !== "blocked") {
      reasons.push("Proveedor con visita próxima; conviene preparar pedido antes del corte.");
      signals.push(signal(link, "supplier_soon", "medium", `${supplier.tradeName} visita pronto.`, input.now));
    }

    if (isCostStale(link.lastCostUpdateAt, input.now)) {
      action = priority === "critical" || priority === "high" ? "review_cost" : action;
      reasons.push("Costo reciente necesita revisión antes de aprobar compra grande.");
      signals.push(signal(link, "cost_stale", "medium", `${link.name} tiene costo sin revisión reciente.`, input.now));
    }

    if (suggestedUnits <= 0 && priority !== "wait" && priority !== "blocked" && priority !== "configure") {
      priority = "wait";
      action = "wait";
      reasons.push("Existencia suficiente para la cobertura objetivo.");
    }

    const line: SmartPurchaseLine = {
      id: `line_${link.id}`,
      productId: link.productId,
      sku: link.sku,
      productName: link.name,
      supplierId: supplier?.id,
      supplierName: supplier?.tradeName,
      suggestedUnits,
      packageSize: link.packageSize,
      suggestedPackages,
      currentStockUnits: link.currentStockUnits,
      averageDailySalesUnits: link.averageDailySalesUnits,
      coverageDaysBefore: round1(coverageBefore),
      coverageDaysAfter: round1(coverageAfter),
      unitCostCents: link.recentCostCents,
      estimatedCostCents,
      marginBps: link.grossMarginBps,
      priority,
      reasons: compactReasons(reasons),
      riskIfSkipped: buildSkippedRisk(priority, supplier?.tradeName),
      riskIfOverbought: buildOverboughtRisk(priority),
      action
    };

    const groupKey = supplier?.id ?? "missing_supplier";
    const group = linesBySupplier.get(groupKey) ?? [];
    group.push(line);
    linesBySupplier.set(groupKey, group);
  }

  const recommendations: SmartPurchaseRecommendation[] = [];
  for (const [supplierId, lines] of linesBySupplier.entries()) {
    const actionable = lines.filter((line) => line.priority !== "wait" || line.action === "review_cost");
    const noBuy = lines.filter((line) => line.priority === "wait");
    const selected = actionable.length ? actionable : noBuy.slice(0, 6);
    if (!selected.length) continue;

    const supplier = suppliersById.get(supplierId);
    const total = selected.reduce((sum, line) => sum + line.estimatedCostCents, 0);
    const dueSoon = payablesSoon.reduce((sum, payable) => sum + payable.amountCents, 0);
    const safeBudget = Math.max(0, input.availableCashCents - input.reserveCashCents - dueSoon);
    const cashAfter = input.availableCashCents - dueSoon - total;
    const cashImpact = classifyCashImpact(total, safeBudget, cashAfter, input.reserveCashCents);
    const priority = rankRecommendationPriority(selected, cashImpact, supplier);
    const action = pickRecommendationAction(selected, cashImpact, supplier);
    const supplierName = supplier?.tradeName ?? "Proveedor por configurar";

    recommendations.push({
      id: `rec_${supplierId}`,
      supplierId: supplier?.id,
      supplierName,
      priority,
      action,
      cashImpact,
      title: buildRecommendationTitle(priority, supplierName),
      summary: buildRecommendationSummary(priority, selected, cashImpact),
      generatedAt: input.now,
      idealOrderDate: supplier?.visitRule?.nextOrderCutoff ?? input.now,
      expectedReceptionDate: supplier?.visitRule?.nextVisitDate ?? input.now,
      expectedPaymentDate: supplier ? addDays(supplier.visitRule?.nextVisitDate ?? input.now, supplier.terms.creditDays) : input.now,
      estimatedTotalCents: total,
      safeBudgetCents: safeBudget,
      cashAfterPurchaseCents: cashAfter,
      lines: selected.sort(sortLinesByPriority),
      reasons: buildGroupReasons(selected, supplier, cashImpact),
      auditRequired: priority === "critical" || cashImpact === "tight" || cashImpact === "blocked",
      blockedReason: cashImpact === "blocked" ? "La compra rebasa el presupuesto seguro o deja caja por debajo de la reserva." : undefined
    });
  }

  return {
    signals: signals.sort((a, b) => severityWeight(b.severity) - severityWeight(a.severity)),
    recommendations: recommendations.sort(sortRecommendations)
  };
}

export function simulatePurchase(input: PurchaseSimulationInput, recommendations: SmartPurchaseRecommendation[]): PurchaseSimulationResult {
  const recommendation = recommendations.find((item) => item.id === input.recommendationId);
  if (!recommendation) {
    throw new Error(`Recommendation not found: ${input.recommendationId}`);
  }

  const includedLines = recommendation.lines
    .filter((line) => !input.excludedLineIds.includes(line.id))
    .map((line) => {
      const override = input.quantityOverrides[line.id];
      if (override === undefined) return line;
      const normalizedUnits = Math.max(0, Math.ceil(override / Math.max(1, line.packageSize)) * line.packageSize);
      return {
        ...line,
        suggestedUnits: normalizedUnits,
        suggestedPackages: normalizedUnits / Math.max(1, line.packageSize),
        estimatedCostCents: normalizedUnits * line.unitCostCents,
        coverageDaysAfter: round1(calculateCoverageDays(line.currentStockUnits + normalizedUnits, line.averageDailySalesUnits))
      };
    });
  const excludedLines = recommendation.lines.filter((line) => input.excludedLineIds.includes(line.id));
  const simulatedTotal = includedLines.reduce((sum, line) => sum + line.estimatedCostCents, 0);
  const cashAfter = input.budgetCents - simulatedTotal;
  const cashImpact = classifyCashImpact(simulatedTotal, input.budgetCents, cashAfter, Math.round(input.budgetCents * 0.2));
  const warnings = buildSimulationWarnings(includedLines, excludedLines, cashImpact);

  return {
    recommendationId: recommendation.id,
    includedLines,
    excludedLines,
    originalTotalCents: recommendation.estimatedTotalCents,
    simulatedTotalCents: simulatedTotal,
    cashAfterPurchaseCents: cashAfter,
    cashImpact,
    warnings,
    coverageSummary: summarizeCoverage(includedLines),
    canCreateOrder: includedLines.length > 0 && cashImpact !== "blocked"
  };
}

function calculateCoverageDays(stock: number, averageDailySales: number): number {
  if (averageDailySales <= 0) return stock > 0 ? 99 : 0;
  return stock / averageDailySales;
}

function daysUntil(now: string, target: string): number {
  return Math.ceil((new Date(target).getTime() - new Date(now).getTime()) / DAY_MS);
}

function addDays(date: string, days: number): string {
  return new Date(new Date(date).getTime() + days * DAY_MS).toISOString();
}

function isCostStale(lastCostUpdateAt: string, now: string): boolean {
  return daysUntil(lastCostUpdateAt, now) > 14;
}

function signal(link: SupplierProductLink, signal: SmartPurchaseSignal["signal"], severity: SmartPurchaseSignal["severity"], evidence: string, now: string): SmartPurchaseSignal {
  return { id: `sig_${link.id}_${signal}`, supplierId: link.supplierId, productId: link.productId, sku: link.sku, productName: link.name, signal, severity, evidence, detectedAt: now };
}

function compactReasons(reasons: string[]): string[] {
  return [...new Set(reasons)].slice(0, 5);
}

function classifyCashImpact(total: number, safeBudget: number, cashAfter: number, reserve: number): CashImpact {
  if (total <= 0) return "safe";
  if (total > safeBudget || cashAfter < 0) return "blocked";
  if (cashAfter < reserve) return "tight";
  if (total > safeBudget * 0.72) return "careful";
  return "safe";
}

function rankRecommendationPriority(lines: SmartPurchaseLine[], cashImpact: CashImpact, supplier?: SupplierAccount): PurchaseRecommendationPriority {
  if (!supplier) return "configure";
  if (supplier.status === "blocked" || cashImpact === "blocked") return "blocked";
  if (lines.some((line) => line.priority === "critical")) return "critical";
  if (lines.some((line) => line.priority === "high")) return "high";
  if (lines.every((line) => line.priority === "wait")) return "wait";
  return "safe";
}

function pickRecommendationAction(lines: SmartPurchaseLine[], cashImpact: CashImpact, supplier?: SupplierAccount): PurchaseRecommendationAction {
  if (!supplier) return "configure_supplier";
  if (supplier.status === "blocked" || cashImpact === "blocked") return "block_purchase";
  if (lines.some((line) => line.action === "review_cost")) return "review_cost";
  if (lines.every((line) => line.action === "wait")) return "wait";
  return "create_order";
}

function buildRecommendationTitle(priority: PurchaseRecommendationPriority, supplierName: string): string {
  const map: Record<PurchaseRecommendationPriority, string> = {
    critical: `Compra crítica con ${supplierName}`,
    high: `Compra prioritaria con ${supplierName}`,
    safe: `Compra segura con ${supplierName}`,
    wait: `No comprar ahora con ${supplierName}`,
    blocked: `Compra para revisar con ${supplierName}`,
    configure: `Configurar proveedor para recomendar compra`
  };
  return map[priority];
}

function buildRecommendationSummary(priority: PurchaseRecommendationPriority, lines: SmartPurchaseLine[], cashImpact: CashImpact): string {
  const criticalCount = lines.filter((line) => line.priority === "critical").length;
  const highCount = lines.filter((line) => line.priority === "high").length;
  if (priority === "wait") return "Hay cobertura suficiente; conviene proteger caja y no repetir compra por costumbre.";
  if (priority === "configure") return "Hay productos con riesgo, pero falta información de proveedor para comprar con evidencia.";
  if (priority === "blocked") return "La compra necesita revisión operativa o financiera. Revisa proveedor, caja o pagos antes de aprobar.";
  return `${criticalCount} productos críticos y ${highCount} prioritarios. Impacto en caja: ${cashImpact}.`;
}

function buildSkippedRisk(priority: PurchaseRecommendationPriority, supplierName?: string): string {
  if (priority === "critical") return `Puede haber quiebre antes de la próxima visita${supplierName ? ` de ${supplierName}` : " del proveedor"}.`;
  if (priority === "high") return "Puede caer cobertura y forzar compra de emergencia.";
  if (priority === "wait") return "Riesgo bajo; esperar protege caja.";
  if (priority === "blocked") return "Comprar sin resolver la causa puede generar inventario o deuda mal registrada.";
  return "Riesgo controlado si se revisa antes del siguiente corte.";
}

function buildOverboughtRisk(priority: PurchaseRecommendationPriority): string {
  if (priority === "wait") return "Comprar ahora puede dejar dinero dormido y ocupar espacio sin necesidad.";
  if (priority === "critical") return "Comprar de más puede apretar caja, pero el riesgo de quiebre es más alto.";
  if (priority === "blocked") return "Comprar de más agrava el riesgo financiero u operativo.";
  return "Comprar de más puede generar sobreinventario si cambia la rotación.";
}

function buildGroupReasons(lines: SmartPurchaseLine[], supplier: SupplierAccount | undefined, cashImpact: CashImpact): string[] {
  const reasons = new Set<string>();
  if (!supplier) reasons.add("Falta proveedor asociado para convertir señal en pedido confiable.");
  if (supplier?.visitRule) reasons.add(`Próxima visita: ${supplier.visitRule.nextVisitDate}. Corte de pedido: ${supplier.visitRule.nextOrderCutoff}.`);
  if (cashImpact === "tight") reasons.add("La compra cabe, pero deja caja apretada después de pagos próximos.");
  if (cashImpact === "blocked") reasons.add("La compra rebasa presupuesto seguro.");
  for (const line of lines.slice(0, 5)) for (const reason of line.reasons) reasons.add(`${line.productName}: ${reason}`);
  return [...reasons].slice(0, 8);
}

function buildSimulationWarnings(included: SmartPurchaseLine[], excluded: SmartPurchaseLine[], cashImpact: CashImpact): string[] {
  const warnings: string[] = [];
  if (cashImpact === "blocked") warnings.push("La simulación deja caja negativa o rebasa el presupuesto seguro.");
  if (cashImpact === "tight") warnings.push("La simulación es posible, pero deja poca caja libre.");
  for (const line of excluded) {
    if (line.priority === "critical") warnings.push(`Quitaste ${line.productName}, que estaba marcado como crítico.`);
  }
  if (!included.length) warnings.push("No hay productos incluidos para crear pedido.");
  return warnings;
}

function summarizeCoverage(lines: SmartPurchaseLine[]): string {
  if (!lines.length) return "Sin cobertura recalculada porque no hay líneas incluidas.";
  const avgBefore = lines.reduce((sum, line) => sum + line.coverageDaysBefore, 0) / lines.length;
  const avgAfter = lines.reduce((sum, line) => sum + line.coverageDaysAfter, 0) / lines.length;
  return `Cobertura promedio: ${round1(avgBefore)} días antes, ${round1(avgAfter)} días después.`;
}

function sortLinesByPriority(a: SmartPurchaseLine, b: SmartPurchaseLine): number {
  return priorityWeight(b.priority) - priorityWeight(a.priority) || b.estimatedCostCents - a.estimatedCostCents;
}

function sortRecommendations(a: SmartPurchaseRecommendation, b: SmartPurchaseRecommendation): number {
  return priorityWeight(b.priority) - priorityWeight(a.priority) || b.estimatedTotalCents - a.estimatedTotalCents;
}

function priorityWeight(priority: PurchaseRecommendationPriority): number {
  return { critical: 6, high: 5, safe: 4, configure: 3, blocked: 2, wait: 1 }[priority];
}

function severityWeight(severity: SmartPurchaseSignal["severity"]): number {
  return { critical: 4, high: 3, medium: 2, low: 1 }[severity];
}

function round1(value: number): number {
  return Math.round(value * 10) / 10;
}
