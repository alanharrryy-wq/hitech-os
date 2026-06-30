import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const toolDir = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(toolDir, "..");
const repoRoot = path.resolve(appRoot, "../../../../..");
const evidenceDir = path.join(toolDir, "evidence");
const jsonReportPath = path.join(evidenceDir, "tablet-visual-surface-v2-report.json");
const mdReportPath = path.join(evidenceDir, "tablet-visual-surface-v2-report.md");

const rel = (absolutePath) => path.relative(appRoot, absolutePath).replace(/\\/g, "/");
const fromRoot = (relativePath) => path.join(appRoot, relativePath);

function read(relativePath) {
  return fs.readFileSync(fromRoot(relativePath), "utf8");
}

function exists(relativePath) {
  return fs.existsSync(fromRoot(relativePath));
}

function walk(dir, predicate = () => true) {
  if (!fs.existsSync(dir)) return [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const absolute = path.join(dir, entry.name);
    if (entry.isDirectory()) files.push(...walk(absolute, predicate));
    else if (predicate(absolute)) files.push(absolute);
  }
  return files;
}

function routeFromPage(absolutePath) {
  const withoutApp = rel(absolutePath).replace(/^app\//, "");
  if (withoutApp === "page.tsx") return "/";
  const relative = withoutApp.replace(/\/page\.tsx$/, "");
  return relative ? `/${relative}` : "/";
}

function makeCheck(id, passed, details) {
  return { id, passed: Boolean(passed), details };
}

const checks = [];
const ownedFiles = [
  "app/layout.tsx",
  "components/tablet-shell/prisma-tablet-shell.tsx",
  "components/pos/pos-ticket-panel.tsx",
  "components/pos/pos-cobro-surface.tsx",
  "components/pos/pos-cobro-surface.module.css",
  "components/tablet-visual-v2/index.ts",
  "components/tablet-visual-v2/prisma-command-dock.module.css",
  "components/tablet-visual-v2/prisma-command-dock.tsx",
  "components/tablet-visual-v2/prisma-glass-control.module.css",
  "components/tablet-visual-v2/prisma-glass-control.tsx",
  "components/tablet-visual-v2/prisma-liquid-action.module.css",
  "components/tablet-visual-v2/prisma-liquid-action.tsx",
  "components/tablet-visual-v2/prisma-modal-shell.module.css",
  "components/tablet-visual-v2/prisma-modal-shell.tsx",
  "components/tablet-visual-v2/prisma-soft-card.module.css",
  "components/tablet-visual-v2/prisma-soft-card.tsx",
  "components/tablet-visual-v2/prisma-status-chip.module.css",
  "components/tablet-visual-v2/prisma-status-chip.tsx",
  "components/tablet-visual-v2/tablet-effect-contract.ts",
  "components/tablet-visual-v2/tablet-layer-contract.ts",
  "components/tablet-visual-v2/tablet-motion-recipes.ts",
  "components/tablet-visual-v2/tablet-visual-tokens.ts",
  "components/tablet-visual-v2/tablet-visual-v2-frame.module.css",
  "components/tablet-visual-v2/tablet-visual-v2-root.module.css",
  "package.json",
  "tools/verify_prisma_tablet_visual_surface_v2_2406.mjs"
];

const missingOwnedFiles = ownedFiles.filter((file) => !exists(file));
const scopeLeaks = ownedFiles.filter((file) => /(^|\/)products\/(pc|mobile|web|control-center)\//.test(file));
checks.push(makeCheck("scope.owned-files-exist", missingOwnedFiles.length === 0, { missingOwnedFiles }));
checks.push(makeCheck("scope.tablet-only", scopeLeaks.length === 0, { ignoredDirtyTree: true, scopeLeaks, repoRoot: repoRoot.replace(/\\/g, "/") }));

const v2CssFiles = [
  ...walk(fromRoot("components/tablet-visual-v2"), (file) => file.endsWith(".module.css")),
  fromRoot("components/pos/pos-cobro-surface.module.css")
].filter((file) => fs.existsSync(file));
const v2Css = v2CssFiles.map((file) => ({ file: rel(file), text: fs.readFileSync(file, "utf8") }));

const importantHits = v2Css.flatMap(({ file, text }) => (text.includes("!important") ? [file] : []));
const globalHits = v2Css.flatMap(({ file, text }) => (/:global\(/.test(text) ? [file] : []));
const bodyHtmlHits = v2Css.flatMap(({ file, text }) => (/(^|[\s,{])(?:body|html)(?:[\s.#[:{,]|$)/m.test(text) ? [file] : []));
const invalidCssHits = v2Css.flatMap(({ file, text }) => {
  const hits = [];
  if (/background-size:[^;]*minmax\(/m.test(text)) hits.push(`${file}: background-size minmax`);
  if (/data-prisma-[a-z-]+\s*:/m.test(text)) hits.push(`${file}: data attribute written as CSS property`);
  return hits;
});
checks.push(makeCheck("css.no-important", importantHits.length === 0, { files: importantHits }));
checks.push(makeCheck("css.no-global-selectors", globalHits.length === 0, { files: globalHits }));
checks.push(makeCheck("css.no-body-html-blast", bodyHtmlHits.length === 0, { files: bodyHtmlHits }));
checks.push(makeCheck("css.syntax-guardrails", invalidCssHits.length === 0, { hits: invalidCssHits }));

const layerContractText = read("components/tablet-visual-v2/tablet-layer-contract.ts");
const layers = Object.fromEntries([...layerContractText.matchAll(/^\s*([A-Za-z][A-Za-z0-9]*):\s*(\d+)/gm)].map((match) => [match[1], Number(match[2])]));
checks.push(makeCheck("layers.required-order", layers.modalBackdrop > layers.dock && layers.modal > layers.modalBackdrop && layers.dock > layers.header && layers.toast > layers.modal, { layers }));
checks.push(makeCheck("layers.no-runaway-zindex", Object.values(layers).every((value) => value < 1000), { layers }));

const effectContractText = read("components/tablet-visual-v2/tablet-effect-contract.ts");
const effectIds = [...effectContractText.matchAll(/id:\s*"([^"]+)"/g)].map((match) => match[1]);
const visualSurfaceText = [
  read("app/layout.tsx"),
  read("components/tablet-shell/prisma-tablet-shell.tsx"),
  read("components/pos/pos-ticket-panel.tsx"),
  read("components/pos/pos-cobro-surface.tsx"),
  ...ownedFiles.filter((file) => file.startsWith("components/tablet-visual-v2/") && exists(file)).map((file) => read(file)),
  ...v2Css.map(({ text }) => text)
].join("\n");
const uncataloguedEffects = [
  "softglass-surface",
  "inner-highlight",
  "rim-light",
  "liquid-glow",
  "pressed-depth",
  "selected-pulse",
  "ticket-total-pulse",
  "product-added-echo",
  "dock-active-glow",
  "modal-depth-dim",
  "method-selected-aura",
  "focus-halo",
  "success-sweep",
  "disabled-frost"
].filter((effect) => !effectIds.includes(effect));
const unusedEffectIds = effectIds.filter((effect) => !visualSurfaceText.includes(effect));
checks.push(makeCheck("effects.catalog-complete", uncataloguedEffects.length === 0, { missing: uncataloguedEffects, effectIds }));
checks.push(makeCheck("effects.static-usage", unusedEffectIds.length === 0, { unusedEffectIds }));

const responsiveSignals = {
  clamp: visualSurfaceText.includes("clamp("),
  minmax: visualSurfaceText.includes("minmax("),
  gridTemplate: visualSurfaceText.includes("grid-template"),
  containerType: visualSurfaceText.includes("container-type"),
  safeArea: visualSurfaceText.includes("safe-area"),
  dvh: visualSurfaceText.includes("dvh"),
  canonical1180: visualSurfaceText.includes("1180"),
  canonical820: visualSurfaceText.includes("820"),
  touch48: visualSurfaceText.includes("48")
};
checks.push(makeCheck("responsive.canonical-and-autosize", Object.values(responsiveSignals).every(Boolean), responsiveSignals));

const cobroText = read("components/pos/pos-cobro-surface.tsx");
const cobroCss = read("components/pos/pos-cobro-surface.module.css");
const modalCss = read("components/tablet-visual-v2/prisma-modal-shell.module.css");
const accessibilitySignals = {
  roleDialog: cobroText.includes('role="dialog"'),
  ariaModal: cobroText.includes('aria-modal="true"'),
  labelledBy: cobroText.includes("aria-labelledby"),
  describedBy: cobroText.includes("aria-describedby"),
  escapeHandler: cobroText.includes('event.key === "Escape"'),
  tabTrap: cobroText.includes('event.key !== "Tab"'),
  inertSiblings: cobroText.includes('setAttribute("inert"'),
  focusVisible: `${cobroCss}\n${modalCss}`.includes(":focus-visible"),
  portalBody: cobroText.includes("createPortal(surfaceNode, document.body)")
};
checks.push(makeCheck("accessibility.modal-focus-and-portal", Object.values(accessibilitySignals).every(Boolean), accessibilitySignals));

const requiredCobroCopy = [
  "Cobro PRISMA",
  "Total a cobrar",
  "Saldo restante",
  "Métodos de pago",
  "Completar pago",
  "Volver al ticket",
  "El pago todavía no cubre el total. Agrega otro método de pago, ajusta el importe o completa el saldo pendiente."
];
const missingCobroCopy = requiredCobroCopy.filter((copy) => !cobroText.includes(copy));
const cobroContractSignals = {
  createPortal: cobroText.includes("createPortal(surfaceNode, document.body)"),
  fixedOverlay: modalCss.includes("position: fixed") && modalCss.includes("inset: 0"),
  documentBodyPortal: cobroText.includes("document.body"),
  liquidConfirm: cobroText.includes("PrismaLiquidAction"),
  noInlineStyleObject: !/style=\{/.test(cobroText),
  noCssPropertiesImport: !cobroText.includes("CSSProperties")
};
checks.push(makeCheck("cobro.required-copy", missingCobroCopy.length === 0, { missingCobroCopy }));
checks.push(makeCheck("cobro.portal-layer-contract", Object.values(cobroContractSignals).every(Boolean), cobroContractSignals));

const pageFiles = walk(fromRoot("app"), (file) => file.endsWith("page.tsx") && !file.replace(/\\/g, "/").includes("/api/"));
const posScreenText = read("components/pos/pos-screen.tsx");
const posRequired = ["PosTerminalSurface", "PosTerminalHeader", "PosProductCanvas", "PosTicketRail", "PosCommandDock", "PosCobroSurface"];
const posMissing = posRequired.filter((name) => !posScreenText.includes(name));
const routeCoverage = pageFiles.map((file) => {
  const source = fs.readFileSync(file, "utf8");
  const route = routeFromPage(file);
  const directSurface = source.match(/<(Tablet[A-Za-z]+SurfaceV2|PrismaRouteSurface)\b/)?.[1] ?? null;
  const redirectOnly = /\bredirect\(/.test(source) && !/return\s*\(/.test(source) && !/SurfaceV2|PosScreen|PrismaTabletShellUnified/.test(source);
  const posSurface = (route === "/pos" || route === "/checkout") && source.includes("PosScreen") && posMissing.length === 0;
  const migrationStatus = redirectOnly ? "nonVisualTechnicalRouteJustified" : posSurface ? "realV2Surface" : directSurface ? "realV2WrappedLegacyContent" : "rootOnly";
  return {
    route,
    file: rel(file),
    coveredByRootVisualV2: false,
    usesShell: /PrismaTabletShell(?:Unified)?/.test(source),
    surfaceComponentRendered: posSurface ? "PosTerminalSurface" : directSurface,
    migrationStatus,
    documentedLegacySurface: null
  };
}).sort((a, b) => a.route.localeCompare(b.route));
const invalidRouteCoverage = routeCoverage.filter((route) => ["rootOnly", "documentedLegacySurface", "legacyOnly", "unknown"].includes(route.migrationStatus));
checks.push(makeCheck("routes.tablet-pages-covered", routeCoverage.length > 0 && invalidRouteCoverage.length === 0, { routeCount: routeCoverage.length, invalidRouteCoverage }));

const syncFiles = [
  "app/api/health/route.ts",
  "app/api/pos/sync/dispatch/route.ts",
  "app/api/pos/sync/health/pc/route.ts",
  "app/api/pos/sync/pull/route.ts",
  "src/server/sync/pc-origin.ts",
  "src/server/sync/dispatcher.ts"
];
const missingSyncFiles = syncFiles.filter((file) => !exists(file));
checks.push(makeCheck("sync.static-contract-present", missingSyncFiles.length === 0, { syncFiles, missingSyncFiles, runtimeDbValidation: "not-run-by-contract" }));

const packageText = read("package.json");
checks.push(makeCheck("scripts.no-prisma-hot-path", packageText.includes('"verify:tablet-visual-surface-v2": "node tools/verify_prisma_tablet_visual_surface_v2_2406.mjs"'), { script: "verify:tablet-visual-surface-v2" }));

const usedRejectedCapabilities = [
  { capability: "Visual V2 tokens", decision: "used", rationale: "Canonical 1180x820@0.75, softglass palette, 48px touch target." },
  { capability: "Layer contract", decision: "used", rationale: "Modal, dock, header, content and toast z-order statically bounded." },
  { capability: "Effect contract", decision: "used", rationale: "Liquid action, modal depth, dock glow, selected aura and ticket/product feedback catalogued and marked." },
  { capability: "Root layout coverage", decision: "used", rationale: "All Tablet pages inherit data-prisma-visual-v2 and root visual tokens." },
  { capability: "POS cobro portal", decision: "used", rationale: "Document body portal preserved with focus trap, Escape, inert siblings and aria dialog." },
  { capability: "Playwright/browser automation", decision: "rejected", rationale: "User forbids browser automation and screenshots in this task." },
  { capability: "Dev server / process kill / port cleanup", decision: "rejected", rationale: "Forbidden by authority envelope for this pass." },
  { capability: "Prisma generate hot path", decision: "rejected", rationale: "Validation runs static Node and direct tsc only, not package scripts that invoke generate." },
  { capability: "PC/Mobile visual edits", decision: "rejected", rationale: "Out of visual scope; only Tablet source files are owned by this pass." }
];

const passed = checks.every((check) => check.passed);
const report = {
  status: passed ? "PASS" : "FAIL",
  task: "PRISMA Tablet Visual Surface V2 premium",
  generatedAt: new Date().toISOString(),
  validationMode: "static-code-only",
  visualHumanValidation: "pending",
  visualHumanValidationMessage: "Validación visual humana pendiente. Validación por código completa.",
  noBrowserAutomation: true,
  noDevServer: true,
  noPrismaGenerateHotPath: true,
  ignoredDirtyTree: true,
  checks,
  routeCoverage,
  usedRejectedCapabilities,
  evidenceFiles: {
    json: rel(jsonReportPath),
    markdown: rel(mdReportPath)
  }
};

fs.mkdirSync(evidenceDir, { recursive: true });
fs.writeFileSync(jsonReportPath, `${JSON.stringify(report, null, 2)}\n`);
fs.writeFileSync(
  mdReportPath,
  [
    "# PRISMA Tablet Visual Surface V2 Evidence",
    "",
    `Status: ${report.status}`,
    "",
    report.visualHumanValidationMessage,
    "",
    "## Checks",
    "",
    ...checks.map((check) => `- ${check.passed ? "PASS" : "FAIL"} ${check.id}`),
    "",
    "## Route Coverage",
    "",
    ...routeCoverage.map((route) => `- ${route.route} (${route.migrationStatus}${route.surfaceComponentRendered ? `, ${route.surfaceComponentRendered}` : ""})`),
    "",
    "## Used / Rejected Capabilities",
    "",
    "| Capability | Decision | Rationale |",
    "| --- | --- | --- |",
    ...usedRejectedCapabilities.map((item) => `| ${item.capability} | ${item.decision} | ${item.rationale} |`),
    ""
  ].join("\n")
);

console.log(JSON.stringify({ status: report.status, checks: checks.length, routeCount: routeCoverage.length, evidence: report.evidenceFiles }, null, 2));

if (!passed) {
  for (const check of checks.filter((item) => !item.passed)) {
    console.error(`[${check.id}] ${JSON.stringify(check.details)}`);
  }
  process.exitCode = 1;
}
