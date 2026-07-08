#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";

const repo = process.cwd();
const api = "apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/py/support_resolver_api.py";
if (!existsSync(api)) {
  console.error(JSON.stringify({ ok: false, error: `missing ${api}` }, null, 2));
  process.exit(1);
}
const code = String.raw`
import json, sys
sys.path.insert(0, r"apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/py")
import support_resolver_api as s
payload = {
  "selectedAuthority": "setup_claim_or_refresh",
  "authorityStrategy": "setup_claim_or_refresh",
  "surface": "tablet",
  "businessId": "biz_prisma_rey_lineage_seed",
  "customer": {
    "displayName": "Prisma Original Customer",
    "customerId": "cust_prisma_original_customer",
    "tenantId": "tenant_prisma_original_customer",
    "licenseId": "lic_prisma_original_customer_001",
    "planLabel": "Tablet + PC Managed",
    "businessId": "biz_78b3c840796a4a4dad",
    "storeId": "store_00728649f3804a9e82",
    "tabletTerminalId": "term_49103c7382d84663a3",
    "tabletDeviceId": "tablet_prisma_original_customer_001",
    "pcDeviceId": "pc_prisma_original_customer_001",
    "mobileDeviceId": "mobile_prisma_original_customer_001"
  },
  "license": {"customerId": "cust_demo", "businessId": "biz_demo", "licenseId": "lic_demo_tablet_pro", "plan": "TABLET_PRO"},
  "runtime": {"businessId": "biz_prisma_rey_lineage_seed", "storeId": "store_prisma_rey_centro", "terminalId": "term_tablet_pos_001", "deviceId": "tablet-pos-source-ready"}
}
out = s.support_payload('/api/support/resolve/simulate', method='POST', body=payload)
print(json.dumps(out, ensure_ascii=False))
`;
const py = spawnSync("py", ["-3", "-c", code], { cwd: repo, encoding: "utf8" });
const run = py.error ? spawnSync("python", ["-c", code], { cwd: repo, encoding: "utf8" }) : py;
if (run.error || run.status !== 0) {
  console.error(JSON.stringify({ ok: false, error: run.error?.message || run.stderr || `python status ${run.status}` }, null, 2));
  process.exit(1);
}
let out;
try { out = JSON.parse(run.stdout); } catch (err) {
  console.error(JSON.stringify({ ok: false, error: `invalid json: ${err.message}`, stdout: run.stdout, stderr: run.stderr }, null, 2));
  process.exit(1);
}
const guide = out.guidedResolution;
const checks = {
  ok: true,
  resultCode: out.resultCode,
  primaryIssueCode: out.primaryIssueCode,
  hasGuidedResolution: Boolean(guide && guide.id === "setup_claim_or_refresh"),
  wouldMutate: out.wouldMutate,
  safeToApply: out.safeToApply,
  rollbackAvailable: out.rollbackAvailable,
  requiresSetupCode: Boolean(guide?.requiredInputs?.some((x) => x.id === "setupCode")),
  blocksSignedLicenseEdit: Boolean(guide?.blockedActions?.includes("edit_signed_license")),
  secretsExposed: Boolean(out.secretsExposed || guide?.secretsExposed)
};
const pass = checks.resultCode === "SETUP_CLAIM_OR_REFRESH_GUIDED"
  && checks.primaryIssueCode === "CROSS_SOURCE_IDENTITY_SPLIT"
  && checks.hasGuidedResolution
  && checks.wouldMutate === false
  && checks.safeToApply === false
  && checks.rollbackAvailable === false
  && checks.requiresSetupCode
  && checks.blocksSignedLicenseEdit
  && checks.secretsExposed === false;
console.log(JSON.stringify(checks, null, 2));
process.exit(pass ? 0 : 1);
