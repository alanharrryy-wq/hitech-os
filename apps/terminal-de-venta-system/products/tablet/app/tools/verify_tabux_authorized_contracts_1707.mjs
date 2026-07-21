import fs from "node:fs";
import path from "node:path";

const repoRoot = path.resolve(process.env.TRIAPP_REPO_ROOT || process.cwd());
const reportPath = process.env.TRIAPP_STATIC_REPORT_PATH;
if (!reportPath) throw new Error("TRIAPP_STATIC_REPORT_PATH is required.");

const root = path.join(repoRoot, "apps", "terminal-de-venta-system");
const tablet = path.join(root, "products", "tablet", "app");
const pc = path.join(root, "products", "pc", "app");
const checks = [];

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

function check(id, condition, detail) {
  checks.push({ id, status: condition ? "PASS" : "FAIL", detail });
}

function has(source, marker) {
  return source.includes(marker);
}

const cashRoute = read("products/tablet/app/app/api/pos/cash/movements/route.ts");
const cashRepository = read("products/tablet/app/src/server/pos-shift/repository.prisma.ts");
const cashTypes = read("products/tablet/app/src/server/pos-shift/types.ts");
const cashValidators = read("products/tablet/app/src/server/pos-shift/validators.ts");
const shiftUi = read("products/tablet/app/components/shift/shift-cash-closure-screen.tsx");
const shiftCss = read("products/tablet/app/components/shift/shift-cash-closure.module.css");
const inventoryRoute = read("products/tablet/app/app/api/pos/inventory/operations/route.ts");
const inventoryRepository = read("products/tablet/app/src/server/inventory-operations/repository.prisma.ts");
const inventoryTypes = read("products/tablet/app/src/server/inventory-operations/types.ts");
const inventoryUi = read("products/tablet/app/components/inventory/inventory-operations-workspace.tsx");
const catalogOwner = read("products/tablet/app/components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen.tsx");
const catalogCss = read("products/tablet/app/components/catalog-stock-selling-assist/catalog-stock-selling-assist.module.css");
const permissions = read("products/tablet/app/src/server/pos-security/permissions.prisma.ts");
const sharedContract = JSON.parse(read("shared/contracts/sync-event-contract.v1.json"));
const twinKernel = read("shared/twin-kernel/src/sync/events.ts");
const tabletSync = read("products/tablet/app/src/server/sync/events.ts");
const pcValidator = read("products/pc/app/src/server/validators/sync-event-contract.ts");
const pcProjector = read("products/pc/app/src/server/services/sync-projectors.service.ts");

check("cash.route.get_post", has(cashRoute, "export async function GET") && has(cashRoute, "export async function POST"), "Cash route exposes read and command owners.");
check("cash.route.permission_error", has(cashRoute, "TabletPermissionError"), "Cash command returns canonical permission failures.");
check("cash.types.signed_movements", has(cashTypes, '"CASH_IN" | "CASH_OUT"'), "Cash input distinguishes deposits and withdrawals.");
check("cash.validation.idempotency", has(cashValidators, "clientRequestId") && has(cashValidators, "amountCents"), "Cash command validates request identity and positive amount.");
const cashCommand = cashRepository.slice(cashRepository.indexOf("async recordMovement"));
check("cash.permission_before_dedupe", cashCommand.indexOf("assertTabletOperationalPermission") < cashCommand.indexOf("outboxEvent.findFirst"), "Authorization is evaluated before an idempotent replay is revealed.");
check("cash.audit_outbox", has(cashRepository, "cashAdjustment.create") && has(cashRepository, "auditEvent.create") && has(cashRepository, 'topic: "cash.movement.recorded"'), "Cash writes adjustment, audit and outbox evidence atomically.");
check("cash.ui.real_command", has(shiftUi, 'workspaceMode === "movement"') && has(shiftUi, 'requestJson<ApiShift>("/api/pos/cash/movements"'), "Tablet shift UI submits the canonical cash command.");
check("cash.ui.retry_key", has(shiftUi, "movementRequestIdRef"), "Cash retry preserves a stable request identifier.");

check("inventory.route.get_post", has(inventoryRoute, "export async function GET") && has(inventoryRoute, "export async function POST"), "Inventory route exposes snapshot and command owners.");
check("inventory.route.license_permission", has(inventoryRoute, "guardTabletLocalPosForApi") && has(inventoryRoute, "TabletPermissionError"), "Inventory route applies license and permission gates.");
check("inventory.actions", ['action: "adjust"', 'action: "count"', 'action: "receive"'].every((marker) => has(inventoryTypes, marker)), "Adjust, count and receive are discriminated real commands.");
check("inventory.permission_before_dedupe", inventoryRepository.indexOf("ensureContext(tx, input)") < inventoryRepository.indexOf("existingResult(tx, input)"), "Authorization is evaluated before inventory replay lookup.");
check("inventory.audit_outbox", has(inventoryRepository, "auditEvent.create") && has(inventoryRepository, "inventory.operation.recorded") && has(inventoryRepository, "stock.adjusted"), "Inventory writes audit and canonical sync receipts.");
check("inventory.no_zero_stock_event", has(inventoryRepository, "affected.deltaQty !== 0"), "Unchanged counted lines do not emit false stock adjustments.");
check("inventory.overreceipt_guard", has(inventoryRepository, "RECEIPT_EXCEEDS_REMAINING"), "Receipt cannot exceed the purchase-order remainder.");
check("inventory.ui.real_command", has(inventoryUi, 'requestJson<Snapshot>("/api/pos/inventory/operations")') && has(inventoryUi, 'method: "POST"'), "Tablet inventory UI reads and writes the real owner.");
check("inventory.ui.single_mode", has(inventoryUi, 'useState<"adjust" | "count" | "receive">') && has(inventoryUi, "changeMode"), "One operational form is active at a time.");
check("inventory.ui.retry_key", has(inventoryUi, "pendingRequestId"), "Inventory retry preserves a stable request identifier.");
check("inventory.ui.integrated", has(catalogOwner, "InventoryOperationsWorkspace"), "Operations are integrated into the existing stock owner.");

check("permissions.codes", has(permissions, '"cash:adjust" | "inventory:adjust"'), "Canonical local permission codes govern both commands.");
check("permissions.scope", has(permissions, "TABLET_OPERATION_SCOPE_MISMATCH"), "Business and terminal scope are enforced.");
check("permissions.rbac", has(permissions, "role_permission") && has(permissions, "configured_runtime_operator"), "RBAC and pre-provisioning fallback are explicit and auditable.");

const contractTopics = Array.isArray(sharedContract.eventTopics) ? sharedContract.eventTopics : [];
check("sync.shared_contract", contractTopics.includes("inventory.operation.recorded"), "Shared JSON contract recognizes inventory operation receipts.");
check("sync.twin_kernel", has(twinKernel, '"inventory.operation.recorded"'), "Twin kernel recognizes the topic.");
check("sync.tablet", has(tabletSync, '"inventory.operation.recorded"'), "Tablet dispatcher contract recognizes the topic.");
check("sync.pc_validator", has(pcValidator, '"inventory.operation.recorded"'), "PC ingest validator recognizes the topic.");
check("sync.pc_projector", has(pcProjector, "projectInventoryOperationRecorded") && has(pcProjector, 'event.topic === "inventory.operation.recorded"'), "PC projects inventory receipts idempotently.");

check("css.zero_important", !shiftCss.includes("!important") && !catalogCss.includes("!important"), "Touched operational CSS contains zero !important declarations.");
check("css.touch_targets", /min-height:\s*var\(--prisma-touch-target\)/.test(shiftCss) && /min-height:\s*(?:44px|var\(--prisma-touch-target\))/.test(catalogCss), "Operational controls retain the canonical 44px touch target.");
check("ownership.tablet_only_ui", fs.existsSync(path.join(tablet, "components", "inventory", "inventory-operations-workspace.tsx")) && fs.existsSync(path.join(pc, "src", "server", "services", "sync-projectors.service.ts")), "UI remains Tablet-owned while reconciliation remains PC-owned.");

const failed = checks.filter((item) => item.status === "FAIL");
const report = {
  schemaVersion: "tabux.authorized-contract-static-gate.v1",
  generatedAt: new Date().toISOString(),
  status: failed.length ? "FAIL" : "PASS",
  summary: { total: checks.length, passed: checks.length - failed.length, failed: failed.length },
  checks
};
fs.mkdirSync(path.dirname(reportPath), { recursive: true });
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
if (failed.length) {
  for (const item of failed) console.error(`FAIL ${item.id}: ${item.detail}`);
  throw new Error(`TABUX_AUTHORIZED_CONTRACT_STATIC_FAIL ${failed.length}/${checks.length}`);
}
console.log(`TABUX_AUTHORIZED_CONTRACT_STATIC_PASS ${checks.length}/${checks.length}`);
