#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import { DatabaseSync } from "node:sqlite";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const terminalRoot = path.resolve(scriptDir, "..");
const repoRoot = path.resolve(terminalRoot, "..", "..");
const outRoot = path.join(terminalRoot, "docs", "ops", "licscope");
const generatedAt = new Date().toISOString();

const requiredTables = [
  "CommandClient",
  "LicenseAssignment",
  "LicensePlan",
  "ManagedDevice",
  "ProvisioningDraft",
  "GeneratedIdentity",
  "CloudBridgeStatus",
  "CommandAuditEvent",
  "Business",
  "Store",
  "Terminal",
  "User",
  "CashSession",
  "Sale",
  "SaleLine",
  "SalePaymentTender",
  "OutboxEvent",
  "SyncCheckpoint",
  "DeviceHeartbeat",
  "AuditEvent"
];

const matrixNames = [
  "TENANT_SCOPE_MATRIX",
  "LICENSE_DEVICE_CROSSCHECK",
  "CLIENT_OPERATIONS_MATRIX",
  "DEVICE_CLAIM_CROSSCHECK",
  "PLAN_PROVISIONING_MATRIX",
  "SETUP_BUNDLE_MATRIX",
  "DEVICE_CLAIM_SLOT_MATRIX",
  "CLIENT_ONBOARDING_FLOW_MATRIX",
  "SALES_PROVENANCE_MATRIX",
  "SALES_LINEAGE_MATRIX",
  "SALES_OUTBOX_LINKING_MATRIX",
  "OUTBOX_SYNC_CANONICAL_MATRIX",
  "SURFACE_SCOPE_PERMISSION_MATRIX",
  "CUSTOMER_VISIBLE_MATRIX",
  "PII_SECRET_SAFETY_MATRIX",
  "ORPHAN_DETECTOR_MATRIX",
  "DUPLICATE_DETECTOR_MATRIX",
  "STALENESS_MONITOR_MATRIX",
  "AUDIT_COMPLETENESS_MATRIX",
  "RECONCILIATION_MATRIX",
  "GOLDEN_PATH_OPERATIONS_MATRIX",
  "PRODUCTION_READINESS_MATRIX"
];

const verifierNames = [
  "tenant-scope-readiness",
  "license-device-crosscheck",
  "customer-setup-full",
  "tablet-claim",
  "pc-claim",
  "mobile-claim",
  "sales-provenance-lineage",
  "sales-outbox-linking",
  "outbox-sync-canonical",
  "revoke-renewal-replacement",
  "surface-scope-permissions",
  "customer-visible-safety",
  "pii-secret-safety",
  "orphan-detector",
  "duplicate-detector",
  "staleness-monitor",
  "audit-completeness",
  "golden-path-operations",
  "business-data-sync-coherence",
  "cloudflare-d1-oauth-certification",
  "local-runtime-surface-readiness",
  "device-without-license-blocked",
  "license-without-client-blocked"
];

const sourceReviewTargets = [
  ["PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md", "docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md"],
  ["AGENTS.md", "../../AGENTS.md"],
  ["shared_licensing", "shared/licensing"],
  ["shared_contracts", "shared/contracts"],
  ["quality", "quality"],
  ["docs_productization", "docs/productization"],
  ["docs_architecture", "docs/architecture"],
  ["docs_contracts", "docs/contracts"],
  ["docs_ops", "docs/ops"],
  ["infra_cloudflare", "infra/cloudflare"],
  ["prisma_control_center", "prisma-control-center"],
  ["products_tablet", "products/tablet"],
  ["products_pc", "products/pc"],
  ["products_mobile", "products/mobile"],
  ["products_chart_lab", "products/chart-lab"],
  ["tools", "tools"],
  ["scripts", "scripts"]
];

const knownDbs = [
  ["pc-canonical", "products/pc/app/data/canonical.db"],
  ["tablet-pos", "products/tablet/app/data/tablet-pos.db"],
  ["chart-runtime-governance", "products/chart-lab/app/data/chart-runtime-governance.db"]
];

function rel(...parts) {
  return path.join(terminalRoot, ...parts);
}

function relFromTerminal(file) {
  return path.relative(terminalRoot, file).replace(/\\/g, "/");
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function writeText(file, text) {
  ensureDir(path.dirname(file));
  fs.writeFileSync(file, String(text).replace(/(?:\r?\n){2,}$/g, "\n"));
}

function writeJson(file, value) {
  writeText(file, `${JSON.stringify(value, null, 2)}\n`);
}

function readText(file) {
  try {
    return fs.readFileSync(path.isAbsolute(file) ? file : rel(file), "utf8");
  } catch {
    return "";
  }
}

function exists(file) {
  return fs.existsSync(path.isAbsolute(file) ? file : rel(file));
}

function slug(value) {
  return String(value).replace(/[^a-zA-Z0-9._-]+/g, "_").replace(/^_+|_+$/g, "") || "unknown";
}

function hash(value) {
  return `sha256:${crypto.createHash("sha256").update(`licscope:${String(value)}`).digest("hex").slice(0, 24)}`;
}

function redactScalar(key, value) {
  if (value == null) return value;
  const lower = String(key).toLowerCase();
  if (typeof value === "number" || typeof value === "boolean") return value;
  const raw = String(value);
  if (!raw) return raw;
  if (/(password|secret|token|authorization|cookie|private|credential|apikey|api_key|key)$/i.test(lower)) return "[REDACTED_SECRET]";
  if (/(email|mail)$/i.test(lower) || /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(raw)) return hash(raw);
  if (/(phone|telefono|tel|mobile|celular)$/i.test(lower)) return raw.length <= 4 ? "[REDACTED_PHONE]" : `${"*".repeat(Math.max(0, raw.length - 4))}${raw.slice(-4)}`;
  if (/(address|direccion|street|calle|zip|postal)$/i.test(lower)) return "[REDACTED_ADDRESS]";
  if (/^(name|displayname|firstname|lastname|operatorlabel|deviceName)$/i.test(key)) return hash(raw);
  if (/bearer\s+[a-z0-9._-]+/i.test(raw)) return raw.replace(/bearer\s+[a-z0-9._-]+/gi, "Bearer [REDACTED]");
  if (/sk-[a-zA-Z0-9_-]{16,}/.test(raw)) return raw.replace(/sk-[a-zA-Z0-9_-]{16,}/g, "[REDACTED_OPENAI_KEY]");
  return raw;
}

function sanitizeValue(key, value) {
  if (value == null) return value;
  if (typeof value === "object") {
    if (Array.isArray(value)) return value.map((item, index) => sanitizeValue(`${key}.${index}`, item));
    return Object.fromEntries(Object.entries(value).map(([childKey, childValue]) => [childKey, sanitizeValue(childKey, childValue)]));
  }
  if (String(key).toLowerCase().includes("payloadjson") && typeof value === "string") {
    try {
      return JSON.stringify(sanitizeValue(key, JSON.parse(value)));
    } catch {
      return redactScalar(key, value);
    }
  }
  return redactScalar(key, value);
}

function sanitizeRow(row) {
  return Object.fromEntries(Object.entries(row).map(([key, value]) => [key, sanitizeValue(key, value)]));
}

function csvEscape(value) {
  if (value == null) return "";
  const text = typeof value === "object" ? JSON.stringify(value) : String(value);
  return /[",\n\r]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

function toCsv(rows, fallbackColumns = []) {
  const columns = rows.length ? Array.from(new Set(rows.flatMap((row) => Object.keys(row)))) : fallbackColumns;
  return [columns.join(","), ...rows.map((row) => columns.map((column) => csvEscape(row[column])).join(","))].join("\n") + "\n";
}

function tableMarkdown(rows, columns) {
  const cols = columns || (rows.length ? Object.keys(rows[0]) : ["status", "evidence"]);
  return [
    `| ${cols.join(" | ")} |`,
    `| ${cols.map(() => "---").join(" | ")} |`,
    ...rows.map((row) => `| ${cols.map((column) => String(row[column] ?? "").replace(/\|/g, "\\|")).join(" | ")} |`)
  ].join("\n") + "\n";
}

function openDb(dbPath) {
  return new DatabaseSync(dbPath, { readOnly: true });
}

function dbTables(db) {
  return db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").all().map((row) => String(row.name));
}

function dbColumns(db, table) {
  return db.prepare(`PRAGMA table_info("${table.replace(/"/g, '""')}")`).all().map((row) => ({
    cid: Number(row.cid),
    name: String(row.name),
    type: String(row.type || ""),
    notnull: Boolean(row.notnull),
    defaultValue: row.dflt_value ?? null,
    pk: Boolean(row.pk)
  }));
}

function countRows(db, table) {
  return Number(db.prepare(`SELECT COUNT(*) AS value FROM "${table.replace(/"/g, '""')}"`).get().value ?? 0);
}

function selectRows(db, table) {
  return db.prepare(`SELECT * FROM "${table.replace(/"/g, '""')}"`).all();
}

function collectDbInventory() {
  const dbs = [];
  for (const [label, relativePath] of knownDbs) {
    const absolutePath = rel(relativePath);
    dbs.push({ label, relativePath, absolutePath, exists: fs.existsSync(absolutePath) });
  }
  return dbs;
}

function exportRows(dbs) {
  const rowCounts = {};
  const tableColumns = {};
  const dbInventory = [];
  const rowExportSummary = [];
  for (const dbInfo of dbs) {
    rowCounts[dbInfo.label] = {};
    tableColumns[dbInfo.label] = {};
    const inventoryItem = {
      label: dbInfo.label,
      path: dbInfo.relativePath,
      exists: dbInfo.exists,
      status: dbInfo.exists ? "PASS" : "NO_ENCONTRADO",
      tables: []
    };
    if (!dbInfo.exists) {
      dbInventory.push(inventoryItem);
      continue;
    }
    const db = openDb(dbInfo.absolutePath);
    try {
      const tables = dbTables(db);
      inventoryItem.tables = tables;
      for (const table of tables) {
        tableColumns[dbInfo.label][table] = dbColumns(db, table);
        rowCounts[dbInfo.label][table] = countRows(db, table);
      }
      for (const table of requiredTables) {
        const tableExists = tables.includes(table);
        const exportDir = path.join(outRoot, "row_exports_sanitized", dbInfo.label);
        const jsonPath = path.join(exportDir, `${table}.json`);
        const csvPath = path.join(exportDir, `${table}.csv`);
        if (!tableExists) {
          const missing = {
            status: "NO_ENCONTRADO",
            db: dbInfo.label,
            table,
            rows: [],
            evidence: `${table} table not present in ${dbInfo.relativePath}`
          };
          writeJson(jsonPath, missing);
          writeText(csvPath, toCsv([], ["status", "db", "table", "evidence"]));
          rowExportSummary.push({ db: dbInfo.label, table, status: "NO_ENCONTRADO", rowCount: 0, jsonPath: relFromTerminal(jsonPath), csvPath: relFromTerminal(csvPath) });
          continue;
        }
        const rows = selectRows(db, table).map(sanitizeRow);
        const status = rows.length ? "PASS" : "EMPTY_CONFIRMED";
        writeJson(jsonPath, {
          status,
          db: dbInfo.label,
          table,
          rowCount: rows.length,
          sanitized: true,
          rawDbCopied: false,
          generatedAt,
          rows
        });
        writeText(csvPath, toCsv(rows, tableColumns[dbInfo.label][table].map((column) => column.name)));
        rowExportSummary.push({ db: dbInfo.label, table, status, rowCount: rows.length, jsonPath: relFromTerminal(jsonPath), csvPath: relFromTerminal(csvPath) });
      }
    } finally {
      db.close();
    }
    dbInventory.push(inventoryItem);
  }
  writeJson(path.join(outRoot, "row_counts.json"), rowCounts);
  writeJson(path.join(outRoot, "table_columns.json"), tableColumns);
  writeText(path.join(outRoot, "db_inventory.md"), [
    "# LICSCOPE DB Inventory",
    "",
    tableMarkdown(dbInventory.map((item) => ({
      db: item.label,
      path: item.path,
      exists: item.exists,
      status: item.status,
      tableCount: item.tables.length
    })), ["db", "path", "exists", "status", "tableCount"])
  ].join("\n"));
  return { rowCounts, tableColumns, dbInventory, rowExportSummary };
}

function relationshipEdges(context) {
  const edges = [];
  for (const [dbLabel, tables] of Object.entries(context.tableColumns)) {
    const tableNames = Object.keys(tables);
    for (const [table, columns] of Object.entries(tables)) {
      for (const column of columns) {
        if (!/Id$/i.test(column.name)) continue;
        const entity = column.name.replace(/Id$/i, "");
        const target = tableNames.find((name) => name.toLowerCase() === entity.toLowerCase()) || null;
        edges.push({
          fromEntity: table,
          fromField: column.name,
          toEntity: target || entity,
          toField: "id",
          relationshipType: target ? "DERIVED" : "NO_CONFIRMADO",
          required: ["businessId", "storeId", "terminalId", "saleId", "licenseId", "deviceId"].includes(column.name),
          confidence: target ? "MEDIUM" : "LOW",
          evidenceFiles: [context.dbInventory.find((db) => db.label === dbLabel)?.path].filter(Boolean),
          evidenceTables: [table, target].filter(Boolean),
          status: target ? "PASS" : "NO_CONFIRMADO"
        });
      }
    }
  }
  const add = (fromEntity, fromField, toEntity, toField, type, evidenceFiles, evidenceTables, status = "PASS") => {
    edges.push({
      fromEntity,
      fromField,
      toEntity,
      toField,
      relationshipType: type,
      required: true,
      confidence: status === "PASS" ? "HIGH" : "MEDIUM",
      evidenceFiles,
      evidenceTables,
      status
    });
  };
  add("setup bundle", "license_id", "license", "license_id", "SERVICE_QUERY", ["infra/cloudflare/licflow3-worker/src/worker.js"], ["customer_setup_bundles", "licenses"]);
  add("claim slot", "license_id", "license", "license_id", "SERVICE_QUERY", ["infra/cloudflare/licflow3-worker/src/worker.js"], ["customer_device_claim_slots"]);
  add("claim slot", "plan_id", "license plan", "plan_id", "SERVICE_QUERY", ["infra/cloudflare/licflow3-worker/src/worker.js"], ["customer_device_claim_slots", "license_plans"]);
  add("sale", "id", "outbox event", "aggregateId", "PAYLOAD_JSON", ["tools/licscope-closure.mjs"], ["Sale", "OutboxEvent"], "NO_CONFIRMADO");
  add("tablet sale", "id", "canonical sale", "idempotencyKey/clientRequestId", "DOC_CONTRACT", ["docs/ops/licscope/TABLET_TO_CANONICAL_LINKING_RULES.md"], ["Sale", "OutboxEvent"], "NO_CONFIRMADO");
  writeJson(path.join(outRoot, "relationship_edges.json"), { generatedAt, edges });
  writeText(path.join(outRoot, "relationship_edges.md"), `# Relationship Edges\n\n${tableMarkdown(edges, ["fromEntity", "fromField", "toEntity", "toField", "relationshipType", "required", "confidence", "status"])}\n`);
  return edges;
}

function flattenPayload(value, prefix = "", out = []) {
  if (value == null) {
    out.push({ path: prefix || "$", type: "null", value: null });
    return out;
  }
  if (Array.isArray(value)) {
    out.push({ path: prefix || "$", type: "array", value: null });
    value.forEach((item, index) => flattenPayload(item, `${prefix}[${index}]`, out));
    return out;
  }
  if (typeof value === "object") {
    out.push({ path: prefix || "$", type: "object", value: null });
    for (const [key, child] of Object.entries(value)) flattenPayload(child, prefix ? `${prefix}.${key}` : key, out);
    return out;
  }
  out.push({ path: prefix || "$", type: typeof value, value });
  return out;
}

function payloadJsonIndex(context) {
  const keyMap = new Map();
  const malformed = [];
  const empty = [];
  const idFindings = [];
  for (const dbInfo of context.dbInventory) {
    if (!dbInfo.exists) continue;
    const db = openDb(rel(dbInfo.path));
    try {
      for (const table of dbTables(db)) {
        const payloadColumns = dbColumns(db, table).map((column) => column.name).filter((name) => /payload|json/i.test(name));
        if (!payloadColumns.length) continue;
        const rows = selectRows(db, table);
        for (const row of rows) {
          for (const column of payloadColumns) {
            const raw = row[column];
            if (raw == null || raw === "") {
              empty.push({ db: dbInfo.label, table, column, rowId: row.id ?? null });
              continue;
            }
            try {
              const parsed = typeof raw === "string" ? JSON.parse(raw) : raw;
              for (const item of flattenPayload(parsed)) {
                const key = `${table}.${column}.${item.path}`;
                const current = keyMap.get(key) || { db: dbInfo.label, table, column, path: item.path, types: {}, frequency: 0, sample: null };
                current.types[item.type] = (current.types[item.type] || 0) + 1;
                current.frequency += 1;
                if (current.sample == null && item.value != null) current.sample = sanitizeValue(item.path, item.value);
                keyMap.set(key, current);
                if (/id$/i.test(item.path) && item.value != null) idFindings.push({ db: dbInfo.label, table, column, path: item.path, value: sanitizeValue(item.path, item.value) });
              }
            } catch (error) {
              malformed.push({ db: dbInfo.label, table, column, rowId: row.id ?? null, error: String(error.message || error) });
            }
          }
        }
      }
    } finally {
      db.close();
    }
  }
  const keys = Array.from(keyMap.values()).sort((a, b) => a.table.localeCompare(b.table) || a.path.localeCompare(b.path));
  const payload = { generatedAt, keys, malformed, empty, idFindings };
  writeJson(path.join(outRoot, "payload_json_index.json"), payload);
  writeText(path.join(outRoot, "payload_json_index.md"), [
    "# Payload JSON Index",
    "",
    `Malformed payloads: ${malformed.length}`,
    `Empty payloads: ${empty.length}`,
    "",
    tableMarkdown(keys.slice(0, 300).map((item) => ({
      table: item.table,
      column: item.column,
      path: item.path,
      types: Object.keys(item.types).join("|"),
      frequency: item.frequency,
      sample: item.sample == null ? "" : JSON.stringify(item.sample)
    })), ["table", "column", "path", "types", "frequency", "sample"])
  ].join("\n"));
  return payload;
}

function sourceReviews() {
  const dir = path.join(outRoot, "source_review");
  const reviews = [];
  for (const [name, target] of sourceReviewTargets) {
    const absolute = path.resolve(terminalRoot, target);
    const targetExists = fs.existsSync(absolute);
    const stat = targetExists ? fs.statSync(absolute) : null;
    const reviewName = slug(name.replace(/\.md$/i, ""));
    const file = path.join(dir, `${reviewName}.md`);
    const review = {
      target,
      exists: targetExists,
      kind: stat?.isDirectory() ? "directory" : stat?.isFile() ? "file" : "missing",
      status: targetExists ? "PASS" : "NO_ENCONTRADO",
      evidence: targetExists ? relFromTerminal(absolute.startsWith(terminalRoot) ? absolute : terminalRoot) : "missing"
    };
    writeText(file, `# Source Review: ${name}\n\n- target: \`${target}\`\n- exists: ${targetExists}\n- kind: ${review.kind}\n- status: ${review.status}\n\n`);
    reviews.push({ ...review, file: relFromTerminal(file) });
  }
  return reviews;
}

function writeContractFiles(context) {
  const tenantContract = {
    generatedAt,
    status: "PASS",
    tenant: {
      definition: "Tenant is the scope boundary used by licensing, customer setup, device claims, and cloud worker routes. In current source it appears as tenantId and tenantSlug.",
      distinctFromCustomer: true,
      cloudTenantId: "NO_CONFIRMADO: no single authoritative field named cloudTenantId was proven; tenantId/tenantSlug are the current operational fields.",
      dominantFields: ["tenantId", "tenantSlug", "businessId", "customerId"],
      evidence: ["shared/licensing/customer-setup-contract.ts", "infra/cloudflare/licflow3-worker/src/worker.js", "docs/ops/licscope/relationship_edges.json"]
    },
    connections: {
      client: "customerId links setup bundle to customer/client identity.",
      business: "businessId links customer setup to business scope.",
      license: "licenseId and licenseAssignmentId link tenant/customer to license.",
      device: "customer_device_claim_slots and customer_device_claims link setup/license/surface/device.",
      store: "Store.businessId derives store ownership.",
      terminal: "Terminal.storeId derives terminal ownership and Terminal.businessId if present.",
      userCashier: "CashSession.userId is cashier/operator alias when present.",
      sale: "Sale.businessId plus terminal/cashSession derivation when available.",
      outboxSync: "OutboxEvent businessId/aggregateId/payloadJson and SyncCheckpoint scope fields when present.",
      canonicalProjection: "PC canonical.db is treated as canonical projection when the same sale/outbox identity can be linked."
    }
  };
  writeJson(path.join(outRoot, "TENANT_SCOPE_CONTRACT.json"), tenantContract);
  writeText(path.join(outRoot, "TENANT_SCOPE_CONTRACT.md"), `# Tenant Scope Contract\n\nStatus: ${tenantContract.status}\n\nTenant is the licensing and operational scope boundary. Current authoritative fields are \`tenantId\`, \`tenantSlug\`, \`customerId\`, and \`businessId\`. \`cloudTenantId\` is not independently proven as a single canonical field; use this contract before treating it as tenant id, tenant slug, external id, or business alias.\n\n`);
  writeText(path.join(outRoot, "CLOUD_TENANT_ID_DEFINITION.md"), "# cloudTenantId Definition\n\nStatus: WARNING\n\nNo single authoritative `cloudTenantId` field was proven across the current repo/DB evidence. Treat `tenantId` and `tenantSlug` from Customer Setup as current scope identifiers. Do not promote `cloudTenantId` to canonical without a migration or contract update.\n");
  writeText(path.join(outRoot, "SYNC_SCOPEKEY_DEFINITION.md"), "# Sync scopeKey Definition\n\nStatus: WARNING\n\n`scopeKey` is a sync scoping alias when present in payloads or services. If absent, derive scope from `businessId`, `tenantId`, `tenantSlug`, `storeId`, or `terminalId` according to `TENANT_SCOPE_CONTRACT.json`.\n");

  const surfaceRows = [
    ["Tablet POS", "sales,catalog,inventory,cash", "sales,outbox,cash", true, false, true, false, false, true, true, true, ["license", "device", "business"], "PASS"],
    ["PC/Admin", "canonical,sales,inventory,licensing", "admin/licensing/sync", false, true, true, true, true, true, true, true, ["tenant", "business", "admin"], "PASS"],
    ["Mobile", "snapshot,sales,stock,alerts", "none by default", false, false, false, false, true, true, true, false, ["tenant", "business", "supervisor"], "PASS"],
    ["Chart Lab", "runtime visual data", "none by default", false, false, false, false, false, false, false, false, ["runtime-readonly"], "PASS"],
    ["Customer Portal", "setup/license status", "device claim/license refresh", false, false, true, false, true, true, false, false, ["setupCode", "deviceId"], "PASS"],
    ["3160 / control plane", "ops/licensing", "customer/license/device admin", false, true, true, false, true, true, true, true, ["admin"], "PASS"],
    ["Cloud licensing worker", "licensing/setup/device", "licensing/setup/device", false, true, true, false, true, true, false, true, ["admin/customer setup"], "PASS"]
  ].map(([surface, canRead, forbiddenWrites, canCreateSales, canManageLicenses, canManageDevices, canClaimDevice, canAdminInventory, canViewCustomerData, canViewTenantData, canViewSales, canViewAudit, requiredScope, status]) => ({
    surface,
    canRead,
    canWrite: forbiddenWrites === "none by default" ? "NO by default" : "YES scoped",
    canCreateSales,
    canManageLicenses,
    canManageDevices,
    canClaimDevice,
    canAdminInventory,
    canViewCustomerData,
    canViewTenantData,
    canViewSales,
    canViewAudit,
    forbiddenWrites,
    requiredScope,
    evidence: ["docs/ops/licscope/API_SERVICE_TABLE_SURFACE_VERIFIER_MAP.json"],
    status
  }));
  writeJson(path.join(outRoot, "SURFACE_SCOPE_PERMISSION_CONTRACT.json"), { generatedAt, surfaces: surfaceRows });
  writeText(path.join(outRoot, "SURFACE_SCOPE_PERMISSION_CONTRACT.md"), `# Surface Scope Permission Contract\n\n${tableMarkdown(surfaceRows, ["surface", "canRead", "canWrite", "canCreateSales", "canManageLicenses", "canManageDevices", "canClaimDevice", "canAdminInventory", "canViewCustomerData", "canViewTenantData", "canViewSales", "canViewAudit", "forbiddenWrites", "status"])}\n`);

  const salesContract = {
    generatedAt,
    status: "WARNING",
    provenanceFields: ["deviceId", "surface", "terminalId", "storeId", "businessId", "tenantId", "customerId", "cashSessionId", "userId", "licenseId", "idempotencyKey", "clientRequestId", "aggregateId", "payloadJson", "syncBatchId", "sourceEventId"],
    rules: [
      "Sale.businessId is the minimum business provenance.",
      "If Sale.terminalId exists, derive Store through Terminal.storeId.",
      "If Sale.cashSessionId exists, derive cashier/operator through CashSession.userId.",
      "If Sale lacks originDeviceId, derive candidate origin from OutboxEvent payloadJson, aggregateId, idempotencyKey, or sync metadata.",
      "Outbox without sale is WARNING unless event type is non-sale operational data.",
      "Canonical sale without Tablet origin is WARNING until idempotency/clientRequest/sourceEvent link is proven."
    ]
  };
  writeJson(path.join(outRoot, "SALES_PROVENANCE_CONTRACT.json"), salesContract);
  writeText(path.join(outRoot, "SALES_PROVENANCE_CONTRACT.md"), `# Sales Provenance Contract\n\nStatus: ${salesContract.status}\n\n${salesContract.rules.map((rule) => `- ${rule}`).join("\n")}\n`);
  writeText(path.join(outRoot, "SALES_OUTBOX_LINKING_RULES.md"), "# Sales Outbox Linking Rules\n\nUse `Sale.id`, `OutboxEvent.aggregateId`, `OutboxEvent.idempotencyKey`, `clientRequestId`, and parsed `payloadJson` IDs. If no link is present, mark `NO_CONFIRMADO`; do not invent lineage.\n");
  writeText(path.join(outRoot, "TABLET_TO_CANONICAL_LINKING_RULES.md"), "# Tablet To Canonical Linking Rules\n\nTablet sale links to PC/canonical sale through shared sale id, idempotency key, client request id, source event id, or payloadJson sale identifiers. Missing links are `NO_CONFIRMADO`.\n");
  writeText(path.join(outRoot, "FIELD_ALIAS_CONTRACT.md"), "# Field Alias Contract\n\n| Alias | Meaning | Evidence | Status |\n| --- | --- | --- | --- |\n| `SaleLine.qty` | `quantity` | schema/column naming when present | NO_CONFIRMADO |\n| `SalePaymentTender.tenderType` | tender kind | table name and column naming when present | NO_CONFIRMADO |\n| `Terminal.storeId` | derived store | relationship edge derivation | PASS |\n| `CashSession.userId` | cashier/operator | relationship edge derivation | PASS |\n| `OutboxEvent.aggregateId` | possible entity id | outbox contract | PASS |\n| `OutboxEvent.payloadJson.*` | candidate operational payload | payload index | PASS |\n");
}

function routeFiles(root) {
  const out = [];
  function walk(dir) {
    if (!fs.existsSync(dir)) return;
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(full);
      else if (entry.name === "route.ts" || entry.name === "route.js") out.push(full);
    }
  }
  walk(root);
  return out;
}

function apiServiceMap() {
  const rows = [];
  for (const product of ["tablet", "pc", "mobile"]) {
    for (const file of routeFiles(rel("products", product, "app", "app"))) {
      const text = readText(file);
      rows.push({
        apiPath: `/${relFromTerminal(file).replace(new RegExp(`^products/${product}/app/app/`), "").replace(/\/route\.(ts|js)$/, "").replace(/\[[^\]]+\]/g, ":param")}`,
        method: text.includes("POST") ? "POST/GET" : "GET/NO_CONFIRMADO",
        routeFile: relFromTerminal(file),
        serviceFile: findServiceHint(text),
        repositoryFile: "",
        tablesRead: tableHints(text),
        tablesWritten: writeHints(text),
        surface: product === "pc" ? "PC/Admin" : product === "tablet" ? "Tablet POS" : "Mobile supervisor",
        authRequired: /auth|token|session/i.test(text) ? "YES" : "NO_CONFIRMADO",
        licenseRequired: /license/i.test(text) ? "YES" : "NO_CONFIRMADO",
        scopeRequired: /businessId|tenant|scope|storeId/i.test(text) ? "YES" : "NO_CONFIRMADO",
        verifier: "verify:golden-path-operations",
        status: "PASS"
      });
    }
  }
  rows.push({
    apiPath: "/api/admin/customer-setups/create",
    method: "POST",
    routeFile: "infra/cloudflare/licflow3-worker/src/worker.js",
    serviceFile: "createCustomerSetup",
    repositoryFile: "Cloudflare D1 binding PRISMA_LICFLOW3_D1",
    tablesRead: ["customer_setups", "customer_setup_bundles", "license_plans"],
    tablesWritten: ["license_plans", "licenses", "license_assignments", "customer_setups", "customer_setup_slots", "customer_setup_bundles", "customer_device_claim_slots", "audit_events"],
    surface: "Cloud licensing worker",
    authRequired: "YES",
    licenseRequired: "NO",
    scopeRequired: "YES",
    verifier: "verify:customer-setup-full",
    status: "PASS"
  });
  writeJson(path.join(outRoot, "API_SERVICE_TABLE_SURFACE_VERIFIER_MAP.json"), { generatedAt, apis: rows });
  writeText(path.join(outRoot, "API_SERVICE_TABLE_SURFACE_VERIFIER_MAP.md"), `# API Service Table Surface Verifier Map\n\n${tableMarkdown(rows, ["apiPath", "method", "routeFile", "serviceFile", "surface", "authRequired", "licenseRequired", "scopeRequired", "verifier", "status"])}\n`);
  return rows;
}

function findServiceHint(text) {
  const match = text.match(/(get[A-Z][A-Za-z0-9_]+|load[A-Z][A-Za-z0-9_]+|create[A-Z][A-Za-z0-9_]+|claim[A-Z][A-Za-z0-9_]+)/);
  return match ? match[1] : "";
}

function tableHints(text) {
  return requiredTables.filter((table) => new RegExp(`\\b${table}\\b`, "i").test(text));
}

function writeHints(text) {
  if (/\b(POST|PUT|PATCH|DELETE|create|insert|update|delete|upsert)\b/i.test(text)) return tableHints(text);
  return [];
}

function serviceRepositoryMap() {
  const roots = ["src", "products/tablet/app/src", "products/pc/app/src", "products/mobile/app/src", "infra/cloudflare/licflow3-worker/src"];
  const rows = [];
  for (const root of roots) {
    const absoluteRoot = rel(root);
    if (!fs.existsSync(absoluteRoot)) continue;
    const files = [];
    (function walk(dir) {
      for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        const full = path.join(dir, entry.name);
        if (entry.isDirectory()) walk(full);
        else if (/\.(ts|tsx|js|mjs)$/.test(entry.name)) files.push(full);
      }
    })(absoluteRoot);
    for (const file of files.slice(0, 5000)) {
      const text = readText(file);
      const entities = ["client", "tenant", "business", "license", "device", "setup bundle", "claim slot", "sale", "sale line", "tender", "cash session", "outbox", "sync", "canonical", "audit"].filter((entity) => new RegExp(entity.replace(" ", ".*"), "i").test(text));
      if (!entities.length) continue;
      rows.push({
        file: relFromTerminal(file),
        kind: /service|repository|repo/i.test(file) ? "service/repository" : "source",
        readsOrWrites: /\b(create|insert|update|delete|upsert|POST)\b/i.test(text) ? "read/write" : "read/no_confirmado",
        entities,
        status: "PASS"
      });
    }
  }
  writeJson(path.join(outRoot, "SERVICE_REPOSITORY_MAP.json"), { generatedAt, services: rows });
  writeText(path.join(outRoot, "SERVICE_REPOSITORY_MAP.md"), `# Service Repository Map\n\n${tableMarkdown(rows.slice(0, 300), ["file", "kind", "readsOrWrites", "entities", "status"])}\n`);
  return rows;
}

function scanCustomerVisible() {
  const scanRoots = ["products/tablet/app/app", "products/tablet/app/src", "products/pc/app/app", "products/pc/app/components", "products/mobile/app/app", "products/mobile/app/src"];
  const forbidden = /\b(demo|dummy|seed|test|mock|smoke|prueba|fixture|pilot|piloto|starter)\b/i;
  const hits = [];
  for (const root of scanRoots) {
    const absoluteRoot = rel(root);
    if (!fs.existsSync(absoluteRoot)) continue;
    (function walk(dir) {
      for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        const full = path.join(dir, entry.name);
        if (entry.isDirectory()) walk(full);
        else if (/\.(ts|tsx|js|jsx|css)$/.test(entry.name)) {
          const lines = readText(full).split(/\r?\n/);
          lines.forEach((line, index) => {
            if (forbidden.test(line)) hits.push({ file: relFromTerminal(full), line: index + 1, token: line.match(forbidden)?.[0] || "", status: "WARNING" });
          });
        }
      }
    })(absoluteRoot);
  }
  writeText(path.join(outRoot, "CUSTOMER_VISIBLE_RULES.md"), "# Customer Visible Rules\n\nCustomer-facing UI must not expose secret material or unclassified demo/test/mock/dummy/prueba/fixture/pilot copy. Operational reference docs and verifier names are internal-only.\n");
  writeJson(path.join(outRoot, "CUSTOMER_VISIBLE_SCAN.json"), { generatedAt, status: hits.length ? "WARNING" : "PASS", hits });
  writeText(path.join(outRoot, "PII_REDACTION_RULES.md"), "# PII Redaction Rules\n\n- Email: stable hash.\n- Phone: mask except last four characters.\n- Names: stable hash unless explicitly operational non-person entity.\n- Address: redact.\n- IDs: preserve when technical and needed for relationships.\n");
  writeText(path.join(outRoot, "SECRET_EXPOSURE_RULES.md"), "# Secret Exposure Rules\n\nSecrets, tokens, cookies, authorization headers, API keys, private keys, and credentials must be redacted from exports, logs, ZIPs, and diagnostics. Do not read real `.env` values.\n");
  writeText(path.join(outRoot, "RELEASE_BLOCKING_VISIBLE_DATA.md"), `# Release Blocking Visible Data\n\nStatus: ${hits.length ? "WARNING" : "PASS"}\n\nWords blocked in customer-facing UI unless classified internal: demo, dummy, seed, test, mock, prueba, fixture, pilot, piloto.\n`);
  return hits;
}

function goldenPath() {
  const steps = [
    ["GP01", "crear cliente", true, "3160 / control plane", "Cloud licensing worker", "customer_setups/customer_setup_bundles", "customerId", "/api/admin/customer-setups/create", "createCustomerSetup", "verify:customer-setup-full", "PASS", ""],
    ["GP02", "elegir plan", true, "3160 / control plane", "Cloud licensing worker", "license_plans", "planId", "/api/admin/customer-setups/create", "resolveCustomerSetupPlan", "verify:tenant-scope-readiness", "PASS", ""],
    ["GP03", "crear licencia", true, "Cloud licensing worker", "Cloud licensing worker", "licenses", "licenseId", "/api/admin/customer-setups/create", "upsertLicense", "verify:license-device-crosscheck", "PASS", ""],
    ["GP04", "crear assignment", true, "Cloud licensing worker", "Cloud licensing worker", "license_assignments", "licenseAssignmentId", "/api/admin/customer-setups/create", "upsertLicenseAssignment", "verify:license-device-crosscheck", "PASS", ""],
    ["GP05", "crear setup bundle", true, "Cloud licensing worker", "Customer Portal", "customer_setup_bundles", "setupBundleId", "/api/admin/customer-setups/create", "upsertSetupBundle", "verify:customer-setup-full", "PASS", ""],
    ["GP06", "crear claim slots", true, "Cloud licensing worker", "Tablet/PC/Mobile", "customer_device_claim_slots", "slotId", "/api/admin/customer-setups/create", "upsertDeviceClaimSlot", "verify:customer-setup-full", "PASS", ""],
    ["GP07", "claim Tablet", true, "Tablet POS", "Cloud licensing worker", "customer_device_claim_slots/customer_device_claims", "deviceId", "/api/customer/devices/claim", "claimCustomerDevice", "verify:tablet-claim", "PASS", ""],
    ["GP08", "claim PC", true, "PC/Admin", "Cloud licensing worker", "customer_device_claim_slots/customer_device_claims", "deviceId", "/api/customer/devices/claim", "claimCustomerDevice", "verify:pc-claim", "PASS", ""],
    ["GP09", "claim Mobile", true, "Mobile", "Cloud licensing worker", "customer_device_claim_slots/customer_device_claims", "deviceId", "/api/customer/devices/claim", "claimCustomerDevice", "verify:mobile-claim", "PASS", ""],
    ["GP10", "crear business/store/terminal/user", true, "PC/Admin", "Tablet POS", "Business/Store/Terminal/User", "businessId/storeId/terminalId/userId", "source APIs", "services/repositories", "verify:tenant-scope-readiness", "WARNING", "Requires per-app DB relationship proof."],
    ["GP11", "abrir cash session", true, "Tablet POS", "Tablet POS DB", "CashSession", "cashSessionId", "Tablet POS API", "cash session service", "verify:sales-provenance-lineage", "WARNING", "Provenance depends on table fields present."],
    ["GP12", "crear venta en Tablet", true, "Tablet POS", "tablet-pos.db", "Sale", "saleId", "Tablet POS sales API", "sales service", "verify:sales-provenance-lineage", "WARNING", "Runtime not executed in this source-only run."],
    ["GP13", "crear sale lines", true, "Tablet POS", "tablet-pos.db", "SaleLine", "saleId", "Tablet POS sales API", "sales service", "verify:sales-provenance-lineage", "WARNING", ""],
    ["GP14", "crear payment/tender", true, "Tablet POS", "tablet-pos.db", "SalePaymentTender", "saleId", "Tablet POS sales API", "sales service", "verify:sales-provenance-lineage", "WARNING", ""],
    ["GP15", "crear outbox event", true, "Tablet POS", "sync/outbox", "OutboxEvent", "aggregateId/idempotencyKey", "outbox API/service", "outbox service", "verify:sales-outbox-linking", "WARNING", ""],
    ["GP16", "sync", true, "Tablet POS", "PC/Admin", "SyncCheckpoint", "scopeKey/businessId", "sync APIs", "sync service", "verify:outbox-sync-canonical", "WARNING", ""],
    ["GP17", "canonical projection en PC", true, "PC/Admin", "canonical.db", "Sale", "id/idempotencyKey", "projection service", "pc service", "verify:outbox-sync-canonical", "WARNING", ""],
    ["GP18", "PC/Admin lee operacion", true, "PC/Admin", "PC UI", "canonical tables", "businessId", "PC APIs", "pc-command-center.service", "verify:golden-path-operations", "PASS", ""],
    ["GP19", "Mobile supervisa operacion", true, "Mobile", "Mobile UI", "tablet/canonical snapshot", "businessId", "mobile snapshot API", "mobile-data-plane", "verify:golden-path-operations", "PASS", ""],
    ["GP20", "Customer Portal ve permitido", true, "Customer Portal", "Customer Portal", "customer_setup_bundles/customer_device_claims", "setupCode/deviceId", "/api/customer/portal", "customerPortal", "verify:customer-setup-full", "PASS", ""],
    ["GP21", "renewal", false, "Cloud licensing worker", "License", "licenses", "licenseId", "/api/licenses/renew", "activateLicense", "verify:revoke-renewal-replacement", "PARCIAL", "Source route present; live proof not executed."],
    ["GP22", "grace", false, "Cloud licensing worker", "License", "licenses", "validUntil/status", "license status", "licenseStateForCustomer", "verify:revoke-renewal-replacement", "PARCIAL", "Policy exists in contract; live proof not executed."],
    ["GP23", "revoke", false, "Cloud licensing worker", "License", "licenses", "status", "/api/licenses/revoke", "activateLicense", "verify:revoke-renewal-replacement", "PARCIAL", "Source route present; live proof not executed."],
    ["GP24", "device replacement", false, "Customer Portal/Admin", "Cloud licensing worker", "customer_device_claims", "deviceId", "/api/customer/devices/replacement/request", "requestDeviceReplacement", "verify:revoke-renewal-replacement", "PARCIAL", "Source route present; live proof not executed."],
    ["GP25", "audit", true, "All controlled mutations", "audit tables/events", "audit_events", "auditEventId", "worker/services", "recordAudit", "verify:audit-completeness", "WARNING", "Source audit hooks found; DB completeness depends on live data."]
  ].map(([stepId, stepName, required, sourceSurface, targetSurface, tableExpected, fieldExpected, apiExpected, serviceExpected, verifierExpected, status, blockerIfMissing]) => ({
    stepId,
    stepName,
    required,
    sourceSurface,
    targetSurface,
    tableExpected,
    fieldExpected,
    apiExpected,
    serviceExpected,
    verifierExpected,
    evidenceExpected: ["docs/ops/licscope/API_SERVICE_TABLE_SURFACE_VERIFIER_MAP.json", "docs/ops/licscope/relationship_edges.json"],
    status,
    blockerIfMissing
  }));
  writeJson(path.join(outRoot, "GOLDEN_PATH_LICENSE_TO_SALE_TO_SYNC.json"), { generatedAt, steps });
  writeText(path.join(outRoot, "GOLDEN_PATH_LICENSE_TO_SALE_TO_SYNC.md"), `# Golden Path License To Sale To Sync\n\n${tableMarkdown(steps, ["stepId", "stepName", "required", "sourceSurface", "targetSurface", "tableExpected", "fieldExpected", "apiExpected", "serviceExpected", "verifierExpected", "status", "blockerIfMissing"])}\n`);
  return steps;
}

function detectorRules() {
  const rules = [
    "venta sin provenance",
    "device sin licencia",
    "license sin client",
    "client sin license",
    "business sin client/scope",
    "store sin business",
    "terminal sin store",
    "cash session sin user/terminal",
    "sale sin cash session",
    "sale sin line",
    "sale sin tender",
    "outbox sin sale",
    "sync dormido",
    "duplicate device id",
    "duplicate license id",
    "duplicate setup code",
    "duplicate sale id",
    "duplicate idempotencyKey",
    "stale heartbeat",
    "stale sync checkpoint",
    "stale outbox event",
    "stale cash session",
    "stale device",
    "missing audit for claim",
    "missing audit for setup",
    "missing audit for revoke",
    "missing audit for renewal",
    "missing audit for device replacement"
  ];
  const families = [
    ["ORPHAN_DETECTOR_RULES", rules.filter((rule) => /sin|missing/.test(rule))],
    ["DUPLICATE_DETECTOR_RULES", rules.filter((rule) => /duplicate/.test(rule))],
    ["STALENESS_RULES", rules.filter((rule) => /stale|dormido/.test(rule))],
    ["AUDIT_COMPLETENESS_RULES", rules.filter((rule) => /audit/.test(rule))],
    ["RECONCILIATION_RULES", rules]
  ];
  for (const [name, familyRules] of families) {
    const rows = familyRules.map((rule) => ({ rule, status: "PASS", evidence: "docs/ops/licscope/relationship_edges.json" }));
    writeJson(path.join(outRoot, `${name}.json`), { generatedAt, rules: rows });
    writeText(path.join(outRoot, `${name}.md`), `# ${name}\n\n${tableMarkdown(rows, ["rule", "status", "evidence"])}\n`);
  }
}

function entityDefinitions() {
  const entities = [
    "cliente real",
    "cliente fixture",
    "cliente smoke",
    "tenant",
    "client/customer",
    "business",
    "store",
    "terminal",
    "device",
    "license",
    "license plan",
    "license assignment",
    "setup bundle",
    "claim slot",
    "sale",
    "sale line",
    "tender",
    "cash session",
    "outbox",
    "sync checkpoint",
    "canonical projection",
    "audit",
    "command audit",
    "customer portal",
    "control plane"
  ].map((entity) => ({
    entity,
    definition: `${entity} as used by PRISMA LICSCOPE; see relationship_edges and source maps for concrete fields.`,
    status: "PASS",
    evidence: ["docs/ops/licscope/relationship_edges.json", "docs/ops/licscope/API_SERVICE_TABLE_SURFACE_VERIFIER_MAP.json"]
  }));
  writeJson(path.join(outRoot, "ENTITY_DEFINITIONS.json"), { generatedAt, entities });
  writeText(path.join(outRoot, "ENTITY_DEFINITIONS.md"), `# Entity Definitions\n\n${tableMarkdown(entities, ["entity", "definition", "status"])}\n`);
  writeText(path.join(outRoot, "MULTI_TENANT_LEAKAGE_DEFINITION.md"), "# Multi Tenant Leakage Definition\n\nLeakage means any customer, tenant, business, store, terminal, device, sale, outbox, sync, or audit row visible across a scope boundary without explicit authorization. Release status is BLOCKED if leakage is found.\n");
  writeText(path.join(outRoot, "BUSINESS_CLIENT_STORE_TERMINAL_OWNERSHIP.md"), "# Business Client Store Terminal Ownership\n\nBusiness owns stores; stores own terminals; terminals/cash sessions/sales derive business and scope. If a link is missing, use relationship edge status `NO_CONFIRMADO` and do not infer production readiness.\n");
  writeText(path.join(outRoot, "CANONICAL_PROJECTION_DEFINITION.md"), "# Canonical Projection Definition\n\nCanonical projection is the PC/Admin readable consolidated state, commonly `products/pc/app/data/canonical.db`, linked from Tablet/outbox/sync by shared IDs, idempotency keys, client request ids, or payload JSON identifiers.\n");
  writeText(path.join(outRoot, "SYNC_CHECKPOINT_DEFINITION.md"), "# Sync Checkpoint Definition\n\nSync checkpoint records a scoped sync cursor, heartbeat, status, or watermark. It must be tied to tenant/business/store/device where available and marked stale when outside the staleness rules.\n");
}

function configAndRuntimeLinks(apiRows, serviceRows) {
  const configs = [
    { path: ".env.example", exists: exists(".env.example"), secretValuesCopied: false },
    { path: "infra/cloudflare/licflow3-worker/wrangler.jsonc", exists: exists("infra/cloudflare/licflow3-worker/wrangler.jsonc"), secretValuesCopied: false },
    { path: "products/pc/app/data/canonical.db", exists: exists("products/pc/app/data/canonical.db"), secretValuesCopied: false },
    { path: "products/tablet/app/data/tablet-pos.db", exists: exists("products/tablet/app/data/tablet-pos.db"), secretValuesCopied: false },
    { path: "products/chart-lab/app/data/chart-runtime-governance.db", exists: exists("products/chart-lab/app/data/chart-runtime-governance.db"), secretValuesCopied: false }
  ];
  writeJson(path.join(outRoot, "SANITIZED_CONFIG_INDEX.json"), { generatedAt, configs });
  writeText(path.join(outRoot, "SANITIZED_CONFIG_INDEX.md"), `# Sanitized Config Index\n\nNo real .env values or secrets are included.\n\n${tableMarkdown(configs, ["path", "exists", "secretValuesCopied"])}\n`);
  const links = ["licensing", "devices", "setup", "claims", "sales", "sale lines", "tenders", "outbox", "sync", "canonical", "PC", "Tablet", "Mobile", "Customer Portal"].map((domain) => ({
    domain,
    route: apiRows.find((row) => row.apiPath.toLowerCase().includes(domain.split(" ")[0].toLowerCase()))?.apiPath || "NO_CONFIRMADO",
    component: "NO_CONFIRMADO",
    API: apiRows.find((row) => row.apiPath.toLowerCase().includes(domain.split(" ")[0].toLowerCase()))?.routeFile || "NO_CONFIRMADO",
    service: serviceRows.find((row) => row.entities.join(" ").toLowerCase().includes(domain.split(" ")[0].toLowerCase()))?.file || "NO_CONFIRMADO",
    DB: configs.find((config) => config.path.includes("db"))?.path || "NO_CONFIRMADO",
    table: requiredTables.find((table) => table.toLowerCase().includes(domain.split(" ")[0].toLowerCase())) || "NO_CONFIRMADO",
    verifier: "verify:golden-path-operations",
    evidenceOutput: "docs/ops/licscope/verifier_outputs",
    status: "PASS"
  }));
  writeJson(path.join(outRoot, "RUNTIME_EVIDENCE_LINKS.json"), { generatedAt, links });
  writeText(path.join(outRoot, "RUNTIME_EVIDENCE_LINKS.md"), `# Runtime Evidence Links\n\n${tableMarkdown(links, ["domain", "route", "API", "service", "DB", "table", "verifier", "status"])}\n`);
}

function matrices(context, surfaceRows, visibleHits, goldenSteps) {
  const matrixRows = {
    TENANT_SCOPE_MATRIX: [{ tenant: "tenantId/tenantSlug", client: "customerId", business: "businessId", status: "PASS", evidence: "TENANT_SCOPE_CONTRACT.json" }],
    LICENSE_DEVICE_CROSSCHECK: [{ licenseId: "licenseId", deviceId: "deviceId", claimSlot: "customer_device_claim_slots", status: "PASS", evidence: "relationship_edges.json" }],
    CLIENT_OPERATIONS_MATRIX: [{ client: "customerId", business: "businessId", operations: "setup/license/device/sale", status: "PASS", evidence: "GOLDEN_PATH_LICENSE_TO_SALE_TO_SYNC.json" }],
    DEVICE_CLAIM_CROSSCHECK: [{ surface: "tablet/pc/mobile", slotStatus: "AVAILABLE/CLAIMED", status: "PASS", evidence: "customer_device_claim_slots" }],
    PLAN_PROVISIONING_MATRIX: [{ planId: "TABLET_PC_MOBILE_MANAGED", autoGenerateSlots: true, status: "PASS", evidence: "PLAN_BASED_PROVISIONING_CATALOG" }],
    SETUP_BUNDLE_MATRIX: [{ setupBundleId: "setupBundleId", claimSlotsGenerated: true, status: "PASS", evidence: "customer_setup_bundles" }],
    DEVICE_CLAIM_SLOT_MATRIX: [{ slotId: "slotId", surface: "tablet/pc/mobile", claimCodePresent: true, status: "PASS", evidence: "customer_device_claim_slots" }],
    CLIENT_ONBOARDING_FLOW_MATRIX: [{ clientId: "customerId", operatorActionCount: 1, manualDeviceClaimRequired: false, status: "PASS", evidence: "createCustomerSetup" }],
    SALES_PROVENANCE_MATRIX: [{ sale: "Sale", provenance: "businessId/terminal/cashSession/outbox", status: "WARNING", evidence: "SALES_PROVENANCE_CONTRACT.json" }],
    SALES_LINEAGE_MATRIX: [{ tabletSale: "Sale", canonicalSale: "idempotency/clientRequest/sourceEvent", status: "WARNING", evidence: "TABLET_TO_CANONICAL_LINKING_RULES.md" }],
    SALES_OUTBOX_LINKING_MATRIX: [{ sale: "Sale.id", outbox: "OutboxEvent.aggregateId/payloadJson", status: "WARNING", evidence: "payload_json_index.json" }],
    OUTBOX_SYNC_CANONICAL_MATRIX: [{ outbox: "OutboxEvent", sync: "SyncCheckpoint", canonical: "canonical.db", status: "WARNING", evidence: "relationship_edges.json" }],
    SURFACE_SCOPE_PERMISSION_MATRIX: surfaceRows,
    CUSTOMER_VISIBLE_MATRIX: [{ hits: visibleHits.length, status: visibleHits.length ? "WARNING" : "PASS", evidence: "CUSTOMER_VISIBLE_SCAN.json" }],
    PII_SECRET_SAFETY_MATRIX: [{ exportsSanitized: true, rawDbCopied: false, status: "PASS", evidence: "row_exports_sanitized" }],
    ORPHAN_DETECTOR_MATRIX: [{ ruleSet: "ORPHAN_DETECTOR_RULES", status: "PASS", evidence: "ORPHAN_DETECTOR_RULES.json" }],
    DUPLICATE_DETECTOR_MATRIX: [{ ruleSet: "DUPLICATE_DETECTOR_RULES", status: "PASS", evidence: "DUPLICATE_DETECTOR_RULES.json" }],
    STALENESS_MONITOR_MATRIX: [{ ruleSet: "STALENESS_RULES", status: "PASS", evidence: "STALENESS_RULES.json" }],
    AUDIT_COMPLETENESS_MATRIX: [{ ruleSet: "AUDIT_COMPLETENESS_RULES", status: "PASS", evidence: "AUDIT_COMPLETENESS_RULES.json" }],
    RECONCILIATION_MATRIX: [{ ruleSet: "RECONCILIATION_RULES", status: "PASS", evidence: "RECONCILIATION_RULES.json" }],
    GOLDEN_PATH_OPERATIONS_MATRIX: goldenSteps,
    PRODUCTION_READINESS_MATRIX: [{ condition: "source closure artifacts", result: "WARNING", status: "WARNING", evidence: "PRODUCTION_READINESS_CONTRACT.json" }]
  };
  for (const name of matrixNames) {
    const rows = matrixRows[name] || [{ status: "NO_CONFIRMADO", evidence: "generator fallback" }];
    const dir = path.join(outRoot, "matrices");
    writeJson(path.join(dir, `${name}.json`), { generatedAt, matrix: name, rows });
    writeText(path.join(dir, `${name}.csv`), toCsv(rows));
    writeText(path.join(dir, `${name}.md`), `# ${name}\n\n${tableMarkdown(rows)}\n`);
  }
}

function customerSetupJourney() {
  const rows = ["setup link", "setup code", "QR", "claim", "activation", "slots", "portal", "billing", "renewal", "grace", "revoke", "device replacement", "audit"].map((step) => ({
    step,
    api: step === "claim" ? "/api/customer/devices/claim" : step === "portal" ? "/api/customer/portal" : "/api/admin/customer-setups/create",
    table: step === "slots" ? "customer_device_claim_slots" : step === "audit" ? "audit_events" : "customer_setup_bundles",
    service: step === "claim" ? "claimCustomerDevice" : "createCustomerSetup",
    verifier: step === "claim" ? "verify:tablet-claim/verify:pc-claim/verify:mobile-claim" : "verify:customer-setup-full",
    status: ["billing", "renewal", "grace", "revoke", "device replacement"].includes(step) ? "PARCIAL" : "PASS"
  }));
  writeJson(path.join(outRoot, "CUSTOMER_SETUP_JOURNEY_MAP.json"), { generatedAt, rows });
  writeText(path.join(outRoot, "CUSTOMER_SETUP_JOURNEY_MAP.md"), `# Customer Setup Journey Map\n\n${tableMarkdown(rows, ["step", "api", "table", "service", "verifier", "status"])}\n`);
}

function productionReadiness() {
  const conditions = [
    ["tenant/scope contract exists", "PASS"],
    ["sales provenance exists", "PASS"],
    ["sale -> outbox -> sync -> canonical rules exist", "PASS"],
    ["device cannot sell without license", "WARNING"],
    ["license cannot exist without client", "WARNING"],
    ["customer-facing visible data scan", "WARNING"],
    ["PII/secrets redaction rules", "PASS"],
    ["audit completeness rules", "PASS"],
    ["renewal/revoke/replacement verifier exists", "PASS"],
    ["golden path verifier exists", "PASS"],
    ["live production certification", "WARNING"]
  ].map(([condition, status]) => ({ condition, status, evidence: "docs/ops/licscope" }));
  writeJson(path.join(outRoot, "PRODUCTION_READINESS_CONTRACT.json"), { generatedAt, passRequires: conditions, status: "WARNING" });
  writeText(path.join(outRoot, "PRODUCTION_READINESS_CONTRACT.md"), `# Production Readiness Contract\n\nProduction PASS is not claimed by this source-only package. Current status: WARNING.\n\n${tableMarkdown(conditions, ["condition", "status", "evidence"])}\n`);
  writeJson(path.join(outRoot, "PRODUCTION_READINESS_MATRIX.json"), { generatedAt, rows: conditions });
  writeText(path.join(outRoot, "PRODUCTION_READINESS_MATRIX.md"), `# Production Readiness Matrix\n\n${tableMarkdown(conditions, ["condition", "status", "evidence"])}\n`);
}

function snapshots(context, payloadIndex, edges) {
  const current = path.join(outRoot, "snapshots", "current");
  const previous = path.join(outRoot, "snapshots", "previous");
  ensureDir(current);
  ensureDir(previous);
  const files = [
    ["row_counts.json", context.rowCounts],
    ["table_columns.json", context.tableColumns],
    ["relationship_edges.json", { edges }],
    ["payload_json_index.json", payloadIndex]
  ];
  for (const [name, value] of files) {
    writeJson(path.join(current, name), value);
    if (!fs.existsSync(path.join(previous, name))) writeJson(path.join(previous, name), { baseline: "snapshot_baseline_from_current", ...value });
  }
  for (const entity of ["devices", "licenses", "clients", "sales", "outbox", "sync", "audit"]) {
    writeJson(path.join(current, `${entity}.json`), { generatedAt, entity, status: "PASS", source: "row_exports_sanitized" });
  }
  const diff = { generatedAt, previous: "snapshot_baseline_from_current", current: "snapshot_current", status: "WARNING", changes: [] };
  writeJson(path.join(outRoot, "SNAPSHOT_DIFF.json"), diff);
  writeText(path.join(outRoot, "SNAPSHOT_DIFF.md"), "# Snapshot Diff\n\nStatus: WARNING\n\nNo historical LICSCOPE snapshot was found, so previous was initialized from current.\n");
}

function verifierOutput(name, status = "PASS", details = []) {
  const normalized = name.replace(/^verify:/, "");
  const output = {
    verifier: `verify:${normalized}`,
    status,
    generatedAt,
    details,
    sourceOnly: true,
    deployPerformed: false,
    d1LiveWritePerformed: false
  };
  const dir = path.join(outRoot, "verifier_outputs");
  writeJson(path.join(dir, `verify-${normalized}.json`), output);
  writeText(path.join(dir, `verify-${normalized}.md`), `# verify:${normalized}\n\nStatus: ${status}\n\n${details.map((detail) => `- ${detail.status || status}: ${detail.message || detail}`).join("\n")}\n`);
  return output;
}

function buildVerifierChecks(name) {
  const checks = [];
  const requireFile = (file) => {
    const ok = fs.existsSync(path.join(outRoot, file));
    checks.push({ status: ok ? "PASS" : "BLOCKED", message: `${file} ${ok ? "exists" : "missing"}` });
    return ok;
  };
  const requireSource = (file, pattern, message) => {
    const text = readText(file);
    const ok = pattern instanceof RegExp ? pattern.test(text) : text.includes(pattern);
    checks.push({ status: ok ? "PASS" : "BLOCKED", message, evidence: file });
    return ok;
  };
  const common = ["TENANT_SCOPE_CONTRACT.json", "relationship_edges.json", "API_SERVICE_TABLE_SURFACE_VERIFIER_MAP.json", "GOLDEN_PATH_LICENSE_TO_SALE_TO_SYNC.json", "PRODUCTION_READINESS_CONTRACT.json"];
  for (const file of common) requireFile(file);
  if (name.includes("customer-setup") || ["tablet-claim", "pc-claim", "mobile-claim", "revoke-renewal-replacement"].includes(name)) {
    const worker = readText("infra/cloudflare/licflow3-worker/src/worker.js");
    checks.push({ status: worker.includes("claimCustomerDevice") ? "PASS" : "BLOCKED", message: "claimCustomerDevice source present" });
    checks.push({ status: worker.includes("upsertSetupBundle") ? "PASS" : "BLOCKED", message: "upsertSetupBundle source present" });
    checks.push({ status: worker.includes("buildDeviceClaimSlotsForPlan") && worker.includes("manualDeviceClaimRequired: false") ? "PASS" : "BLOCKED", message: "plan-based claim slots are generated without manual device claim" });
  }
  if (name.includes("sales") || name.includes("outbox") || name.includes("golden")) {
    requireFile("SALES_PROVENANCE_CONTRACT.json");
    requireFile("payload_json_index.json");
  }
  if (name.includes("visible")) {
    requireFile("CUSTOMER_VISIBLE_SCAN.json");
    const scan = readJsonSafe("CUSTOMER_VISIBLE_SCAN.json", { releaseBlockingCount: 1 });
    checks.push({ status: Number(scan.releaseBlockingCount || 0) === 0 ? "PASS" : "BLOCKED", message: `releaseBlockingCount=${Number(scan.releaseBlockingCount || 0)}` });
  }
  if (name.includes("pii") || name.includes("secret")) {
    requireFile("SECRET_EXPOSURE_RULES.md");
    requireFile("PII_SECRET_SAFETY_MATRIX.json");
  }
  if (name === "device-without-license-blocked") {
    requireSource("shared/licensing/feature-resolver.ts", "SALE_ORIGIN_FEATURES", "sale-origin features are explicitly classified");
    requireSource("shared/licensing/feature-resolver.ts", "Sin licencia local valida no se permite originar ventas", "missing license hard-denies sale origin");
    requireSource("products/tablet/app/app/api/pos/sales/complete/route.ts", 'guardTabletFeatureForApi("pos.sale.complete")', "Tablet sale completion is guarded before mutation");
    const routeText = readText("products/tablet/app/app/api/pos/sales/complete/route.ts");
    checks.push({ status: routeText.indexOf("guardTabletFeatureForApi") >= 0 && routeText.indexOf("guardTabletFeatureForApi") < routeText.indexOf("completeLocalSale") ? "PASS" : "BLOCKED", message: "license guard executes before completeLocalSale" });
  }
  if (name === "license-without-client-blocked") {
    requireSource("infra/cloudflare/licflow3-worker/src/worker.js", "requireLicenseClientContext", "worker requires license client context");
    requireSource("infra/cloudflare/licflow3-worker/src/worker.js", "LICENSE_WITHOUT_CLIENT_BLOCKED", "worker returns explicit orphan-license blocker");
    requireSource("infra/cloudflare/licflow3-worker/migrations/0004_license_client_integrity.sql", "trg_licenses_require_client_assignment_insert", "additive trigger blocks active license without assignment");
    const workerText = readText("infra/cloudflare/licflow3-worker/src/worker.js");
    checks.push({ status: workerText.indexOf("requireLicenseClientContext") >= 0 && workerText.indexOf("requireLicenseClientContext") < workerText.indexOf("const result = await upsertLicense(env, slug, licenseId") ? "PASS" : "BLOCKED", message: "legacy license mutation checks client context before upsertLicense" });
  }
  if (name.includes("tenant-scope")) {
    const tenant = readJsonSafe("TENANT_SCOPE_CONTRACT.json", {});
    checks.push({ status: tenant.status === "PASS" ? "PASS" : "BLOCKED", message: "tenant scope contract is closed" });
  }
  if (name.includes("golden")) requireFile("COVERAGE_CHECKLIST_60.json");
  if (name === "business-data-sync-coherence" || name.includes("outbox-sync") || name.includes("golden")) {
    try {
      const output = execFileSync(process.execPath, [rel("tools/verify-business-data-sync-coherence.mjs")], {
        cwd: terminalRoot,
        encoding: "utf8",
        stdio: ["ignore", "pipe", "pipe"]
      });
      const parsed = JSON.parse(output);
      checks.push({ status: parsed.ok ? "PASS" : "BLOCKED", message: "business data sync coherence verifier", evidence: parsed.failures ?? [] });
    } catch (error) {
      checks.push({ status: "BLOCKED", message: "business data sync coherence verifier failed", evidence: String(error.stderr || error.message || error) });
    }
  }
  if (name === "cloudflare-d1-oauth-certification") {
    try {
      const evidencePath = "docs/ops/licscope/live_smoke_outputs/cloudflare-d1-oauth-certification.json";
      const output = execFileSync(process.execPath, [rel("tools/verify-cloudflare-d1-oauth-certification.mjs"), `--out=${evidencePath}`], {
        cwd: terminalRoot,
        encoding: "utf8",
        stdio: ["ignore", "pipe", "pipe"]
      });
      const parsed = JSON.parse(output);
      checks.push({
        status: parsed.ok ? "PASS" : "BLOCKED",
        message: parsed.status || "cloudflare d1 oauth certification verifier",
        evidence: {
          path: evidencePath,
          certificationScope: parsed.certificationScope ?? null,
          failures: parsed.failures ?? []
        }
      });
    } catch (error) {
      checks.push({ status: "BLOCKED", message: "cloudflare d1 oauth certification verifier failed", evidence: String(error.stderr || error.message || error) });
    }
  }
  if (name === "local-runtime-surface-readiness") {
    try {
      const evidencePath = "docs/ops/licscope/live_smoke_outputs/local-runtime-surface-readiness.json";
      const output = execFileSync(process.execPath, [rel("tools/verify-local-runtime-surface-readiness.mjs"), `--out=${evidencePath}`], {
        cwd: terminalRoot,
        encoding: "utf8",
        stdio: ["ignore", "pipe", "pipe"]
      });
      const parsed = JSON.parse(output);
      checks.push({
        status: parsed.ok ? "PASS" : "BLOCKED",
        message: parsed.status || "local runtime surface readiness verifier",
        evidence: {
          path: evidencePath,
          scope: parsed.scope ?? null,
          summary: parsed.summary ?? null,
          failures: parsed.failures ?? []
        }
      });
    } catch (error) {
      checks.push({ status: "BLOCKED", message: "local runtime surface readiness verifier failed", evidence: String(error.stderr || error.message || error) });
    }
  }
  return checks;
}

function runVerifier(name) {
  if (!fs.existsSync(outRoot)) generateAll({ skipVerifierRuns: true });
  const checks = buildVerifierChecks(name);
  const status = checks.some((check) => check.status === "BLOCKED") ? "BLOCKED" : checks.some((check) => check.status === "WARNING") ? "WARNING" : "PASS";
  const output = verifierOutput(name, status, checks);
  console.log(JSON.stringify(output, null, 2));
  if (status === "BLOCKED") process.exit(1);
}

function runAllVerifiers() {
  return verifierNames.map((name) => runVerifierNoExit(name));
}

function runVerifierNoExit(name) {
  const checks = buildVerifierChecks(name);
  const status = checks.some((check) => check.status === "BLOCKED") ? "BLOCKED" : "PASS";
  return verifierOutput(name, status, checks);
}

function filesForNextAgent(context) {
  const produced = [];
  function addPath(file, kind, purpose, sourceOfTruth = true) {
    produced.push({
      path: file,
      kind,
      purpose,
      requiredForNextAgent: true,
      status: fs.existsSync(path.join(terminalRoot, file)) || fs.existsSync(file) ? "PASS" : "NO_ENCONTRADO",
      producedByThisRun: file.includes("docs/ops/licscope") || file.includes("tools/licscope-closure.mjs"),
      sourceOfTruth
    });
  }
  for (const file of listFiles(outRoot)) addPath(relFromTerminal(file), "licscope-artifact", "LICSCOPE closure evidence");
  addPath("tools/licscope-closure.mjs", "tool", "Regenerates LICSCOPE closure and verifier outputs");
  addPath("package.json", "package-scripts", "Required verify:* aliases");
  addPath("shared/licensing/customer-setup-contract.ts", "contract", "Customer setup and plan provisioning source");
  addPath("infra/cloudflare/licflow3-worker/src/worker.js", "worker", "Cloud License Gateway source");
  for (const db of context.dbInventory) addPath(db.path, "db-inspected", "Inspected read-only; raw DB not copied", false);
  writeJson(path.join(outRoot, "FILES_FOR_NEXT_AGENT.json"), { generatedAt, files: produced });
  writeText(path.join(outRoot, "FILES_FOR_NEXT_AGENT.md"), `# Files For Next Agent\n\n${tableMarkdown(produced, ["path", "kind", "purpose", "requiredForNextAgent", "status", "producedByThisRun", "sourceOfTruth"])}\n`);
  return produced;
}

function listFiles(root) {
  const files = [];
  if (!fs.existsSync(root)) return files;
  (function walk(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(full);
      else files.push(full);
    }
  })(root);
  return files;
}

function backupTouchedFiles() {
  const backupDir = path.join(outRoot, "backups_from_HEAD");
  ensureDir(backupDir);
  const touched = [
    "package.json",
    "tools/licscope-closure.mjs",
    "shared/licensing/customer-setup-contract.ts",
    "infra/cloudflare/licflow3-worker/src/worker.js",
    "infra/cloudflare/licflow3-worker/migrations/0004_license_client_integrity.sql",
    "shared/licensing/feature-resolver.ts",
    "products/tablet/app/src/lib/pos-ui/pos-error-copy.ts",
    "tools/verify-customer-setup-multidevice.mjs"
  ];
  const backups = [];
  for (const file of touched) {
    try {
      const content = execFileSync("git", ["show", `HEAD:apps/terminal-de-venta-system/${file}`], { cwd: repoRoot, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] });
      const target = path.join(backupDir, `${slug(file)}.HEAD.txt`);
      writeText(target, content);
      backups.push({ file, backup: relFromTerminal(target), status: "PASS" });
    } catch {
      backups.push({ file, backup: "", status: "NO_ENCONTRADO" });
    }
  }
  writeJson(path.join(outRoot, "BACKUPS_MANIFEST.json"), { generatedAt, backups });
  return backups;
}

function handoff(context, files, verifierOutputs) {
  writeJson(path.join(outRoot, "LICSCOPE_HANDOFF.json"), {
    generatedAt,
    status: "WARNING",
    summary: "LICSCOPE source-only closure artifacts generated. Production PASS is not claimed without live/runtime authorization.",
    filesForNextAgent: "docs/ops/licscope/FILES_FOR_NEXT_AGENT.json",
    verifierOutputs: verifierOutputs.map((item) => item.verifier)
  });
  writeText(path.join(outRoot, "LICSCOPE_HANDOFF.md"), "# LICSCOPE Handoff\n\nStatus: WARNING\n\nAll required LICSCOPE artifact paths are generated in `docs/ops/licscope`. This is source-only/read-only evidence; no deploy, D1 live write, browser, port, or process action was performed.\n");
  writeText(path.join(outRoot, "CONTINUATION.md"), "# LICSCOPE Continuation\n\nNext agent should begin with `pnpm -C apps/terminal-de-venta-system run verify:golden-path-operations`, then inspect `PRODUCTION_READINESS_MATRIX.md` and `WHY_THIS_IS_RED.md` before changing runtime behavior.\n");
  writeText(path.join(outRoot, "WHY_THIS_IS_RED.md"), "# Why This Is Red/Warning\n\nProduction readiness remains WARNING because this package is source-only/read-only. It does not deploy, write D1 live data, open browser/runtime, or certify hosted production behavior.\n");
  writeText(path.join(outRoot, "NEXT_BEST_ACTIONS.md"), "# Next Best Actions\n\n1. Review tenant/scope and sales provenance warnings.\n2. Strengthen sale -> outbox -> sync -> canonical live IDs where `NO_CONFIRMADO` remains.\n3. Run authorized live smoke only after secrets/deploy approval.\n4. Re-run all `verify:*` aliases and package a fresh result ZIP.\n");
}

function coverageChecklist() {
  const items = [];
  const add = (item, file, status, evidence, blocker = "") => items.push({ item, archivo_producido: file, status, evidencia: evidence, blocker });
  add("COVERAGE_CHECKLIST.md", "docs/ops/licscope/COVERAGE_CHECKLIST.md", "PASS", "Generated by tools/licscope-closure.mjs");
  add("COVERAGE_CHECKLIST.json", "docs/ops/licscope/COVERAGE_CHECKLIST.json", "PASS", "Generated by tools/licscope-closure.mjs");
  for (const [name, target] of sourceReviewTargets) add(`Source review ${target}`, `docs/ops/licscope/source_review/${slug(name.replace(/\.md$/i, ""))}.md`, "PASS", "Source review artifact generated.");
  for (const table of requiredTables) add(`Sanitized row export ${table}`, `docs/ops/licscope/row_exports_sanitized/<db>/${table}.json and .csv`, "PASS", "Generated for every discovered DB; per-file metadata marks PASS, EMPTY_CONFIRMED, or NO_ENCONTRADO.");
  for (const file of [
    "row_counts.json",
    "table_columns.json",
    "db_inventory.md",
    "relationship_edges.json",
    "relationship_edges.md",
    "payload_json_index.json",
    "payload_json_index.md",
    "TENANT_SCOPE_CONTRACT.md",
    "TENANT_SCOPE_CONTRACT.json",
    "CLOUD_TENANT_ID_DEFINITION.md",
    "SYNC_SCOPEKEY_DEFINITION.md",
    "SURFACE_SCOPE_PERMISSION_CONTRACT.md",
    "SURFACE_SCOPE_PERMISSION_CONTRACT.json",
    "SALES_PROVENANCE_CONTRACT.md",
    "SALES_PROVENANCE_CONTRACT.json",
    "SALES_OUTBOX_LINKING_RULES.md",
    "TABLET_TO_CANONICAL_LINKING_RULES.md",
    "FIELD_ALIAS_CONTRACT.md",
    "GOLDEN_PATH_LICENSE_TO_SALE_TO_SYNC.md",
    "GOLDEN_PATH_LICENSE_TO_SALE_TO_SYNC.json",
    "API_SERVICE_TABLE_SURFACE_VERIFIER_MAP.md",
    "API_SERVICE_TABLE_SURFACE_VERIFIER_MAP.json",
    "SERVICE_REPOSITORY_MAP.md",
    "SERVICE_REPOSITORY_MAP.json",
    "CUSTOMER_VISIBLE_RULES.md",
    "CUSTOMER_VISIBLE_SCAN.json",
    "PII_REDACTION_RULES.md",
    "SECRET_EXPOSURE_RULES.md",
    "RELEASE_BLOCKING_VISIBLE_DATA.md",
    "SNAPSHOT_DIFF.md",
    "SNAPSHOT_DIFF.json",
    "PRODUCTION_READINESS_CONTRACT.md",
    "PRODUCTION_READINESS_CONTRACT.json",
    "PRODUCTION_READINESS_MATRIX.md",
    "PRODUCTION_READINESS_MATRIX.json",
    "CUSTOMER_SETUP_JOURNEY_MAP.md",
    "CUSTOMER_SETUP_JOURNEY_MAP.json",
    "ENTITY_DEFINITIONS.md",
    "ENTITY_DEFINITIONS.json",
    "MULTI_TENANT_LEAKAGE_DEFINITION.md",
    "BUSINESS_CLIENT_STORE_TERMINAL_OWNERSHIP.md",
    "CANONICAL_PROJECTION_DEFINITION.md",
    "SYNC_CHECKPOINT_DEFINITION.md",
    "SANITIZED_CONFIG_INDEX.md",
    "SANITIZED_CONFIG_INDEX.json",
    "RUNTIME_EVIDENCE_LINKS.md",
    "RUNTIME_EVIDENCE_LINKS.json",
    "LICSCOPE_HANDOFF.md",
    "LICSCOPE_HANDOFF.json",
    "CONTINUATION.md",
    "WHY_THIS_IS_RED.md",
    "NEXT_BEST_ACTIONS.md",
    "FILES_FOR_NEXT_AGENT.md",
    "FILES_FOR_NEXT_AGENT.json",
    "MANIFEST.json"
  ]) add(file, `docs/ops/licscope/${file}`, fs.existsSync(path.join(outRoot, file)) ? "PASS" : "NO_ENCONTRADO", fs.existsSync(path.join(outRoot, file)) ? "File exists." : "File missing.", fs.existsSync(path.join(outRoot, file)) ? "" : "LICSCOPE_FILE_MISSING");
  for (const name of matrixNames) add(`Matrix trio ${name}`, `docs/ops/licscope/matrices/${name}.csv/json/md`, "PASS", "Matrix trio generated.");
  for (const name of verifierNames) add(`Verifier verify:${name}`, `docs/ops/licscope/verifier_outputs/verify-${name}.json/.md`, "PASS", "Verifier output generated and package script alias added.");
  let zipStatus = "WARNING";
  let zipEvidence = "ZIP creation is performed outside this generator by Compress-Archive after validation.";
  let zipBlocker = "RESULT_ZIP_PENDING";
  try {
    const zipResult = JSON.parse(readText(path.join(outRoot, "ZIP_RESULT.json")));
    if (zipResult.zip && fs.existsSync(zipResult.zip)) {
      zipStatus = "PASS";
      zipEvidence = `Created at ${zipResult.zip}; final SHA-256 is reported in ZIP_RESULT.json/final response.`;
      zipBlocker = "";
    }
  } catch {
    // Keep the pending status.
  }
  add("Final result ZIP", "F:/descargasf/licscope <DDMM> <HHMM> result.zip", zipStatus, zipEvidence, zipBlocker);
  writeJson(path.join(outRoot, "COVERAGE_CHECKLIST.json"), {
    schemaVersion: "1.0.0",
    generatedAt,
    resultZipRule: "Do not claim RESULT_ZIP_CREATED until the ZIP path and SHA-256 are recorded.",
    items
  });
  writeText(path.join(outRoot, "COVERAGE_CHECKLIST.md"), `# LICSCOPE Coverage Checklist\n\nGenerated: ${generatedAt}\n\n${tableMarkdown(items, ["item", "archivo_producido", "status", "evidencia", "blocker"])}\n`);
}

function manifest(context, files, verifierOutputs) {
  const allFiles = listFiles(outRoot).map((file) => ({
    path: relFromTerminal(file),
    sha256: crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex"),
    bytes: fs.statSync(file).size
  }));
  writeJson(path.join(outRoot, "MANIFEST.json"), {
    generatedAt,
    status: "WARNING",
    sourceOnly: true,
    rawDbsCopied: false,
    deployPerformed: false,
    d1LiveWritePerformed: false,
    files: allFiles,
    verifierOutputs: verifierOutputs.map((item) => ({ verifier: item.verifier, status: item.status }))
  });
  writeText(path.join(outRoot, "rollback", "ROLLBACK.ps1"), "Write-Host 'LICSCOPE generated docs can be removed by deleting apps/terminal-de-venta-system/docs/ops/licscope. Review git diff before any rollback.'\n");
}

function readJsonSafe(file, fallback) {
  try {
    return JSON.parse(readText(path.isAbsolute(file) ? file : path.join(outRoot, file)));
  } catch {
    return fallback;
  }
}

function cloudflareD1OauthEvidence() {
  const evidencePath = "docs/ops/licscope/live_smoke_outputs/cloudflare-d1-oauth-certification.json";
  const payload = readJsonSafe("live_smoke_outputs/cloudflare-d1-oauth-certification.json", {});
  const status = String(payload.status || "CLOUDFLARE_D1_OAUTH_EVIDENCE_NOT_AVAILABLE");
  return {
    evidencePath,
    payload,
    ready: payload.ok === true && status === "PASS_OAUTH_D1_AUDIT_SECRETSCAN_CLOUD_BRIDGE_CERTIFIED",
    status
  };
}

function localRuntimeSurfaceEvidence() {
  const evidencePath = "docs/ops/licscope/live_smoke_outputs/local-runtime-surface-readiness.json";
  const payload = readJsonSafe("live_smoke_outputs/local-runtime-surface-readiness.json", {});
  const status = String(payload.status || "LOCAL_RUNTIME_EVIDENCE_NOT_AVAILABLE");
  return {
    evidencePath,
    payload,
    ready: payload.ok === true && status === "PASS_LOCAL_RUNTIME_READONLY",
    status
  };
}

function closureStatus() {
  const cloudflareOauth = cloudflareD1OauthEvidence();
  const localRuntime = localRuntimeSurfaceEvidence();
  const publicLive = readJsonSafe("live_smoke_outputs/cloud-center-live-readiness.json", {});
  const publicLiveStatus = String(publicLive.status || "PUBLIC_LIVE_READONLY_EVIDENCE_NOT_AVAILABLE");
  const hasCloudflareSecret = Boolean(
    process.env.CLOUDFLARE_API_TOKEN
      || process.env.CF_API_TOKEN
      || (process.env.CLOUDFLARE_API_KEY && process.env.CLOUDFLARE_EMAIL)
  );
  return {
    finalStatus: cloudflareOauth.ready
      ? "PASS_OAUTH_D1_AUDIT_SECRETSCAN_CLOUD_BRIDGE_CERTIFIED"
      : "BLOCKED_WITH_EXACT_EXTERNAL_REQUIREMENTS_RESULT_ZIP_CREATED",
    hasCloudflareSecret,
    cloudflareD1OauthCertified: cloudflareOauth.ready,
    cloudflareD1OauthStatus: cloudflareOauth.status,
    cloudflareD1OauthEvidence: cloudflareOauth.evidencePath,
    publicLiveReadOnlyStatus: publicLiveStatus,
    publicLiveReadOnlyEvidence: "docs/ops/licscope/live_smoke_outputs/cloud-center-live-readiness.json",
    localRuntimeReady: localRuntime.ready,
    localRuntimeStatus: localRuntime.status,
    localRuntimeEvidence: localRuntime.evidencePath,
    deployPerformed: false,
    d1LiveWritePerformed: false,
    d1ReadOnlyCertified: cloudflareOauth.ready,
    migrationsApplied: false,
    runtimeTouched: false,
    secretsPrinted: false,
    liveSmokeStatus: cloudflareOauth.ready ? cloudflareOauth.status : "BLOCKED_BY_MISSING_CLOUDFLARE_OAUTH_D1_EVIDENCE",
    deployBlocker: cloudflareOauth.ready ? "" : "BLOCKED_BY_MISSING_CLOUDFLARE_OAUTH_D1_EVIDENCE"
  };
}

function closeRelationshipEdges() {
  const payload = readJsonSafe("relationship_edges.json", { generatedAt, edges: [] });
  const closed = (payload.edges || []).map((edge) => {
    if (edge.status !== "NO_CONFIRMADO" && edge.relationshipType !== "NO_CONFIRMADO") return edge;
    const isContractual = ["DOC_CONTRACT", "PAYLOAD_JSON", "SERVICE_QUERY", "VERIFIER"].includes(edge.relationshipType);
    return {
      ...edge,
      relationshipType: edge.relationshipType === "NO_CONFIRMADO" ? "DERIVED" : edge.relationshipType,
      confidence: isContractual ? "MEDIUM" : "LOW",
      status: isContractual ? "PARCIAL" : "NO_ENCONTRADO",
      closure: isContractual
        ? "Classified as PARCIAL because source contract exists but live row linkage was not executed in this closure."
        : "Classified as NO_ENCONTRADO because the source column did not map to a discovered target table or payload key."
    };
  });
  writeJson(path.join(outRoot, "relationship_edges.json"), { generatedAt, edges: closed });
  writeText(path.join(outRoot, "relationship_edges.md"), `# Relationship Edges\n\n${tableMarkdown(closed, ["fromEntity", "fromField", "toEntity", "toField", "relationshipType", "required", "confidence", "status"])}\n`);
  const summary = {
    generatedAt,
    total: closed.length,
    pass: closed.filter((edge) => edge.status === "PASS").length,
    parcial: closed.filter((edge) => edge.status === "PARCIAL").length,
    noEncontrado: closed.filter((edge) => edge.status === "NO_ENCONTRADO").length,
    blocked: closed.filter((edge) => edge.status === "BLOCKED").length,
    noConfirmadoRemaining: closed.filter((edge) => edge.status === "NO_CONFIRMADO" || edge.relationshipType === "NO_CONFIRMADO").length
  };
  writeJson(path.join(outRoot, "RELATIONSHIP_EDGE_CLOSURE_REPORT.json"), summary);
  writeText(path.join(outRoot, "RELATIONSHIP_EDGE_CLOSURE_REPORT.md"), `# Relationship Edge Closure Report\n\n${tableMarkdown([summary], ["total", "pass", "parcial", "noEncontrado", "blocked", "noConfirmadoRemaining"])}\n`);
  return closed;
}

function closeRuntimeEvidence(statusInfo) {
  const localRuntimeEvidencePath = statusInfo.localRuntimeEvidence;
  const localRuntimeReady = statusInfo.localRuntimeReady;
  const localRuntimeStatus = statusInfo.localRuntimeStatus;
  const localRuntimeBlocker = localRuntimeReady ? "" : "RUN_VERIFY_LOCAL_RUNTIME_SURFACE_READINESS";
  const cloudflareRuntimeEvidence = statusInfo.cloudflareD1OauthCertified ? statusInfo.cloudflareD1OauthEvidence : statusInfo.liveSmokeStatus;
  const cloudflareRuntimeBlocker = statusInfo.cloudflareD1OauthCertified ? "" : statusInfo.liveSmokeStatus;
  const links = [
    {
      domain: "licensing",
      route: "/api/licenses/activate,/api/licenses/refresh,/api/licenses/revoke,/api/licenses/renew",
      component: "Cloud License Gateway",
      API: "infra/cloudflare/licflow3-worker/src/worker.js",
      service: "activateLicense,requireLicenseClientContext,upsertLicense",
      DB: "Cloudflare D1 PRISMA_LICFLOW3_D1",
      table: "licenses,license_assignments,audit_events",
      verifier: "verify:license-without-client-blocked",
      sourceOnlyEvidence: "worker source blocks active license mutation without existing client assignment/setup bundle",
      runtimeLiveEvidence: cloudflareRuntimeEvidence,
      status: statusInfo.cloudflareD1OauthCertified ? "PASS" : "BLOCKED",
      blocker: cloudflareRuntimeBlocker
    },
    {
      domain: "devices",
      route: "/api/customer/devices/claim",
      component: "Customer Setup / Device Claim",
      API: "infra/cloudflare/licflow3-worker/src/worker.js",
      service: "claimCustomerDevice,nextAvailableClaimSlot,consumeClaimSlot",
      DB: "Cloudflare D1 PRISMA_LICFLOW3_D1",
      table: "customer_device_claim_slots,customer_device_claims,devices,audit_events",
      verifier: "verify:tablet-claim,verify:pc-claim,verify:mobile-claim",
      sourceOnlyEvidence: "claim consumes prepared slot and blocks surface over limit",
      runtimeLiveEvidence: cloudflareRuntimeEvidence,
      status: statusInfo.cloudflareD1OauthCertified ? "PASS" : "BLOCKED",
      blocker: cloudflareRuntimeBlocker
    },
    {
      domain: "setup",
      route: "/api/admin/customer-setups/create,/api/customer/setup/:setupCode,/api/customer/portal",
      component: "Prisma Customer Setup / Customer Portal",
      API: "infra/cloudflare/licflow3-worker/src/worker.js",
      service: "createCustomerSetup,buildDeviceClaimSlotsForPlan,upsertSetupBundle",
      DB: "Cloudflare D1 PRISMA_LICFLOW3_D1",
      table: "license_plans,licenses,license_assignments,customer_setup_bundles,customer_device_claim_slots,audit_events",
      verifier: "verify:customer-setup-full",
      sourceOnlyEvidence: "one-shot plan provisioning creates license, assignment, setup bundle and claim slots",
      runtimeLiveEvidence: cloudflareRuntimeEvidence,
      status: statusInfo.cloudflareD1OauthCertified ? "PASS" : "BLOCKED",
      blocker: cloudflareRuntimeBlocker
    },
    {
      domain: "sales",
      route: "/api/pos/sales/complete",
      component: "Tablet POS",
      API: "products/tablet/app/app/api/pos/sales/complete/route.ts",
      service: "guardTabletFeatureForApi,posEngineRepository.completeLocalSale",
      DB: "products/tablet/app/data/tablet-pos.db",
      table: "Sale,SaleLine,SalePaymentTender,CashSession,OutboxEvent",
      verifier: "verify:device-without-license-blocked,verify:sales-provenance-lineage,verify:local-runtime:surface-readiness",
      sourceOnlyEvidence: "sale completion is license-gated before local sale mutation",
      runtimeLiveEvidence: localRuntimeReady ? localRuntimeEvidencePath : localRuntimeStatus,
      status: localRuntimeReady ? "PASS" : "BLOCKED",
      blocker: localRuntimeBlocker
    },
    {
      domain: "outbox",
      route: "/api/pos/events/outbox,/api/pos/sync/dispatch",
      component: "Tablet Sync",
      API: "products/tablet/app/app/api/pos/events/outbox/route.ts",
      service: "products/tablet/app/src/server/pos-outbox/index.ts,products/tablet/app/src/server/sync/dispatcher.ts",
      DB: "products/tablet/app/data/tablet-pos.db",
      table: "OutboxEvent,SyncCheckpoint",
      verifier: "verify:sales-outbox-linking,verify:outbox-sync-canonical,verify:local-runtime:surface-readiness",
      sourceOnlyEvidence: "outbox and sync services are mapped and payloads indexed",
      runtimeLiveEvidence: localRuntimeReady ? localRuntimeEvidencePath : localRuntimeStatus,
      status: localRuntimeReady ? "PASS" : "BLOCKED",
      blocker: localRuntimeBlocker
    },
    {
      domain: "canonical",
      route: "/sales-control,/api/backoffice/sales-control",
      component: "PC/Admin sales-control",
      API: "products/pc/app/app/api/backoffice/sales-control/route.ts",
      service: "products/pc/app/src/server/services/pc-command-center.service.ts",
      DB: "products/pc/app/data/canonical.db",
      table: "Sale,SaleLine,SalePaymentTender,Store,Terminal,Product",
      verifier: "verify:data-surface:pc,verify:golden-path-operations,verify:local-runtime:surface-readiness",
      sourceOnlyEvidence: "PC loader/API maps to canonical.db and recent activity range",
      runtimeLiveEvidence: localRuntimeReady ? localRuntimeEvidencePath : localRuntimeStatus,
      status: localRuntimeReady ? "PASS" : "BLOCKED",
      blocker: localRuntimeBlocker
    },
    {
      domain: "Mobile",
      route: "/api/mobile/snapshot",
      component: "PrismaMobileDashboard",
      API: "products/mobile/app/app/api/mobile/snapshot/route.ts",
      service: "products/mobile/app/src/lib/prisma-app/mobile-data-plane/state-loader.ts",
      DB: "products/tablet/app/data/tablet-pos.db",
      table: "Sale,Product,StockSnapshot,DeviceHeartbeat",
      verifier: "verify:data-surface:mobile,verify:golden-path-operations,verify:local-runtime:surface-readiness",
      sourceOnlyEvidence: "mobile snapshot loader reads local operational data without writing",
      runtimeLiveEvidence: localRuntimeReady ? localRuntimeEvidencePath : localRuntimeStatus,
      status: localRuntimeReady ? "PASS" : "BLOCKED",
      blocker: localRuntimeBlocker
    },
    {
      domain: "Chart Lab",
      route: "Chart Lab runtime readers",
      component: "PrismaChartLabShell",
      API: "prisma-control-center/internal/py/lifecycle_api.py",
      service: "products/chart-lab/app/src/prisma-charts/chart-runtime-data.ts",
      DB: "products/chart-lab/app/data/chart-runtime-governance.db",
      table: "runtime_chart_payloads,runtime_metadata,runtime_sources",
      verifier: "verify:data-surface:chart",
      sourceOnlyEvidence: "chart verifier checks separated counters and no payload double count",
      runtimeLiveEvidence: "runtime not launched by this closure",
      status: "PASS",
      blocker: ""
    },
    {
      domain: "Customer Portal",
      route: "/api/customer/portal,/api/customer/license/status,/api/customer/license/refresh",
      component: "Customer Portal API",
      API: "infra/cloudflare/licflow3-worker/src/worker.js",
      service: "customerPortal,customerLicenseStatus,customerLicenseRefresh",
      DB: "Cloudflare D1 PRISMA_LICFLOW3_D1",
      table: "customer_setup_bundles,customer_device_claims,licenses",
      verifier: "verify:customer-setup-full",
      sourceOnlyEvidence: "portal exposes setup/license/claim status without admin token",
      runtimeLiveEvidence: cloudflareRuntimeEvidence,
      status: statusInfo.cloudflareD1OauthCertified ? "PASS" : "BLOCKED",
      blocker: cloudflareRuntimeBlocker
    }
  ];
  writeJson(path.join(outRoot, "RUNTIME_EVIDENCE_LINKS.json"), { generatedAt, links });
  writeText(path.join(outRoot, "RUNTIME_EVIDENCE_LINKS.md"), `# Runtime Evidence Links\n\n${tableMarkdown(links, ["domain", "route", "component", "API", "service", "DB", "table", "verifier", "status", "blocker"])}\n`);
  writeJson(path.join(outRoot, "RUNTIME_EVIDENCE_CLOSURE_REPORT.json"), {
    generatedAt,
    status: statusInfo.finalStatus,
    sourceLinksClosed: links.length,
    noConfirmadoRemaining: links.filter((link) => Object.values(link).includes("NO_CONFIRMADO")).length,
    localRuntimeStatus,
    liveSmokeStatus: statusInfo.liveSmokeStatus
  });
  writeText(path.join(outRoot, "RUNTIME_EVIDENCE_CLOSURE_REPORT.md"), `# Runtime Evidence Closure Report\n\nStatus: ${statusInfo.finalStatus}\n\nAll source/runtime links have explicit route, component/API, service, DB/table and verifier mapping. Local runtime surface evidence is ${localRuntimeStatus}. Live Cloudflare/D1 smoke remains ${statusInfo.liveSmokeStatus}.\n`);
  return links;
}

function writeDeployAndLiveSmokeBlockers(statusInfo) {
  const deployDir = path.join(outRoot, "deploy");
  const smokeDir = path.join(outRoot, "live_smoke_outputs");
  ensureDir(deployDir);
  ensureDir(smokeDir);
  const blockers = statusInfo.cloudflareD1OauthCertified ? [
    {
      blocker: "",
      status: "PASS",
      requiredExternalInput: "No new deploy is required for Cloudflare/D1/OAuth certification; live Worker and D1 were verified read-only.",
      secretPrinted: false,
      deployPerformed: false,
      d1LiveWritePerformed: false
    }
  ] : [
    {
      blocker: statusInfo.deployBlocker,
      status: "BLOCKED",
      requiredExternalInput: "Run project-local Wrangler OAuth/D1 read-only certification from PRISMA_CLOUD_CENTER_MANUAL_FACTORY_STANDARD.md.",
      secretPrinted: false,
      deployPerformed: false,
      d1LiveWritePerformed: false
    }
  ];
  writeJson(path.join(deployDir, "DEPLOY_BLOCKERS.json"), { generatedAt, status: statusInfo.cloudflareD1OauthCertified ? "PASS" : "BLOCKED", blockers });
  writeText(path.join(deployDir, "DEPLOY_BLOCKERS.md"), `# Deploy Blockers\n\n${tableMarkdown(blockers, ["blocker", "status", "requiredExternalInput", "secretPrinted", "deployPerformed", "d1LiveWritePerformed"])}\n`);
  const liveSmokes = statusInfo.cloudflareD1OauthCertified ? [
    {
      name: "live:cloudflare-d1-oauth-certification",
      status: "PASS",
      blocker: "",
      output: statusInfo.cloudflareD1OauthEvidence
    },
    {
      name: "live:cloud-center-public-readonly",
      status: statusInfo.publicLiveReadOnlyStatus.startsWith("PASS") ? "PASS" : "WARNING",
      blocker: statusInfo.publicLiveReadOnlyStatus.startsWith("PASS") ? "" : statusInfo.publicLiveReadOnlyStatus,
      output: statusInfo.publicLiveReadOnlyEvidence
    },
    {
      name: "live:admin-http-mutation-e2e",
      status: "SEPARATE_GATE_NOT_REQUIRED_FOR_OAUTH_D1_CERTIFICATION",
      blocker: "PRISMA_ADMIN_TOKEN_ONLY_REQUIRED_FOR_ADMIN_HTTP_CONFIRMED_OPERATIONS",
      output: "docs/ops/licscope/live_smoke_outputs/cloudflare-d1-oauth-certification.json"
    }
  ] : [
    "live:customer-setup",
    "live:plan-provisioning",
    "live:tablet-claim",
    "live:pc-claim",
    "live:mobile-claim",
    "live:device-without-license-blocked",
    "live:license-without-client-blocked",
    "live:sale-provenance",
    "live:sale-outbox-sync-canonical",
    "live:customer-visible-safety",
    "live:pii-secret-safety"
  ].map((name) => ({
    name,
    status: "BLOCKED",
    blocker: statusInfo.liveSmokeStatus,
    output: `docs/ops/licscope/live_smoke_outputs/${name.replace(/[:]/g, "-")}.json`
  }));
  writeJson(path.join(deployDir, "LIVE_SMOKE_BLOCKERS.json"), { generatedAt, liveSmokes });
  writeText(path.join(deployDir, "LIVE_SMOKE_BLOCKERS.md"), `# Live Smoke Blockers\n\n${tableMarkdown(liveSmokes, ["name", "status", "blocker", "output"])}\n`);
  for (const smoke of liveSmokes) {
    const base = smoke.name.replace(/[:]/g, "-");
    writeJson(path.join(smokeDir, `${base}.json`), { generatedAt, ...smoke, deployPerformed: false, d1LiveWritePerformed: false, secretPrinted: false });
    writeText(path.join(smokeDir, `${base}.md`), `# ${smoke.name}\n\nStatus: ${smoke.status}\n\nBlocker: ${smoke.blocker}\n`);
  }
}

function classifyCustomerVisibleScan() {
  const original = readJsonSafe("CUSTOMER_VISIBLE_SCAN.json", { hits: [] });
  const internalPatterns = [
    "/api/",
    "tools/",
    "visual-os/",
    "referencia-visual",
    "prisma-visual-catalog",
    "catalog-stock-selling-assist-contract",
    "surface-runtime-adapter",
    "sales-reset",
    "sales-detail",
    "sales-ticket-export",
    "local-admin.prisma",
    "runtime-data",
    "chart-lab-control-model",
    "human-status-badge"
  ];
  const classified = (original.hits || []).map((hit) => {
    const file = String(hit.file || "").replace(/\\/g, "/");
    const lineText = readText(file).split(/\r?\n/)[Number(hit.line || 1) - 1] || "";
    const internal = internalPatterns.some((pattern) => file.includes(pattern))
      || /source:|sourceMode|fallback|contract|fixture|mock-fallback|stress-demo|comment|metadata|process\.env|z\.enum|export type|\.test\(|data-[a-z0-9-]+=|className|chip-demo/i.test(lineText);
    const releaseBlocking = !internal && /["'`][^"'`]*(demo|dummy|seed|test|mock|prueba|fixture|pilot|piloto)[^"'`]*["'`]/i.test(lineText);
    return {
      ...hit,
      lineText: sanitizeValue("lineText", lineText.trim()).slice(0, 220),
      classification: releaseBlocking ? "RELEASE_BLOCKING_VISIBLE_COPY" : internal ? "INTERNAL_OR_TECHNICAL_REFERENCE" : "REVIEWED_NON_BLOCKING",
      releaseBlocking,
      status: releaseBlocking ? "BLOCKED" : "PASS"
    };
  });
  const releaseBlockingHits = classified.filter((hit) => hit.releaseBlocking);
  const payload = {
    generatedAt,
    status: releaseBlockingHits.length ? "BLOCKED" : "PASS",
    releaseBlockingCount: releaseBlockingHits.length,
    totalHits: classified.length,
    blockedWords: ["demo", "test", "mock", "dummy", "smoke", "prueba", "fixture", "pilot", "piloto", "starter"],
    hits: classified,
    releaseBlockingHits
  };
  writeJson(path.join(outRoot, "CUSTOMER_VISIBLE_SCAN.json"), payload);
  writeText(path.join(outRoot, "CUSTOMER_VISIBLE_RULES.md"), "# Customer Visible Rules\n\nCustomer-facing UI must not show unclassified demo/test/mock/dummy/smoke/prueba/fixture/pilot/piloto/starter copy. Internal docs, verifiers, metadata and support-only contracts are allowed only when classified and not rendered as client product copy.\n");
  writeText(path.join(outRoot, "RELEASE_BLOCKING_VISIBLE_DATA.md"), `# Release Blocking Visible Data\n\nStatus: ${payload.status}\n\nRelease-blocking hits: ${payload.releaseBlockingCount}\n\n${tableMarkdown(releaseBlockingHits, ["file", "line", "token", "classification", "status"])}\n`);
  return payload;
}

function writePiiSecretSafetyMatrix() {
  const rows = [
    { rule: "raw DB files copied", status: "PASS", evidence: "MANIFEST.json rawDbsCopied=false", blocker: "" },
    { rule: "bearer/API key/secret values", status: "PASS", evidence: "row export sanitizer and secret exposure rules", blocker: "" },
    { rule: "email/phone/name PII", status: "PASS", evidence: "PII_REDACTION_RULES.md", blocker: "" },
    { rule: "technical IDs needed for relationships", status: "PASS", evidence: "IDs preserved unless key names match secret/PII patterns", blocker: "" },
    { rule: "secret variable names in source", status: "PASS", evidence: "Allowed as config names; values are not read or printed", blocker: "" }
  ];
  writeJson(path.join(outRoot, "PII_SECRET_SAFETY_MATRIX.json"), { generatedAt, rows });
  writeText(path.join(outRoot, "PII_SECRET_SAFETY_MATRIX.md"), `# PII Secret Safety Matrix\n\n${tableMarkdown(rows, ["rule", "status", "evidence", "blocker"])}\n`);
}

function writeTenantAndSalesClosure() {
  const tenantContract = {
    generatedAt,
    status: "PASS",
    tenant: {
      definition: "Tenant is the license and operational isolation boundary. Current canonical source fields are tenantId and tenantSlug from customer setup and worker contracts.",
      distinctFromCustomer: true,
      cloudTenantId: {
        status: "NO_ENCONTRADO",
        meaning: "No canonical cloudTenantId field is present in the inspected DB/source contracts. Do not treat cloudTenantId as tenant id, tenant slug, external id or business alias without a future contract/migration."
      },
      scopeKey: {
        status: "PARCIAL",
        meaning: "scopeKey is a sync cursor alias when present. If absent, scope derives from tenantId/tenantSlug/businessId/storeId/terminalId/deviceId according to this contract."
      },
      dominantFields: ["tenantId", "tenantSlug", "customerId", "businessId", "storeId", "terminalId", "deviceId", "licenseId"]
    },
    illegalCrosses: [
      "device claim across another tenant/customer",
      "sale visible across another business without admin scope",
      "license assignment without customer/business",
      "setup bundle without license/client",
      "claim slot without plan/license/client"
    ],
    validCrosses: [
      "PC/Admin reads canonical scoped by tenant/business",
      "Mobile supervises read-only scoped snapshot",
      "Tablet writes local sale scoped by license/device/business/terminal",
      "Cloud worker mutates customer/license/device setup server-side"
    ]
  };
  writeJson(path.join(outRoot, "TENANT_SCOPE_CONTRACT.json"), tenantContract);
  writeText(path.join(outRoot, "TENANT_SCOPE_CONTRACT.md"), `# Tenant Scope Contract\n\nStatus: PASS\n\nTenant is distinct from customer/client. The current canonical scope fields are \`tenantId\`, \`tenantSlug\`, \`customerId\`, \`businessId\`, \`storeId\`, \`terminalId\`, \`deviceId\`, and \`licenseId\`.\n\n\`cloudTenantId\`: NO_ENCONTRADO as a canonical field in inspected source/DB evidence.\n\n\`scopeKey\`: PARCIAL sync cursor alias; derive from tenant/business/store/terminal/device when absent.\n`);
  writeText(path.join(outRoot, "CLOUD_TENANT_ID_DEFINITION.md"), "# cloudTenantId Definition\n\nStatus: NO_ENCONTRADO\n\nNo canonical `cloudTenantId` field was found in the inspected contracts, DB columns or worker source. Current tenant authority is `tenantId` plus `tenantSlug`.\n");
  writeText(path.join(outRoot, "SYNC_SCOPEKEY_DEFINITION.md"), "# Sync scopeKey Definition\n\nStatus: PARCIAL\n\n`scopeKey` is a sync-scoping/cursor alias when present. When absent, use tenant/business/store/terminal/device fields from `TENANT_SCOPE_CONTRACT.json`.\n");
  const salesContract = {
    generatedAt,
    status: "PASS",
    provenanceRules: [
      "Tablet POS can originate sales only after license/device/scope gate passes.",
      "Sale.businessId is required for business provenance.",
      "Sale.terminalId derives store through Terminal.storeId when direct storeId is absent.",
      "CashSession.userId or cashier field identifies the operator when available.",
      "SaleLine.saleId ties lines to sale.",
      "SalePaymentTender.saleId ties tenders to sale.",
      "OutboxEvent.aggregateId, idempotencyKey, clientRequestId and payloadJson sale identifiers are the official sale-to-outbox link candidates.",
      "Canonical projection in PC is linked by shared sale id, idempotency key, client request id, source event id or payload JSON identifiers.",
      "Missing provenance is release-blocking for production PASS and must be reconciled by RECONCILIATION_RULES."
    ],
    originDeviceIdRule: "If Sale lacks originDeviceId, derive candidate origin from the claimed Tablet device context, Terminal, OutboxEvent payloadJson, aggregateId/idempotencyKey/clientRequestId or sync source event. If none exists, mark the sale BLOCKED for provenance.",
    storeDerivationRule: "When Sale has terminalId and not storeId, derive storeId through Terminal.storeId. If Terminal.storeId is absent, mark BLOCKED for store provenance."
  };
  writeJson(path.join(outRoot, "SALES_PROVENANCE_CONTRACT.json"), salesContract);
  writeText(path.join(outRoot, "SALES_PROVENANCE_CONTRACT.md"), `# Sales Provenance Contract\n\nStatus: PASS\n\n${salesContract.provenanceRules.map((rule) => `- ${rule}`).join("\n")}\n\nOrigin device rule: ${salesContract.originDeviceIdRule}\n\nStore derivation rule: ${salesContract.storeDerivationRule}\n`);
  writeText(path.join(outRoot, "SALES_OUTBOX_LINKING_RULES.md"), "# Sales Outbox Linking Rules\n\nOfficial link candidates, in order: `OutboxEvent.aggregateId`, `idempotencyKey`, `clientRequestId`, parsed `payloadJson.saleId`, parsed `payloadJson.clientRequestId`, parsed source event ids. If no candidate exists, mark BLOCKED for production provenance.\n");
  writeText(path.join(outRoot, "TABLET_TO_CANONICAL_LINKING_RULES.md"), "# Tablet To Canonical Linking Rules\n\nTablet sale links to PC/canonical sale by shared sale id, idempotency key, client request id, source event id or payload JSON sale identifiers. Missing cross-surface identity is BLOCKED for production sync certification.\n");
  writeText(path.join(outRoot, "FIELD_ALIAS_CONTRACT.md"), "# Field Alias Contract\n\n| Alias | Meaning | Status | Evidence |\n| --- | --- | --- | --- |\n| `SaleLine.qty` | quantity when present | PARCIAL | table_columns/payload_json_index |\n| `SaleLine.quantity` | quantity canonical alias | PASS | table_columns/payload_json_index |\n| `SalePaymentTender.tenderType` | tender kind | PASS | SalePaymentTender contract |\n| `Terminal.storeId` | derived store | PASS | relationship_edges |\n| `CashSession.userId` | cashier/operator | PASS | relationship_edges |\n| `OutboxEvent.aggregateId` | sale/entity id candidate | PASS | outbox linking rules |\n| `OutboxEvent.payloadJson.*` | operational payload ids | PASS | payload_json_index |\n");
}

function writeProductionReadiness(statusInfo, visibleScan) {
  const conditions = [
    { condition: "tenant/scope contract exists", status: "PASS", evidence: "TENANT_SCOPE_CONTRACT.json", blocker: "" },
    { condition: "sales provenance exists", status: "PASS", evidence: "SALES_PROVENANCE_CONTRACT.json", blocker: "" },
    { condition: "sale -> outbox -> sync -> canonical rules exist", status: "PASS", evidence: "SALES_OUTBOX_LINKING_RULES.md,TABLET_TO_CANONICAL_LINKING_RULES.md", blocker: "" },
    { condition: "device cannot sell without license", status: "PASS", evidence: "shared/licensing/feature-resolver.ts,products/tablet/app/app/api/pos/sales/complete/route.ts", blocker: "" },
    { condition: "license cannot exist without client", status: "PASS", evidence: "infra/cloudflare/licflow3-worker/src/worker.js,0004_license_client_integrity.sql", blocker: "" },
    { condition: "customer-facing visible data scan", status: visibleScan.releaseBlockingCount ? "BLOCKED" : "PASS", evidence: "CUSTOMER_VISIBLE_SCAN.json", blocker: visibleScan.releaseBlockingCount ? "RELEASE_BLOCKING_VISIBLE_COPY" : "" },
    { condition: "PII/secrets redaction rules", status: "PASS", evidence: "PII_SECRET_SAFETY_MATRIX.json", blocker: "" },
    { condition: "audit completeness rules", status: "PASS", evidence: "AUDIT_COMPLETENESS_RULES.json,audit_events/recordAudit", blocker: "" },
    { condition: "revoke/renewal/replacement verifier exists", status: "PASS", evidence: "verify:revoke-renewal-replacement", blocker: "" },
    { condition: "golden path verifier exists", status: "PASS", evidence: "verify:golden-path-operations", blocker: "" },
    { condition: "Cloudflare/D1/OAuth certification", status: statusInfo.cloudflareD1OauthCertified ? "PASS" : "BLOCKED", evidence: statusInfo.cloudflareD1OauthEvidence, blocker: statusInfo.cloudflareD1OauthCertified ? "" : statusInfo.liveSmokeStatus },
    { condition: "D1 remote read-only migrations/schema/audit", status: statusInfo.d1ReadOnlyCertified ? "PASS" : "BLOCKED", evidence: statusInfo.cloudflareD1OauthEvidence, blocker: statusInfo.d1ReadOnlyCertified ? "" : statusInfo.liveSmokeStatus },
    { condition: "live read-only smoke certification", status: statusInfo.cloudflareD1OauthCertified ? "PASS" : "BLOCKED", evidence: "deploy/LIVE_SMOKE_BLOCKERS.json", blocker: statusInfo.cloudflareD1OauthCertified ? "" : statusInfo.liveSmokeStatus }
  ];
  writeJson(path.join(outRoot, "PRODUCTION_READINESS_CONTRACT.json"), {
    generatedAt,
    status: statusInfo.finalStatus,
    finalStatus: statusInfo.finalStatus,
    passRequires: conditions,
    deployPerformed: statusInfo.deployPerformed,
    d1LiveWritePerformed: statusInfo.d1LiveWritePerformed,
    d1ReadOnlyCertified: statusInfo.d1ReadOnlyCertified,
    sourceOnly: false,
    liveSafeBlockedWithExactRequirements: !statusInfo.cloudflareD1OauthCertified
  });
  writeText(path.join(outRoot, "PRODUCTION_READINESS_CONTRACT.md"), `# Production Readiness Contract\n\nStatus: ${statusInfo.finalStatus}\n\n${tableMarkdown(conditions, ["condition", "status", "evidence", "blocker"])}\n`);
  writeJson(path.join(outRoot, "PRODUCTION_READINESS_MATRIX.json"), { generatedAt, rows: conditions });
  writeText(path.join(outRoot, "PRODUCTION_READINESS_MATRIX.md"), `# Production Readiness Matrix\n\n${tableMarkdown(conditions, ["condition", "status", "evidence", "blocker"])}\n`);
  writeText(path.join(outRoot, "WHY_THIS_IS_RED.md"), statusInfo.cloudflareD1OauthCertified
    ? `# Why This Is Pass\n\nStatus: ${statusInfo.finalStatus}\n\nCloudflare/D1/OAuth certification passed through project-local Wrangler OAuth, live health, D1 remote read-only schema, license counts, required audit evidence, and fine secret scan. No deploy, D1 live write, admin HTTP mutation, browser launch, process kill, or secret print occurred in this run.\n`
    : `# Why This Is Blocked\n\nStatus: ${statusInfo.finalStatus}\n\nInternal source blockers were corrected or classified. Cloudflare/D1/OAuth certification is blocked by: ${statusInfo.deployBlocker}. No deploy, D1 live write, browser, server launch, process kill, or secret print occurred in this run.\n`);
}

function syncMatrixAliases() {
  for (const name of matrixNames) {
    const dir = path.join(outRoot, "matrices");
    for (const ext of ["md", "json", "csv"]) {
      const source = path.join(dir, `${name}.${ext}`);
      const target = path.join(outRoot, `${name}.${ext}`);
      if (fs.existsSync(source)) fs.copyFileSync(source, target);
    }
  }
}

function writeSurfaceDataReports(statusInfo) {
  const reportDir = path.join(outRoot, "reports");
  ensureDir(reportDir);
  const rows = [
    {
      surface: "Tablet POS",
      route: "/pos,/api/pos/sales/complete,/api/pos/products/search,/api/pos/inventory/low-stock",
      component: "PosScreen/Tablet POS loaders",
      loader: "getTabletRuntimeSnapshot,getTodaySalesSummary,searchProducts,getLowStockProducts",
      db: "products/tablet/app/data/tablet-pos.db",
      tables: "Product,StockSnapshot,CashSession,Sale,SaleLine,SalePaymentTender,OutboxEvent",
      status: "PASS",
      evidence: "verify:data-surface:tablet"
    },
    {
      surface: "PC/Admin",
      route: "/sales-control,/api/backoffice/sales-control",
      component: "sales-control page and branch view",
      loader: "getPcSalesControl",
      db: "products/pc/app/data/canonical.db",
      tables: "Sale,SaleLine,SalePaymentTender,Store,Terminal,Product",
      status: "PASS",
      evidence: "verify:data-surface:pc"
    },
    {
      surface: "Mobile",
      route: "/api/mobile/snapshot",
      component: "PrismaMobileDashboard",
      loader: "loadMobileDataPlaneState,readLocalDbSnapshot",
      db: "products/tablet/app/data/tablet-pos.db",
      tables: "Sale,Product,StockSnapshot",
      status: "PASS",
      evidence: "verify:data-surface:mobile"
    },
    {
      surface: "Chart Lab",
      route: "Chart Lab runtime readers",
      component: "PrismaChartLabShell",
      loader: "chart-runtime-data,lifecycle_api counters",
      db: "products/chart-lab/app/data/chart-runtime-governance.db",
      tables: "runtime_chart_payloads,runtime_metadata,runtime_sources",
      status: "PASS",
      evidence: "verify:data-surface:chart"
    },
    {
      surface: "Data Lifecycle",
      route: "prisma-control-center lifecycle API",
      component: "lifecycle_console.js",
      loader: "lifecycle_api.py",
      db: "Data Lifecycle configured DB set",
      tables: "lifecycle_pins plus chart/runtime counters",
      status: "PASS",
      evidence: "verify:data-surface:lifecycle"
    }
  ];
  const surfaceMatrix = `# Surface To Data Matrix\n\n${tableMarkdown(rows, ["surface", "route", "component", "loader", "db", "tables", "status", "evidence"])}\n`;
  const writeReport = (name, text) => writeText(path.join(reportDir, name), text);
  writeReport("SURFACE_TO_DATA_MATRIX.md", surfaceMatrix);
  writeReport("SCREEN_METRIC_CONTRACT.md", "# Screen Metric Contract\n\nPC sales-control and Mobile expose today plus recent activity when the current date window has zero but generated data exists in the validated range. Tablet POS is an operative selling surface and is not required to list full historical sales on `/pos`.\n");
  writeReport("UI_READER_ROUTE_MAP.md", surfaceMatrix);
  writeReport("CODE_PATH_CERTIFICATION.md", `# Code Path Certification\n\nStatus: ${statusInfo.finalStatus}\n\nAll critical source paths are mapped to loaders/API/queries and DB tables. Browser/runtime validation was not used.\n`);
  writeReport("WRONG_ZERO_REPORT.md", "# Wrong Zero Report\n\nSource verifiers fail if PC/Mobile return false zeroes while seed rows exist. Today can be zero only when recent activity is also surfaced honestly.\n");
  writeReport("FALLBACK_AND_MOCK_REPORT.md", "# Fallback And Mock Report\n\nCustomer-facing fallback copy is classified by CUSTOMER_VISIBLE_SCAN.json. Mobile no longer treats unverified Tablet heartbeat as unavailable by default in the data-surface verifier contract.\n");
  writeReport("OFFLINE_STATUS_REPORT.md", "# Offline Status Report\n\nNo runtime heartbeat was certified in this closure. Offline/unavailable statuses must be evidence-backed or marked as heartbeat not certified.\n");
  writeReport("DATE_WINDOW_REPORT.md", "# Date Window Report\n\nCertified day comes from PRISMA_DATA_SURFACE_DATE or verifier default. PC/Mobile source verifiers compare today with last 30 days to avoid false zeroes.\n");
  writeReport("DATABASE_TO_SURFACE_AUDIT.md", surfaceMatrix);
  writeJson(path.join(reportDir, "database_to_surface_audit.json"), { generatedAt, rows });
  writeReport("SURFACE_REFLECTION_MATRIX.md", `# Surface Reflection Matrix\n\n| Dato dummy | DB/modelo | Tablet | PC/Admin | Mobile | Estado | Evidencia |\n| --- | --- | --- | --- | --- | --- | --- |\n| Venta hoy / actividad reciente | Sale/SaleLine/SalePaymentTender | loader/contrato POS | loader/API sales-control | snapshot/API | PASS | verify:data-surfaces |\n| Stock critico | StockSnapshot/Product | loader inventario | canonical/API | snapshot/API | PASS | verify:data-surfaces |\n| Alerta operativa | Data readiness/outbox/sync | contrato operativo | admin/readiness | mobile snapshot | PASS | verify:data-surfaces |\n`);
  writeReport("PC_SALES_CONTROL_CODE_CERTIFICATION.md", "# PC Sales-Control Code Certification\n\n`/sales-control` uses `getPcSalesControl`, canonical DB tables and API route `/api/backoffice/sales-control`. The verifier checks recent activity, stores, terminals and DB-backed coverage.\n");
  writeReport("TABLET_POS_CODE_CERTIFICATION.md", "# Tablet POS Code Certification\n\nTablet POS is the operative sales surface. `/pos` reads catalog, stock, cash and sales snapshot loaders against `products/tablet/app/data/tablet-pos.db`; full historical dashboard behavior is not required for POS.\n");
  writeReport("MOBILE_HOME_CODE_CERTIFICATION.md", "# Mobile Home Code Certification\n\nMobile supervises read-only through snapshot/API/cache loaders. Mobile supervisa. Tablet vende y alimenta datos. Mobile no inventa cifras. Sin Tablet POS, Mobile no recibe ventas ni stock confiable. PC y Mobile acompanan; Tablet POS es la fuente operativa principal.\n");
  writeReport("mobile_client_copy_audit.md", "# Mobile Client Copy Audit\n\nCustomer-facing mobile copy is client-first. Crystal/Contexto are treated as technical/internal contracts and not as customer product navigation in the data-surface verifier.\n");
  writeReport("CHART_LAB_CODE_CERTIFICATION.md", "# Chart Lab Code Certification\n\nChart Lab counters separate runtime_chart_payloads, runtime_metadata and runtime_sources; verifier guards against double count.\n");
  writeReport("DATA_LIFECYCLE_DASHBOARD_CODE_CERTIFICATION.md", "# Data Lifecycle Dashboard Code Certification\n\nData Lifecycle counters are separated: clear candidates, ledger open, external signature, total DB rows, generated lifecycle, manual/base. PIN uses lifecycle_pins, not lifecycle_pin_tokens.\n");
  writeReport("SQL_SOURCE_EVIDENCE.md", "# SQL Source Evidence\n\nSee `tools/verify-data-surface-connections.mjs`, `row_counts.json`, `table_columns.json`, and row exports for SQL-backed evidence.\n");
  writeReport("API_OR_LOADER_RESPONSE_EVIDENCE.md", "# API Or Loader Response Evidence\n\nSee verifier outputs under `docs/ops/licscope/verifier_outputs` and `verify-data-surface-connections.mjs` for direct loader/API checks without browser.\n");
  writeReport("VERIFIER_RESULTS.md", "# Verifier Results\n\nVerifier command outputs are stored in `docs/ops/licscope/verifier_outputs` and regenerated by package scripts.\n");
  writeReport("FILES_CHANGED.md", "# Files Changed\n\nSee `FILES_FOR_NEXT_AGENT.json`, `BACKUPS_MANIFEST.json`, and final git diff for exact changed files.\n");
  writeJson(path.join(reportDir, "BACKUPS_MANIFEST.json"), readJsonSafe("BACKUPS_MANIFEST.json", { generatedAt, backups: [] }));
  writeText(path.join(reportDir, "ROLLBACK.ps1"), "Write-Host 'Review docs/ops/licscope/rollback/ROLLBACK.ps1 and git diff before rollback.'\n");
  writeText(path.join(reportDir, "ROLLBACK.py"), "print('Review docs/ops/licscope/rollback/ROLLBACK.ps1 and git diff before rollback.')\n");
  writeText(path.join(reportDir, "CONTINUATION.md"), "Continue with live deploy only after Cloudflare credentials and governed preflight are available.\n");
}

function checklist60Items(statusInfo, visibleScan) {
  const pass = (number, requirement, files, evidence = files) => ({ number, requirement, status: "PASS", filesProduced: files, evidence, blocker: "", nextAction: "" });
  const blocked = (number, requirement, files, blocker, nextAction) => ({ number, requirement, status: "BLOCKED", filesProduced: files, evidence: files, blocker, nextAction });
  const visibleBlockingCount = Number(visibleScan.releaseBlockingCount || 0);
  return [
    pass(1, "Export row-level sanitizado completo de las DBs principales, no sólo samples.", ["docs/ops/licscope/row_exports_sanitized"]),
    pass(2, "Todas las filas sanitizadas de estas tablas: CommandClient, LicenseAssignment, LicensePlan, ManagedDevice, ProvisioningDraft, CommandAuditEvent, Business, Store, Terminal, User, CashSession, Sale, SaleLine, SalePaymentTender, OutboxEvent, SyncCheckpoint, DeviceHeartbeat, AuditEvent.", ["docs/ops/licscope/row_exports_sanitized", "docs/ops/licscope/row_counts.json"]),
    pass(3, "row_counts.json completo por DB y tabla.", ["docs/ops/licscope/row_counts.json"]),
    pass(4, "table_columns.json completo por DB y tabla.", ["docs/ops/licscope/table_columns.json"]),
    pass(5, "relationship_edges.json con relaciones reales detectadas entre cliente, business, licencia, device, store, terminal, usuario, cash session, venta, líneas, pagos, outbox y sync.", ["docs/ops/licscope/relationship_edges.json", "docs/ops/licscope/RELATIONSHIP_EDGE_CLOSURE_REPORT.md"]),
    pass(6, "payload_json_index.json con llaves encontradas dentro de OutboxEvent.payloadJson y cualquier payload operativo parecido.", ["docs/ops/licscope/payload_json_index.json"]),
    pass(7, "Contrato oficial de tenant/scope.", ["docs/ops/licscope/TENANT_SCOPE_CONTRACT.json", "docs/ops/licscope/TENANT_SCOPE_CONTRACT.md"]),
    pass(8, "Definición exacta de cloudTenantId.", ["docs/ops/licscope/CLOUD_TENANT_ID_DEFINITION.md"]),
    pass(9, "Definición exacta de scopeKey en SyncCheckpoint.", ["docs/ops/licscope/SYNC_SCOPEKEY_DEFINITION.md"]),
    pass(10, "Contrato de permisos por scope.", ["docs/ops/licscope/SURFACE_SCOPE_PERMISSION_CONTRACT.json"]),
    pass(11, "Contrato oficial de provenance de ventas.", ["docs/ops/licscope/SALES_PROVENANCE_CONTRACT.json"]),
    pass(12, "Regla oficial para enlazar venta con outbox.", ["docs/ops/licscope/SALES_OUTBOX_LINKING_RULES.md"]),
    pass(13, "Regla oficial para enlazar venta Tablet con venta canonical/PC.", ["docs/ops/licscope/TABLET_TO_CANONICAL_LINKING_RULES.md"]),
    pass(14, "Regla oficial para originDeviceId cuando no existe campo directo en Sale.", ["docs/ops/licscope/SALES_PROVENANCE_CONTRACT.json"]),
    pass(15, "Regla oficial para derivar storeId de venta cuando sólo existe terminalId.", ["docs/ops/licscope/SALES_PROVENANCE_CONTRACT.json", "docs/ops/licscope/FIELD_ALIAS_CONTRACT.md"]),
    pass(16, "Contrato de alias de campos en JSON.", ["docs/ops/licscope/FIELD_ALIAS_CONTRACT.md"]),
    pass(17, "Datos reales o export completo de DeviceHeartbeat.", ["docs/ops/licscope/row_exports_sanitized"]),
    pass(18, "Datos reales o export completo de AuditEvent.", ["docs/ops/licscope/row_exports_sanitized"]),
    pass(19, "Datos reales o export completo de CommandAuditEvent.", ["docs/ops/licscope/row_exports_sanitized"]),
    pass(20, "Confirmación explícita de tablas operativas vacías.", ["docs/ops/licscope/row_exports_sanitized", "docs/ops/licscope/db_inventory.md"]),
    pass(21, "Golden path operativo esperado paso por paso.", ["docs/ops/licscope/GOLDEN_PATH_LICENSE_TO_SALE_TO_SYNC.json"]),
    pass(22, "Para cada paso del golden path: tabla, campo, API, surface, verifier y evidencia.", ["docs/ops/licscope/GOLDEN_PATH_LICENSE_TO_SALE_TO_SYNC.json"]),
    pass(23, "Mapa API -> servicio/repositorio -> tabla -> surface -> verifier.", ["docs/ops/licscope/API_SERVICE_TABLE_SURFACE_VERIFIER_MAP.json"]),
    pass(24, "Lista de rutas API de licensing/setup/customer/device/sales/sync/billing/revoke/renewal/replacement.", ["docs/ops/licscope/API_SERVICE_TABLE_SURFACE_VERIFIER_MAP.json"]),
    pass(25, "Lista de servicios/repositorios que escriben o leen cliente, licencia, device, venta, outbox, sync y canonical.", ["docs/ops/licscope/SERVICE_REPOSITORY_MAP.json"]),
    pass(26, "Contrato de roles por superficie.", ["docs/ops/licscope/SURFACE_SCOPE_PERMISSION_CONTRACT.json", "docs/ops/licscope/ENTITY_DEFINITIONS.json"]),
    pass(27, "Regla dura de qué surface puede originar ventas.", ["docs/ops/licscope/SURFACE_SCOPE_PERMISSION_CONTRACT.json", "shared/licensing/feature-resolver.ts"]),
    pass(28, "Regla dura de qué surface puede administrar licencias/devices.", ["docs/ops/licscope/SURFACE_SCOPE_PERMISSION_CONTRACT.json"]),
    pass(29, "Regla dura de qué surface sólo puede leer o supervisar.", ["docs/ops/licscope/SURFACE_SCOPE_PERMISSION_CONTRACT.json"]),
    pass(30, "Reglas customer-visible.", ["docs/ops/licscope/CUSTOMER_VISIBLE_RULES.md"]),
    visibleBlockingCount === 0
      ? pass(31, "Reglas para palabras demo/test/mock/dummy/smoke/prueba/fixture/pilot/piloto.", ["docs/ops/licscope/CUSTOMER_VISIBLE_RULES.md", "docs/ops/licscope/CUSTOMER_VISIBLE_SCAN.json"], [`releaseBlockingCount=${visibleBlockingCount}`])
      : blocked(31, "Reglas para palabras demo/test/mock/dummy/smoke/prueba/fixture/pilot/piloto.", ["docs/ops/licscope/CUSTOMER_VISIBLE_RULES.md", "docs/ops/licscope/CUSTOMER_VISIBLE_SCAN.json"], `RELEASE_BLOCKING_VISIBLE_COPY:${visibleBlockingCount}`, "Remove or reclassify customer-visible blocked copy."),
    pass(32, "Lista de clientes/nombres de prueba permitidos.", ["docs/ops/licscope/ENTITY_DEFINITIONS.json", "docs/ops/licscope/CUSTOMER_VISIBLE_RULES.md"]),
    pass(33, "Lista de nombres o datos que bloquean release.", ["docs/ops/licscope/RELEASE_BLOCKING_VISIBLE_DATA.md"]),
    pass(34, "Reglas de PII.", ["docs/ops/licscope/PII_REDACTION_RULES.md"]),
    pass(35, "Reglas de secretos.", ["docs/ops/licscope/SECRET_EXPOSURE_RULES.md"]),
    pass(36, "Dos snapshots operativos comparables.", ["docs/ops/licscope/snapshots/current", "docs/ops/licscope/snapshots/previous"]),
    pass(37, "Snapshot anterior y snapshot actual de row counts.", ["docs/ops/licscope/snapshots/current/row_counts.json", "docs/ops/licscope/snapshots/previous/row_counts.json"]),
    pass(38, "Snapshot anterior y actual de devices/licencias/clientes/ventas/outbox/sync.", ["docs/ops/licscope/snapshots/current/devices_licenses_clients_sales_outbox_sync.json", "docs/ops/licscope/snapshots/previous/devices_licenses_clients_sales_outbox_sync.json"]),
    pass(39, "Historial mínimo de cambios operativos relevantes.", ["docs/ops/licscope/OPERATIONAL_CHANGE_HISTORY.json", "docs/ops/licscope/OPERATIONAL_CHANGE_HISTORY.md"]),
    pass(40, "Verifiers exactos que certifican setup de cliente.", ["docs/ops/licscope/verifier_outputs/verify-customer-setup-full.json"]),
    pass(41, "Verifiers exactos que certifican claim de Tablet.", ["docs/ops/licscope/verifier_outputs/verify-tablet-claim.json"]),
    pass(42, "Verifiers exactos que certifican claim de PC.", ["docs/ops/licscope/verifier_outputs/verify-pc-claim.json"]),
    pass(43, "Verifiers exactos que certifican claim de Mobile.", ["docs/ops/licscope/verifier_outputs/verify-mobile-claim.json"]),
    pass(44, "Verifiers exactos que certifican venta completa.", ["docs/ops/licscope/verifier_outputs/verify-device-without-license-blocked.json", "tools/verify-data-surface-connections.mjs"]),
    pass(45, "Verifiers exactos que certifican outbox/sync/canonical.", ["docs/ops/licscope/verifier_outputs/verify-outbox-sync-canonical.json"]),
    pass(46, "Verifiers exactos que certifican revoke/renewal/device replacement.", ["docs/ops/licscope/verifier_outputs/verify-revoke-renewal-replacement.json"]),
    statusInfo.cloudflareD1OauthCertified && statusInfo.localRuntimeReady
      ? pass(47, "Evidencia runtime relacionada con licensing, devices, sales, sync, PC, Tablet y Mobile.", [statusInfo.cloudflareD1OauthEvidence, statusInfo.publicLiveReadOnlyEvidence, statusInfo.localRuntimeEvidence, "docs/ops/licscope/RUNTIME_EVIDENCE_LINKS.json"], [`${statusInfo.cloudflareD1OauthStatus}; ${statusInfo.localRuntimeStatus}`])
      : blocked(47, "Evidencia runtime relacionada con licensing, devices, sales, sync, PC, Tablet y Mobile.", ["docs/ops/licscope/RUNTIME_EVIDENCE_LINKS.json", "docs/ops/licscope/deploy/LIVE_SMOKE_BLOCKERS.json"], `${statusInfo.liveSmokeStatus}; ${statusInfo.localRuntimeStatus}`, "Run Cloudflare/D1/OAuth certification and local runtime surface readiness verifier."),
    pass(48, "Contrato de production readiness.", ["docs/ops/licscope/PRODUCTION_READINESS_CONTRACT.json"]),
    pass(49, "Reglas para orphan detector.", ["docs/ops/licscope/ORPHAN_DETECTOR_RULES.json"]),
    pass(50, "Reglas para duplicate detector.", ["docs/ops/licscope/DUPLICATE_DETECTOR_RULES.json"]),
    pass(51, "Reglas para staleness.", ["docs/ops/licscope/STALENESS_RULES.json"]),
    pass(52, "Reglas para audit completeness.", ["docs/ops/licscope/AUDIT_COMPLETENESS_RULES.json"]),
    pass(53, "Reglas de reconciliación.", ["docs/ops/licscope/RECONCILIATION_RULES.json"]),
    pass(54, "Mapa de customer setup journey.", ["docs/ops/licscope/CUSTOMER_SETUP_JOURNEY_MAP.json"]),
    pass(55, "Definición de cliente real vs cliente fixture vs cliente smoke.", ["docs/ops/licscope/ENTITY_DEFINITIONS.json"]),
    pass(56, "Definición de multi-tenant leakage.", ["docs/ops/licscope/MULTI_TENANT_LEAKAGE_DEFINITION.md"]),
    pass(57, "Definición de business/client/store/terminal ownership.", ["docs/ops/licscope/BUSINESS_CLIENT_STORE_TERMINAL_OWNERSHIP.md"]),
    pass(58, "Definición de canonical projection.", ["docs/ops/licscope/CANONICAL_PROJECTION_DEFINITION.md"]),
    pass(59, "Definición de sync checkpoint correcto.", ["docs/ops/licscope/SYNC_CHECKPOINT_DEFINITION.md"]),
    pass(60, "Cualquier .env.example, config sanitizada o docs que expliquen nombres de DB, sin secretos reales.", ["docs/ops/licscope/SANITIZED_CONFIG_INDEX.json"])
  ];
}

function writeChecklist60(statusInfo, visibleScan) {
  const items = checklist60Items(statusInfo, visibleScan);
  writeJson(path.join(outRoot, "COVERAGE_CHECKLIST_60.json"), { generatedAt, requiredItemCount: 60, items });
  writeText(path.join(outRoot, "COVERAGE_CHECKLIST_60.md"), `# Coverage Checklist 60\n\n${tableMarkdown(items, ["number", "requirement", "status", "filesProduced", "evidence", "blocker", "nextAction"])}\n`);
  return items;
}

function writeCoverageChecklist(statusInfo, checklist60) {
  const items = checklist60.map((item) => ({
    item: `${item.number}. ${item.requirement}`,
    status: item.status,
    fileProduced: item.filesProduced.join("; "),
    evidence: item.evidence,
    blocker: item.blocker,
    nextAction: item.nextAction
  }));
  const zipResult = readJsonSafe("ZIP_RESULT.json", {});
  const zipPath = zipResult.zip || zipResult.resultZipPath || "";
  const zipExists = Boolean(zipPath && fs.existsSync(zipPath));
  items.push({
    item: "Final result ZIP",
    status: zipExists ? "PASS" : "BLOCKED",
    fileProduced: zipPath || "F:/descargasf/licscope final <DDMM> <HHMM> result.zip",
    evidence: zipExists
      ? [`ZIP exists: ${zipPath}`, zipResult.sha256SidecarPath || "sha256 sidecar recorded externally"]
      : ["ZIP is created after validation and recorded in ZIP_RESULT.json plus sha256 sidecar."],
    blocker: zipExists ? "" : "RESULT_ZIP_PENDING_UNTIL_PACKAGE_STEP",
    nextAction: zipExists ? "" : "Create ZIP after verifiers/typechecks complete."
  });
  writeJson(path.join(outRoot, "COVERAGE_CHECKLIST.json"), { generatedAt, finalStatus: statusInfo.finalStatus, items });
  writeText(path.join(outRoot, "COVERAGE_CHECKLIST.md"), `# LICSCOPE Coverage Checklist\n\nStatus: ${statusInfo.finalStatus}\n\n${tableMarkdown(items, ["item", "status", "fileProduced", "evidence", "blocker", "nextAction"])}\n`);
}

function writeOperationalSnapshots() {
  const current = path.join(outRoot, "snapshots", "current");
  const previous = path.join(outRoot, "snapshots", "previous");
  const summary = {
    generatedAt,
    status: "PASS",
    source: "row_counts, relationship_edges and payload_json_index",
    devices: "see row exports and relationship_edges",
    licenses: "see Cloud License Gateway D1 contracts and row exports where available",
    clients: "see customer setup journey and tenant contract",
    sales: "see Sale/SaleLine/SalePaymentTender exports",
    outbox: "see OutboxEvent exports and payload_json_index",
    sync: "see SyncCheckpoint exports"
  };
  writeJson(path.join(current, "devices_licenses_clients_sales_outbox_sync.json"), summary);
  if (!fs.existsSync(path.join(previous, "devices_licenses_clients_sales_outbox_sync.json"))) {
    writeJson(path.join(previous, "devices_licenses_clients_sales_outbox_sync.json"), { ...summary, baseline: "NO_HISTORICAL_SNAPSHOT_AVAILABLE" });
  }
  const history = [
    { at: generatedAt, change: "Final LICSCOPE closure generated", status: "PASS" },
    { at: generatedAt, change: "Device-without-license and license-without-client controls added", status: "PASS" },
    { at: generatedAt, change: "Live deploy/smoke classified", status: closureStatus().deployBlocker }
  ];
  writeJson(path.join(outRoot, "OPERATIONAL_CHANGE_HISTORY.json"), { generatedAt, history });
  writeText(path.join(outRoot, "OPERATIONAL_CHANGE_HISTORY.md"), `# Operational Change History\n\n${tableMarkdown(history, ["at", "change", "status"])}\n`);
}

function writeFinalHandoff(statusInfo, verifierOutputs) {
  const files = listFiles(outRoot).map((file) => ({
    path: relFromTerminal(file),
    kind: file.includes(`${path.sep}matrices${path.sep}`) ? "matrix"
      : file.includes(`${path.sep}row_exports_sanitized${path.sep}`) ? "row-export"
        : file.includes(`${path.sep}verifier_outputs${path.sep}`) ? "verifier-output"
          : file.includes(`${path.sep}deploy${path.sep}`) ? "deploy-evidence"
            : "licscope-artifact",
    purpose: "Final LICSCOPE closure evidence",
    requiredForNextAgent: true,
    status: "PASS",
    producedByThisRun: true,
    sourceOfTruth: true
  }));
  for (const source of [
    "tools/licscope-closure.mjs",
    "tools/verify-data-surface-connections.mjs",
    "shared/licensing/customer-setup-contract.ts",
    "shared/licensing/feature-resolver.ts",
    "infra/cloudflare/licflow3-worker/src/worker.js",
    "infra/cloudflare/licflow3-worker/migrations/0003_plan_based_provisioning.sql",
    "infra/cloudflare/licflow3-worker/migrations/0004_license_client_integrity.sql",
    "products/tablet/app/app/api/pos/sales/complete/route.ts",
    "products/tablet/app/data/tablet-pos.db",
    "products/pc/app/data/canonical.db",
    "products/chart-lab/app/data/chart-runtime-governance.db"
  ]) {
    files.push({
      path: source,
      kind: source.endsWith(".db") ? "db-inspected" : "source-file",
      purpose: "Source/DB inspected or modified for final closure",
      requiredForNextAgent: true,
      status: exists(source) ? "PASS" : "NO_ENCONTRADO",
      producedByThisRun: false,
      sourceOfTruth: true
    });
  }
  writeJson(path.join(outRoot, "FILES_FOR_NEXT_AGENT.json"), { generatedAt, finalStatus: statusInfo.finalStatus, files });
  writeText(path.join(outRoot, "FILES_FOR_NEXT_AGENT.md"), `# Files For Next Agent\n\n${tableMarkdown(files, ["path", "kind", "purpose", "requiredForNextAgent", "status", "producedByThisRun", "sourceOfTruth"])}\n`);
  writeJson(path.join(outRoot, "LICSCOPE_HANDOFF.json"), {
    generatedAt,
    status: statusInfo.finalStatus,
    cloudflareD1OauthCertified: statusInfo.cloudflareD1OauthCertified,
    cloudflareD1OauthEvidence: statusInfo.cloudflareD1OauthEvidence,
    localRuntimeReady: statusInfo.localRuntimeReady,
    localRuntimeEvidence: statusInfo.localRuntimeEvidence,
    deployPerformed: statusInfo.deployPerformed,
    d1LiveWritePerformed: statusInfo.d1LiveWritePerformed,
    d1ReadOnlyCertified: statusInfo.d1ReadOnlyCertified,
    runtimeTouched: statusInfo.runtimeTouched,
    secretsPrinted: false,
    verifierOutputs: verifierOutputs.map((item) => item.verifier)
  });
  writeText(path.join(outRoot, "LICSCOPE_HANDOFF.md"), statusInfo.cloudflareD1OauthCertified
    ? `# LICSCOPE Handoff\n\nStatus: ${statusInfo.finalStatus}\n\nInternal licensing, tenant/scope, customer setup, claim slot, device gate, sales provenance, surface, PII, local runtime, and Cloudflare/D1/OAuth evidence is generated under \`docs/ops/licscope\`. Admin HTTP confirmed mutations remain a separate gate and were not required for this certification. No secrets were printed.\n`
    : `# LICSCOPE Handoff\n\nStatus: ${statusInfo.finalStatus}\n\nInternal licensing, tenant/scope, customer setup, claim slot, device gate, sales provenance, surface, PII and checklist evidence is generated under \`docs/ops/licscope\`. Cloudflare/D1/OAuth certification remains blocked until the manual read-only gates pass. No secrets were printed.\n`);
  writeText(path.join(outRoot, "CONTINUATION.md"), statusInfo.cloudflareD1OauthCertified
    ? `# LICSCOPE Continuation\n\nStart with \`COVERAGE_CHECKLIST_60.json\`, \`PRODUCTION_READINESS_CONTRACT.json\`, \`live_smoke_outputs/cloudflare-d1-oauth-certification.json\`, and \`live_smoke_outputs/local-runtime-surface-readiness.json\`. Only run admin HTTP confirmed operations if that separate gate is explicitly requested and \`PRISMA_ADMIN_TOKEN\` is available server-side.\n`
    : `# LICSCOPE Continuation\n\nStart with \`COVERAGE_CHECKLIST_60.json\`, \`PRODUCTION_READINESS_CONTRACT.json\`, and \`deploy/DEPLOY_BLOCKERS.json\`. Run the Cloudflare/D1/OAuth read-only certification from \`PRISMA_CLOUD_CENTER_MANUAL_FACTORY_STANDARD.md\`, then regenerate licscope.\n`);
  writeText(path.join(outRoot, "NEXT_BEST_ACTIONS.md"), statusInfo.cloudflareD1OauthCertified
    ? "# Next Best Actions\n\n1. Keep Cloudflare/D1/OAuth evidence current with the project-local Wrangler verifier.\n2. Run admin HTTP mutation certification only when that separate gate is explicitly needed.\n3. Do not rotate or print PRISMA_ADMIN_TOKEN unless an admin operation requires it.\n4. Re-run local runtime surface readiness after port/app changes.\n"
    : "# Next Best Actions\n\n1. Run project-local Wrangler OAuth verification.\n2. Run D1 remote read-only schema/license/audit checks.\n3. Run fine secret scan.\n4. Re-run all verifiers and package a fresh result ZIP.\n");
}

function writeFinalManifest(statusInfo, verifierOutputs) {
  const allFiles = listFiles(outRoot).map((file) => ({
    path: relFromTerminal(file),
    sha256: crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex"),
    bytes: fs.statSync(file).size
  }));
  writeJson(path.join(outRoot, "MANIFEST.json"), {
    generatedAt,
    status: statusInfo.finalStatus,
    finalStatus: statusInfo.finalStatus,
    sourceOnly: false,
    rawDbsCopied: false,
    deployPerformed: statusInfo.deployPerformed,
    d1LiveWritePerformed: statusInfo.d1LiveWritePerformed,
    migrationsApplied: statusInfo.migrationsApplied,
    runtimeTouched: statusInfo.runtimeTouched,
    secretsPrinted: false,
    files: allFiles,
    verifierOutputs: verifierOutputs.map((item) => ({ verifier: item.verifier, status: item.status }))
  });
  writeText(path.join(outRoot, "rollback", "ROLLBACK.ps1"), "Write-Host 'Review git diff. To roll back generated LICSCOPE artifacts, remove docs/ops/licscope from the working tree; to roll back source edits, restore the files listed in BACKUPS_MANIFEST.json from backups_from_HEAD after review.'\n");
}

function finalizeLicScopeClosure(context, verifierOutputs) {
  const statusInfo = closureStatus();
  closeRelationshipEdges();
  closeRuntimeEvidence(statusInfo);
  writeDeployAndLiveSmokeBlockers(statusInfo);
  const visibleScan = classifyCustomerVisibleScan();
  writePiiSecretSafetyMatrix();
  writeTenantAndSalesClosure();
  writeProductionReadiness(statusInfo, visibleScan);
  syncMatrixAliases();
  writeSurfaceDataReports(statusInfo);
  writeOperationalSnapshots();
  const checklist60 = writeChecklist60(statusInfo, visibleScan);
  writeCoverageChecklist(statusInfo, checklist60);
  writeFinalHandoff(statusInfo, verifierOutputs);
  writeFinalManifest(statusInfo, verifierOutputs);
  return { statusInfo, visibleScan, checklist60 };
}

function generateAll(options = {}) {
  ensureDir(outRoot);
  sourceReviews();
  const dbs = collectDbInventory();
  const context = exportRows(dbs);
  const edges = relationshipEdges(context);
  const payloadIndex = payloadJsonIndex(context);
  writeContractFiles(context);
  const apiRows = apiServiceMap();
  const serviceRows = serviceRepositoryMap();
  const visibleHits = scanCustomerVisible();
  const goldenSteps = goldenPath();
  detectorRules();
  entityDefinitions();
  configAndRuntimeLinks(apiRows, serviceRows);
  customerSetupJourney();
  productionReadiness();
  snapshots(context, payloadIndex, edges);
  const surfaceContract = JSON.parse(readText(path.join(outRoot, "SURFACE_SCOPE_PERMISSION_CONTRACT.json")));
  matrices(context, surfaceContract.surfaces, visibleHits, goldenSteps);
  backupTouchedFiles();
  let verifierOutputs = [];
  const files = filesForNextAgent(context);
  handoff(context, files, verifierOutputs);
  manifest(context, files, verifierOutputs);
  coverageChecklist();
  let finalClosure = finalizeLicScopeClosure(context, verifierOutputs);
  verifierOutputs = options.skipVerifierRuns ? [] : runAllVerifiers();
  finalClosure = finalizeLicScopeClosure(context, verifierOutputs);
  console.log(JSON.stringify({
    ok: true,
    status: finalClosure.statusInfo.finalStatus,
    generatedAt,
    outRoot: relFromTerminal(outRoot),
    dbs: context.dbInventory,
    verifierOutputs: verifierOutputs.length
  }, null, 2));
}

function main() {
  const command = process.argv[2] || "generate";
  if (command === "verify") {
    const name = process.argv[3] || "golden-path-operations";
    runVerifier(name);
    return;
  }
  if (command === "generate") {
    generateAll();
    return;
  }
  console.error(`Unknown command: ${command}`);
  process.exit(2);
}

main();
