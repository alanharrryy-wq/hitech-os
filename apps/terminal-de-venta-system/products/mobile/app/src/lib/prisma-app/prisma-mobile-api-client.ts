import {
  PrismaMobileAlertsPayloadSchema,
  PrismaMobileBranchesPayloadSchema,
  PrismaMobileCashCurrentPayloadSchema,
  PrismaMobileHealthPayloadSchema,
  PrismaMobileInventoryWatchlistPayloadSchema,
  PrismaMobileReportsDailyPayloadSchema,
  PrismaMobileSalesTodayPayloadSchema,
  PrismaMobileSummaryPayloadSchema,
  type PrismaMobileAlertsPayload,
  type PrismaMobileBranchesPayload,
  type PrismaMobileCashCurrentPayload,
  type PrismaMobileHealthPayload,
  type PrismaMobileInventoryWatchlistPayload,
  type PrismaMobileReportsDailyPayload,
  type PrismaMobileSalesTodayPayload,
  type PrismaMobileSummaryPayload
} from "./prisma-app-api-contracts";
import { readCachedPrismaMobileSnapshot, writeCachedPrismaMobileSnapshot } from "./prisma-mobile-cache";
import {
  PRISMA_MOBILE_SNAPSHOT_ENDPOINT,
  PrismaMobileSnapshotEnvelopeSchema,
  createClientSnapshot,
  type PrismaMobileClientSnapshot,
  type PrismaMobileSnapshotPayload,
  type PrismaMobileSnapshotParts
} from "./prisma-mobile-snapshot-contract";
import { prismaMobileErrorMessage } from "./prisma-mobile-error";

const endpointPaths = {
  summary: "/api/mobile/summary",
  salesToday: "/api/mobile/sales/today",
  cashCurrent: "/api/mobile/cash/current",
  inventoryWatchlist: "/api/mobile/inventory/watchlist",
  alerts: "/api/mobile/alerts",
  reportsDaily: "/api/mobile/reports/daily",
  branches: "/api/mobile/branches",
  health: "/api/mobile/health"
} as const;

const payloadSchemas = {
  summary: PrismaMobileSummaryPayloadSchema,
  salesToday: PrismaMobileSalesTodayPayloadSchema,
  cashCurrent: PrismaMobileCashCurrentPayloadSchema,
  inventoryWatchlist: PrismaMobileInventoryWatchlistPayloadSchema,
  alerts: PrismaMobileAlertsPayloadSchema,
  reportsDaily: PrismaMobileReportsDailyPayloadSchema,
  branches: PrismaMobileBranchesPayloadSchema,
  health: PrismaMobileHealthPayloadSchema
};

type EndpointKey = keyof typeof endpointPaths;
type EndpointPayloadMap = {
  summary: PrismaMobileSummaryPayload;
  salesToday: PrismaMobileSalesTodayPayload;
  cashCurrent: PrismaMobileCashCurrentPayload;
  inventoryWatchlist: PrismaMobileInventoryWatchlistPayload;
  alerts: PrismaMobileAlertsPayload;
  reportsDaily: PrismaMobileReportsDailyPayload;
  branches: PrismaMobileBranchesPayload;
  health: PrismaMobileHealthPayload;
};

type ApiEnvelope<TData> = { ok: true; data: TData; meta?: unknown };

async function fetchJson(path: string): Promise<unknown> {
  const response = await fetch(path, { cache: "no-store", headers: { Accept: "application/json" } });
  if (!response.ok) throw new Error(`${path} respondió HTTP ${response.status}`);
  return response.json();
}

async function loadEndpoint<TKey extends EndpointKey>(key: TKey): Promise<EndpointPayloadMap[TKey]> {
  const envelope = (await fetchJson(endpointPaths[key])) as ApiEnvelope<unknown>;
  if (!envelope || envelope.ok !== true) throw new Error(`${endpointPaths[key]} devolvió contrato inválido.`);
  return payloadSchemas[key].parse(envelope.data) as EndpointPayloadMap[TKey];
}

async function loadSnapshotEndpoint(): Promise<PrismaMobileClientSnapshot> {
  const envelope = PrismaMobileSnapshotEnvelopeSchema.parse(await fetchJson(PRISMA_MOBILE_SNAPSHOT_ENDPOINT));
  const clientSnapshot = createClientSnapshot(envelope.data, envelope.meta.source, []);
  writeCachedPrismaMobileSnapshot(clientSnapshot.snapshot);
  return clientSnapshot;
}

async function loadParallelEndpoints(): Promise<PrismaMobileClientSnapshot> {
  const settled = await Promise.allSettled([
    loadEndpoint("summary"),
    loadEndpoint("salesToday"),
    loadEndpoint("cashCurrent"),
    loadEndpoint("inventoryWatchlist"),
    loadEndpoint("alerts"),
    loadEndpoint("reportsDaily"),
    loadEndpoint("branches"),
    loadEndpoint("health")
  ] as const);
  const errors = settled.flatMap((result, index) => result.status === "rejected" ? [`${Object.keys(endpointPaths)[index]}: ${prismaMobileErrorMessage(result.reason, "endpoint rechazado")}`] : []);
  if (settled.some((result) => result.status === "rejected")) throw new Error(errors.join(" | "));
  const values = settled.map((result) => result.status === "fulfilled" ? result.value : null) as [PrismaMobileSummaryPayload, PrismaMobileSalesTodayPayload, PrismaMobileCashCurrentPayload, PrismaMobileInventoryWatchlistPayload, PrismaMobileAlertsPayload, PrismaMobileReportsDailyPayload, PrismaMobileBranchesPayload, PrismaMobileHealthPayload];
  const snapshot: PrismaMobileSnapshotPayload = { summary: values[0], salesToday: values[1], cashCurrent: values[2], inventoryWatchlist: values[3], alerts: values[4], reportsDaily: values[5], branches: values[6], health: values[7] } satisfies PrismaMobileSnapshotParts;
  const clientSnapshot = createClientSnapshot(snapshot, "api-endpoints", []);
  writeCachedPrismaMobileSnapshot(clientSnapshot.snapshot);
  return clientSnapshot;
}

export async function loadPrismaMobileSnapshot(): Promise<PrismaMobileClientSnapshot> {
  const errors: string[] = [];
  try { return await loadSnapshotEndpoint(); } catch (error) { errors.push(prismaMobileErrorMessage(error, "fuente móvil no disponible")); }
  try { return await loadParallelEndpoints(); } catch (error) { errors.push(prismaMobileErrorMessage(error, "fuente móvil no disponible")); }
  const cached = readCachedPrismaMobileSnapshot();
  if (cached) return { ...cached, stale: true, errors };
  throw new Error(`No se pudo cargar PRISMA App con fuentes conectadas: ${errors.join(" | ")}`);
}

export function sourceLabel(source: PrismaMobileClientSnapshot["source"]): string {
  const labels: Record<PrismaMobileClientSnapshot["source"], string> = {
    "api-snapshot": "API móvil conectada",
    "api-endpoints": "APIs móviles conectadas",
    "connected-data-plane": "Data-plane Tablet/PC",
    "tablet-pos": "Tablet POS",
    "pc-backoffice": "PC Backoffice",
    "local-cache": "Caché local",
    "unavailable": "Sin fuente conectada"
  };
  return labels[source] ?? source;
}
