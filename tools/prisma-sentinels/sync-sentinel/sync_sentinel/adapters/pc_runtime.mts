import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const pcAppRoot = process.cwd();
const readyFile = process.env.SYNC_SENTINEL_READY_FILE;
const token = process.env.SYNC_SENTINEL_TOKEN;
const tempRoot = process.env.SYNC_SENTINEL_TEMP_ROOT;
if (!readyFile || !token || !tempRoot) throw new Error("SYNC_SENTINEL_RUNTIME_ENV_MISSING");

const importFile = async (rel: string) => import(pathToFileURL(path.join(pcAppRoot, rel)).href);
const [
  { prisma },
  { persistSyncIngestPayload },
  { exportPcCatalogDelta },
  { GET: getSalesControl },
] = await Promise.all([
  importFile("src/server/prisma/client.ts"),
  importFile("src/server/services/sync-ingest.service.ts"),
  importFile("src/server/services/catalog-delta-export.service.ts"),
  importFile("app/api/backoffice/sales-control/route.ts"),
]);

const ids = {
  businessId: "biz_sync_sentinel",
  storeId: "store_sync_sentinel",
  terminalId: "terminal_sync_sentinel",
  taxRateId: "tax_sync_sentinel",
  brandId: "brand_sync_sentinel",
  supplierId: "supplier_sync_sentinel",
  productId: "product_sync_sentinel",
  productSupplierId: "product_supplier_sync_sentinel",
  priceListId: "price_list_sync_sentinel",
  priceListItemId: "price_list_item_sync_sentinel",
};

type FaultMode = "online" | "ingest_unavailable" | "mobile_read_unavailable";
let faultMode: FaultMode = "online";

async function seedPc() {
  const now = new Date();
  await prisma.business.upsert({ where: { id: ids.businessId }, update: { name: "Sync Sentinel PC" }, create: { id: ids.businessId, name: "Sync Sentinel PC", currency: "MXN" } });
  await prisma.store.upsert({ where: { businessId_code: { businessId: ids.businessId, code: "SENT" } }, update: { name: "Sentinel Store" }, create: { id: ids.storeId, businessId: ids.businessId, code: "SENT", name: "Sentinel Store" } });
  await prisma.terminal.upsert({ where: { businessId_code: { businessId: ids.businessId, code: "SENT-TAB" } }, update: { storeId: ids.storeId, name: "Sentinel Tablet", isActive: true }, create: { id: ids.terminalId, businessId: ids.businessId, storeId: ids.storeId, code: "SENT-TAB", name: "Sentinel Tablet", isActive: true } });
  await prisma.taxRate.upsert({ where: { id: ids.taxRateId }, update: { name: "IVA Sentinel", rateBps: 1600, isDefault: true, isActive: true }, create: { id: ids.taxRateId, businessId: ids.businessId, name: "IVA Sentinel", rateBps: 1600, isDefault: true, isActive: true } });
  await prisma.brand.upsert({ where: { id: ids.brandId }, update: { name: "Sentinel Brand", status: "ACTIVE" }, create: { id: ids.brandId, businessId: ids.businessId, name: "Sentinel Brand", description: "Synthetic certification brand", status: "ACTIVE" } });
  await prisma.supplier.upsert({ where: { id: ids.supplierId }, update: { name: "Sentinel Supplier", status: "ACTIVE" }, create: { id: ids.supplierId, businessId: ids.businessId, name: "Sentinel Supplier", status: "ACTIVE" } });
  await prisma.product.upsert({
    where: { id: ids.productId },
    update: { sku: "SYNC-SENTINEL-001", name: "Sentinel Product v1", category: "SENTINEL", brandId: ids.brandId, taxRateId: ids.taxRateId, priceCents: 1234, costCents: 700, stockOnHand: 80, isActive: true },
    create: { id: ids.productId, businessId: ids.businessId, sku: "SYNC-SENTINEL-001", name: "Sentinel Product v1", category: "SENTINEL", brandId: ids.brandId, taxRateId: ids.taxRateId, priceCents: 1234, costCents: 700, stockOnHand: 80, isActive: true },
  });
  await prisma.barcode.upsert({ where: { businessId_code: { businessId: ids.businessId, code: "7500000000001" } }, update: { productId: ids.productId }, create: { id: "barcode_sync_sentinel", businessId: ids.businessId, productId: ids.productId, code: "7500000000001" } });
  await prisma.productSupplier.upsert({ where: { businessId_productId_supplierId: { businessId: ids.businessId, productId: ids.productId, supplierId: ids.supplierId } }, update: { isPrimary: true, status: "ACTIVE", leadTimeDays: 2 }, create: { id: ids.productSupplierId, businessId: ids.businessId, productId: ids.productId, supplierId: ids.supplierId, isPrimary: true, status: "ACTIVE", leadTimeDays: 2 } });
  await prisma.priceList.upsert({ where: { id: ids.priceListId }, update: { name: "Sentinel Retail", currency: "MXN", isDefault: true, isActive: true, startsAt: now }, create: { id: ids.priceListId, businessId: ids.businessId, name: "Sentinel Retail", currency: "MXN", isDefault: true, isActive: true, startsAt: now } });
  const existingPli = await prisma.priceListItem.findFirst({ where: { id: ids.priceListItemId, businessId: ids.businessId } });
  if (existingPli) await prisma.priceListItem.update({ where: { id: ids.priceListItemId }, data: { priceCents: 1234, startsAt: now } });
  else await prisma.priceListItem.create({ data: { id: ids.priceListItemId, businessId: ids.businessId, priceListId: ids.priceListId, productId: ids.productId, priceCents: 1234, startsAt: now } });
}

function json(res: http.ServerResponse, status: number, value: unknown) {
  const responseBody = JSON.stringify(value);
  res.writeHead(status, { "content-type": "application/json", "content-length": Buffer.byteLength(responseBody), "cache-control": "no-store" });
  res.end(responseBody);
}

async function body(req: http.IncomingMessage) {
  const chunks: Buffer[] = [];
  for await (const chunk of req) chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  if (!chunks.length) return null;
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

async function sendWebResponse(res: http.ServerResponse, response: Response) {
  const bytes = Buffer.from(await response.arrayBuffer());
  const headers: Record<string, string> = {};
  response.headers.forEach((value, key) => { headers[key] = value; });
  headers["content-length"] = String(bytes.length);
  headers["cache-control"] = headers["cache-control"] || "no-store";
  res.writeHead(response.status, headers);
  res.end(bytes);
}

function ingestHttpStatus(result: any) {
  const summary = result?.summary ?? {};
  if (Number(summary.rejected ?? 0) > 0) return 207;
  if (Number(summary.conflict ?? 0) > 0 || Number(summary.duplicate ?? 0) > 0) return 202;
  return 200;
}
function controlAuthorized(req: http.IncomingMessage) { return req.headers["x-sync-sentinel-token"] === token; }

await seedPc();

const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url ?? "/", "http://127.0.0.1");
    if (req.method === "GET" && url.pathname === "/api/health") {
      if (faultMode === "mobile_read_unavailable") return json(res, 503, { ok: false, code: "SYNC_SENTINEL_PC_MOBILE_READ_UNAVAILABLE" });
      return json(res, 200, { ok: true, source: "sync-sentinel-loopback-bridge", canonicalRuntime: "3130", faultMode });
    }
    if (req.method === "GET" && url.pathname === "/api/backoffice/sales-control") {
      if (faultMode === "mobile_read_unavailable") return json(res, 503, { ok: false, code: "SYNC_SENTINEL_PC_MOBILE_READ_UNAVAILABLE" });
      const request = new Request(`http://127.0.0.1${url.pathname}${url.search}`, { method: "GET", headers: { Accept: "application/json" } });
      return sendWebResponse(res, await getSalesControl(request));
    }
    if (req.method === "POST" && url.pathname === "/api/backoffice/sync/ingest") {
      if (faultMode === "ingest_unavailable") return json(res, 503, { ok: false, code: "SYNC_SENTINEL_PC_INGEST_UNAVAILABLE" });
      const payload = await body(req);
      const result = await persistSyncIngestPayload(payload);
      return json(res, ingestHttpStatus(result), { ok: Number(result?.summary?.rejected ?? 0) === 0, data: result, endpoint: "POST /api/backoffice/sync/ingest", persistence: result?.meta?.persistence });
    }
    if (req.method === "POST" && url.pathname === "/api/sync/export/catalog-delta") {
      const payload = (await body(req)) ?? {};
      const result = await exportPcCatalogDelta({ ...payload, businessId: payload.businessId || ids.businessId }, { recordAudit: false });
      return json(res, 200, { ok: true, data: result.envelope, auditEventId: null });
    }
    if (req.method === "POST" && url.pathname === "/__sentinel/fault") {
      if (!controlAuthorized(req)) return json(res, 403, { ok: false, code: "FORBIDDEN" });
      const payload = (await body(req)) ?? {};
      const requested = String(payload.mode || "online");
      if (!(["online", "ingest_unavailable", "mobile_read_unavailable"] as string[]).includes(requested)) return json(res, 400, { ok: false, code: "INVALID_FAULT_MODE" });
      faultMode = requested as FaultMode;
      return json(res, 200, { ok: true, faultMode });
    }
    if (req.method === "POST" && url.pathname === "/__sentinel/expected-scope") {
      if (!controlAuthorized(req)) return json(res, 403, { ok: false, code: "FORBIDDEN" });
      const payload = (await body(req)) ?? {};
      process.env.PRISMA_SYNC_TENANT_ID = String(payload.tenantId || "").trim();
      process.env.PRISMA_SYNC_CUSTOMER_ID = String(payload.customerId || "").trim();
      return json(res, 200, { ok: true, tenantScopeEnabled: Boolean(process.env.PRISMA_SYNC_TENANT_ID), customerScopeEnabled: Boolean(process.env.PRISMA_SYNC_CUSTOMER_ID) });
    }
    if (req.method === "POST" && url.pathname === "/__sentinel/catalog-mutation") {
      if (!controlAuthorized(req)) return json(res, 403, { ok: false, code: "FORBIDDEN" });
      const payload = (await body(req)) ?? {};
      const product = await prisma.product.update({ where: { id: ids.productId }, data: { name: String(payload.name || "Sentinel Product v2"), priceCents: Number(payload.priceCents ?? 1777), stockOnHand: Number(payload.stockOnHand ?? 999) } });
      return json(res, 200, { ok: true, product: { id: product.id, name: product.name, priceCents: product.priceCents, stockOnHand: product.stockOnHand, updatedAt: product.updatedAt } });
    }
    if (req.method === "POST" && url.pathname === "/__sentinel/catalog-envelope") {
      if (!controlAuthorized(req)) return json(res, 403, { ok: false, code: "FORBIDDEN" });
      const payload = (await body(req)) ?? {};
      const result = await exportPcCatalogDelta({ ...payload, businessId: payload.businessId || ids.businessId }, { recordAudit: false });
      return json(res, 200, { ok: true, data: result.envelope });
    }
    if (req.method === "GET" && url.pathname === "/__sentinel/state") {
      if (!controlAuthorized(req)) return json(res, 403, { ok: false, code: "FORBIDDEN" });
      const businessId = url.searchParams.get("businessId")?.trim() || ids.businessId;
      const eventId = url.searchParams.get("eventId")?.trim() || "";
      const folio = url.searchParams.get("folio")?.trim() || "SYNC-SENTINEL-SALE";
      const [sale, saleCount, product, outbox, event] = await Promise.all([
        prisma.sale.findFirst({ where: { businessId, folio }, include: { lines: true, paymentTenders: true } }),
        prisma.sale.count({ where: { businessId } }),
        prisma.product.findUnique({ where: { id: ids.productId } }),
        prisma.outboxEvent.findMany({ where: { businessId, topic: "sale.completed" }, orderBy: { createdAt: "desc" }, take: 25 }),
        eventId ? prisma.outboxEvent.findUnique({ where: { id: eventId } }) : Promise.resolve(null),
      ]);
      return json(res, 200, { ok: true, sale, saleCount, product, outbox, event, faultMode });
    }
    return json(res, 404, { ok: false, code: "NOT_FOUND" });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return json(res, 500, { ok: false, code: "SENTINEL_BRIDGE_ERROR", message });
  }
});

server.listen(0, "127.0.0.1", () => {
  const address = server.address();
  if (!address || typeof address === "string") throw new Error("SENTINEL_BRIDGE_ADDRESS_INVALID");
  fs.mkdirSync(path.dirname(readyFile), { recursive: true });
  fs.writeFileSync(readyFile, JSON.stringify({ ready: true, pid: process.pid, port: address.port, canonicalRuntime: "3130", businessId: ids.businessId, terminalId: ids.terminalId, storeId: ids.storeId, productId: ids.productId }, null, 2), "utf8");
  console.log(`SYNC_SENTINEL_PC_BRIDGE_READY port=${address.port}`);
});

async function shutdown() {
  await new Promise<void>((resolve) => server.close(() => resolve()));
  await prisma.$disconnect();
  process.exit(0);
}
process.on("SIGTERM", () => { void shutdown(); });
process.on("SIGINT", () => { void shutdown(); });