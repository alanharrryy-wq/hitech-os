#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const toolsDir = path.dirname(__filename);
const appRoot = path.resolve(toolsDir, "..");

function exists(p) {
  return fs.existsSync(p);
}

function read(p) {
  return fs.readFileSync(p, "utf8");
}

function readJson(p) {
  return JSON.parse(read(p));
}

const checks = [];
function check(id, ok, detail) {
  checks.push({ id, ok, detail });
}

const files = {
  checkoutPage: path.join(appRoot, "app", "checkout", "page.tsx"),
  searchRoute: path.join(appRoot, "app", "api", "pos", "products", "search", "route.ts"),
  resolveRoute: path.join(appRoot, "app", "api", "pos", "products", "resolve", "route.ts"),
  contextualExport: path.join(appRoot, "app", "api", "pos", "export", "contextual", "route.ts"),
  success: path.join(appRoot, "components", "pos", "pos-sale-success.tsx"),
  css: path.join(appRoot, "components", "pos", "pos.module.css"),
  localCatalog: path.join(appRoot, "src", "server", "local-catalog", "index.ts"),
  workflow: path.join(appRoot, "docs", "qa", "TABLET_LOCAL_PY_WORKFLOW_CONTRACT.md"),
  qa: path.join(appRoot, "docs", "qa", "TABLET_03_POS_UNIFICADO.md"),
  pkg: path.join(appRoot, "package.json"),
};

for (const [key, file] of Object.entries(files)) {
  check(`T03-EXISTS-${key}`, exists(file), file);
}

if (exists(files.checkoutPage)) {
  const text = read(files.checkoutPage);
  check("T03-001 checkout renders PosScreen", text.includes("PosScreen") && !text.includes("CheckoutScreen"), files.checkoutPage);
  check("T03-002 checkout metadata says unified", text.includes("Cobro unificado"), files.checkoutPage);
}

if (exists(files.searchRoute)) {
  const text = read(files.searchRoute);
  check("T03-003 search imports local catalog", text.includes("listLocalCatalogProducts"), files.searchRoute);
  check("T03-004 search fallback source local catalog", text.includes("source: \"local-catalog\"") || text.includes('source = "local-catalog"'), files.searchRoute);
}

if (exists(files.resolveRoute)) {
  const text = read(files.resolveRoute);
  check("T03-005 resolve imports local catalog", text.includes("resolveLocalCatalogProduct"), files.resolveRoute);
  check("T03-006 resolve local fallback before not found", text.includes("localProduct") && text.indexOf("resolveLocalCatalogProduct") < text.indexOf("PRODUCT_NOT_FOUND"), files.resolveRoute);
}

if (exists(files.success)) {
  const text = read(files.success);
  check("T03-007 success imports Link", text.includes("next/link"), files.success);
  check("T03-008 success has Ver detalle", text.includes("Ver detalle"), files.success);
  check("T03-009 success links to sales detail", text.includes("/sales/today/") && text.includes("encodeURIComponent"), files.success);
}

if (exists(files.contextualExport)) {
  const text = read(files.contextualExport);
  check("T03-010 no biz_demo_001 in contextual export", !text.includes("biz_demo_001"), files.contextualExport);
  check("T03-011 export uses DEFAULT_POS_API_BUSINESS_ID", text.includes("DEFAULT_POS_API_BUSINESS_ID"), files.contextualExport);
}

if (exists(files.css)) {
  const text = read(files.css);
  check("T03-012 css successActions exists", text.includes("successActions"), files.css);
  check("T03-013 css secondaryButton exists", text.includes("secondaryButton"), files.css);
}

if (exists(files.workflow)) {
  const text = read(files.workflow);
  check("T03-014 workflow one py", text.includes("un solo `.py` autocontenido"), files.workflow);
  check("T03-015 workflow run rollback", text.includes("--run") && text.includes("--rollback"), files.workflow);
  check("T03-016 workflow descargas", text.includes("F:\\descargasf"), files.workflow);
}

if (exists(files.pkg)) {
  const pkg = readJson(files.pkg);
  const scripts = pkg.scripts || {};
  check("T03-017 script tablet:03:pos exists", Boolean(scripts["tablet:03:pos"]), files.pkg);
  check("T03-018 script verify:03-pos exists", Boolean(scripts["verify:03-pos"]), files.pkg);
}

const ok = checks.every((item) => item.ok);
const evidenceDir = path.join(appRoot, "evidence", "verifier-output");
fs.mkdirSync(evidenceDir, { recursive: true });
const report = {
  ok,
  appRoot,
  checks,
  verdict: ok ? "PASS" : "FAIL",
  note: "T03 verifies POS/checkout unification, local catalog fallback for product lookup, ticket detail CTA after sale, and biz_demo_001 removal from contextual export."
};
fs.writeFileSync(path.join(evidenceDir, "verify_tablet_03_pos_unificado.json"), JSON.stringify(report, null, 2) + "\n", "utf8");
console.log(JSON.stringify(report, null, 2));
process.exit(ok ? 0 : 2);
