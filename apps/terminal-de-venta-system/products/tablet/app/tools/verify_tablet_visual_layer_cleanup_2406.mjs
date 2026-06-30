import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const toolDir = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(toolDir, "..");
const evidenceDir = path.join(toolDir, "evidence");
const jsonReportPath = path.join(evidenceDir, "tablet-visual-layer-cleanup-report.json");
const mdReportPath = path.join(evidenceDir, "tablet-visual-layer-cleanup-report.md");

const rel = (absolutePath) => path.relative(appRoot, absolutePath).replace(/\\/g, "/");
const fromRoot = (relativePath) => path.join(appRoot, relativePath);

function readAbsolute(file) {
  return fs.readFileSync(file, "utf8");
}

function read(relativePath) {
  return readAbsolute(fromRoot(relativePath));
}

function walk(dir, predicate = () => true) {
  if (!fs.existsSync(dir)) return [];
  const files = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const absolute = path.join(dir, entry.name);
    if (entry.isDirectory()) files.push(...walk(absolute, predicate));
    else if (predicate(absolute)) files.push(absolute);
  }
  return files;
}

function routeFromPage(absolutePath) {
  const withoutApp = rel(absolutePath).replace(/^app\//, "");
  if (withoutApp === "page.tsx") return "/";
  return `/${withoutApp.replace(/\/page\.tsx$/, "")}`;
}

function countTag(text, name) {
  return [...text.matchAll(new RegExp(`<${name}\\b`, "g"))].length;
}

function tagNames(text, pattern) {
  return [...new Set([...text.matchAll(pattern)].map((match) => match[1]))].sort();
}

function makeCheck(id, passed, details) {
  return { id, passed: Boolean(passed), details };
}

function stripCssComments(text) {
  return text.replace(/\/\*[\s\S]*?\*\//g, "");
}

function hasBodyHtmlSelector(text) {
  return /(^|[}\s])(?:body|html)(?=[\s.#[:{,>+~])/m.test(stripCssComments(text));
}

function hasInlineGlobalStyleInjection(text) {
  return /<style\b[^>]*dangerouslySetInnerHTML\s*=\{\{\s*__html:/m.test(text);
}

function candidateFiles(basePath) {
  return [
    basePath,
    `${basePath}.tsx`,
    `${basePath}.ts`,
    `${basePath}.jsx`,
    `${basePath}.js`,
    path.join(basePath, "index.tsx"),
    path.join(basePath, "index.ts")
  ];
}

function resolveImportSource(importSource, importerFile) {
  let basePath = null;
  if (importSource.startsWith("@components/")) {
    basePath = fromRoot(path.join("components", importSource.replace("@components/", "")));
  } else if (importSource.startsWith("@/")) {
    basePath = fromRoot(importSource.replace("@/", ""));
  } else if (importSource.startsWith(".")) {
    basePath = path.resolve(path.dirname(importerFile), importSource);
  }

  if (!basePath) return null;
  return candidateFiles(basePath).find((file) => fs.existsSync(file) && fs.statSync(file).isFile()) ?? null;
}

function importedLocalNames(importClause) {
  const names = [];
  const clause = importClause.trim();
  const defaultMatch = clause.match(/^([A-Za-z_$][\w$]*)\s*(?:,|$)/);
  if (defaultMatch && defaultMatch[1] !== "type") names.push(defaultMatch[1]);

  const namedMatch = clause.match(/\{([\s\S]+)\}/);
  if (namedMatch) {
    for (const rawPart of namedMatch[1].split(",")) {
      const part = rawPart.trim().replace(/^type\s+/, "");
      if (!part) continue;
      const alias = part.match(/\bas\s+([A-Za-z_$][\w$]*)$/);
      names.push(alias ? alias[1] : part.split(/\s+/)[0]);
    }
  }

  return [...new Set(names)].filter((name) => /^[A-Z]/.test(name));
}

function directComponentImports(pageText, pageFile) {
  const imports = [];
  const importRegex = /import\s+([\s\S]*?)\s+from\s+["']([^"']+)["'];?/g;
  for (const match of pageText.matchAll(importRegex)) {
    const source = match[2];
    const resolved = resolveImportSource(source, pageFile);
    if (!resolved) continue;
    for (const localName of importedLocalNames(match[1])) {
      if (pageText.includes(`<${localName}`)) {
        imports.push({ localName, source, file: resolved });
      }
    }
  }
  return imports;
}

function expandReExports(file) {
  const files = new Set([file]);
  const text = readAbsolute(file);
  const exportRegex = /export\s+(?:\{[\s\S]*?\}|\*)\s+from\s+["']([^"']+)["'];?/g;
  for (const match of text.matchAll(exportRegex)) {
    const resolved = resolveImportSource(match[1], file);
    if (resolved) files.add(resolved);
  }
  return [...files];
}

function routeImports(pageText, pageFile) {
  const imports = [];
  for (const item of directComponentImports(pageText, pageFile)) {
    for (const resolvedFile of expandReExports(item.file)) {
      imports.push({ ...item, file: resolvedFile });
    }
  }
  return imports;
}

function routeIssues(record) {
  const issues = [];
  if (record.routeType === "technical-redirect") return issues;
  if (record.shellsPresent.length !== 1) issues.push("expected exactly one visible Tablet shell");
  if (record.legacyShellsPresent.length > 0) issues.push("legacy shell is mounted inside the visible route");
  if (record.pageV2Wrappers.length > 0 && record.childShellSources.length > 0) issues.push("page V2 wrapper surrounds an owner shell");
  if (record.pageV2Wrappers.length > 0 && record.legacyShellsPresent.length > 0) issues.push("V2 wrapper surrounds a legacy shell");
  if (record.inlineGlobalStylePresent) issues.push("route owner injects inline global CSS");
  if (record.contentSurfaceCount !== 1) issues.push("expected exactly one visible content surface");
  if (record.visibleDockCount > 1) issues.push("more than one dock source can be visible");
  if (record.route === "/pos" && record.ownerReal !== "PosScreen") issues.push("/pos must be owned by PosScreen");
  if ((record.route === "/pos" || record.route === "/checkout") && !record.posSurfaceMain) issues.push("POS route must render PosTerminalSurface as the main surface");
  if ((record.route === "/pos" || record.route === "/checkout") && record.posBottomDockEnabled) issues.push("POS shell bottom dock must be disabled when PosCommandDock is present");
  if (record.legacyTerminalStateDetected) issues.push("documentedLegacySurface cannot be accepted as a terminal state");
  return issues;
}

function classifyRoute(file) {
  const route = routeFromPage(file);
  const pageFile = rel(file);
  const pageText = readAbsolute(file);
  const isRedirectOnly = /\bredirect\(/.test(pageText) && !/<[A-Z][A-Za-z0-9_]*\b/.test(pageText);
  const imports = routeImports(pageText, file);
  const ownerFiles = [...new Map(imports.map((item) => [rel(item.file), item])).values()];
  const ownerTexts = ownerFiles.map((item) => ({ ...item, text: readAbsolute(item.file) }));
  const pageShell = countTag(pageText, "PrismaTabletShellUnified") > 0;
  const ownerShells = ownerTexts.filter((item) => countTag(item.text, "PrismaTabletShellUnified") > 0);
  const pageV2Wrappers = tagNames(pageText, /<(Tablet[A-Za-z]+SurfaceV2|PrismaRouteSurface)\b/g);
  const ownerV2Wrappers = tagNames(ownerTexts.map((item) => item.text).join("\n"), /<(Tablet[A-Za-z]+SurfaceV2|PrismaRouteSurface)\b/g);
  const pageLegacyShells = tagNames(pageText, /<(PrismaDarkPosShell|PrismaRouteUI|TouchPosUI|PrismaTabletShell)\b/g);
  const ownerLegacyShells = tagNames(ownerTexts.map((item) => item.text).join("\n"), /<(PrismaDarkPosShell|PrismaRouteUI|TouchPosUI|PrismaTabletShell)\b/g);
  const usesPosScreen = pageText.includes("<PosScreen");
  const posOwner = ownerTexts.find((item) => item.localName === "PosScreen" || rel(item.file).endsWith("components/pos/pos-screen.tsx"));
  const posSurfaceCount = posOwner ? countTag(posOwner.text, "PosTerminalSurface") : 0;
  const posCommandDock = posOwner ? countTag(posOwner.text, "PosCommandDock") > 0 : false;
  const posBottomDockEnabled = Boolean(posOwner && /visualSurface="tablet-pos"/.test(posOwner.text) && !/showBottomDock=\{false\}/.test(posOwner.text));
  const childShellSources = ownerShells.map((item) => `${item.localName}@${rel(item.file)}`);
  const shellsPresent = [
    ...(pageShell ? [`PrismaTabletShellUnified@${pageFile}`] : []),
    ...childShellSources.map((source) => `PrismaTabletShellUnified@${source}`)
  ];
  const legacyShellsPresent = [
    ...pageLegacyShells.map((name) => `${name}@${pageFile}`),
    ...ownerLegacyShells.map((name) => `${name}@owner`)
  ];
  const wrapperSources = [
    ...pageV2Wrappers.map((name) => `${name}@${pageFile}`),
    ...ownerV2Wrappers.map((name) => `${name}@owner`)
  ];
  const ownerReal = isRedirectOnly
    ? "redirect"
    : usesPosScreen
      ? "PosScreen"
      : ownerShells[0]?.localName ?? (pageShell ? "page.tsx" : ownerFiles[0]?.localName ?? "unknown");
  const routeType = isRedirectOnly ? "technical-redirect" : "visible";
  const pageSurfaceCount = pageV2Wrappers.length > 0 ? 1 : 0;
  const ownerSurfaceCount = ownerShells.length > 0 && pageV2Wrappers.length === 0 ? 1 : 0;
  const posSurfaceMain = usesPosScreen && posSurfaceCount > 0 && pageV2Wrappers.length === 0 && ownerV2Wrappers.length === 0;
  const contentSurfaceCount = isRedirectOnly ? 0 : (posSurfaceMain ? 1 : pageSurfaceCount || ownerSurfaceCount ? 1 : 0);
  const visibleDockCount = (pageV2Wrappers.length > 0 ? 1 : 0) + (posCommandDock ? 1 : 0) + (posBottomDockEnabled ? 1 : 0);
  const documentedLegacySurfaceTerminated = /\bdocumentedLegacySurface\b/.test(pageText) || ownerTexts.some((item) => /\bdocumentedLegacySurface\b/.test(item.text));
  const inlineGlobalStylePresent = hasInlineGlobalStyleInjection(pageText) || ownerTexts.some((item) => hasInlineGlobalStyleInjection(item.text));
  const legacyCssDominant = legacyShellsPresent.length > 0 || (pageV2Wrappers.length > 0 && childShellSources.length > 0);

  const record = {
    route,
    file: pageFile,
    routeType,
    ownerReal,
    shellsPresent,
    wrappersV2Present: wrapperSources,
    legacyCssDominant,
    legacyShellsPresent,
    childShellSources,
    pageV2Wrappers,
    ownerV2Wrappers,
    contentSurfaceCount,
    visibleDockCount,
    posSurfaceMain,
    posBottomDockEnabled,
    inlineGlobalStylePresent,
    legacyTerminalStateDetected: documentedLegacySurfaceTerminated,
    actionRequired: "pending"
  };

  const issues = routeIssues(record);
  record.status = issues.length === 0 ? "saneada" : "requires-cleanup";
  record.actionRequired = issues.length > 0
    ? issues.join("; ")
    : routeType === "technical-redirect"
      ? "technical redirect kept; no visible Tablet shell"
      : posSurfaceMain
        ? "saneada: PosTerminalSurface owns the visible POS surface; shell bottom dock disabled"
        : pageV2Wrappers.length > 0
          ? "saneada: one Tablet shell with one V2 content surface"
          : "saneada: wrapper removed; owner shell governs one content surface";
  return record;
}

const pageFiles = walk(fromRoot("app"), (file) => file.endsWith("page.tsx") && !file.replace(/\\/g, "/").includes("/api/"));
const routeCoverage = pageFiles.map(classifyRoute).sort((a, b) => a.route.localeCompare(b.route));
const visibleRoutes = routeCoverage.filter((route) => route.routeType === "visible");
const failingRoutes = visibleRoutes.filter((route) => route.status !== "saneada");
const shellInsideShellRoutes = visibleRoutes.filter((route) => route.shellsPresent.length !== 1 || route.legacyShellsPresent.length > 0);
const wrapperAroundShellRoutes = visibleRoutes.filter((route) => route.pageV2Wrappers.length > 0 && route.childShellSources.length > 0);
const wrapperAroundLegacyRoutes = visibleRoutes.filter((route) => route.pageV2Wrappers.length > 0 && route.legacyShellsPresent.length > 0);
const rootOnlyRoutes = visibleRoutes.filter((route) => route.shellsPresent.length === 1 && route.contentSurfaceCount !== 1);
const inlineGlobalStyleRoutes = visibleRoutes.filter((route) => route.inlineGlobalStylePresent);
const posRoutes = routeCoverage.filter((route) => route.route === "/pos" || route.route === "/checkout");
const posFailures = posRoutes.filter((route) => route.routeType === "visible" && (!route.posSurfaceMain || route.posBottomDockEnabled));
const multiDockRoutes = visibleRoutes.filter((route) => route.visibleDockCount > 1);
const documentedLegacyRoutes = routeCoverage.filter((route) => route.legacyTerminalStateDetected);

const cssFiles = [
  ...walk(fromRoot("components/tablet-visual-v2"), (file) => file.endsWith(".module.css")),
  ...walk(fromRoot("components/tablet-shell"), (file) => file.endsWith(".module.css")),
  ...walk(fromRoot("components/pos"), (file) => file.endsWith(".module.css"))
].filter((file) => fs.existsSync(file));
const cssEntries = cssFiles.map((file) => ({ file: rel(file), text: readAbsolute(file) }));
const importantHits = cssEntries.filter((entry) => entry.text.includes("!important")).map((entry) => entry.file);
const globalModuleHits = cssEntries.filter((entry) => /:global\(/.test(entry.text)).map((entry) => entry.file);
const bodyHtmlModuleHits = cssEntries.filter((entry) => hasBodyHtmlSelector(entry.text)).map((entry) => entry.file);

const packageText = read("package.json");
const checks = [
  makeCheck("routes.inventory", routeCoverage.length > 0, { routeCount: routeCoverage.length, visibleRouteCount: visibleRoutes.length }),
  makeCheck("routes.no-shell-inside-shell", shellInsideShellRoutes.length === 0, { routes: shellInsideShellRoutes.map((route) => route.route) }),
  makeCheck("routes.no-v2-wrapper-around-shell", wrapperAroundShellRoutes.length === 0, { routes: wrapperAroundShellRoutes.map((route) => route.route) }),
  makeCheck("routes.no-v2-wrapper-around-legacy-shell", wrapperAroundLegacyRoutes.length === 0, { routes: wrapperAroundLegacyRoutes.map((route) => route.route) }),
  makeCheck("routes.no-root-only", rootOnlyRoutes.length === 0, { routes: rootOnlyRoutes.map((route) => route.route) }),
  makeCheck("routes.no-inline-global-css-owner", inlineGlobalStyleRoutes.length === 0, { routes: inlineGlobalStyleRoutes.map((route) => route.route) }),
  makeCheck("routes.no-documented-legacy-terminal-state", documentedLegacyRoutes.length === 0, { routes: documentedLegacyRoutes.map((route) => route.route) }),
  makeCheck("routes.one-content-surface", failingRoutes.length === 0, { routes: failingRoutes.map((route) => ({ route: route.route, actionRequired: route.actionRequired })) }),
  makeCheck("pos.main-surface", posFailures.length === 0, { routes: posFailures.map((route) => ({ route: route.route, posSurfaceMain: route.posSurfaceMain, posBottomDockEnabled: route.posBottomDockEnabled })) }),
  makeCheck("dock.single-visible-source", multiDockRoutes.length === 0, { routes: multiDockRoutes.map((route) => ({ route: route.route, visibleDockCount: route.visibleDockCount })) }),
  makeCheck("css.no-important", importantHits.length === 0, { files: importantHits }),
  makeCheck("css.no-global-selectors-in-modules", globalModuleHits.length === 0 && bodyHtmlModuleHits.length === 0, { globalModuleHits, bodyHtmlModuleHits }),
  makeCheck("scripts.no-prisma-generate-hot-path", /"verify:tablet-visual-layer-cleanup"\s*:\s*"node tools\/verify_tablet_visual_layer_cleanup_2406\.mjs"/.test(packageText), { script: "verify:tablet-visual-layer-cleanup" })
];

const passed = checks.every((check) => check.passed);
const report = {
  status: passed ? "PASS" : "FAIL",
  task: "Tablet Visual Layer Cleanup",
  generatedAt: new Date().toISOString(),
  validationMode: "static-code-only",
  noBrowserAutomation: true,
  noDevServer: true,
  noProcessKill: true,
  noPrismaGenerateHotPath: true,
  scope: "Tablet app visual composition only",
  checks,
  summary: {
    routeCount: routeCoverage.length,
    visibleRouteCount: visibleRoutes.length,
    technicalRedirectCount: routeCoverage.length - visibleRoutes.length,
    saneadaCount: visibleRoutes.filter((route) => route.status === "saneada").length,
    failingRouteCount: failingRoutes.length
  },
  routeCoverage,
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
    "# Tablet Visual Layer Cleanup Evidence",
    "",
    `Status: ${report.status}`,
    "",
    "Validation mode: static-code-only. No browser automation, no dev server, no process kill, no Prisma generate hot path.",
    "",
    "## Checks",
    "",
    ...checks.map((check) => `- ${check.passed ? "PASS" : "FAIL"} ${check.id}`),
    "",
    "## Route Inventory",
    "",
    "| Route | Owner real | Shells present | V2 wrappers | Legacy CSS dominant | Action required |",
    "| --- | --- | --- | --- | --- | --- |",
    ...routeCoverage.map((route) => `| ${route.route} | ${route.ownerReal} | ${route.shellsPresent.join("<br>") || "n/a"} | ${route.wrappersV2Present.join("<br>") || "n/a"} | ${route.legacyCssDominant ? "yes" : "no"} | ${route.actionRequired} |`),
    ""
  ].join("\n")
);

console.log(JSON.stringify({
  status: report.status,
  checks: checks.length,
  routeCount: report.summary.routeCount,
  visibleRouteCount: report.summary.visibleRouteCount,
  failingRouteCount: report.summary.failingRouteCount,
  evidence: report.evidenceFiles
}, null, 2));

if (!passed) {
  for (const check of checks.filter((item) => !item.passed)) {
    console.error(`[${check.id}] ${JSON.stringify(check.details)}`);
  }
  process.exitCode = 1;
}
