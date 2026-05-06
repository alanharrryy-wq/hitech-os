#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const failures = [];

function rel(...parts) {
  return path.join(root, ...parts);
}

function read(...parts) {
  const full = rel(...parts);
  if (!fs.existsSync(full)) {
    failures.push(`Missing file: ${path.relative(root, full)}`);
    return "";
  }
  return fs.readFileSync(full, "utf8");
}

function readJson(...parts) {
  const full = rel(...parts);
  if (!fs.existsSync(full)) {
    failures.push(`Missing JSON file: ${path.relative(root, full)}`);
    return {};
  }
  return JSON.parse(fs.readFileSync(full, "utf8"));
}

function assert(condition, message) {
  if (!condition) failures.push(message);
}

function assertIncludes(source, markers, label) {
  for (const marker of markers) {
    assert(source.includes(marker), `${label} missing marker: ${marker}`);
  }
}

const contract = readJson("shared", "contracts", "security-audit-permissions.v1.json");
assert(contract.contractId === "PRISMA_SECURITY_AUDIT_PERMISSIONS_01", "Security contract id drift.");
assertIncludes(JSON.stringify(contract), [
  "tablet_operator",
  "tablet_supervisor",
  "pc_backoffice",
  "pc_admin",
  "pos.sale.complete",
  "export.local.create",
  "sync.ingest.write",
  "sync.conflict.resolve",
  "actorId",
  "permission",
  "offlineAllowed"
], "security-audit-permissions.v1.json");

const requiredAuditFields = ["actorId", "role", "terminalId", "businessId", "action", "permission", "entityType", "entityId", "before", "after", "createdAt"];
for (const field of requiredAuditFields) {
  assert(contract.auditFields?.includes(field), `Security contract auditFields missing ${field}.`);
}

const tabletAudit = read("products", "tablet", "app", "src", "server", "pos-security", "audit.ts");
assertIncludes(tabletAudit, [
  "TABLET_SENSITIVE_ACTION_PERMISSIONS",
  '"pos.sale.complete"',
  '"export.local.create"',
  "tabletAuditMeta",
  "tabletAuditHeaders",
  "readTabletAuditActor",
  "offlineAllowed: true"
], "Tablet audit helper");

const saleRoute = read("products", "tablet", "app", "app", "api", "pos", "sales", "complete", "route.ts");
assertIncludes(saleRoute, [
  "tabletAuditMeta",
  '"pos.sale.complete"',
  "actorId: sale.cashier",
  "entityType: \"Sale\"",
  "audit"
], "Tablet sale complete route");

const posExport = read("products", "tablet", "app", "src", "server", "pos-export", "index.ts");
assertIncludes(posExport, [
  "extraHeaders",
  "...extraHeaders"
], "Tablet CSV export response");

for (const exportRoute of [
  ["sales-today", "SalesTodayExport"],
  ["events", "OutboxEventExport"],
  ["inventory-movements", "InventoryMovementExport"]
]) {
  const source = read("products", "tablet", "app", "app", "api", "pos", "export", exportRoute[0], "route.ts");
  assertIncludes(source, [
    "readTabletAuditActor",
    "tabletAuditMeta",
    "tabletAuditHeaders",
    '"export.local.create"',
    exportRoute[1],
    "csvResponse(result.filename, result.csv, tabletAuditHeaders(audit))",
    "audit"
  ], `Tablet ${exportRoute[0]} export route`);
}

const pcAudit = read("products", "pc", "app", "src", "lib", "backoffice", "security-audit.ts");
assertIncludes(pcAudit, [
  "BACKOFFICE_SENSITIVE_ACTION_PERMISSIONS",
  '"sync.ingest.persist"',
  '"sync.conflict.resolve"',
  "readBackofficeAuditActor",
  "backofficeAuditMeta",
  "offlineAllowed: false"
], "PC audit helper");

const pcIngest = read("products", "pc", "app", "app", "api", "backoffice", "sync", "ingest", "route.ts");
assertIncludes(pcIngest, [
  "readBackofficeAuditActor",
  "backofficeAuditMeta",
  '"sync.ingest.persist"',
  'permission: "sync.ingest.write"',
  "entityType: \"OutboxEvent\"",
  "audit"
], "PC sync ingest route");

const pcConflicts = read("products", "pc", "app", "app", "api", "backoffice", "sync", "conflicts", "route.ts");
assertIncludes(pcConflicts, [
  "readBackofficeAuditActor",
  "backofficeAuditMeta",
  '"sync.conflict.resolve"',
  'mode: "read_only_catalog"',
  'permission: "sync.conflict.resolve"',
  "audit"
], "PC sync conflicts route");

for (const docPath of [
  ["docs", "contracts", "PERMISSIONS_AUDIT_CONTRACT.md"],
  ["shared", "contracts", "permission-contract.md"],
  ["products", "tablet", "app", "docs", "pos", "TABLET_POS_PERMISSIONS.md"]
]) {
  const doc = read(...docPath);
  assertIncludes(doc, [
    "shared/contracts/security-audit-permissions.v1.json",
    "tablet_operator",
    "pc_backoffice",
    "actorId",
    "permission"
  ], path.join(...docPath));
}

const eventFactory = read("products", "tablet", "app", "src", "server", "pos-engine", "event-factory.ts");
assertIncludes(eventFactory, [
  "actorId: context.actorId",
  "schemaVersion"
], "Tablet event envelope");

const pcEventContract = read("products", "pc", "app", "src", "lib", "backoffice", "event-contract.ts");
assertIncludes(pcEventContract, [
  '"actorId"',
  "actorId debe ser texto"
], "PC event contract actor requirement");

if (failures.length) {
  console.error("PRISMA_SECURITY_AUDIT_PERMISSIONS_01 failed");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PRISMA_SECURITY_AUDIT_PERMISSIONS_01 passed");
console.log(JSON.stringify({
  sourceOfTruth: "shared/contracts/security-audit-permissions.v1.json",
  roles: contract.roles?.length ?? 0,
  tabletSensitiveActions: Object.keys(contract.sensitiveActions?.tablet ?? {}).length,
  pcSensitiveActions: Object.keys(contract.sensitiveActions?.pc ?? {}).length,
  auditFields: contract.auditFields?.length ?? 0
}, null, 2));
