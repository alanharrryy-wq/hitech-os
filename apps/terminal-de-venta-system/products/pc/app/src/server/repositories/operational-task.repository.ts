import { randomUUID } from "node:crypto";
import { prisma } from "@/server/prisma/client";

export const operationalTaskPriorities = ["high", "medium", "low"] as const;
export const operationalTaskStatuses = ["open", "in_progress", "completed", "cancelled"] as const;

export type OperationalTaskPriority = typeof operationalTaskPriorities[number];
export type OperationalTaskStatus = typeof operationalTaskStatuses[number];

export type OperationalTaskRecord = {
  id: string;
  businessId: string;
  title: string;
  description: string | null;
  area: string;
  priority: OperationalTaskPriority;
  status: OperationalTaskStatus;
  href: string | null;
  source: string;
  assignedToId: string | null;
  assignedToName: string | null;
  version: number;
  dueAt: string | null;
  completedAt: string | null;
  cancelledAt: string | null;
  createdAt: string;
  updatedAt: string;
};

export type OperationalTaskAssignee = { id: string; displayName: string };

export type CreateOperationalTaskInput = {
  title: string;
  description?: string | null;
  area: string;
  priority: OperationalTaskPriority;
  href?: string | null;
  assignedToId?: string | null;
  dueAt?: Date | null;
  idempotencyKey: string;
};

export type UpdateOperationalTaskInput = {
  expectedVersion: number;
  status?: OperationalTaskStatus;
  assignedToId?: string | null;
};

type TaskRow = {
  id: string;
  businessId: string;
  title: string;
  description: string | null;
  area: string;
  priority: string;
  status: string;
  href: string | null;
  source: string;
  assignedToId: string | null;
  assignedToName: string | null;
  version: number;
  dueAt: Date | string | null;
  completedAt: Date | string | null;
  cancelledAt: Date | string | null;
  createdAt: Date | string;
  updatedAt: Date | string;
};

function iso(value: Date | string | null) {
  if (!value) return null;
  const date = value instanceof Date ? value : new Date(value);
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}

function asPriority(value: string): OperationalTaskPriority {
  return operationalTaskPriorities.includes(value as OperationalTaskPriority) ? value as OperationalTaskPriority : "medium";
}

function asStatus(value: string): OperationalTaskStatus {
  return operationalTaskStatuses.includes(value as OperationalTaskStatus) ? value as OperationalTaskStatus : "open";
}

function toRecord(row: TaskRow): OperationalTaskRecord {
  return {
    id: row.id,
    businessId: row.businessId,
    title: row.title,
    description: row.description,
    area: row.area,
    priority: asPriority(row.priority),
    status: asStatus(row.status),
    href: row.href,
    source: row.source,
    assignedToId: row.assignedToId,
    assignedToName: row.assignedToName,
    version: Number(row.version),
    dueAt: iso(row.dueAt),
    completedAt: iso(row.completedAt),
    cancelledAt: iso(row.cancelledAt),
    createdAt: iso(row.createdAt) ?? new Date(0).toISOString(),
    updatedAt: iso(row.updatedAt) ?? new Date(0).toISOString()
  };
}

export class OperationalTaskRepository {
  private async readOne(businessId: string, taskId: string): Promise<OperationalTaskRecord | null> {
    const rows = await prisma.$queryRaw<TaskRow[]>`
      SELECT "OperationalTask"."id", "OperationalTask"."businessId", "OperationalTask"."title", "OperationalTask"."description",
        "OperationalTask"."area", "OperationalTask"."priority", "OperationalTask"."status", "OperationalTask"."href", "OperationalTask"."source",
        "OperationalTask"."assignedToId", "User"."displayName" AS "assignedToName", "OperationalTask"."version", "OperationalTask"."dueAt",
        "OperationalTask"."completedAt", "OperationalTask"."cancelledAt", "OperationalTask"."createdAt", "OperationalTask"."updatedAt"
      FROM "OperationalTask"
      LEFT JOIN "User" ON "User"."id" = "OperationalTask"."assignedToId" AND "User"."businessId" = "OperationalTask"."businessId"
      WHERE "OperationalTask"."businessId" = ${businessId} AND "OperationalTask"."id" = ${taskId}
      LIMIT 1
    `;
    return rows[0] ? toRecord(rows[0]) : null;
  }

  private async ensureAssignee(businessId: string, assignedToId: string | null | undefined) {
    if (!assignedToId) return;
    const rows = await prisma.$queryRaw<Array<{ id: string }>>`
      SELECT "id" FROM "User" WHERE "businessId" = ${businessId} AND "id" = ${assignedToId} AND "status" = 'ACTIVE' LIMIT 1
    `;
    if (!rows[0]) throw new Error("OPERATIONAL_TASK_ASSIGNEE_NOT_FOUND");
  }

  private async recordAudit(tx: any, input: { businessId: string; topic: string; task: OperationalTaskRecord; before?: Pick<OperationalTaskRecord, "status" | "assignedToId" | "version"> }) {
    await tx.auditEvent.create({
      data: {
        id: randomUUID(),
        businessId: input.businessId,
        actorId: null,
        topic: input.topic,
        entityType: "OperationalTask",
        entityId: input.task.id,
        summary: `Operational task ${input.task.title} ${input.topic}.`,
        beforeJson: input.before ? JSON.stringify(input.before) : null,
        afterJson: JSON.stringify({ id: input.task.id, area: input.task.area, status: input.task.status, assignedToId: input.task.assignedToId, version: input.task.version }),
        metadataJson: JSON.stringify({ source: "pc", durable: true, privacy: "no_customer_or_payment_data" })
      }
    });
  }

  private async recordOutbox(tx: any, input: { businessId: string; eventType: "created" | "updated" | "completed" | "cancelled"; task: OperationalTaskRecord; at: Date }) {
    await tx.outboxEvent.create({
      data: {
        id: randomUUID(),
        businessId: input.businessId,
        topic: "operational_task.changed",
        eventType: `operational_task.${input.eventType}`,
        aggregateId: input.task.id,
        idempotencyKey: `operational_task:${input.task.id}:v${input.task.version}`,
        payloadJson: JSON.stringify({ id: input.task.id, businessId: input.businessId, status: input.task.status, assignedToId: input.task.assignedToId, version: input.task.version, occurredAt: input.at.toISOString() }),
        source: "pc",
        schemaVersion: "operational-task.v1",
        status: "pending",
        lifecycleStatus: "pending",
        attempts: 0,
        createdAt: input.at
      }
    });
  }

  async list(input: { businessId: string; status?: OperationalTaskStatus | "active"; limit?: number }) {
    const limit = Math.max(1, Math.min(Math.trunc(input.limit ?? 80), 160));
    const rows = input.status === "active"
      ? await prisma.$queryRaw<TaskRow[]>`
          SELECT "OperationalTask"."id", "OperationalTask"."businessId", "OperationalTask"."title", "OperationalTask"."description",
            "OperationalTask"."area", "OperationalTask"."priority", "OperationalTask"."status", "OperationalTask"."href", "OperationalTask"."source",
            "OperationalTask"."assignedToId", "User"."displayName" AS "assignedToName", "OperationalTask"."version", "OperationalTask"."dueAt",
            "OperationalTask"."completedAt", "OperationalTask"."cancelledAt", "OperationalTask"."createdAt", "OperationalTask"."updatedAt"
          FROM "OperationalTask" LEFT JOIN "User" ON "User"."id" = "OperationalTask"."assignedToId" AND "User"."businessId" = "OperationalTask"."businessId"
          WHERE "OperationalTask"."businessId" = ${input.businessId} AND "OperationalTask"."status" IN ('open', 'in_progress')
          ORDER BY CASE "OperationalTask"."priority" WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END, "OperationalTask"."updatedAt" DESC
          LIMIT ${limit}
        `
      : await prisma.$queryRaw<TaskRow[]>`
          SELECT "OperationalTask"."id", "OperationalTask"."businessId", "OperationalTask"."title", "OperationalTask"."description",
            "OperationalTask"."area", "OperationalTask"."priority", "OperationalTask"."status", "OperationalTask"."href", "OperationalTask"."source",
            "OperationalTask"."assignedToId", "User"."displayName" AS "assignedToName", "OperationalTask"."version", "OperationalTask"."dueAt",
            "OperationalTask"."completedAt", "OperationalTask"."cancelledAt", "OperationalTask"."createdAt", "OperationalTask"."updatedAt"
          FROM "OperationalTask" LEFT JOIN "User" ON "User"."id" = "OperationalTask"."assignedToId" AND "User"."businessId" = "OperationalTask"."businessId"
          WHERE "OperationalTask"."businessId" = ${input.businessId} AND (${input.status ?? ""} = '' OR "OperationalTask"."status" = ${input.status ?? ""})
          ORDER BY CASE "OperationalTask"."priority" WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END, "OperationalTask"."updatedAt" DESC
          LIMIT ${limit}
        `;
    return rows.map(toRecord);
  }

  async listAssignees(businessId: string): Promise<OperationalTaskAssignee[]> {
    return prisma.$queryRaw<OperationalTaskAssignee[]>`
      SELECT "id", "displayName" FROM "User"
      WHERE "businessId" = ${businessId} AND "status" = 'ACTIVE'
      ORDER BY "displayName" ASC, "id" ASC LIMIT 100
    `;
  }

  async create(businessId: string, input: CreateOperationalTaskInput) {
    const existing = await prisma.$queryRaw<Array<{ id: string }>>`
      SELECT "id" FROM "OperationalTask" WHERE "businessId" = ${businessId} AND "idempotencyKey" = ${input.idempotencyKey} LIMIT 1
    `;
    if (existing[0]) {
      const task = await this.readOne(businessId, existing[0].id);
      if (task) return { task, replayed: true };
    }
    await this.ensureAssignee(businessId, input.assignedToId);
    const now = new Date();
    const taskId = randomUUID();
    const auditTask: OperationalTaskRecord = {
      id: taskId,
      businessId,
      title: input.title,
      description: input.description ?? null,
      area: input.area,
      priority: input.priority,
      status: "open",
      href: input.href ?? null,
      source: "manual",
      assignedToId: input.assignedToId ?? null,
      assignedToName: null,
      version: 1,
      dueAt: iso(input.dueAt ?? null),
      completedAt: null,
      cancelledAt: null,
      createdAt: now.toISOString(),
      updatedAt: now.toISOString()
    };
    await prisma.$transaction(async (tx: any) => {
      await tx.$executeRaw`
        INSERT INTO "OperationalTask" ("id", "businessId", "createdById", "assignedToId", "title", "description", "area", "priority", "status", "href", "source", "idempotencyKey", "version", "dueAt", "createdAt", "updatedAt")
        VALUES (${taskId}, ${businessId}, ${null}, ${input.assignedToId ?? null}, ${input.title}, ${input.description ?? null}, ${input.area}, ${input.priority}, 'open', ${input.href ?? null}, 'manual', ${input.idempotencyKey}, 1, ${input.dueAt ?? null}, ${now}, ${now})
      `;
      await this.recordAudit(tx, { businessId, topic: "operational_task.created", task: auditTask });
      await this.recordOutbox(tx, { businessId, eventType: "created", task: auditTask, at: now });
    });
    const task = await this.readOne(businessId, taskId);
    if (!task) throw new Error("OPERATIONAL_TASK_CREATE_NOT_VISIBLE");
    return { task, replayed: false };
  }

  async update(businessId: string, taskId: string, input: UpdateOperationalTaskInput) {
    const current = await this.readOne(businessId, taskId);
    if (!current) return null;
    if (current.version !== input.expectedVersion) throw new Error("OPERATIONAL_TASK_VERSION_CONFLICT");
    if ((current.status === "completed" || current.status === "cancelled") && input.status && input.status !== current.status) throw new Error("OPERATIONAL_TASK_TERMINAL_STATE");
    const assignedToId = input.assignedToId === undefined ? current.assignedToId : input.assignedToId;
    const status = input.status ?? current.status;
    await this.ensureAssignee(businessId, assignedToId);
    const now = new Date();
    const completedAt = status === "completed" ? current.completedAt ? new Date(current.completedAt) : now : current.completedAt ? new Date(current.completedAt) : null;
    const cancelledAt = status === "cancelled" ? current.cancelledAt ? new Date(current.cancelledAt) : now : current.cancelledAt ? new Date(current.cancelledAt) : null;
    const next: OperationalTaskRecord = {
      ...current,
      assignedToId,
      assignedToName: null,
      status,
      version: current.version + 1,
      completedAt: iso(completedAt),
      cancelledAt: iso(cancelledAt),
      updatedAt: now.toISOString()
    };
    const changed = await prisma.$transaction(async (tx: any) => {
      const count = await tx.$executeRaw`
        UPDATE "OperationalTask"
        SET "assignedToId" = ${assignedToId}, "status" = ${status}, "completedAt" = ${completedAt}, "cancelledAt" = ${cancelledAt}, "version" = "version" + 1, "updatedAt" = ${now}
        WHERE "businessId" = ${businessId} AND "id" = ${taskId} AND "version" = ${input.expectedVersion}
      `;
      if (Number(count) <= 0) return false;
      const eventType = status === "completed" ? "completed" : status === "cancelled" ? "cancelled" : "updated";
      await this.recordAudit(tx, {
        businessId,
        topic: `operational_task.${eventType}`,
        task: next,
        before: { status: current.status, assignedToId: current.assignedToId, version: current.version }
      });
      await this.recordOutbox(tx, { businessId, eventType, task: next, at: now });
      return true;
    });
    if (!changed) throw new Error("OPERATIONAL_TASK_VERSION_CONFLICT");
    const task = await this.readOne(businessId, taskId);
    if (!task) throw new Error("OPERATIONAL_TASK_UPDATE_NOT_VISIBLE");
    return task;
  }
}
