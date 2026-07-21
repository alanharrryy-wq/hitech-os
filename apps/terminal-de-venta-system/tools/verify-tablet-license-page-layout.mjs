#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { reportPaths, terminalRoot, writeJson, writeText } from "../scripts/prisma-codex-utils.mjs";

function read(rel) {
  return fs.readFileSync(path.join(terminalRoot, rel), "utf8");
}

const shell = read("products/tablet/app/components/tablet-shell/prisma-tablet-shell.tsx");
const shellCss = read("products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css");
const settings = read("products/tablet/app/components/settings/settings-workspace.tsx");
const settingsCss = read("products/tablet/app/components/settings/settings-workspace.module.css");
const card = read("products/tablet/app/components/license/license-status-card.tsx");
const refresh = read("products/tablet/app/components/license/license-refresh-panel.tsx");
const licenseCss = read("products/tablet/app/components/license/license-ui.module.css");

const retiredManagementCopy = [
  "Importar licencia local",
  "Abrir License Ops",
  "Exportar diagnóstico",
  "Validar runtime"
];

const checks = [
  {
    name: "settings header has one canonical premium owner",
    status:
      shellCss.includes("PRISMA_TABLET_SETTINGS_POLISH_V3_CANONICAL")
      && (shellCss.match(/PRISMA_TABLET_SETTINGS_POLISH_V3_CANONICAL/g) ?? []).length === 1
      && shellCss.includes(".supportShell .topbar")
      && shellCss.includes("position: sticky")
      && shellCss.includes("backdrop-filter: blur(25px)")
      && shellCss.includes("overflow: visible")
        ? "PASS"
        : "FAIL"
  },
  {
    name: "settings logo is enlarged and not clipped",
    status:
      shellCss.includes(".supportShell .brandMark")
      && shellCss.includes(".supportShell .brandImage")
      && shellCss.includes("width: 54px")
      && shellCss.includes("height: 54px")
      && shellCss.includes("object-fit: contain")
        ? "PASS"
        : "FAIL"
  },
  {
    name: "settings context is informational and bell stays navigational",
    status:
      shell.includes('aria-label="Contexto informativo de la Tablet"')
      && shell.includes('title="Abrir sincronización y notificaciones"')
      && shell.includes("supportSurface ? (")
        ? "PASS"
        : "FAIL"
  },
  {
    name: "vertical settings rail is canonical and semantic",
    status:
      settings.includes("data-accent={section.accent}")
      && settingsCss.includes("PRISMA_TABLET_SETTINGS_WORKSPACE_V3_CANONICAL")
      && settingsCss.includes(".sectionNav")
      && settingsCss.includes(".sectionLinkActive::before")
        ? "PASS"
        : "FAIL"
  },
  {
    name: "customer missing license retains clear pending state",
    status:
      card.includes('status.state === "missing" && context.runtimeMode === "customer"')
      && card.includes("Instalación pendiente de licencia local")
        ? "PASS"
        : "FAIL"
  },
  {
    name: "customer license surface remains read-only without retired management CTAs",
    status:
      card.includes('data-prisma-client-license-view="readonly"')
      && retiredManagementCopy.every((text) => !card.includes(text))
        ? "PASS"
        : "FAIL"
  },
  {
    name: "license refresh remains local-first and read-only",
    status:
      refresh.includes('data-prisma-license-refresh-view="readonly"')
      && refresh.includes("Licencia local primero")
      && refresh.includes("Las acciones avanzadas de licencia quedan agrupadas en soporte")
        ? "PASS"
        : "FAIL"
  },
  {
    name: "refresh failure preserves local policy",
    status:
      refresh.includes("Se conserva la política local vigente")
        ? "PASS"
        : "FAIL"
  },
  {
    name: "license styles use current canonical owners",
    status:
      licenseCss.includes("PRISMA_TABLET_LICENSE_V3_CANONICAL")
      && [".heroCard", ".identityStrip", ".evidenceDisclosure", ".refreshPanel", ".featurePanel", ".featureGroup"]
        .every((selector) => licenseCss.includes(selector))
        ? "PASS"
        : "FAIL"
  },
  {
    name: "retired CTA selectors were not resurrected",
    status:
      [".actionPanel", ".primaryLink", ".secondaryLink"]
        .every((selector) => !licenseCss.includes(selector))
        ? "PASS"
        : "FAIL"
  },
  {
    name: "no governance important rules were introduced",
    status:
      !shellCss.includes("!important")
      && !settingsCss.includes("!important")
      && !licenseCss.includes("!important")
        ? "PASS"
        : "FAIL"
  }
];

const overall = checks.some((item) => item.status === "FAIL") ? "FAIL" : "PASS";
const report = {
  schema: "prisma.tablet.license-page-layout.verify.v3",
  generatedAt: new Date().toISOString(),
  overall,
  contract: "read-only customer license surface + PRISMA Settings Polish V3 canonical owners",
  checks
};

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
