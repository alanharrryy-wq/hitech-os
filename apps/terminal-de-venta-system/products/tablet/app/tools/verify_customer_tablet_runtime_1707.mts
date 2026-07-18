import { GET, POST } from "../app/api/pos/customers/route";
import { applyCustomerProjectionEnvelope } from "../src/server/sync/customer-projection-pull";
import { prisma } from "../src/server/prisma/client";
import { saleCompletedEvent } from "../src/server/pos-engine/event-factory";

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

function customerRequest(body: Record<string, unknown>) {
  return new Request("http://local/api/pos/customers", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body)
  });
}

async function main() {
  if (!process.env.TABLET_DATABASE_URL) throw new Error("CUSTOMER_TABLET_RUNTIME_DATABASE_URL_REQUIRED");
  const created = await POST(customerRequest({ displayName: "Tablet Customer" }));
  assert(created.status === 201, `CUSTOMER_TABLET_CREATE_FAILED:${created.status}`);
  const createdBody = await created.json() as { data: { customer: { id: string } } };
  const customerId = createdBody.data.customer.id;

  const listed = await GET(new Request("http://local/api/pos/customers?q=Tablet"));
  const listedBody = await listed.json() as { data: { customers: Array<{ id: string; displayName: string }> } };
  assert(listedBody.data.customers.some((customer) => customer.id === customerId && customer.displayName === "Tablet Customer"), "CUSTOMER_TABLET_SEARCH_FAILED");

  const duplicate = await POST(customerRequest({ displayName: "tablet customer" }));
  assert(duplicate.status === 409, "CUSTOMER_TABLET_DUPLICATE_NOT_REJECTED");
  const denied = await POST(customerRequest({ displayName: "Wrong scope", businessId: "biz-other" }));
  assert(denied.status === 403, "CUSTOMER_TABLET_SCOPE_NOT_DENIED");

  const at = "2026-07-17T00:00:00.000Z";
  const envelope = {
    contractId: "PRISMA_PC_TO_TABLET_CUSTOMER_PROJECTION_V1",
    schemaVersion: "1.0.0",
    stream: "pc.customer.projection.v1",
    businessId: "biz-tablet",
    generatedAt: at,
    cursor: { requested: null, next: `${at}~pc-customer`, hasMore: false },
    changes: [{
      changeId: "pc.customer.projection.v1:pc-customer:1",
      customerId: "pc-customer",
      businessId: "biz-tablet",
      operation: "upsert",
      version: 1,
      occurredAt: at,
      cursor: `${at}~pc-customer`,
      payload: { id: "pc-customer", businessId: "biz-tablet", displayName: "PC Projection", isActive: true, version: 1, sourceSurface: "pc", updatedAt: at, tombstoneAt: null }
    }]
  };
  const applied = await applyCustomerProjectionEnvelope({ businessId: "biz-tablet", terminalId: "term-tablet", envelope });
  assert(applied.ok && applied.counts.applied === 1, "CUSTOMER_TABLET_PROJECTION_APPLY_FAILED");
  const replay = await applyCustomerProjectionEnvelope({ businessId: "biz-tablet", terminalId: "term-tablet", envelope });
  assert(replay.ok && replay.counts.duplicate === 1, "CUSTOMER_TABLET_PROJECTION_REPLAY_FAILED");

  const checkpointCount = await prisma.syncCheckpoint.count({ where: { businessId: "biz-tablet", stream: "pc.customer.projection.v1", status: "acked" } });
  assert(checkpointCount === 1, "CUSTOMER_TABLET_CHECKPOINT_MISSING");
  const outbox = await prisma.outboxEvent.findFirst({ where: { businessId: "biz-tablet", topic: "customer.created" } });
  assert(Boolean(outbox) && !/fiscal|credit|phone|email|rfc/i.test(outbox!.payloadJson), "CUSTOMER_TABLET_OUTBOX_PRIVACY_FAILED");

  const saleEvent = saleCompletedEvent({
    saleId: "sale-customer", folio: "F-1", businessId: "biz-tablet", terminalId: "term-tablet", cashSessionId: "cash-1", customerId: "pc-customer",
    clientRequestId: "request-customer", cashier: "tablet-cashier", subtotalCents: 1800, discountCents: 0, totalCents: 1800,
    paymentMethod: "cash", cashReceivedCents: 1800, changeCents: 0, paymentTenders: [], status: "COMPLETED",
    createdAt: new Date(at), completedAt: new Date(at), lines: []
  }, { businessId: "biz-tablet", storeId: "store-tablet", terminalId: "term-tablet", deviceId: "device-tablet", actorId: "tablet-cashier", occurredAt: new Date(at) });
  assert(saleEvent.payload.saleCustomerId === "pc-customer" && saleEvent.payload.customerId === undefined, "CUSTOMER_SALE_OUTBOX_SCOPE_FAILED");
  await prisma.$disconnect();
  console.log("customer_tablet_runtime=PASS");
}

main().catch(async (error) => {
  await prisma.$disconnect().catch(() => undefined);
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
});
