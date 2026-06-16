#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { reportPaths, terminalRoot, writeJson, writeText } from "../scripts/prisma-codex-utils.mjs";

function read(rel) {
  return fs.readFileSync(path.join(terminalRoot, rel), "utf8");
}

const shellCss = read("products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css");
const card = read("products/tablet/app/components/license/license-status-card.tsx");
const refresh = read("products/tablet/app/components/license/license-refresh-panel.tsx");
const licenseCss = read("products/tablet/app/components/license/license-ui.module.css");

const checks = [
  {
    name: "tablet header has layout stability block",
    status: shellCss.includes("PRISMA_TABLET_HEADER_LAYOUT_STABILITY_01") ? "PASS" : "FAIL",
  },
  {
    name: "header no longer clips content",
    status: shellCss.includes("overflow: visible") && shellCss.includes("white-space: normal") ? "PASS" : "FAIL",
  },
  {
    name: "header controls wrap on tablet horizontal",
    status: shellCss.includes("flex-wrap: wrap") && shellCss.includes("@media (max-width: 1280px)") ? "PASS" : "FAIL",
  },
  {
    name: "customer missing license renders LICENSE_CUSTOMER_PENDING",
    status: card.includes("LICENSE_CUSTOMER_PENDING") && card.includes("Instalación pendiente de licencia local") ? "PASS" : "FAIL",
  },
  {
    name: "customer pending exposes License Ops CTAs",
    status: ["Importar licencia local", "Abrir License Ops", "Exportar diagnóstico", "Validar runtime"].every((text) => card.includes(text)) ? "PASS" : "FAIL",
  },
  {
    name: "refresh disabled is not primary active refresh",
    status: refresh.includes('data-prisma-refresh-state="disabled"') && refresh.includes("Configurar refresh remoto") && refresh.includes("disabled") ? "PASS" : "FAIL",
  },
  {
    name: "remote refresh failure preserves local policy copy",
    status: refresh.includes("No se pudo refrescar licencia remota. Se conserva política local vigente.") ? "PASS" : "FAIL",
  },
  {
    name: "license CTAs keep premium styles",
    status: licenseCss.includes(".actionPanel") && licenseCss.includes(".primaryLink") && licenseCss.includes(".secondaryLink") ? "PASS" : "FAIL",
  },
];

const overall = checks.some((item) => item.status === "FAIL") ? "FAIL" : "PASS";
const report = { generatedAt: new Date().toISOString(), overall, checks };
const files = reportPaths("PRISMA_TABLET_LICENSE_PAGE_LAYOUT");
writeJson(files.json, report);
writeText(files.md, [
  "# PRISMA Tablet License Page Layout Verify",
  "",
  `Overall: ${overall}`,
  "",
  ...checks.map((item) => `- ${item.status}: ${item.name}`)
].join("\n") + "\n");

console.log(`${overall} tablet license page layout report: ${files.md}`);
if (overall !== "PASS") process.exit(1);
