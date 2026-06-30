import { DecisionScreen } from "@components/uiux/decision-screen";
import type { EvidenceItem, RecommendedAction, SummaryCard } from "@components/uiux/decision-types";

export const dynamic = "force-dynamic";

const dashboardSummaryCards: SummaryCard[] = [
  {
    title: "3 frentes vivos",
    eyebrow: "qué pide atención",
    tone: "warn",
    lines: [
      "Inventario crítico, sincronización y caja ya aparecen como trabajo accionable.",
      "El usuario ve causa, impacto y ruta de resolución sin brincar a pantallas nuevas."
    ]
  },
  {
    title: "Filtros listos",
    eyebrow: "dropdowns inteligentes",
    tone: "ok",
    lines: [
      "La superficie Hoy usa el dock global para sucursal, periodo y responsable.",
      "Los catálogos DB-backed se usan cuando existen y los fallback quedan declarados."
    ]
  },
  {
    title: "Acción honesta",
    eyebrow: "sin botones de utilería",
    tone: "info",
    lines: [
      "Resolver abre la superficie operativa correcta.",
      "Marcar revisado y posponer quedan bloqueados hasta existir endpoint auditable."
    ]
  }
];

const dashboardRecommendedAction: RecommendedAction = {
  title: "Resolver primero lo que puede costar venta",
  motive: "Hoy debe ordenar pendientes por impacto operativo: quiebre de stock, sincronización atrasada y diferencias de caja.",
  actions: [
    { label: "Atender productos críticos", href: "/existencias-criticas", primary: true },
    { label: "Revisar sincronización", href: "/sync-operativo" },
    { label: "Validar caja", href: "/sales-control" }
  ]
};

const dashboardTasks = [
  {
    priority: "Alta",
    area: "Inventario",
    title: "Productos críticos antes de vender",
    status: "Revisar",
    impact: "Evita quiebres y ventas perdidas en productos de alta rotación.",
    cause: "Stock bajo mínimo, productos sin proveedor o cobertura menor a la venta esperada.",
    action: "Abrir existencias críticas",
    href: "/existencias-criticas",
    evidence: "Fuente operativa: inventario, stock mínimo, ventas recientes y proveedor preferido."
  },
  {
    priority: "Media",
    area: "Sincronización",
    title: "Cambios PC-tablet pendientes",
    status: "Vigilar",
    impact: "Evita que una tablet venda con catálogo, precios o cortes desfasados.",
    cause: "Eventos pendientes, fallidos o sin confirmación final desde tablets.",
    action: "Abrir sync operativo",
    href: "/sync-operativo",
    evidence: "Fuente operativa: outbox, heartbeat, delta de catálogo y estado de confirmación."
  },
  {
    priority: "Media",
    area: "Caja",
    title: "Cortes y movimientos sensibles",
    status: "Operativo",
    impact: "Reduce diferencias de efectivo, retiros sin motivo y cierres incompletos.",
    cause: "Caja abierta, movimientos sensibles o tickets que requieren revisión.",
    action: "Abrir ventas y caja",
    href: "/sales-control",
    evidence: "Fuente operativa: ventas, sesiones de caja, terminal, cajero y método de pago."
  }
];

const dashboardRows = dashboardTasks.map((task) => ({
  Prioridad: task.priority,
  Área: task.area,
  Estado: task.status,
  Impacto: task.impact,
  "Qué hacer": task.action
}));

const dashboardEvidence: EvidenceItem[] = [
  {
    kind: "operational",
    label: "Función de Hoy",
    value: "Mostrar qué resolver ahora: inventario, sync, caja, compras, proveedores y tareas del día."
  },
  {
    kind: "operational",
    label: "Dropdowns",
    value: "La pantalla usa SmartDropdownDock con sucursal, periodo, responsable, severidad y estado operativo."
  },
  {
    kind: "operational",
    label: "Acciones",
    value: "Las acciones principales abren rutas existentes para resolver; las acciones sin backend quedan bloqueadas con explicación."
  },
  {
    kind: "technical",
    label: "Sin pantallas nuevas",
    value: "El cambio se concentra en /dashboard/page.tsx y aprovecha DecisionScreen, NextBestAction, ActionableTable y EvidenceDrawer."
  },
  {
    kind: "governance",
    label: "Criterio",
    value: "Cero botones decorativos: cada control resuelve, abre detalle o declara por qué todavía no puede ejecutar."
  }
];

function TaskActionBoard() {
  return (
    <section className="card" data-prisma-component="DashboardTaskBoard" data-prisma-surface="pc.hoy">
      <div className="section-head">
        <div>
          <div className="kicker">tareas del día</div>
          <h2 className="section-title">Qué hacer ahorita</h2>
          <div className="section-copy">
            Cada pendiente explica causa, impacto y siguiente acción. Marcar revisado o posponer queda bloqueado hasta tener endpoint auditable.
          </div>
        </div>
      </div>

      <div className="dashboard-grid" aria-label="Tareas accionables del día">
        {dashboardTasks.map((task) => (
          <article className="card metric-card" key={`${task.area}-${task.title}`} data-dashboard-task={task.area.toLowerCase()}>
            <div className="kicker">{task.priority} · {task.area}</div>
            <div className="card-title">{task.title}</div>
            <div className="list" style={{ marginTop: 12 }}>
              <div className="list-item"><strong>Estado:</strong> {task.status}</div>
              <div className="list-item"><strong>Impacto:</strong> {task.impact}</div>
              <div className="list-item"><strong>Causa:</strong> {task.cause}</div>
            </div>

            <div className="inline-list" style={{ marginTop: 16 }}>
              <a className="btn btn-primary" href={task.href}>{task.action}</a>
              <button
                className="btn btn-secondary"
                type="button"
                disabled
                aria-disabled="true"
                title="Pendiente de endpoint auditable para registrar revisión."
              >
                Marcar revisado
              </button>
              <button
                className="btn btn-secondary"
                type="button"
                disabled
                aria-disabled="true"
                title="Pendiente de endpoint auditable para posponer con motivo."
              >
                Posponer
              </button>
            </div>

            <details style={{ marginTop: 14 }}>
              <summary>Evidencia y criterio</summary>
              <p>{task.evidence}</p>
              <p>Si se ignora, PRISMA mantiene el pendiente visible para no fabricar verde falso.</p>
            </details>
          </article>
        ))}
      </div>
    </section>
  );
}

export default async function DashboardPage() {
  return (
    <DecisionScreen
      currentPath="/dashboard"
      title="Hoy"
      subtitle="Resumen accionable de lo que necesita atención antes de vender, comprar o cerrar caja."
      status="3 prioridades listas para operar"
      lastUpdated="Lectura operativa local"
      summaryCards={dashboardSummaryCards}
      recommendedAction={dashboardRecommendedAction}
      tableTitle="Prioridades del día"
      tableSubtitle="Pendientes entendibles para dueño, gerente, caja, almacén y soporte."
      columns={["Prioridad", "Área", "Estado", "Impacto", "Qué hacer"]}
      rows={dashboardRows}
      evidence={dashboardEvidence}
    >
      <TaskActionBoard />
    </DecisionScreen>
  );
}
