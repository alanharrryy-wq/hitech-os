import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  bootstrapPrismaOriginalCustomerLicense,
  buildPrismaOriginalCustomerLicenseDocument
} from "../shared/licensing/adlant4-local-issuer";
import { getLicenseGovernorSnapshot } from "../shared/licensing/license-governor";
import { PLAN_CATALOG } from "../shared/licensing/plan-catalog";
import { verifySignedLicenseEnvelope } from "../shared/licensing/license-signature";
import { PRISMA_ORIGINAL_CUSTOMER } from "../shared/customer/prisma-original-customer";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const terminalRoot = path.resolve(scriptDir, "..");
const monorepoRoot = path.resolve(terminalRoot, "..", "..");
const terminalRel = "apps/terminal-de-venta-system";
const mode = String(process.argv[2] ?? "").trim();

type JsonObject = Record<string, unknown>;

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

function readText(relativePath: string): string {
  return fs.readFileSync(path.join(terminalRoot, relativePath), "utf8");
}

function readJson<T = JsonObject>(relativePath: string): T {
  return JSON.parse(readText(relativePath)) as T;
}

function isInside(target: string, root: string): boolean {
  const relative = path.relative(path.resolve(root), path.resolve(target));
  return Boolean(relative) && !relative.startsWith("..") && !path.isAbsolute(relative);
}

function withRuntimeConfig<T>(runtimeConfigPath: string, action: () => T): T {
  const previous = process.env.PRISMA_RUNTIME_CONFIG;
  process.env.PRISMA_RUNTIME_CONFIG = runtimeConfigPath;
  try {
    return action();
  } finally {
    if (previous === undefined) {
      delete process.env.PRISMA_RUNTIME_CONFIG;
    } else {
      process.env.PRISMA_RUNTIME_CONFIG = previous;
    }
  }
}

function summarizeGovernor(snapshot: ReturnType<typeof getLicenseGovernorSnapshot>) {
  return {
    surface: snapshot.surface,
    state: snapshot.status.state,
    plan: snapshot.status.plan,
    assignmentState: snapshot.status.assignmentState,
    operationalDecision: snapshot.operationalDecision,
    denialReason: snapshot.denialReason,
    source: snapshot.status.source,
    path: snapshot.status.path,
    decisions: snapshot.decisions.map((decision) => ({
      key: decision.key,
      allowed: decision.allowed,
      reason: decision.reason
    }))
  };
}

function assertGovernorPass(snapshot: ReturnType<typeof getLicenseGovernorSnapshot>, label: string): void {
  assert(snapshot.status.state === "active", `${label} state is ${snapshot.status.state}, expected active.`);
  assert(snapshot.status.plan === "TABLET_PC_MANAGED", `${label} plan is ${snapshot.status.plan}, expected TABLET_PC_MANAGED.`);
  assert(snapshot.status.assignmentState === "assigned", `${label} assignment is ${snapshot.status.assignmentState}, expected assigned.`);
  assert(snapshot.operationalDecision === "allow", `${label} operational decision is ${snapshot.operationalDecision}, expected allow.`);
  assert(!snapshot.denialReason, `${label} has denialReason ${snapshot.denialReason}.`);
  assert(snapshot.decisions.every((decision) => decision.allowed), `${label} denied at least one requested feature.`);
}

function pass(name: string, evidence: JsonObject): void {
  console.log(JSON.stringify({ ok: true, verifier: name, generatedAt: new Date().toISOString(), ...evidence }, null, 2));
}

function modeCatalog(): void {
  const catalog = readJson<{ plans: Array<JsonObject> }>("shared/licensing/plan-catalog.canonical.json");
  const plans = Array.isArray(catalog.plans) ? catalog.plans : [];
  const byCode = new Map(plans.map((plan) => [String(plan.plan), plan]));
  const managed = byCode.get("TABLET_PC_MANAGED");
  const development = byCode.get("DEVELOPMENT");
  assert(managed, "TABLET_PC_MANAGED is missing from canonical catalog.");
  assert(managed.vendible === true, "TABLET_PC_MANAGED must be vendible.");
  assert(development, "DEVELOPMENT is missing from canonical catalog.");
  assert(development.vendible === false && development.internal === true, "DEVELOPMENT must be internal and non-vendible.");
  const features = new Set(Array.isArray(managed.features) ? managed.features.map(String) : []);
  for (const key of ["pc.open", "sync.managed", "event.outbox.view"]) {
    assert(features.has(key), `TABLET_PC_MANAGED is missing required feature ${key}.`);
    assert(PLAN_CATALOG.TABLET_PC_MANAGED.features.has(key), `TypeScript PLAN_CATALOG is missing required feature ${key}.`);
  }
  const shellStore = readText("Prisma Cloud Ctr/internal/py/command_center_store.py");
  const shellUi = readText("Prisma Cloud Ctr/internal/web/cloud_command_center.js");
  assert(shellStore.includes("PLAN_CATALOG_PATH"), "Shell Lab store does not read the canonical plan catalog.");
  assert(shellStore.includes("TABLET_PC_MANAGED"), "Shell Lab store is not wired to TABLET_PC_MANAGED.");
  assert(shellUi.includes("TABLET_PC_MANAGED"), "Shell Lab UI fallback is not wired to TABLET_PC_MANAGED.");
  assert(!shellStore.includes('("demo","Piloto"'), "Shell Lab store still exposes legacy demo plan catalog.");
  assert(!shellUi.includes('code: "demo"'), "Shell Lab UI fallback still exposes legacy demo plan catalog.");
  pass("verify:licdesk:catalog", {
    catalogPath: "shared/licensing/plan-catalog.canonical.json",
    vendiblePlans: plans.filter((plan) => plan.vendible === true).map((plan) => plan.plan),
    internalPlans: plans.filter((plan) => plan.internal === true).map((plan) => plan.plan),
    requiredFeatures: ["pc.open", "sync.managed", "event.outbox.view"]
  });
}

function modeCustomerDevice(): void {
  const document = buildPrismaOriginalCustomerLicenseDocument(new Date("2026-06-30T00:00:00.000Z"));
  assert(document.customerId === PRISMA_ORIGINAL_CUSTOMER.customerId, "License customerId does not match Prisma Original Customer.");
  assert(document.businessId === PRISMA_ORIGINAL_CUSTOMER.businessId, "License businessId does not match Prisma Original Customer.");
  assert(document.storeId === PRISMA_ORIGINAL_CUSTOMER.storeId, "License storeId does not match Prisma Original Customer.");
  assert(document.plan === "TABLET_PC_MANAGED", "Prisma Original Customer license is not TABLET_PC_MANAGED.");
  assert(document.state === "active", "Prisma Original Customer license is not active.");
  assert(document.assignmentState === "assigned", "Prisma Original Customer license is not assigned.");
  assert(document.plan !== "DEVELOPMENT", "DEVELOPMENT cannot be used as the customer license.");
  const devices = document.authorizedDevices ?? [];
  const roles = new Set(devices.map((device) => device.role));
  assert(devices.some((device) => device.deviceId === PRISMA_ORIGINAL_CUSTOMER.pcDeviceId && device.role === "pc"), "PC device authorization is missing.");
  assert(devices.some((device) => device.deviceId === PRISMA_ORIGINAL_CUSTOMER.tabletDeviceId && device.role === "tablet" && device.terminalId === PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId), "Tablet terminal authorization is missing.");
  assert(devices.some((device) => device.deviceId === PRISMA_ORIGINAL_CUSTOMER.mobileDeviceId && device.role === "mobile"), "Mobile device authorization is missing.");
  assert(roles.has("pc") && roles.has("tablet") && roles.has("mobile"), "Authorized device roles are incomplete.");
  pass("verify:licdesk:customer-device", {
    customer: {
      displayName: PRISMA_ORIGINAL_CUSTOMER.displayName,
      customerId: document.customerId,
      businessId: document.businessId,
      storeId: document.storeId,
      licenseId: document.licenseId,
      plan: document.plan
    },
    authorizedDevices: devices
  });
}

function modeSigning(): void {
  const activation = bootstrapPrismaOriginalCustomerLicense();
  assert(!isInside(activation.privateKeyPath, terminalRoot), "ADLANT4 private key is inside terminal-de-venta-system.");
  assert(!isInside(activation.privateKeyPath, monorepoRoot), "ADLANT4 private key is inside the hitech-os repo.");
  assert(fs.existsSync(activation.privateKeyPath), "ADLANT4 private key was not created.");
  assert(fs.existsSync(activation.publicKeyPath), "ADLANT4 public key registry file was not created.");
  assert(fs.existsSync(activation.signedLicensePath), "ADLANT4 signed license file was not created.");
  assert(fs.existsSync(activation.receiptPath), "ADLANT4 activation receipt was not created.");
  const envelope = JSON.parse(fs.readFileSync(activation.signedLicensePath, "utf8"));
  const verification = verifySignedLicenseEnvelope(envelope);
  assert(verification.ok, `Signed license verification failed: ${verification.ok ? "" : verification.issues.join("; ")}`);
  assert(envelope.payload.plan === "TABLET_PC_MANAGED", "Signed license payload is not TABLET_PC_MANAGED.");
  assert(envelope.payload.state === "active", "Signed license payload is not active.");
  assert(envelope.payload.customerId === PRISMA_ORIGINAL_CUSTOMER.customerId, "Signed license payload has wrong customer.");
  const privateKeyHitsAll = scanPrivateKeyBlocks([terminalRoot]);
  const allowedFixturePrefix = "tooling/licensing/server11d/";
  const privateKeyHits = privateKeyHitsAll.filter((hit) => !hit.file.replace(/\\/g, "/").startsWith(allowedFixturePrefix));
  assert(privateKeyHits.length === 0, `Private key material was found inside the repo: ${JSON.stringify(privateKeyHits.slice(0, 10))}`);
  pass("verify:licdesk:signing", {
    keyId: activation.keyId,
    alg: envelope.alg,
    licenseHash: activation.licenseHash,
    signedLicensePath: activation.signedLicensePath,
    publicKeyPath: activation.publicKeyPath,
    receiptPath: activation.receiptPath,
    privateKeyPath: "<outside-repo-redacted>",
    runtimeConfigs: activation.runtimeConfigs,
    deviceIdentities: activation.deviceIdentities,
    signatureVerified: true,
    privateKeyRepoHits: privateKeyHits,
    allowedFixturePrivateKeyHits: privateKeyHitsAll.length - privateKeyHits.length
  });
}

function modeGovernor(verifierName = "verify:licdesk:governor"): void {
  const activation = bootstrapPrismaOriginalCustomerLicense();
  const pc = withRuntimeConfig(activation.runtimeConfigs.pc, () => getLicenseGovernorSnapshot({ surface: "pc", featureKeys: ["pc.open", "sync.managed"] }));
  const tablet = withRuntimeConfig(activation.runtimeConfigs.tablet, () => getLicenseGovernorSnapshot({ surface: "tablet", featureKeys: ["pos.sale.complete", "event.outbox.view"] }));
  const mobile = withRuntimeConfig(activation.runtimeConfigs.mobile, () => getLicenseGovernorSnapshot({ surface: "mobile", featureKeys: [] }));
  assertGovernorPass(pc, "PC");
  assertGovernorPass(tablet, "Tablet");
  assertGovernorPass(mobile, "Mobile");
  pass(verifierName, {
    keyId: activation.keyId,
    licenseHash: activation.licenseHash,
    runtimeConfigs: activation.runtimeConfigs,
    governor: {
      pc: summarizeGovernor(pc),
      tablet: summarizeGovernor(tablet),
      mobile: summarizeGovernor(mobile)
    }
  });
}

function modeSupport(): void {
  const licenseOps = readText("Prisma Cloud Ctr/internal/py/license_ops_api.py");
  const shellStore = readText("Prisma Cloud Ctr/internal/py/command_center_store.py");
  const pcService = readText("products/pc/app/src/server/licensing/pc-license-service.ts");
  const tabletService = readText("products/tablet/app/src/server/licensing/tablet-license-service.ts");
  const mobileConfig = readText("products/mobile/app/src/lib/prisma-app/mobile-data-plane/config.ts");
  assert(licenseOps.includes("signedEnvelope"), "License Ops API does not summarize signed envelopes.");
  assert(licenseOps.includes("authorizedDeviceCount"), "License Ops API does not expose authorized device count.");
  assert(licenseOps.includes("_redact"), "License Ops API redaction path is missing.");
  assert(shellStore.includes("active_local_signed"), "Shell Lab first-customer activation status is not local signed.");
  assert(shellStore.includes("PLAN_CATALOG_PATH"), "Shell Lab store is not using canonical plan catalog.");
  assert(pcService.includes("getLicenseGovernorSnapshot"), "PC licensing service is not routed through license governor.");
  assert(tabletService.includes("getLicenseGovernorSnapshot"), "Tablet licensing service is not routed through license governor for features.");
  assert(mobileConfig.includes("Licencia local firmada activa"), "Mobile support account label does not reflect signed local activation.");
  pass("verify:licdesk:support", {
    supportSurfaces: [
      "Shell Lab canonical plan/customer/device seeding",
      "License Ops signed-envelope read-only diagnostics",
      "PC governor feature resolution",
      "Tablet governor feature resolution",
      "Mobile signed-license support label"
    ],
    readOnlyDiagnostics: true,
    redaction: "paths/tokens/secrets/signatures redacted in public mode"
  });
}

function modeSyncE2E(): void {
  const pnpmExecPath = process.env.npm_execpath && fs.existsSync(process.env.npm_execpath) ? process.env.npm_execpath : null;
  const command = pnpmExecPath ? process.execPath : process.platform === "win32" ? "pnpm.cmd" : "pnpm";
  const args = pnpmExecPath
    ? [pnpmExecPath, "-C", "products/pc/app", "verify:prisma-original-customer-sync-e2e"]
    : ["-C", "products/pc/app", "verify:prisma-original-customer-sync-e2e"];
  const result = spawnSync(command, args, {
    cwd: terminalRoot,
    encoding: "utf8",
    env: {
      ...process.env,
      TV_SYSTEM_ROOT: terminalRoot
    }
  });
  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);
  assert(!result.error, `verify:prisma-original-customer-sync-e2e could not start: ${result.error?.message}`);
  assert(result.status === 0, `verify:prisma-original-customer-sync-e2e failed with exit code ${result.status}.`);
  pass("verify:adlant4:sync-e2e", {
    delegatedCommand: "pnpm -C products/pc/app verify:prisma-original-customer-sync-e2e",
    exitCode: result.status
  });
}

function modeNoDb(): void {
  const dbExts = new Set([".db", ".sqlite", ".sqlite3", ".db-wal", ".db-shm"]);
  const tracked = runGit(["ls-files", "-z", "--", terminalRel]).split("\0").filter(Boolean);
  const trackedDb = tracked.filter((file) => dbExts.has(path.extname(file).toLowerCase()));
  const statusEntries = runGit(["status", "--porcelain=v1", "-z", "--", terminalRel]).split("\0").filter(Boolean);
  const dirtyDb = statusEntries
    .map((entry) => entry.length > 3 ? entry.slice(3) : entry)
    .filter((file) => dbExts.has(path.extname(file).toLowerCase()));
  assert(trackedDb.length === 0, `Tracked DB files found: ${trackedDb.join(", ")}`);
  assert(dirtyDb.length === 0, `Dirty DB files found in git status: ${dirtyDb.join(", ")}`);
  pass("verify:adlant4:no-db-commit", {
    trackedDbFiles: trackedDb,
    dirtyDbFiles: dirtyDb,
    scannedGitScope: terminalRel
  });
}

function modeNoDemo(): void {
  const forbidden = ["cust_demo", "biz_demo", "demo-prisma"];
  const productionRoots = [
    path.join(terminalRoot, "Prisma Cloud Ctr", "internal", "py"),
    path.join(terminalRoot, "Prisma Cloud Ctr", "internal", "web"),
    path.join(terminalRoot, "products", "pc", "app", "src"),
    path.join(terminalRoot, "products", "tablet", "app", "src"),
    path.join(terminalRoot, "products", "mobile", "app", "src"),
    path.join(terminalRoot, "shared", "licensing")
  ];
  const hits = scanTextFiles(productionRoots, forbidden);
  assert(hits.length === 0, `Forbidden demo identifiers found in production-visible surfaces: ${JSON.stringify(hits)}`);
  const customerSource = readText("shared/customer/prisma-original-customer.ts");
  const originalSegment = customerSource.slice(0, customerSource.indexOf("PRISMA_LEGACY_LOCAL_IDS"));
  for (const token of forbidden) {
    assert(!originalSegment.toLowerCase().includes(token), `Forbidden demo identifier ${token} found in Prisma Original Customer truth.`);
  }
  pass("verify:adlant4:no-demo-leaks", {
    forbiddenIdentifiers: forbidden,
    productionRoots: productionRoots.map((root) => path.relative(terminalRoot, root)),
    hits,
    allowedLegacyRemap: "shared/customer/prisma-original-customer.ts keeps legacy demo IDs only as normalization inputs outside Prisma Original Customer truth"
  });
}

function runGit(args: string[]): string {
  const result = spawnSync("git", ["-C", monorepoRoot, ...args], { encoding: "utf8" });
  if (result.status !== 0) {
    throw new Error(`git ${args.join(" ")} failed: ${result.stderr || result.stdout}`);
  }
  return result.stdout;
}

function scanTextFiles(roots: string[], tokens: string[]) {
  const hits: Array<{ file: string; token: string; line: number }> = [];
  const loweredTokens = tokens.map((token) => token.toLowerCase());
  for (const root of roots) {
    for (const file of walk(root)) {
      const stat = fs.statSync(file);
      if (stat.size > 2_000_000) continue;
      const text = fs.readFileSync(file, "utf8");
      const lines = text.split(/\r?\n/);
      for (let index = 0; index < lines.length; index += 1) {
        const lower = lines[index].toLowerCase();
        loweredTokens.forEach((token, tokenIndex) => {
          if (lower.includes(token)) {
            hits.push({
              file: path.relative(terminalRoot, file),
              token: tokens[tokenIndex],
              line: index + 1
            });
          }
        });
      }
    }
  }
  return hits;
}

function scanPrivateKeyBlocks(roots: string[]) {
  const hits: Array<{ file: string; token: string; line: number }> = [];
  const privateKeyBlock = /-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z0-9 ]*PRIVATE KEY-----/g;
  for (const root of roots) {
    for (const file of walk(root)) {
      const stat = fs.statSync(file);
      if (stat.size > 5_000_000) continue;
      const text = fs.readFileSync(file, "utf8");
      let match: RegExpExecArray | null;
      while ((match = privateKeyBlock.exec(text)) !== null) {
        const line = text.slice(0, match.index).split(/\r?\n/).length;
        hits.push({ file: path.relative(terminalRoot, file), token: "PEM_PRIVATE_KEY_BLOCK", line });
      }
    }
  }
  return hits;
}

function walk(root: string): string[] {
  if (!fs.existsSync(root)) return [];
  const skipDirs = new Set(["node_modules", ".next", ".git", ".turbo", "coverage", "dist", "build", "data", "out"]);
  const textExts = new Set([".ts", ".tsx", ".mts", ".js", ".mjs", ".json", ".py", ".md", ".html", ".css", ".pem", ".key"]);
  const out: string[] = [];
  const stack = [root];
  while (stack.length) {
    const current = stack.pop() as string;
    const stat = fs.statSync(current);
    if (stat.isDirectory()) {
      if (skipDirs.has(path.basename(current))) continue;
      for (const child of fs.readdirSync(current)) stack.push(path.join(current, child));
    } else if (stat.isFile() && textExts.has(path.extname(current).toLowerCase())) {
      out.push(current);
    }
  }
  return out;
}

try {
  switch (mode) {
    case "catalog":
      modeCatalog();
      break;
    case "customer-device":
      modeCustomerDevice();
      break;
    case "signing":
      modeSigning();
      break;
    case "governor":
      modeGovernor();
      break;
    case "adlant4-governor":
      modeGovernor("verify:adlant4:license-governor");
      break;
    case "support":
      modeSupport();
      break;
    case "sync-e2e":
      modeSyncE2E();
      break;
    case "no-db":
      modeNoDb();
      break;
    case "no-demo":
      modeNoDemo();
      break;
    default:
      throw new Error(`Unknown LICDESK4/ADLANT4 verifier mode: ${mode || "<missing>"}`);
  }
} catch (error) {
  console.error(JSON.stringify({
    ok: false,
    verifier: mode || "<missing>",
    generatedAt: new Date().toISOString(),
    error: error instanceof Error ? error.message : String(error)
  }, null, 2));
  process.exit(1);
}
