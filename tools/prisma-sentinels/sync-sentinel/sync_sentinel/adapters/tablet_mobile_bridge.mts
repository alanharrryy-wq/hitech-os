import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const tabletAppRoot = process.cwd();
const readyFile = process.env.SYNC_SENTINEL_TABLET_READY_FILE;
const token = process.env.SYNC_SENTINEL_TOKEN;
if (!readyFile || !token) throw new Error("SYNC_SENTINEL_TABLET_MOBILE_ENV_MISSING");

const importFile = async (rel: string) => import(pathToFileURL(path.join(tabletAppRoot, rel)).href);
const [
  { prisma },
  { getLowStockProducts, getOutboxEvents },
  { getTodaySalesSummary },
  { readPosListInput, readSalesTodayInput },
  { countOutboxByState },
] = await Promise.all([
  importFile("src/server/prisma/client.ts"),
  importFile("src/server/pos-reports/index.ts"),
  importFile("src/server/pos-api/sales-summary.prisma.ts"),
  importFile("src/server/pos-api/validators.ts"),
  importFile("src/server/pos-outbox/index.ts"),
]);

type FaultMode = "online" | "unavailable" | "malformed_outbox";
let faultMode: FaultMode = "online";
const requestCounts = new Map<string, number>();

function bump(pathname: string) {
  requestCounts.set(pathname, (requestCounts.get(pathname) ?? 0) + 1);
}

function requestCountObject() {
  return Object.fromEntries([...requestCounts.entries()].sort(([a], [b]) => a.localeCompare(b)));
}

function json(res: http.ServerResponse, status: number, value: unknown) {
  const responseBody = JSON.stringify(value);
  res.writeHead(status, {
    "content-type": "application/json",
    "content-length": Buffer.byteLength(responseBody),
    "cache-control": "no-store",
  });
  res.end(responseBody);
}

async function body(req: http.IncomingMessage) {
  const chunks: Buffer[] = [];
  for await (const chunk of req) chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  if (!chunks.length) return {};
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

function controlAuthorized(req: http.IncomingMessage) {
  return req.headers["x-sync-sentinel-token"] === token;
}

function sourceUnavailable(res: http.ServerResponse) {
  return json(res, 503, { ok: false, code: "SYNC_SENTINEL_TABLET_SOURCE_UNAVAILABLE" });
}

const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url ?? "/", "http://127.0.0.1");
    const pathname = url.pathname;

    if (pathname.startsWith("/__sentinel/")) {
      if (!controlAuthorized(req)) return json(res, 403, { ok: false, code: "FORBIDDEN" });

      if (req.method === "GET" && pathname === "/__sentinel/state") {
        const businessId = url.searchParams.get("businessId")?.trim() || "biz_sync_sentinel";
        const counts = await countOutboxByState(businessId);
        const events = await getOutboxEvents({ businessId, limit: 200 });
        return json(res, 200, {
          ok: true,
          businessId,
          counts,
          eventCount: events.length,
          eventIds: events.map((event: any) => event.id),
          faultMode,
          requestCounts: requestCountObject(),
        });
      }

      if (req.method === "POST" && pathname === "/__sentinel/fault") {
        const payload = (await body(req)) as Record<string, unknown>;
        const requested = String(payload.mode ?? "online");
        if (!["online", "unavailable", "malformed_outbox"].includes(requested)) {
          return json(res, 400, { ok: false, code: "INVALID_FAULT_MODE" });
        }
        faultMode = requested as FaultMode;
        return json(res, 200, { ok: true, faultMode });
      }

      if (req.method === "POST" && pathname === "/__sentinel/outbox-mutation") {
        const payload = (await body(req)) as Record<string, unknown>;
        const businessId = String(payload.businessId ?? "biz_sync_sentinel");
        const terminalId = String(payload.terminalId ?? "terminal_sync_sentinel");
        const eventId = String(payload.eventId ?? `event_mobile_sentinel_${Date.now()}`);
        const aggregateId = String(payload.aggregateId ?? eventId.replace(/^event_/, "aggregate_"));
        const status = String(payload.status ?? "pending");
        const ageSeconds = Math.max(0, Number(payload.ageSeconds ?? 0));
        const createdAt = new Date(Date.now() - ageSeconds * 1000);
        await prisma.outboxEvent.deleteMany({ where: { id: eventId } });
        await prisma.outboxEvent.create({
          data: {
            id: eventId,
            businessId,
            terminalId,
            topic: "mobile.sentinel.synthetic",
            aggregateId,
            idempotencyKey: `idem_${eventId}`,
            payloadJson: JSON.stringify({
              eventId,
              eventType: "mobile.sentinel.synthetic",
              businessId,
              terminalId,
              aggregateId,
              occurredAt: createdAt.toISOString(),
              syntheticTestData: true,
            }),
            source: "sync-sentinel-mobile",
            schemaVersion: "1.0.0",
            status,
            createdAt,
          },
        });
        return json(res, 200, { ok: true, eventId, status, createdAt: createdAt.toISOString() });
      }

      if (req.method === "POST" && pathname === "/__sentinel/outbox-delete") {
        const payload = (await body(req)) as Record<string, unknown>;
        const eventId = String(payload.eventId ?? "").trim();
        if (!eventId) return json(res, 400, { ok: false, code: "EVENT_ID_REQUIRED" });
        const deleted = await prisma.outboxEvent.deleteMany({ where: { id: eventId } });
        return json(res, 200, { ok: true, eventId, deleted: deleted.count });
      }

      return json(res, 404, { ok: false, code: "NOT_FOUND" });
    }

    bump(pathname);
    if (faultMode === "unavailable") return sourceUnavailable(res);

    if (req.method === "GET" && pathname === "/api/health") {
      return json(res, 200, { system: "PRISMA", app: "tablet", status: "ok", sentinelTransport: true });
    }

    if (req.method === "GET" && pathname === "/api/pos/sales/today") {
      const input = readSalesTodayInput(url.searchParams);
      const summary = await getTodaySalesSummary(input);
      return json(res, 200, {
        ok: true,
        data: { summary },
        meta: { endpoint: "GET /api/pos/sales/today", businessId: input.businessId, terminalId: input.terminalId ?? null },
      });
    }

    if (req.method === "GET" && pathname === "/api/pos/inventory/low-stock") {
      const input = readPosListInput(url.searchParams, 50, 200);
      const products = await getLowStockProducts(input);
      return json(res, 200, {
        ok: true,
        data: { products, count: products.length },
        meta: { endpoint: "GET /api/pos/inventory/low-stock", businessId: input.businessId, threshold: input.threshold },
      });
    }

    if (req.method === "GET" && pathname === "/api/pos/events/outbox") {
      if (faultMode === "malformed_outbox") {
        const invalid = "{this-is-not-valid-json";
        res.writeHead(200, {
          "content-type": "application/json",
          "content-length": Buffer.byteLength(invalid),
          "cache-control": "no-store",
        });
        return res.end(invalid);
      }
      const input = readPosListInput(url.searchParams, 50, 200);
      const [events, counts] = await Promise.all([
        getOutboxEvents(input),
        countOutboxByState(input.businessId),
      ]);
      return json(res, 200, {
        ok: true,
        data: { events, counts, count: events.length },
        meta: { endpoint: "GET /api/pos/events/outbox", businessId: input.businessId, status: input.status ?? null },
      });
    }

    return json(res, 404, { ok: false, code: "NOT_FOUND" });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return json(res, 500, { ok: false, code: "SENTINEL_TABLET_BRIDGE_ERROR", message });
  }
});

server.listen(0, "127.0.0.1", () => {
  const address = server.address();
  if (!address || typeof address === "string") throw new Error("SENTINEL_TABLET_BRIDGE_ADDRESS_INVALID");
  fs.mkdirSync(path.dirname(readyFile), { recursive: true });
  fs.writeFileSync(
    readyFile,
    JSON.stringify({ ready: true, pid: process.pid, port: address.port, canonicalRuntime: "3120" }, null, 2),
    "utf8",
  );
  console.log(`SYNC_SENTINEL_TABLET_MOBILE_BRIDGE_READY port=${address.port}`);
});

async function shutdown() {
  await new Promise<void>((resolve) => server.close(() => resolve()));
  await prisma.$disconnect();
  process.exit(0);
}
process.on("SIGTERM", () => { void shutdown(); });
process.on("SIGINT", () => { void shutdown(); });
