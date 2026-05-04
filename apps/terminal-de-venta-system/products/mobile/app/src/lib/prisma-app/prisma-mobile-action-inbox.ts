import type { PrismaMobileAlert, PrismaMobileBranch, PrismaMobileInventoryItem } from "./prisma-app-api-contracts";
import type { PrismaMobileClientSnapshot, PrismaMobileSnapshotPayload } from "./prisma-mobile-snapshot-contract";
import { buildPrismaMobileCommandCenter, type PrismaMobileCommandDecision, type PrismaMobileCommandTone } from "./prisma-mobile-command-center";
import { formatSignedMxnFromCents } from "./prisma-mobile-formatters";

export const PRISMA_MOBILE_ACTION_INBOX_CONTRACT_ID = "PRISMA_APP_MOBILE_21_OWNER_ACTION_INBOX";

export type PrismaMobileActionInboxLaneId = "ahora" | "hoy" | "corte";
export type PrismaMobileActionInboxArea = "caja" | "inventario" | "ventas" | "sucursal" | "datos" | "alertas";

export type PrismaMobileOwnerAction = {
  id: string;
  area: PrismaMobileActionInboxArea;
  title: string;
  summary: string;
  recommendedAction: string;
  owner: string;
  lane: PrismaMobileActionInboxLaneId;
  tone: PrismaMobileCommandTone;
  priorityScore: number;
  dueLabel: string;
  evidence: string[];
  escalation: string;
  shareLine: string;
};

export type PrismaMobileActionInboxLane = {
  id: PrismaMobileActionInboxLaneId;
  title: string;
  subtitle: string;
  count: number;
  tone: PrismaMobileCommandTone;
  actions: PrismaMobileOwnerAction[];
};

export type PrismaMobileActionInbox = {
  contractId: typeof PRISMA_MOBILE_ACTION_INBOX_CONTRACT_ID;
  generatedLabel: string;
  headline: string;
  summary: string;
  readinessLabel: string;
  actionCount: number;
  urgentCount: number;
  ownerMessage: string;
  lanes: PrismaMobileActionInboxLane[];
  digest: {
    title: string;
    lines: string[];
  };
};

const laneOrder: PrismaMobileActionInboxLaneId[] = ["ahora", "hoy", "corte"];

function clamp(value: number, min = 0, max = 100): number {
  return Math.min(max, Math.max(min, Math.round(value)));
}

function moneyAbs(cents: number): number {
  return Math.abs(cents);
}

function normalizeId(value: string): string {
  return value.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "").slice(0, 72) || "accion";
}

function toneRank(tone: PrismaMobileCommandTone): number {
  return tone === "offline" ? 4 : tone === "urgente" ? 3 : tone === "revisar" ? 2 : 1;
}

function laneForScore(score: number, tone: PrismaMobileCommandTone): PrismaMobileActionInboxLaneId {
  if (tone === "offline" || tone === "urgente" || score >= 24) return "ahora";
  if (tone === "revisar" || score >= 9) return "hoy";
  return "corte";
}

function dueForLane(lane: PrismaMobileActionInboxLaneId): string {
  if (lane === "ahora") return "antes de seguir operando";
  if (lane === "hoy") return "hoy antes del corte";
  return "en la revisión de cierre";
}

function laneTone(actions: PrismaMobileOwnerAction[]): PrismaMobileCommandTone {
  if (actions.some((action) => action.tone === "offline")) return "offline";
  if (actions.some((action) => action.tone === "urgente")) return "urgente";
  if (actions.some((action) => action.tone === "revisar")) return "revisar";
  return "sano";
}

function actionFromDecision(decision: PrismaMobileCommandDecision): PrismaMobileOwnerAction {
  const area: PrismaMobileActionInboxArea = decision.kind === "cash" ? "caja" : decision.kind === "inventory" ? "inventario" : decision.kind === "sync" || decision.kind === "data" ? "datos" : decision.kind === "sales" ? "ventas" : "sucursal";
  const lane = laneForScore(decision.score, decision.tone);
  return {
    id: `decision-${decision.id}`,
    area,
    title: decision.title,
    summary: decision.detail,
    recommendedAction: decision.action,
    owner: decision.owner,
    lane,
    tone: decision.tone,
    priorityScore: clamp(decision.score),
    dueLabel: dueForLane(lane),
    evidence: [`Valor: ${decision.value}`, `Score: ${decision.score}/100`, `Origen: Centro de Mando`],
    escalation: decision.tone === "sano" ? "No escalar; mantener vigilancia." : `Escalar con ${decision.owner} si no hay avance en la siguiente revisión.`,
    shareLine: `${decision.owner}: ${decision.title}. ${decision.action}`
  };
}

function actionFromAlert(alert: PrismaMobileAlert, index: number): PrismaMobileOwnerAction {
  const score = alert.severity === "critica" ? 36 : alert.severity === "alta" ? 24 : alert.severity === "media" ? 12 : 4;
  const tone: PrismaMobileCommandTone = alert.severity === "critica" ? "urgente" : alert.severity === "alta" || alert.severity === "media" ? "revisar" : "sano";
  const lane = laneForScore(score, tone);
  return {
    id: `alerta-${normalizeId(alert.id || `${alert.title}-${index}`)}`,
    area: "alertas",
    title: alert.title,
    summary: `${alert.area}: ${alert.detail}`,
    recommendedAction: alert.action,
    owner: "Supervisor",
    lane,
    tone,
    priorityScore: score,
    dueLabel: dueForLane(lane),
    evidence: [`Severidad: ${alert.severity}`, `Hora: ${alert.time}`, `Área: ${alert.area}`],
    escalation: tone === "urgente" ? "Escalar al dueño si no se confirma atención inmediata." : "Validar avance con el encargado del área.",
    shareLine: `Supervisor: ${alert.title}. ${alert.action}`
  };
}

function actionFromInventory(item: PrismaMobileInventoryItem): PrismaMobileOwnerAction {
  const score = item.state === "critico" ? 34 : item.state === "reponer" ? 20 : item.state === "sobrestock" ? 10 : 0;
  const tone: PrismaMobileCommandTone = item.state === "critico" ? "urgente" : item.state === "reponer" || item.state === "sobrestock" ? "revisar" : "sano";
  const lane = laneForScore(score, tone);
  const verb = item.state === "sobrestock" ? "revisar exhibición y evitar compra innecesaria" : item.state === "normal" ? "mantener en observación" : "confirmar existencia física y preparar reabasto";
  return {
    id: `inventario-${normalizeId(item.sku)}`,
    area: "inventario",
    title: item.name,
    summary: `${item.sku} · ${item.stock} · ${item.movement}`,
    recommendedAction: verb,
    owner: "Inventario",
    lane,
    tone,
    priorityScore: score,
    dueLabel: dueForLane(lane),
    evidence: [`Categoría: ${item.category}`, `Vendidas/semana: ${item.weeklyUnitsSold}`, `Stock numérico: ${item.stockQty}`],
    escalation: item.state === "critico" ? "Escalar si no se localiza producto o proveedor en el turno." : "Registrar decisión en revisión de inventario.",
    shareLine: `Inventario: ${item.name}. ${verb}.`
  };
}

function actionFromBranch(branch: PrismaMobileBranch): PrismaMobileOwnerAction {
  const score = branch.status === "offline" ? 38 : branch.status === "urgente" ? 30 : branch.status === "revisar" ? 14 : 0;
  const lane = laneForScore(score, branch.status);
  const action = branch.status === "sano" ? "mantener seguimiento normal" : "contactar responsable y confirmar caja, alertas y sincronización";
  return {
    id: `sucursal-${normalizeId(branch.name)}`,
    area: "sucursal",
    title: branch.name,
    summary: `${branch.salesToday} · ${branch.cashState} · ${branch.alerts} alertas`,
    recommendedAction: action,
    owner: "Supervisor",
    lane,
    tone: branch.status,
    priorityScore: score,
    dueLabel: dueForLane(lane),
    evidence: [`Sync: ${branch.syncLag}`, `Tickets: ${branch.tickets}`, `Variación: ${branch.salesDelta}`],
    escalation: branch.status === "offline" ? "Escalar si no recupera señal antes de la siguiente venta sensible." : "Pedir confirmación al encargado.",
    shareLine: `Supervisor: ${branch.name}. ${action}.`
  };
}

function cashAction(snapshot: PrismaMobileSnapshotPayload): PrismaMobileOwnerAction | null {
  const exposure = moneyAbs(snapshot.cashCurrent.differenceCents);
  if (exposure === 0) return null;
  const score = exposure >= 20000 ? 36 : exposure >= 5000 ? 22 : 10;
  const tone: PrismaMobileCommandTone = score >= 30 ? "urgente" : "revisar";
  const lane = laneForScore(score, tone);
  return {
    id: "caja-diferencia-corte",
    area: "caja",
    title: "Diferencia de caja",
    summary: `${formatSignedMxnFromCents(snapshot.cashCurrent.differenceCents)} contra esperado en corte ${snapshot.cashCurrent.lastCut}.`,
    recommendedAction: "pedir conteo rápido, revisar movimientos grandes y dejar nota de cierre",
    owner: "Encargado de turno",
    lane,
    tone,
    priorityScore: score,
    dueLabel: dueForLane(lane),
    evidence: [`Esperado: ${snapshot.cashCurrent.expectedLabel}`, `Contado: ${snapshot.cashCurrent.countedLabel}`, `Estado: ${snapshot.cashCurrent.status}`],
    escalation: "Escalar al dueño si la diferencia se repite o no se explica.",
    shareLine: `Encargado de turno: revisar diferencia de caja ${formatSignedMxnFromCents(snapshot.cashCurrent.differenceCents)}.`
  };
}

function dataAction(client: PrismaMobileClientSnapshot): PrismaMobileOwnerAction | null {
  if (!client.stale && client.errors.length === 0) return null;
  const tone: PrismaMobileCommandTone = client.source === "local-cache" ? "offline" : "revisar";
  const score = client.source === "local-cache" ? 30 : 16;
  const lane = laneForScore(score, tone);
  return {
    id: "datos-respaldo-local",
    area: "datos",
    title: "Datos con respaldo local",
    summary: client.errors.length > 0 ? client.errors.slice(0, 2).join(" · ") : `Fuente activa: ${client.source}`,
    recommendedAction: "refrescar conexión antes de autorizar decisiones sensibles",
    owner: "Operación",
    lane,
    tone,
    priorityScore: score,
    dueLabel: dueForLane(lane),
    evidence: [`Fuente: ${client.source}`, `Stale: ${client.stale ? "sí" : "no"}`, `Errores: ${client.errors.length}`],
    escalation: "Si se mantiene en respaldo local, validar Tablet/PC antes del corte.",
    shareLine: "Operación: refrescar conexión de PRISMA App antes de decisiones sensibles."
  };
}

function uniqueActions(actions: PrismaMobileOwnerAction[]): PrismaMobileOwnerAction[] {
  const seen = new Set<string>();
  const result: PrismaMobileOwnerAction[] = [];
  for (const action of actions) {
    const key = `${action.area}:${normalizeId(action.title)}:${normalizeId(action.owner)}`;
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(action);
  }
  return result;
}

function sortActions(actions: PrismaMobileOwnerAction[]): PrismaMobileOwnerAction[] {
  return [...actions].sort((a, b) => {
    const laneDelta = laneOrder.indexOf(a.lane) - laneOrder.indexOf(b.lane);
    return laneDelta || toneRank(b.tone) - toneRank(a.tone) || b.priorityScore - a.priorityScore || a.title.localeCompare(b.title, "es-MX");
  });
}

function buildActions(client: PrismaMobileClientSnapshot): PrismaMobileOwnerAction[] {
  const snapshot = client.snapshot;
  const command = buildPrismaMobileCommandCenter(client);
  const actions: PrismaMobileOwnerAction[] = [
    ...command.decisionQueue.map(actionFromDecision),
    ...snapshot.alerts.alerts.slice(0, 6).map(actionFromAlert),
    ...snapshot.inventoryWatchlist.items.filter((item) => item.state !== "normal").slice(0, 8).map(actionFromInventory),
    ...snapshot.branches.branches.filter((branch) => branch.status !== "sano").slice(0, 5).map(actionFromBranch)
  ];
  const cash = cashAction(snapshot);
  const data = dataAction(client);
  if (cash) actions.push(cash);
  if (data) actions.push(data);
  return sortActions(uniqueActions(actions)).slice(0, 18);
}

function emptyAction(lane: PrismaMobileActionInboxLaneId): PrismaMobileOwnerAction {
  const title = lane === "ahora" ? "Sin incendios inmediatos" : lane === "hoy" ? "Sin pendientes fuertes para hoy" : "Cierre operativo normal";
  return {
    id: `empty-${lane}`,
    area: "ventas",
    title,
    summary: "La app no detectó acciones urgentes en esta bandeja.",
    recommendedAction: "mantener monitoreo y revisar cierre",
    owner: "Dueño",
    lane,
    tone: "sano",
    priorityScore: 0,
    dueLabel: dueForLane(lane),
    evidence: ["Sin alertas críticas para esta categoría"],
    escalation: "No aplica.",
    shareLine: `${title}: mantener monitoreo.`
  };
}

function buildLane(id: PrismaMobileActionInboxLaneId, actions: PrismaMobileOwnerAction[]): PrismaMobileActionInboxLane {
  const copy = {
    ahora: { title: "Resolver ahora", subtitle: "Lo que puede frenar caja, venta o control si se deja pasar." },
    hoy: { title: "Dar seguimiento hoy", subtitle: "Pendientes que conviene cerrar antes del corte." },
    corte: { title: "Revisar en cierre", subtitle: "Control y aprendizaje para que mañana no amanezca torcido." }
  } satisfies Record<PrismaMobileActionInboxLaneId, { title: string; subtitle: string }>;
  const laneActions = actions.filter((action) => action.lane === id);
  const visibleActions = laneActions.length > 0 ? laneActions : [emptyAction(id)];
  return {
    id,
    title: copy[id].title,
    subtitle: copy[id].subtitle,
    count: laneActions.length,
    tone: laneTone(visibleActions),
    actions: visibleActions
  };
}

function readinessLabel(urgentCount: number, actionCount: number): string {
  if (urgentCount > 0) return `${urgentCount} acción${urgentCount === 1 ? "" : "es"} para resolver ya`;
  if (actionCount > 0) return `${actionCount} pendiente${actionCount === 1 ? "" : "s"} bajo control`;
  return "Sin pendientes operativos fuertes";
}

export function buildPrismaMobileActionInbox(client: PrismaMobileClientSnapshot): PrismaMobileActionInbox {
  const actions = buildActions(client);
  const urgentCount = actions.filter((action) => action.lane === "ahora" && action.priorityScore > 0).length;
  const actionCount = actions.filter((action) => action.priorityScore > 0).length;
  const lanes = laneOrder.map((lane) => buildLane(lane, actions));
  const top = actions.filter((action) => action.priorityScore > 0).slice(0, 5);
  const ownerMessage = top.length > 0
    ? top.map((action, index) => `${index + 1}. ${action.shareLine}`).join(" ")
    : "PRISMA App: operación sin pendientes fuertes; revisar cierre normal.";

  return {
    contractId: PRISMA_MOBILE_ACTION_INBOX_CONTRACT_ID,
    generatedLabel: client.snapshot.summary.generatedLabel,
    headline: urgentCount > 0 ? "Hay acciones que no conviene patear" : actionCount > 0 ? "Pendientes ordenados para el dueño" : "Operación móvil en calma",
    summary: urgentCount > 0 ? "La app separó lo que puede pegarle a caja, inventario o datos conectados." : "La app armó una bandeja accionable sin obligarte a abrir PC para cada pendiente.",
    readinessLabel: readinessLabel(urgentCount, actionCount),
    actionCount,
    urgentCount,
    ownerMessage,
    lanes,
    digest: {
      title: "Mensaje listo para encargado",
      lines: top.length > 0 ? top.map((action) => `${action.owner}: ${action.recommendedAction}. Evidencia: ${action.evidence[0]}.`) : ["Sin acciones urgentes; mantener monitoreo y cierre normal."]
    }
  };
}
