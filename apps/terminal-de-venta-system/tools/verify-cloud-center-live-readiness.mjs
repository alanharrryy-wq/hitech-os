#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const terminalRoot = path.resolve(fileURLToPath(new URL("..", import.meta.url)));
const defaultBaseUrl = "https://app.hitechrts.com";
const baseUrl = (process.env.PRISMA_CLOUD_CENTER_LIVE_URL || defaultBaseUrl).replace(/\/+$/, "");
const outPath = process.argv.find((arg) => arg.startsWith("--out="))?.slice("--out=".length) || "";
const checkedAt = new Date().toISOString();

function rel(file) {
  return path.isAbsolute(file) ? file : path.join(terminalRoot, file);
}

function jsonPreview(value) {
  if (value == null) return null;
  const clone = JSON.parse(JSON.stringify(value));
  return clone;
}

async function requestJson(method, route, body) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 20000);
  try {
    const response = await fetch(`${baseUrl}${route}`, {
      method,
      signal: controller.signal,
      headers: body ? { "content-type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined
    });
    const text = await response.text();
    let json = null;
    try {
      json = text ? JSON.parse(text) : null;
    } catch {
      json = { rawText: text.slice(0, 500) };
    }
    return { route, method, status: response.status, ok: response.ok, json: jsonPreview(json) };
  } finally {
    clearTimeout(timer);
  }
}

function check(condition, name, evidence) {
  return { name, status: condition ? "PASS" : "FAIL", evidence };
}

function hasCapabilities(json, names) {
  return names.every((name) => json?.capabilities?.[name] === true);
}

function adminBlocked(result) {
  if (![401, 403].includes(result.status)) return false;
  const text = JSON.stringify(result.json ?? {});
  return /ADMIN_TOKEN_REQUIRED|admin|token|unauthorized|forbidden/i.test(text);
}

function mutationPrevented(result) {
  if (adminBlocked(result)) return true;
  const body = result.json ?? {};
  return body.safeToMutate === false
    && (body.mutationMode === "simulation" || /SIMULATION|DRY_RUN/i.test(String(body.status ?? body.resultCode ?? "")))
    && body.secretsExposed === false;
}

async function main() {
  const health = await requestJson("GET", "/health");
  const capabilities = await requestJson("GET", "/api/public/capabilities");
  const adminSetupNoToken = await requestJson("POST", "/api/admin/customer-setups/create", {
    dryRun: true,
    source: "codex-live-readonly-guard"
  });
  const adminActivateNoToken = await requestJson("POST", "/api/licenses/activate", {
    dryRun: true,
    tenantSlug: "codex-live-readonly-guard",
    licenseId: "codex-live-readonly-guard"
  });

  const requiredCapabilities = [
    "customerSetup",
    "setupLink",
    "setupQr",
    "planBasedProvisioning",
    "autoGenerateClaimSlots",
    "deviceClaim",
    "multiDeviceSlots",
    "deviceReplacement",
    "customerPortal",
    "customerLicenseRefresh",
    "billingRenewal",
    "gracePeriod"
  ];

  const checks = [
    check(health.status === 200 && health.json?.ok === true, "live health returns 200 ok", health),
    check(health.json?.dbHealth === "D1_BOUND", "live D1 binding is reported", { dbHealth: health.json?.dbHealth, counts: health.json?.counts ?? null }),
    check(capabilities.status === 200 && capabilities.json?.ok === true, "live capabilities returns 200 ok", capabilities),
    check(hasCapabilities(capabilities.json, requiredCapabilities), "live capabilities include customer setup, slots, claims and renewal", { requiredCapabilities, capabilities: capabilities.json?.capabilities ?? null }),
    check(mutationPrevented(adminSetupNoToken), "admin customer setup is blocked or simulation-only without token", adminSetupNoToken),
    check(mutationPrevented(adminActivateNoToken), "admin license activation is blocked or simulation-only without token", adminActivateNoToken)
  ];

  const payload = {
    ok: checks.every((item) => item.status === "PASS"),
    status: checks.every((item) => item.status === "PASS") ? "PASS_PUBLIC_LIVE_READONLY" : "FAIL",
    checkedAt,
    baseUrl,
    authenticated: false,
    adminMutationPerformed: false,
    d1MutationPerformed: false,
    secretsPrinted: false,
    checks,
    failures: checks.filter((item) => item.status === "FAIL")
  };

  if (outPath) {
    const absoluteOut = rel(outPath);
    fs.mkdirSync(path.dirname(absoluteOut), { recursive: true });
    fs.writeFileSync(absoluteOut, `${JSON.stringify(payload, null, 2)}\n`);
  }

  console.log(JSON.stringify(payload, null, 2));
  if (!payload.ok) process.exit(1);
}

main().catch((error) => {
  console.error(JSON.stringify({
    ok: false,
    status: "FAIL",
    checkedAt,
    baseUrl,
    authenticated: false,
    adminMutationPerformed: false,
    d1MutationPerformed: false,
    secretsPrinted: false,
    error: String(error?.message || error)
  }, null, 2));
  process.exit(1);
});
