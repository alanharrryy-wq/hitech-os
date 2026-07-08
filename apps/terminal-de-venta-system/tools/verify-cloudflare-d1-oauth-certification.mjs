#!/usr/bin/env node
import crypto from "node:crypto";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const terminalRoot = path.resolve(fileURLToPath(new URL("..", import.meta.url)));
const workerRoot = path.join(terminalRoot, "infra/cloudflare/licflow3-worker");
const workerRootRel = "infra/cloudflare/licflow3-worker";
const checkedAt = new Date().toISOString();
const outPath = process.argv.find((arg) => arg.startsWith("--out="))?.slice("--out=".length)
  || "docs/ops/licscope/live_smoke_outputs/cloudflare-d1-oauth-certification.json";
const liveBase = "https://app.hitechrts.com";
const d1Name = "prisma_cloud_semilla";
const passStatus = "PASS_OAUTH_D1_AUDIT_SECRETSCAN_CLOUD_BRIDGE_CERTIFIED";
const requiredLicenseColumns = ["id", "tenant_id", "plan", "status", "max_devices", "starts_at", "expires_at", "created_at", "updated_at"];
const requiredAuditEvents = [
  "customer_setup.create",
  "customer_setup.plan_based_provision",
  "customer_device.claim",
  "customer_license.refresh",
  "license.revoke",
  "license.renew",
  "license.commercial-state",
  "customer_device.replacement.request",
  "customer_device.replacement.approve"
];

function rel(file) {
  return path.isAbsolute(file) ? file : path.join(terminalRoot, file);
}

function repoRel(file) {
  return path.relative(terminalRoot, file).replace(/\\/g, "/");
}

function sanitizeText(value) {
  return String(value || "")
    .replace(/\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi, "[EMAIL_REDACTED]")
    .replace(/\bBearer\s+[A-Za-z0-9._-]{16,}\b/g, "Bearer [REDACTED]")
    .replace(/\b(?:sk|gh[pousr])-[A-Za-z0-9_-]{16,}\b/g, "[TOKEN_REDACTED]")
    .replace(/\bgh[pousr]_[A-Za-z0-9_]{20,}\b/g, "[TOKEN_REDACTED]")
    .replace(/\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi, "[UUID_REDACTED]")
    .replace(/\b[0-9a-f]{28,40}\b/gi, "[HEX_ID_REDACTED]")
    .slice(0, 12000);
}

function runWrangler(args) {
  const startedAt = new Date().toISOString();
  let result;
  if (process.platform === "win32") {
    const wranglerBin = path.join(workerRoot, "node_modules", ".bin", "wrangler.cmd");
    const quote = (value) => `'${String(value).replace(/'/g, "''")}'`;
    const commandText = fs.existsSync(wranglerBin)
      ? `& ${quote(wranglerBin)} ${args.map(quote).join(" ")}`
      : `& pnpm -C ${quote(workerRootRel)} exec wrangler ${args.map(quote).join(" ")}`;
    result = spawnSync("powershell.exe", ["-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", commandText], {
      cwd: fs.existsSync(wranglerBin) ? workerRoot : terminalRoot,
      encoding: "utf8",
      shell: false,
      env: process.env
    });
  } else {
    const wranglerBin = path.join(workerRoot, "node_modules", ".bin", "wrangler");
    const executable = fs.existsSync(wranglerBin) ? wranglerBin : process.platform === "win32" ? "pnpm.cmd" : "pnpm";
    const spawnArgs = fs.existsSync(wranglerBin) ? args : ["-C", workerRootRel, "exec", "wrangler", ...args];
    result = spawnSync(executable, spawnArgs, {
      cwd: fs.existsSync(wranglerBin) ? workerRoot : terminalRoot,
      encoding: "utf8",
      shell: false,
      env: process.env
    });
  }
  const stdout = sanitizeText(result.stdout);
  const stderr = sanitizeText(result.stderr);
  return {
    command: `pnpm -C apps/terminal-de-venta-system/infra/cloudflare/licflow3-worker exec wrangler ${args.join(" ")}`,
    startedAt,
    exitCode: typeof result.status === "number" ? result.status : 1,
    ok: result.status === 0 && !result.error,
    stdout,
    stderr,
    error: result.error ? sanitizeText(result.error.message) : "",
    stdoutSha256: crypto.createHash("sha256").update(result.stdout || "").digest("hex"),
    stderrSha256: crypto.createHash("sha256").update(result.stderr || "").digest("hex")
  };
}

function runD1Execute(name, sql) {
  const sqlDir = rel("docs/ops/licscope/live_smoke_outputs/d1_readonly_sql");
  fs.mkdirSync(sqlDir, { recursive: true });
  const sqlPath = path.join(sqlDir, `${name}.sql`);
  fs.writeFileSync(sqlPath, `${sql.trim()}\n`, "utf8");
  return runWrangler(["d1", "execute", d1Name, "--remote", "--json", "--command", sql]);
}

function parseJsonFromOutput(output) {
  const text = String(output || "").trim();
  for (const [open, close] of [["[", "]"], ["{", "}"]]) {
    const start = text.indexOf(open);
    const end = text.lastIndexOf(close);
    if (start >= 0 && end > start) {
      try {
        return JSON.parse(text.slice(start, end + 1));
      } catch {
        // Keep falling back to text checks.
      }
    }
  }
  return null;
}

function rowsFromD1Json(parsed) {
  if (!parsed) return [];
  const batches = Array.isArray(parsed) ? parsed : [parsed];
  return batches.flatMap((item) => {
    if (Array.isArray(item?.results)) return item.results;
    if (Array.isArray(item?.result?.[0]?.results)) return item.result[0].results;
    if (Array.isArray(item?.result?.results)) return item.result.results;
    return [];
  });
}

function check(condition, name, evidence) {
  return { name, status: condition ? "PASS" : "FAIL", evidence };
}

async function requestJson(route) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 20000);
  try {
    const response = await fetch(`${liveBase}${route}`, { signal: controller.signal });
    const text = await response.text();
    let json = null;
    try {
      json = text ? JSON.parse(text) : null;
    } catch {
      json = { rawText: sanitizeText(text) };
    }
    return { route, status: response.status, ok: response.ok, json };
  } finally {
    clearTimeout(timer);
  }
}

function walkTextFiles(root) {
  const files = [];
  const allow = new Set([".cmd", ".html", ".js", ".json", ".jsonc", ".md", ".mjs", ".mts", ".ps1", ".py", ".sql", ".ts"]);
  const skip = /(?:^|[\\/])(?:\.git|node_modules|\.next|dist|build|coverage|row_exports_sanitized|changed_files)(?:[\\/]|$)/i;
  function walk(current) {
    if (!fs.existsSync(current) || skip.test(current)) return;
    const stat = fs.statSync(current);
    if (stat.isDirectory()) {
      for (const entry of fs.readdirSync(current)) walk(path.join(current, entry));
      return;
    }
    if (stat.isFile() && stat.size <= 1_500_000 && allow.has(path.extname(current).toLowerCase())) files.push(current);
  }
  walk(root);
  return files;
}

function fineSecretScan() {
  const roots = [
    "infra/cloudflare/licflow3-worker",
    "Prisma Cloud Ctr/internal/config",
    "Prisma Cloud Ctr/internal/py",
    "Prisma Cloud Ctr/internal/web",
    "Prisma Cloud Ctr/PRISMA_CLOUD_CENTER_MANUAL_FACTORY_STANDARD.md",
    "shared/licensing",
    "docs/ops/LICFLOW3_CLOUDFLARE_RUNBOOK.md",
    "docs/ops/licscope/LICFLOW3_CLOUDFLARE_WRANGLER_D1_RUNBOOK.md",
    "tools/verify-cloud-center-live-readiness.mjs",
    "tools/verify-cloudflare-d1-oauth-certification.mjs",
    "tools/licscope-closure.mjs"
  ];
  const patterns = [
    { reason: "private key block", regex: /-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----/ },
    { reason: "github token literal", regex: /\bgh[pousr]_[A-Za-z0-9_]{30,}\b/ },
    { reason: "openai key literal", regex: /\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}\b/ },
    { reason: "bearer token literal", regex: /\bBearer\s+(?!\[REDACTED\]|<TOKEN|TOKEN|your-token|example)[A-Za-z0-9._-]{30,}\b/i },
    { reason: "cloudflare token assignment literal", regex: /\b(?:CLOUDFLARE_API_TOKEN|CF_API_TOKEN)\s*[:=]\s*["']?(?!\$|%|<|process\.env|os\.environ|REDACTED|YOUR_|example|placeholder)[A-Za-z0-9_.-]{30,}/i },
    { reason: "admin token assignment literal", regex: /\b(?:PRISMA_ADMIN_TOKEN|ADMIN_TOKEN|LICFLOW_ADMIN_TOKEN)\s*[:=]\s*["']?(?!\$|%|<|process\.env|os\.environ|getenv|REDACTED|YOUR_|example|placeholder)[A-Za-z0-9_.-]{24,}/i }
  ];
  const files = roots.flatMap((root) => {
    const absolute = rel(root);
    if (!fs.existsSync(absolute)) return [];
    if (fs.statSync(absolute).isFile()) return [absolute];
    return walkTextFiles(absolute);
  });
  const findings = [];
  for (const file of files) {
    const lines = fs.readFileSync(file, "utf8").split(/\r?\n/);
    lines.forEach((line, index) => {
      for (const pattern of patterns) {
        if (pattern.regex.test(line)) {
          findings.push({ file: repoRel(file), line: index + 1, reason: pattern.reason });
        }
      }
    });
  }
  return {
    scannedRoots: roots,
    scannedFiles: files.length,
    findingsCount: findings.length,
    findings
  };
}

async function main() {
  const wranglerVersion = runWrangler(["--version"]);
  const whoami = runWrangler(["whoami"]);
  const health = await requestJson("/health");
  const d1List = runWrangler(["d1", "list"]);
  const migrations = runWrangler(["d1", "migrations", "list", d1Name, "--remote"]);
  const schema = runD1Execute("schema", "SELECT type,name,tbl_name,sql FROM sqlite_schema WHERE type IN ('table','index','trigger','view') ORDER BY type,name;");
  const licensesInfo = runD1Execute("licenses_table_info", "PRAGMA table_info(licenses);");
  const licenseStatusCounts = runD1Execute("license_status_counts", "SELECT status, COUNT(*) AS count FROM licenses GROUP BY status ORDER BY status;");
  const auditInfo = runD1Execute("audit_events_table_info", "PRAGMA table_info(audit_events);");
  const auditCounts = runD1Execute("audit_event_counts", "SELECT event_type, COUNT(*) AS count FROM audit_events GROUP BY event_type ORDER BY count DESC LIMIT 50;");
  const requiredAuditQuery = `SELECT event_type, COUNT(*) AS count FROM audit_events WHERE event_type IN (${requiredAuditEvents.map((event) => `'${event}'`).join(",")}) GROUP BY event_type ORDER BY event_type;`;
  const requiredAudit = runD1Execute("required_audit_events", requiredAuditQuery);
  const secretScan = fineSecretScan();

  const schemaText = `${schema.stdout}\n${schema.stderr}`;
  const licensesRows = rowsFromD1Json(parseJsonFromOutput(licensesInfo.stdout));
  const licenseColumns = licensesRows.map((row) => String(row.name || ""));
  const missingLicenseColumns = requiredLicenseColumns.filter((column) => !licenseColumns.includes(column));
  const auditRows = rowsFromD1Json(parseJsonFromOutput(auditInfo.stdout));
  const auditColumns = auditRows.map((row) => String(row.name || ""));
  const licenseStatusRows = rowsFromD1Json(parseJsonFromOutput(licenseStatusCounts.stdout));
  const requiredAuditRows = rowsFromD1Json(parseJsonFromOutput(requiredAudit.stdout));
  const foundAuditEvents = new Set(requiredAuditRows.map((row) => String(row.event_type || "")));
  const missingAuditEvents = requiredAuditEvents.filter((event) => !foundAuditEvents.has(event));
  const healthText = JSON.stringify(health.json || {});

  const checks = [
    check(wranglerVersion.ok && /(?:wrangler\s+)?\d+\.\d+\.\d+/i.test(wranglerVersion.stdout), "project-local Wrangler version passes", { exitCode: wranglerVersion.exitCode, stdout: wranglerVersion.stdout }),
    check(whoami.ok, "Cloudflare OAuth through Wrangler passes", { exitCode: whoami.exitCode, stdout: whoami.stdout, stderr: whoami.stderr }),
    check(health.status === 200 && health.json?.ok === true, "live Cloud Bridge health returns HTTP 200 ok", health),
    check(/LICFLOW3/i.test(healthText) && /D1_BOUND/i.test(healthText) && /Cloud Licensing/i.test(healthText), "health includes LICFLOW3, D1_BOUND and Cloud Licensing markers", { health }),
    check(d1List.ok && d1List.stdout.includes(d1Name), "D1 list includes prisma_cloud_semilla", { exitCode: d1List.exitCode, stdout: d1List.stdout }),
    check(migrations.ok, "D1 remote migrations list passes", { exitCode: migrations.exitCode, stdout: migrations.stdout, stderr: migrations.stderr }),
    check(schema.ok, "D1 remote schema read-only query passes", { exitCode: schema.exitCode, stdoutSha256: schema.stdoutSha256 }),
    check(!/NEW\.license_id/i.test(schemaText), "legacy broken trigger NEW.license_id is absent", { stdoutSha256: schema.stdoutSha256 }),
    check(licensesInfo.ok && missingLicenseColumns.length === 0, "licenses table exposes expected legacy-compatible columns", { columns: licenseColumns, missingLicenseColumns }),
    check(licenseStatusCounts.ok && licenseStatusRows.length > 0, "license status counts are readable", { rows: licenseStatusRows }),
    check(auditInfo.ok && auditColumns.includes("event_type"), "audit_events.event_type column is readable", { columns: auditColumns }),
    check(auditCounts.ok, "audit event counts are readable", { exitCode: auditCounts.exitCode, stdoutSha256: auditCounts.stdoutSha256 }),
    check(requiredAudit.ok && missingAuditEvents.length === 0, "required audit event evidence is present", { requiredAuditEvents, foundAuditEvents: Array.from(foundAuditEvents).sort(), missingAuditEvents }),
    check(secretScan.findingsCount === 0, "fine secret scan has zero findings", secretScan)
  ];

  const payload = {
    ok: checks.every((item) => item.status === "PASS"),
    status: checks.every((item) => item.status === "PASS") ? passStatus : "FAIL_BLOCKERS_FOUND",
    checkedAt,
    liveBase,
    workerRoot: repoRel(workerRoot),
    d1Name,
    certificationScope: "Cloudflare/D1/OAuth read-only certification; admin HTTP mutations and customer onboarding production run are separate gates.",
    adminTokenRequired: false,
    deployPerformed: false,
    d1LiveWritePerformed: false,
    d1ReadOnlyQueriesPerformed: true,
    secretsPrinted: false,
    checks,
    commandEvidence: {
      wranglerVersion,
      whoami,
      d1List,
      migrations,
      schema: { ...schema, stdout: "[SANITIZED_HASH_ONLY]", stderr: schema.stderr },
      licensesInfo,
      licenseStatusCounts,
      auditInfo,
      auditCounts: { ...auditCounts, stdout: "[SANITIZED_HASH_ONLY]", stderr: auditCounts.stderr },
      requiredAudit
    },
    failures: checks.filter((item) => item.status === "FAIL")
  };

  const absoluteOut = rel(outPath);
  fs.mkdirSync(path.dirname(absoluteOut), { recursive: true });
  fs.writeFileSync(absoluteOut, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
  console.log(JSON.stringify(payload, null, 2));
  if (!payload.ok) process.exit(1);
}

main().catch((error) => {
  const payload = {
    ok: false,
    status: "FAIL_BLOCKERS_FOUND",
    checkedAt,
    liveBase,
    d1Name,
    adminTokenRequired: false,
    deployPerformed: false,
    d1LiveWritePerformed: false,
    secretsPrinted: false,
    error: sanitizeText(error?.message || error)
  };
  const absoluteOut = rel(outPath);
  fs.mkdirSync(path.dirname(absoluteOut), { recursive: true });
  fs.writeFileSync(absoluteOut, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
  console.error(JSON.stringify(payload, null, 2));
  process.exit(1);
});
