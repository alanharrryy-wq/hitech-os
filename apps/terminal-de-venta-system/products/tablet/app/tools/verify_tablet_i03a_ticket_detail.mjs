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

const route = path.join(appRoot, "app", "api", "pos", "sales", "detail", "route.ts");
const screen = path.join(appRoot, "components", "sales", "sales-ticket-detail-screen.tsx");
const list = path.join(appRoot, "components", "sales", "sales-ticket-list.tsx");
const css = path.join(appRoot, "components", "sales", "sales.module.css");
const workflow = path.join(appRoot, "docs", "qa", "TABLET_LOCAL_PY_WORKFLOW_CONTRACT.md");
const qa = path.join(appRoot, "docs", "qa", "TABLET_I03A_TICKET_DETAIL_HOTFIX.md");
const pkgPath = path.join(appRoot, "package.json");

check("I03A-001 sales detail route exists", exists(route), route);
check("I03A-002 detail screen exists", exists(screen), screen);
check("I03A-003 ticket list exists", exists(list), list);
check("I03A-004 sales css exists", exists(css), css);
check("I03A-005 workflow contract doc exists", exists(workflow), workflow);
check("I03A-006 QA doc exists", exists(qa), qa);

if (exists(route)) {
  const text = read(route);
  check("I03A-007 route uses getSaleDetail", text.includes("getSaleDetail"), route);
  check("I03A-008 route supports saleId/folio", text.includes("saleId") && text.includes("folio"), route);
  check("I03A-009 route returns SALE_NOT_FOUND", text.includes("SALE_NOT_FOUND"), route);
}

if (exists(screen)) {
  const text = read(screen);
  check("I03A-010 screen calls direct detail endpoint", text.includes("/api/pos/sales/detail?") && text.includes("params.toString()"), screen);
  check("I03A-011 screen handles not_found", text.includes('status: "not_found"') || text.includes("SALE_NOT_FOUND"), screen);
  check("I03A-012 screen handles error", text.includes('status: "error"') && text.includes("No se pudo abrir"), screen);
  check("I03A-013 loading is not permanent-only state", text.includes("setState(asHumanError(error))"), screen);
  check("I03A-014 screen renders ticket lines", text.includes("state.ticket.lines.map"), screen);
}

if (exists(list)) {
  const text = read(list);
  check("I03A-015 list uses Next Link", text.includes("next/link") && text.includes("<Link"), list);
  check("I03A-016 list links to encoded ticket identity", text.includes("encodeURIComponent(ticket.folio || ticket.saleId)") || text.includes("encodeURIComponent(ticket.saleId"), list);
  check("I03A-017 list has aria label", text.includes("aria-label"), list);
}

if (exists(css)) {
  const text = read(css);
  check("I03A-018 css has interactive ticket focus", text.includes("ticketRow:focus-visible"), css);
  check("I03A-019 css has state card", text.includes("stateCard"), css);
}

if (exists(workflow)) {
  const text = read(workflow);
  check("I03A-020 workflow says one py", text.includes("un solo `.py` autocontenido"), workflow);
  check("I03A-021 workflow says --run", text.includes("--run"), workflow);
  check("I03A-022 workflow says --rollback", text.includes("--rollback"), workflow);
  check("I03A-023 workflow says F:\\descargasf", text.includes("F:\\descargasf"), workflow);
}

if (exists(pkgPath)) {
  const pkg = readJson(pkgPath);
  const scripts = pkg.scripts || {};
  check("I03A-024 package script verify:i03a-ticket-detail exists", Boolean(scripts["verify:i03a-ticket-detail"]), pkgPath);
  check("I03A-025 package script tablet:i03a:ticket-detail exists", Boolean(scripts["tablet:i03a:ticket-detail"]), pkgPath);
}

const ok = checks.every((item) => item.ok);
const evidenceDir = path.join(appRoot, "evidence", "verifier-output");
fs.mkdirSync(evidenceDir, { recursive: true });
const report = {
  ok,
  appRoot,
  checks,
  verdict: ok ? "PASS" : "FAIL",
  note: "I03A verifies direct ticket detail route, visible error/not_found states, clickable ticket rows, and local .py workflow contract."
};
fs.writeFileSync(path.join(evidenceDir, "verify_tablet_i03a_ticket_detail.json"), JSON.stringify(report, null, 2) + "\n", "utf8");
console.log(JSON.stringify(report, null, 2));
process.exit(ok ? 0 : 2);
