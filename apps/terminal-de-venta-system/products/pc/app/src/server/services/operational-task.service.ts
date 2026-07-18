import { resolvePcBusinessScope } from "@/server/services/pc-command-center.service";
import {
  OperationalTaskRepository,
  operationalTaskPriorities,
  operationalTaskStatuses,
  type CreateOperationalTaskInput,
  type OperationalTaskPriority,
  type OperationalTaskStatus,
  type UpdateOperationalTaskInput
} from "@/server/repositories/operational-task.repository";

const repository = new OperationalTaskRepository();

function stringValue(value: unknown, max: number) {
  return typeof value === "string" ? value.trim().slice(0, max) : "";
}

function nullableString(value: unknown, max: number) {
  const normalized = stringValue(value, max);
  return normalized || null;
}

function priorityValue(value: unknown): OperationalTaskPriority {
  return operationalTaskPriorities.includes(value as OperationalTaskPriority) ? value as OperationalTaskPriority : "medium";
}

function statusValue(value: unknown): OperationalTaskStatus | undefined {
  return operationalTaskStatuses.includes(value as OperationalTaskStatus) ? value as OperationalTaskStatus : undefined;
}

export function readOperationalTaskCreate(body: unknown): CreateOperationalTaskInput {
  const raw = body && typeof body === "object" && !Array.isArray(body) ? body as Record<string, unknown> : {};
  const title = stringValue(raw.title, 160);
  const area = stringValue(raw.area, 80);
  const idempotencyKey = stringValue(raw.idempotencyKey, 120);
  if (title.length < 3) throw new Error("OPERATIONAL_TASK_TITLE_REQUIRED");
  if (area.length < 2) throw new Error("OPERATIONAL_TASK_AREA_REQUIRED");
  if (idempotencyKey.length < 12) throw new Error("OPERATIONAL_TASK_IDEMPOTENCY_REQUIRED");
  const dueAtValue = nullableString(raw.dueAt, 48);
  const dueAt = dueAtValue ? new Date(dueAtValue) : null;
  if (dueAt && Number.isNaN(dueAt.getTime())) throw new Error("OPERATIONAL_TASK_DUE_AT_INVALID");
  return {
    title,
    description: nullableString(raw.description, 1_000),
    area,
    priority: priorityValue(raw.priority),
    href: nullableString(raw.href, 240),
    assignedToId: nullableString(raw.assignedToId, 120),
    dueAt,
    idempotencyKey
  };
}

export function readOperationalTaskUpdate(body: unknown): UpdateOperationalTaskInput {
  const raw = body && typeof body === "object" && !Array.isArray(body) ? body as Record<string, unknown> : {};
  const expectedVersion = Number(raw.expectedVersion);
  if (!Number.isInteger(expectedVersion) || expectedVersion < 1) throw new Error("OPERATIONAL_TASK_VERSION_REQUIRED");
  const status = raw.status === undefined ? undefined : statusValue(raw.status);
  if (raw.status !== undefined && !status) throw new Error("OPERATIONAL_TASK_STATUS_INVALID");
  return {
    expectedVersion,
    status,
    assignedToId: raw.assignedToId === undefined ? undefined : nullableString(raw.assignedToId, 120)
  };
}

export async function getOperationalTaskWorkspace() {
  try {
    const businessId = await resolvePcBusinessScope();
    const [tasks, assignees] = await Promise.all([
      repository.list({ businessId, status: "active" }),
      repository.listAssignees(businessId)
    ]);
    return { tasks, assignees, meta: { source: "canonical_prisma" as const, generatedAt: new Date().toISOString(), warning: null as string | null } };
  } catch (error) {
    const reason = error instanceof Error ? error.message : "lectura no disponible";
    return { tasks: [], assignees: [], meta: { source: "unavailable" as const, generatedAt: new Date().toISOString(), warning: `No fue posible leer tareas operativas: ${reason}. Verifica que la migración canónica esté aplicada.` } };
  }
}

export async function listOperationalTasks(status?: OperationalTaskStatus | "active") {
  const businessId = await resolvePcBusinessScope();
  return repository.list({ businessId, status });
}

export async function createOperationalTask(input: CreateOperationalTaskInput) {
  const businessId = await resolvePcBusinessScope();
  return repository.create(businessId, input);
}

export async function updateOperationalTask(taskId: string, input: UpdateOperationalTaskInput) {
  const businessId = await resolvePcBusinessScope();
  return repository.update(businessId, taskId, input);
}
