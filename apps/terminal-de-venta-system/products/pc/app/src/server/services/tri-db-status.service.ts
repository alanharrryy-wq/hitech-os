import { promises as fs } from "node:fs";
import path from "node:path";
import type { TriDbStatusCardModel, TriDbStatusTableParity } from "../../modules/sync/tri-db-status.types";

const NUMBER_FORMAT = new Intl.NumberFormat("es-MX");
const DATE_FORMAT = new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" });

function asNumber(value: unknown): number {
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
}

function labelDate(value: unknown): string {
  if (typeof value !== "string" || !value.trim()) return "No disponible";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "No disponible";
  return DATE_FORMAT.format(date);
}

function fallbackStatus(sourcePath: string, mode: "missing" | "invalid", warning: string): TriDbStatusCardModel {
  return {
    status: mode === "missing" ? "UNKNOWN" : "BLOCKED",
    latestBridgeStatus: "NO_DISPONIBLE",
    generatedAtLabel: "No disponible",
    lastSyncLabel: "No disponible",
    bridgeTablesProjected: 0,
    bridgeRowsInsertedOrUpdated: 0,
    bridgeOutboxAcknowledged: 0,
    tablet: { productCount: 0, saleCount: 0, outboxCount: 0, barcodeCount: 0, lowStockCount: 0, salesTotalCents: 0 },
    pc: { productCount: 0, saleCount: 0, outboxCount: 0, barcodeCount: 0, lowStockCount: 0, salesTotalCents: 0 },
    parityOk: false,
    parityTables: [],
    warnings: [warning],
    sourcePath,
    evidencePath: null,
    mode
  };
}

function tableCount(data: any, surface: "tablet" | "pc", table: string): number {
  return asNumber(data?.[surface]?.table_counts?.[table]);
}

function surfaceStatus(data: any, surface: "tablet" | "pc") {
  return {
    productCount: tableCount(data, surface, "Product"),
    saleCount: tableCount(data, surface, "Sale"),
    outboxCount: tableCount(data, surface, "OutboxEvent"),
    barcodeCount: tableCount(data, surface, "Barcode"),
    lowStockCount: asNumber(data?.[surface]?.low_stock_count),
    salesTotalCents: asNumber(data?.[surface]?.sales_total_cents)
  };
}

function parityRows(data: any): TriDbStatusTableParity[] {
  const tables = data?.parity?.tables;
  if (!tables || typeof tables !== "object") return [];
  return Object.entries(tables).map(([table, row]: [string, any]) => ({
    table,
    tabletRows: asNumber(row?.tablet_rows),
    pcRows: asNumber(row?.pc_rows),
    pcCoversTablet: Boolean(row?.pc_covers_tablet),
    deltaPcMinusTablet: asNumber(row?.delta_pc_minus_tablet)
  }));
}

function candidateStatusPaths(): string[] {
  const cwd = process.cwd();
  const envPath = process.env.PRISMA_TRI_DB_STATUS_JSON;
  const candidates = [
    envPath,
    path.resolve(cwd, "../../../shared/tri-db/status.latest.json"),
    path.resolve(cwd, "shared/tri-db/status.latest.json"),
    path.resolve(cwd, "../../../../apps/terminal-de-venta-system/shared/tri-db/status.latest.json")
  ].filter((item): item is string => Boolean(item && item.trim()));
  return Array.from(new Set(candidates));
}

async function readFirstExistingStatus() {
  const candidates = candidateStatusPaths();
  for (const candidate of candidates) {
    try {
      const raw = await fs.readFile(candidate, "utf-8");
      return { raw, sourcePath: candidate };
    } catch (error: any) {
      if (error?.code !== "ENOENT") {
        throw new Error(`No pude leer status.latest.json en ${candidate}: ${error?.message ?? String(error)}`);
      }
    }
  }
  return { raw: null, sourcePath: candidates[0] ?? "shared/tri-db/status.latest.json" };
}

export function formatTriDbCurrency(cents: number) {
  return `$${NUMBER_FORMAT.format(Math.round(cents / 100))}`;
}

export async function getTriDbStatusCard(): Promise<TriDbStatusCardModel> {
  const loaded = await readFirstExistingStatus();
  if (!loaded.raw) {
    return fallbackStatus(loaded.sourcePath, "missing", "No encontre shared/tri-db/status.latest.json. Ejecuta primero el status v06.");
  }

  try {
    const data = JSON.parse(loaded.raw);
    const status = typeof data?.status === "string" ? data.status : "UNKNOWN";
    const warnings = Array.isArray(data?.warnings) ? data.warnings.map((item: unknown) => String(item)) : [];
    return {
      status: ["READY", "READY_WITH_CAVEATS", "BLOCKED"].includes(status) ? status : "UNKNOWN",
      latestBridgeStatus: typeof data?.latest_bridge_status === "string" ? data.latest_bridge_status : "NO_ENCONTRADO",
      generatedAtLabel: labelDate(data?.generated_at),
      lastSyncLabel: labelDate(data?.last_sync_generated_at),
      bridgeTablesProjected: asNumber(data?.bridge_tables_projected),
      bridgeRowsInsertedOrUpdated: asNumber(data?.bridge_rows_inserted_or_updated),
      bridgeOutboxAcknowledged: asNumber(data?.bridge_outbox_acknowledged),
      tablet: surfaceStatus(data, "tablet"),
      pc: surfaceStatus(data, "pc"),
      parityOk: Boolean(data?.parity?.pc_covers_tablet),
      parityTables: parityRows(data),
      warnings,
      sourcePath: loaded.sourcePath,
      evidencePath: typeof data?.evidence?.latest_status_json === "string" ? data.evidence.latest_status_json : null,
      mode: "real"
    };
  } catch (error: any) {
    return fallbackStatus(loaded.sourcePath, "invalid", `status.latest.json existe pero no se pudo interpretar: ${error?.message ?? String(error)}`);
  }
}
