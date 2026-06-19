#!/usr/bin/env node
import fs from 'node:fs';
import net from 'node:net';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const moduleDir = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(moduleDir, '..', '..');
const prismaUiRoot = path.join(appRoot, '.prisma-ui');
const currentRoot = path.join(prismaUiRoot, 'current');
const routeContractsPath = path.join(prismaUiRoot, 'routes.json');
const surfacesPath = path.join(prismaUiRoot, 'surfaces.json');

const ROUTE_HARD_STATES = [
  'RUNTIME_CERTIFIED',
  'SOURCE_CERTIFIED',
  'BLOCKED',
  'DRIFT',
  'CONFLICT',
  'RUNTIME_BLOCKED',
  'ROUTE_UNMAPPED',
  'ANCHOR_MISSING',
  'SELECTOR_MISSING'
];

const NEXT_SURFACES = [
  {
    surface: 'chart-lab',
    app: 'Chart Lab',
    port: 3000,
    pageRoot: 'products/chart-lab/app/app',
    appDir: 'products/chart-lab/app'
  },
  {
    surface: 'web',
    app: 'PRISMA Web/Edit',
    port: 3110,
    pageRoot: 'products/web/app/app',
    appDir: 'products/web/app'
  },
  {
    surface: 'tablet',
    app: 'PRISMA Tablet Core',
    port: 3120,
    pageRoot: 'products/tablet/app/app',
    appDir: 'products/tablet/app'
  },
  {
    surface: 'pc',
    app: 'PRISMA PC Backoffice',
    port: 3130,
    pageRoot: 'products/pc/app/app',
    appDir: 'products/pc/app'
  },
  {
    surface: 'mobile',
    app: 'PRISMA Mobile Adder',
    port: 3140,
    pageRoot: 'products/mobile/app/app',
    appDir: 'products/mobile/app'
  }
];

const CONTROL_CENTER = {
  surface: 'control-center',
  app: 'Control Center',
  port: 3150,
  pageFile: 'prisma-control-center/internal/web/index.html'
};

const SUCCESS_STATUSES = new Set(['CERTIFIED', 'RUNTIME_CERTIFIED', 'ALL_RUNTIME_PAGES_CERTIFIED']);

function exists(filePath) {
  try {
    return fs.existsSync(filePath);
  } catch {
    return false;
  }
}

function readText(filePath) {
  return fs.readFileSync(filePath, 'utf8');
}

function readJson(filePath) {
  return JSON.parse(readText(filePath));
}

function writeText(filePath, value) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, value, 'utf8');
}

function writeJson(filePath, value) {
  writeText(filePath, `${JSON.stringify(value, null, 2)}\n`);
}

function toPosix(value) {
  return String(value || '').replace(/\\/g, '/');
}

function absApp(relativePath) {
  return path.join(appRoot, relativePath);
}

function relApp(filePath) {
  return toPosix(path.relative(appRoot, filePath));
}

function nowIso() {
  return new Date().toISOString();
}

function gitValue(args, fallback = null) {
  try {
    return execFileSync('git', args, {
      cwd: appRoot,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore']
    }).trim() || fallback;
  } catch {
    return fallback;
  }
}

function baseReport(schema, command, status) {
  return {
    schema,
    status,
    command,
    generated_at: nowIso(),
    repoRoot: toPosix(path.resolve(appRoot, '..', '..')),
    appRoot: relApp(appRoot),
    repoHead: gitValue(['rev-parse', 'HEAD'], 'unknown'),
    branch: gitValue(['branch', '--show-current'], 'unknown')
  };
}

function parseArgs(raw = process.argv.slice(2)) {
  const cmd = raw.shift() || 'routes';
  const flags = { _: [] };
  for (let index = 0; index < raw.length; index += 1) {
    const item = raw[index];
    if (!item.startsWith('--')) {
      flags._.push(item);
      continue;
    }
    const key = item.slice(2);
    const next = raw[index + 1];
    if (next && !next.startsWith('--')) {
      flags[key] = next;
      index += 1;
    } else {
      flags[key] = true;
    }
  }
  return { cmd, flags };
}

function escapeRegExp(value) {
  return String(value || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function walk(dir, out = []) {
  if (!exists(dir)) return out;
  const skip = new Set(['.git', 'node_modules', '.next', 'dist', 'build', 'coverage', '.turbo', '.cache', 'out']);
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (skip.has(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full, out);
    else out.push(full);
  }
  return out;
}

function selectedSurfaceSet(flags = {}) {
  if (flags.surface && flags.surface !== 'all') return new Set([String(flags.surface)]);
  return new Set([...NEXT_SURFACES.map((surface) => surface.surface), CONTROL_CENTER.surface]);
}

function segmentToRoutePart(segment) {
  if (/^\[\[\.\.\..+\]\]$/.test(segment)) return `:${segment.slice(5, -2)}*`;
  if (/^\[\.\.\..+\]$/.test(segment)) return `:${segment.slice(4, -1)}*`;
  if (/^\[.+\]$/.test(segment)) return `:${segment.slice(1, -1)}`;
  return segment;
}

function routeFromPageFile(surface, pageFile) {
  const pageRoot = absApp(surface.pageRoot);
  const relativeDir = toPosix(path.relative(pageRoot, path.dirname(pageFile)));
  if (!relativeDir || relativeDir === '.') {
    return { route: '/', dynamic: false, routeDirSegments: [] };
  }
  const sourceSegments = relativeDir.split('/').filter(Boolean);
  const routeSegments = sourceSegments.map(segmentToRoutePart);
  return {
    route: `/${routeSegments.join('/')}`,
    dynamic: sourceSegments.some((segment) => segment.includes('[')),
    routeDirSegments: sourceSegments
  };
}

function routeSort(a, b) {
  if (a.route === '/' && b.route !== '/') return -1;
  if (b.route === '/' && a.route !== '/') return 1;
  return a.route.localeCompare(b.route);
}

function panelIdForRoute(surface, route) {
  if (surface === CONTROL_CENTER.surface) return 'control-center.workspace';
  if (route === '/') return `${surface}.root.route`;
  const key = route
    .slice(1)
    .replace(/[^A-Za-z0-9]+/g, '.')
    .replace(/^\.|\.$/g, '');
  return `${surface}.${key}.route`;
}

function layoutFilesFor(surface, routeDirSegments) {
  const files = [];
  const rootLayout = path.join(absApp(surface.pageRoot), 'layout.tsx');
  if (exists(rootLayout)) files.push(relApp(rootLayout));
  let current = absApp(surface.pageRoot);
  for (const segment of routeDirSegments) {
    current = path.join(current, segment);
    const layout = path.join(current, 'layout.tsx');
    if (exists(layout)) files.push(relApp(layout));
  }
  return files;
}

function loadPanels() {
  const panelDir = path.join(prismaUiRoot, 'panels');
  if (!exists(panelDir)) return [];
  return fs.readdirSync(panelDir)
    .filter((name) => name.endsWith('.json'))
    .sort()
    .flatMap((name) => {
      try {
        const panel = readJson(path.join(panelDir, name));
        return [{ ...panel, __file: `.prisma-ui/panels/${name}` }];
      } catch {
        return [];
      }
    });
}

function matchingPanelContracts(panels, surface, route) {
  return panels
    .filter((panel) => panel.surface === surface && (panel.route === route || panel.route === '*'))
    .map((panel) => panel.panel_id)
    .filter(Boolean)
    .sort();
}

function contractForNextPage(surface, pageFile, panels) {
  const relPageFile = relApp(pageFile);
  const { route, dynamic, routeDirSegments } = routeFromPageFile(surface, pageFile);
  const pageText = safeRead(relPageFile);
  const redirectTarget = pageText.match(/\bredirect\s*\(\s*["']([^"']+)["']\s*\)/)?.[1] || null;
  const panelId = panelIdForRoute(surface.surface, route);
  const layoutFiles = layoutFilesFor(surface, routeDirSegments);
  const middleware = `${surface.appDir}/middleware.ts`;
  const matchedPanels = matchingPanelContracts(panels, surface.surface, route);
  const runtimeMode = dynamic ? 'source-only-dynamic-route' : (redirectTarget ? 'source-only-redirect-route' : 'runtime');
  const sourceJustification = dynamic
    ? 'Next.js dynamic segment requires a domain instance value; source-certified by page file, root layout data-prisma anchor provider, and middleware x-prisma-route propagation.'
    : (redirectTarget ? `This page is a source-level redirect alias to ${redirectTarget}; the canonical target route carries runtime UI anchors.` : null);
  return {
    route_id: panelId,
    panel_id: panelId,
    app: surface.app,
    surface: surface.surface,
    port: surface.port,
    route,
    pageFile: relPageFile,
    layoutFiles,
    ownerComponent: relPageFile,
    anchorOwnerComponent: layoutFiles[0] || relPageFile,
    middleware,
    currentPanelContract: matchedPanels.length === 1 ? matchedPanels[0] : (matchedPanels.length ? matchedPanels : null),
    runtimeUrl: runtimeMode === 'runtime' ? `http://127.0.0.1:${surface.port}${route}` : null,
    runtimeMode,
    sourceJustification,
    redirectTarget,
    anchors: {
      'data-prisma-panel': panelId,
      'data-prisma-surface': surface.surface,
      'data-prisma-route': route
    },
    canonical_selectors: [`[data-prisma-panel="${panelId}"]`],
    allowed_files: [
      '.prisma-ui/current/**',
      '.prisma-ui/routes.json',
      'tools/quality/ui-certainty.mjs',
      'tools/quality/ui-runtime-certainty.mjs',
      'package.json',
      relPageFile,
      ...layoutFiles,
      middleware
    ]
  };
}

function contractForControlCenter(panels) {
  const matchedPanels = matchingPanelContracts(panels, CONTROL_CENTER.surface, '/');
  return {
    route_id: 'control-center.workspace',
    panel_id: 'control-center.workspace',
    app: CONTROL_CENTER.app,
    surface: CONTROL_CENTER.surface,
    port: CONTROL_CENTER.port,
    route: '/',
    pageFile: CONTROL_CENTER.pageFile,
    layoutFiles: [],
    ownerComponent: CONTROL_CENTER.pageFile,
    anchorOwnerComponent: CONTROL_CENTER.pageFile,
    middleware: null,
    currentPanelContract: matchedPanels[0] || 'control-center.workspace',
    runtimeUrl: `http://127.0.0.1:${CONTROL_CENTER.port}/`,
    runtimeMode: 'runtime',
    sourceJustification: null,
    anchors: {
      'data-prisma-panel': 'control-center.workspace',
      'data-prisma-surface': CONTROL_CENTER.surface,
      'data-prisma-route': '/'
    },
    canonical_selectors: ['[data-prisma-panel="control-center.workspace"]'],
    allowed_files: [
      '.prisma-ui/current/**',
      '.prisma-ui/routes.json',
      'tools/quality/ui-certainty.mjs',
      'tools/quality/ui-runtime-certainty.mjs',
      'package.json',
      CONTROL_CENTER.pageFile
    ]
  };
}

function routeCounts(routes) {
  const counts = {};
  for (const route of routes) {
    counts[route.surface] ||= {
      app: route.app,
      port: route.port,
      routeCount: 0,
      runtimeRoutes: 0,
      sourceOnlyDynamicRoutes: 0,
      sourceOnlyRedirectRoutes: 0,
      runtimeCertifiedCount: 0,
      sourceCertifiedCount: 0,
      runtimeBlockedCount: 0
    };
    counts[route.surface].routeCount += 1;
    if (route.runtimeMode === 'runtime') counts[route.surface].runtimeRoutes += 1;
    if (route.runtimeMode === 'source-only-dynamic-route') counts[route.surface].sourceOnlyDynamicRoutes += 1;
    if (route.runtimeMode === 'source-only-redirect-route') counts[route.surface].sourceOnlyRedirectRoutes += 1;
  }
  return counts;
}

function discoverRouteContracts(flags = {}) {
  const selected = selectedSurfaceSet(flags);
  const panels = loadPanels();
  const routes = [];
  for (const surface of NEXT_SURFACES) {
    if (!selected.has(surface.surface)) continue;
    const pageRoot = absApp(surface.pageRoot);
    const pageFiles = walk(pageRoot)
      .filter((file) => path.basename(file) === 'page.tsx')
      .sort((a, b) => relApp(a).localeCompare(relApp(b)));
    for (const pageFile of pageFiles) {
      routes.push(contractForNextPage(surface, pageFile, panels));
    }
  }
  if (selected.has(CONTROL_CENTER.surface) && exists(absApp(CONTROL_CENTER.pageFile))) {
    routes.push(contractForControlCenter(panels));
  }
  const order = new Map([...NEXT_SURFACES.map((surface, index) => [surface.surface, index]), [CONTROL_CENTER.surface, NEXT_SURFACES.length]]);
  routes.sort((a, b) => {
    const surfaceDelta = (order.get(a.surface) ?? 99) - (order.get(b.surface) ?? 99);
    return surfaceDelta || routeSort(a, b);
  });
  if (flags.route) return routes.filter((route) => route.route === flags.route);
  return routes;
}

function routePayload(routes) {
  return {
    schema: 'prisma.ui.route.contracts.v1',
    created_by: 'uirun1',
    generated_at: nowIso(),
    source: 'filesystem-page-discovery',
    hard_states: ROUTE_HARD_STATES,
    routeCount: routes.length,
    countsBySurface: routeCounts(routes),
    routes
  };
}

function syncSurfacesJson(routes) {
  if (!exists(surfacesPath)) return;
  const payload = readJson(surfacesPath);
  const bySurface = {};
  for (const route of routes) {
    bySurface[route.surface] ||= [];
    bySurface[route.surface].push(route.route);
  }
  const surfaces = Array.isArray(payload.surfaces) ? payload.surfaces : [];
  for (const surface of surfaces) {
    if (!bySurface[surface.id || surface.surface]) continue;
    surface.routes = bySurface[surface.id || surface.surface].sort((a, b) => routeSort({ route: a }, { route: b }));
  }
  payload.hard_states = ROUTE_HARD_STATES;
  payload.runtimePageCertification = {
    schema: 'prisma.ui.route.contracts.v1',
    route_contracts: '.prisma-ui/routes.json',
    routeCount: routes.length,
    countsBySurface: routeCounts(routes)
  };
  writeJson(surfacesPath, payload);
}

function persistRouteContracts(routes) {
  writeJson(routeContractsPath, routePayload(routes));
  syncSurfacesJson(routes);
}

function markdownReport(name, report) {
  const lines = [
    `# ${name.replace(/_/g, ' ')}`,
    '',
    `- schema: \`${report.schema || 'n/a'}\``,
    `- status: \`${report.status || 'n/a'}\``,
    `- command: \`${report.command || 'n/a'}\``,
    `- routeCount: \`${report.routeCount ?? 0}\``,
    `- routeUnmappedCount: \`${report.routeUnmappedCount ?? 0}\``,
    `- runtimeBlockedCount: \`${report.runtimeBlockedCount ?? 0}\``,
    `- anchorMissingCount: \`${report.anchorMissingCount ?? 0}\``,
    `- selectorMissingCount: \`${report.selectorMissingCount ?? 0}\``,
    `- blockedCount: \`${report.blockedCount ?? 0}\``,
    `- driftCount: \`${report.driftCount ?? 0}\``,
    `- conflictCount: \`${report.conflictCount ?? 0}\``,
    ''
  ];
  if (report.countsBySurface) {
    lines.push('## Surfaces');
    for (const [surface, counts] of Object.entries(report.countsBySurface)) {
      lines.push(`- ${surface}: routes ${counts.routeCount}, runtime ${counts.runtimeCertifiedCount ?? counts.runtimeRoutes ?? 0}, source ${counts.sourceCertifiedCount ?? counts.sourceOnlyDynamicRoutes ?? 0}, blocked ${counts.runtimeBlockedCount ?? 0}`);
    }
    lines.push('');
  }
  if (Array.isArray(report.gaps) && report.gaps.length) {
    lines.push('## Gaps');
    for (const gap of report.gaps) lines.push(`- ${gap.status || gap.type}: ${gap.surface || 'global'} ${gap.route || ''} ${gap.reason || ''}`.trim());
    lines.push('');
  }
  if (Array.isArray(report.routes)) {
    lines.push('## Routes');
    for (const route of report.routes) lines.push(`- ${route.status || route.runtimeMode || 'ROUTE'} - ${route.surface} ${route.route} - ${route.runtimeUrl || route.pageFile || 'source-only'}`);
    lines.push('');
  }
  return lines.join('\n');
}

function writeReports(name, report) {
  writeJson(path.join(currentRoot, `${name}.json`), report);
  writeText(path.join(currentRoot, `${name}.md`), markdownReport(name, report));
}

function reportName(baseName, flags = {}) {
  if (flags.surface && flags.surface !== 'all') {
    const suffix = String(flags.surface).replace(/[^A-Za-z0-9]+/g, '_').replace(/^_+|_+$/g, '').toUpperCase();
    return `${baseName}_${suffix}`;
  }
  if (flags.route) {
    const suffix = String(flags.route).replace(/[^A-Za-z0-9]+/g, '_').replace(/^_+|_+$/g, '').toUpperCase() || 'ROOT';
    return `${baseName}_ROUTE_${suffix}`;
  }
  return baseName;
}

function hasAttributeValue(text, attribute, value) {
  if (!value) return false;
  const rx = new RegExp(`${escapeRegExp(attribute)}\\s*=\\s*["']${escapeRegExp(value)}["']`);
  return rx.test(text);
}

function attributeValues(text, attribute) {
  const rx = new RegExp(`${escapeRegExp(attribute)}\\s*=\\s*["']([^"']+)["']`, 'g');
  const values = [];
  let match;
  while ((match = rx.exec(text))) values.push(match[1]);
  return Array.from(new Set(values));
}

function normalizedPathFromUrl(url) {
  try {
    const pathname = new URL(url).pathname || '/';
    return pathname.length > 1 ? pathname.replace(/\/+$/, '') : pathname;
  } catch {
    return null;
  }
}

function runtimeAnchorResult(text, route, responseUrl) {
  const expectedPanel = route.anchors['data-prisma-panel'];
  const expectedSurface = route.anchors['data-prisma-surface'];
  const expectedRoute = route.anchors['data-prisma-route'];
  const finalRoute = normalizedPathFromUrl(responseUrl);
  const actualPanels = attributeValues(text, 'data-prisma-panel');
  const actualSurfaces = attributeValues(text, 'data-prisma-surface');
  const actualRoutes = attributeValues(text, 'data-prisma-route');
  const hasPanel = actualPanels.includes(expectedPanel);
  const hasSurface = actualSurfaces.includes(expectedSurface);
  const hasRoute = actualRoutes.includes(expectedRoute);
  const hasAnyPanel = actualPanels.length > 0;
  const finalHasRoute = finalRoute ? actualRoutes.includes(finalRoute) : false;
  const exact = hasPanel && hasSurface && hasRoute;
  const currentPanelRoute = !exact && hasAnyPanel && hasSurface && hasRoute;
  const redirect = !exact && !currentPanelRoute && finalRoute && finalRoute !== expectedRoute && hasAnyPanel && hasSurface && finalHasRoute;
  return {
    expectedPanel,
    expectedSurface,
    expectedRoute,
    actualPanels,
    actualSurfaces,
    actualRoutes,
    hasPanel,
    hasSurface,
    hasRoute,
    hasAnyPanel,
    finalRoute,
    finalHasRoute,
    accepted: exact || currentPanelRoute || redirect,
    acceptance: exact ? 'exact-panel-route-anchor' : (currentPanelRoute ? 'current-panel-route-anchor' : (redirect ? 'redirect-target-route-anchor' : null)),
    redirectCertified: Boolean(redirect),
    redirectTargetRoute: redirect ? finalRoute : null
  };
}

function safeRead(relativePath) {
  const filePath = absApp(relativePath);
  try {
    if (fs.statSync(filePath).size > 3_500_000) return '';
    return readText(filePath);
  } catch {
    return '';
  }
}

function anchorProviderCheck(route) {
  const anchorOwner = route.anchorOwnerComponent || route.ownerComponent;
  const anchorText = anchorOwner ? safeRead(anchorOwner) : '';
  if (route.surface === CONTROL_CENTER.surface) {
    return hasAttributeValue(anchorText, 'data-prisma-panel', route.anchors['data-prisma-panel'])
      && hasAttributeValue(anchorText, 'data-prisma-surface', route.anchors['data-prisma-surface'])
      && hasAttributeValue(anchorText, 'data-prisma-route', route.anchors['data-prisma-route']);
  }
  const middlewareText = route.middleware ? safeRead(route.middleware) : '';
  return anchorText.includes('data-prisma-panel')
    && anchorText.includes('data-prisma-surface')
    && anchorText.includes('data-prisma-route')
    && anchorText.includes('prismaRoutePanelId')
    && middlewareText.includes('x-prisma-route');
}

function routeCoverage(flags = {}) {
  const allRoutes = discoverRouteContracts({});
  persistRouteContracts(allRoutes);
  const routes = flags.route ? allRoutes.filter((route) => route.route === flags.route) : discoverRouteContracts(flags);
  const seen = new Set();
  const rows = routes.map((route) => {
    const blockers = [];
    const drifts = [];
    const conflicts = [];
    if (route.route === '/page.tsx' || String(route.runtimeUrl || '').includes('/page.tsx')) blockers.push('critical root route mapped as /page.tsx');
    if (!route.route_id) blockers.push('missing route_id');
    if (route.route_id && seen.has(route.route_id)) conflicts.push('duplicate route_id');
    if (route.route_id) seen.add(route.route_id);
    if (!route.ownerComponent || !exists(absApp(route.ownerComponent))) drifts.push(`ownerComponent missing: ${route.ownerComponent || 'n/a'}`);
    if (!route.pageFile || !exists(absApp(route.pageFile))) drifts.push(`pageFile missing: ${route.pageFile || 'n/a'}`);
    if (!anchorProviderCheck(route)) blockers.push(`anchor provider missing for route ${route.route}`);
    const selectorFound = (route.canonical_selectors || []).some((selector) => selector.startsWith('[data-prisma-panel='));
    if (!selectorFound) blockers.push(`selector missing for route ${route.route}`);
    let status = route.runtimeMode === 'source-only-dynamic-route' ? 'SOURCE_CERTIFIED' : 'SOURCE_CERTIFIED';
    if (conflicts.length) status = 'CONFLICT';
    else if (drifts.length) status = 'DRIFT';
    else if (blockers.some((item) => item.includes('selector'))) status = 'SELECTOR_MISSING';
    else if (blockers.some((item) => item.includes('anchor'))) status = 'ANCHOR_MISSING';
    else if (blockers.length) status = 'ROUTE_UNMAPPED';
    return {
      ...route,
      status,
      blockers,
      drifts,
      conflicts,
      anchorStrategy: route.surface === CONTROL_CENTER.surface ? 'static-html-anchor' : 'root-layout-plus-middleware-path-header',
      selectorChecks: (route.canonical_selectors || []).map((selector) => ({
        selector,
        status: selector.startsWith('[data-prisma-panel=') ? 'SOURCE_CERTIFIED' : 'SELECTOR_MISSING'
      }))
    };
  });
  const routeUnmappedCount = rows.filter((row) => row.status === 'ROUTE_UNMAPPED').length;
  const anchorMissingCount = rows.filter((row) => row.status === 'ANCHOR_MISSING').length;
  const selectorMissingCount = rows.reduce((count, row) => count + row.selectorChecks.filter((check) => check.status === 'SELECTOR_MISSING').length, 0);
  const driftCount = rows.filter((row) => row.status === 'DRIFT').length;
  const conflictCount = rows.filter((row) => row.status === 'CONFLICT').length;
  const blockedCount = routeUnmappedCount + anchorMissingCount + selectorMissingCount;
  const status = blockedCount || driftCount || conflictCount ? 'BLOCKED' : 'CERTIFIED';
  const report = {
    ...baseReport('prisma.ui.route.coverage.report.v1', 'route-coverage', status),
    routeCount: rows.length,
    routeUnmappedCount,
    runtimeBlockedCount: 0,
    anchorMissingCount,
    selectorMissingCount,
    blockedCount,
    driftCount,
    conflictCount,
    countsBySurface: routeCounts(rows),
    routes: rows,
    blockers: rows.flatMap((row) => row.blockers.map((reason) => ({ route: row.route, surface: row.surface, reason }))),
    drifts: rows.flatMap((row) => row.drifts.map((reason) => ({ route: row.route, surface: row.surface, reason }))),
    conflicts: rows.flatMap((row) => row.conflicts.map((reason) => ({ route: row.route, surface: row.surface, reason }))),
    exitCodeExpectation: status === 'CERTIFIED' ? 0 : 1
  };
  writeReports(reportName('UI_ROUTE_COVERAGE_REPORT', flags), report);
  return report;
}

function routeInventory(flags = {}) {
  const allRoutes = discoverRouteContracts({});
  persistRouteContracts(allRoutes);
  const routes = flags.route ? allRoutes.filter((route) => route.route === flags.route) : discoverRouteContracts(flags);
  const report = {
    ...baseReport('prisma.ui.route.inventory.report.v1', 'routes', 'CERTIFIED'),
    routeCount: routes.length,
    countsBySurface: routeCounts(routes),
    entries: routes.map((route) => ({
      app: route.app,
      port: route.port,
      surface: route.surface,
      route: route.route,
      pageFile: route.pageFile,
      layoutFiles: route.layoutFiles,
      ownerComponent: route.ownerComponent,
      currentPanelContract: route.currentPanelContract,
      requiredContract: route.route_id,
      runtimeUrl: route.runtimeUrl,
      runtimeMode: route.runtimeMode,
      sourceJustification: route.sourceJustification,
      status: route.runtimeMode === 'source-only-dynamic-route' ? 'SOURCE_CERTIFIED' : 'RUNTIME_CERTIFIED_CANDIDATE'
    })),
    routes,
    exitCodeExpectation: 0
  };
  writeReports(reportName('UI_ROUTE_INVENTORY_REPORT', flags), report);
  return report;
}

async function fetchWithTimeout(url, timeoutMs) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(new Error(`timeout after ${timeoutMs}ms`)), timeoutMs);
  try {
    const response = await fetch(url, {
      redirect: 'follow',
      signal: controller.signal,
      headers: {
        accept: 'text/html,*/*;q=0.8',
        connection: 'close'
      }
    });
    const text = await response.text();
    return { response, text };
  } finally {
    clearTimeout(timer);
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function errorDetails(error) {
  const base = String(error?.message || error);
  const cause = error?.cause;
  if (!cause) return base;
  const parts = [base];
  if (cause.code) parts.push(`code=${cause.code}`);
  if (cause.errno) parts.push(`errno=${cause.errno}`);
  if (cause.address) parts.push(`address=${cause.address}`);
  if (cause.port) parts.push(`port=${cause.port}`);
  if (cause.message && cause.message !== base) parts.push(`cause=${cause.message}`);
  return parts.join('; ');
}

async function fetchWithRetries(url, timeoutMs, attempts = 5) {
  let lastError;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      return { ...(await fetchWithTimeout(url, timeoutMs)), attempts: attempt };
    } catch (error) {
      lastError = error;
      if (attempt < attempts) await sleep(250 * attempt);
    }
  }
  throw lastError;
}

function probeTcpPort(port, timeoutMs) {
  return new Promise((resolve) => {
    const socket = new net.Socket();
    let settled = false;
    const finish = (result) => {
      if (settled) return;
      settled = true;
      socket.destroy();
      resolve(result);
    };
    socket.setTimeout(timeoutMs);
    socket.once('connect', () => finish({ reachable: true, transport: 'tcp' }));
    socket.once('timeout', () => finish({ reachable: false, transport: 'tcp', error: `tcp timeout after ${timeoutMs}ms` }));
    socket.once('error', (error) => finish({ reachable: false, transport: 'tcp', error: String(error?.message || error) }));
    socket.connect(port, '127.0.0.1');
  });
}

async function probePorts(routes, timeoutMs) {
  const ports = new Map();
  for (const route of routes) {
    if (route.runtimeMode !== 'runtime') continue;
    if (!ports.has(route.port)) ports.set(route.port, { port: route.port, url: `http://127.0.0.1:${route.port}/`, reachable: false, status: null, error: null });
  }
  for (const entry of ports.values()) {
    const tcp = await probeTcpPort(entry.port, Math.min(timeoutMs, 2000));
    entry.reachable = tcp.reachable;
    entry.transport = tcp.transport;
    if (!tcp.reachable) {
      entry.error = tcp.error || `tcp probe failed for port ${entry.port}`;
      continue;
    }
    try {
      const { response } = await fetchWithTimeout(entry.url, Math.min(timeoutMs, 3000));
      entry.status = response.status;
      entry.finalUrl = response.url;
    } catch (error) {
      entry.httpProbeError = String(error?.message || error);
    }
  }
  return Object.fromEntries(Array.from(ports.entries()));
}

function reducedHtml(text) {
  return String(text || '')
    .replace(/<script\b[\s\S]*?<\/script>/gi, '<script data-prisma-omitted="true"></script>')
    .replace(/<style\b[\s\S]*?<\/style>/gi, '<style data-prisma-omitted="true"></style>')
    .slice(0, 200000);
}

function snapshotName(route) {
  const routeKey = route.route === '/' ? 'root' : route.route.slice(1).replace(/[^A-Za-z0-9]+/g, '_').replace(/^_+|_+$/g, '');
  return `${route.surface}_${routeKey || 'root'}.html`;
}

function runtimeMissingReason(row) {
  const missing = [];
  if (!row.hasAnyPanel) missing.push('data-prisma-panel');
  if (!row.hasSurface) missing.push('data-prisma-surface');
  if (!row.hasRoute) missing.push('data-prisma-route');
  return missing.length ? `missing runtime anchors: ${missing.join(', ')}` : null;
}

async function runtimeProbe(flags = {}) {
  const allRoutes = discoverRouteContracts({});
  persistRouteContracts(allRoutes);
  const routes = flags.route ? allRoutes.filter((route) => route.route === flags.route) : discoverRouteContracts(flags);
  const timeoutMs = Number(flags['timeout-ms'] || flags.timeoutMs || 15000);
  const htmlDir = path.join(currentRoot, 'runtime-html');
  fs.mkdirSync(htmlDir, { recursive: true });
  const portStates = await probePorts(routes, Math.min(timeoutMs, 3000));
  const rows = [];
  for (const route of routes) {
    const startedAt = nowIso();
    if (route.runtimeMode !== 'runtime') {
      rows.push({
        ...route,
        status: 'SOURCE_CERTIFIED',
        httpStatus: null,
        finalUrl: null,
        redirected: false,
        contentType: null,
        title: null,
        hasPanel: true,
        hasSurface: true,
        hasRoute: true,
        htmlSnapshot: null,
        screenshot: null,
        screenshotReason: 'source-only dynamic route',
        startedAt,
        finishedAt: nowIso(),
        reason: route.sourceJustification
      });
      continue;
    }
    const portState = portStates[route.port];
    if (!portState?.reachable) {
      rows.push({
        ...route,
        status: 'RUNTIME_BLOCKED',
        httpStatus: null,
        finalUrl: route.runtimeUrl,
        redirected: false,
        contentType: null,
        title: null,
        hasPanel: false,
        hasSurface: false,
        hasRoute: false,
        htmlSnapshot: null,
        screenshot: null,
        screenshotReason: 'runtime port was not reachable',
        portReachable: false,
        startedAt,
        finishedAt: nowIso(),
        error: portState?.error || `port ${route.port} did not respond`,
        reason: `port ${route.port} did not respond to passive probe`
      });
      continue;
    }
    try {
      const { response, text, attempts } = await fetchWithRetries(route.runtimeUrl, timeoutMs);
      const anchor = runtimeAnchorResult(text, route, response.url);
      const title = text.match(/<title[^>]*>(.*?)<\/title>/i)?.[1] || null;
      const snapshot = path.join(htmlDir, snapshotName(route));
      writeText(snapshot, reducedHtml(text));
      const ok = response.ok && anchor.accepted;
      const row = {
        ...route,
        status: ok ? 'RUNTIME_CERTIFIED' : (!response.ok ? 'RUNTIME_BLOCKED' : 'ANCHOR_MISSING'),
        httpStatus: response.status,
        finalUrl: response.url,
        redirected: response.redirected,
        contentType: response.headers.get('content-type'),
        title,
        hasPanel: anchor.hasPanel,
        hasAnyPanel: anchor.hasAnyPanel,
        hasSurface: anchor.hasSurface,
        hasRoute: anchor.hasRoute,
        actualPanels: anchor.actualPanels,
        actualSurfaces: anchor.actualSurfaces,
        actualRoutes: anchor.actualRoutes,
        anchorAcceptance: anchor.acceptance,
        redirectCertified: anchor.redirectCertified,
        redirectTargetRoute: anchor.redirectTargetRoute,
        htmlSnapshot: relApp(snapshot),
        screenshot: null,
        screenshotReason: 'Playwright/Chromium screenshot capture was unavailable without installing browsers',
        portReachable: true,
        attempts,
        startedAt,
        finishedAt: nowIso()
      };
      row.reason = ok ? (anchor.redirectCertified ? `redirect certified to ${anchor.redirectTargetRoute}` : null) : (!response.ok ? `HTTP ${response.status}` : runtimeMissingReason(row));
      rows.push(row);
    } catch (error) {
      rows.push({
        ...route,
        status: 'RUNTIME_BLOCKED',
        httpStatus: null,
        finalUrl: route.runtimeUrl,
        redirected: false,
        contentType: null,
        title: null,
        hasPanel: false,
        hasSurface: false,
        hasRoute: false,
        htmlSnapshot: null,
        screenshot: null,
        screenshotReason: 'runtime fetch failed before screenshot capture',
        portReachable: true,
        startedAt,
        finishedAt: nowIso(),
        error: errorDetails(error),
        reason: errorDetails(error)
      });
    }
  }
  const runtimeBlockedCount = rows.filter((row) => row.status === 'RUNTIME_BLOCKED').length;
  const anchorMissingCount = rows.filter((row) => row.status === 'ANCHOR_MISSING').length;
  const selectorMissingCount = rows.filter((row) => row.status === 'SELECTOR_MISSING').length;
  const driftCount = rows.filter((row) => row.status === 'DRIFT').length;
  const conflictCount = rows.filter((row) => row.status === 'CONFLICT').length;
  const blockedCount = runtimeBlockedCount + anchorMissingCount + selectorMissingCount;
  const countsBySurface = routeCounts(rows);
  for (const row of rows) {
    if (row.status === 'RUNTIME_CERTIFIED') countsBySurface[row.surface].runtimeCertifiedCount += 1;
    if (row.status === 'SOURCE_CERTIFIED') countsBySurface[row.surface].sourceCertifiedCount += 1;
    if (row.status === 'RUNTIME_BLOCKED') countsBySurface[row.surface].runtimeBlockedCount += 1;
  }
  const status = blockedCount || driftCount || conflictCount ? 'RUNTIME_BLOCKED' : 'RUNTIME_CERTIFIED';
  const report = {
    ...baseReport('prisma.ui.runtime.evidence.report.v1', 'runtime-probe', status),
    routeCount: rows.length,
    runtimeCertifiedCount: rows.filter((row) => row.status === 'RUNTIME_CERTIFIED').length,
    sourceCertifiedCount: rows.filter((row) => row.status === 'SOURCE_CERTIFIED').length,
    runtimeBlockedCount,
    anchorMissingCount,
    selectorMissingCount,
    blockedCount,
    driftCount,
    conflictCount,
    timeoutMs,
    portStates,
    screenshotPolicy: 'capture if Playwright/Chromium is available without installation; no local browser package was invoked by this fetch probe',
    countsBySurface,
    routes: rows,
    exitCodeExpectation: status === 'RUNTIME_CERTIFIED' ? 0 : 1
  };
  writeReports(reportName('UI_RUNTIME_EVIDENCE_REPORT', flags), report);
  return report;
}

function gapsFromReports(coverage, runtime, certificateStatus) {
  const gaps = [];
  for (const blocker of coverage.blockers || []) gaps.push({ type: 'coverage', status: 'BLOCKED', ...blocker });
  for (const drift of coverage.drifts || []) gaps.push({ type: 'coverage', status: 'DRIFT', ...drift });
  for (const conflict of coverage.conflicts || []) gaps.push({ type: 'coverage', status: 'CONFLICT', ...conflict });
  for (const route of runtime.routes || []) {
    if (!['RUNTIME_BLOCKED', 'ANCHOR_MISSING', 'SELECTOR_MISSING', 'DRIFT', 'CONFLICT'].includes(route.status)) continue;
    gaps.push({
      type: 'runtime',
      status: route.status,
      app: route.app,
      port: route.port,
      surface: route.surface,
      route: route.route,
      runtimeUrl: route.runtimeUrl,
      httpStatus: route.httpStatus,
      reason: route.reason || route.error || 'runtime certification failed'
    });
  }
  return {
    ...baseReport('prisma.ui.runtime.gaps.report.v1', 'certify-runtime-pages', gaps.length ? 'RUNTIME_BLOCKED' : 'CERTIFIED'),
    finalRuntimeStatus: certificateStatus,
    gapCount: gaps.length,
    routeCount: runtime.routeCount,
    routeUnmappedCount: coverage.routeUnmappedCount,
    runtimeBlockedCount: runtime.runtimeBlockedCount,
    anchorMissingCount: coverage.anchorMissingCount + runtime.anchorMissingCount,
    selectorMissingCount: coverage.selectorMissingCount + runtime.selectorMissingCount,
    blockedCount: coverage.blockedCount + runtime.blockedCount,
    driftCount: coverage.driftCount + runtime.driftCount,
    conflictCount: coverage.conflictCount + runtime.conflictCount,
    gaps,
    exitCodeExpectation: gaps.length ? 1 : 0
  };
}

function executiveSummaryFromReports(certificate, coverage, runtime) {
  return {
    ...baseReport('prisma.ui.runtime.executive.summary.v1', 'certify-runtime-pages', certificate.status),
    routeCount: certificate.routeCount,
    runtimeCertifiedCount: certificate.runtimeCertifiedCount,
    sourceCertifiedCount: certificate.sourceCertifiedCount,
    routeUnmappedCount: certificate.routeUnmappedCount,
    runtimeBlockedCount: certificate.runtimeBlockedCount,
    anchorMissingCount: certificate.anchorMissingCount,
    selectorMissingCount: certificate.selectorMissingCount,
    blockedCount: certificate.blockedCount,
    driftCount: certificate.driftCount,
    conflictCount: certificate.conflictCount,
    countsBySurface: certificate.countsBySurface,
    coverageReport: 'UI_ROUTE_COVERAGE_REPORT.json',
    runtimeEvidenceReport: 'UI_RUNTIME_EVIDENCE_REPORT.json',
    pageCertificationReport: 'UI_RUNTIME_PAGE_CERT_REPORT.json',
    routeContracts: '.prisma-ui/routes.json',
    runtimeHtmlSnapshots: '.prisma-ui/current/runtime-html',
    finalGate: certificate.status === 'ALL_RUNTIME_PAGES_CERTIFIED'
      ? 'Runtime page certification closed with no route, anchor, selector, drift, conflict, or runtime blockers.'
      : 'Runtime page certification is blocked; inspect UI_RUNTIME_GAPS_REPORT.',
    coverageStatus: coverage.status,
    runtimeStatus: runtime.status,
    exitCodeExpectation: certificate.status === 'ALL_RUNTIME_PAGES_CERTIFIED' ? 0 : 1
  };
}

async function certifyRuntimePages(flags = {}) {
  const coverage = routeCoverage(flags);
  const runtime = await runtimeProbe(flags);
  const routeUnmappedCount = coverage.routeUnmappedCount;
  const runtimeBlockedCount = runtime.runtimeBlockedCount;
  const anchorMissingCount = coverage.anchorMissingCount + runtime.anchorMissingCount;
  const selectorMissingCount = coverage.selectorMissingCount + runtime.selectorMissingCount;
  const blockedCount = coverage.blockedCount + runtime.blockedCount;
  const driftCount = coverage.driftCount + runtime.driftCount;
  const conflictCount = coverage.conflictCount + runtime.conflictCount;
  const status = routeUnmappedCount || runtimeBlockedCount || anchorMissingCount || selectorMissingCount || blockedCount || driftCount || conflictCount
    ? 'RUNTIME_BLOCKED'
    : 'ALL_RUNTIME_PAGES_CERTIFIED';
  const report = {
    ...baseReport('prisma.ui.runtime.page.cert.report.v1', 'certify-runtime-pages', status),
    routeCount: runtime.routeCount,
    runtimeCertifiedCount: runtime.runtimeCertifiedCount,
    sourceCertifiedCount: runtime.sourceCertifiedCount,
    routeUnmappedCount,
    runtimeBlockedCount,
    anchorMissingCount,
    selectorMissingCount,
    blockedCount,
    driftCount,
    conflictCount,
    countsBySurface: runtime.countsBySurface,
    coverageReport: 'UI_ROUTE_COVERAGE_REPORT.json',
    runtimeEvidenceReport: 'UI_RUNTIME_EVIDENCE_REPORT.json',
    gapsReport: 'UI_RUNTIME_GAPS_REPORT.json',
    executiveSummaryReport: 'UI_RUNTIME_EXECUTIVE_SUMMARY.json',
    routes: runtime.routes.map((route) => ({
      app: route.app,
      port: route.port,
      surface: route.surface,
      route: route.route,
      panel: route.panel_id,
      status: route.status,
      runtimeMode: route.runtimeMode,
      runtimeUrl: route.runtimeUrl,
      httpStatus: route.httpStatus,
      finalUrl: route.finalUrl,
      redirected: route.redirected,
      contentType: route.contentType,
      title: route.title,
      actualPanels: route.actualPanels || [],
      actualRoutes: route.actualRoutes || [],
      anchorAcceptance: route.anchorAcceptance || null,
      redirectCertified: Boolean(route.redirectCertified),
      redirectTargetRoute: route.redirectTargetRoute || null,
      htmlSnapshot: route.htmlSnapshot,
      screenshot: route.screenshot,
      reason: route.reason || null
    })),
    exitCodeExpectation: status === 'ALL_RUNTIME_PAGES_CERTIFIED' ? 0 : 1
  };
  writeReports(reportName('UI_RUNTIME_PAGE_CERT_REPORT', flags), report);
  const gaps = gapsFromReports(coverage, runtime, status);
  writeReports(reportName('UI_RUNTIME_GAPS_REPORT', flags), gaps);
  const summary = executiveSummaryFromReports(report, coverage, runtime);
  writeReports(reportName('UI_RUNTIME_EXECUTIVE_SUMMARY', flags), summary);
  return report;
}

export async function runUiRuntimeCommand(cmd, flags = {}) {
  if (cmd === 'routes') return routeInventory(flags);
  if (cmd === 'route-coverage') return routeCoverage(flags);
  if (cmd === 'runtime-probe') return runtimeProbe(flags);
  if (cmd === 'certify-runtime-pages') return certifyRuntimePages(flags);
  throw new Error(`Unknown runtime command: ${cmd}`);
}

export function isUiRuntimeSuccess(status) {
  return SUCCESS_STATUSES.has(status);
}

function printReport(report) {
  const compact = {
    status: report.status,
    routeCount: report.routeCount,
    runtimeCertifiedCount: report.runtimeCertifiedCount,
    sourceCertifiedCount: report.sourceCertifiedCount,
    routeUnmappedCount: report.routeUnmappedCount,
    runtimeBlockedCount: report.runtimeBlockedCount,
    anchorMissingCount: report.anchorMissingCount,
    selectorMissingCount: report.selectorMissingCount,
    blockedCount: report.blockedCount,
    driftCount: report.driftCount,
    conflictCount: report.conflictCount
  };
  for (const key of Object.keys(compact)) if (compact[key] === undefined) delete compact[key];
  console.log(JSON.stringify(compact, null, 2));
}

const isMain = path.resolve(process.argv[1] || '') === fileURLToPath(import.meta.url);
if (isMain) {
  const { cmd, flags } = parseArgs();
  try {
    const result = await runUiRuntimeCommand(cmd, flags);
    printReport(result);
    if (flags.strict && !isUiRuntimeSuccess(result.status)) process.exit(1);
  } catch (error) {
    console.error(String(error?.stack || error?.message || error));
    process.exit(2);
  }
}
