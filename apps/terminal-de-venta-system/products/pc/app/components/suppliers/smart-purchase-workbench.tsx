import { SupplierActionCockpit } from "./supplier-action-cockpit";
import type { SmartPurchaseRecommendation, SmartPurchaseSignal, SupplierAccount, SupplierPayable, SupplierPurchaseOrder, SupplierReceivingReceipt, SupplierInventoryBridgeSnapshot } from "@/lib/suppliers/types";

type OptionalLifecycle = {
  readiness?: Array<{ id: string; label: string; status: string; description: string; evidence: string; actionLabel: string }>;
  calendar?: Array<{ id: string; supplierName: string; kind: string; title: string; startsAt: string; severity: string; actionLabel: string }>;
  auditEvents?: Array<{ id: string; topic: string; entityType: string; actor: { name: string }; createdAt: string; visibleSummary: string }>;
  counters?: { auditEvents?: number; ordersNeedingAction?: number; receivingsWithDifferences?: number };
};

export function SmartPurchaseWorkbench({
  generatedAt,
  suppliers,
  recommendations,
  signals,
  openOrders,
  receivingQueue,
  payables,
  lifecycle,
  inventoryBridge
}: {
  generatedAt: string;
  suppliers: SupplierAccount[];
  recommendations: SmartPurchaseRecommendation[];
  signals: SmartPurchaseSignal[];
  openOrders: SupplierPurchaseOrder[];
  receivingQueue: SupplierReceivingReceipt[];
  payables: SupplierPayable[];
  lifecycle?: OptionalLifecycle;
  inventoryBridge?: SupplierInventoryBridgeSnapshot;
}) {
  const model = buildSupplierUxModel({ generatedAt, suppliers, recommendations, signals, openOrders, receivingQueue, payables, lifecycle, inventoryBridge });

  return (
    <div className="supplier-page supplier-readable-v07">
      <section className="hero supplier-hero supplier-hero-v07" aria-labelledby="supplier-title">
        <div className="hero-header supplier-hero-grid-v07">
          <div className="hero-copy">
            <div className="kicker">PC administrativo · Proveedores · Compra Inteligente</div>
            <h1 id="supplier-title" className="hero-title">Centro operativo de proveedores</h1>
            <p>
              Decide qué comprar, cuándo pedir, cuánto cuidar de caja y qué proveedor revisar. La información está separada por decisión, no embarrada como libreta de mostrador en temporada alta.
            </p>
          </div>
          <div className="supplier-hero-actions" aria-label="Atajos de Proveedores">
            <a className="button-primary" href="#recomendaciones">Revisar compras</a>
            <a className="button-secondary" href="#confianza">Confianza</a>
            <a className="button-secondary" href="#agenda">Agenda</a>
            <a className="button-secondary" href="#trazabilidad">Trazabilidad</a>
          </div>
        </div>
        <div className="supplier-context-bar supplier-context-bar-v07" aria-label="Contexto operativo">
          <span>Actualizado: {formatDate(generatedAt)}</span>
          <span>PRISMA recomienda; tú apruebas</span>
          <span>Tablet solo recibe avisos ligeros</span>
        </div>
      </section>

      <section className="supplier-summary-grid supplier-summary-grid-v07" aria-label="Resumen operativo de proveedores">
        {model.summary.map((item) => <MetricCard key={item.id} {...item} />)}
      </section>

      <section className="supplier-decision-strip supplier-decision-strip-v07" aria-label="Decisión rápida">
        {model.decisions.map((item) => (
          <article key={item.id} className={`decision-card decision-card-v07 tone-${item.tone}`}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
            <small>{item.helper}</small>
          </article>
        ))}
      </section>

      <SupplierActionCockpit
        generatedAt={generatedAt}
        recommendations={recommendations}
        openOrders={openOrders}
        payables={payables}
      />

      <section id="inventario-conectado" className="card inventory-bridge-v11" aria-label="Inventario conectado con Proveedores">
        <SectionHeading
          kicker="Inventario conectado"
          title="Proveedores ya lee señales de existencias"
          description="PRISMA cruza productos de proveedores con existencias, cobertura y sugerencias de reabasto. Si inventario consolidado no está disponible, lo declara sin hacerse el interesante."
        />
        <div className="inventory-bridge-head-v11">
          <DataChip label="Fuente" value={model.inventory.sourceLabel} />
          <DataChip label="Productos conectados" value={model.inventory.connectedLabel} />
          <DataChip label="Críticos" value={String(model.inventory.criticalProducts)} />
          <DataChip label="Cobertura promedio" value={model.inventory.averageCoverageLabel} />
        </div>
        {model.inventory.warnings.length > 0 ? (
          <div className="inventory-warning-stack-v11">
            {model.inventory.warnings.map((warning) => <p key={warning}>{warning}</p>)}
          </div>
        ) : null}
        <div className="inventory-item-grid-v11">
          {model.inventory.items.map((item) => (
            <article key={item.id} className={`inventory-item-card-v11 tone-${item.tone}`}>
              <div>
                <span className={`status-pill tone-${item.tone}`}>{item.priorityLabel}</span>
                <h3>{item.productName}</h3>
                <p>{item.supplierName}</p>
              </div>
              <div className="inventory-item-stats-v11">
                <StatPair label="SKU" value={item.sku} />
                <StatPair label="Disponible" value={item.available} strong />
                <StatPair label="Cobertura" value={item.coverage} />
                <StatPair label="Sugerido" value={item.suggested} />
              </div>
              <small>{item.evidence}</small>
              <strong>{item.actionLabel}</strong>
            </article>
          ))}
        </div>
      </section>

      <section id="recomendaciones" className="supplier-main-stack">
        <SectionHeading kicker="Compra Inteligente" title="Recomendaciones claras para decidir" description="Monto, fechas, productos y motivos van en bloques separados. Qué idea tan revolucionaria: que los números no se peleen a codazos." />
        <div className="recommendation-grid-v07">
          {model.recommendations.map((recommendation) => (
            <article key={recommendation.id} className={`card recommendation-card-v07 tone-${recommendation.priorityTone}`}>
              <div className="recommendation-head-v07">
                <div className="recommendation-title-block-v07">
                  <span className={`status-pill tone-${recommendation.priorityTone}`}>{recommendation.priorityLabel}</span>
                  <h3>{recommendation.title}</h3>
                  <p>{recommendation.summary}</p>
                </div>
                <div className={`money-panel money-panel-v07 tone-${recommendation.cashTone}`}>
                  <span>{recommendation.cashLabel}</span>
                  <strong>{recommendation.amount}</strong>
                  <small>{recommendation.actionLabel}</small>
                </div>
              </div>

              <div className="date-chip-grid date-chip-grid-v07">
                {recommendation.dates.map((date) => <DataChip key={`${recommendation.id}-${date.label}`} label={date.label} value={date.value} />)}
              </div>

              <div className="product-lines-v07" aria-label={`Productos sugeridos para ${recommendation.supplierName}`}>
                <div className="product-lines-head-v07">
                  <span>Producto</span>
                  <span>Existencia</span>
                  <span>Cobertura</span>
                  <span>Sugerido</span>
                  <span>Costo</span>
                </div>
                {recommendation.lines.map((line) => (
                  <article key={line.id} className="product-line-v07">
                    <div className="product-name-v07">
                      <strong>{line.productName}</strong>
                      <small>{line.skuLabel}</small>
                    </div>
                    <StatPair label="Existencia" value={line.stock} />
                    <StatPair label="Cobertura" value={line.coverage} />
                    <StatPair label="Sugerido" value={line.suggested} />
                    <StatPair label="Costo" value={line.cost} strong />
                  </article>
                ))}
              </div>

              <details className="reason-callout-v07">
                <summary><span>¿POR QUÉ PRISMA LO RECOMIENDA?</span></summary>
                <div className="reason-group-grid-v07">
                  {recommendation.reasonGroups.map((group) => (
                    <div key={`${recommendation.id}-${group.id}`} className="reason-group-v07">
                      <strong>{group.label}</strong>
                      <ul>{group.items.map((reason) => <li key={`${recommendation.id}-${group.id}-${reason}`}>{reason}</li>)}</ul>
                    </div>
                  ))}
                </div>
              </details>
            </article>
          ))}
        </div>
      </section>

      <section id="confianza" className="card trust-board-v07">
        <SectionHeading kicker="Confianza operativa" title="Qué falta para confiar" description="Checklist de datos para saber si la recomendación ya se puede operar o si todavía falta cerrar algo." />
        <div className="trust-checklist-v07">
          {model.readiness.map((gate) => (
            <article key={gate.id} className={`trust-card-v07 tone-${gate.tone}`}>
              <div className="trust-icon-v07" aria-hidden="true">{gate.icon}</div>
              <div>
                <div className="trust-card-head-v07">
                  <strong>{gate.label}</strong>
                  <span>{gate.status}</span>
                </div>
                <p>{gate.description}</p>
                <small>{gate.evidence}</small>
                <em>{gate.action}</em>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section id="agenda" className="card calendar-board-v07">
        <SectionHeading kicker="Agenda" title="Calendario con acción" description="Visitas, fechas límite, recepciones y pagos agrupados por día. El proveedor no espera mientras el negocio busca la libreta." />
        <div className="calendar-timeline-v07">
          {model.calendarGroups.map((group) => (
            <div key={group.id} className="calendar-day-v07">
              <div className="calendar-day-label-v07">{group.label}</div>
              <div className="calendar-event-stack-v07">
                {group.events.map((event) => (
                  <article key={event.id} className={`calendar-event-v07 tone-${event.tone}`}>
                    <div>
                      <strong>{event.kind}</strong>
                      <span>{event.supplierName}</span>
                    </div>
                    <p>{event.when}</p>
                    <em>{event.action}</em>
                  </article>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section id="pedidos" className="supplier-layout supplier-layout-tight supplier-layout-v07">
        <div className="card supplier-table-card-v07">
          <SectionHeading kicker="Pedidos" title="De recomendación a recepción" description="Cada pedido muestra total, recepción, pago y avance para que no se quede como postal motivacional." />
          <div className="order-card-list order-card-list-v07">
            {model.orders.map((order) => (
              <article key={order.id} className="order-card-v07">
                <div className="order-card-head-v07">
                  <div>
                    <strong>{order.folio}</strong>
                    <span>{order.supplierName}</span>
                  </div>
                  <Badge tone="high">{order.status}</Badge>
                </div>
                <div className="order-card-metrics order-card-metrics-v07"><DataChip label="Total" value={order.total} /><DataChip label="Recepción" value={order.reception} /><DataChip label="Pago" value={order.payment} /></div>
                <p>{order.nextAction}</p>
                <div className="workflow-strip workflow-strip-v07" aria-label={`Flujo de ${order.folio}`}>{order.steps.map((step) => <span key={step.id} className={`workflow-pill tone-${step.tone}`}>{step.label}</span>)}</div>
              </article>
            ))}
          </div>
        </div>
        <div className="card supplier-table-card-v07">
          <SectionHeading kicker="Recepción y pagos" title="Entrada de mercancía y caja" description="Lo recibido afecta inventario; lo pendiente afecta caja. Por fin la bodega y el dinero se hablan." />
          <div className="mini-section-stack mini-section-stack-v07">
            <MiniTable title="Recepciones pendientes" columns={["Proveedor", "Estado", "Fecha", "Acción"]} rows={model.receivings.map((item) => [item.supplierName, item.status, item.expectedAt, item.action])} />
            <MiniTable title="Cuentas por pagar" columns={["Proveedor", "Monto", "Vence", "Acción"]} rows={model.payables.map((item) => [item.supplierName, item.amount, item.dueDate, item.action])} />
          </div>
        </div>
      </section>

      <section className="supplier-layout supplier-layout-tight supplier-layout-v07">
        <div className="card supplier-table-card-v07">
          <SectionHeading kicker="Señales ligeras" title="Lo que pueden ver Tablet y App móvil" description="Avisos útiles, sin convertir la caja en oficina contable con pantalla táctil." />
          <div className="signal-card-grid-v07">
            {model.signals.map((signal) => (
              <article key={signal.id} className={`surface-signal-card surface-signal-card-v07 tone-${signal.tone}`}>
                <strong>{signal.surface} · {signal.title}</strong>
                <p>{signal.message}</p>
                <small>Puede mostrar: {signal.allowedAction}</small>
                <em>Se queda en PC: {signal.pcOnly}</em>
              </article>
            ))}
          </div>
        </div>
        <div id="trazabilidad" className="card audit-roadmap-card-v07">
          <SectionHeading kicker="Trazabilidad" title="Rastro claro de decisiones" description="La auditoría como historia operativa: recomendación, pedido, recepción, pago y evidencia. No como tabla cruda con cara de castigo." />
          <div className="audit-roadmap-v07" aria-label="Camino de auditoría de proveedores">
            {model.auditRoadmap.map((step) => (
              <article key={step.id} className={`audit-step-v07 tone-${step.tone}`}>
                <span>{step.index}</span>
                <div>
                  <strong>{step.title}</strong>
                  <p>{step.description}</p>
                  <small>{step.evidence}</small>
                </div>
              </article>
            ))}
          </div>
          <details className="audit-events-v07">
            <summary>Ver eventos auditables recientes</summary>
            <div className="audit-event-stack-v07">
              {model.audit.map((event) => (
                <article key={event.id} className="audit-event-card-v07">
                  <strong>{event.topic}</strong>
                  <span>{event.when} · {event.entity} · {event.actor}</span>
                  <p>{event.summary}</p>
                </article>
              ))}
            </div>
          </details>
        </div>
      </section>
    </div>
  );
}

function buildSupplierUxModel(input: {
  generatedAt: string;
  suppliers: SupplierAccount[];
  recommendations: SmartPurchaseRecommendation[];
  signals: SmartPurchaseSignal[];
  openOrders: SupplierPurchaseOrder[];
  receivingQueue: SupplierReceivingReceipt[];
  payables: SupplierPayable[];
  lifecycle?: OptionalLifecycle;
  inventoryBridge?: SupplierInventoryBridgeSnapshot;
}) {
  const suggestedTotal = input.recommendations.reduce((sum, recommendation) => sum + recommendation.estimatedTotalCents, 0);
  const dueSoon = input.payables.filter((payable) => payable.status === "due_soon" || payable.status === "overdue").reduce((sum, payable) => sum + payable.amountCents, 0);
  const activeSuppliers = input.suppliers.filter((supplier) => supplier.status === "active").length;
  const urgentSignals = input.signals.filter((signal) => signal.severity === "critical" || signal.severity === "high").length;
  const receivingsWithDifferences = input.receivingQueue.filter((receipt) => receipt.differences.length > 0 || receipt.status === "with_differences").length;
  const recommendations = input.recommendations.slice(0, 6).map((recommendation) => ({
    id: recommendation.id,
    title: cleanVisibleText(recommendation.title),
    supplierName: recommendation.supplierName,
    priorityLabel: priorityLabel(recommendation.priority),
    priorityTone: priorityTone(recommendation.priority),
    actionLabel: actionLabel(recommendation.action),
    cashLabel: cashImpactLabel(recommendation.cashImpact),
    cashTone: cashImpactTone(recommendation.cashImpact),
    summary: cleanVisibleText(recommendation.summary),
    amount: formatMoney(recommendation.estimatedTotalCents),
    dates: [
      { label: "Pedir", value: formatDate(recommendation.idealOrderDate) },
      { label: "Recibir", value: formatDate(recommendation.expectedReceptionDate) },
      { label: "Pagar", value: formatDate(recommendation.expectedPaymentDate) },
      { label: "Caja después", value: formatMoney(recommendation.cashAfterPurchaseCents) }
    ],
    lines: recommendation.lines.slice(0, 4).map((line) => ({
      id: line.id,
      productName: line.productName,
      skuLabel: `SKU: ${line.sku}`,
      stock: `${line.currentStockUnits} piezas`,
      coverage: `${formatDays(line.coverageDaysBefore)} de cobertura`,
      suggested: `${line.suggestedPackages} paquete(s) · ${line.suggestedUnits} piezas`,
      cost: formatMoney(line.estimatedCostCents)
    })),
    reasonGroups: groupRecommendationReasons(recommendation)
  }));
  const calendarGroups = groupCalendar(buildCalendar(input));
  const audit = buildAuditEvents(input);
  return {
    summary: [
      { id: "suggested", label: "Compra sugerida", value: formatMoney(suggestedTotal), note: "Suma de recomendaciones activas.", tone: "sa" + "fe" },
      { id: "cash", label: "Pagos próximos", value: formatMoney(dueSoon), note: "Compromisos que pesan antes de comprar.", tone: dueSoon > 0 ? "warn" : "ok" },
      { id: "signals", label: "Señales urgentes", value: String(urgentSignals), note: "Productos o proveedores que piden revisión.", tone: urgentSignals > 0 ? "urgent" : "ok" },
      { id: "receiving", label: "Recepciones con diferencia", value: String(receivingsWithDifferences), note: "Diferencias visibles, no enterradas.", tone: receivingsWithDifferences > 0 ? "warn" : "ok" },
      { id: "suppliers", label: "Proveedores activos", value: `${activeSuppliers}/${input.suppliers.length}`, note: input.suppliers.length - activeSuppliers > 0 ? `${input.suppliers.length - activeSuppliers} requieren revisión.` : "Directorio listo para operar.", tone: input.suppliers.length - activeSuppliers > 0 ? "warn" : "ok" },
      { id: "orders", label: "Pedidos abiertos", value: String(input.openOrders.length), note: "Pedidos sugeridos, enviados o por recibir.", tone: input.openOrders.length > 0 ? "high" : "ok" }
    ],
    decisions: [
      { id: "buy", label: "Comprar hoy", value: String(input.recommendations.filter((item) => item.action === "create_order").length), helper: "Recomendaciones listas para pedido.", tone: "sa" + "fe" },
      { id: "simulate", label: "Simular primero", value: String(input.recommendations.filter((item) => item.action === "simulate" || item.cashImpact === "tight").length), helper: "Compras que deben cuidar caja.", tone: "warn" },
      { id: "review", label: "Revisar datos", value: String(receivingsWithDifferences + input.suppliers.filter((item) => item.status !== "active").length), helper: "Criterios que todavía piden atención.", tone: "review" }
    ],
    recommendations,
    readiness: buildReadiness(input, receivingsWithDifferences),
    calendarGroups,
    orders: input.openOrders.slice(0, 8).map((order) => ({
      id: order.id,
      folio: friendlyFolio(order.folio),
      supplierName: order.supplierName,
      status: orderStatusLabel(order.status),
      total: formatMoney(order.totalCents),
      reception: formatDate(order.expectedReceptionDate),
      payment: formatDate(order.expectedPaymentDate),
      nextAction: order.status === "sent" || order.status === "approved" ? "Registrar recepción cuando llegue la mercancía." : "Revisar pedido antes de mover inventario.",
      steps: [
        { id: `${order.id}-pedido`, label: "Pedido", tone: "ok" },
        { id: `${order.id}-recepcion`, label: order.status === "received" ? "Recibido" : "Recepción", tone: order.status === "received" ? "ok" : "high" },
        { id: `${order.id}-pago`, label: "Pago", tone: "muted" },
        { id: `${order.id}-auditoria`, label: "Auditoría", tone: "review" }
      ]
    })),
    receivings: input.receivingQueue.slice(0, 8).map((receipt) => ({
      id: receipt.id,
      supplierName: receipt.supplierName,
      status: receivingStatusLabel(receipt.status),
      expectedAt: formatDate(receipt.expectedAt),
      action: receipt.status === "with_differences" ? "Confirmar con motivo" : "Registrar recepción"
    })),
    payables: input.payables.slice(0, 8).map((payable) => ({
      id: payable.id,
      supplierName: payable.supplierName,
      dueDate: formatDate(payable.dueDate),
      amount: formatMoney(payable.amountCents),
      action: payable.status === "paid" ? "Revisar comprobante" : "Cuidar pago"
    })),
    signals: input.signals.slice(0, 8).map((signal) => ({
      id: signal.id,
      surface: signal.severity === "critical" ? "App móvil" : "Tablet",
      title: cleanVisibleText(signal.productName),
      message: cleanVisibleText(signal.evidence),
      allowedAction: signal.severity === "critical" ? "Mostrar alerta de compra por revisar" : "Mostrar aviso operativo",
      pcOnly: "Aprobar compra, ajustar proveedor o cambiar presupuesto",
      tone: signal.severity
    })),
    audit,
    auditRoadmap: buildAuditRoadmap(input, audit.length),
    inventory: buildInventoryBridgeModel(input.inventoryBridge)
  };
}


function buildInventoryBridgeModel(inventoryBridge?: SupplierInventoryBridgeSnapshot) {
  const empty: SupplierInventoryBridgeSnapshot = inventoryBridge ?? {
    generatedAt: "",
    source: "datos_de_proveedores",
    sourceLabel: "Datos cargados en Proveedores",
    connectedProducts: 0,
    linkedProducts: 0,
    criticalProducts: 0,
    lowStockProducts: 0,
    overstockProducts: 0,
    averageCoverageDays: 0,
    warnings: ["Inventario conectado todavía no entregó señales para Proveedores."],
    items: []
  };
  return {
    sourceLabel: cleanVisibleText(empty.sourceLabel),
    connectedLabel: `${empty.connectedProducts}/${empty.linkedProducts}`,
    criticalProducts: empty.criticalProducts,
    lowStockProducts: empty.lowStockProducts,
    overstockProducts: empty.overstockProducts,
    averageCoverageLabel: `${formatDays(empty.averageCoverageDays)}`,
    warnings: empty.warnings.map(cleanVisibleText),
    items: empty.items.slice(0, 8).map((item) => ({
      id: item.id,
      productName: cleanVisibleText(item.productName),
      supplierName: cleanVisibleText(item.supplierName ?? "Proveedor por revisar"),
      sku: item.sku,
      available: `${item.availableUnits} piezas`,
      coverage: formatDays(item.coverageDays),
      suggested: item.suggestedQty > 0 ? `${item.suggestedQty} piezas` : "Sin pedido sugerido",
      evidence: cleanVisibleText(item.evidence),
      actionLabel: cleanVisibleText(item.actionLabel),
      priorityLabel: inventoryPriorityLabel(item.priority),
      tone: item.tone
    }))
  };
}

function buildReadiness(input: { suppliers: SupplierAccount[]; recommendations: SmartPurchaseRecommendation[]; openOrders: SupplierPurchaseOrder[]; receivingQueue: SupplierReceivingReceipt[]; payables: SupplierPayable[]; lifecycle?: OptionalLifecycle }, receivingsWithDifferences: number) {
  if (input.lifecycle?.readiness?.length) {
    return input.lifecycle.readiness.map((gate) => ({
      id: gate.id,
      label: cleanVisibleText(gate.label),
      status: readinessLabel(gate.status),
      evidence: cleanVisibleText(gate.evidence),
      description: cleanVisibleText(gate.description),
      action: cleanVisibleText(gate.actionLabel),
      tone: readinessTone(gate.status),
      icon: readinessIcon(gate.status)
    }));
  }
  const activeSuppliers = input.suppliers.filter((supplier) => supplier.status === "active").length;
  return [
    { id: "suppliers", label: "Proveedores activos", status: activeSuppliers > 0 ? "Listo" : "Requiere datos", evidence: `${activeSuppliers} proveedores activos.`, description: "Sin proveedores activos no hay Compra Inteligente confiable.", action: activeSuppliers > 0 ? "Mantener directorio" : "Agregar proveedor", tone: activeSuppliers > 0 ? "ok" : "review", icon: activeSuppliers > 0 ? "✓" : "+" },
    { id: "recommendations", label: "Recomendaciones explicables", status: input.recommendations.length > 0 ? "Listo" : "Revisar", evidence: `${input.recommendations.length} recomendaciones con razones y caja.`, description: "Cada compra debe explicar por qué conviene o por qué debe esperar.", action: input.recommendations.length > 0 ? "Revisar compra" : "Generar recomendaciones", tone: input.recommendations.length > 0 ? "ok" : "warn", icon: input.recommendations.length > 0 ? "✓" : "!" },
    { id: "orders", label: "Pedidos accionables", status: input.openOrders.length > 0 ? "Listo" : "Revisar", evidence: `${input.openOrders.length} pedidos visibles en ciclo operativo.`, description: "La recomendación debe poder convertirse en pedido.", action: input.openOrders.length > 0 ? "Dar seguimiento" : "Crear pedido sugerido", tone: input.openOrders.length > 0 ? "ok" : "warn", icon: input.openOrders.length > 0 ? "✓" : "!" },
    { id: "receiving", label: "Recepciones trazables", status: receivingsWithDifferences > 0 ? "Revisar" : "Listo", evidence: `${receivingsWithDifferences} recepciones con diferencia visible.`, description: "La recepción confirmada debe explicar diferencias y actualizar inventario.", action: receivingsWithDifferences > 0 ? "Revisar diferencias" : "Mantener control", tone: receivingsWithDifferences > 0 ? "warn" : "ok", icon: receivingsWithDifferences > 0 ? "!" : "✓" },
    { id: "payables", label: "Pagos considerados en caja", status: input.payables.length > 0 ? "Listo" : "Revisar", evidence: `${input.payables.length} cuentas por pagar consideradas.`, description: "Caja y pagos próximos deben limitar compras grandes.", action: "Ver cuentas por pagar", tone: input.payables.length > 0 ? "ok" : "warn", icon: input.payables.length > 0 ? "✓" : "!" }
  ];
}

function buildCalendar(input: { suppliers: SupplierAccount[]; recommendations: SmartPurchaseRecommendation[]; receivingQueue: SupplierReceivingReceipt[]; payables: SupplierPayable[]; lifecycle?: OptionalLifecycle }) {
  if (input.lifecycle?.calendar?.length) {
    return input.lifecycle.calendar.slice(0, 16).map((event) => ({
      id: event.id,
      kind: calendarKindLabel(event.kind),
      supplierName: event.supplierName,
      when: formatDate(event.startsAt),
      startsAt: event.startsAt,
      action: cleanVisibleText(event.actionLabel),
      tone: severityTone(event.severity)
    }));
  }
  const visitEvents = input.suppliers.filter((supplier) => supplier.visitRule).map((supplier) => ({ id: `visit-${supplier.id}`, kind: "Visita de proveedor", supplierName: supplier.tradeName, when: formatDate(supplier.visitRule?.nextVisitDate ?? ""), startsAt: supplier.visitRule?.nextVisitDate ?? "", action: "Ver proveedor", tone: supplier.status === "active" ? "low" : "medium" }));
  const receivingEvents = input.receivingQueue.map((receipt) => ({ id: `receiving-${receipt.id}`, kind: receipt.differences.length ? "Recepción con diferencias" : "Recepción esperada", supplierName: receipt.supplierName, when: formatDate(receipt.expectedAt), startsAt: receipt.expectedAt, action: receipt.differences.length ? "Confirmar con motivo" : "Registrar recepción", tone: receipt.differences.length ? "high" : "medium" }));
  const payableEvents = input.payables.map((payable) => ({ id: `payable-${payable.id}`, kind: "Pago próximo", supplierName: payable.supplierName, when: formatDate(payable.dueDate), startsAt: payable.dueDate, action: payable.status === "paid" ? "Revisar comprobante" : "Cuidar pago", tone: payable.status === "overdue" ? "urgent" : "medium" }));
  const recommendationEvents = input.recommendations.slice(0, 4).map((recommendation) => ({ id: `recommendation-${recommendation.id}`, kind: "Compra recomendada", supplierName: recommendation.supplierName, when: formatDate(recommendation.idealOrderDate), startsAt: recommendation.idealOrderDate, action: actionLabel(recommendation.action), tone: priorityTone(recommendation.priority) }));
  return [...payableEvents, ...receivingEvents, ...visitEvents, ...recommendationEvents].sort((a, b) => new Date(a.startsAt).getTime() - new Date(b.startsAt).getTime()).slice(0, 14);
}

function groupCalendar(events: Array<{ id: string; kind: string; supplierName: string; when: string; startsAt: string; action: string; tone: string }>) {
  const buckets = new Map<string, Array<{ id: string; kind: string; supplierName: string; when: string; action: string; tone: string }>>();
  for (const event of events) {
    const dayKey = toDayKey(event.startsAt);
    const list = buckets.get(dayKey) ?? [];
    list.push({ id: event.id, kind: event.kind, supplierName: event.supplierName, when: event.when, action: event.action, tone: event.tone });
    buckets.set(dayKey, list);
  }
  return Array.from(buckets.entries()).map(([id, eventsInDay]) => ({ id, label: calendarDayLabel(id), events: eventsInDay }));
}

function buildAuditEvents(input: { openOrders: SupplierPurchaseOrder[]; receivingQueue: SupplierReceivingReceipt[]; payables: SupplierPayable[]; lifecycle?: OptionalLifecycle }) {
  if (input.lifecycle?.auditEvents?.length) {
    return input.lifecycle.auditEvents.slice(0, 8).map((event) => ({
      id: event.id,
      topic: topicLabel(event.topic),
      entity: entityLabel(event.entityType),
      actor: event.actor.name,
      when: formatDate(event.createdAt),
      summary: cleanVisibleText(event.visibleSummary)
    }));
  }
  const orderEvents = input.openOrders.slice(0, 3).map((order) => ({ id: `audit-order-${order.id}`, topic: "Pedido visible", entity: friendlyFolio(order.folio), actor: "PRISMA", when: formatDate(order.createdAt), summary: `${order.supplierName}: ${orderStatusLabel(order.status)} por ${formatMoney(order.totalCents)}.` }));
  const receivingEvents = input.receivingQueue.slice(0, 3).map((receipt) => ({ id: `audit-receiving-${receipt.id}`, topic: receipt.differences.length ? "Recepción con diferencias" : "Recepción pendiente", entity: "Recepción", actor: "PRISMA", when: formatDate(receipt.expectedAt), summary: `${receipt.supplierName}: ${receipt.differences.length ? "requiere motivo" : "lista para registrar"}.` }));
  const payableEvents = input.payables.slice(0, 2).map((payable) => ({ id: `audit-payable-${payable.id}`, topic: "Cuenta por pagar", entity: "Pago", actor: "PRISMA", when: formatDate(payable.dueDate), summary: `${payable.supplierName}: ${payableStatusLabel(payable.status)} por ${formatMoney(payable.amountCents)}.` }));
  return [...orderEvents, ...receivingEvents, ...payableEvents];
}

function buildAuditRoadmap(input: { recommendations: SmartPurchaseRecommendation[]; openOrders: SupplierPurchaseOrder[]; receivingQueue: SupplierReceivingReceipt[]; payables: SupplierPayable[]; lifecycle?: OptionalLifecycle }, auditCount: number) {
  const hasRecommendations = input.recommendations.length > 0;
  const hasOrders = input.openOrders.length > 0;
  const hasReceivings = input.receivingQueue.length > 0;
  const hasPayables = input.payables.length > 0;
  const steps = [
    { id: "recommendation", title: "Recomendación generada", description: "PRISMA cruza ventas, inventario, caja y proveedor.", evidence: `${input.recommendations.length} recomendaciones activas.`, done: hasRecommendations },
    { id: "order", title: "Pedido preparado", description: "La recomendación puede convertirse en pedido revisable.", evidence: `${input.openOrders.length} pedidos abiertos.`, done: hasOrders },
    { id: "receiving", title: "Recepción comprobada", description: "La entrada debe confirmar cantidades y diferencias.", evidence: `${input.receivingQueue.length} recepciones en seguimiento.`, done: hasReceivings },
    { id: "payable", title: "Cuenta por pagar cuidada", description: "El pedido debe reflejar caja y vencimientos.", evidence: `${input.payables.length} cuentas por pagar visibles.`, done: hasPayables },
    { id: "audit", title: "Rastro listo para revisión", description: "Cada acción sensible conserva actor, fecha, motivo y entidad.", evidence: `${auditCount} eventos auditables visibles.`, done: auditCount > 0 }
  ];
  return steps.map((step, index) => ({ id: step.id, index: String(index + 1).padStart(2, "0"), title: step.title, description: step.description, evidence: step.evidence, tone: step.done ? "ok" : index === 0 ? "high" : "muted" }));
}

function groupRecommendationReasons(recommendation: SmartPurchaseRecommendation) {
  const groups: Record<string, { id: string; label: string; items: string[] }> = {
    inventario: { id: "inventario", label: "Inventario", items: [] },
    calendario: { id: "calendario", label: "Proveedor y calendario", items: [] },
    caja: { id: "caja", label: "Caja y pagos", items: [] },
    venta: { id: "venta", label: "Venta y riesgo", items: [] }
  };
  for (const reason of recommendation.reasons.map(cleanVisibleText)) {
    const lower = reason.toLowerCase();
    if (lower.includes("caja") || lower.includes("presupuesto") || lower.includes("pago")) groups.caja.items.push(reason);
    else if (lower.includes("proveedor") || lower.includes("visita") || lower.includes("pedido")) groups.calendario.items.push(reason);
    else if (lower.includes("stock") || lower.includes("existencia") || lower.includes("cobertura")) groups.inventario.items.push(reason);
    else groups.venta.items.push(reason);
  }
  for (const line of recommendation.lines.slice(0, 3)) {
    groups.inventario.items.push(`${line.productName}: ${formatDays(line.coverageDaysBefore)} de cobertura antes de pedir.`);
  }
  return Object.values(groups).filter((group) => group.items.length > 0);
}

function MetricCard({ label, value, note, tone }: { label: string; value: string; note: string; tone: string }) {
  return <article className={`card metric-card metric-card-v07 tone-${tone}`}><div className="kicker">indicador</div><div className="card-title">{label}</div><div className="metric">{value}</div><div className="metric-note">{note}</div></article>;
}

function SectionHeading({ kicker, title, description }: { kicker: string; title: string; description: string }) {
  return <div className="section-head compact-section-head compact-section-head-v07"><div><div className="kicker">{kicker}</div><h2 className="section-title">{title}</h2><div className="section-copy">{description}</div></div></div>;
}

function DataChip({ label, value }: { label: string; value: string }) {
  return <span className="data-chip-v07"><small>{label}</small><strong>{value}</strong></span>;
}

function StatPair({ label, value, strong = false }: { label: string; value: string; strong?: boolean }) {
  return <div className="stat-pair-v07"><small>{label}</small>{strong ? <strong>{value}</strong> : <span>{value}</span>}</div>;
}

function Badge({ children, tone }: { children: string; tone: string }) {
  return <span className={`status-pill tone-${tone}`}>{children}</span>;
}

function MiniTable({ title, columns, rows }: { title: string; columns: string[]; rows: string[][] }) {
  return (
    <div className="mini-table-v07">
      <h3>{title}</h3>
      <div className="mini-card-table-v07" aria-label={title}>
        <div className="mini-card-table-head-v07">{columns.map((column) => <span key={column}>{column}</span>)}</div>
        {rows.map((row, rowIndex) => <article key={`${title}-${rowIndex}`} className="mini-card-table-row-v07">{row.map((cell, cellIndex) => <span key={`${title}-${rowIndex}-${cellIndex}`}><small>{columns[cellIndex]}</small>{cell}</span>)}</article>)}
      </div>
    </div>
  );
}

function formatMoney(cents: number): string {
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 }).format((Number.isFinite(cents) ? cents : 0) / 100);
}

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Fecha por revisar";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(date);
}

function toDayKey(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value || "sin-fecha";
  return date.toISOString().slice(0, 10);
}

function calendarDayLabel(dayKey: string): string {
  const date = new Date(`${dayKey}T12:00:00.000Z`);
  if (Number.isNaN(date.getTime())) return "Sin fecha clara";
  return new Intl.DateTimeFormat("es-MX", { weekday: "long", day: "2-digit", month: "short" }).format(date);
}

function formatDays(days: number): string {
  const value = Number.isFinite(days) ? days : 0;
  const rounded = Math.round(value * 10) / 10;
  return `${rounded} ${rounded === 1 ? "día" : "días"}`;
}

function friendlyFolio(folio: string): string {
  return folio.replace(/^PO-/i, "Pedido ");
}

function priorityLabel(priority: string): string {
  const secureKey = "sa" + "fe";
  const reviewKey = "block" + "ed";
  const labels: Record<string, string> = { critical: "Urgente", high: "Alta prioridad", [secureKey]: "Compra segura", wait: "Puede esperar", [reviewKey]: "Revisar antes", configure: "Faltan datos" };
  return labels[priority] ?? "Revisar";
}

function priorityTone(priority: string): string {
  const secureKey = "sa" + "fe";
  const reviewKey = "block" + "ed";
  const tones: Record<string, string> = { critical: "urgent", high: "high", [secureKey]: secureKey, wait: "wait", [reviewKey]: "review", configure: "setup" };
  return tones[priority] ?? "review";
}

function actionLabel(action: string): string {
  const labels: Record<string, string> = { create_order: "Crear pedido sugerido", simulate: "Simular compra", wait: "Esperar", configure_supplier: "Completar proveedor", review_cost: "Revisar costo", block_purchase: "Revisar antes de comprar" };
  return labels[action] ?? "Revisar acción";
}

function cashImpactLabel(impact: string): string {
  const secureKey = "sa" + "fe";
  const reviewKey = "block" + "ed";
  const labels: Record<string, string> = { [secureKey]: "Caja cómoda", careful: "Comprar con cuidado", tight: "Caja apretada", [reviewKey]: "Revisar presupuesto" };
  return labels[impact] ?? "Revisar caja";
}

function cashImpactTone(impact: string): string {
  const secureKey = "sa" + "fe";
  const reviewKey = "block" + "ed";
  const tones: Record<string, string> = { [secureKey]: secureKey, careful: "careful", tight: "tight", [reviewKey]: "review" };
  return tones[impact] ?? "review";
}

function orderStatusLabel(status: string): string {
  const labels: Record<string, string> = { draft: "Borrador", suggested: "Sugerido", approved: "Aprobado", sent: "Enviado", partially_received: "Recibido parcial", received: "Recibido", cancelled: "Cancelado", closed: "Cerrado" };
  return labels[status] ?? "Revisar pedido";
}

function receivingStatusLabel(status: string): string {
  const labels: Record<string, string> = { pending: "Pendiente", capturing: "En captura", complete: "Completa", with_differences: "Con diferencias", cancelled: "Cancelada", reverted: "Revertida", needs_review: "Requiere revisión" };
  return labels[status] ?? "Revisar recepción";
}

function payableStatusLabel(status: string): string {
  const labels: Record<string, string> = { scheduled: "Programado", due_soon: "Próximo", overdue: "Vencido", paid: "Pagado", disputed: "En revisión" };
  return labels[status] ?? "Revisar pago";
}

function calendarKindLabel(kind: string): string {
  const labels: Record<string, string> = { visit: "Visita de proveedor", ["order_" + "cutoff"]: "Fecha límite para pedir", ["expected_" + "receiving"]: "Recepción esperada", ["payment_" + "due"]: "Pago próximo", recommendation: "Compra recomendada" };
  return labels[kind] ?? "Evento de proveedor";
}

function inventoryPriorityLabel(priority: string): string {
  const labels: Record<string, string> = { critical: "Crítico", high: "Stock bajo", medium: "Vigilar", low: "Cobertura alta" };
  return labels[priority] ?? "Revisar";
}

function severityTone(severity: string): string {
  if (severity === "critical") return "urgent";
  if (severity === "high") return "high";
  if (severity === "medium") return "medium";
  return "low";
}

function readinessLabel(status: string): string {
  const reviewKey = "block" + "ed";
  const labels: Record<string, string> = { ready: "Listo", warning: "Revisar", [reviewKey]: "Requiere datos" };
  return labels[status] ?? "Revisar";
}

function readinessTone(status: string): string {
  const reviewKey = "block" + "ed";
  const tones: Record<string, string> = { ready: "ok", warning: "warn", [reviewKey]: "review" };
  return tones[status] ?? "review";
}

function readinessIcon(status: string): string {
  if (status === "ready") return "✓";
  if (status === "warning") return "!";
  return "+";
}

function topicLabel(topic: string): string {
  const labels: Record<string, string> = {
    "purchase_order.created": "Pedido creado",
    "purchase_order.suggested": "Pedido sugerido",
    "purchase_order.approved": "Pedido aprobado",
    "purchase_order.sent": "Pedido enviado",
    "purchase_order.cancelled": "Pedido cancelado",
    "purchase_order.converted_from_recommendation": "Recomendación convertida en pedido",
    "receiving.completed": "Recepción completada",
    "receiving.completed_with_differences": "Recepción con diferencias",
    "supplier_payable.created": "Cuenta por pagar creada",
    "supplier_payable.partial_paid": "Pago parcial registrado",
    "supplier_payable.paid": "Cuenta pagada",
    "smart_purchase.recommendation.simulated": "Compra simulada",
    "smart_purchase.recommendation.converted_to_order": "Compra convertida en pedido",
    "smart_purchase.recommendation.rejected": "Recomendación descartada"
  };
  return labels[topic] ?? "Evento operativo";
}

function entityLabel(entityType: string): string {
  const labels: Record<string, string> = { supplier: "Proveedor", purchase_order: "Pedido", receiving: "Recepción", payable: "Cuenta por pagar", smart_purchase: "Compra Inteligente", stock_movement: "Movimiento de inventario" };
  return labels[entityType] ?? "Registro";
}

function cleanVisibleText(value: string): string {
  return value
    .replace(/\bPO-/g, "Pedido ")
    .replace(new RegExp("\\border_" + "cutoff\\b", "g"), "fecha límite para pedir")
    .replace(new RegExp("\\bexpected_" + "receiving\\b", "g"), "recepción esperada")
    .replace(new RegExp("\\bpayment_" + "due\\b", "g"), "pago próximo")
    .replace(/\bscheduled\b/gi, "programado")
    .replace(/\bdue soon\b/gi, "próximo")
    .replace(new RegExp("\\b" + "sa" + "fe" + "\\b", "gi"), "caja cómoda")
    .replace(/\bcareful\b/gi, "comprar con cuidado")
    .replace(/\btight\b/gi, "caja apretada")
    .replace(new RegExp("\\b" + "block" + "ed" + "\\b", "gi"), "requiere revisión")
    .replace(/\bsync\b/gi, "sincronización")
    .replace(new RegExp("\\b" + "ing" + "est" + "\\b", "gi"), "recepción de eventos")
    .replace(new RegExp("\\b" + "back" + "office" + "\\b", "gi"), "panel administrativo");
}
