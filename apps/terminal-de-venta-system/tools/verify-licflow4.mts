import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

type JsonObject = Record<string, unknown>;

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const terminalRoot = path.resolve(scriptDir, "..");
const mode = String(process.argv[2] ?? "").trim();
const cloudCtrRoot = "Prisma Cloud Ctr";

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

function readText(relativePath: string): string {
  return fs.readFileSync(path.join(terminalRoot, relativePath), "utf8");
}

function readJson<T = JsonObject>(relativePath: string): T {
  return JSON.parse(readText(relativePath)) as T;
}

function walk(root: string, extensions: string[]): string[] {
  const absoluteRoot = path.join(terminalRoot, root);
  if (!fs.existsSync(absoluteRoot)) return [];
  const out: string[] = [];
  for (const entry of fs.readdirSync(absoluteRoot, { withFileTypes: true })) {
    const filePath = path.join(absoluteRoot, entry.name);
    if (entry.isDirectory()) out.push(...walk(path.relative(terminalRoot, filePath), extensions));
    else if (extensions.includes(path.extname(entry.name).toLowerCase())) out.push(filePath);
  }
  return out;
}

function rel(file: string): string {
  return path.relative(terminalRoot, file).replace(/\\/g, "/");
}

function pass(name: string, evidence: JsonObject): void {
  console.log(JSON.stringify({ ok: true, verifier: name, generatedAt: new Date().toISOString(), ...evidence }, null, 2));
}

function cloudCtr(relativePath: string): string {
  return `${cloudCtrRoot}/${relativePath}`;
}

function modeAdminBridge(): void {
  const server = readText(cloudCtr("internal/py/prisma_unified_lab_v3.py"));
  const bridge = readText(cloudCtr("internal/py/licflow4_admin_bridge.py"));
  const ui = readText(cloudCtr("internal/web/cloud_command_center.js"));
  const config = readJson<{ endpoints?: JsonObject; licflow3?: JsonObject }>(cloudCtr("internal/config/cloud_saas.json"));
  for (const route of [
    "/api/licflow4/bridge/status",
    "/api/licflow4/bridge/activate",
    "/api/licflow4/bridge/refresh",
    "/api/licflow4/bridge/revoke"
  ]) {
    assert(server.includes(route) || bridge.includes(route) || ui.includes(route), `Missing LICFLOW4 bridge route ${route}`);
  }
  assert(server.includes("import licflow4_admin_bridge"), "Local server does not import LICFLOW4 admin bridge.");
  assert(server.includes("licflow4_admin_bridge.diagnostics_payload()"), "Diagnostics do not include LICFLOW4 bridge payload.");
  assert(server.includes("is_local_operator_request()"), "Mutating bridge routes must enforce local operator requests.");
  assert(bridge.includes("X-Prisma-Admin-Token"), "Backend bridge must send admin token server-side.");
  assert(bridge.includes("_read_admin_token_for_bridge()"), "Backend bridge must read token only inside bridge action path.");
  assert(ui.includes("LICFLOW4 Admin Bridge"), "Cloud Command Center does not render LICFLOW4 bridge status.");
  for (const action of ["activate", "refresh", "revoke"]) {
    assert(ui.includes(`bridgeForm("${action}"`), `Cloud Command Center lacks ${action} bridge form.`);
  }
  assert(ui.includes("licflow4-dryrun-${action}") && ui.includes("licflow4-run-${action}"), "Cloud Command Center lacks protected LICFLOW4 action templates.");
  assert(config.endpoints?.licenseActivate === "/api/licenses/activate", "LICFLOW3 activate endpoint changed unexpectedly.");
  pass("verify:licflow4:admin-bridge", {
    root: cloudCtrRoot,
    routes: ["/api/licflow4/bridge/status", "/api/licflow4/bridge/activate", "/api/licflow4/bridge/refresh", "/api/licflow4/bridge/revoke"],
    worker: config.licflow3?.worker,
    d1: config.licflow3?.d1
  });
}

function modeNoTokenFrontend(): void {
  const files = walk(cloudCtrRoot, [".html", ".js", ".css"]);
  const forbidden = [
    "X-Prisma-Admin-Token",
    "Authorization: Bearer",
    "x-admin-token",
    "ADMIN_TOKEN.txt",
    "localStorage.setItem('ADMIN_TOKEN",
    "localStorage.setItem(\"ADMIN_TOKEN",
    "sessionStorage.setItem('ADMIN_TOKEN",
    "sessionStorage.setItem(\"ADMIN_TOKEN"
  ];
  const hits: Array<{ file: string; token: string }> = [];
  for (const file of files) {
    const text = fs.readFileSync(file, "utf8");
    for (const token of forbidden) {
      if (text.includes(token)) hits.push({ file: rel(file), token });
    }
  }
  assert(hits.length === 0, `Frontend exposes forbidden token material: ${JSON.stringify(hits)}`);
  pass("verify:licflow4:no-token-frontend", { scannedFiles: files.map(rel), forbiddenHits: hits });
}

function modeConfirmations(): void {
  const bridge = readText(cloudCtr("internal/py/licflow4_admin_bridge.py"));
  const ui = readText(cloudCtr("internal/web/cloud_command_center.js"));
  for (const token of [
    "confirmAdminLicenseAction",
    "ADMIN_ACTION_CONFIRMATION_REQUIRED",
    "confirmRevoke",
    "REVOKE_LICENSE",
    "REVOKE_CONFIRMATION_REQUIRED",
    "INVALID_ADMIN_ACTION_PAYLOAD",
    "DRY_RUN_READY",
    "ADMIN_TOKEN_NOT_CONFIGURED",
    "UPSTREAM_ADMIN_TOKEN_REQUIRED"
  ]) {
    assert(bridge.includes(token) || ui.includes(token), `Missing LICFLOW4 confirmation token ${token}`);
  }
  assert(ui.includes("data-bridge-confirm") && ui.includes("bridge-confirm-${esc(action)}"), "UI lacks explicit action confirmations.");
  assert(ui.includes("bridge-phrase-revoke"), "UI lacks revoke phrase field.");
  pass("verify:licflow4:confirmations", {
    confirmationField: "confirmAdminLicenseAction",
    revokePhrase: "REVOKE_LICENSE",
    dryRunOnlyCheck: true
  });
}

function modeDiagnosticsSanitized(): void {
  const server = readText(cloudCtr("internal/py/prisma_unified_lab_v3.py"));
  const bridge = readText(cloudCtr("internal/py/licflow4_admin_bridge.py"));
  assert(server.includes('"licflow4AdminBridge": licflow4_admin_bridge.diagnostics_payload()'), "Diagnostics export does not include LICFLOW4 bridge summary.");
  assert(bridge.includes('"secretsExposed": False'), "Bridge diagnostics must assert secretsExposed false.");
  assert(!bridge.includes('"token": token'), "Bridge must not serialize raw token.");
  assert(!server.includes("ADMIN_TOKEN.txt"), "Server diagnostics must not expose token file names.");
  pass("verify:licflow4:diagnostics-sanitized", {
    diagnostics: "licflow4AdminBridge",
    secretsExposed: false
  });
}

function modeNoAutorunMutations(): void {
  const ui = readText(cloudCtr("internal/web/cloud_command_center.js"));
  const server = readText(cloudCtr("internal/py/prisma_unified_lab_v3.py"));
  const loadAllStart = ui.indexOf("async function loadAll()");
  const loadAllEnd = ui.indexOf("async function postAction", loadAllStart);
  const loadAll = loadAllStart >= 0 && loadAllEnd > loadAllStart ? ui.slice(loadAllStart, loadAllEnd) : "";
  assert(loadAll.includes("/api/licflow4/bridge/status"), "UI load path must fetch bridge status.");
  for (const action of ["activate", "refresh", "revoke"]) {
    assert(!loadAll.includes(`/api/licflow4/bridge/${action}`), `UI load path must not auto-run ${action}.`);
  }
  const forbiddenUiCommands = ["wrangler deploy", "d1 execute", "d1 export", "cloudflared tunnel", "cloudflare tunnel"];
  for (const forbidden of forbiddenUiCommands) assert(!ui.includes(forbidden), `Forbidden operational command present in UI: ${forbidden}`);
  const serverCommandPattern = /subprocess\.[\s\S]{0,400}(wrangler|cloudflared|\bd1\b)|os\.system\([\s\S]{0,400}(wrangler|cloudflared|\bd1\b)/i;
  assert(!serverCommandPattern.test(server), "Server contains an auto-run Cloudflare/D1 command path.");
  pass("verify:licflow4:no-autorun-mutations", {
    statusOnLoad: true,
    activateOnLoad: false,
    refreshOnLoad: false,
    revokeOnLoad: false,
    deployPerformed: false,
    d1OperationPerformed: false
  });
}

const modes: Record<string, () => void> = {
  "admin-bridge": modeAdminBridge,
  "no-token-frontend": modeNoTokenFrontend,
  confirmations: modeConfirmations,
  "diagnostics-sanitized": modeDiagnosticsSanitized,
  "no-autorun-mutations": modeNoAutorunMutations
};

const run = modes[mode];
if (!run) {
  console.error(`Unknown mode "${mode}". Expected one of: ${Object.keys(modes).join(", ")}`);
  process.exit(2);
}

try {
  run();
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
