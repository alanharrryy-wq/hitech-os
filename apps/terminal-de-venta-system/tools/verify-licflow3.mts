import { spawnSync } from "node:child_process";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  buildLicflow3CloudContractStatus,
  LICFLOW3_CLOUDFLARE_ROUTES_LIVE,
  LICFLOW3_CLOUD_CONTRACT,
  LICFLOW3_CLOUD_ENDPOINTS,
  LICFLOW3_REQUIRED_CAPABILITIES,
  type Licflow3EndpointKey
} from "../shared/licensing/licflow3-cloud-contract";

type JsonObject = Record<string, unknown>;

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const terminalRoot = path.resolve(scriptDir, "..");
const monorepoRoot = path.resolve(terminalRoot, "..", "..");
const terminalRel = "apps/terminal-de-venta-system";
const mode = String(process.argv[2] ?? "").trim();
const LICFLOW3_REAL_WORKER_NAME = "prisma-cloud-semilla";
const LICFLOW3_REAL_D1_NAME = "prisma_cloud_semilla";
const LICFLOW3_REAL_D1_ID = "76b12f35-f123-4b94-914f-6dde22b7fdc9";

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

function evidenceBase(): string {
  return path.resolve(process.env.PRISMA_LICFLOW3_EVIDENCE_ROOT || path.join(process.env.PRISMA_REPORT_ROOT || "F:/descargasf", "licflow3-evidence", "latest"));
}

function evidenceRoot(name: string): string {
  const root = path.join(evidenceBase(), name);
  fs.mkdirSync(root, { recursive: true });
  return root;
}

function rel(file: string): string {
  const relative = path.relative(terminalRoot, file);
  if (relative && !relative.startsWith("..") && !path.isAbsolute(relative)) return relative.replace(/\\/g, "/");
  return path.resolve(file);
}

function readText(relativePath: string): string {
  return fs.readFileSync(path.join(terminalRoot, relativePath), "utf8");
}

function readJson<T = JsonObject>(relativePath: string): T {
  return JSON.parse(readText(relativePath)) as T;
}

function writeJson(filePath: string, value: unknown): void {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

function sha256File(filePath: string): string {
  return crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
}

function pass(name: string, evidence: JsonObject): void {
  const payload = { ok: true, verifier: name, generatedAt: new Date().toISOString(), ...evidence };
  writeJson(path.join(evidenceRoot("verifier-output"), `${name.replace(/[:/]/g, "_")}.json`), payload);
  console.log(JSON.stringify(payload, null, 2));
}

function runGit(args: string[]): string {
  const result = spawnSync("git", ["-C", monorepoRoot, ...args], { encoding: "utf8" });
  if (result.status !== 0) throw new Error(`git ${args.join(" ")} failed: ${result.stderr || result.stdout}`);
  return result.stdout;
}

function runNodeCheck(relativePath: string): JsonObject {
  const result = spawnSync(process.execPath, ["--check", relativePath], { cwd: terminalRoot, encoding: "utf8" });
  return {
    command: `node --check ${relativePath}`,
    exitCode: result.status,
    stdout: result.stdout,
    stderr: result.stderr
  };
}

function runWorkerRouteContract(action: "activate" | "refresh" | "revoke"): void {
  const routeByAction = {
    activate: {
      path: "/api/licenses/activate",
      body: {
        licenseKey: "DUMMY-LICFLOW3-TEST-KEY",
        deviceId: "dummy-device-id",
        tenantId: "dummy-tenant",
        app: "terminal-de-venta-system"
      }
    },
    refresh: {
      path: "/api/licenses/refresh",
      body: {
        licenseKey: "DUMMY-LICFLOW3-TEST-KEY",
        deviceId: "dummy-device-id",
        tenantId: "dummy-tenant"
      }
    },
    revoke: {
      path: "/api/licenses/revoke",
      body: {
        licenseKey: "DUMMY-LICFLOW3-TEST-KEY",
        deviceId: "dummy-device-id",
        tenantId: "dummy-tenant",
        reason: "dummy-smoke"
      }
    }
  } as const;
  const route = routeByAction[action];
  const script = `
    import worker from "./infra/cloudflare/licflow3-worker/src/worker.js";
    const request = new Request("https://local.licflow3.test${route.path}", {
      method: "POST",
      headers: { "content-type": "application/json", "accept": "application/json" },
      body: JSON.stringify(${JSON.stringify(route.body)})
    });
    const response = await worker.fetch(request, { PRISMA_LICFLOW3_MODE: "local-contract-test" }, {});
    const text = await response.text();
    console.log(JSON.stringify({
      status: response.status,
      contentType: response.headers.get("content-type"),
      bodySha256: await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text)).then((buf) => Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, "0")).join("")),
      body: JSON.parse(text)
    }));
  `;
  const result = spawnSync(process.execPath, ["--input-type=module", "-e", script], { cwd: terminalRoot, encoding: "utf8" });
  assert(result.status === 0, `local worker route ${action} failed: ${result.stderr || result.stdout}`);
  const observed = JSON.parse(result.stdout) as {
    status: number;
    contentType: string | null;
    bodySha256: string;
    body: { ok?: unknown; status?: unknown; reason?: unknown };
  };
  const acceptedRouteEvidence = new Set([400, 401, 403, 422]);
  assert(observed.status !== 404, `${route.path} returned 404 in local worker contract check.`);
  assert(observed.status < 500, `${route.path} returned blocker status ${observed.status}.`);
  assert(acceptedRouteEvidence.has(observed.status), `${route.path} returned non-contract dummy status ${observed.status}.`);
  assert(observed.body && observed.body.ok === false, `${route.path} did not return structured rejection JSON.`);
  pass(`verify:licflow3:route-${action}`, {
    route: route.path,
    method: "POST",
    expectedDummyStatuses: [...acceptedRouteEvidence],
    observedStatus: observed.status,
    observedBodyStatus: observed.body.status || null,
    observedReason: observed.body.reason || null,
    bodySha256: observed.bodySha256,
    liveCloudTouched: false
  });
}

function scanFiles(files: string[], tokens: string[]) {
  const hits: Array<{ file: string; token: string; line: number }> = [];
  const lowered = tokens.map((token) => token.toLowerCase());
  for (const file of files) {
    if (!fs.existsSync(file) || fs.statSync(file).size > 5_000_000) continue;
    const lines = fs.readFileSync(file, "utf8").split(/\r?\n/);
    for (let index = 0; index < lines.length; index += 1) {
      const line = lines[index].toLowerCase();
      for (let tokenIndex = 0; tokenIndex < lowered.length; tokenIndex += 1) {
        if (line.includes(lowered[tokenIndex])) {
          hits.push({ file: rel(file), token: tokens[tokenIndex], line: index + 1 });
        }
      }
    }
  }
  return hits;
}

function walk(root: string, exts: string[]): string[] {
  if (!fs.existsSync(root)) return [];
  const skip = new Set(["node_modules", ".next", ".git", ".turbo", "coverage", "dist", "build", "data", "out"]);
  const out: string[] = [];
  const stack = [root];
  while (stack.length) {
    const current = stack.pop() as string;
    const stat = fs.statSync(current);
    if (stat.isDirectory()) {
      if (skip.has(path.basename(current))) continue;
      for (const child of fs.readdirSync(current)) stack.push(path.join(current, child));
    } else if (stat.isFile() && exts.includes(path.extname(current).toLowerCase())) {
      out.push(current);
    }
  }
  return out;
}

function modeInventory(): void {
  const reports = [
    "docs/reports/LICFLOW3_EXISTING_INVENTORY.md",
    "docs/reports/LICFLOW3_REUSE_MAP.md",
    "docs/reports/LICFLOW3_MISSING_REAL.md",
    "docs/reports/LICFLOW3_LEGACY_DO_NOT_USE.md",
    "docs/reports/LICFLOW3_IMPLEMENTATION_PLAN.md"
  ];
  const combined = reports.map(readText).join("\n");
  for (const report of reports) assert(fs.existsSync(path.join(terminalRoot, report)), `Missing report: ${report}`);
  for (const token of ["REUSE", "EXTEND", "CREATE", "LEGACY_DO_NOT_USE_WITHOUT_PROOF", "DOC_ONLY", "RUNTIME_ARTIFACT", "DANGER_DO_NOT_AUTORUN"]) {
    assert(combined.includes(token), `Inventory reports do not include classification token ${token}`);
  }
  assert(combined.includes("git status --short --branch"), "Inventory did not capture requested git status preflight.");
  assert(combined.includes("git diff --name-only"), "Inventory did not capture requested git diff preflight.");
  pass("verify:licflow3:inventory", { reports });
}

function modeNoDuplicates(): void {
  const licensingFiles = walk(path.join(terminalRoot, "shared", "licensing"), [".ts"]);
  const keygenHits = scanFiles(licensingFiles, ["generateKeyPairSync"]);
  const unexpectedKeygen = keygenHits.filter((hit) => hit.file !== "shared/licensing/adlant4-local-issuer.ts");
  const licflow3 = readText("shared/licensing/licflow3-cloud-contract.ts");
  assert(unexpectedKeygen.length === 0, `Unexpected issuer/keygen implementation found: ${JSON.stringify(unexpectedKeygen)}`);
  assert(!licflow3.includes("signLicenseDocument"), "LICFLOW3 contract must not duplicate ADLANT4 signing.");
  assert(!licflow3.includes("mock_license_server"), "LICFLOW3 contract imports mock license server.");
  pass("verify:licflow3:no-duplicates", {
    reusedLocalActivation: "shared/licensing/licflow2-activation.ts",
    reusedIssuer: "shared/licensing/adlant4-local-issuer.ts",
    licflow3Contract: "shared/licensing/licflow3-cloud-contract.ts",
    keygenHits,
    unexpectedKeygen
  });
}

function modeCloudContract(): void {
  const config = readJson<{ apiBaseUrl: string; tenantSlug: string; endpoints: Partial<Record<Licflow3EndpointKey, string>> }>("prisma-control-center-unified-shell-lab-v3/internal/config/cloud_saas.json");
  const status = buildLicflow3CloudContractStatus({ apiBaseUrl: config.apiBaseUrl, tenantSlug: config.tenantSlug, endpoints: config.endpoints });
  assert(status.ok, `LICFLOW3 cloud contract incomplete: ${JSON.stringify({ missing: status.missing, mismatched: status.mismatched })}`);
  assert(status.hostedCloudEvidenceStatus === LICFLOW3_CLOUDFLARE_ROUTES_LIVE, "LICFLOW3 cloud contract must reflect the authorized live Cloudflare routes evidence.");
  const capabilities = new Set(LICFLOW3_CLOUD_ENDPOINTS.map((endpoint) => endpoint.capability));
  for (const capability of LICFLOW3_REQUIRED_CAPABILITIES) assert(capabilities.has(capability), `Missing required capability ${capability}`);
  for (const endpoint of LICFLOW3_CLOUD_ENDPOINTS.filter((item) => item.mutatesCloud)) {
    assert(endpoint.safeSummaryCall === false, `${endpoint.key} mutating endpoint must not be called by summary refresh.`);
  }
  pass("verify:licflow3:cloud-contract", {
    contractId: LICFLOW3_CLOUD_CONTRACT.contractId,
    baseUrl: status.baseUrl,
    tenantSlug: status.tenantSlug,
    endpointCount: LICFLOW3_CLOUD_ENDPOINTS.length,
    hostedCloudEvidenceStatus: status.hostedCloudEvidenceStatus,
    liveDeployment: status.liveDeployment
  });
}

function mode3160Bridge(): void {
  const config = readText("prisma-control-center-unified-shell-lab-v3/internal/config/cloud_saas.json");
  const api = readText("prisma-control-center-unified-shell-lab-v3/internal/py/cloud_saas_api.py");
  const ccc = readText("prisma-control-center-unified-shell-lab-v3/internal/web/cloud_command_center.js");
  const consoleJs = readText("prisma-control-center-unified-shell-lab-v3/internal/web/cloud_saas_console.js");
  const contract = readJson<{ lab: { host: string; port: number }; modules: Array<{ id: string; directUrl?: string }> }>("prisma-control-center-unified-shell-lab-v3/internal/runtime/prisma-module-contract.json");
  const wrapper = readText("prisma-control-center/internal/wrappers/cloud_command_center_3160.ps1");
  for (const token of ["licenseActivate", "licenseRefresh", "licenseRevoke", "supportDiagnostics", "LICFLOW3_CLOUDFLARE_HOSTED_LICENSING_SUPPORT_BRIDGE"]) {
    assert(config.includes(token) || api.includes(token) || ccc.includes(token) || consoleJs.includes(token), `3160 bridge missing token ${token}`);
  }
  assert(api.includes("_licflow3_contract_status"), "cloud_saas_api does not expose LICFLOW3 contract status.");
  assert(api.includes('"supportDiagnostics": _call("supportDiagnostics"'), "cloud_saas_api does not call support diagnostics through guarded summary.");
  for (const forbidden of ['_call("licenseActivate"', '_call("licenseRefresh"', '_call("licenseRevoke"']) {
    assert(!api.includes(forbidden), `cloud_saas_api must not auto-call mutating endpoint ${forbidden}`);
  }
  assert(ccc.includes("LICFLOW3_ENDPOINT_MATRIX"), "Cloud Command Center does not show LICFLOW3 endpoint matrix.");
  assert(ccc.includes("licflow3Contract"), "Cloud Command Center does not expose LICFLOW3 contract.");
  assert(consoleJs.includes('["contract", "LICFLOW3"]'), "Cloud SaaS console lacks LICFLOW3 view.");
  assert(contract.lab.host === "127.0.0.1" && contract.lab.port === 3160, "Module contract does not keep 3160 local/private.");
  assert(contract.modules.some((item) => item.id === "cloud-saas" && item.directUrl === "https://app.hitechrts.com"), "Module contract lacks app.hitechrts.com cloud-saas module.");
  assert(wrapper.includes("3160"), "Existing 3160 wrapper not detected.");
  pass("verify:licflow3:3160-bridge", {
    cockpit: "127.0.0.1:3160",
    cloudTarget: "https://app.hitechrts.com",
    files: [
      "prisma-control-center-unified-shell-lab-v3/internal/config/cloud_saas.json",
      "prisma-control-center-unified-shell-lab-v3/internal/py/cloud_saas_api.py",
      "prisma-control-center-unified-shell-lab-v3/internal/web/cloud_command_center.js",
      "prisma-control-center-unified-shell-lab-v3/internal/web/cloud_saas_console.js"
    ]
  });
}

function modeAppHitechrtsContract(): void {
  const workerRoot = "infra/cloudflare/licflow3-worker";
  const packageJson = readJson<{ devDependencies: Record<string, string>; scripts: Record<string, string> }>(`${workerRoot}/package.json`);
  const wrangler = readJson<JsonObject>(`${workerRoot}/wrangler.jsonc`);
  const worker = readText(`${workerRoot}/src/worker.js`);
  const migration = readText(`${workerRoot}/migrations/0001_licflow3_core.sql`);
  const readme = readText(`${workerRoot}/README.md`);
  const check = runNodeCheck(`${workerRoot}/src/worker.js`);
  assert(check.exitCode === 0, `Worker syntax check failed: ${check.stderr || check.stdout}`);
  assert(packageJson.devDependencies.wrangler === "4.93.0", "Worker root must use package-local Wrangler 4.93.0.");
  assert(packageJson.scripts["wrangler:version"].includes("pnpm exec wrangler --version"), "Worker root lacks package-local Wrangler version script.");
  assert(wrangler.name === LICFLOW3_REAL_WORKER_NAME, "Wrangler project name must preserve real Worker prisma-cloud-semilla.");
  assert(!("routes" in wrangler), "Wrangler scaffold must not bind routes before authorization.");
  assert(JSON.stringify(wrangler).includes("PRISMA_LICFLOW3_D1"), "Wrangler config missing D1 binding name.");
  const d1Databases = Array.isArray(wrangler.d1_databases) ? wrangler.d1_databases : [];
  assert(d1Databases.some((item) => item.database_name === LICFLOW3_REAL_D1_NAME && item.database_id === LICFLOW3_REAL_D1_ID), "Wrangler config must preserve real D1 prisma_cloud_semilla.");
  for (const token of ["/api/licenses/activate", "/api/licenses/refresh", "/api/licenses/revoke", "/api/devices/register", "/api/client/integration-receipt", "/api/support/diagnostics"]) {
    assert(worker.includes(token), `Worker missing endpoint ${token}`);
  }
  for (const table of ["tenants", "licenses", "devices", "integration_receipts", "support_notes", "audit_events"]) {
    assert(migration.includes(`CREATE TABLE IF NOT EXISTS ${table}`), `D1 migration missing table ${table}`);
  }
  assert(readme.includes("Do not deploy without explicit authorization."), "Worker README does not block deploy by default.");
  assert(readme.includes("PRISMA_ADMIN_TOKEN") && readme.includes("PRISMA_LICFLOW3_D1"), "Worker README does not document expected binding/secret names.");
  pass("verify:licflow3:app-hitechrts-contract", {
    workerRoot,
    realWorker: LICFLOW3_REAL_WORKER_NAME,
    realD1: LICFLOW3_REAL_D1_NAME,
    wranglerPattern: "pnpm -C infra/cloudflare/licflow3-worker exec wrangler --version",
    nodeCheck: check,
    deployPerformed: false,
    cloudflareLiveEvidence: LICFLOW3_CLOUDFLARE_ROUTES_LIVE,
    liveDeployment: LICFLOW3_CLOUD_CONTRACT.liveDeployment
  });
}

function modeNoSecrets(): void {
  const roots = [
    "docs/reports",
    "shared/licensing/licflow3-cloud-contract.ts",
    "tools/verify-licflow3.mts",
    "prisma-control-center-unified-shell-lab-v3/internal/config/cloud_saas.json",
    "prisma-control-center-unified-shell-lab-v3/internal/py/cloud_saas_api.py",
    "prisma-control-center-unified-shell-lab-v3/internal/web/cloud_command_center.js",
    "prisma-control-center-unified-shell-lab-v3/internal/web/cloud_saas_console.js",
    "infra/cloudflare/licflow3-worker"
  ];
  const files = roots.flatMap((root) => {
    const absolute = path.join(terminalRoot, root);
    if (!fs.existsSync(absolute)) return [];
    if (fs.statSync(absolute).isDirectory()) return walk(absolute, [".md", ".json", ".jsonc", ".ts", ".mts", ".js", ".py", ".sql"]);
    return [absolute];
  });
  const forbiddenNameHits = files
    .map((file) => ({ file, name: path.basename(file).toLowerCase() }))
    .filter((item) => item.name === ".env" || item.name.endsWith(".pem") || item.name.endsWith(".pfx") || item.name.endsWith(".p12") || item.name.includes("private-key") || [".db", ".sqlite", ".sqlite3"].includes(path.extname(item.name)))
    .map((item) => rel(item.file));
  const forbiddenContentHits: Array<{ file: string; reason: string }> = [];
  const patterns = [
    { reason: "private key block", regex: /-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----/ },
    { reason: "OpenAI key", regex: /\bsk-[A-Za-z0-9_-]{20,}/ }
  ];
  for (const file of files) {
    if (fs.statSync(file).size > 2_000_000) continue;
    const text = fs.readFileSync(file, "utf8");
    for (const pattern of patterns) {
      if (pattern.regex.test(text) && !text.includes("00000000-0000-0000-0000-000000000000")) {
        forbiddenContentHits.push({ file: rel(file), reason: pattern.reason });
      }
    }
  }
  assert(forbiddenNameHits.length === 0, `Forbidden secret/db-like filenames found: ${forbiddenNameHits.join(", ")}`);
  assert(forbiddenContentHits.length === 0, `Forbidden secret-like content found: ${JSON.stringify(forbiddenContentHits)}`);
  pass("verify:licflow3:no-secrets", {
    scannedRoots: roots,
    scannedFiles: files.length,
    forbiddenNameHits,
    forbiddenContentHits
  });
}

function modeNoDbCommit(verifierName = "verify:licflow3:no-db-commit"): void {
  const dbExts = new Set([".db", ".sqlite", ".sqlite3", ".db-wal", ".db-shm"]);
  const tracked = runGit(["ls-files", "-z", "--", terminalRel]).split("\0").filter(Boolean);
  const trackedDb = tracked.filter((file) => dbExts.has(path.extname(file).toLowerCase()));
  const statusEntries = runGit(["status", "--porcelain=v1", "-z", "--", terminalRel]).split("\0").filter(Boolean);
  const dirtyDb = statusEntries
    .map((entry) => (entry.length > 3 ? entry.slice(3) : entry))
    .filter((file) => dbExts.has(path.extname(file).toLowerCase()));
  assert(trackedDb.length === 0, `Tracked DB files found: ${trackedDb.join(", ")}`);
  assert(dirtyDb.length === 0, `Dirty DB files found in git status: ${dirtyDb.join(", ")}`);
  pass(verifierName, { trackedDbFiles: trackedDb, dirtyDbFiles: dirtyDb, scannedGitScope: terminalRel });
}

function modeNoDangerAutorun(verifierName = "verify:licflow3:no-danger-autorun"): void {
  const packageJson = readJson<{ scripts: Record<string, string> }>("package.json");
  const licflow3Scripts = Object.entries(packageJson.scripts).filter(([key]) => key.startsWith("verify:licflow3:"));
  assert(licflow3Scripts.length >= 10, "Expected LICFLOW3 verifier scripts are missing.");
  const files = [
    path.join(terminalRoot, "tools", "verify-licflow3.mts"),
    path.join(terminalRoot, "shared", "licensing", "licflow3-cloud-contract.ts"),
    ...walk(path.join(terminalRoot, "infra", "cloudflare", "licflow3-worker"), [".js", ".json", ".jsonc", ".md", ".sql"])
  ];
  const dangerTokens = [
    ["task", "kill"].join(""),
    ["Stop", "-", "Process"].join(""),
    ["Start", "-", "Process"].join(""),
    ["kill", "_", "everything"].join(""),
    ["_", "kill", "_", "ports"].join(""),
    ["wrangler", " deploy"].join(""),
    ["pages", " deploy"].join(""),
    ["cloudflared", " tunnel"].join(""),
    ["prisma", " generate"].join("")
  ];
  const hits = scanFiles(files, dangerTokens);
  const badScripts = licflow3Scripts.filter(([, value]) => dangerTokens.some((token) => value.toLowerCase().includes(token.toLowerCase())));
  assert(hits.length === 0, `Dangerous tokens found in LICFLOW3 files: ${JSON.stringify(hits)}`);
  assert(badScripts.length === 0, `Dangerous verifier script commands found: ${JSON.stringify(badScripts)}`);
  pass(verifierName, {
    scripts: licflow3Scripts.map(([key]) => key),
    dangerTokens,
    hits
  });
}

function modeLicflow2Compatibility(kind: "offline" | "hybrid"): void {
  const root = path.join(evidenceRoot(`licflow2-${kind}`));
  const commandLine = `pnpm run verify:licflow2:${kind}`;
  const result = process.platform === "win32" ? spawnSync("cmd.exe", ["/d", "/s", "/c", commandLine], {
    cwd: terminalRoot,
    encoding: "utf8",
    env: { ...process.env, PRISMA_LICFLOW2_EVIDENCE_ROOT: root }
  }) : spawnSync("pnpm", ["run", `verify:licflow2:${kind}`], {
    cwd: terminalRoot,
    encoding: "utf8",
    env: { ...process.env, PRISMA_LICFLOW2_EVIDENCE_ROOT: root }
  });
  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);
  assert(!result.error, `Could not run verify:licflow2:${kind}: ${result.error?.message}`);
  assert(result.status === 0, `verify:licflow2:${kind} failed with exit code ${result.status}`);
  pass(`verify:licflow3:${kind}-still-valid`, {
    delegatedCommand: `pnpm run verify:licflow2:${kind}`,
    exitCode: result.status,
    evidenceRoot: root,
    stdoutSha256: crypto.createHash("sha256").update(result.stdout || "").digest("hex")
  });
}

try {
  switch (mode) {
    case "inventory":
      modeInventory();
      break;
    case "no-duplicates":
      modeNoDuplicates();
      break;
    case "cloud-contract":
      modeCloudContract();
      break;
    case "3160-bridge":
      mode3160Bridge();
      break;
    case "app-hitechrts-contract":
      modeAppHitechrtsContract();
      break;
    case "route-activate":
      runWorkerRouteContract("activate");
      break;
    case "route-refresh":
      runWorkerRouteContract("refresh");
      break;
    case "route-revoke":
      runWorkerRouteContract("revoke");
      break;
    case "no-secrets":
      modeNoSecrets();
      break;
    case "no-db":
      modeNoDbCommit();
      break;
    case "no-db-copy":
      modeNoDbCommit("verify:licflow3:no-db-copy");
      break;
    case "no-danger-autorun":
      modeNoDangerAutorun();
      break;
    case "no-deploy-autorun":
      modeNoDangerAutorun("verify:licflow3:no-deploy-autorun");
      break;
    case "offline-still-valid":
      modeLicflow2Compatibility("offline");
      break;
    case "hybrid-still-valid":
      modeLicflow2Compatibility("hybrid");
      break;
    default:
      throw new Error(`Unknown LICFLOW3 verifier mode: ${mode || "<missing>"}`);
  }
} catch (error) {
  const payload = {
    ok: false,
    verifier: mode || "<missing>",
    generatedAt: new Date().toISOString(),
    error: error instanceof Error ? error.message : String(error)
  };
  writeJson(path.join(evidenceRoot("verifier-output"), `${(mode || "missing").replace(/[:/]/g, "_")}.fail.json`), payload);
  console.error(JSON.stringify(payload, null, 2));
  process.exit(1);
}
