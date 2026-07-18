import { prisma } from "../src/server/prisma/client";
import { OperationalTaskRepository } from "../src/server/repositories/operational-task.repository";

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

async function bootstrap() {
  const ddl = [
    `CREATE TABLE "Business" ("id" TEXT NOT NULL PRIMARY KEY, "name" TEXT NOT NULL, "taxId" TEXT, "currency" TEXT NOT NULL DEFAULT 'MXN', "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)`,
    `CREATE TABLE "User" ("id" TEXT NOT NULL PRIMARY KEY, "businessId" TEXT NOT NULL, "displayName" TEXT NOT NULL, "email" TEXT, "status" TEXT NOT NULL DEFAULT 'ACTIVE', "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)`,
    `CREATE TABLE "AuditEvent" ("id" TEXT NOT NULL PRIMARY KEY, "businessId" TEXT NOT NULL, "actorId" TEXT, "topic" TEXT NOT NULL, "entityType" TEXT NOT NULL, "entityId" TEXT, "summary" TEXT NOT NULL, "beforeJson" TEXT, "afterJson" TEXT, "metadataJson" TEXT, "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)`,
    `CREATE TABLE "OutboxEvent" ("id" TEXT NOT NULL PRIMARY KEY, "businessId" TEXT NOT NULL, "terminalId" TEXT, "topic" TEXT NOT NULL, "eventType" TEXT, "aggregateId" TEXT NOT NULL, "idempotencyKey" TEXT, "correlationId" TEXT, "payloadJson" TEXT NOT NULL, "source" TEXT, "schemaVersion" TEXT, "status" TEXT NOT NULL, "lifecycleStatus" TEXT, "attempts" INTEGER NOT NULL DEFAULT 0, "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "sentAt" DATETIME, "receivedAt" DATETIME, "validatedAt" DATETIME, "acceptedAt" DATETIME, "projectedAt" DATETIME, "reconciledAt" DATETIME, "failedAt" DATETIME, "deadLetterAt" DATETIME, "conflictCode" TEXT, "diagnosticsJson" TEXT, "lastError" TEXT)`,
    `CREATE TABLE "OperationalTask" ("id" TEXT NOT NULL PRIMARY KEY, "businessId" TEXT NOT NULL, "createdById" TEXT, "assignedToId" TEXT, "title" TEXT NOT NULL, "description" TEXT, "area" TEXT NOT NULL, "priority" TEXT NOT NULL DEFAULT 'medium', "status" TEXT NOT NULL DEFAULT 'open', "href" TEXT, "source" TEXT NOT NULL DEFAULT 'manual', "idempotencyKey" TEXT, "version" INTEGER NOT NULL DEFAULT 1, "dueAt" DATETIME, "completedAt" DATETIME, "cancelledAt" DATETIME, "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)`,
    `CREATE UNIQUE INDEX "OperationalTask_businessId_idempotencyKey_key" ON "OperationalTask"("businessId", "idempotencyKey")`
  ];
  for (const statement of ddl) await prisma.$executeRawUnsafe(statement);
  await prisma.$executeRawUnsafe(`INSERT INTO "Business" ("id", "name", "currency") VALUES ('biz-task-a', 'Task A', 'MXN'), ('biz-task-b', 'Task B', 'MXN')`);
  await prisma.$executeRawUnsafe(`INSERT INTO "User" ("id", "businessId", "displayName", "status") VALUES ('user-task-a', 'biz-task-a', 'Operadora A', 'ACTIVE'), ('user-task-b', 'biz-task-b', 'Operador B', 'ACTIVE')`);
}

async function main() {
  if (!process.env.DATABASE_URL) throw new Error("OPERATIONAL_TASK_RUNTIME_DATABASE_URL_REQUIRED");
  await bootstrap();
  const repository = new OperationalTaskRepository();
  const created = await repository.create("biz-task-a", {
    title: "Contar exhibición",
    description: "Validar faltantes antes de apertura.",
    area: "Inventario",
    priority: "high",
    assignedToId: "user-task-a",
    idempotencyKey: "operational-task-runtime-create-1"
  });
  assert(!created.replayed && created.task.status === "open" && created.task.version === 1, "OPERATIONAL_TASK_CREATE_READ_AFTER_WRITE_FAILED");
  assert(created.task.assignedToName === "Operadora A", "OPERATIONAL_TASK_ASSIGNMENT_READ_FAILED");

  const replay = await repository.create("biz-task-a", {
    title: "Ignored due to idempotency",
    area: "Inventario",
    priority: "low",
    idempotencyKey: "operational-task-runtime-create-1"
  });
  assert(replay.replayed && replay.task.id === created.task.id, "OPERATIONAL_TASK_IDEMPOTENCY_REPLAY_FAILED");

  const started = await repository.update("biz-task-a", created.task.id, { expectedVersion: created.task.version, status: "in_progress" });
  assert(started?.status === "in_progress" && started.version === 2, "OPERATIONAL_TASK_START_READ_AFTER_WRITE_FAILED");

  let conflict = false;
  try {
    await repository.update("biz-task-a", created.task.id, { expectedVersion: 1, status: "completed" });
  } catch (error) {
    conflict = error instanceof Error && error.message === "OPERATIONAL_TASK_VERSION_CONFLICT";
  }
  assert(conflict, "OPERATIONAL_TASK_VERSION_CONFLICT_NOT_ENFORCED");

  const completed = await repository.update("biz-task-a", created.task.id, { expectedVersion: started!.version, status: "completed" });
  assert(completed?.status === "completed" && completed.completedAt !== null, "OPERATIONAL_TASK_COMPLETION_FAILED");

  let terminal = false;
  try {
    await repository.update("biz-task-a", created.task.id, { expectedVersion: completed!.version, status: "open" });
  } catch (error) {
    terminal = error instanceof Error && error.message === "OPERATIONAL_TASK_TERMINAL_STATE";
  }
  assert(terminal, "OPERATIONAL_TASK_TERMINAL_STATE_NOT_ENFORCED");

  let foreignAssignee = false;
  try {
    await repository.create("biz-task-a", { title: "Invalid assignee", area: "Operación", priority: "medium", assignedToId: "user-task-b", idempotencyKey: "operational-task-runtime-create-foreign" });
  } catch (error) {
    foreignAssignee = error instanceof Error && error.message === "OPERATIONAL_TASK_ASSIGNEE_NOT_FOUND";
  }
  assert(foreignAssignee, "OPERATIONAL_TASK_BUSINESS_SCOPE_NOT_ENFORCED");

  const crossBusiness = await repository.update("biz-task-b", created.task.id, { expectedVersion: completed!.version, status: "completed" });
  assert(crossBusiness === null, "OPERATIONAL_TASK_CROSS_BUSINESS_READ_LEAK");
  const auditCount = await prisma.auditEvent.count({ where: { businessId: "biz-task-a", entityType: "OperationalTask" } });
  assert(auditCount === 3, `OPERATIONAL_TASK_AUDIT_COUNT_INVALID:${auditCount}`);
  const outboxEvents = await prisma.$queryRaw<Array<{ idempotencyKey: string; payloadJson: string }>>`SELECT "idempotencyKey", "payloadJson" FROM "OutboxEvent" WHERE "businessId" = 'biz-task-a' ORDER BY "createdAt" ASC`;
  assert(outboxEvents.length === 3 && outboxEvents.every((event) => event.idempotencyKey.startsWith("operational_task:")), "OPERATIONAL_TASK_OUTBOX_MISSING");
  assert(outboxEvents.every((event) => !event.payloadJson.includes("Contar exhibición") && !event.payloadJson.includes("description")), "OPERATIONAL_TASK_OUTBOX_NOT_MINIMIZED");
  console.log("operational_tasks_runtime=PASS");
}

main().catch(async (error) => {
  await prisma.$disconnect().catch(() => undefined);
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
}).then(async () => {
  await prisma.$disconnect();
});
