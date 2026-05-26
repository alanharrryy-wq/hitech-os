import { prisma } from "@/server/prisma/client";

type PrismaAny = typeof prisma & {
  $queryRawUnsafe<T = unknown>(query: string, ...values: unknown[]): Promise<T>;
};

const db = prisma as PrismaAny;

const OPERATIONAL_MODELS = [
  "business",
  "store",
  "terminal",
  "taxRate",
  "product",
  "barcode",
  "stockSnapshot",
  "cashSession",
  "sale",
  "saleLine",
  "outboxEvent"
];

const DROPDOWN_FALLBACKS = {
  dataMode: ["DEMO", "CLIENT", "BOOTSTRAP", "LOCKED"],
  demoProfile: ["Abarrotes", "Ferretería", "Farmacia", "Restaurante pequeño", "General"],
  demoSize: ["Mini", "Normal", "Grande"],
  purgePolicy: ["Borrar demo", "Ocultar demo", "Archivar demo"],
  clientOrigin: ["Manual", "CSV", "Tablet sync", "API", "Migración"],
  validationLevel: ["Rápida", "Completa", "Auditoría"]
};

async function safeCount(modelName: string) {
  const delegate = (db as any)[modelName];
  if (!delegate?.count) return null;
  try {
    return await delegate.count();
  } catch {
    return null;
  }
}

async function tableExists(name: string) {
  try {
    const rows = await db.$queryRawUnsafe<Array<{ name: string }>>(
      "SELECT name FROM sqlite_master WHERE type='table' AND name = ? LIMIT 1",
      name
    );
    return rows.length > 0;
  } catch {
    return false;
  }
}

async function rawCount(table: string, where = "") {
  try {
    const quoted = table.replace(/"/g, "\"\"");
    const rows = await db.$queryRawUnsafe<Array<{ count: number }>>(`SELECT COUNT(*) as count FROM "${quoted}" ${where}`);
    return Number(rows[0]?.count ?? 0);
  } catch {
    return null;
  }
}

export async function getPcDbHealthContract() {
  const counts = Object.fromEntries(await Promise.all(OPERATIONAL_MODELS.map(async (model) => [model, await safeCount(model)])));
  const integrity = await db.$queryRawUnsafe<Array<{ integrity_check: string }>>("PRAGMA integrity_check").catch(() => []);
  const tableNames = await db.$queryRawUnsafe<Array<{ name: string }>>("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").catch(() => []);
  return {
    checkedAt: new Date().toISOString(),
    integrity: integrity[0]?.integrity_check ?? "unknown",
    tableCount: tableNames.length,
    tables: tableNames.map((row) => row.name),
    counts,
    emptyOperationalCore: Object.values(counts).every((value) => value === 0 || value === null)
  };
}

export async function getPcDataModeStatusContract() {
  const dbHealth = await getPcDbHealthContract();
  const demoRegistryExists = await tableExists("DemoSeedRegistry");
  const demoRegistryRows = demoRegistryExists ? await rawCount("DemoSeedRegistry", "WHERE purgedAt IS NULL") : null;
  const operationalRows = Object.values(dbHealth.counts).reduce(
    (total: number, value) => total + (typeof value === "number" ? value : 0),
    0
  );
  const dataMode = operationalRows === 0
    ? "EMPTY"
    : demoRegistryRows && demoRegistryRows > 0
      ? "DEMO_OR_MIXED_RISK"
      : "CLIENT_OR_BOOTSTRAP_UNMARKED";

  return {
    checkedAt: new Date().toISOString(),
    dataMode,
    operationalRows,
    demoRegistry: {
      exists: demoRegistryExists,
      activeRows: demoRegistryRows,
      note: demoRegistryExists
        ? "DemoSeedRegistry is present; destructive demo operations must use this registry."
        : "DemoSeedRegistry is not present; destructive demo operations are intentionally blocked."
    },
    dbHealth,
    guardrails: {
      destructiveDemoActionsEnabled: false,
      reason: "Safe contract endpoint only. Seed/purge/reset require explicit schema-backed implementation and rollback plan."
    }
  };
}

export async function getPcDropdownContract() {
  const dropdowns = Object.entries(DROPDOWN_FALLBACKS).map(([key, values]) => ({
    key,
    source: "contract-fallback",
    options: values.map((label) => ({ label, value: label }))
  }));

  return {
    checkedAt: new Date().toISOString(),
    dropdowns,
    note: "Fallback dropdown contract. DB-backed DropdownCatalog/DropdownOption wiring can replace this without changing route shape."
  };
}

export async function getPcClientReadinessContract() {
  const status = await getPcDataModeStatusContract();
  const blockers: string[] = [];
  const warnings: string[] = [];

  if (!status.demoRegistry.exists) warnings.push("DemoSeedRegistry missing; demo/client separation is not fully enforceable yet.");
  if (status.dataMode === "DEMO_OR_MIXED_RISK") blockers.push("Demo rows may still be visible; client activation remains blocked.");
  if (status.dbHealth.emptyOperationalCore) warnings.push("PC canonical operational core is empty; client mode can be configured but not proven with live data.");

  return {
    checkedAt: new Date().toISOString(),
    ready: blockers.length === 0,
    blockers,
    warnings,
    dataMode: status.dataMode,
    evidence: status
  };
}

export function guardedMutationResponse(action: string) {
  return {
    action,
    okToMutate: false,
    code: "PC_DATA_MODE_MUTATION_NOT_WIRED",
    message: "Endpoint exists, but mutation is intentionally blocked until schema-backed demo registry, rollback, and verifiers are installed.",
    nextRequiredImplementation: [
      "Create or confirm DemoSeedRegistry",
      "Write seed/purge/reset as idempotent DB transactions",
      "Back up canonical.db before every mutation",
      "Add verifiers that fail on demo/client mixing",
      "Record audit/outbox evidence"
    ]
  };
}

export function getSyncContract(action: "export-pc-to-tablet" | "project-tablet-to-pc") {
  return {
    action,
    wired: false,
    mutationPerformed: false,
    checkedAt: new Date().toISOString(),
    message: "Route contract exists. Actual projector/exporter must be implemented against the active sync services and verified end-to-end before enabling mutation.",
    safety: "No data was modified by this endpoint."
  };
}
