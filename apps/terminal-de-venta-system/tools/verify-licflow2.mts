import { spawnSync } from "node:child_process";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  createLicflow2ActivationPackage,
  createLicflow2HybridActivationEvidence,
  createLicflow2OnlineActivationEvidence,
  LICFLOW2_ACTIVATION_MODES,
  LICFLOW2_SERVICE_CONTRACT_ENDPOINT,
  type Licflow2ActivationPackageResult
} from "../shared/licensing/licflow2-activation";
import { getLicenseGovernorSnapshot } from "../shared/licensing/license-governor";
import { verifySignedLicenseEnvelope } from "../shared/licensing/license-signature";
import { PRISMA_ORIGINAL_CUSTOMER } from "../shared/customer/prisma-original-customer";

type JsonObject = Record<string, unknown>;

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const terminalRoot = path.resolve(scriptDir, "..");
const monorepoRoot = path.resolve(terminalRoot, "..", "..");
const terminalRel = "apps/terminal-de-venta-system";
const mode = String(process.argv[2] ?? "").trim();

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

function evidenceBase(): string {
  return path.resolve(process.env.PRISMA_LICFLOW2_EVIDENCE_ROOT || path.join(process.env.PRISMA_REPORT_ROOT || "F:/descargasf", "licflow2-evidence", "latest"));
}

function evidenceRoot(name: string): string {
  const root = path.join(evidenceBase(), name);
  fs.mkdirSync(root, { recursive: true });
  return root;
}

function rel(file: string): string {
  return path.relative(terminalRoot, file).replace(/\\/g, "/");
}

function readText(relativePath: string): string {
  return fs.readFileSync(path.join(terminalRoot, relativePath), "utf8");
}

function readJson<T = JsonObject>(filePath: string): T {
  return JSON.parse(fs.readFileSync(filePath, "utf8")) as T;
}

function writeJson(filePath: string, value: unknown): void {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

function sha256(filePath: string): string {
  return crypto.createHash("sha256").update(fs.readFileSync(filePath)).digest("hex");
}

function pass(name: string, evidence: JsonObject): void {
  const payload = { ok: true, verifier: name, generatedAt: new Date().toISOString(), ...evidence };
  writeJson(path.join(evidenceRoot("verifier-output"), `${name.replace(/[:/]/g, "_")}.json`), payload);
  console.log(JSON.stringify(payload, null, 2));
}

function summarizeGovernor(snapshot: ReturnType<typeof getLicenseGovernorSnapshot>) {
  return {
    surface: snapshot.surface,
    state: snapshot.status.state,
    plan: snapshot.status.plan,
    assignmentState: snapshot.status.assignmentState,
    operationalDecision: snapshot.operationalDecision,
    denialReason: snapshot.denialReason,
    activationMode: snapshot.status.raw?.activation?.mode ?? null,
    refreshState: snapshot.refreshState.state,
    path: snapshot.status.path
  };
}

function assertGovernorActive(snapshot: ReturnType<typeof getLicenseGovernorSnapshot>, label: string): void {
  assert(snapshot.status.state === "active", `${label} license state is ${snapshot.status.state}`);
  assert(snapshot.status.plan === "TABLET_PC_MANAGED", `${label} plan is ${snapshot.status.plan}`);
  assert(snapshot.status.assignmentState === "assigned", `${label} assignment state is ${snapshot.status.assignmentState}`);
  assert(snapshot.operationalDecision === "allow", `${label} operational decision is ${snapshot.operationalDecision}`);
  assert(!snapshot.denialReason, `${label} denial reason is ${snapshot.denialReason}`);
}

function withEnv<T>(updates: Record<string, string | undefined>, action: () => T): T {
  const previous = new Map<string, string | undefined>();
  for (const [key, value] of Object.entries(updates)) {
    previous.set(key, process.env[key]);
    if (value === undefined) delete process.env[key];
    else process.env[key] = value;
  }
  try {
    return action();
  } finally {
    for (const [key, value] of previous.entries()) {
      if (value === undefined) delete process.env[key];
      else process.env[key] = value;
    }
  }
}

function psQuote(value: string): string {
  return value.replace(/'/g, "''");
}

function zipDirectory(sourceDir: string, zipPath: string): void {
  const command = `$ErrorActionPreference='Stop'; $source='${psQuote(sourceDir)}'; $destination='${psQuote(zipPath)}'; $items=Join-Path -Path $source -ChildPath '*'; Compress-Archive -Path $items -DestinationPath $destination -Force`;
  const result = spawnSync("powershell", ["-NoProfile", "-Command", command], { encoding: "utf8" });
  if (result.status !== 0) {
    throw new Error(`Compress-Archive failed: ${result.stderr || result.stdout}`);
  }
}

function runProvision(packageResult: Licflow2ActivationPackageResult, role: "pc" | "tablet" | "mobile", runtimeRoot: string) {
  const result = spawnSync(process.execPath, [
    "tools/provision-prisma-runtime.mjs",
    "--activation-package",
    packageResult.packageRoot,
    "--role",
    role,
    "--runtime-root",
    runtimeRoot,
    "--runtime-mode",
    "customer",
    "--package-type",
    "TABLET_PC_MANAGED",
    "--apply"
  ], {
    cwd: terminalRoot,
    encoding: "utf8",
    env: { ...process.env, TV_SYSTEM_ROOT: terminalRoot }
  });
  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);
  assert(!result.error, `Provisioning could not start: ${result.error?.message}`);
  assert(result.status === 0, `Provisioning failed with exit code ${result.status}`);
  return {
    exitCode: result.status,
    runtimeRoot,
    runtimeConfigPath: path.join(runtimeRoot, "Config", "runtime.json"),
    licensePath: path.join(runtimeRoot, "Config", "license.json"),
    deviceIdentityPath: path.join(runtimeRoot, "Config", "device-identity.json"),
    receiptPath: path.join(runtimeRoot, "Config", "activation-receipt.json")
  };
}

function assertPackageSafe(packageResult: Licflow2ActivationPackageResult): void {
  assert(packageResult.manifest.security.privateKeyIncluded === false, "Package manifest says private key included.");
  assert(packageResult.manifest.security.dbFilesIncluded === false, "Package manifest says DB files included.");
  assert(packageResult.manifest.security.envFilesIncluded === false, "Package manifest says env files included.");
  assert(packageResult.manifest.security.secretsIncluded === false, "Package manifest says secrets included.");
  for (const role of ["pc", "tablet", "mobile"] as const) {
    assert(packageResult.manifest.roles[role], `Package missing role ${role}.`);
  }
  const verification = verifySignedLicenseEnvelope(packageResult.envelope);
  assert(verification.ok, `Signed package license failed verification: ${verification.ok ? "" : verification.issues.join("; ")}`);
  assert(packageResult.envelope.payload.customerId === PRISMA_ORIGINAL_CUSTOMER.customerId, "Package license customer mismatch.");
  assert(packageResult.envelope.payload.plan === "TABLET_PC_MANAGED", "Package license plan mismatch.");
}

function modeInventory(): void {
  const preexisting = readText("docs/reports/LICFLOW2_PREEXISTING_DIRTY_FILES.md");
  const inventory = readText("docs/reports/LICFLOW2_EXISTING_INVENTORY.md");
  const packageJson = readJson<{ scripts: Record<string, string> }>(path.join(terminalRoot, "package.json"));
  assert(preexisting.includes("Git Status Before LICFLOW2 Patch"), "Preexisting dirty report missing git status section.");
  assert(inventory.includes("Existing Licensing Core To Reuse"), "Existing inventory missing licensing reuse section.");
  assert(inventory.includes("shared/licensing/adlant4-local-issuer.ts"), "Existing inventory does not cite ADLANT4 issuer.");
  assert(inventory.includes("tools/provision-prisma-runtime.mjs"), "Existing inventory does not cite provisioning tool.");
  assert(Array.isArray([...LICFLOW2_ACTIVATION_MODES]), "LICFLOW2 modes are not exported.");
  pass("verify:licflow2:inventory", {
    reports: [
      "docs/reports/LICFLOW2_PREEXISTING_DIRTY_FILES.md",
      "docs/reports/LICFLOW2_EXISTING_INVENTORY.md"
    ],
    modes: LICFLOW2_ACTIVATION_MODES,
    scriptsKnownAfterPatch: Object.keys(packageJson.scripts).filter((key) => key.startsWith("verify:licflow2:")).sort()
  });
}

function modeOffline(): void {
  const root = evidenceRoot("offline");
  const packageResult = createLicflow2ActivationPackage({ mode: "OFFLINE_PACKAGE", outputRoot: root });
  assertPackageSafe(packageResult);
  const zipPath = `${packageResult.packageRoot}.zip`;
  zipDirectory(packageResult.packageRoot, zipPath);
  assert(fs.existsSync(zipPath), `Offline activation ZIP missing: ${zipPath}`);
  const provision = runProvision(packageResult, "tablet", path.join(root, "provisioned-tablet-runtime"));
  for (const file of [provision.runtimeConfigPath, provision.licensePath, provision.deviceIdentityPath, provision.receiptPath]) {
    assert(fs.existsSync(file), `Provisioned file missing: ${file}`);
  }
  const governor = withEnv({ PRISMA_RUNTIME_CONFIG: provision.runtimeConfigPath }, () => getLicenseGovernorSnapshot({ surface: "tablet", featureKeys: ["pos.sale.complete", "event.outbox.view"] }));
  assertGovernorActive(governor, "offline tablet");
  assert(governor.status.raw?.activation?.mode === "OFFLINE_PACKAGE", "Offline license activation mode not visible in governor raw payload.");
  pass("verify:licflow2:offline", {
    packageRoot: packageResult.packageRoot,
    packageZip: zipPath,
    packageZipSha256: sha256(zipPath),
    manifestPath: packageResult.manifestPath,
    signedLicensePath: packageResult.signedLicensePath,
    receiptPath: packageResult.receiptPath,
    licenseHash: packageResult.licenseHash,
    provision,
    governor: summarizeGovernor(governor)
  });
}

function modeOnline(): void {
  const root = evidenceRoot("online");
  const online = createLicflow2OnlineActivationEvidence({ outputRoot: root, role: "pc" });
  assertPackageSafe(online.packageResult);
  assert(online.response.endpoint === LICFLOW2_SERVICE_CONTRACT_ENDPOINT, "Online service contract endpoint mismatch.");
  assert(online.response.hostedCloud === false, "Online verifier must not claim hosted cloud.");
  const provision = runProvision(online.packageResult, "pc", path.join(root, "provisioned-pc-runtime"));
  const governor = withEnv({ PRISMA_RUNTIME_CONFIG: provision.runtimeConfigPath }, () => getLicenseGovernorSnapshot({ surface: "pc", featureKeys: ["pc.open", "sync.managed"] }));
  assertGovernorActive(governor, "online pc");
  assert(governor.status.raw?.activation?.mode === "ONLINE_ACTIVATION", "Online license activation mode not visible in governor raw payload.");
  pass("verify:licflow2:online", {
    request: online.request,
    response: online.response,
    hostedCloudClaimed: false,
    serviceContract: LICFLOW2_SERVICE_CONTRACT_ENDPOINT,
    provision,
    governor: summarizeGovernor(governor)
  });
}

function modeHybrid(): void {
  const root = evidenceRoot("hybrid");
  const hybrid = createLicflow2HybridActivationEvidence({ outputRoot: root });
  assertPackageSafe(hybrid.packageResult);
  assert(hybrid.refreshFallback.localLicenseStillValid === true, "Hybrid fallback does not preserve local license.");
  assert(hybrid.refreshFallback.operationalDecision === "allow_with_warning", "Hybrid fallback decision mismatch.");
  const provision = runProvision(hybrid.packageResult, "tablet", path.join(root, "provisioned-hybrid-tablet-runtime"));
  const governor = withEnv({ PRISMA_RUNTIME_CONFIG: provision.runtimeConfigPath }, () => getLicenseGovernorSnapshot({ surface: "tablet", featureKeys: ["pos.sale.complete", "sync.dispatch"] }));
  assertGovernorActive(governor, "hybrid tablet");
  assert(governor.status.raw?.activation?.mode === "HYBRID", "Hybrid license activation mode not visible in governor raw payload.");
  pass("verify:licflow2:hybrid", {
    packageRoot: hybrid.packageResult.packageRoot,
    fallback: hybrid.refreshFallback,
    provision,
    governor: summarizeGovernor(governor)
  });
}

function modeSupport(): void {
  const root = evidenceRoot("support");
  const packageResult = createLicflow2ActivationPackage({ mode: "HYBRID", outputRoot: root });
  const provision = runProvision(packageResult, "mobile", path.join(root, "provisioned-mobile-runtime"));
  const governor = withEnv({ PRISMA_RUNTIME_CONFIG: provision.runtimeConfigPath }, () => getLicenseGovernorSnapshot({ surface: "mobile", featureKeys: [] }));
  assertGovernorActive(governor, "support mobile");
  const licenseOpsPy = readText("Prisma Cloud Ctr/internal/py/license_ops_api.py");
  const licenseOpsJs = readText("Prisma Cloud Ctr/internal/web/license_ops_console.js");
  const mobileConfig = readText("products/mobile/app/src/lib/prisma-app/mobile-data-plane/config.ts");
  const mobileContracts = readText("products/mobile/app/src/lib/prisma-app/prisma-app-api-contracts.ts");
  assert(licenseOpsPy.includes('"activation"'), "Shell Lab License Ops API does not expose activation summary.");
  assert(licenseOpsPy.includes('"receiptId"'), "Shell Lab License Ops API does not expose activation receipt id.");
  assert(licenseOpsJs.includes("activation.mode"), "Shell Lab License Ops UI does not render activation mode.");
  assert(mobileConfig.includes("PRISMA_MOBILE_ACTIVATION_MODE"), "Mobile data plane config lacks activation mode env support.");
  assert(mobileContracts.includes("activationModeLabel"), "Mobile API account contract lacks activation mode label.");
  pass("verify:licflow2:support", {
    shellLab: {
      api: "Prisma Cloud Ctr/internal/py/license_ops_api.py",
      ui: "Prisma Cloud Ctr/internal/web/license_ops_console.js",
      readOnly: true
    },
    pcTablet: "existing license governor snapshots expose raw activation metadata",
    mobile: "mobile account contract exposes activationMode and activationModeLabel",
    provision,
    governor: summarizeGovernor(governor)
  });
}

function modeNoDuplicates(): void {
  const licensingFiles = walk(path.join(terminalRoot, "shared", "licensing"), [".ts"]);
  const keygenHits = scanFiles(licensingFiles, ["generateKeyPairSync"]);
  const unexpectedKeygen = keygenHits.filter((hit) => hit.file !== "shared/licensing/adlant4-local-issuer.ts");
  assert(unexpectedKeygen.length === 0, `Unexpected issuer/keygen implementation found: ${JSON.stringify(unexpectedKeygen)}`);
  const licflowSource = readText("shared/licensing/licflow2-activation.ts");
  assert(licflowSource.includes("bootstrapPrismaOriginalCustomerLicense"), "LICFLOW2 does not reuse ADLANT4 bootstrap.");
  assert(licflowSource.includes("signLicenseDocument"), "LICFLOW2 does not reuse ADLANT4 signing.");
  assert(!licflowSource.includes("mock_license_server"), "LICFLOW2 imports mock license server.");
  pass("verify:licflow2:no-duplicates", {
    reusedIssuer: "shared/licensing/adlant4-local-issuer.ts",
    keygenHits,
    unexpectedKeygen,
    licflowModule: "shared/licensing/licflow2-activation.ts"
  });
}

function modeNoSecrets(): void {
  const roots = [
    evidenceBase(),
    path.join(terminalRoot, "shared", "licensing", "licflow2-activation.ts"),
    path.join(terminalRoot, "tools", "verify-licflow2.mts"),
    path.join(terminalRoot, "Prisma Cloud Ctr", "internal", "py", "license_ops_api.py"),
    path.join(terminalRoot, "Prisma Cloud Ctr", "internal", "web", "license_ops_console.js")
  ];
  const files = roots.flatMap((root) => fs.existsSync(root) && fs.statSync(root).isDirectory() ? walk(root, [".json", ".md", ".ts", ".mts", ".js", ".py"]) : fs.existsSync(root) ? [root] : []);
  const forbiddenNameHits = files
    .map((file) => ({ file, name: path.basename(file).toLowerCase() }))
    .filter((item) => item.name === ".env" || item.name.endsWith(".pem") || item.name.endsWith(".pfx") || item.name.endsWith(".p12") || item.name.includes("private-key"))
    .map((item) => relOrAbsolute(item.file));
  const privateKeyBlocks = [];
  const privateKeyPattern = /-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----/;
  for (const file of files) {
    if (fs.statSync(file).size > 5_000_000) continue;
    const text = fs.readFileSync(file, "utf8");
    if (privateKeyPattern.test(text)) privateKeyBlocks.push(relOrAbsolute(file));
  }
  assert(forbiddenNameHits.length === 0, `Forbidden secret-like filenames found: ${forbiddenNameHits.join(", ")}`);
  assert(privateKeyBlocks.length === 0, `Private key blocks found: ${privateKeyBlocks.join(", ")}`);
  pass("verify:licflow2:no-secrets", {
    scannedRoots: roots.map(relOrAbsolute),
    scannedFiles: files.length,
    forbiddenNameHits,
    privateKeyBlocks
  });
}

function modeNoDbCommit(): void {
  const dbExts = new Set([".db", ".sqlite", ".sqlite3", ".db-wal", ".db-shm"]);
  const tracked = runGit(["ls-files", "-z", "--", terminalRel]).split("\0").filter(Boolean);
  const trackedDb = tracked.filter((file) => dbExts.has(path.extname(file).toLowerCase()));
  const statusEntries = runGit(["status", "--porcelain=v1", "-z", "--", terminalRel]).split("\0").filter(Boolean);
  const dirtyDb = statusEntries
    .map((entry) => entry.length > 3 ? entry.slice(3) : entry)
    .filter((file) => dbExts.has(path.extname(file).toLowerCase()));
  assert(trackedDb.length === 0, `Tracked DB files found: ${trackedDb.join(", ")}`);
  assert(dirtyDb.length === 0, `Dirty DB files found in git status: ${dirtyDb.join(", ")}`);
  pass("verify:licflow2:no-db-commit", {
    trackedDbFiles: trackedDb,
    dirtyDbFiles: dirtyDb,
    scannedGitScope: terminalRel
  });
}

function modeNoDemoLeaks(): void {
  const forbidden = [["cust", "demo"].join("_"), ["biz", "demo"].join("_"), ["demo", "prisma"].join("-")];
  const files = [
    path.join(terminalRoot, "shared", "licensing", "licflow2-activation.ts"),
    path.join(terminalRoot, "tools", "verify-licflow2.mts"),
    path.join(terminalRoot, "products", "mobile", "app", "src", "lib", "prisma-app", "mobile-data-plane", "config.ts"),
    path.join(terminalRoot, "products", "mobile", "app", "src", "lib", "prisma-app", "mobile-data-plane", "types.ts"),
    path.join(terminalRoot, "products", "mobile", "app", "src", "lib", "prisma-app", "mobile-data-plane", "payload-builders.ts"),
    path.join(terminalRoot, "products", "mobile", "app", "src", "lib", "prisma-app", "prisma-app-api-contracts.ts"),
    path.join(terminalRoot, "Prisma Cloud Ctr", "internal", "py", "license_ops_api.py"),
    path.join(terminalRoot, "Prisma Cloud Ctr", "internal", "web", "license_ops_console.js"),
    ...walk(evidenceBase(), [".json", ".md"]).filter((file) => !file.replace(/\\/g, "/").includes("/verifier-output/"))
  ].filter((file) => fs.existsSync(file));
  const hits = scanFiles(files, forbidden);
  assert(hits.length === 0, `Forbidden demo identifiers found in LICFLOW2 implementation/evidence: ${JSON.stringify(hits)}`);
  pass("verify:licflow2:no-demo-leaks", {
    forbiddenIdentifiers: forbidden,
    scannedFiles: files.length,
    hits
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
          hits.push({ file: relOrAbsolute(file), token: tokens[tokenIndex], line: index + 1 });
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

function relOrAbsolute(file: string): string {
  const relative = path.relative(terminalRoot, file);
  if (relative && !relative.startsWith("..") && !path.isAbsolute(relative)) return relative.replace(/\\/g, "/");
  return path.resolve(file);
}

function runGit(args: string[]): string {
  const result = spawnSync("git", ["-C", monorepoRoot, ...args], { encoding: "utf8" });
  if (result.status !== 0) throw new Error(`git ${args.join(" ")} failed: ${result.stderr || result.stdout}`);
  return result.stdout;
}

try {
  switch (mode) {
    case "inventory":
      modeInventory();
      break;
    case "offline":
      modeOffline();
      break;
    case "online":
      modeOnline();
      break;
    case "hybrid":
      modeHybrid();
      break;
    case "support":
      modeSupport();
      break;
    case "no-duplicates":
      modeNoDuplicates();
      break;
    case "no-secrets":
      modeNoSecrets();
      break;
    case "no-db":
      modeNoDbCommit();
      break;
    case "no-demo":
      modeNoDemoLeaks();
      break;
    default:
      throw new Error(`Unknown LICFLOW2 verifier mode: ${mode || "<missing>"}`);
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
