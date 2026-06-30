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

const DROPDOWN_FALLBACKS: Record<string, string[]> = {
  dataMode: ["DEMO", "CLIENT", "BOOTSTRAP", "LOCKED"],
  demoProfile: ["Abarrotes", "Ferretería", "Farmacia", "Restaurante pequeño", "General"],
  demoSize: ["Mini", "Normal", "Grande"],
  purgePolicy: ["Borrar demo", "Ocultar demo", "Archivar demo"],
  clientOrigin: ["Manual", "CSV", "Tablet sync", "API", "Migración"],
  validationLevel: ["Rápida", "Completa", "Auditoría"],

  periods: ["Hoy", "Ayer", "Turno actual", "7 días", "30 días", "Personalizado"],
  severity: ["Crítico", "Revisar", "Informativo"],
  operationalStatus: ["Activo", "Pausado", "Bloqueado", "Pendiente", "Resuelto"],
  stockStatus: ["Activo", "Inactivo", "Sin stock", "Crítico", "Sin barcode", "Precio raro"],
  units: ["Pieza", "Caja", "Paquete", "Kilo", "Litro", "Metro", "Servicio"],
  taxRates: ["IVA 0%", "IVA 8%", "IVA 16%", "Exento"],
  paymentMethods: ["Efectivo", "Tarjeta", "Transferencia", "Mixto"],
  adjustmentReasons: ["Conteo", "Merma", "Daño", "Robo", "Devolución", "Corrección"],
  purchaseTypes: ["Reabasto", "Emergencia", "Compra manual", "Reposición"],
  purchaseStatus: ["Borrador", "Aprobada", "Enviada", "Parcial", "Recibida", "Cancelada"],
  paymentTerms: ["Contado", "Crédito 7 días", "Crédito 15 días", "Crédito 30 días", "Anticipo", "Contra entrega"],
  differenceReasons: ["Faltante", "Sobrante", "Dañado", "Precio distinto", "Producto incorrecto"],
  receivingActions: ["Confirmar completa", "Confirmar parcial", "Rechazar línea", "Dejar pendiente"],
  supplierTypes: ["Mercancía", "Servicios", "Mixto", "Transporte"],
  supplierStatus: ["Activo", "Pausado", "Bloqueado", "Prospecto"],
  supplierCategories: ["Bebidas", "Alimentos", "Limpieza", "Farmacia", "General"],
  riskLevels: ["Bajo", "Medio", "Alto"],
  syncTypes: ["Catálogo", "Ventas", "Caja", "Inventario", "Configuración"],
  syncStatus: ["Pendiente", "Enviado", "Recibido", "Conflicto", "Fallido", "Resuelto", "Revisado"],
  syncActions: ["Reintentar", "Marcar revisado", "Exportar evidencia", "Generar delta"],
  reportTypes: ["Ventas", "Caja", "Inventario", "Compras", "Proveedores", "Sync"],
  exportFormats: ["PDF", "CSV", "Excel", "JSON"],
  metricTypes: ["Ventas", "Margen", "Inventario", "Compras", "Caja", "Sync"],
  comparisonModes: ["Hoy vs ayer", "Semana vs semana", "Sucursal vs sucursal"],
  groupingModes: ["Producto", "Categoría", "Proveedor", "Cajero", "Terminal"],
  systemAreas: ["Ventas", "Inventario", "Sync", "Caja", "Proveedores", "Sistema"],
  roles: ["Dueño", "Gerente", "Cajero", "Almacén", "Auditor", "Soporte"],
  permissions: ["Ver", "Crear", "Editar", "Aprobar", "Exportar", "Configurar"],
  currency: ["MXN"],
  timezones: ["America/Mexico_City"]
};

type DropdownSource = "database" | "contract-fallback" | "computed";

type DropdownOption = {
  label: string;
  value: string;
  disabled?: boolean;
  reason?: string;
  search?: string;
  meta?: Record<string, string | number | boolean | null>;
};

type DropdownQuickCreate = {
  label: string;
  href: string;
  permission: string;
};

type DropdownCatalog = {
  key: string;
  label: string;
  source: DropdownSource;
  options: DropdownOption[];
  usage: string[];
  quickCreate?: DropdownQuickCreate;
  dependency?: {
    parentKey: string;
    description: string;
  };
};

type DropdownSpec = {
  key: string;
  label: string;
  tableCandidates: string[];
  valueColumns: string[];
  labelColumns: string[];
  statusColumns?: string[];
  extraColumns?: string[];
  usage: string[];
  quickCreate?: DropdownQuickCreate;
  dependency?: DropdownCatalog["dependency"];
};

const GLOBAL_DROPDOWN_SPECS: DropdownSpec[] = [
  {
    key: "branches",
    label: "Sucursales",
    tableCandidates: ["Store", "store", "Branch", "branches"],
    valueColumns: ["id", "code", "slug", "name"],
    labelColumns: ["name", "code", "slug"],
    statusColumns: ["status", "isActive", "active"],
    extraColumns: ["businessId"],
    usage: ["ventas", "inventario", "compras", "reportes", "equipos"],
    quickCreate: { label: "Alta sucursal", href: "/settings?quick=sucursal", permission: "configurar:sucursales" }
  },
  {
    key: "devices",
    label: "Tablets / terminales",
    tableCandidates: ["Terminal", "terminal", "Device", "devices", "Tablet", "tablet"],
    valueColumns: ["id", "deviceId", "code", "name"],
    labelColumns: ["name", "code", "deviceId", "storeId"],
    statusColumns: ["status", "syncStatus", "isActive", "active"],
    extraColumns: ["storeId", "lastSeenAt", "lastSyncAt"],
    usage: ["ventas", "caja", "sync", "equipos"],
    quickCreate: { label: "Vincular tablet", href: "/devices?quick=vincular-tablet", permission: "editar:equipos" },
    dependency: { parentKey: "branches", description: "La sucursal filtra tablets y cajas." }
  },
  {
    key: "users",
    label: "Usuarios / responsables",
    tableCandidates: ["User", "user", "Operator", "operator", "Employee", "employee"],
    valueColumns: ["id", "email", "username", "name"],
    labelColumns: ["name", "email", "username", "role"],
    statusColumns: ["status", "isActive", "active"],
    extraColumns: ["role"],
    usage: ["caja", "auditoría", "configuración"],
    quickCreate: { label: "Alta usuario", href: "/settings?quick=usuario", permission: "configurar:usuarios" }
  },
  {
    key: "suppliers",
    label: "Proveedores",
    tableCandidates: ["Supplier", "supplier", "Provider", "provider", "Proveedor", "proveedor"],
    valueColumns: ["id", "code", "rfc", "name"],
    labelColumns: ["name", "code", "rfc"],
    statusColumns: ["status", "isActive", "active"],
    extraColumns: ["paymentTerms", "riskLevel", "category"],
    usage: ["inventario", "compras", "reabasto", "pagos"],
    quickCreate: { label: "Alta proveedor", href: "/proveedores?quick=proveedor", permission: "crear:proveedores" }
  },
  {
    key: "products",
    label: "Productos",
    tableCandidates: ["Product", "product", "CatalogProduct", "catalogProduct", "InventoryItem", "inventoryItem"],
    valueColumns: ["id", "sku", "barcode", "code", "name"],
    labelColumns: ["name", "sku", "barcode", "code"],
    statusColumns: ["status", "isActive", "active"],
    extraColumns: ["categoryId", "supplierId", "unit", "price", "cost"],
    usage: ["inventario", "compras", "proveedores", "reportes"],
    quickCreate: { label: "Alta producto", href: "/catalog?quick=producto", permission: "crear:productos" },
    dependency: { parentKey: "suppliers", description: "El proveedor puede filtrar productos asociados." }
  },
  {
    key: "categories",
    label: "Categorías",
    tableCandidates: ["Category", "category", "ProductCategory", "productCategory"],
    valueColumns: ["id", "slug", "code", "name"],
    labelColumns: ["name", "slug", "code"],
    statusColumns: ["status", "isActive", "active"],
    usage: ["catálogo", "inventario", "reportes", "compras"],
    quickCreate: { label: "Alta categoría", href: "/catalog?quick=categoria", permission: "crear:categorias" }
  }
];

const FALLBACK_LABELS: Record<string, string> = {
  periods: "Periodo",
  severity: "Severidad",
  operationalStatus: "Estado operativo",
  stockStatus: "Estado de inventario",
  units: "Unidades",
  taxRates: "Impuestos",
  paymentMethods: "Métodos de pago",
  adjustmentReasons: "Motivos de ajuste",
  purchaseTypes: "Tipo de compra",
  purchaseStatus: "Estado de orden",
  paymentTerms: "Condición de pago",
  differenceReasons: "Motivo de diferencia",
  receivingActions: "Acción de recepción",
  supplierTypes: "Tipo de proveedor",
  supplierStatus: "Estado proveedor",
  supplierCategories: "Categoría proveedor",
  riskLevels: "Riesgo",
  syncTypes: "Tipo de sync",
  syncStatus: "Estado sync",
  syncActions: "Acción sync",
  reportTypes: "Tipo de reporte",
  exportFormats: "Formato",
  metricTypes: "Métrica",
  comparisonModes: "Comparación",
  groupingModes: "Agrupación",
  systemAreas: "Área",
  roles: "Roles",
  permissions: "Permisos",
  currency: "Moneda",
  timezones: "Zona horaria"
};

const DROPDOWN_BEHAVIOR = [
  "Búsqueda interna por superficie.",
  "Catálogos DB-backed cuando existe tabla canónica.",
  "Fallback honesto cuando la DB aún no tiene el catálogo.",
  "Dropdowns dependientes: proveedor→productos y sucursal→tablets.",
  "Quick-create sólo como ruta segura con permisos declarados.",
  "Opciones bloqueadas deben explicar el motivo.",
  "Sin pantallas nuevas: se integra como dock dentro de superficies existentes."
];

function uniqueStrings(values: string[]) {
  return [...new Set(values.filter(Boolean))];
}

function quoteIdentifier(value: string) {
  return `"${value.replace(/"/g, "\"\"")}"`;
}

function normalizeOptionText(value: unknown) {
  if (value === null || value === undefined) return "";
  if (typeof value === "boolean") return value ? "Activo" : "Inactivo";
  return String(value).trim();
}

function isInactiveLike(value: unknown) {
  const text = normalizeOptionText(value).toLowerCase();
  return ["false", "0", "inactive", "inactivo", "paused", "pausado", "blocked", "bloqueado"].includes(text);
}

async function resolveExistingTable(candidates: string[]) {
  for (const candidate of uniqueStrings([...candidates, ...candidates.map((item) => item.toLowerCase())])) {
    if (await tableExists(candidate)) return candidate;
  }
  return null;
}

async function getTableColumns(table: string) {
  try {
    const rows = await db.$queryRawUnsafe<Array<{ name: string }>>(`PRAGMA table_info(${quoteIdentifier(table)})`);
    return rows.map((row) => row.name).filter(Boolean);
  } catch {
    return [];
  }
}

function pickFirst(row: Record<string, unknown>, columns: string[]) {
  for (const column of columns) {
    const value = normalizeOptionText(row[column]);
    if (value) return value;
  }
  return "";
}

function buildOptionFromRow(spec: DropdownSpec, row: Record<string, unknown>, index: number): DropdownOption {
  const value = pickFirst(row, spec.valueColumns) || `${spec.key}-${index + 1}`;
  const labelParts = spec.labelColumns.map((column) => normalizeOptionText(row[column])).filter(Boolean);
  const label = uniqueStrings(labelParts).join(" · ") || value;
  const statusColumn = spec.statusColumns?.find((column) => Object.prototype.hasOwnProperty.call(row, column));
  const disabled = statusColumn ? isInactiveLike(row[statusColumn]) : false;
  const metaColumns = uniqueStrings([...(spec.extraColumns ?? []), ...(spec.statusColumns ?? [])]);
  const meta = Object.fromEntries(
    metaColumns
      .filter((column) => Object.prototype.hasOwnProperty.call(row, column))
      .map((column) => [column, normalizeOptionText(row[column]) || null])
  );

  return {
    label,
    value,
    disabled,
    reason: disabled ? "Opción inactiva o bloqueada por estado operativo." : undefined,
    search: uniqueStrings([...labelParts, value]).join(" ").toLowerCase(),
    meta
  };
}

async function readDatabaseCatalog(spec: DropdownSpec): Promise<DropdownCatalog | null> {
  const table = await resolveExistingTable(spec.tableCandidates);
  if (!table) return null;

  const columns = await getTableColumns(table);
  if (!columns.length) return null;

  const wantedColumns = uniqueStrings([
    ...spec.valueColumns,
    ...spec.labelColumns,
    ...(spec.statusColumns ?? []),
    ...(spec.extraColumns ?? [])
  ]).filter((column) => columns.includes(column));

  if (!wantedColumns.length) return null;

  try {
    const orderColumn = spec.labelColumns.find((column) => wantedColumns.includes(column)) ?? wantedColumns[0];
    const selectSql = wantedColumns.map(quoteIdentifier).join(", ");
    const rows = await db.$queryRawUnsafe<Array<Record<string, unknown>>>(
      `SELECT ${selectSql} FROM ${quoteIdentifier(table)} ORDER BY ${quoteIdentifier(orderColumn)} COLLATE NOCASE LIMIT 120`
    );

    return {
      key: spec.key,
      label: spec.label,
      source: "database",
      options: rows.map((row, index) => buildOptionFromRow(spec, row, index)),
      usage: spec.usage,
      quickCreate: spec.quickCreate,
      dependency: spec.dependency
    };
  } catch {
    return null;
  }
}

function fallbackCatalog(key: string, values: string[]): DropdownCatalog {
  return {
    key,
    label: FALLBACK_LABELS[key] ?? key,
    source: "contract-fallback",
    options: values.map((label) => ({ label, value: label })),
    usage: ["fallback contractual"]
  };
}


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
  const databaseCatalogs = (await Promise.all(GLOBAL_DROPDOWN_SPECS.map(readDatabaseCatalog)))
    .filter((catalog): catalog is DropdownCatalog => Boolean(catalog));

  const databaseKeys = new Set(databaseCatalogs.map((catalog) => catalog.key));
  const databaseSpecs = new Set(GLOBAL_DROPDOWN_SPECS.map((spec) => spec.key));
  const fallbackCatalogs = Object.entries(DROPDOWN_FALLBACKS)
    .filter(([key]) => !databaseKeys.has(key) && !databaseSpecs.has(key))
    .map(([key, values]) => fallbackCatalog(key, values));

  const missingDatabaseCatalogs = GLOBAL_DROPDOWN_SPECS
    .filter((spec) => !databaseKeys.has(spec.key))
    .map((spec) => ({
      key: spec.key,
      label: spec.label,
      source: "contract-fallback" as const,
      options: [{ label: `Sin datos DB: ${spec.label}`, value: "__empty__", disabled: true, reason: "La tabla canónica no existe o aún no tiene columnas compatibles." }],
      usage: spec.usage,
      quickCreate: spec.quickCreate,
      dependency: spec.dependency
    }));

  const dropdowns = [...databaseCatalogs, ...missingDatabaseCatalogs, ...fallbackCatalogs];

  return {
    checkedAt: new Date().toISOString(),
    version: "pcfunc-dd1-global-dropdowns",
    dropdowns,
    catalogsByKey: Object.fromEntries(dropdowns.map((catalog) => [catalog.key, catalog])),
    routeHints: {
      hoy: ["branches", "periods", "users", "severity", "operationalStatus"],
      ventasCaja: ["branches", "devices", "users", "periods", "paymentMethods", "operationalStatus"],
      inventario: ["products", "categories", "suppliers", "stockStatus", "units", "taxRates", "adjustmentReasons"],
      compras: ["suppliers", "products", "purchaseTypes", "purchaseStatus", "paymentTerms", "receivingActions", "differenceReasons"],
      proveedores: ["suppliers", "supplierTypes", "supplierStatus", "supplierCategories", "paymentTerms", "riskLevels", "products"],
      sincronizacion: ["devices", "syncTypes", "syncStatus", "severity", "syncActions"],
      reportes: ["reportTypes", "periods", "branches", "exportFormats"],
      analisis: ["metricTypes", "comparisonModes", "groupingModes", "branches", "periods"],
      sistema: ["systemAreas", "severity", "operationalStatus", "devices"],
      configuracion: ["roles", "permissions", "branches", "currency", "timezones"]
    },
    behavior: DROPDOWN_BEHAVIOR,
    dbBackedCount: databaseCatalogs.length,
    fallbackCount: fallbackCatalogs.length + missingDatabaseCatalogs.length,
    note: "Global dropdown contract for PRISMA PC. Existing surfaces can consume this without creating new screens."
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
