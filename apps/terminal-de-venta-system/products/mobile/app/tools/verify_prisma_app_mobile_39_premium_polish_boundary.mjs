#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
const root = process.cwd();
const phase = "MOBILE_PREMIUM_POLISH_PHASE_2";
function fail(message, extra = {}) { console.error(JSON.stringify({ ok: false, phase, message, ...extra }, null, 2)); process.exit(1); }
function read(rel) { const full = path.join(root, rel); if (!fs.existsSync(full)) fail("Missing required file", { rel }); return fs.readFileSync(full, "utf8"); }
const files = {
  pkg: "package.json",
  dashboard: "src/components/prisma-app/PrismaMobileDashboard.tsx",
  navigator: "src/components/prisma-app/PrismaMobilePremiumNavigator.tsx",
  css: "src/components/prisma-app/prisma-mobile-dashboard.module.css",
  globals: "app/globals.css",
  doc: "docs/prisma-app/PRISMA_APP_MOBILE_39_PREMIUM_POLISH.md",
  qa: "docs/prisma-app/qa/prisma-app-mobile-39-premium-polish-scenarios.json",
  addendum: "docs/atlas/ATLAS_MOBILE_PREMIUM_POLISH_V12_ADDENDUM.md",
  rollback: "docs/atlas/ATLAS_MOBILE_PREMIUM_POLISH_V12_ROLLBACK.md",
  mark: "public/prisma-mobile-premium-mark.svg",
  icon: "public/prisma-mobile-maskable-icon.svg"
};
const text = Object.values(files).map(read).join("\n");
const required = ["MOBILE_PREMIUM_POLISH_PHASE_2", "PRISMA_APP_MOBILE_39_PREMIUM_POLISH", "PRISMA_MOBILE_PREMIUM_POLISH_GLOBALS", "mobile-premium-polish", "Mobile supervisa", "Tablet Solo vende sola", "Mobile no es requisito para vender", "Mobile no bloquea POS", "PC y Mobile son adders opcionales", "Cloudflare y soporte remoto son opcionales", "Internet no es requisito para venta base Tablet Solo"];
for (const token of required) if (!text.includes(token)) fail("Missing premium polish token", { token });
const forbiddenParts = [
  ["Mobile", " requerido para operar"],
  ["Conecta la app", " móvil para vender"],
  ["Supervisión", " móvil obligatoria"],
  ["Cloudflare", " requerido"],
  ["Internet", " requerido para venta base"],
  ["PC o Mobile", " requeridos para licencia base"],
  ["Mobile", " bloquea POS"],
  ["Mobile", " bloquea cobro"],
  ["Mobile", " bloquea corte"],
  ["Mobile", " bloquea ticket"],
  ["Mobile", " bloquea licencia local"],
  ["Mobile", " bloquea operación offline"]
];
const forbidden = forbiddenParts.map((parts) => parts.join(""));
for (const token of forbidden) if (text.includes(token)) fail("Forbidden dependency copy found", { token });
const pkg = JSON.parse(read(files.pkg));
if (!pkg.scripts || pkg.scripts["verify:premium-polish-boundary"] !== "node tools/verify_prisma_app_mobile_39_premium_polish_boundary.mjs") fail("Missing package script verify:premium-polish-boundary");
console.log(JSON.stringify({ ok: true, phase, message: "Mobile premium polish verified without Tablet dependency." }, null, 2));
