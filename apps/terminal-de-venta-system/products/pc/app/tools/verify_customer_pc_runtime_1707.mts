import { createCustomer, updateCustomer } from "../src/server/services/customer.service";
import { prisma } from "../src/server/prisma/client";
import { projectAcceptedSyncEvent } from "../src/server/services/sync-projectors.service";

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

async function main() {
  if (!process.env.DATABASE_URL) throw new Error("CUSTOMER_PC_RUNTIME_DATABASE_URL_REQUIRED");

  const created = await createCustomer({
    displayName: "Runtime Customer",
    phone: "5550101",
    email: "runtime@example.test",
    segment: "runtime",
    fiscalProfile: { legalName: "Runtime Fiscal", rfc: "RUN010101AAA" }
  });
  assert(created.displayName === "Runtime Customer" && created.version === 1, "CUSTOMER_PC_CREATE_READ_AFTER_WRITE_FAILED");

  const updated = await updateCustomer(created.id, {
    displayName: "Runtime Customer Edit",
    expectedVersion: created.version,
    isActive: true
  });
  assert(updated?.displayName === "Runtime Customer Edit" && updated.version === 2, "CUSTOMER_PC_UPDATE_READ_AFTER_WRITE_FAILED");

  let versionConflict = false;
  try {
    await updateCustomer(created.id, { displayName: "Stale update", expectedVersion: 1 });
  } catch (error) {
    versionConflict = error instanceof Error && error.message === "CUSTOMER_VERSION_CONFLICT";
  }
  assert(versionConflict, "CUSTOMER_PC_VERSION_CONFLICT_NOT_ENFORCED");

  const event = {
    eventId: "evt-customer-runtime-1",
    topic: "customer.created",
    aggregateId: "tablet-runtime-customer",
    businessId: "biz-runtime",
    terminalId: "term-runtime",
    storeId: "store-runtime",
    actorId: "tablet-cashier",
    occurredAt: "2026-07-17T01:00:00.000Z",
    payload: {
      retailCustomerId: "tablet-runtime-customer",
      displayName: "Offline Runtime Customer",
      version: 1,
      updatedAt: "2026-07-17T01:00:00.000Z"
    }
  } as any;
  const first = await prisma.$transaction((tx) => projectAcceptedSyncEvent(tx, event));
  assert(first.status === "projected", `CUSTOMER_PC_PROJECTOR_CREATE_FAILED:${first.status}`);
  const replay = await prisma.$transaction((tx) => projectAcceptedSyncEvent(tx, event));
  assert(replay.status === "reconciled", `CUSTOMER_PC_PROJECTOR_REPLAY_FAILED:${replay.status}`);

  const collision = {
    ...event,
    eventId: "evt-customer-runtime-2",
    aggregateId: "tablet-runtime-collision",
    payload: { ...event.payload, retailCustomerId: "tablet-runtime-collision", displayName: "Offline Runtime Customer" }
  };
  const duplicate = await prisma.$transaction((tx) => projectAcceptedSyncEvent(tx, collision));
  assert(duplicate.status === "conflict" && duplicate.diagnostics.includes("CUSTOMER_CREATE_NAME_COLLISION"), "CUSTOMER_PC_PROJECTOR_DUPLICATE_FAILED");

  const wrongScope = await prisma.$transaction((tx) => projectAcceptedSyncEvent(tx, { ...event, eventId: "evt-customer-runtime-3", businessId: "biz-other" }));
  assert(wrongScope.status === "conflict" && wrongScope.diagnostics.includes("CUSTOMER_CREATE_SCOPE_CONFLICT"), "CUSTOMER_PC_PROJECTOR_SCOPE_FAILED");

  const auditCount = await prisma.auditEvent.count({ where: { businessId: "biz-runtime", entityType: "Customer" } });
  assert(auditCount >= 3, "CUSTOMER_PC_AUDIT_MISSING");
  await prisma.$disconnect();
  console.log("customer_pc_runtime=PASS");
}

main().catch(async (error) => {
  await prisma.$disconnect().catch(() => undefined);
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
});
