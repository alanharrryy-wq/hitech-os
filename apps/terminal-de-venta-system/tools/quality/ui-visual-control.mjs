#!/usr/bin/env node
/* PRISMA Visual Control System v1 - registry, ownership, editable slots, and layer certification */
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import postcss from 'postcss';

const appRoot = process.cwd();
const ACTIVE_ROOTS = [
  'products/tablet/app',
  'products/pc/app',
  'products/mobile/app',
  'products/web/app',
  'products/chart-lab/app',
  'prisma-control-center/internal/web',
  'products/shared-ui',
  'shared'
];
const CONFIG_ROOTS = [
  'config/prisma-visual',
  'config/prisma-visual-system',
  'config/prisma-visual-os',
  'docs/visual-layer-map'
];
const SKIP_DIRS = new Set(['.git', 'node_modules', '.next', 'dist', 'build', 'coverage', '.turbo', '.cache', 'out', '__pycache__', '.generated']);
const TEXT_EXTS = new Set(['.tsx', '.jsx', '.ts', '.js', '.mjs', '.cjs', '.html', '.css', '.scss', '.md', '.json']);
const ACTIVE_TEXT_EXTS = new Set(['.tsx', '.jsx', '.ts', '.js', '.mjs', '.html', '.css', '.scss']);
const IMAGE_EXTS = new Set(['.png', '.jpg', '.jpeg', '.webp', '.svg', '.avif', '.gif']);
const SURFACE_IDS = ['chart-lab', 'web', 'tablet', 'pc', 'mobile', 'control-center', 'shared-ui'];
const EDITABLE_KNOBS = {
  shell: ['maxWidth', 'padding', 'gap', 'density', 'alignment', 'background', 'foreground'],
  background: ['background', 'opacity', 'blur/glass', 'zIndex range', 'visibility'],
  atmospheric: ['background', 'opacity', 'blur/glass', 'zIndex range', 'visibility'],
  'main-content': ['maxWidth', 'padding', 'gap', 'density', 'alignment'],
  panel: ['width', 'height', 'minHeight', 'maxWidth', 'padding', 'gap', 'radius', 'shadow', 'background', 'foreground', 'density'],
  card: ['width', 'height', 'minHeight', 'maxWidth', 'padding', 'gap', 'radius', 'shadow', 'background', 'foreground', 'density'],
  table: ['density', 'gap', 'padding', 'foreground', 'background', 'visibility'],
  form: ['gap', 'padding', 'alignment', 'foreground', 'background', 'density'],
  toolbar: ['gap', 'padding', 'alignment', 'placement', 'visibility', 'density'],
  header: ['height', 'padding', 'gap', 'background', 'foreground', 'alignment'],
  footer: ['height', 'padding', 'gap', 'background', 'foreground', 'alignment'],
  'buttons/action-zones': ['visibility', 'placement', 'button add/remove/move safety', 'gap', 'padding', 'alignment'],
  'empty-state': ['padding', 'gap', 'alignment', 'foreground', 'background', 'visibility'],
  'modal/drawer/popover': ['width', 'height', 'minHeight', 'maxWidth', 'padding', 'gap', 'radius', 'shadow', 'background', 'zIndex range', 'visibility']
};
const VISUAL_CONTROL_COMMANDS = new Set([
  'visual-control:inventory',
  'visual-control:owners',
  'visual-control:slots',
  'visual-control:layers',
  'visual-control:report',
  'visual-control:certify',
  'visual-control:self-test'
]);

function exists(p) {
  try { return fs.existsSync(p); } catch { return false; }
}

function readText(p) {
  return fs.readFileSync(p, 'utf8');
}

function readJson(p, fallback = null) {
  try { return JSON.parse(readText(p)); } catch { return fallback; }
}

function writeText(p, value) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, value, 'utf8');
}

function writeJson(p, value) {
  writeText(p, JSON.stringify(value, null, 2) + '\n');
}

function toPosix(value) {
  return String(value || '').replace(/\\/g, '/');
}

function absApp(rel) {
  return path.join(appRoot, rel);
}

function relApp(abs) {
  return toPosix(path.relative(appRoot, abs));
}

function nowIso() {
  return new Date().toISOString();
}

function uniq(values) {
  return Array.from(new Set(values.filter((value) => value !== undefined && value !== null && value !== '')));
}

function sortUniq(values) {
  return uniq(Array.isArray(values) ? values : []).sort((a, b) => String(a).localeCompare(String(b)));
}

function omitEmpty(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return value;
  const out = {};
  for (const [key, item] of Object.entries(value)) {
    if (item === null || item === undefined) continue;
    if (Array.isArray(item) && item.length === 0) continue;
    if (typeof item === 'object' && !Array.isArray(item) && Object.keys(item).length === 0) continue;
    out[key] = item;
  }
  return out;
}

function createProfileStore(prefix) {
  const keyToId = new Map();
  const profiles = {};
  return {
    ref(values) {
      const normalized = sortUniq(Array.isArray(values) ? values : values ? [values] : []);
      if (!normalized.length) return null;
      const key = JSON.stringify(normalized);
      if (!keyToId.has(key)) {
        const id = `${prefix}.${String(keyToId.size + 1).padStart(3, '0')}`;
        keyToId.set(key, id);
        profiles[id] = normalized;
      }
      return keyToId.get(key);
    },
    profiles
  };
}

function compactId(value) {
  return String(value || 'unknown')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '.')
    .replace(/^\.+|\.+$/g, '')
    .slice(0, 180) || 'unknown';
}

function safeRead(relOrAbs, limit = 1_200_000) {
  const full = path.isAbsolute(relOrAbs) ? relOrAbs : absApp(relOrAbs);
  try {
    const stat = fs.statSync(full);
    if (stat.size > limit) return '';
    return readText(full);
  } catch {
    return '';
  }
}

function walk(dir, out = []) {
  if (!exists(dir)) return out;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (!SKIP_DIRS.has(entry.name)) walk(full, out);
    } else {
      out.push(full);
    }
  }
  return out;
}

function gitMeta() {
  const run = (args) => {
    try { return execFileSync('git', args, { cwd: appRoot, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim(); }
    catch { return null; }
  };
  return {
    repoHead: run(['rev-parse', 'HEAD']),
    branch: run(['branch', '--show-current'])
  };
}

function parseArgs(raw = process.argv.slice(2)) {
  const cmd = raw.shift() || 'report';
  const flags = { _: [] };
  for (let i = 0; i < raw.length; i += 1) {
    const item = raw[i];
    if (!item.startsWith('--')) {
      flags._.push(item);
      continue;
    }
    const key = item.slice(2);
    const next = raw[i + 1];
    if (next && !next.startsWith('--')) {
      flags[key] = next;
      i += 1;
    } else {
      flags[key] = true;
    }
  }
  return { cmd, flags };
}

function loadState(flags = {}) {
  const uiRoot = path.join(appRoot, '.prisma-ui');
  const outputRoot = flags['output-root']
    ? path.resolve(String(flags['output-root']))
    : uiRoot;
  const governanceRoot = path.join(appRoot, '.governance', 'current');
  const panelDir = path.join(uiRoot, 'panels');
  const panels = exists(panelDir)
    ? fs.readdirSync(panelDir)
      .filter((name) => name.endsWith('.json'))
      .sort()
      .map((name) => {
        const full = path.join(panelDir, name);
        return { ...(readJson(full, { __parse_error: true }) || {}), __file: relApp(full) };
      })
    : [];
  return {
    uiRoot,
    currentRoot: path.join(outputRoot, 'current'),
    visualRoot: path.join(outputRoot, 'visual-control'),
    governanceRoot,
    registry: readJson(path.join(uiRoot, 'registry.json'), {}),
    surfaces: readJson(path.join(uiRoot, 'surfaces.json'), { surfaces: [] }),
    routes: readJson(path.join(uiRoot, 'routes.json'), { routes: [] }),
    panels,
    runtimeCert: readJson(path.join(uiRoot, 'current', 'UI_RUNTIME_PAGE_CERT_REPORT.json'), null),
    authorityLock: readJson(path.join(governanceRoot, 'AUTHORITY_READSET.lock.json'), null),
    contractGateMatrix: readJson(path.join(governanceRoot, 'CONTRACT_AND_GATE_MATRIX.json'), null),
    layerMap: readJson(path.join(appRoot, 'docs', 'visual-layer-map', 'layer-map.json'), null)
  };
}

function surfaceDefinitions(state) {
  return Array.isArray(state.surfaces?.surfaces) ? state.surfaces.surfaces : [];
}

function targetSurfaceIds(state) {
  const explicit = Array.isArray(state.registry?.targetApps) ? state.registry.targetApps : [];
  return explicit.length ? explicit : surfaceDefinitions(state).filter((surface) => surface.port !== null && surface.port !== undefined).map((surface) => surface.id);
}

function routeContracts(state) {
  return Array.isArray(state.routes?.routes) ? state.routes.routes : [];
}

function runtimeByRoute(state) {
  const rows = Array.isArray(state.runtimeCert?.routes) ? state.runtimeCert.routes : [];
  const map = new Map();
  for (const row of rows) map.set(`${row.surface}:${row.route}`, row);
  return map;
}

function evidenceClassForPath(rel) {
  const file = toPosix(rel);
  const low = file.toLowerCase();
  if (low.includes('/node_modules/') || low.includes('/.next/') || low.includes('/dist/') || low.includes('/build/') || low.includes('/coverage/') || low.includes('/.generated/')) return 'generatedEvidenceOnly';
  if (low.startsWith('.prisma_installer_backups/') || low.startsWith('obsoletos/') || low.includes('/archive/') || low.includes('/archived/')) return 'inactiveArchive';
  if (low.startsWith('fixtures/') || low.includes('/fixtures/') || low.includes('/__fixtures__/')) return 'fixtureOnly';
  if (low.startsWith('docs/') || low.endsWith('.md')) return 'docsOnly';
  if (low.startsWith('.prisma-ui/current/') || low.startsWith('.governance/current/') || low.startsWith('reports/') || low.includes('/tools/_local/evidence/')) return 'generatedEvidenceOnly';
  if (low.startsWith('tools/') || low.includes('/tools/') || low.startsWith('quality/')) return 'toolingOnly';
  return 'activeRuntime';
}

function surfaceFromPath(rel) {
  const file = toPosix(rel);
  if (file.startsWith('products/tablet/app/')) return 'tablet';
  if (file.startsWith('products/pc/app/')) return 'pc';
  if (file.startsWith('products/mobile/app/')) return 'mobile';
  if (file.startsWith('products/web/app/')) return 'web';
  if (file.startsWith('products/chart-lab/app/')) return 'chart-lab';
  if (file.startsWith('prisma-control-center/internal/web/')) return 'control-center';
  if (file.startsWith('products/shared-ui/') || file.startsWith('shared/')) return 'shared-ui';
  if (file.startsWith('config/') || file.startsWith('styles/')) return 'shared-ui';
  return 'unknown';
}

function excludedSurfaces(surface) {
  if (!surface || surface === 'shared-ui') return [];
  return SURFACE_IDS.filter((item) => item !== surface && item !== 'shared-ui');
}

function scanFiles() {
  const roots = [...ACTIVE_ROOTS, ...CONFIG_ROOTS].map(absApp).filter(exists);
  const files = [];
  for (const root of roots) walk(root, files);
  return uniq(files.map(relApp));
}

function scanActiveFiles() {
  return scanFiles().filter((file) => evidenceClassForPath(file) === 'activeRuntime' && ACTIVE_TEXT_EXTS.has(path.extname(file).toLowerCase()));
}

function resolveImport(fromRel, specifier) {
  if (!specifier.startsWith('.')) return null;
  const base = path.dirname(absApp(fromRel));
  const candidate = path.resolve(base, specifier);
  const variants = [candidate, `${candidate}.css`, `${candidate}.scss`];
  for (const item of variants) {
    if (exists(item)) return relApp(item);
  }
  return null;
}

function cssOwnersForComponent(componentRel, fallbackCss = null) {
  const owners = [];
  if (fallbackCss) owners.push(fallbackCss);
  if (!componentRel) return uniq(owners);
  const text = safeRead(componentRel);
  const importRx = /import\s+(?:[^'"]+\s+from\s+)?["']([^"']+\.(?:css|scss))["']/g;
  let match;
  while ((match = importRx.exec(text))) {
    const resolved = resolveImport(componentRel, match[1]);
    if (resolved) owners.push(resolved);
  }
  const dir = path.dirname(absApp(componentRel));
  if (exists(dir)) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      if (entry.isFile() && /\.(module\.)?(css|scss)$/i.test(entry.name)) owners.push(relApp(path.join(dir, entry.name)));
    }
  }
  return uniq(owners).filter((file) => exists(absApp(file)));
}

function detectComponentTraits(file) {
  const text = safeRead(file);
  return {
    hasButton: /<button\b|<Button\b|role=["']button["']/i.test(text),
    hasEventHandler: /\bon(?:Click|Submit|Change|Pointer|Mouse|Key|Touch)[A-Z]?\s*=|addEventListener\s*\(/.test(text),
    hasFormSubmit: /<form\b|\btype=["']submit["']|\bformAction\b/i.test(text),
    hasNavigation: /\bhref\s*=|\brouter\.(?:push|replace)\b|\bredirect\s*\(/.test(text),
    hasPermissionSignals: /\b(permission|role|auth|can[A-Z]|entitlement|license|guard|disabled)\b/.test(text),
    dataPrismaPanels: uniq(Array.from(text.matchAll(/data-prisma-panel\s*=\s*{?\s*["'`]([^"'`}]+)["'`]\s*}?/g)).map((m) => m[1])),
    classNames: uniq(Array.from(text.matchAll(/className\s*=\s*{?\s*["'`]([^"'`}]+)["'`]\s*}?/g)).flatMap((m) => m[1].split(/\s+/))).slice(0, 80)
  };
}

function buildComponentMap(state, routes, panels) {
  const components = new Map();
  function add(pathRel, payload = {}) {
    if (!pathRel) return;
    const normalized = toPosix(pathRel);
    const existing = components.get(normalized) || {
      component_id: compactId(normalized),
      path: normalized,
      fileClass: evidenceClassForPath(normalized),
      surface: surfaceFromPath(normalized),
      routes: [],
      panels: [],
      cssOwners: [],
      assetOwners: [],
      tokenOwners: tokenOwners(),
      sharedGlobalOwner: surfaceFromPath(normalized) === 'shared-ui',
      exists: exists(absApp(normalized))
    };
    existing.routes = uniq([...existing.routes, ...(payload.routes || [])]);
    existing.panels = uniq([...existing.panels, ...(payload.panels || [])]);
    existing.cssOwners = uniq([...existing.cssOwners, ...(payload.cssOwners || [])]);
    components.set(normalized, existing);
  }
  for (const route of routes) {
    add(route.ownerComponent, {
      routes: [`${route.surface}:${route.route}`],
      cssOwners: cssOwnersForComponent(route.ownerComponent)
    });
    for (const layout of route.layoutFiles || []) {
      add(layout, {
        routes: [`${route.surface}:${route.route}`],
        cssOwners: cssOwnersForComponent(layout)
      });
    }
  }
  for (const panel of panels) {
    add(panel.owner_component, {
      panels: [panel.panel_id],
      routes: panel.route ? [`${panel.surface}:${panel.route}`] : [],
      cssOwners: cssOwnersForComponent(panel.owner_component, panel.owner_css_module)
    });
  }
  return Array.from(components.values()).map((component) => {
    const traits = component.exists ? detectComponentTraits(component.path) : {};
    return {
      ...component,
      ...traits,
      riskClass: component.sharedGlobalOwner ? 'sharedGlobalRisk' : (traits.hasEventHandler ? 'visualWithFunctionalRisk' : 'safeVisualOnly')
    };
  }).sort((a, b) => a.path.localeCompare(b.path));
}

function inferRoutesForComponent(file) {
  const rel = toPosix(file);
  if (rel.startsWith('products/mobile/app/src/components/prisma-app/')) return ['mobile:/prisma-app'];
  if (rel.startsWith('products/mobile/app/app/prisma-command/')) return ['mobile:/prisma-command'];
  if (rel.startsWith('products/mobile/app/app/prisma-app/install/')) return ['mobile:/prisma-app/install'];
  if (rel.startsWith('products/mobile/app/app/prisma-app/offline/')) return ['mobile:/prisma-app/offline'];
  if (rel.startsWith('products/mobile/app/app/prisma-app/')) return ['mobile:/prisma-app'];
  if (rel.startsWith('products/tablet/app/components/pos/')) return ['tablet:/pos'];
  if (rel.startsWith('products/pc/app/components/')) return ['pc:*'];
  return [`${surfaceFromPath(rel)}:*`];
}

function mergeDiscoveredComponents(components, files) {
  const byPath = new Map(components.map((component) => [component.path, component]));
  for (const file of files) {
    if (!/\.(tsx|jsx|html)$/i.test(file)) continue;
    if (evidenceClassForPath(file) !== 'activeRuntime') continue;
    const text = safeRead(file);
    if (!text || !(/<button\b|<Button\b|role=["']button["']/i.test(text))) continue;
    const traits = detectComponentTraits(file);
    const existing = byPath.get(file) || {
      component_id: compactId(file),
      path: file,
      fileClass: evidenceClassForPath(file),
      surface: surfaceFromPath(file),
      routes: inferRoutesForComponent(file),
      panels: [],
      cssOwners: cssOwnersForComponent(file),
      assetOwners: [],
      tokenOwners: tokenOwners(),
      sharedGlobalOwner: surfaceFromPath(file) === 'shared-ui',
      exists: exists(absApp(file))
    };
    existing.routes = uniq([...(existing.routes || []), ...inferRoutesForComponent(file)]);
    existing.cssOwners = uniq([...(existing.cssOwners || []), ...cssOwnersForComponent(file)]);
    Object.assign(existing, traits, {
      riskClass: existing.sharedGlobalOwner ? 'sharedGlobalRisk' : (traits.hasEventHandler ? 'visualWithFunctionalRisk' : 'safeVisualOnly')
    });
    byPath.set(file, existing);
  }
  return Array.from(byPath.values()).sort((a, b) => a.path.localeCompare(b.path));
}

function tokenOwners() {
  const candidates = [
    'config/prisma-visual/recipe-map.json',
    'config/prisma-visual/layer-budget.json',
    'config/prisma-visual/authority-map.json',
    'config/prisma-visual-system/tokens.registry.json',
    'config/prisma-visual-system/viscurate-layer-budget.json',
    'config/prisma-visual-os/prisma-visual-controls.active.json'
  ];
  return candidates.filter((file) => exists(absApp(file)));
}

function cssAssetOwners(cssRel, declarations) {
  const owners = [];
  const values = Object.values(declarations || {}).join(' ');
  const rx = /url\(([^)]+)\)/g;
  let match;
  while ((match = rx.exec(values))) {
    const raw = match[1].trim().replace(/^["']|["']$/g, '');
    if (!raw || raw.startsWith('data:') || /^https?:\/\//i.test(raw)) continue;
    if (raw.startsWith('/')) owners.push(raw);
    else {
      const resolved = resolveImport(cssRel, raw);
      if (resolved) owners.push(resolved);
    }
  }
  return uniq(owners);
}

function layerNameForSelector(selector, declarations) {
  const low = `${selector} ${Object.keys(declarations || {}).join(' ')}`.toLowerCase();
  if (/modal|drawer|popover|dialog|overlay|sheet/.test(low)) return 'modal/drawer/popover';
  if (/background|backdrop|atmosphere|ambient|aura|canvas|wallpaper|hero|::before|::after|body|html/.test(low)) {
    if (/aura|atmosphere|ambient|veil|mist|glass|cloud/.test(low)) return 'atmospheric';
    return 'background';
  }
  if (/header|topbar|navbar|nav\b/.test(low)) return 'header';
  if (/footer|bottombar/.test(low)) return 'footer';
  if (/toolbar|actions|command|segmented|button|btn|chip/.test(low)) return 'toolbar';
  if (/table|grid|list|row|cell/.test(low)) return 'table';
  if (/form|input|select|textarea|field/.test(low)) return 'form';
  if (/empty|blank|placeholder/.test(low)) return 'empty-state';
  if (/card|tile|metric|kpi/.test(low)) return 'card';
  if (/panel|pane|drawer|workspace|section/.test(low)) return 'panel';
  if (/shell|layout|page|screen|main|content/.test(low)) return 'shell';
  return 'main-content';
}

function safetyForLayer(region, declarations, surface) {
  if (surface === 'shared-ui') return 'sharedGlobalRisk';
  const props = Object.keys(declarations || {}).map((item) => item.toLowerCase());
  if (region === 'toolbar' && props.some((item) => item.includes('pointer') || item === 'display' || item === 'visibility')) return 'visualWithFunctionalRisk';
  if (region === 'buttons/action-zones') return 'functionalControl';
  if (props.includes('z-index') || props.includes('position') || props.includes('display') || props.includes('visibility')) return 'visualWithFunctionalRisk';
  if (region === 'modal/drawer/popover' || region === 'background' || region === 'atmospheric') return 'visualWithFunctionalRisk';
  return 'safeVisualOnly';
}

function collectRuleDeclarations(rule) {
  const declarations = {};
  rule.walkDecls((decl) => {
    if (/^(background|background-image|position|z-index|isolation|overflow|opacity|backdrop-filter|-webkit-backdrop-filter|height|min-height|max-height|width|min-width|max-width|padding|gap|border-radius|box-shadow|display|visibility|filter|color)$/i.test(decl.prop)) {
      declarations[decl.prop] = decl.value;
    }
  });
  return declarations;
}

function parseCssLayers(cssRel) {
  const text = safeRead(cssRel, 2_500_000);
  if (!text) return [];
  const layers = [];
  try {
    const root = postcss.parse(text, { from: cssRel });
    root.walkRules((rule) => {
      const declarations = collectRuleDeclarations(rule);
      if (!Object.keys(declarations).length) return;
      const selector = String(rule.selector || '').replace(/\s+/g, ' ').trim();
      const surface = surfaceFromPath(cssRel);
      const region = layerNameForSelector(selector, declarations);
      const risks = [];
      if (declarations['z-index']) risks.push(`z-index:${declarations['z-index']}`);
      if (declarations.position && /fixed|absolute|sticky/i.test(declarations.position)) risks.push(`position:${declarations.position}`);
      if (declarations.opacity && Number.parseFloat(declarations.opacity) < 1) risks.push(`opacity:${declarations.opacity}`);
      if (declarations['backdrop-filter'] || declarations['-webkit-backdrop-filter'] || declarations.filter) risks.push('filter/glass');
      layers.push({
        layer_id: compactId(`${cssRel}:${selector}`),
        surface,
        file: cssRel,
        selector: selector.slice(0, 500),
        visualRegion: region,
        layer: region,
        ownerCss: cssRel,
        ownerComponent: null,
        evidenceClass: evidenceClassForPath(cssRel),
        safetyClassification: safetyForLayer(region, declarations, surface),
        background: declarations.background || declarations['background-image'] || null,
        position: declarations.position || null,
        zIndex: declarations['z-index'] || null,
        isolation: declarations.isolation || null,
        overflow: declarations.overflow || null,
        opacity: declarations.opacity || null,
        backdropFilter: declarations['backdrop-filter'] || declarations['-webkit-backdrop-filter'] || declarations.filter || null,
        height: declarations.height || declarations['min-height'] || declarations['max-height'] || null,
        width: declarations.width || declarations['min-width'] || declarations['max-width'] || null,
        spacing: declarations.padding || declarations.gap || null,
        radius: declarations['border-radius'] || null,
        shadow: declarations['box-shadow'] || null,
        assetOwners: cssAssetOwners(cssRel, declarations),
        risks
      });
    });
  } catch (error) {
    layers.push({
      layer_id: compactId(`${cssRel}:parse-error`),
      surface: surfaceFromPath(cssRel),
      file: cssRel,
      selector: null,
      visualRegion: 'unknown',
      layer: 'unknown',
      ownerCss: cssRel,
      ownerComponent: null,
      evidenceClass: evidenceClassForPath(cssRel),
      safetyClassification: 'visualWithFunctionalRisk',
      risks: [`css parse failed: ${String(error?.message || error)}`]
    });
  }
  return layers;
}

function scanVisualAssets(files) {
  return files
    .filter((file) => IMAGE_EXTS.has(path.extname(file).toLowerCase()))
    .filter((file) => /visual-backgrounds|surface-visual-governor|atmosphere-assets|backgrounds/i.test(file))
    .map((file) => ({
      asset_id: compactId(file),
      surface: surfaceFromPath(file),
      file,
      ownerSurface: surfaceFromPath(file),
      evidenceClass: evidenceClassForPath(file),
      layer: 'background',
      safetyClassification: surfaceFromPath(file) === 'shared-ui' ? 'sharedGlobalRisk' : 'visualWithFunctionalRisk'
    }))
    .sort((a, b) => a.file.localeCompare(b.file));
}

function buildLayers(files) {
  const cssFiles = files.filter((file) => /\.(css|scss)$/i.test(file) && evidenceClassForPath(file) === 'activeRuntime');
  const layers = cssFiles.flatMap(parseCssLayers);
  const assets = scanVisualAssets(files);
  return {
    cssFiles,
    assets,
    layers: layers.sort((a, b) => `${a.surface}:${a.file}:${a.selector}`.localeCompare(`${b.surface}:${b.file}:${b.selector}`))
  };
}

function buildRoutes(state) {
  const runtime = runtimeByRoute(state);
  return routeContracts(state).map((route) => {
    const key = `${route.surface}:${route.route}`;
    const runtimeRow = runtime.get(key);
    const ownerCss = cssOwnersForComponent(route.ownerComponent);
    return {
      route_id: route.route_id,
      human_id: `${route.app} ${route.route}`,
      app: route.app,
      surface: route.surface,
      route: route.route,
      routePath: route.route,
      pageFile: route.pageFile,
      layoutFiles: route.layoutFiles || [],
      ownerComponent: route.ownerComponent,
      ownerCss,
      currentPanelContract: route.currentPanelContract || null,
      runtimeUrl: route.runtimeUrl,
      runtimeMode: route.runtimeMode,
      runtimeCertificationStatus: runtimeRow?.status || (route.runtimeMode === 'runtime' ? 'RUNTIME_CERTIFIED_CANDIDATE' : 'SOURCE_CERTIFIED'),
      runtimeSourceCertification: runtimeRow ? runtimeRow.status : (route.runtimeMode === 'runtime' ? 'runtimeCandidate' : 'sourceCertified'),
      certificationEvidence: runtimeRow?.htmlSnapshot || '.prisma-ui/routes.json',
      anchors: route.anchors || {},
      excludedSurfaces: excludedSurfaces(route.surface),
      safetyClassification: route.surface === 'shared-ui' ? 'sharedGlobalRisk' : 'visualWithFunctionalRisk'
    };
  });
}

function visualRegionForPanel(panel) {
  const id = String(panel.panel_id || '').toLowerCase();
  const title = String(panel.title || '').toLowerCase();
  const joined = `${id} ${title}`;
  if (/payment|overlay|checkout/.test(joined)) return 'modal/drawer/popover';
  if (/cart|panel|workspace|stock|settings|catalog|dashboard/.test(joined)) return 'panel';
  if (/grid|list|table/.test(joined)) return 'table';
  if (/search|form|filter/.test(joined)) return 'form';
  if (/rail|toolbar|action|category/.test(joined)) return 'toolbar';
  return 'panel';
}

function buildVisualRegions(routes, panels, layers, components = []) {
  const regions = [];
  for (const route of routes) {
    regions.push({
      region_id: `${route.route_id}.shell`,
      surface: route.surface,
      route: route.route,
      human_id: `${route.human_id} shell`,
      visualRegion: 'shell',
      ownerComponent: route.ownerComponent,
      ownerCss: route.ownerCss,
      assetOwner: null,
      tokenOwner: tokenOwners(),
      safetyClassification: route.surface === 'shared-ui' ? 'sharedGlobalRisk' : 'visualWithFunctionalRisk',
      excludedSurfaces: route.excludedSurfaces
    });
    regions.push({
      region_id: `${route.route_id}.main-content`,
      surface: route.surface,
      route: route.route,
      human_id: `${route.human_id} main content`,
      visualRegion: 'main-content',
      ownerComponent: route.ownerComponent,
      ownerCss: route.ownerCss,
      assetOwner: null,
      tokenOwner: tokenOwners(),
      safetyClassification: 'safeVisualOnly',
      excludedSurfaces: route.excludedSurfaces
    });
  }
  for (const panel of panels) {
    const region = visualRegionForPanel(panel);
    regions.push({
      region_id: panel.panel_id,
      surface: panel.surface,
      route: panel.route,
      human_id: panel.title || panel.panel_id,
      visualRegion: region,
      ownerComponent: panel.owner_component || null,
      ownerCss: uniq([panel.owner_css_module, ...cssOwnersForComponent(panel.owner_component, panel.owner_css_module)]),
      assetOwner: [],
      tokenOwner: tokenOwners(),
      safetyClassification: region === 'toolbar' ? 'visualWithFunctionalRisk' : 'safeVisualOnly',
      excludedSurfaces: panel.forbidden_surfaces || excludedSurfaces(panel.surface),
      sourceContract: panel.__file
    });
  }
  for (const layer of layers.filter((item) => item.background || item.backdropFilter || item.zIndex)) {
    regions.push({
      region_id: `${layer.layer_id}.layer`,
      surface: layer.surface,
      route: null,
      human_id: `${layer.surface} ${layer.visualRegion} layer`,
      visualRegion: layer.visualRegion,
      ownerComponent: null,
      ownerCss: [layer.ownerCss],
      assetOwner: layer.assetOwners || [],
      tokenOwner: tokenOwners(),
      safetyClassification: layer.safetyClassification,
      excludedSurfaces: excludedSurfaces(layer.surface),
      layerOwner: layer.layer_id
    });
  }
  for (const component of components.filter((item) => item.hasButton)) {
    const routeRefs = component.routes.length ? component.routes : [`${component.surface}:*`];
    for (const routeRef of routeRefs) {
      const [surface, ...routeParts] = routeRef.split(':');
      const route = routeParts.join(':') || null;
      regions.push({
        region_id: `${component.component_id}.${compactId(route || 'all-routes')}.buttons`,
        surface: surface || component.surface,
        route: route === '*' ? null : route,
        human_id: `${component.path} button/action zone`,
        visualRegion: 'buttons/action-zones',
        ownerComponent: component.path,
        ownerCss: component.cssOwners || [],
        assetOwner: component.assetOwners || [],
        tokenOwner: tokenOwners(),
        safetyClassification: component.hasEventHandler || component.hasFormSubmit || component.hasNavigation || component.hasPermissionSignals
          ? 'functionalControl'
          : 'visualWithFunctionalRisk',
        excludedSurfaces: excludedSurfaces(surface || component.surface),
        functionalSignals: {
          hasButton: Boolean(component.hasButton),
          hasEventHandler: Boolean(component.hasEventHandler),
          hasFormSubmit: Boolean(component.hasFormSubmit),
          hasNavigation: Boolean(component.hasNavigation),
          hasPermissionSignals: Boolean(component.hasPermissionSignals)
        }
      });
    }
  }
  return regions.sort((a, b) => `${a.surface}:${a.route}:${a.region_id}`.localeCompare(`${b.surface}:${b.route}:${b.region_id}`));
}

function safetyForSlot(region, knob, ownerSurface) {
  const low = `${region} ${knob}`.toLowerCase();
  if (ownerSurface === 'shared-ui') return 'sharedGlobalRisk';
  if (low.includes('button add/remove/move')) return 'functionalControl';
  if (/zindex|z-index|visibility|placement|height|background|blur|glass|opacity|modal|drawer|popover|toolbar/.test(low)) return 'visualWithFunctionalRisk';
  return 'safeVisualOnly';
}

function gatesForSlot(slot) {
  const gates = [
    'node tools/quality/ui-certainty.mjs self-test --strict',
    'node tools/quality/ui-certainty.mjs certify-all-surfaces --strict',
    'node tools/quality/ui-certainty.mjs zero-important',
    'node tools/quality/ui-certainty.mjs scope --all',
    'node tools/quality/ui-certainty.mjs visual-control:certify --strict'
  ];
  if (slot.surface) gates.splice(2, 0, `node tools/quality/ui-certainty.mjs certify --surface ${slot.surface} --strict`);
  return gates;
}

function buildEditableSlots(regions, components) {
  const componentByPath = new Map(components.map((component) => [component.path, component]));
  const slots = [];
  for (const region of regions) {
    const knobs = EDITABLE_KNOBS[region.visualRegion] || EDITABLE_KNOBS['main-content'];
    const component = region.ownerComponent ? componentByPath.get(region.ownerComponent) : null;
    for (const knob of knobs) {
      const safetyClassification = safetyForSlot(region.visualRegion, knob, region.surface);
      const functionalSignals = component ? {
        hasButton: Boolean(component.hasButton),
        hasEventHandler: Boolean(component.hasEventHandler),
        hasFormSubmit: Boolean(component.hasFormSubmit),
        hasNavigation: Boolean(component.hasNavigation),
        hasPermissionSignals: Boolean(component.hasPermissionSignals)
      } : {};
      slots.push({
        slot_id: compactId(`${region.region_id}.${knob}`),
        target: region.region_id,
        human_id: `${region.human_id} / ${knob}`,
        surface: region.surface,
        route: region.route,
        visualRegion: region.visualRegion,
        knob,
        ownerComponent: region.ownerComponent,
        ownerCss: region.ownerCss || [],
        assetOwner: region.assetOwner || [],
        tokenOwner: region.tokenOwner || [],
        safetyClassification,
        functionalSignals,
        buttonRemovalSafety: knob === 'button add/remove/move safety'
          ? (functionalSignals.hasEventHandler || functionalSignals.hasFormSubmit || functionalSignals.hasNavigation ? 'removal unsafe; prefer hide/disable/reposition only with owner review' : 'decorative not proven; require source review before removal')
          : null,
        allowedChangeShape: slotChangeShape(knob, safetyClassification),
        gates: gatesForSlot(region),
        rollbackScope: uniq([region.ownerComponent, ...(region.ownerCss || []), ...(region.assetOwner || [])]).filter(Boolean),
        excludedSurfaces: region.excludedSurfaces || []
      });
    }
  }
  return slots.sort((a, b) => a.slot_id.localeCompare(b.slot_id));
}

function slotChangeShape(knob, safetyClassification) {
  if (safetyClassification === 'functionalControl') return 'Plan only. Do not remove or move functional controls without explicit owner and behavior review.';
  if (/zIndex|z-index/i.test(knob)) return 'Bounded z-index range inside the owning surface/layer budget only.';
  if (/background|blur|glass|opacity/i.test(knob)) return 'Change only owner CSS/asset/token files; preserve readability and route anchors.';
  if (/height|minHeight|width|maxWidth|padding|gap|radius|shadow|density|alignment|placement/i.test(knob)) return 'Local owner-only visual adjustment with route/surface gates.';
  return 'Local visual-only owner change with route/surface gates.';
}

function buildOwners(routes, regions, components, layers, assets) {
  const cssOwners = new Map();
  for (const component of components) {
    for (const css of component.cssOwners || []) {
      const entry = cssOwners.get(css) || {
        owner_id: compactId(css),
        file: css,
        surface: surfaceFromPath(css),
        routes: [],
        panels: [],
        components: [],
        safetyClassification: surfaceFromPath(css) === 'shared-ui' ? 'sharedGlobalRisk' : 'safeVisualOnly'
      };
      entry.routes = uniq([...entry.routes, ...component.routes]);
      entry.panels = uniq([...entry.panels, ...component.panels]);
      entry.components = uniq([...entry.components, component.path]);
      cssOwners.set(css, entry);
    }
  }
  return {
    componentOwners: components,
    cssOwners: Array.from(cssOwners.values()).sort((a, b) => a.file.localeCompare(b.file)),
    assetOwners: assets,
    tokenThemeOwners: tokenOwners().map((file) => ({
      owner_id: compactId(file),
      file,
      surface: 'shared-ui',
      safetyClassification: 'sharedGlobalRisk',
      affectedSurfaces: targetSurfaceIds({ registry: { targetApps: SURFACE_IDS }, surfaces: { surfaces: [] } }).filter((surface) => surface !== 'shared-ui')
    })),
    routeOwners: routes.map((route) => ({
      route_id: route.route_id,
      surface: route.surface,
      route: route.route,
      ownerComponent: route.ownerComponent,
      ownerCss: route.ownerCss,
      certificationStatus: route.runtimeCertificationStatus
    })),
    regionOwners: regions.map((region) => ({
      region_id: region.region_id,
      surface: region.surface,
      route: region.route,
      ownerComponent: region.ownerComponent,
      ownerCss: region.ownerCss,
      assetOwner: region.assetOwner,
      tokenOwner: region.tokenOwner,
      safetyClassification: region.safetyClassification
    }))
  };
}

function scanImportantHits(files) {
  const hits = [];
  for (const file of files) {
    if (!/\.(css|scss|tsx|jsx|ts|js|mjs|html)$/i.test(file)) continue;
    const text = safeRead(file, 1_800_000);
    if (!text) continue;
    text.split(/\r?\n/).forEach((line, index) => {
      if (line.includes('!important')) hits.push({ file, line: index + 1, text: line.trim().slice(0, 220), evidenceClass: evidenceClassForPath(file) });
    });
  }
  return hits;
}

function buildRisks(state, routes, regions, slots, layers, activeFiles, allFiles, requestedSurface = null) {
  const targets = requestedSurface ? [requestedSurface] : targetSurfaceIds(state);
  const routeSurfaces = new Set(routes.map((route) => route.surface));
  const panelSurfaces = new Set(state.panels.map((panel) => panel.surface));
  const missingTargetSurfaces = targets.filter((surface) => !surfaceDefinitions(state).some((item) => item.id === surface));
  const targetSurfacesWithoutRoutes = targets.filter((surface) => !routeSurfaces.has(surface));
  const targetSurfacesWithoutPanelContracts = targets.filter((surface) => !panelSurfaces.has(surface) && surface !== 'control-center');
  const routeOwnerMissing = routes.filter((route) => !route.ownerComponent || !exists(absApp(route.ownerComponent)));
  const regionOwnerMissing = regions.filter((region) => !region.ownerComponent && !(Array.isArray(region.ownerCss) && region.ownerCss.length) && !(Array.isArray(region.assetOwner) && region.assetOwner.length));
  const slotUnclassified = slots.filter((slot) => !slot.safetyClassification);
  const activeImportantHits = scanImportantHits(activeFiles).filter((hit) => hit.evidenceClass === 'activeRuntime');
  const ambiguousActiveLayerOwners = layers.filter((layer) => layer.evidenceClass === 'activeRuntime' && (!layer.surface || layer.surface === 'unknown'));
  const docsOnlyCount = allFiles.filter((file) => evidenceClassForPath(file) === 'docsOnly').length;
  const fixtureOnlyCount = allFiles.filter((file) => evidenceClassForPath(file) === 'fixtureOnly').length;
  const generatedEvidenceOnlyCount = allFiles.filter((file) => evidenceClassForPath(file) === 'generatedEvidenceOnly').length;
  const inactiveArchiveCount = allFiles.filter((file) => evidenceClassForPath(file) === 'inactiveArchive').length;
  const blockers = [
    ...missingTargetSurfaces.map((surface) => ({ category: 'surface', surface, reason: 'target surface is not registered' })),
    ...targetSurfacesWithoutRoutes.map((surface) => ({ category: 'routes', surface, reason: 'target surface has no route entries' })),
    ...routeOwnerMissing.map((route) => ({ category: 'owner', surface: route.surface, route: route.route, reason: `route owner missing: ${route.ownerComponent}` })),
    ...regionOwnerMissing.map((region) => ({ category: 'owner', surface: region.surface, route: region.route, reason: `visual region owner missing: ${region.region_id}` })),
    ...slotUnclassified.map((slot) => ({ category: 'slots', surface: slot.surface, route: slot.route, reason: `slot unclassified: ${slot.slot_id}` })),
    ...activeImportantHits.map((hit) => ({ category: 'zero-important', file: hit.file, line: hit.line, reason: 'active runtime file contains !important' })),
    ...ambiguousActiveLayerOwners.map((layer) => ({ category: 'layers', file: layer.file, selector: layer.selector, reason: 'active layer owner surface is ambiguous' }))
  ];
  const warnings = [
    ...targetSurfacesWithoutPanelContracts.map((surface) => ({ category: 'panels', surface, reason: 'surface is route-covered but has only workspace or route-level visual control' }))
  ];
  return {
    status: blockers.length ? 'BLOCKED' : 'CERTIFIED',
    blockerCount: blockers.length,
    warningCount: warnings.length,
    missingTargetSurfaces,
    targetSurfacesWithoutRoutes,
    targetSurfacesWithoutPanelContracts,
    routeOwnerMissingCount: routeOwnerMissing.length,
    regionOwnerMissingCount: regionOwnerMissing.length,
    slotUnclassifiedCount: slotUnclassified.length,
    activeImportantCount: activeImportantHits.length,
    ambiguousActiveLayerOwnerCount: ambiguousActiveLayerOwners.length,
    docsOnlyCount,
    fixtureOnlyCount,
    generatedEvidenceOnlyCount,
    inactiveArchiveCount,
    blockers,
    warnings,
    activeImportantHits,
    explicitUnmappedRisks: warnings,
    classificationPolicy: {
      activeRuntime: 'Only activeRuntime files can own live visual surfaces.',
      docsOnly: 'Documentation can explain visuals but cannot certify runtime ownership.',
      fixtureOnly: 'Fixtures are evidence only.',
      generatedEvidenceOnly: 'Generated reports/evidence are not runtime owners.',
      inactiveArchive: 'Archive/backups are excluded from ownership.'
    }
  };
}

function surfaceEntries(state, routes, regions, slots) {
  const runtimeCounts = state.runtimeCert?.countsBySurface || {};
  return surfaceDefinitions(state).map((surface) => {
    const surfaceRoutes = routes.filter((route) => route.surface === surface.id);
    const surfaceRegions = regions.filter((region) => region.surface === surface.id);
    const surfaceSlots = slots.filter((slot) => slot.surface === surface.id);
    return {
      surface: surface.id,
      app: surface.app || surface.label,
      root: surface.root,
      port: surface.port ?? null,
      routeCount: surfaceRoutes.length,
      panelCount: (surface.panels || []).length,
      visualRegionCount: surfaceRegions.length,
      editableSlotCount: surfaceSlots.length,
      owners: surface.owners || [],
      allowedScope: surface.allowedScope || [],
      runtimeCertification: runtimeCounts[surface.id] || null,
      status: surfaceRoutes.length || surface.id === 'shared-ui' ? 'CERTIFIED' : 'BLOCKED'
    };
  });
}

function buildReuseReport(state) {
  const reused = [
    { system: '.prisma-ui/registry.json', use: 'target apps, gates, global UI scope, hard states', status: exists(path.join(state.uiRoot, 'registry.json')) ? 'reused' : 'missing' },
    { system: '.prisma-ui/surfaces.json', use: 'surface roots, ports, owners, scope, runtime probe hints', status: exists(path.join(state.uiRoot, 'surfaces.json')) ? 'reused' : 'missing' },
    { system: '.prisma-ui/routes.json', use: '108 route contracts and runtime/source route ownership', status: exists(path.join(state.uiRoot, 'routes.json')) ? 'reused' : 'missing' },
    { system: '.prisma-ui/panels/*.json', use: 'panel owner contracts and safe panel scopes', status: state.panels.length ? 'reused' : 'missing' },
    { system: 'tools/quality/ui-certainty.mjs', use: 'delegating CLI and existing certification surface', status: 'extended' },
    { system: '.governance/current/AUTHORITY_READSET.lock.json', use: 'fresh authority mesh readset for this task', status: state.authorityLock ? 'reused' : 'missing' },
    { system: 'docs/visual-layer-map/layer-map.json', use: 'baseline layer-map evidence, not live owner truth by itself', status: state.layerMap ? 'reused' : 'missing' },
    { system: 'config/prisma-visual* and config/prisma-visual-os', use: 'token, recipe, layer-budget and visual recipe ownership', status: tokenOwners().length ? 'reused' : 'missing' }
  ];
  return {
    schema: 'prisma.ui.visual-control.reuse-report.v1',
    status: reused.some((item) => item.status === 'missing') ? 'WARN' : 'CERTIFIED',
    reusedSystems: reused,
    extendedSystems: ['tools/quality/ui-certainty.mjs', 'package.json', '.prisma-ui/registry.json'],
    leftUntouched: [
      'Active product UI visuals and CSS aesthetics',
      'Prisma schema, migrations, auth, sync and business logic',
      'Runtime servers and process state'
    ],
    newFilesNecessary: [
      'tools/quality/ui-visual-control.mjs',
      'docs/quality/PRISMA_VISUAL_CONTROL_SYSTEM_V1.md',
      '.prisma-ui/visual-control/*.json'
    ],
    authoritativePaths: [
      '.prisma-ui/visual-control/registry.json',
      '.prisma-ui/current/UI_VISUAL_CONTROL_REPORT.json',
      '.prisma-ui/current/UI_EDITABLE_SLOTS_REPORT.json'
    ],
    deprecatedPaths: []
  };
}

function buildModel(flags = {}) {
  const state = loadState(flags);
  const requestedSurface = flags.surface && flags.surface !== 'all' ? flags.surface : null;
  const allFiles = scanFiles().filter((file) => !requestedSurface || surfaceFromPath(file) === requestedSurface);
  const activeFiles = scanActiveFiles().filter((file) => !requestedSurface || surfaceFromPath(file) === requestedSurface);
  const routes = buildRoutes(state).filter((route) => {
    if (flags.surface && flags.surface !== 'all' && route.surface !== flags.surface) return false;
    if (flags.route && route.route !== flags.route) return false;
    return true;
  });
  const panels = state.panels.filter((panel) => {
    if (flags.surface && flags.surface !== 'all' && panel.surface !== flags.surface) return false;
    if (flags.route && panel.route !== flags.route) return false;
    return true;
  });
  const components = mergeDiscoveredComponents(buildComponentMap(state, routes, panels), allFiles);
  const layerPayload = buildLayers(allFiles);
  const regions = buildVisualRegions(routes, panels, layerPayload.layers, components);
  const slots = buildEditableSlots(regions, components);
  const owners = buildOwners(routes, regions, components, layerPayload.layers, layerPayload.assets);
  const risks = buildRisks(state, routes, regions, slots, layerPayload.layers, activeFiles, allFiles, requestedSurface);
  const surfaces = surfaceEntries(state, routes, regions, slots)
    .filter((surface) => !requestedSurface || surface.surface === requestedSurface);
  const reuseReport = buildReuseReport(state);
  const meta = gitMeta();
  const report = {
    schema: 'prisma.ui.visual-control.report.v1',
    createdAt: nowIso(),
    command: 'visual-control',
    cwd: appRoot,
    repoHead: meta.repoHead,
    branch: meta.branch,
    status: risks.status,
    surfaceCount: surfaces.length,
    targetSurfaceCount: requestedSurface ? 1 : targetSurfaceIds(state).length,
    routeCount: routes.length,
    visualRegionCount: regions.length,
    componentOwnerCount: owners.componentOwners.length,
    cssOwnerCount: owners.cssOwners.length,
    assetOwnerCount: owners.assetOwners.length,
    editableSlotCount: slots.length,
    layerCount: layerPayload.layers.length,
    activeCssFileCount: layerPayload.cssFiles.length,
    blockerCount: risks.blockerCount,
    warningCount: risks.warningCount,
    activeImportantCount: risks.activeImportantCount,
    ambiguousActiveLayerOwnerCount: risks.ambiguousActiveLayerOwnerCount,
    runtimeCertificationBaseline: state.runtimeCert ? {
      status: state.runtimeCert.status,
      routeCount: state.runtimeCert.routeCount,
      runtimeCertifiedCount: state.runtimeCert.runtimeCertifiedCount,
      sourceCertifiedCount: state.runtimeCert.sourceCertifiedCount,
      routeUnmappedCount: state.runtimeCert.routeUnmappedCount,
      runtimeBlockedCount: state.runtimeCert.runtimeBlockedCount,
      anchorMissingCount: state.runtimeCert.anchorMissingCount,
      selectorMissingCount: state.runtimeCert.selectorMissingCount
    } : null,
    authorityMesh: state.authorityLock ? {
      status: state.authorityLock.status,
      generatedAt: state.authorityLock.generated_at,
      authorityFileCount: state.authorityLock.authority_file_count,
      missingCount: Array.isArray(state.authorityLock.missing) ? state.authorityLock.missing.length : null
    } : null,
    surfaces,
    routes,
    visualRegions: regions,
    risks: risks.blockers,
    warnings: risks.warnings,
    reuseReport: reuseReport.authoritativePaths,
    futureUsageExamples: futureUsageExamples(slots, routes, layerPayload.layers)
  };
  return {
    state,
    requestedSurface,
    allFiles,
    activeFiles,
    surfaces,
    routes,
    components,
    regions,
    slots,
    owners,
    layers: layerPayload.layers,
    assets: layerPayload.assets,
    risks,
    reuseReport,
    report
  };
}

function futureUsageExamples(slots, routes, layers) {
  const tabletPayment = slots.find((slot) => slot.surface === 'tablet' && slot.target === 'tablet.pos.payment-overlay' && /height|minHeight|padding/.test(slot.knob));
  const pcBackgroundLayer = layers.find((layer) => layer.surface === 'pc' && (layer.visualRegion === 'background' || layer.visualRegion === 'atmospheric'));
  const mobileButton = slots.find((slot) => slot.surface === 'mobile' && slot.knob === 'button add/remove/move safety');
  return {
    tabletPaymentPanelTaller: tabletPayment ? {
      surface: tabletPayment.surface,
      route: tabletPayment.route,
      visualUnit: tabletPayment.target,
      ownerComponent: tabletPayment.ownerComponent,
      ownerCss: tabletPayment.ownerCss,
      editableSlot: tabletPayment.knob,
      risk: tabletPayment.safetyClassification,
      gates: tabletPayment.gates,
      excludedSurfaces: tabletPayment.excludedSurfaces
    } : null,
    pcDashboardBackground: pcBackgroundLayer ? {
      surface: 'pc',
      screen: routes.find((route) => route.surface === 'pc' && route.route === '/dashboard')?.route || '/dashboard',
      backgroundLayerOwner: pcBackgroundLayer.ownerCss,
      assetOwner: pcBackgroundLayer.assetOwners,
      layerLevel: pcBackgroundLayer.visualRegion,
      risk: pcBackgroundLayer.safetyClassification,
      gates: ['node tools/quality/ui-certainty.mjs certify --surface pc --strict', 'node tools/quality/ui-certainty.mjs visual-control:layers --strict']
    } : null,
    mobileRemoveButton: mobileButton ? {
      surface: mobileButton.surface,
      ownerComponent: mobileButton.ownerComponent,
      ownerCss: mobileButton.ownerCss,
      safety: mobileButton.safetyClassification,
      removalGuidance: mobileButton.buttonRemovalSafety,
      gates: mobileButton.gates
    } : null
  };
}

function compactModelForRepo(model) {
  const ownerCssProfiles = createProfileStore('ownerCss');
  const assetOwnerProfiles = createProfileStore('assetOwner');
  const tokenOwnerProfiles = createProfileStore('tokenOwner');
  const gateProfiles = createProfileStore('gate');
  const rollbackProfiles = createProfileStore('rollback');
  const excludedSurfaceProfiles = createProfileStore('excludedSurface');
  const routeProfiles = createProfileStore('route');
  const panelProfiles = createProfileStore('panel');
  const componentProfiles = createProfileStore('component');

  const compactRegion = (region) => omitEmpty({
    region_id: region.region_id,
    surface: region.surface,
    route: region.route,
    human_id: region.human_id,
    visualRegion: region.visualRegion,
    ownerComponent: region.ownerComponent,
    ownerCssProfile: ownerCssProfiles.ref(region.ownerCss),
    assetOwnerProfile: assetOwnerProfiles.ref(region.assetOwner ? [region.assetOwner] : []),
    tokenOwnerProfile: tokenOwnerProfiles.ref(region.tokenOwner),
    safetyClassification: region.safetyClassification,
    excludedSurfacesProfile: excludedSurfaceProfiles.ref(region.excludedSurfaces)
  });

  const visualRegions = model.regions.map(compactRegion);
  const slotsByUnit = new Map();
  const knobKeysByUnit = new Map();
  for (const slot of model.slots) {
    const key = [
      slot.surface,
      slot.route || '',
      slot.target,
      slot.visualRegion,
      slot.ownerComponent || '',
      JSON.stringify(sortUniq(slot.ownerCss)),
      JSON.stringify(sortUniq(slot.assetOwner)),
      JSON.stringify(sortUniq(slot.tokenOwner))
    ].join('|');
    if (!slotsByUnit.has(key)) {
      const unit = omitEmpty({
        slot_unit_id: compactId(`${slot.surface}.${slot.route || 'any'}.${slot.target}`),
        surface: slot.surface,
        route: slot.route,
        target: slot.target,
        human_id: slot.human_id,
        visualRegion: slot.visualRegion,
        ownerComponent: slot.ownerComponent,
        ownerCssProfile: ownerCssProfiles.ref(slot.ownerCss),
        assetOwnerProfile: assetOwnerProfiles.ref(slot.assetOwner),
        tokenOwnerProfile: tokenOwnerProfiles.ref(slot.tokenOwner),
        gatesProfile: gateProfiles.ref(slot.gates),
        rollbackScopeProfile: rollbackProfiles.ref(slot.rollbackScope),
        excludedSurfacesProfile: excludedSurfaceProfiles.ref(slot.excludedSurfaces),
        allowedChangeShape: slot.allowedChangeShape
      });
      unit.knobs = [];
      slotsByUnit.set(key, unit);
      knobKeysByUnit.set(key, new Set());
    }
    const unit = slotsByUnit.get(key);
    const knobKey = JSON.stringify([
      slot.knob,
      slot.safetyClassification,
      slot.buttonRemovalSafety || null,
      Object.keys(slot.functionalSignals || {}).filter((name) => Boolean(slot.functionalSignals[name])).sort()
    ]);
    if (knobKeysByUnit.get(key).has(knobKey)) continue;
    knobKeysByUnit.get(key).add(knobKey);
    unit.knobs.push(omitEmpty({
      knob: slot.knob,
      safetyClassification: slot.safetyClassification,
      buttonRemovalSafety: slot.buttonRemovalSafety,
      functionalSignals: Object.keys(slot.functionalSignals || {}).filter((name) => Boolean(slot.functionalSignals[name])).sort()
    }));
  }

  const compactLayer = (layer) => omitEmpty({
    layer_id: layer.layer_id,
    surface: layer.surface,
    file: layer.file,
    selector: layer.selector,
    visualRegion: layer.visualRegion,
    layer: layer.layer,
    ownerCss: layer.ownerCss,
    ownerComponent: layer.ownerComponent,
    evidenceClass: layer.evidenceClass,
    safetyClassification: layer.safetyClassification,
    background: layer.background,
    position: layer.position,
    zIndex: layer.zIndex,
    isolation: layer.isolation,
    overflow: layer.overflow,
    opacity: layer.opacity,
    backdropFilter: layer.backdropFilter,
    height: layer.height,
    width: layer.width,
    spacing: layer.spacing,
    radius: layer.radius,
    shadow: layer.shadow,
    assetOwnersProfile: assetOwnerProfiles.ref(layer.assetOwners),
    risks: layer.risks
  });

  const compactComponentOwner = (owner) => omitEmpty({
    component_id: owner.component_id,
    path: owner.path,
    fileClass: owner.fileClass,
    surface: owner.surface,
    routesProfile: routeProfiles.ref(owner.routes),
    panelsProfile: panelProfiles.ref(owner.panels),
    cssOwnersProfile: ownerCssProfiles.ref(owner.cssOwners),
    safetyClassification: owner.safetyClassification,
    riskClass: owner.riskClass
  });

  const compactCssOwner = (owner) => omitEmpty({
    owner_id: owner.owner_id,
    file: owner.file,
    surface: owner.surface,
    routesProfile: routeProfiles.ref(owner.routes),
    panelsProfile: panelProfiles.ref(owner.panels),
    componentsProfile: componentProfiles.ref(owner.components),
    safetyClassification: owner.safetyClassification
  });

  const compactRouteOwner = (owner) => omitEmpty({
    route_id: owner.route_id,
    surface: owner.surface,
    route: owner.route,
    ownerComponent: owner.ownerComponent,
    ownerCssProfile: ownerCssProfiles.ref(owner.ownerCss),
    certificationStatus: owner.certificationStatus
  });

  const compactRegionOwner = (owner) => omitEmpty({
    region_id: owner.region_id,
    surface: owner.surface,
    route: owner.route,
    ownerComponent: owner.ownerComponent,
    ownerCssProfile: ownerCssProfiles.ref(owner.ownerCss),
    assetOwnerProfile: assetOwnerProfiles.ref(owner.assetOwner ? [owner.assetOwner] : []),
    tokenOwnerProfile: tokenOwnerProfiles.ref(owner.tokenOwner),
    safetyClassification: owner.safetyClassification
  });

  const profiles = {
    ownerCss: ownerCssProfiles.profiles,
    assetOwner: assetOwnerProfiles.profiles,
    tokenOwner: tokenOwnerProfiles.profiles,
    gates: gateProfiles.profiles,
    rollbackScope: rollbackProfiles.profiles,
    excludedSurfaces: excludedSurfaceProfiles.profiles,
    routes: routeProfiles.profiles,
    panels: panelProfiles.profiles,
    components: componentProfiles.profiles
  };

  return {
    detailPolicy: 'repo contains compact indexes; full expanded detail belongs in external evidence/result.zip when needed',
    profiles,
    visualRegions,
    slotUnits: Array.from(slotsByUnit.values()).sort((a, b) => a.slot_unit_id.localeCompare(b.slot_unit_id)),
    layers: model.layers.map(compactLayer),
    owners: {
      componentOwners: model.owners.componentOwners.map(compactComponentOwner),
      cssOwners: model.owners.cssOwners.map(compactCssOwner),
      assetOwners: model.owners.assetOwners,
      tokenThemeOwners: model.owners.tokenThemeOwners,
      routeOwners: model.owners.routeOwners.map(compactRouteOwner),
      regionOwners: model.owners.regionOwners.map(compactRegionOwner)
    }
  };
}

function countBy(items, keyOrFn) {
  const getKey = typeof keyOrFn === 'function' ? keyOrFn : (item) => item?.[keyOrFn];
  const counts = {};
  for (const item of Array.isArray(items) ? items : []) {
    const raw = getKey(item) || 'unknown';
    const key = String(raw);
    counts[key] = (counts[key] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort((a, b) => a[0].localeCompare(b[0])));
}

function sampleItems(items, limit = 80) {
  return (Array.isArray(items) ? items : []).slice(0, limit);
}

function summarizeProfiles(profiles, groupLimit = 16, valueLimit = 10) {
  const out = {};
  for (const [group, entries] of Object.entries(profiles || {})) {
    const keys = Object.keys(entries || {}).sort();
    out[group] = {
      profileCount: keys.length,
      samples: keys.slice(0, groupLimit).map((key) => ({
        id: key,
        values: sampleItems(entries[key], valueLimit)
      }))
    };
  }
  return out;
}

function compactIndexPolicy(kind, expandedCount) {
  return {
    kind,
    policy: 'repo keeps counts, grouped indexes and bounded samples; expanded detail belongs in external evidence/result.zip when a run needs forensic payload',
    expandedCount
  };
}

function writeArtifacts(model) {
  const root = model.state.visualRoot;
  const compact = compactModelForRepo(model);
  writeJson(path.join(root, 'registry.json'), {
    schema: 'prisma.ui.visual-control.registry.v1',
    createdAt: nowIso(),
    status: model.risks.status,
    detailPolicy: compact.detailPolicy,
    targetSurfaces: model.requestedSurface ? [model.requestedSurface] : targetSurfaceIds(model.state),
    authoritativeInputs: [
      '.prisma-ui/registry.json',
      '.prisma-ui/surfaces.json',
      '.prisma-ui/routes.json',
      '.prisma-ui/panels/*.json',
      '.governance/current/AUTHORITY_READSET.lock.json',
      'docs/visual-layer-map/layer-map.json'
    ],
    outputs: [
      '.prisma-ui/visual-control/surfaces.json',
      '.prisma-ui/visual-control/routes.json',
      '.prisma-ui/visual-control/components.json',
      '.prisma-ui/visual-control/editable-slots.json',
      '.prisma-ui/visual-control/owners.json',
      '.prisma-ui/visual-control/layers.json',
      '.prisma-ui/visual-control/risks.json',
      '.prisma-ui/current/UI_VISUAL_CONTROL_REPORT.json',
      '.prisma-ui/current/UI_EDITABLE_SLOTS_REPORT.json'
    ],
    gates: [
      'ui:visual-control:inventory',
      'ui:visual-control:owners',
      'ui:visual-control:slots',
      'ui:visual-control:layers',
      'ui:visual-control:report',
      'ui:visual-control:certify'
    ],
    nonGoals: [
      'No visual redesign',
      'No CSS hotfix',
      'No route, auth, Prisma, DB, sync or POS behavior change'
    ]
  });
  writeJson(path.join(root, 'surfaces.json'), { schema: 'prisma.ui.visual-control.surfaces.v1', status: model.risks.status, surfaces: model.surfaces });
  writeJson(path.join(root, 'routes.json'), { schema: 'prisma.ui.visual-control.routes.v1', status: model.risks.status, routeCount: model.routes.length, routes: model.routes });
  writeJson(path.join(root, 'components.json'), { schema: 'prisma.ui.visual-control.components.v1', status: model.risks.status, componentCount: model.components.length, components: model.components });
  writeJson(path.join(root, 'editable-slots.json'), {
    schema: 'prisma.ui.visual-control.editable-slots.v1',
    status: model.risks.status,
    detailPolicy: compact.detailPolicy,
    compactIndex: compactIndexPolicy('editable-slots', model.slots.length),
    editableSlotCount: model.slots.length,
    slotUnitCount: compact.slotUnits.length,
    countsBySurface: countBy(compact.slotUnits, 'surface'),
    countsBySafetyClassification: countBy(model.slots, 'safetyClassification'),
    countsByRegion: countBy(compact.slotUnits, 'visualRegion'),
    profileSummary: summarizeProfiles(compact.profiles),
    slotUnitSamples: sampleItems(compact.slotUnits, 180)
  });
  writeJson(path.join(root, 'owners.json'), {
    schema: 'prisma.ui.visual-control.owners.v1',
    status: model.risks.status,
    detailPolicy: compact.detailPolicy,
    compactIndex: compactIndexPolicy('owners', model.owners.componentOwners.length + model.owners.cssOwners.length + model.owners.regionOwners.length),
    componentOwnerCount: compact.owners.componentOwners.length,
    cssOwnerCount: compact.owners.cssOwners.length,
    assetOwnerCount: compact.owners.assetOwners.length,
    tokenThemeOwnerCount: compact.owners.tokenThemeOwners.length,
    routeOwnerCount: compact.owners.routeOwners.length,
    regionOwnerCount: compact.owners.regionOwners.length,
    countsBySurface: countBy(compact.owners.regionOwners, 'surface'),
    countsBySafetyClassification: countBy(compact.owners.regionOwners, 'safetyClassification'),
    profileSummary: summarizeProfiles(compact.profiles),
    componentOwnerSamples: sampleItems(compact.owners.componentOwners, 100),
    cssOwnerSamples: sampleItems(compact.owners.cssOwners, 100),
    assetOwnerSamples: sampleItems(compact.owners.assetOwners, 80),
    tokenThemeOwnerSamples: sampleItems(compact.owners.tokenThemeOwners, 80),
    routeOwnerSamples: sampleItems(compact.owners.routeOwners, 100),
    regionOwnerSamples: sampleItems(compact.owners.regionOwners, 140)
  });
  writeJson(path.join(root, 'layers.json'), {
    schema: 'prisma.ui.visual-control.layers.v1',
    status: model.risks.status,
    detailPolicy: compact.detailPolicy,
    compactIndex: compactIndexPolicy('layers', model.layers.length),
    layerCount: model.layers.length,
    assetCount: model.assets.length,
    countsBySurface: countBy(compact.layers, 'surface'),
    countsByLayer: countBy(compact.layers, 'layer'),
    countsByVisualRegion: countBy(compact.layers, 'visualRegion'),
    countsByEvidenceClass: countBy(compact.layers, 'evidenceClass'),
    countsBySafetyClassification: countBy(compact.layers, 'safetyClassification'),
    layerSamples: sampleItems(compact.layers, 220),
    assetSamples: sampleItems(model.assets, 120)
  });
  writeJson(path.join(root, 'risks.json'), { schema: 'prisma.ui.visual-control.risks.v1', ...model.risks });
  writeJson(path.join(root, 'reuse-report.json'), model.reuseReport);

  const {
    surfaces: _surfaces,
    routes: _routes,
    visualRegions: _visualRegions,
    ...reportSummary
  } = model.report;
  const indexFiles = {
    surfaces: '.prisma-ui/visual-control/surfaces.json',
    routes: '.prisma-ui/visual-control/routes.json',
    components: '.prisma-ui/visual-control/components.json',
    editableSlots: '.prisma-ui/visual-control/editable-slots.json',
    owners: '.prisma-ui/visual-control/owners.json',
    layers: '.prisma-ui/visual-control/layers.json'
  };
  writeCurrentReport(model, 'UI_VISUAL_CONTROL_REPORT', {
    ...reportSummary,
    detailPolicy: compact.detailPolicy,
    indexFiles,
    routeSamples: model.routes.slice(0, 40),
    visualRegionSamples: compact.visualRegions.slice(0, 80)
  }, visualControlMarkdown(model));
  writeCurrentReport(model, 'UI_EDITABLE_SLOTS_REPORT', {
    schema: 'prisma.ui.visual-control.editable-slots.report.v1',
    createdAt: nowIso(),
    status: model.risks.status,
    detailPolicy: compact.detailPolicy,
    indexFile: '.prisma-ui/visual-control/editable-slots.json',
    editableSlotCount: model.slots.length,
    slotUnitCount: compact.slotUnits.length,
    safeVisualOnlyCount: model.slots.filter((slot) => slot.safetyClassification === 'safeVisualOnly').length,
    visualWithFunctionalRiskCount: model.slots.filter((slot) => slot.safetyClassification === 'visualWithFunctionalRisk').length,
    functionalControlCount: model.slots.filter((slot) => slot.safetyClassification === 'functionalControl').length,
    sharedGlobalRiskCount: model.slots.filter((slot) => slot.safetyClassification === 'sharedGlobalRisk').length,
    slotUnitSamples: compact.slotUnits.slice(0, 120)
  }, editableSlotsMarkdown(model));
  writeCurrentReport(model, 'UI_VISUAL_CONTROL_LAYERS_REPORT', {
    schema: 'prisma.ui.visual-control.layers.report.v1',
    createdAt: nowIso(),
    status: model.risks.status,
    detailPolicy: compact.detailPolicy,
    indexFile: '.prisma-ui/visual-control/layers.json',
    layerCount: model.layers.length,
    activeCssFileCount: model.report.activeCssFileCount,
    assetCount: model.assets.length,
    layerSamples: compact.layers.slice(0, 160),
    assetSamples: model.assets.slice(0, 80)
  }, layerMarkdown(model));
  writeCurrentReport(model, 'UI_VISUAL_CONTROL_OWNERS_REPORT', {
    schema: 'prisma.ui.visual-control.owners.report.v1',
    createdAt: nowIso(),
    status: model.risks.status,
    detailPolicy: compact.detailPolicy,
    indexFile: '.prisma-ui/visual-control/owners.json',
    componentOwnerCount: model.owners.componentOwners.length,
    cssOwnerCount: model.owners.cssOwners.length,
    assetOwnerCount: model.owners.assetOwners.length,
    tokenThemeOwnerCount: model.owners.tokenThemeOwners.length,
    routeOwnerCount: model.owners.routeOwners.length,
    regionOwnerCount: model.owners.regionOwners.length,
    componentOwnerSamples: compact.owners.componentOwners.slice(0, 120),
    cssOwnerSamples: compact.owners.cssOwners.slice(0, 120)
  }, ownersMarkdown(model));
  writeCurrentReport(model, 'UI_VISUAL_CONTROL_REUSE_REPORT', model.reuseReport, reuseMarkdown(model));
  writeCurrentReport(model, 'UI_VISUAL_CONTROL_CERT_REPORT', {
    schema: 'prisma.ui.visual-control.cert.report.v1',
    createdAt: nowIso(),
    status: model.risks.status,
    blockerCount: model.risks.blockerCount,
    warningCount: model.risks.warningCount,
    blockers: model.risks.blockers,
    warnings: model.risks.warnings,
    exitCodeExpectation: model.risks.status === 'CERTIFIED' ? 0 : 1
  }, certifyMarkdown(model));
}

function writeCurrentReport(model, name, payload, markdownLines) {
  writeJson(path.join(model.state.currentRoot, `${name}.json`), payload);
  writeText(path.join(model.state.currentRoot, `${name}.md`), markdownLines.join('\n') + '\n');
}

function visualControlMarkdown(model) {
  return [
    '# UI VISUAL CONTROL REPORT',
    '',
    `- status: \`${model.risks.status}\``,
    `- surfaces: \`${model.report.surfaceCount}\``,
    `- routes: \`${model.report.routeCount}\``,
    `- visual regions: \`${model.report.visualRegionCount}\``,
    `- editable slots: \`${model.report.editableSlotCount}\``,
    `- layers: \`${model.report.layerCount}\``,
    `- blockers: \`${model.risks.blockerCount}\``,
    `- warnings: \`${model.risks.warningCount}\``,
    '',
    '## Runtime Baseline',
    '',
    `- status: \`${model.report.runtimeCertificationBaseline?.status || 'n/a'}\``,
    `- routeCount: \`${model.report.runtimeCertificationBaseline?.routeCount ?? 'n/a'}\``,
    `- runtimeCertifiedCount: \`${model.report.runtimeCertificationBaseline?.runtimeCertifiedCount ?? 'n/a'}\``,
    `- sourceCertifiedCount: \`${model.report.runtimeCertificationBaseline?.sourceCertifiedCount ?? 'n/a'}\``,
    '',
    '## Example Queries',
    '',
    '- Tablet payment panel: see `futureUsageExamples.tabletPaymentPanelTaller` in JSON.',
    '- PC dashboard background: see `futureUsageExamples.pcDashboardBackground` in JSON.',
    '- Mobile remove button: see `futureUsageExamples.mobileRemoveButton` in JSON.',
    '',
    '## Blockers',
    '',
    ...(model.risks.blockers.length ? model.risks.blockers.map((item) => `- ${item.category}: ${item.reason}`) : ['- none'])
  ];
}

function editableSlotsMarkdown(model) {
  const byClass = {};
  for (const slot of model.slots) byClass[slot.safetyClassification] = (byClass[slot.safetyClassification] || 0) + 1;
  return [
    '# UI EDITABLE SLOTS REPORT',
    '',
    `- status: \`${model.risks.status}\``,
    `- slot count: \`${model.slots.length}\``,
    `- safeVisualOnly: \`${byClass.safeVisualOnly || 0}\``,
    `- visualWithFunctionalRisk: \`${byClass.visualWithFunctionalRisk || 0}\``,
    `- functionalControl: \`${byClass.functionalControl || 0}\``,
    `- sharedGlobalRisk: \`${byClass.sharedGlobalRisk || 0}\``,
    '',
    '## Sample Slots',
    '',
    ...model.slots.slice(0, 80).map((slot) => `- ${slot.safetyClassification} - ${slot.surface} ${slot.route || ''} - ${slot.target} - ${slot.knob}`)
  ];
}

function layerMarkdown(model) {
  return [
    '# UI VISUAL CONTROL LAYERS REPORT',
    '',
    `- status: \`${model.risks.status}\``,
    `- active CSS files: \`${model.report.activeCssFileCount}\``,
    `- layer count: \`${model.layers.length}\``,
    `- asset count: \`${model.assets.length}\``,
    '',
    '## Layer Samples',
    '',
    ...model.layers.slice(0, 120).map((layer) => `- ${layer.safetyClassification} - ${layer.surface} - ${layer.visualRegion} - ${layer.file} - ${layer.selector || 'asset'}`)
  ];
}

function ownersMarkdown(model) {
  return [
    '# UI VISUAL CONTROL OWNERS REPORT',
    '',
    `- status: \`${model.risks.status}\``,
    `- component owners: \`${model.owners.componentOwners.length}\``,
    `- css owners: \`${model.owners.cssOwners.length}\``,
    `- asset owners: \`${model.owners.assetOwners.length}\``,
    `- token/theme owners: \`${model.owners.tokenThemeOwners.length}\``,
    '',
    '## Component Owners',
    '',
    ...model.owners.componentOwners.slice(0, 120).map((owner) => `- ${owner.riskClass} - ${owner.surface} - ${owner.path}`)
  ];
}

function reuseMarkdown(model) {
  return [
    '# UI VISUAL CONTROL REUSE REPORT',
    '',
    `- status: \`${model.reuseReport.status}\``,
    '',
    '## Reused Systems',
    '',
    ...model.reuseReport.reusedSystems.map((item) => `- ${item.status} - ${item.system}: ${item.use}`),
    '',
    '## Extended Systems',
    '',
    ...model.reuseReport.extendedSystems.map((item) => `- ${item}`),
    '',
    '## Left Untouched',
    '',
    ...model.reuseReport.leftUntouched.map((item) => `- ${item}`),
    '',
    '## Authoritative Paths',
    '',
    ...model.reuseReport.authoritativePaths.map((item) => `- ${item}`)
  ];
}

function certifyMarkdown(model) {
  return [
    '# UI VISUAL CONTROL CERT REPORT',
    '',
    `- status: \`${model.risks.status}\``,
    `- blockers: \`${model.risks.blockerCount}\``,
    `- warnings: \`${model.risks.warningCount}\``,
    `- active important hits: \`${model.risks.activeImportantCount}\``,
    `- ambiguous active layer owners: \`${model.risks.ambiguousActiveLayerOwnerCount}\``,
    '',
    '## Required Zero Categories',
    '',
    `- route owner missing: \`${model.risks.routeOwnerMissingCount}\``,
    `- region owner missing: \`${model.risks.regionOwnerMissingCount}\``,
    `- slot unclassified: \`${model.risks.slotUnclassifiedCount}\``,
    `- active important hits: \`${model.risks.activeImportantCount}\``,
    `- ambiguous active layer owners: \`${model.risks.ambiguousActiveLayerOwnerCount}\``,
    '',
    '## Blockers',
    '',
    ...(model.risks.blockers.length ? model.risks.blockers.map((item) => `- ${item.category}: ${item.reason}`) : ['- none'])
  ];
}

function compactResult(command, model) {
  return {
    schema: 'prisma.ui.visual-control.command.result.v1',
    command,
    status: model.risks.status,
    surfaceCount: model.report.surfaceCount,
    routeCount: model.report.routeCount,
    visualRegionCount: model.report.visualRegionCount,
    editableSlotCount: model.report.editableSlotCount,
    componentOwnerCount: model.report.componentOwnerCount,
    cssOwnerCount: model.report.cssOwnerCount,
    layerCount: model.report.layerCount,
    blockerCount: model.risks.blockerCount,
    warningCount: model.risks.warningCount,
    activeImportantCount: model.risks.activeImportantCount,
    ambiguousActiveLayerOwnerCount: model.risks.ambiguousActiveLayerOwnerCount,
    outputDir: relApp(model.state.visualRoot),
    report: '.prisma-ui/current/UI_VISUAL_CONTROL_REPORT.json',
    slotsReport: '.prisma-ui/current/UI_EDITABLE_SLOTS_REPORT.json'
  };
}

function runSelfTest() {
  const state = loadState();
  const problems = [];
  if (!state.registry?.schema) problems.push('missing .prisma-ui/registry.json');
  if (!surfaceDefinitions(state).length) problems.push('missing surfaces');
  if (!routeContracts(state).length) problems.push('missing routes');
  if (!state.panels.length) problems.push('missing panel contracts');
  if (!state.authorityLock) problems.push('missing fresh authority mesh lock');
  const status = problems.length ? 'BLOCKED' : 'CERTIFIED';
  return {
    schema: 'prisma.ui.visual-control.self-test.v1',
    status,
    problems,
    exitCodeExpectation: status === 'CERTIFIED' ? 0 : 1
  };
}

async function runVisualControlCommand(command, flags = {}) {
  const shortCommand = String(command || '').replace(/^visual-control:/, '') || 'report';
  if (shortCommand === 'self-test') {
    const self = runSelfTest();
    return self;
  }
  const model = buildModel(flags);
  writeArtifacts(model);
  return compactResult(`visual-control:${shortCommand}`, model);
}

function printResult(result) {
  console.log(JSON.stringify(result, null, 2));
}

export { VISUAL_CONTROL_COMMANDS, runVisualControlCommand };

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const { cmd, flags } = parseArgs();
  const result = await runVisualControlCommand(cmd, flags);
  printResult(result);
  if ((flags.strict || cmd === 'certify' || cmd === 'visual-control:certify') && result.status !== 'CERTIFIED') process.exit(1);
}
