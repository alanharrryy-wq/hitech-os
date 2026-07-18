import { DecisionScreen } from "@components/uiux/decision-screen";
import type { EvidenceItem, RecommendedAction, SummaryCard } from "@components/uiux/decision-types";
import { OperationalTaskWorkspace } from "@components/dashboard/operational-task-workspace";
import { getBackofficeDashboard, type BackofficeDashboard } from "@/lib/backoffice/dashboard";
import { getOperationalTaskWorkspace } from "@/server/services/operational-task.service";

export const dynamic = "force-dynamic";

type DashboardTask = {
  priority: "Alta" | "Media" | "Baja";
  area: string;
  title: string;
  status: string;
  impact: string;
  cause: string;
  action: string;
  href: string;
};

function dashboardValue(dashboard: BackofficeDashboard, key: string) {
  return dashboard.kpis.find((item) => item.key === key)?.value ?? "Sin dato";
}

function formatUpdated(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Lectura sin hora registrada";

  return new Intl.DateTimeFormat("es-MX", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(date);
}

function buildTasks(dashboard: BackofficeDashboard): DashboardTask[] {
  const tasks: DashboardTask[] = [];

  if (dashboard.sync.conflictCount > 0) {
    tasks.push({
      priority: "Alta",
      area: "Sincronización",
      title: "Conflictos por resolver",
      status: `${dashboard.sync.conflictCount} pendiente(s)`,
      impact: "Puede dejar información operativa distinta entre equipos.",
      cause: "Existen eventos que requieren una resolución supervisada.",
      action: "Revisar sincronización",
      href: "/sync-operativo"
    });
  }

  if (dashboard.sync.failedEvents > 0 || dashboard.sync.pendingEvents > 0) {
    const total = dashboard.sync.failedEvents + dashboard.sync.pendingEvents;
    tasks.push({
      priority: dashboard.sync.failedEvents > 0 ? "Alta" : "Media",
      area: "Sincronización",
      title: "Movimientos por enviar o revisar",
      status: `${total} pendiente(s)`,
      impact: "La información pendiente puede llegar tarde a los demás equipos.",
      cause: dashboard.sync.failedEvents > 0 ? "Hay intentos que no se completaron." : "Hay movimientos en espera de entrega.",
      action: "Abrir cola operativa",
      href: "/sync-operativo"
    });
  }

  const lowStockCount = Number(dashboardValue(dashboard, "lowStockCount"));
  if (Number.isFinite(lowStockCount) && lowStockCount > 0) {
    tasks.push({
      priority: "Alta",
      area: "Inventario",
      title: "Productos con cobertura baja",
      status: `${lowStockCount} por revisar`,
      impact: "Puede provocar faltantes durante la venta.",
      cause: "La cobertura calculada está por debajo del umbral operativo.",
      action: "Revisar existencias",
      href: "/stock"
    });
  }

  const tickets = Number(dashboardValue(dashboard, "ticketCountToday"));
  if (Number.isFinite(tickets) && tickets > 0) {
    tasks.push({
      priority: "Baja",
      area: "Ventas",
      title: "Ventas del día disponibles",
      status: `${tickets} ticket(s)`,
      impact: "Permite revisar ventas y conciliación antes del cierre.",
      cause: "Hay actividad operativa registrada para el día actual.",
      action: "Revisar ventas",
      href: "/sales-control"
    });
  }

  if (!tasks.length) {
    tasks.push({
      priority: "Baja",
      area: "Operación",
      title: "Sin pendientes críticos detectados",
      status: "Al día",
      impact: "No hay alertas operativas en esta lectura.",
      cause: "La lectura actual no detectó faltantes, conflictos ni eventos pendientes.",
      action: "Revisar ventas",
      href: "/sales-control"
    });
  }

  return tasks;
}

function TaskActionBoard({ tasks }: { tasks: DashboardTask[] }) {
  return (
    <section className="card" data-prisma-component="DashboardTaskBoard" data-prisma-surface="pc.hoy">
      <div className="section-head">
        <div>
          <div className="kicker">tareas del día</div>
          <h2 className="section-title">Qué atender ahora</h2>
          <div className="section-copy">Cada pendiente se calcula desde la lectura operativa actual y abre su superficie de seguimiento.</div>
        </div>
      </div>

      <div className="dashboard-grid" aria-label="Tareas accionables del día">
        {tasks.map((task) => (
          <article className="card metric-card" key={`${task.area}-${task.title}`} data-dashboard-task={task.area.toLowerCase()}>
            <div className="kicker">{task.priority} · {task.area}</div>
            <div className="card-title">{task.title}</div>
            <div className="list" style={{ marginTop: 12 }}>
              <div className="list-item"><strong>Estado:</strong> {task.status}</div>
              <div className="list-item"><strong>Impacto:</strong> {task.impact}</div>
              <div className="list-item"><strong>Motivo:</strong> {task.cause}</div>
            </div>
            <div className="inline-list" style={{ marginTop: 16 }}>
              <a className="btn btn-primary" href={task.href}>{task.action}</a>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

export default async function DashboardPage() {
  const [dashboard, operationalTaskWorkspace] = await Promise.all([getBackofficeDashboard(), getOperationalTaskWorkspace()]);
  const tasks = buildTasks(dashboard);
  const primaryTask = tasks[0];
  const ticketCount = dashboardValue(dashboard, "ticketCountToday");
  const netSales = dashboardValue(dashboard, "netSalesTodayCents");
  const syncPending = dashboard.sync.pendingEvents + dashboard.sync.failedEvents + dashboard.sync.conflictCount;

  const summaryCards: SummaryCard[] = [
    {
      title: `${tasks.length} señal(es)`,
      eyebrow: "qué requiere atención",
      tone: dashboard.sync.conflictCount > 0 || dashboard.sync.failedEvents > 0 ? "danger" : tasks[0]?.priority === "Alta" ? "warn" : "ok",
      lines: [primaryTask.title, primaryTask.cause]
    },
    {
      title: syncPending ? `${syncPending} pendiente(s)` : "Sin pendientes",
      eyebrow: "sincronización",
      tone: dashboard.sync.conflictCount > 0 || dashboard.sync.failedEvents > 0 ? "warn" : "ok",
      lines: [dashboard.sync.healthLabel, syncPending ? "Revisa la cola antes de cerrar la operación." : "No hay movimientos pendientes en esta lectura."]
    },
    {
      title: netSales,
      eyebrow: `${ticketCount} ticket(s) hoy`,
      tone: "info",
      lines: ["Resumen calculado con las ventas registradas hoy.", "Abre ventas para revisar el detalle y la conciliación."]
    }
  ];

  const recommendedAction: RecommendedAction = {
    title: primaryTask.action,
    motive: primaryTask.impact,
    actions: tasks.slice(0, 3).map((task, index) => ({
      label: task.action,
      href: task.href,
      primary: index === 0
    }))
  };

  const rows = tasks.map((task) => ({
    Prioridad: task.priority,
    Área: task.area,
    Estado: task.status,
    Impacto: task.impact,
    "Qué hacer": task.action
  }));

  const evidence: EvidenceItem[] = [
    { kind: "operational", label: "Lectura", value: "Ventas, existencias y pendientes operativos disponibles para esta sucursal." },
    { kind: "operational", label: "Actualización", value: formatUpdated(dashboard.meta.generatedAt) },
    { kind: "governance", label: "Acciones", value: "Cada acción abre una superficie operativa existente; no se muestran confirmaciones sin resultado." }
  ];

  return (
    <DecisionScreen
      currentPath="/dashboard"
      title="Hoy"
      subtitle="Prioridades operativas calculadas desde ventas, existencias y sincronización actual."
      status={primaryTask.status}
      lastUpdated={formatUpdated(dashboard.meta.generatedAt)}
      summaryCards={summaryCards}
      recommendedAction={recommendedAction}
      tableTitle="Prioridades del día"
      tableSubtitle="Pendientes entendibles para operación y enlazados a su seguimiento real."
      columns={["Prioridad", "Área", "Estado", "Impacto", "Qué hacer"]}
      rows={rows}
      evidence={evidence}
    >
      <OperationalTaskWorkspace initialWorkspace={operationalTaskWorkspace} />
      <TaskActionBoard tasks={tasks} />
    </DecisionScreen>
  );
}
