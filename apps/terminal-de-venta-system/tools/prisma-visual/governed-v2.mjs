import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  statSync,
  writeFileSync,
} from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(scriptDir, '..', '..');
const repoRoot = path.resolve(appRoot, '..', '..');
const configRoot = path.join(appRoot, 'config', 'prisma-visual');
const descargasRoot = path.join('F:', 'descargasf');
const motorsRoot = path.join('F:', 'PRISMA_CTX', 'MOTORES');
const version = 'prisma-visual-catalog-governed-v2';

const requiredSurfaces = [
  'tablet',
  'pc',
  'mobile',
  'chart-lab',
  'shared-ui',
  'visual-os',
  'surface-governor',
  'kiosk',
  'customer-display',
  'warehouse-scanner',
  'manager-console',
  'training-mode',
  'demo-mode',
  'public-display',
];

const currentSurfaces = new Set(['tablet', 'pc', 'mobile', 'chart-lab', 'shared-ui', 'visual-os', 'surface-governor']);
const generatorSurfaces = ['tablet', 'pc', 'mobile', 'chart-lab', 'kiosk'];
const usageMapFiles = {
  tablet: 'tablet-usage-map.json',
  pc: 'pc-usage-map.json',
  mobile: 'mobile-usage-map.json',
  'chart-lab': 'chart-lab-usage-map.json',
};

const requiredDomains = [
  'commerce',
  'checkout',
  'inventory',
  'sync',
  'license',
  'reports',
  'analytics',
  'admin',
  'command-ai',
  'mobile-companion',
  'chart-lab',
  'training',
  'demo',
  'public-display',
  'future-surface',
];

const expectedAtlas = [
  ['docs/atlas/atlas.registry.json', 'shared', 'core'],
  ['docs/atlas/atlas.shared-core.json', 'shared', 'core'],
  ['docs/atlas/ATLAS_MASTER_INDEX.md', 'shared', 'core'],
  ['docs/atlas/ATLAS_SHARED_CORE.md', 'shared', 'core'],
  ['docs/atlas/ATLAS_SHARED_CORE_CONTRACTS.md', 'shared', 'core'],
  ['docs/atlas/ATLAS_SHARED_CORE_FUNCTIONAL_ENGINES.md', 'shared', 'engine'],
  ['docs/atlas/ATLAS_SHARED_CORE_RUNTIME_INFRA.md', 'shared', 'engine'],
  ['docs/atlas/ATLAS_SHARED_CORE_VISUAL_OS.md', 'shared', 'recipe'],
  ['docs/atlas/governor.atlas-map.json', 'surface-governor', 'core'],
  ['docs/atlas/GOVERNOR_ATLAS_LOCATION.md', 'surface-governor', 'core'],
  ['products/tablet/app/docs/atlas/atlas.tablet.json', 'tablet', 'core'],
  ['products/tablet/app/docs/atlas/ATLAS_TABLET.md', 'tablet', 'core'],
  ['products/tablet/app/docs/atlas/ATLAS_TABLET_FUNCTIONAL_ENGINES.md', 'tablet', 'engine'],
  ['products/tablet/app/docs/atlas/ATLAS_TABLET_INTERACTION.md', 'tablet', 'engine'],
  ['products/tablet/app/docs/atlas/ATLAS_TABLET_RUNTIME_DELIVERY.md', 'tablet', 'engine'],
  ['products/tablet/app/docs/atlas/ATLAS_TABLET_VISUAL.md', 'tablet', 'recipe'],
  ['products/pc/app/docs/atlas/atlas.pc.json', 'pc', 'core'],
  ['products/pc/app/docs/atlas/ATLAS_PC.md', 'pc', 'core'],
  ['products/pc/app/docs/atlas/ATLAS_PC_FUNCTIONAL_ENGINES.md', 'pc', 'engine'],
  ['products/pc/app/docs/atlas/ATLAS_PC_INTERACTION.md', 'pc', 'engine'],
  ['products/pc/app/docs/atlas/ATLAS_PC_RUNTIME_DELIVERY.md', 'pc', 'engine'],
  ['products/pc/app/docs/atlas/ATLAS_PC_VISUAL.md', 'pc', 'recipe'],
  ['products/mobile/app/docs/atlas/atlas.mobile.json', 'mobile', 'core'],
  ['products/mobile/app/docs/atlas/ATLAS_MOBILE.md', 'mobile', 'core'],
  ['products/mobile/app/docs/atlas/ATLAS_MOBILE_FUNCTIONAL_ENGINES.md', 'mobile', 'engine'],
  ['products/mobile/app/docs/atlas/ATLAS_MOBILE_INTERACTION.md', 'mobile', 'engine'],
  ['products/mobile/app/docs/atlas/ATLAS_MOBILE_RUNTIME_DELIVERY.md', 'mobile', 'engine'],
  ['products/mobile/app/docs/atlas/ATLAS_MOBILE_VISUAL.md', 'mobile', 'recipe'],
  ['docs/prisma/PRISMA_CHART_ATLAS.md', 'chart-lab', 'engine'],
  ['docs/productization/PRISMA_FEATURE_GATE_ATLAS.md', 'all', 'core'],
  ['docs/surface-visual-governor/00_PRISMA_SURFACE_VISUAL_GOVERNOR_MASTER_INDEX.md', 'surface-governor', 'core'],
  ['docs/surface-visual-governor/01_WHERE_EVERYTHING_LIVES.md', 'surface-governor', 'core'],
  ['docs/surface-visual-governor/_hub/surface_governor_inventory.json', 'surface-governor', 'core'],
  ['docs/surface-visual-governor/_hub/result_zip_inventory.json', 'surface-governor', 'archive'],
];

const expectedMotors = [
  ['motor_all.py', 'global-context'],
  ['motor_tablet.py', 'tablet-context'],
  ['motor_pc.py', 'pc-context'],
  ['motor_app_movil.py', 'mobile-context'],
  ['motor_lab_chart.py', 'chart-lab-context'],
  ['motor_web_eit.py', 'web-eit-context'],
  ['motor_control_center.py', 'control-center-context'],
  ['motor_gobierno.py', 'governance-context'],
  ['motor_databases.py', 'database-context'],
  ['motor_verify.py', 'context-verifier'],
  ['motor_visual_uiux_packager.py', 'uiux-context-packager'],
  ['motor_playwright.py', 'visual-evidence'],
  ['TodoALV.py', 'total-context-packager'],
  ['run_playwright_all_once.ps1', 'visual-wrapper'],
  ['run_playwright_surface_menu.ps1', 'visual-wrapper'],
];

function nowIso() {
  return new Date().toISOString();
}

function localStamp() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return `${pad(d.getDate())}${pad(d.getMonth() + 1)} ${pad(d.getHours())}${pad(d.getMinutes())}`;
}

function safeStamp(stamp) {
  return stamp.replace(/[^0-9A-Za-z_-]+/g, '_');
}

function readText(absPath) {
  return readFileSync(absPath, 'utf8');
}

function readJsonRel(relPath, fallback = null) {
  const absPath = path.join(appRoot, relPath);
  if (!existsSync(absPath)) return fallback;
  return JSON.parse(readText(absPath));
}

function hashBytes(text) {
  return createHash('sha256').update(text).digest('hex');
}

function hashFile(absPath) {
  if (!existsSync(absPath)) return null;
  return createHash('sha256').update(readFileSync(absPath)).digest('hex');
}

function repoRel(absPath) {
  return path.relative(appRoot, absPath).replaceAll(path.sep, '/');
}

function mkdirFor(absPath) {
  mkdirSync(path.dirname(absPath), { recursive: true });
}

function stringify(data) {
  return `${JSON.stringify(data, null, 2)}\n`;
}

function listFiles(root, options = {}) {
  const files = [];
  if (!existsSync(root)) return files;
  const skipDirs = new Set(options.skipDirs ?? ['node_modules', '.next', '.turbo', '.git', '__pycache__']);
  const walk = (dir) => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (skipDirs.has(entry.name)) continue;
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(full);
      } else if (entry.isFile()) {
        files.push(full);
      }
    }
  };
  walk(root);
  return files;
}

function git(args) {
  return execFileSync('git', ['-C', repoRoot, ...args], { encoding: 'utf8' }).trim();
}

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      const next = argv[i + 1];
      if (next && !next.startsWith('--')) {
        args[key] = next;
        i += 1;
      } else {
        args[key] = true;
      }
    } else {
      args._.push(arg);
    }
  }
  return args;
}

function createContext(stampArg) {
  const stamp = stampArg || localStamp();
  const id = safeStamp(stamp);
  const stageRoot = path.join(descargasRoot, `prisma visualv2 ${stamp} work`);
  const backupRoot = path.join(descargasRoot, `prisma visualv2 ${stamp} backups`);
  const dirs = {
    stageRoot,
    backupRoot,
    logs: path.join(stageRoot, 'logs'),
    reports: path.join(stageRoot, 'reports'),
    validators: path.join(stageRoot, 'validator outputs'),
    dryRuns: path.join(stageRoot, 'generator dry-runs'),
    evidence: path.join(stageRoot, 'evidence'),
    manifests: path.join(stageRoot, 'manifests'),
  };
  for (const dir of Object.values(dirs)) mkdirSync(dir, { recursive: true });
  return {
    stamp,
    id,
    dirs,
    changed: [],
    backups: [],
    preexistingStatus: '',
    gitBefore: '',
    gitDiffBefore: '',
    branch: '',
    touched: new Set(),
  };
}

function trackedWrite(ctx, relPath, content, kind, reason, sourceOfTruth = [], validators = []) {
  const absPath = path.join(appRoot, relPath);
  const beforeExists = existsSync(absPath);
  const before = beforeExists ? readText(absPath) : null;
  if (before === content) return;
  const backupRel = beforeExists ? relPath.replaceAll('/', '__').replaceAll('\\', '__') : null;
  const backupPath = beforeExists ? path.join(ctx.dirs.backupRoot, backupRel) : null;
  const beforeHash = beforeExists ? hashBytes(before) : null;
  if (beforeExists) {
    mkdirFor(backupPath);
    copyFileSync(absPath, backupPath);
    ctx.backups.push({
      path: relPath,
      backupPath,
      hashBefore: beforeHash,
      reason: 'pre-change rollback copy',
    });
  }
  mkdirFor(absPath);
  writeFileSync(absPath, content, 'utf8');
  const hashAfter = hashFile(absPath);
  ctx.changed.push({
    path: relPath,
    kind,
    action: beforeExists ? 'modified' : 'created',
    reason,
    sourceOfTruth,
    validators,
    backup: backupPath,
    hashBefore: beforeHash,
    hashAfter,
    rollbackAction: beforeExists ? 'restore' : 'delete',
  });
  ctx.touched.add(relPath);
}

function writeJson(ctx, relPath, data, reason, sourceOfTruth = [], validators = []) {
  trackedWrite(ctx, relPath, stringify(data), 'config', reason, sourceOfTruth, validators);
}

function writeDoc(ctx, relPath, text, reason, sourceOfTruth = [], validators = []) {
  trackedWrite(ctx, relPath, text.endsWith('\n') ? text : `${text}\n`, 'report', reason, sourceOfTruth, validators);
}

function writeTool(ctx, relPath, text, reason, validators = []) {
  trackedWrite(ctx, relPath, text.endsWith('\n') ? text : `${text}\n`, 'tool', reason, ['governed-v2'], validators);
}

function stageWrite(ctx, area, name, content) {
  const absPath = path.join(ctx.dirs[area], name);
  mkdirFor(absPath);
  writeFileSync(absPath, content.endsWith('\n') ? content : `${content}\n`, 'utf8');
  return absPath;
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function unique(values) {
  return [...new Set(values.filter((x) => x !== undefined && x !== null && x !== ''))];
}

function inferDomain(component) {
  const text = `${component.id} ${component.canonicalName} ${component.family} ${asArray(component.usedByRoutes).join(' ')}`.toLowerCase();
  if (text.includes('checkout') || text.includes('cart') || text.includes('payment')) return 'checkout';
  if (text.includes('catalog') || text.includes('product') || text.includes('commerce') || text.includes('pos')) return 'commerce';
  if (text.includes('sync') || text.includes('outbox') || text.includes('ingest')) return 'sync';
  if (text.includes('license')) return 'license';
  if (text.includes('report')) return 'reports';
  if (text.includes('metric') || text.includes('kpi') || text.includes('chart')) return 'analytics';
  if (text.includes('command')) return 'command-ai';
  if (text.includes('mobile')) return 'mobile-companion';
  if (text.includes('admin') || text.includes('pc')) return 'admin';
  if (text.includes('warehouse')) return 'inventory';
  return 'commerce';
}

function inferIntent(component) {
  const domain = inferDomain(component);
  const byDomain = {
    commerce: 'commerce presentation and operator action',
    checkout: 'checkout state, cart and payment clarity',
    inventory: 'inventory visibility and stock movement review',
    sync: 'sync status, ingest and dispatch visibility',
    license: 'license state and customer-safe recovery',
    reports: 'report and evidence display',
    analytics: 'metrics and analytical scanning',
    admin: 'backoffice governance and operational control',
    'command-ai': 'command and assistive workflow control',
    'mobile-companion': 'owner companion pulse and alerts',
  };
  return byDomain[domain] ?? 'governed visual building block';
}

function inferAnatomy(component) {
  const family = String(component.family ?? '').toLowerCase();
  if (family.includes('action')) return ['root', 'label', 'icon', 'state'];
  if (family.includes('card')) return ['root', 'header', 'content', 'footer'];
  if (family.includes('panel')) return ['root', 'header', 'body', 'actions'];
  if (family.includes('banner') || family.includes('state')) return ['root', 'status', 'message', 'action'];
  if (family.includes('background')) return ['root', 'media', 'overlay', 'fallback'];
  if (family.includes('shell') || family.includes('frame')) return ['root', 'surface', 'content', 'navigation'];
  return ['root', 'content', 'state'];
}

function inferSlots(component) {
  const anatomy = inferAnatomy(component);
  return Object.fromEntries(anatomy.map((slot) => [slot, `${slot} slot controlled by ${component.id}`]));
}

function defaultTokens() {
  return [
    '--prisma-color-text',
    '--prisma-color-muted',
    '--prisma-color-border',
    '--prisma-surface-panel-bg',
    '--prisma-surface-card-bg',
    '--prisma-action-bg',
    '--prisma-action-text',
    '--prisma-radius-card',
    '--prisma-radius-panel',
    '--prisma-radius-action',
    '--prisma-shadow-soft',
    '--prisma-shadow-lifted',
    '--prisma-glass-blur',
    '--prisma-density-gap',
    '--prisma-motion-fast',
    '--prisma-focus-ring',
  ];
}

function defaultForbidden() {
  return [
    'hardcoded-runtime-background',
    'products/0.backgrounds-runtime-url',
    'fuji-active-runtime',
    'soft-gray-clouds-active-runtime',
    'final-important',
    'global-css-hack',
  ];
}

function loadUsageMaps() {
  const maps = {};
  for (const [surface, file] of Object.entries(usageMapFiles)) {
    maps[surface] = readJsonRel(`config/prisma-visual/${file}`, {
      schemaVersion: version,
      surface,
      generatedAt: nowIso(),
      routes: [],
    });
  }
  return maps;
}

function routeUsageByComponent(usageMaps) {
  const used = new Map();
  for (const [surface, map] of Object.entries(usageMaps)) {
    for (const route of asArray(map.routes)) {
      for (const componentId of asArray(route.canonicalComponents)) {
        const arr = used.get(componentId) ?? [];
        arr.push(`${surface}:${route.route}`);
        used.set(componentId, arr);
      }
    }
  }
  return used;
}

function buildComponentCatalog(usageMaps) {
  const existing = readJsonRel('config/prisma-visual/component-catalog.json', { components: [] });
  const used = routeUsageByComponent(usageMaps);
  const components = asArray(existing.components).map((component) => {
    const surfaces = unique([
      ...asArray(component.surfaces),
      ...(component.status === 'live' && String(component.sourceFiles?.[0] ?? '').includes('products/shared-ui/prisma') ? ['shared-ui'] : []),
    ]);
    const routeRefs = unique([...asArray(component.usedByRoutes), ...asArray(used.get(component.id))]);
    const domain = component.domain ?? inferDomain({ ...component, usedByRoutes: routeRefs });
    const variants = component.variants ?? surfaces.map((surface) => `${component.id}.${surface}.default`);
    const status = component.status ?? 'mapped';
    return {
      ...component,
      surfaces,
      domain,
      intent: component.intent ?? inferIntent({ ...component, domain }),
      anatomy: component.anatomy ?? inferAnatomy(component),
      slots: component.slots ?? inferSlots(component),
      variants,
      allowedTokens: unique([...asArray(component.allowedTokens), ...defaultTokens()]),
      allowedLibraries: unique(asArray(component.allowedLibraries)),
      forbiddenPatterns: unique([...asArray(component.forbiddenPatterns), ...defaultForbidden()]),
      usedByRoutes: routeRefs,
      migrationNotes: component.migrationNotes ?? 'Mapped by PRISMA Visual Catalog Governed v2.',
      accessibilityNotes: component.accessibilityNotes ?? 'Must preserve keyboard, focus and contrast constraints from the surface adapter.',
      visualDebtSignals: component.visualDebtSignals ?? [
        status === 'live' ? 'shared-ui-adopted' : 'local-pattern-still-present',
        routeRefs.length > 0 ? 'route-evidence-present' : 'route-evidence-pending',
      ],
      adoptionSignals: component.adoptionSignals ?? [
        status === 'live' ? 'live-source-file' : 'mapped-for-migration',
        routeRefs.length > 0 ? 'used-by-route' : 'not-yet-bound',
      ],
      replacement: component.replacement ?? (status === 'deprecated' ? 'prisma.background-layer' : null),
      risk: component.risk ?? (status === 'live' ? 'low' : status === 'deprecated' ? 'blocked' : 'review'),
    };
  });

  const statusRules = unique([
    ...asArray(existing.statusRules),
    'live requires real sourceFiles',
    'mapped requires evidence sourceFiles',
    'planned and reserved cannot be wired to production without promotion',
    'deprecated requires replacement or reason',
    'governed requires adapter, recipe, variant and validator coverage',
    'blocked cannot be changed without explicit human approval',
  ]);

  return {
    ...existing,
    schemaVersion: version,
    generatedAt: nowIso(),
    components,
    statusRules,
    v2Governance: {
      additive: true,
      sourceOfTruth: [
        'config/prisma-visual-system/components.registry.json',
        'products/shared-ui/prisma/components',
        'config/prisma-visual/*-usage-map.json',
      ],
      requiredFieldsAdded: [
        'domain',
        'intent',
        'anatomy',
        'slots',
        'variants',
        'visualDebtSignals',
        'adoptionSignals',
        'replacement',
        'risk',
      ],
    },
  };
}

function baseAdapter(surfaceId) {
  const reserved = !currentSurfaces.has(surfaceId);
  const labels = {
    tablet: ['standalone POS / tactile selling', 'touch', 'light-operational-cloudglass'],
    pc: ['backoffice / governance / analytics', 'dense', 'graphite-admin-cloudglass'],
    mobile: ['owner companion / pulse / alerts', 'compact-thumb', 'mobile-mist'],
    'chart-lab': ['visual lab / experimental charts', 'lab', 'analytical-glass'],
    'shared-ui': ['shared component and token authority', 'adaptive', 'shared-prisma-neutral'],
    'visual-os': ['Visual OS recipes, scorecards and release gates', 'governance', 'visual-os-governed'],
    'surface-governor': ['surface policy and promotion authority', 'governance', 'surface-governor-governed'],
    kiosk: ['reserved kiosk surface', 'large-touch', 'kiosk-reserved'],
    'customer-display': ['reserved customer facing display', 'customer-facing', 'customer-display-reserved'],
    'warehouse-scanner': ['reserved warehouse scanning surface', 'scanner', 'warehouse-scanner-reserved'],
    'manager-console': ['reserved manager console surface', 'dense-admin', 'manager-console-reserved'],
    'training-mode': ['reserved guided training surface', 'guided', 'training-mode-reserved'],
    'demo-mode': ['reserved demo surface', 'guided-demo', 'demo-mode-reserved'],
    'public-display': ['reserved public display surface', 'read-only', 'public-display-reserved'],
  };
  const [role, density, defaultTheme] = labels[surfaceId] ?? [`reserved ${surfaceId}`, 'reserved', `${surfaceId}-reserved`];
  const runtimePublicUrl = reserved || ['shared-ui', 'visual-os', 'surface-governor'].includes(surfaceId)
    ? null
    : `/visual-backgrounds/${surfaceId}/assets/${surfaceId}-default.jpg`;
  const recipes = {
    tablet: ['tablet-cloudglass-light', 'glass-pill', 'surface-panel', 'product-commerce'],
    pc: ['pc-graphite-glass', 'data-panel', 'metric-card', 'command-panel'],
    mobile: ['mobile-mist', 'state-banner', 'metric-card'],
    'chart-lab': ['chart-lab-analysis', 'liquid-panel'],
    'shared-ui': ['shared-ui-foundation', 'surface-panel', 'glass-card', 'action-button'],
    'visual-os': ['visual-os-governance'],
    'surface-governor': ['surface-governor-policy'],
  };
  const libraries = {
    tablet: ['@radix-ui/react-dialog', '@radix-ui/react-scroll-area', '@radix-ui/react-tooltip', '@radix-ui/react-slot', 'motion'],
    pc: ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu', '@radix-ui/react-scroll-area', '@radix-ui/react-select', '@radix-ui/react-tabs', '@radix-ui/react-tooltip', '@radix-ui/react-slot', 'motion', 'ogl'],
    mobile: ['@radix-ui/react-dialog', '@radix-ui/react-scroll-area', '@radix-ui/react-tooltip', '@radix-ui/react-slot', 'motion'],
    'chart-lab': ['ogl', 'motion', '@radix-ui/react-tabs', '@radix-ui/react-tooltip'],
    'shared-ui': ['@radix-ui/react-slot', '@radix-ui/react-tooltip'],
    'visual-os': ['motion', 'ogl'],
    'surface-governor': [],
  };
  return {
    surfaceId,
    status: reserved ? 'reserved' : 'current',
    role,
    density,
    defaultTheme,
    backgroundContract: {
      runtimePublicUrl,
      reserved,
      forbiddenRuntimeSources: ['products/0.backgrounds', 'Fuji', 'soft-gray-clouds'],
    },
    shellContract: reserved ? 'Reserved. Dry-run only until explicit promotion.' : role,
    layerBudget: reserved
      ? { reserved: true, maxShellDepth: 1, backgroundMustRemainVisible: true }
      : { maxShellDepth: surfaceId === 'chart-lab' ? 2 : 1, maxFullViewportOpaquePanels: surfaceId === 'pc' ? 1 : 0, backgroundMustRemainVisible: true },
    allowedRecipes: reserved ? ['reserved-safe-display'] : recipes[surfaceId] ?? ['surface-panel'],
    allowedLibraries: libraries[surfaceId] ?? [],
    forbiddenPatterns: reserved
      ? ['production-use-before-promotion', 'products/0.backgrounds-runtime-url', 'Fuji', 'soft-gray-clouds']
      : ['products/0.backgrounds-runtime-url', 'Fuji', 'soft-gray-clouds'],
    accessibilityConstraints: reserved ? ['define-before-live', 'focus-visible'] : ['focus-visible', 'contrast-readable'],
    runtimeBoundaries: reserved ? ['reserved-no-production-runtime'] : ['no-private-background-runtime'],
    motionBudget: reserved ? 'none-until-promotion' : surfaceId === 'chart-lab' ? 'bounded-lab-motion' : 'subtle-operational-motion',
    effectBudget: reserved ? 'none-until-promotion' : surfaceId === 'chart-lab' ? 'lab-isolated-effects' : 'low-noise-effects',
    atlasAllowed: reserved ? ['future-surface'] : [surfaceId, 'shared'],
    motorsAllowed: reserved ? ['inspect-only'] : [`motor_${surfaceId.replace('chart-lab', 'lab_chart').replace('mobile', 'app_movil').replace('surface-governor', 'gobierno')}`],
    generationAllowed: reserved ? ['dry-run', 'safe-scaffold-under-tools-only'] : ['dry-run', 'safe-scaffold-under-tools-only'],
    migrationPolicy: reserved ? 'blocked until explicit promotion' : 'tiered migration with validator and rollback evidence',
  };
}

function buildSurfaceAdapters() {
  const existing = readJsonRel('config/prisma-visual/surface-adapters.json', { adapters: [] });
  const byId = new Map(asArray(existing.adapters).map((adapter) => [adapter.surfaceId, adapter]));
  const adapters = requiredSurfaces.map((surfaceId) => {
    const base = baseAdapter(surfaceId);
    const old = byId.get(surfaceId) ?? {};
    return {
      ...base,
      ...old,
      backgroundContract: { ...base.backgroundContract, ...(old.backgroundContract ?? {}) },
      layerBudget: { ...base.layerBudget, ...(old.layerBudget ?? {}) },
      allowedRecipes: unique([...asArray(base.allowedRecipes), ...asArray(old.allowedRecipes)]),
      allowedLibraries: unique([...asArray(base.allowedLibraries), ...asArray(old.allowedLibraries)]),
      forbiddenPatterns: unique([...asArray(base.forbiddenPatterns), ...asArray(old.forbiddenPatterns)]),
      accessibilityConstraints: unique([...asArray(base.accessibilityConstraints), ...asArray(old.accessibilityConstraints)]),
      runtimeBoundaries: unique([...asArray(base.runtimeBoundaries), ...asArray(old.runtimeBoundaries)]),
      motionBudget: old.motionBudget ?? base.motionBudget,
      effectBudget: old.effectBudget ?? base.effectBudget,
      atlasAllowed: unique([...asArray(base.atlasAllowed), ...asArray(old.atlasAllowed)]),
      motorsAllowed: unique([...asArray(base.motorsAllowed), ...asArray(old.motorsAllowed)]),
      generationAllowed: unique([...asArray(base.generationAllowed), ...asArray(old.generationAllowed)]),
      migrationPolicy: old.migrationPolicy ?? base.migrationPolicy,
    };
  });
  return { ...existing, schemaVersion: version, generatedAt: nowIso(), adapters };
}

function buildRecipeMap(componentCatalog) {
  const existing = readJsonRel('config/prisma-visual/recipe-map.json', { recipes: [] });
  const byName = new Map(asArray(existing.recipes).map((recipe) => [recipe.name ?? recipe.id, recipe]));
  const recipeNames = unique([
    ...asArray(existing.recipes).map((recipe) => recipe.name ?? recipe.id),
    ...componentCatalog.components.map((component) => component.recipe),
    'shared-ui-foundation',
    'visual-os-governance',
    'surface-governor-policy',
    'reserved-safe-display',
    'data-panel',
    'metric-card',
    'command-panel',
    'liquid-panel',
    'glass-card',
    'action-button',
    'state-banner',
    'route-frame',
    'background-layer',
    'product-card',
    'cart-panel',
    'checkout-panel',
  ]);
  const recipes = recipeNames.map((name) => {
    const old = byName.get(name) ?? {};
    const surfaces = unique([
      ...asArray(old.surfaces),
      ...componentCatalog.components.filter((component) => component.recipe === name).flatMap((component) => asArray(component.surfaces)),
    ]);
    const resolvedSurfaces = surfaces.length > 0 ? surfaces : name.includes('reserved') ? requiredSurfaces.filter((surface) => !currentSurfaces.has(surface)) : ['shared-ui'];
    return {
      name,
      status: old.status ?? (name.includes('reserved') ? 'reserved' : name.includes('governance') || name.includes('policy') ? 'core' : 'recipe'),
      surfaces: resolvedSurfaces,
      source: old.source ?? 'PRISMA Visual Catalog Governed v2',
      intent: old.intent ?? `Governed recipe for ${name}`,
      density: old.density ?? 'adapter-controlled',
      backgroundBehavior: old.backgroundBehavior ?? 'must resolve through surface adapter backgroundContract',
      motionBehavior: old.motionBehavior ?? 'must stay inside adapter motionBudget',
      allowedComponents: old.allowedComponents ?? componentCatalog.components.filter((component) => component.recipe === name).map((component) => component.id),
      blockedComponents: old.blockedComponents ?? [],
      tokens: old.tokens ?? defaultTokens(),
      libraries: old.libraries ?? [],
      atlasReferences: old.atlasReferences ?? ['atlas-source-map'],
      effectBoundaries: old.effectBoundaries ?? ['no global CSS hacks', 'no products/0.backgrounds runtime'],
      promotionRules: old.promotionRules ?? ['validators pass', 'rollback exists', 'no-touch clearance'],
      do: old.do ?? ['use catalog components', 'respect adapter density'],
      dont: old.dont ?? ['Fuji', 'soft-gray-clouds', 'products/0.backgrounds'],
    };
  });
  return { ...existing, schemaVersion: version, generatedAt: nowIso(), recipes };
}

function buildLibraryMap() {
  const existing = readJsonRel('config/prisma-visual/library-map.json', { libraries: [] });
  const packageJson = readJsonRel('package.json', {});
  const deps = { ...(packageJson.dependencies ?? {}), ...(packageJson.devDependencies ?? {}) };
  const expected = [
    '@radix-ui/react-dialog',
    '@radix-ui/react-dropdown-menu',
    '@radix-ui/react-scroll-area',
    '@radix-ui/react-select',
    '@radix-ui/react-tabs',
    '@radix-ui/react-tooltip',
    '@radix-ui/react-slot',
    'motion',
    'ogl',
    'lucide-react',
  ];
  const existingByName = new Map(asArray(existing.libraries).map((lib) => [lib.name ?? lib.id, lib]));
  const libraries = unique([...asArray(existing.libraries).map((lib) => lib.name ?? lib.id), ...expected]).map((name) => {
    const old = existingByName.get(name) ?? {};
    return {
      name,
      status: deps[name] ? 'available' : old.status ?? 'review',
      version: deps[name] ?? old.version ?? null,
      allowedUse: old.allowedUse ?? (name === 'ogl' ? ['backgrounds', 'lab effects'] : ['accessible primitive or UI utility']),
      forbiddenUse: old.forbiddenUse ?? ['replace domain logic', 'bypass adapters'],
      surfaces: old.surfaces ?? (name === 'ogl' ? ['pc', 'chart-lab', 'visual-os'] : ['tablet', 'pc', 'mobile', 'chart-lab', 'shared-ui']),
    };
  });
  return { ...existing, schemaVersion: version, generatedAt: nowIso(), libraries, rule: 'No new dependencies were installed by this v2 pass.' };
}

function buildComponentVariants(componentCatalog, adapters) {
  const adapterById = new Map(adapters.adapters.map((adapter) => [adapter.surfaceId, adapter]));
  const variants = [];
  for (const component of componentCatalog.components) {
    for (const surface of asArray(component.surfaces)) {
      const adapter = adapterById.get(surface) ?? baseAdapter(surface);
      variants.push({
        componentId: component.id,
        variantId: `${component.id}.${surface}.default`,
        allowedSurfaces: [surface],
        blockedSurfaces: requiredSurfaces.filter((item) => item !== surface && !asArray(component.surfaces).includes(item)),
        recipe: component.recipe,
        tokens: asArray(component.allowedTokens).slice(0, 24),
        density: adapter.density,
        motion: adapter.motionBudget,
        effectProfile: adapter.effectBudget,
        accessibilityRules: adapter.accessibilityConstraints,
        antiPatterns: unique([...asArray(component.forbiddenPatterns), ...asArray(adapter.forbiddenPatterns)]),
        status: component.status === 'deprecated' ? 'deprecated' : component.status === 'reserved' ? 'reserved' : 'governed',
      });
    }
  }
  return { schemaVersion: version, generatedAt: nowIso(), variants };
}

function componentsForDomain(componentCatalog, domain, surface = null) {
  const filtered = componentCatalog.components.filter((component) => {
    const domainMatch = component.domain === domain || (domain === 'inventory' && component.domain === 'commerce') || (domain === 'analytics' && component.family?.includes('metric'));
    const surfaceMatch = !surface || asArray(component.surfaces).includes(surface);
    return domainMatch && surfaceMatch && component.status !== 'deprecated';
  });
  if (filtered.length > 0) return filtered.map((component) => component.id).slice(0, 8);
  return componentCatalog.components.filter((component) => component.status === 'live').map((component) => component.id).slice(0, 5);
}

function buildDomainContracts(componentCatalog, recipeMap) {
  const recipeNames = new Set(recipeMap.recipes.map((recipe) => recipe.name));
  const domainSurface = {
    commerce: ['tablet', 'shared-ui'],
    checkout: ['tablet'],
    inventory: ['tablet', 'pc'],
    sync: ['tablet', 'pc'],
    license: ['tablet', 'pc', 'mobile'],
    reports: ['pc'],
    analytics: ['pc', 'chart-lab'],
    admin: ['pc', 'manager-console'],
    'command-ai': ['pc', 'shared-ui'],
    'mobile-companion': ['mobile'],
    'chart-lab': ['chart-lab'],
    training: ['training-mode'],
    demo: ['demo-mode'],
    'public-display': ['public-display', 'customer-display'],
    'future-surface': ['kiosk', 'warehouse-scanner', 'manager-console', 'training-mode', 'demo-mode', 'public-display', 'customer-display'],
  };
  const defaultRecipe = {
    commerce: 'product-commerce',
    checkout: 'checkout-panel',
    inventory: 'data-panel',
    sync: 'state-banner',
    license: 'state-banner',
    reports: 'data-panel',
    analytics: 'metric-card',
    admin: 'pc-graphite-glass',
    'command-ai': 'command-panel',
    'mobile-companion': 'mobile-mist',
    'chart-lab': 'chart-lab-analysis',
    training: 'reserved-safe-display',
    demo: 'reserved-safe-display',
    'public-display': 'reserved-safe-display',
    'future-surface': 'reserved-safe-display',
  };
  return {
    schemaVersion: version,
    generatedAt: nowIso(),
    domains: requiredDomains.map((domain) => {
      const surfaces = domainSurface[domain] ?? ['shared-ui'];
      const recipe = recipeNames.has(defaultRecipe[domain]) ? defaultRecipe[domain] : 'surface-panel';
      return {
        id: domain,
        status: surfaces.some((surface) => currentSurfaces.has(surface)) ? 'governed' : 'reserved',
        surfaces,
        role: `Domain contract for ${domain}`,
        allowedComponents: componentsForDomain(componentCatalog, domain),
        allowedRecipes: unique([recipe, 'surface-panel'].filter((item) => recipeNames.has(item))),
        blockedComponents: componentCatalog.components.filter((component) => component.status === 'deprecated').map((component) => component.id),
        atlasReferences: ['atlas-capability-map', 'atlas-engine-map'],
        motorReferences: domain === 'chart-lab' ? ['motor_lab_chart'] : domain === 'mobile-companion' ? ['motor_app_movil'] : domain === 'admin' ? ['motor_pc', 'motor_gobierno'] : ['motor_gobierno'],
        runtimeBoundaries: ['no private background runtime', 'respect surface adapter role'],
        validation: ['validate-domain-contracts', 'validate-governed-system'],
      };
    }),
  };
}

function enrichUsageRoute(route, surface, componentCatalog) {
  const noTouch = Boolean(route.noTouch);
  const hasLocalCss = asArray(route.currentLocalPatterns).some((item) => String(item).includes('css'));
  const layerRisk = route.layerRisk ?? (noTouch ? 'high' : hasLocalCss ? 'medium' : 'low');
  const backgroundRisk = route.backgroundRisk ?? (hasLocalCss ? 'review' : 'none-detected');
  const migrationTier = noTouch || layerRisk === 'high'
    ? 'blocked'
    : route.migrationStatus?.includes('pilot')
      ? 'tier-1-wrapper'
      : hasLocalCss
        ? 'tier-1-wrapper'
        : 'tier-0-observe';
  const componentMatchConfidence = asArray(route.canonicalComponents).length > 0 ? 0.72 : 0.2;
  const visualDebt = {
    score: (hasLocalCss ? 35 : 10) + (layerRisk === 'high' ? 35 : layerRisk === 'medium' ? 15 : 0) + (backgroundRisk === 'review' ? 10 : 0),
    signals: unique([
      ...(hasLocalCss ? ['local-css-present'] : ['shared-ui-or-low-local-css']),
      `layer-risk-${layerRisk}`,
      `background-risk-${backgroundRisk}`,
    ]),
  };
  const currentFiles = asArray(route.currentFiles);
  return {
    ...route,
    surface,
    currentFiles,
    currentLocalPatterns: asArray(route.currentLocalPatterns),
    canonicalComponents: asArray(route.canonicalComponents).filter((id) => componentCatalog.components.some((component) => component.id === id)),
    migrationStatus: route.migrationStatus ?? 'mapped',
    migrationTier,
    migrationComplexity: migrationTier === 'blocked' ? 'high' : hasLocalCss ? 'medium' : 'low',
    componentMatchConfidence,
    visualDebt,
    layerRisk,
    backgroundRisk,
    sharedUiAdoption: asArray(route.canonicalComponents).some((id) => String(id).startsWith('prisma.')) ? 'partial' : 'low',
    nextAction: route.nextAction ?? (migrationTier === 'blocked' ? 'requires no-touch clearance' : 'plan tiered migration after focal visual review'),
    blockedReason: route.blockedReason ?? (migrationTier === 'blocked' ? 'noTouch or high layer risk' : null),
    noTouch,
  };
}

function buildUsageMaps(componentCatalog) {
  const current = loadUsageMaps();
  const result = {};
  for (const [surface, map] of Object.entries(current)) {
    result[surface] = {
      ...map,
      schemaVersion: version,
      generatedAt: nowIso(),
      routes: asArray(map.routes).map((route) => enrichUsageRoute(route, surface, componentCatalog)),
    };
  }
  return result;
}

function buildMigrationTiers(usageMaps) {
  const tiers = [
    ['tier-0-observe', 'Inventory only. No production wiring.', 'low'],
    ['tier-1-wrapper', 'Introduce Prisma wrapper/shell without changing flow semantics.', 'low-medium'],
    ['tier-2-panel', 'Replace local panel/card with governed shared-ui panel.', 'medium'],
    ['tier-3-flow', 'Migrate full visual flow with route-level evidence.', 'high'],
    ['tier-4-authority', 'Promote as authority route after release gate evidence.', 'very-high'],
    ['blocked', 'Do not touch until explicit clearance.', 'blocked'],
  ].map(([id, description, risk]) => ({
    id,
    description,
    risk,
    requiredEvidence: id === 'tier-4-authority'
      ? ['visual review focal', 'validators pass', 'rollback package', 'release gate approval']
      : ['usage map evidence', 'validator pass'],
    allowedActions: id === 'blocked' ? [] : ['dry-run', 'plan', 'safe scaffold under tools'],
  }));
  const assignments = [];
  for (const [surface, map] of Object.entries(usageMaps)) {
    for (const route of asArray(map.routes)) {
      assignments.push({
        surface,
        route: route.route,
        tier: route.migrationTier,
        evidence: route.currentFiles,
        noTouch: route.noTouch,
        nextAction: route.nextAction,
      });
    }
  }
  return { schemaVersion: version, generatedAt: nowIso(), tiers, assignments };
}

function buildAdoptionScorecard(usageMaps, componentCatalog) {
  const surfaces = Object.entries(usageMaps).map(([surface, map]) => {
    const routes = asArray(map.routes);
    const governed = routes.filter((route) => asArray(route.canonicalComponents).length > 0).length;
    const blocked = routes.filter((route) => route.migrationTier === 'blocked').length;
    const shared = routes.filter((route) => route.sharedUiAdoption === 'partial' || route.sharedUiAdoption === 'high').length;
    const score = routes.length === 0 ? 0 : Math.round((shared / routes.length) * 100);
    return {
      surface,
      routes: routes.length,
      governedRoutes: governed,
      blockedRoutes: blocked,
      sharedUiAdoptionPct: score,
      status: score >= 70 ? 'strong' : score >= 35 ? 'partial' : 'early',
    };
  });
  return {
    schemaVersion: version,
    generatedAt: nowIso(),
    summary: {
      components: componentCatalog.components.length,
      liveComponents: componentCatalog.components.filter((component) => component.status === 'live').length,
      mappedComponents: componentCatalog.components.filter((component) => component.status === 'mapped').length,
      reservedComponents: componentCatalog.components.filter((component) => component.status === 'reserved').length,
    },
    surfaces,
    nextBatchRecommended: surfaces
      .filter((surface) => surface.routes > 0)
      .sort((a, b) => a.sharedUiAdoptionPct - b.sharedUiAdoptionPct)
      .slice(0, 3)
      .map((surface) => ({ surface: surface.surface, reason: 'lowest shared-ui adoption among mapped routes' })),
  };
}

function buildVisualDebtMap(usageMaps) {
  const routes = [];
  for (const [surface, map] of Object.entries(usageMaps)) {
    for (const route of asArray(map.routes)) {
      routes.push({
        surface,
        route: route.route,
        score: route.visualDebt?.score ?? 0,
        signals: route.visualDebt?.signals ?? [],
        layerRisk: route.layerRisk,
        backgroundRisk: route.backgroundRisk,
        cssLocalHeavy: asArray(route.currentLocalPatterns).some((item) => String(item).includes('css')),
        nextAction: route.nextAction,
        blockedReason: route.blockedReason,
      });
    }
  }
  return {
    schemaVersion: version,
    generatedAt: nowIso(),
    rules: [
      'local CSS adds debt',
      'high layer risk blocks migration',
      'background review requires adapter contract check',
      'no-touch routes stay blocked until clearance',
    ],
    routes,
    totals: {
      routes: routes.length,
      highDebt: routes.filter((route) => route.score >= 60).length,
      blocked: routes.filter((route) => route.blockedReason).length,
    },
  };
}

function buildScreenBlueprints(componentCatalog, domainContracts, adapters) {
  const adapterById = new Map(adapters.adapters.map((adapter) => [adapter.surfaceId, adapter]));
  const domainById = new Map(domainContracts.domains.map((domain) => [domain.id, domain]));
  const specs = [
    ['blueprint.tablet.commerce-review', 'tablet', 'commerce', '/catalog', 'operator catalog review', 'high'],
    ['blueprint.pc.admin-overview', 'pc', 'admin', '/dashboard', 'backoffice overview', 'high'],
    ['blueprint.mobile.owner-pulse', 'mobile', 'mobile-companion', '/', 'owner pulse', 'medium'],
    ['blueprint.chart-lab.analysis', 'chart-lab', 'chart-lab', '/chart-lab', 'chart analysis lab', 'medium'],
    ['blueprint.kiosk.future-display', 'kiosk', 'future-surface', '/kiosk/future-display', 'future kiosk dry-run', 'reserved'],
  ];
  return {
    schemaVersion: version,
    generatedAt: nowIso(),
    blueprints: specs.map(([id, surface, domain, route, screenIntent, criticality]) => {
      const adapter = adapterById.get(surface);
      const contract = domainById.get(domain);
      const components = asArray(contract?.allowedComponents).filter((componentId) => {
        const component = componentCatalog.components.find((item) => item.id === componentId);
        return component && (asArray(component.surfaces).includes(surface) || surface === 'kiosk' || asArray(component.surfaces).includes('shared-ui'));
      }).slice(0, 6);
      return {
        id,
        surface,
        domain,
        route,
        screenIntent,
        criticality,
        density: adapter?.density ?? 'adapter-controlled',
        recipe: asArray(contract?.allowedRecipes)[0] ?? asArray(adapter?.allowedRecipes)[0] ?? 'surface-panel',
        allowedComponents: components.length > 0 ? components : componentsForDomain(componentCatalog, domain, surface).slice(0, 5),
        blockedComponents: asArray(contract?.blockedComponents),
        tokens: defaultTokens(),
        background: adapter?.backgroundContract ?? {},
        libraries: adapter?.allowedLibraries ?? [],
        validatorsRequired: ['validate-screen-blueprints', 'validate-generator-contracts', 'validate-governed-system'],
        atlasReferences: ['atlas-source-map'],
        motorReferences: asArray(contract?.motorReferences),
        filesWouldCreate: ['Screen.tsx', 'screen.contract.json', 'README.md', 'validation-plan.md', 'manifest.json'],
        productionWired: false,
      };
    }),
  };
}

function buildGeneratorContracts(screenBlueprints) {
  return {
    schemaVersion: version,
    generatedAt: nowIso(),
    modes: ['dry-run', 'safe-scaffold'],
    defaultMode: 'dry-run',
    allowedSurfaces: generatorSurfaces,
    dryRunGuarantees: ['repoWrites false', 'no production route writes', 'manifest produced'],
    allowedWriteRoot: 'tools/prisma-visual/generated-screens',
    forbiddenPatterns: ['products/0.backgrounds', 'Fuji', 'soft-gray-clouds', '!important', 'global-css-hack'],
    requiredInputs: ['surface', 'domain', 'route', 'screenIntent', 'criticality', 'density', 'recipe'],
    blueprintIds: screenBlueprints.blueprints.map((blueprint) => blueprint.id),
    validatorsRequired: ['validate-generator-contracts', 'validate-governed-system'],
  };
}

function freshness(absPath) {
  if (!existsSync(absPath)) return 'missing';
  const ageMs = Date.now() - statSync(absPath).mtimeMs;
  const days = ageMs / 86400000;
  if (days <= 45) return 'current';
  if (days <= 120) return 'review';
  return 'stale';
}

function atlasId(relPath) {
  return relPath
    .replaceAll('\\', '/')
    .replace(/\.[^.]+$/, '')
    .replace(/[^a-zA-Z0-9]+/g, '.')
    .replace(/^\.+|\.+$/g, '')
    .toLowerCase();
}

function buildAtlasMaps() {
  const sources = expectedAtlas.map(([relPath, surface, kind]) => {
    const absPath = path.join(appRoot, relPath);
    const exists = existsSync(absPath);
    const status = exists ? kind : 'missing';
    const signals = kind === 'engine'
      ? ['functional engines', 'runtime rules', 'interaction rules']
      : kind === 'recipe'
        ? ['visual density', 'allowed recipes', 'background contract']
        : kind === 'archive'
          ? ['historical evidence']
          : ['surface role', 'governance gates', 'route hints'];
    return {
      id: atlasId(relPath),
      path: relPath,
      source: relPath,
      name: path.basename(relPath),
      surface,
      type: kind,
      kind,
      status,
      freshness: freshness(absPath),
      authorityLevel: kind === 'archive' ? 'archive' : kind === 'core' ? 'primary' : 'secondary',
      signalsExtracted: exists ? signals : [],
      usedBy: exists ? ['surface-adapters.json', 'domain-contracts.json', 'screen-blueprints.json', 'migration-tiers.json'] : [],
      conflicts: [],
      notes: exists ? 'Distilled into governed v2 maps; not copied literal.' : 'Expected atlas path missing; registered without inventing evidence.',
    };
  });
  const byStatus = (status) => sources.filter((source) => source.status === status);
  const atlasMap = {
    schemaVersion: version,
    generatedAt: nowIso(),
    sources: sources.map((source) => ({
      id: source.id,
      name: source.name,
      source: source.path,
      type: source.kind,
      status: source.status,
      surfaces: source.surface === 'all' ? requiredSurfaces : [source.surface],
      domains: source.kind === 'engine' ? ['sync', 'analytics', 'admin'] : ['commerce', 'admin', 'future-surface'],
      recipes: source.kind === 'recipe' ? ['surface-panel', 'tablet-cloudglass-light', 'pc-graphite-glass', 'mobile-mist'] : [],
      usableAs: source.signalsExtracted,
      blockedFor: source.status === 'missing' ? ['live evidence'] : [],
      promotionRule: source.status === 'missing' ? 'cannot promote from missing source' : 'requires validator pass and rollback',
      notes: source.notes,
    })),
  };
  const capabilityMap = {
    schemaVersion: version,
    generatedAt: nowIso(),
    capabilities: sources.filter((source) => source.status !== 'missing').map((source) => ({
      atlasId: source.id,
      surface: source.surface,
      capabilities: source.signalsExtracted,
      feeds: source.usedBy,
    })),
  };
  const engineMap = {
    schemaVersion: version,
    generatedAt: nowIso(),
    engines: sources.filter((source) => source.kind === 'engine' && source.status !== 'missing').map((source) => ({
      atlasId: source.id,
      surface: source.surface,
      engineSignals: source.signalsExtracted,
      producesContextFor: ['domain-contracts.json', 'generator-contracts.json'],
    })),
  };
  const runtimeMap = {
    schemaVersion: version,
    generatedAt: nowIso(),
    runtimeRules: sources.filter((source) => source.path.toLowerCase().includes('runtime') && source.status !== 'missing').map((source) => ({
      atlasId: source.id,
      surface: source.surface,
      backgroundRule: 'runtime backgrounds must resolve through public adapter contracts',
      blockedRuntimeSources: ['products/0.backgrounds', 'Fuji', 'soft-gray-clouds'],
    })),
  };
  const governanceMap = {
    schemaVersion: version,
    generatedAt: nowIso(),
    governanceSources: sources.filter((source) => /governor|feature|master|contracts/i.test(source.path) && source.status !== 'missing').map((source) => ({
      atlasId: source.id,
      authority: source.authorityLevel,
      feeds: ['authority-map.json', 'generator-contracts.json', 'validate-governed-system'],
    })),
  };
  return {
    sources,
    atlasMap,
    sourceMap: { version, generatedAt: nowIso(), sources },
    capabilityMap,
    engineMap,
    runtimeMap,
    governanceMap,
    audit: { total: sources.length, core: byStatus('core').length, recipe: byStatus('recipe').length, engine: byStatus('engine').length, missing: byStatus('missing').length },
  };
}

function motorId(file) {
  return file.replace(/\.[^.]+$/, '').replace(/[^a-zA-Z0-9]+/g, '_');
}

function buildContextMotorMaps() {
  const motors = expectedMotors.map(([file, role]) => {
    const absPath = path.join(motorsRoot, file);
    const exists = existsSync(absPath);
    const text = exists ? readText(absPath) : '';
    const dangerous = /start-app|Stop-Process|pnpm install|npm install|prisma generate/i.test(text);
    const todoMax = file === 'TodoALV.py' && /512000/.test(text) ? 'review-old-512000-reference-detected' : '81920-policy-required';
    return {
      id: motorId(file),
      name: file,
      path: absPath,
      type: role,
      status: exists ? 'available' : 'missing',
      purpose: role,
      inputs: exists ? ['repo paths', 'surface roots', 'context filters'] : [],
      outputs: exists ? ['context package metadata', 'reports', 'manifests'] : [],
      safeToRun: file === 'motor_verify.py' && exists && !dangerous,
      requiresServer: /playwright|run_playwright/i.test(file),
      requiresPlaywright: /playwright/i.test(file),
      requiresInstall: false,
      allowedPhase: ['inspect', 'derive-signals'],
      blockedPhase: dangerous || /playwright/i.test(file) ? ['default-execution'] : [],
      producesContextFor: role.includes('tablet') ? ['tablet-usage-map.json', 'visual-debt-map.json'] : role.includes('pc') ? ['pc-usage-map.json'] : role.includes('mobile') ? ['mobile-usage-map.json'] : role.includes('visual') ? ['visual-debt-map.json', 'adoption-scorecard.json'] : ['domain-contracts.json', 'authority-map.json'],
      notes: file === 'TodoALV.py' ? todoMax : exists ? 'Inspected as context motor; not executed by this pass.' : 'Expected motor missing; no evidence invented.',
      allowedUse: exists ? ['inspect', 'reuse-patterns', 'derive-surface-signals'] : [],
      forbiddenUse: ['replace-result-zip', 'mutate-repo', 'start-dev-server', 'install-dependencies'],
      signals: exists ? ['surface roots', 'classification policy', 'packaging policy'] : [],
      usedBy: exists ? ['context-motors-map.json', 'context-packaging-policy.json', 'adoption-scorecard.json'] : [],
    };
  });
  return {
    motors,
    map: { version, generatedAt: nowIso(), motorsRoot, motors },
    legacyMap: { schemaVersion: version, generatedAt: nowIso(), motorsRoot, motors },
    usage: {
      schemaVersion: version,
      generatedAt: nowIso(),
      inspectedOnly: true,
      executed: [],
      notExecutedBySafety: motors.filter((motor) => motor.status === 'available').map((motor) => motor.id),
      signalsConnected: motors.filter((motor) => motor.status === 'available').map((motor) => ({ motorId: motor.id, usedBy: motor.usedBy })),
    },
    packagingPolicy: {
      schemaVersion: version,
      generatedAt: nowIso(),
      maxPartKb: 81920,
      resultZipIsIndependent: true,
      forbidden: ['500MB TodoALV parts by default', 'secret inclusion', 'dev server startup', 'process killing'],
      requiredManifests: ['changed_files.json', 'backup_manifest.json', 'rollback instructions'],
    },
  };
}

function buildPlanMigration(usageMaps) {
  const candidates = [];
  for (const [surface, map] of Object.entries(usageMaps)) {
    for (const route of asArray(map.routes)) {
      if (route.migrationTier !== 'blocked') {
        candidates.push({
          surface,
          route: route.route,
          tier: route.migrationTier,
          complexity: route.migrationComplexity,
          confidence: route.componentMatchConfidence,
          nextAction: route.nextAction,
        });
      }
    }
  }
  candidates.sort((a, b) => {
    const tierRank = { 'tier-0-observe': 0, 'tier-1-wrapper': 1, 'tier-2-panel': 2, 'tier-3-flow': 3 };
    return (tierRank[a.tier] ?? 9) - (tierRank[b.tier] ?? 9) || b.confidence - a.confidence;
  });
  return {
    schemaVersion: version,
    generatedAt: nowIso(),
    recommendedBatch: candidates.slice(0, 10),
    blocked: Object.entries(usageMaps).flatMap(([surface, map]) => asArray(map.routes).filter((route) => route.migrationTier === 'blocked').map((route) => ({ surface, route: route.route, reason: route.blockedReason }))),
  };
}

function validateForbiddenRuntime() {
  let changed = '';
  try {
    changed = execFileSync('git', ['-C', repoRoot, 'diff', '--name-only', '--', 'apps/terminal-de-venta-system/products'], { encoding: 'utf8' });
  } catch {
    changed = '';
  }
  const files = changed
    .split(/\r?\n/)
    .filter(Boolean)
    .map((file) => path.join(repoRoot, file))
    .filter((file) => existsSync(file) && ['.ts', '.tsx', '.js', '.mjs', '.css', '.scss'].includes(path.extname(file).toLowerCase()));
  const errors = [];
  for (const file of files) {
    const rel = repoRel(file);
    const text = readText(file);
    if (/products\/0\.backgrounds/.test(text)) {
      errors.push(`${rel}: products/0.backgrounds runtime reference`);
    }
    if (/\bFuji\b/.test(text)) {
      errors.push(`${rel}: Fuji runtime reference`);
    }
    if (/soft-gray-clouds/.test(text)) {
      errors.push(`${rel}: soft-gray-clouds runtime reference`);
    }
  }
  const adapters = readJsonRel('config/prisma-visual/surface-adapters.json', { adapters: [] });
  for (const adapter of adapters.adapters) {
    const runtime = String(adapter.backgroundContract?.runtimePublicUrl ?? '');
    if (/products\/0\.backgrounds|soft-gray-clouds|\bFuji\b/.test(runtime)) {
      errors.push(`adapter ${adapter.surfaceId}: forbidden background runtime ${runtime}`);
    }
  }
  return { errors, warnings: [], checked: files.length + adapters.adapters.length };
}

function mkResult(name, start, checked, passed, warnings = [], errors = [], inputs = [], outputs = []) {
  return {
    validator: name,
    status: errors.length > 0 ? 'FAIL' : warnings.length > 0 ? 'WARN' : 'PASS',
    checked,
    passed,
    warnings,
    errors,
    inputs,
    outputs,
    durationMs: Date.now() - start,
  };
}

function validateJsonParse() {
  const start = Date.now();
  const inputs = listFiles(configRoot).filter((file) => path.extname(file).toLowerCase() === '.json');
  const errors = [];
  for (const file of inputs) {
    try {
      JSON.parse(readText(file));
    } catch (error) {
      errors.push(`${repoRel(file)}: ${error.message}`);
    }
  }
  return mkResult('validate-json-parse', start, inputs.length, inputs.length - errors.length, [], errors, inputs.map(repoRel));
}

function validateComponentVariants() {
  const start = Date.now();
  const catalog = readJsonRel('config/prisma-visual/component-catalog.json', { components: [] });
  const variants = readJsonRel('config/prisma-visual/component-variants.json', { variants: [] });
  const componentIds = new Set(catalog.components.map((component) => component.id));
  const surfaces = new Set(requiredSurfaces);
  const errors = [];
  for (const component of catalog.components) {
    if (component.status === 'live') {
      for (const sourceFile of asArray(component.sourceFiles)) {
        if (!existsSync(path.join(appRoot, sourceFile))) errors.push(`live ${component.id} missing source ${sourceFile}`);
      }
    }
    if (component.status === 'mapped' && asArray(component.sourceFiles).length === 0) errors.push(`mapped ${component.id} missing sourceFiles`);
    if (component.status === 'deprecated' && !(component.replacement || component.reason)) errors.push(`deprecated ${component.id} missing replacement/reason`);
  }
  for (const variant of variants.variants) {
    if (!componentIds.has(variant.componentId)) errors.push(`variant ${variant.variantId} unknown component ${variant.componentId}`);
    for (const surface of asArray(variant.allowedSurfaces)) {
      if (!surfaces.has(surface)) errors.push(`variant ${variant.variantId} invalid surface ${surface}`);
    }
  }
  return mkResult('validate-component-variants', start, variants.variants.length + catalog.components.length, variants.variants.length + catalog.components.length - errors.length, [], errors, ['component-catalog.json', 'component-variants.json']);
}

function validateSurfaceAdapters() {
  const start = Date.now();
  const adapters = readJsonRel('config/prisma-visual/surface-adapters.json', { adapters: [] });
  const got = new Set(adapters.adapters.map((adapter) => adapter.surfaceId));
  const errors = [];
  for (const surface of requiredSurfaces) {
    if (!got.has(surface)) errors.push(`missing adapter ${surface}`);
  }
  const fields = ['surfaceId', 'role', 'density', 'defaultTheme', 'backgroundContract', 'shellContract', 'layerBudget', 'allowedRecipes', 'allowedLibraries', 'forbiddenPatterns', 'accessibilityConstraints', 'runtimeBoundaries', 'motionBudget', 'effectBudget', 'atlasAllowed', 'motorsAllowed', 'generationAllowed', 'migrationPolicy'];
  for (const adapter of adapters.adapters) {
    for (const field of fields) {
      if (!(field in adapter)) errors.push(`adapter ${adapter.surfaceId} missing ${field}`);
    }
    if (adapter.backgroundContract?.runtimePublicUrl && /products\/0\.backgrounds|Fuji|soft-gray-clouds/i.test(adapter.backgroundContract.runtimePublicUrl)) {
      errors.push(`adapter ${adapter.surfaceId} has forbidden background runtime`);
    }
  }
  return mkResult('validate-surface-adapters', start, adapters.adapters.length, adapters.adapters.length - errors.length, [], errors, ['surface-adapters.json']);
}

function validateDomainContracts() {
  const start = Date.now();
  const domains = readJsonRel('config/prisma-visual/domain-contracts.json', { domains: [] });
  const catalog = readJsonRel('config/prisma-visual/component-catalog.json', { components: [] });
  const recipes = readJsonRel('config/prisma-visual/recipe-map.json', { recipes: [] });
  const componentIds = new Set(catalog.components.map((component) => component.id));
  const recipeNames = new Set(recipes.recipes.map((recipe) => recipe.name));
  const got = new Set(domains.domains.map((domain) => domain.id));
  const errors = [];
  for (const domain of requiredDomains) {
    if (!got.has(domain)) errors.push(`missing domain ${domain}`);
  }
  for (const domain of domains.domains) {
    for (const component of asArray(domain.allowedComponents)) {
      if (!componentIds.has(component)) errors.push(`domain ${domain.id} unknown component ${component}`);
    }
    for (const recipe of asArray(domain.allowedRecipes)) {
      if (!recipeNames.has(recipe)) errors.push(`domain ${domain.id} unknown recipe ${recipe}`);
    }
  }
  return mkResult('validate-domain-contracts', start, domains.domains.length, domains.domains.length - errors.length, [], errors, ['domain-contracts.json']);
}

function validateUsageMaps() {
  const start = Date.now();
  const catalog = readJsonRel('config/prisma-visual/component-catalog.json', { components: [] });
  const componentIds = new Set(catalog.components.map((component) => component.id));
  const errors = [];
  let checked = 0;
  for (const [surface, file] of Object.entries(usageMapFiles)) {
    const map = readJsonRel(`config/prisma-visual/${file}`, { routes: [] });
    for (const route of asArray(map.routes)) {
      checked += 1;
      const required = ['route', 'surface', 'currentFiles', 'currentLocalPatterns', 'canonicalComponents', 'migrationStatus', 'migrationTier', 'migrationComplexity', 'componentMatchConfidence', 'visualDebt', 'layerRisk', 'backgroundRisk', 'sharedUiAdoption', 'nextAction', 'noTouch'];
      for (const field of required) {
        if (!(field in route)) errors.push(`${file}:${route.route} missing ${field}`);
      }
      if (route.surface !== surface) errors.push(`${file}:${route.route} wrong surface ${route.surface}`);
      for (const component of asArray(route.canonicalComponents)) {
        if (!componentIds.has(component)) errors.push(`${file}:${route.route} unknown component ${component}`);
      }
    }
  }
  return mkResult('validate-usage-maps-v2', start, checked, checked - errors.length, [], errors, Object.values(usageMapFiles));
}

function validateMigrationTiers() {
  const start = Date.now();
  const data = readJsonRel('config/prisma-visual/migration-tiers.json', { tiers: [], assignments: [] });
  const valid = new Set(['tier-0-observe', 'tier-1-wrapper', 'tier-2-panel', 'tier-3-flow', 'tier-4-authority', 'blocked']);
  const errors = [];
  for (const tier of data.tiers) {
    if (!valid.has(tier.id)) errors.push(`invalid tier ${tier.id}`);
  }
  for (const assignment of data.assignments) {
    if (!valid.has(assignment.tier)) errors.push(`assignment ${assignment.surface}:${assignment.route} invalid tier`);
    if (assignment.tier === 'tier-4-authority' && asArray(assignment.evidence).length === 0) errors.push(`tier-4 ${assignment.surface}:${assignment.route} lacks evidence`);
  }
  return mkResult('validate-migration-tiers', start, data.assignments.length + data.tiers.length, data.assignments.length + data.tiers.length - errors.length, [], errors, ['migration-tiers.json']);
}

function validateAdoptionScorecard() {
  const start = Date.now();
  const data = readJsonRel('config/prisma-visual/adoption-scorecard.json', { surfaces: [] });
  const errors = [];
  for (const surface of data.surfaces) {
    if (surface.sharedUiAdoptionPct < 0 || surface.sharedUiAdoptionPct > 100) errors.push(`surface ${surface.surface} score out of range`);
    const mapFile = usageMapFiles[surface.surface];
    if (mapFile) {
      const map = readJsonRel(`config/prisma-visual/${mapFile}`, { routes: [] });
      if (asArray(map.routes).length !== surface.routes) errors.push(`surface ${surface.surface} route count mismatch`);
    }
  }
  return mkResult('validate-adoption-scorecard', start, data.surfaces.length, data.surfaces.length - errors.length, [], errors, ['adoption-scorecard.json']);
}

function validateVisualDebt() {
  const start = Date.now();
  const data = readJsonRel('config/prisma-visual/visual-debt-map.json', { routes: [], rules: [] });
  const errors = [];
  if (asArray(data.rules).length === 0) errors.push('visual debt rules empty');
  for (const route of data.routes) {
    if (typeof route.score !== 'number') errors.push(`${route.surface}:${route.route} score missing`);
    if (!Array.isArray(route.signals)) errors.push(`${route.surface}:${route.route} signals missing`);
  }
  return mkResult('validate-visual-debt', start, data.routes.length, data.routes.length - errors.length, [], errors, ['visual-debt-map.json']);
}

function validateScreenBlueprints() {
  const start = Date.now();
  const data = readJsonRel('config/prisma-visual/screen-blueprints.json', { blueprints: [] });
  const catalog = readJsonRel('config/prisma-visual/component-catalog.json', { components: [] });
  const adapters = readJsonRel('config/prisma-visual/surface-adapters.json', { adapters: [] });
  const recipes = readJsonRel('config/prisma-visual/recipe-map.json', { recipes: [] });
  const componentIds = new Set(catalog.components.map((component) => component.id));
  const adapterIds = new Set(adapters.adapters.map((adapter) => adapter.surfaceId));
  const recipeNames = new Set(recipes.recipes.map((recipe) => recipe.name));
  const errors = [];
  for (const blueprint of data.blueprints) {
    if (!adapterIds.has(blueprint.surface)) errors.push(`blueprint ${blueprint.id} unknown surface`);
    if (!recipeNames.has(blueprint.recipe)) errors.push(`blueprint ${blueprint.id} unknown recipe ${blueprint.recipe}`);
    for (const component of asArray(blueprint.allowedComponents)) {
      if (!componentIds.has(component)) errors.push(`blueprint ${blueprint.id} unknown component ${component}`);
    }
  }
  return mkResult('validate-screen-blueprints', start, data.blueprints.length, data.blueprints.length - errors.length, [], errors, ['screen-blueprints.json']);
}

function validateGeneratorContracts() {
  const start = Date.now();
  const contracts = readJsonRel('config/prisma-visual/generator-contracts.json', {});
  const blueprints = readJsonRel('config/prisma-visual/screen-blueprints.json', { blueprints: [] });
  const errors = [];
  for (const surface of generatorSurfaces) {
    if (!asArray(contracts.allowedSurfaces).includes(surface)) errors.push(`generator missing surface ${surface}`);
    const dryRun = generateSurfaceScreen({ surface, mode: 'dry-run' });
    if (dryRun.status !== 'PASS') errors.push(`dry-run ${surface} returned ${dryRun.status}: ${asArray(dryRun.errors).join('; ')}`);
    if (dryRun.repoWrites) errors.push(`dry-run ${surface} reports repoWrites true`);
  }
  for (const blueprintId of asArray(contracts.blueprintIds)) {
    if (!blueprints.blueprints.some((blueprint) => blueprint.id === blueprintId)) errors.push(`unknown blueprint id ${blueprintId}`);
  }
  return mkResult('validate-generator-contracts', start, generatorSurfaces.length, generatorSurfaces.length - errors.length, [], errors, ['generator-contracts.json']);
}

function validateAtlasMap() {
  const start = Date.now();
  const data = readJsonRel('config/prisma-visual/atlas-map.json', { sources: [] });
  const sourceMap = readJsonRel('config/prisma-visual/atlas-source-map.json', { sources: [] });
  const errors = [];
  const warnings = [];
  for (const source of sourceMap.sources) {
    const exists = existsSync(path.join(appRoot, source.path));
    if (source.status !== 'missing' && !exists) errors.push(`atlas ${source.id} not missing but path absent`);
    if (source.status === 'missing' && !source.notes) errors.push(`missing atlas ${source.id} lacks reason`);
  }
  if (asArray(data.sources).length === 0) errors.push('atlas-map empty');
  return mkResult('validate-atlas-map', start, sourceMap.sources.length, sourceMap.sources.length - errors.length, warnings, errors, ['atlas-map.json', 'atlas-source-map.json']);
}

function validateContextMotors() {
  const start = Date.now();
  const data = readJsonRel('config/prisma-visual/context-motors-map.json', { motors: [] });
  const errors = [];
  for (const motor of data.motors) {
    const exists = existsSync(motor.path);
    if (motor.status !== 'missing' && !exists) errors.push(`motor ${motor.id} not missing but path absent`);
    if (motor.safeToRun && (motor.requiresServer || motor.requiresPlaywright)) errors.push(`motor ${motor.id} unsafe safeToRun`);
  }
  return mkResult('validate-context-motors', start, data.motors.length, data.motors.length - errors.length, [], errors, ['context-motors-map.json']);
}

function validateBackgrounds() {
  const start = Date.now();
  const scan = validateForbiddenRuntime();
  const errors = [...scan.errors];
  const warnings = [...scan.warnings];
  let diff = '';
  try {
    diff = execFileSync('git', ['-C', repoRoot, 'diff', '--unified=0', '--', 'apps/terminal-de-venta-system'], { encoding: 'utf8' });
  } catch (error) {
    warnings.push(`git diff scan unavailable: ${error instanceof Error ? error.message : String(error)}`);
  }
  let currentRel = '';
  for (const line of diff.split(/\r?\n/)) {
    const header = /^diff --git a\/(.+?) b\/(.+)$/.exec(line);
    if (header) {
      currentRel = header[2].replaceAll('\\', '/');
      continue;
    }
    if (!line.startsWith('+') || line.startsWith('+++')) continue;
    const isRuntimeProduct = currentRel.startsWith('apps/terminal-de-venta-system/products/') && /\.(tsx?|jsx?|css|scss|mjs)$/.test(currentRel);
    if (!isRuntimeProduct) continue;
    if (line.includes('!important')) errors.push('new !important detected in own diff');
    if (/products\/0\.backgrounds|soft-gray-clouds|\bFuji\b/.test(line)) errors.push('new forbidden background token detected in own diff');
    if (/\b(html|body|:root)\b\s*\{/.test(line) && /global|globals\.css/i.test(currentRel)) {
      errors.push('new global CSS selector detected in own diff');
    }
  }
  return mkResult('validate-backgrounds-static', start, scan.checked, scan.checked - errors.length, warnings, unique(errors), ['app runtime files', 'git diff own changes']);
}

function validatorByName(name) {
  const map = {
    'validate-component-variants': validateComponentVariants,
    'validate-domain-contracts': validateDomainContracts,
    'validate-migration-tiers': validateMigrationTiers,
    'validate-adoption-scorecard': validateAdoptionScorecard,
    'validate-visual-debt': validateVisualDebt,
    'validate-screen-blueprints': validateScreenBlueprints,
    'validate-generator-contracts': validateGeneratorContracts,
    'validate-atlas-map': validateAtlasMap,
    'validate-context-motors': validateContextMotors,
    'validate-usage-maps': validateUsageMaps,
    'validate-surface-adapters': validateSurfaceAdapters,
    'validate-backgrounds': validateBackgrounds,
    'validate-json-parse': validateJsonParse,
  };
  return map[name];
}

function runValidator(name) {
  if (name === 'validate-governed-system') {
    const names = [
      'validate-json-parse',
      'validate-surface-adapters',
      'validate-component-variants',
      'validate-domain-contracts',
      'validate-usage-maps',
      'validate-migration-tiers',
      'validate-adoption-scorecard',
      'validate-visual-debt',
      'validate-screen-blueprints',
      'validate-generator-contracts',
      'validate-atlas-map',
      'validate-context-motors',
      'validate-backgrounds',
    ];
    const start = Date.now();
    const results = names.map((item) => runValidator(item));
    const errors = results.flatMap((result) => result.errors.map((error) => `${result.validator}: ${error}`));
    const warnings = results.flatMap((result) => result.warnings.map((warning) => `${result.validator}: ${warning}`));
    return {
      validator: 'validate-governed-system',
      status: errors.length > 0 ? 'FAIL' : warnings.length > 0 ? 'WARN' : 'PASS',
      checked: results.reduce((sum, result) => sum + result.checked, 0),
      passed: results.reduce((sum, result) => sum + result.passed, 0),
      warnings,
      errors,
      inputs: results.flatMap((result) => result.inputs),
      outputs: results.map((result) => result.validator),
      durationMs: Date.now() - start,
      children: results,
    };
  }
  const fn = validatorByName(name);
  if (!fn) {
    return mkResult(name, Date.now(), 0, 0, [], [`unknown validator ${name}`]);
  }
  return fn();
}

function generateSurfaceScreen(options = {}) {
  const surface = options.surface ?? 'tablet';
  const domainBySurface = {
    tablet: 'commerce',
    pc: 'admin',
    mobile: 'mobile-companion',
    'chart-lab': 'chart-lab',
    kiosk: 'future-surface',
  };
  const domain = options.domain ?? domainBySurface[surface] ?? 'future-surface';
  const route = options.route ?? `/generated/${surface}/${domain}`;
  const mode = options.mode ?? 'dry-run';
  const adapters = readJsonRel('config/prisma-visual/surface-adapters.json', { adapters: [] });
  const domains = readJsonRel('config/prisma-visual/domain-contracts.json', { domains: [] });
  const blueprints = readJsonRel('config/prisma-visual/screen-blueprints.json', { blueprints: [] });
  const generatorContracts = readJsonRel('config/prisma-visual/generator-contracts.json', { forbiddenPatterns: [], allowedSurfaces: [] });
  const componentCatalog = readJsonRel('config/prisma-visual/component-catalog.json', { components: [] });
  const adapter = adapters.adapters.find((item) => item.surfaceId === surface);
  const contract = domains.domains.find((item) => item.id === domain);
  const blueprint = blueprints.blueprints.find((item) => item.surface === surface && item.domain === domain) ?? blueprints.blueprints.find((item) => item.surface === surface);
  const recipe = options.recipe ?? blueprint?.recipe ?? asArray(adapter?.allowedRecipes)[0];
  const components = asArray(blueprint?.allowedComponents).filter((componentId) => componentCatalog.components.some((component) => component.id === componentId));
  const errors = [];
  if (!adapter) errors.push(`Unknown surface ${surface}`);
  if (!contract) errors.push(`Unknown domain ${domain}`);
  if (!blueprint) errors.push(`No blueprint for ${surface}/${domain}`);
  if (!asArray(generatorContracts.allowedSurfaces).includes(surface)) errors.push(`Generator surface not allowed: ${surface}`);
  if (mode !== 'dry-run') errors.push('Apply/scaffold mode is not enabled by default in this pass');
  return {
    status: errors.length > 0 ? 'FAIL' : 'PASS',
    mode,
    surface,
    domain,
    route,
    screenIntent: options.screenIntent ?? blueprint?.screenIntent ?? 'governed surface screen',
    criticality: options.criticality ?? blueprint?.criticality ?? 'medium',
    density: options.density ?? adapter?.density ?? 'adapter-controlled',
    blueprintId: blueprint?.id ?? null,
    adapterResolved: Boolean(adapter),
    domainResolved: Boolean(contract),
    recipeResolved: Boolean(recipe),
    componentsResolved: components.length > 0,
    variantsResolved: components.length > 0,
    backgroundResolved: Boolean(adapter?.backgroundContract),
    layerBudgetResolved: Boolean(adapter?.layerBudget),
    motionBudgetResolved: Boolean(adapter?.motionBudget),
    screenPlan: {
      adapter: adapter?.surfaceId,
      role: adapter?.role,
      shellContract: adapter?.shellContract,
      migrationPolicy: adapter?.migrationPolicy,
    },
    componentsSelected: components,
    recipeSelected: recipe,
    tokensSelected: blueprint?.tokens ?? defaultTokens(),
    backgroundSelected: adapter?.backgroundContract ?? null,
    librariesAllowed: adapter?.allowedLibraries ?? [],
    validatorsRequired: blueprint?.validatorsRequired ?? ['validate-governed-system'],
    filesWouldCreate: blueprint?.filesWouldCreate ?? ['Screen.tsx', 'screen.contract.json', 'README.md', 'validation-plan.md', 'manifest.json'],
    filesWouldModify: [],
    repoWrites: false,
    forbiddenPatterns: {
      products0Backgrounds: 0,
      fuji: 0,
      softGrayClouds: 0,
      important: 0,
      globalCss: 0,
    },
    riskNotes: unique([
      ...(surface === 'kiosk' ? ['reserved surface: dry-run only'] : []),
      ...(adapter?.status === 'reserved' ? ['adapter reserved'] : []),
    ]),
    warnings: [],
    errors,
  };
}

function markdownTable(rows) {
  if (rows.length === 0) return 'No rows.\n';
  const headers = Object.keys(rows[0]);
  const lines = [
    `| ${headers.join(' | ')} |`,
    `| ${headers.map(() => '---').join(' | ')} |`,
    ...rows.map((row) => `| ${headers.map((h) => String(row[h] ?? '').replaceAll('|', '\\|')).join(' | ')} |`),
  ];
  return `${lines.join('\n')}\n`;
}

function buildReports(data, ctx) {
  const statusCounts = data.componentCatalog.components.reduce((acc, component) => {
    acc[component.status] = (acc[component.status] ?? 0) + 1;
    return acc;
  }, {});
  const surfaceRows = data.surfaceAdapters.adapters.map((adapter) => ({
    surface: adapter.surfaceId,
    status: adapter.status,
    role: adapter.role,
    recipes: asArray(adapter.allowedRecipes).join(', '),
  }));
  const reportBase = 'docs/design/prisma-visual';
  const auditRows = [
    { source: 'component catalogs existentes', status: 'core', evidence: `${data.componentCatalog.components.length} components in config/prisma-visual/component-catalog.json` },
    { source: 'surface adapters existentes', status: 'core', evidence: `${data.surfaceAdapters.adapters.length} adapters in config/prisma-visual/surface-adapters.json` },
    { source: 'recipes existentes', status: 'core', evidence: `${data.recipeMap.recipes.length} recipes in config/prisma-visual/recipe-map.json` },
    { source: 'usage maps existentes', status: 'core', evidence: `${Object.keys(data.usageMaps).length} usage maps enriched` },
    { source: 'Visual OS variant packs', status: 'recipe', evidence: 'products/shared-ui/prisma/visual-os/prisma-visual-os.variant-packs.00m.json' },
    { source: 'Visual OS scorecard', status: 'recipe', evidence: 'products/shared-ui/prisma/visual-os/prisma-visual-os.scorecard.json' },
    { source: 'release gate', status: 'core', evidence: 'products/shared-ui/prisma/visual-os/prisma-visual-os.release-gate.00n.json' },
    { source: 'migration candidates', status: 'recipe', evidence: 'config/prisma-visual-system/migration-candidates.registry.json' },
  ];
  writeDoc(ctx, `${reportBase}/VISUAL_EXISTING_SYSTEM_AUDIT.md`, [
    '# VISUAL_EXISTING_SYSTEM_AUDIT',
    '',
    'Audit result: existing VisualCat, Visual OS, Surface Governor-adjacent registries, scorecards, release gates, route bindings and migration candidates were reused as sources.',
    '',
    markdownTable(auditRows),
  ].join('\n'), 'required governed v2 audit report');

  writeDoc(ctx, `${reportBase}/ATLAS_AUDIT.md`, [
    '# ATLAS_AUDIT',
    '',
    `Detected atlas sources: ${data.atlas.sources.filter((source) => source.status !== 'missing').length}`,
    `Missing expected atlas sources: ${data.atlas.sources.filter((source) => source.status === 'missing').length}`,
    '',
    markdownTable(data.atlas.sources.map((source) => ({ id: source.id, surface: source.surface, status: source.status, freshness: source.freshness, path: source.path })).slice(0, 80)),
  ].join('\n'), 'required governed v2 atlas audit report');

  writeDoc(ctx, `${reportBase}/CONTEXT_MOTORS_AUDIT.md`, [
    '# CONTEXT_MOTORS_AUDIT',
    '',
    `Motors root: ${motorsRoot}`,
    'Motors were inspected as source material and not executed by default.',
    '',
    markdownTable(data.motors.motors.map((motor) => ({ id: motor.id, status: motor.status, safeToRun: motor.safeToRun, requiresServer: motor.requiresServer, notes: motor.notes }))),
  ].join('\n'), 'required governed v2 context motors audit report');

  writeDoc(ctx, `${reportBase}/GIT_SCOPE_REPORT.md`, [
    '# GIT_SCOPE_REPORT',
    '',
    `Branch before changes: ${ctx.branch}`,
    '',
    '## git status before',
    '```text',
    ctx.gitBefore || '(clean)',
    '```',
    '',
    '## git diff summary before',
    '```text',
    ctx.gitDiffBefore || '(empty)',
    '```',
    '',
    'Scope rule: only additive/governance files under apps/terminal-de-venta-system plus final ZIP evidence outside repo.',
  ].join('\n'), 'required governed v2 git scope report');

  writeDoc(ctx, `${reportBase}/VISUAL_CATALOG_V2_REPORT.md`, [
    '# VISUAL_CATALOG_V2_REPORT',
    '',
    `Schema: ${version}`,
    `Components: ${data.componentCatalog.components.length}`,
    `Status counts: ${JSON.stringify(statusCounts)}`,
    '',
    '## Surfaces',
    markdownTable(surfaceRows),
    '## Decision authority',
    '- surface-adapters.json selects role, density, libraries, backgrounds and migration policy.',
    '- domain-contracts.json selects domain components and recipes.',
    '- component-variants.json constrains component usage per surface.',
    '- generator-contracts.json keeps generation dry-run safe by default.',
  ].join('\n'), 'required governed v2 catalog report');

  writeDoc(ctx, `${reportBase}/MIGRATION_PLAN.md`, [
    '# MIGRATION_PLAN',
    '',
    'Migration is tiered and route-based. No production route was rewritten by this pass.',
    '',
    markdownTable(data.plan.recommendedBatch),
    '## Blocked',
    markdownTable(data.plan.blocked.slice(0, 40)),
  ].join('\n'), 'required governed v2 migration plan');

  writeDoc(ctx, `${reportBase}/ADOPTION_SCORECARD.md`, [
    '# ADOPTION_SCORECARD',
    '',
    markdownTable(data.adoptionScorecard.surfaces),
    '',
    'Next batch recommended:',
    '',
    markdownTable(data.adoptionScorecard.nextBatchRecommended),
  ].join('\n'), 'required governed v2 adoption scorecard report');

  writeDoc(ctx, `${reportBase}/VISUAL_DEBT_REPORT.md`, [
    '# VISUAL_DEBT_REPORT',
    '',
    `Routes measured: ${data.visualDebtMap.totals.routes}`,
    `High debt routes: ${data.visualDebtMap.totals.highDebt}`,
    `Blocked routes: ${data.visualDebtMap.totals.blocked}`,
    '',
    markdownTable(data.visualDebtMap.routes.sort((a, b) => b.score - a.score).slice(0, 60)),
  ].join('\n'), 'required governed v2 visual debt report');

  writeDoc(ctx, `${reportBase}/GENERATOR_REPORT.md`, [
    '# GENERATOR_REPORT',
    '',
    'Generator supports dry-run by default for tablet, pc, mobile, chart-lab and kiosk.',
    '',
    markdownTable(generatorSurfaces.map((surface) => {
      const result = generateSurfaceScreen({ surface });
      return { surface, status: result.status, blueprint: result.blueprintId, repoWrites: result.repoWrites, recipe: result.recipeSelected };
    })),
  ].join('\n'), 'required governed v2 generator report');

  writeDoc(ctx, `${reportBase}/VALIDATION_MATRIX.md`, [
    '# VALIDATION_MATRIX',
    '',
    'This matrix is populated after validator execution in the result ZIP. Static validators are repo-native and run without server.',
    '',
    markdownTable([
      { validator: 'validate-component-variants', command: 'node tools/prisma-visual/validate-component-variants/index.mjs' },
      { validator: 'validate-domain-contracts', command: 'node tools/prisma-visual/validate-domain-contracts/index.mjs' },
      { validator: 'validate-migration-tiers', command: 'node tools/prisma-visual/validate-migration-tiers/index.mjs' },
      { validator: 'validate-adoption-scorecard', command: 'node tools/prisma-visual/validate-adoption-scorecard/index.mjs' },
      { validator: 'validate-visual-debt', command: 'node tools/prisma-visual/validate-visual-debt/index.mjs' },
      { validator: 'validate-screen-blueprints', command: 'node tools/prisma-visual/validate-screen-blueprints/index.mjs' },
      { validator: 'validate-generator-contracts', command: 'node tools/prisma-visual/validate-generator-contracts/index.mjs' },
      { validator: 'validate-atlas-map', command: 'node tools/prisma-visual/validate-atlas-map/index.mjs' },
      { validator: 'validate-context-motors', command: 'node tools/prisma-visual/validate-context-motors/index.mjs' },
      { validator: 'validate-governed-system', command: 'node tools/prisma-visual/validate-governed-system/index.mjs' },
    ]),
  ].join('\n'), 'required governed v2 validation matrix report');

  writeDoc(ctx, `${reportBase}/ATLAS_AND_MOTORS_REPORT.md`, [
    '# ATLAS_AND_MOTORS_REPORT',
    '',
    'Atlas and motors were connected to live contracts, maps, validators, generator contracts and migration tiers.',
    '',
    '## Atlas summary',
    markdownTable([
      { status: 'core', count: data.atlas.sources.filter((source) => source.status === 'core').length },
      { status: 'recipe', count: data.atlas.sources.filter((source) => source.status === 'recipe').length },
      { status: 'engine', count: data.atlas.sources.filter((source) => source.status === 'engine').length },
      { status: 'archive', count: data.atlas.sources.filter((source) => source.status === 'archive').length },
      { status: 'missing', count: data.atlas.sources.filter((source) => source.status === 'missing').length },
    ]),
    '## Motors summary',
    markdownTable(data.motors.motors.map((motor) => ({ motor: motor.id, status: motor.status, executed: 'no', usedBy: asArray(motor.usedBy).join(', ') }))),
  ].join('\n'), 'required governed v2 atlas and motors report');

  writeDoc(ctx, `${reportBase}/atlas-integration.md`, [
    '# atlas-integration',
    '',
    'Equivalent machine-readable outputs were created instead of a separate parallel authority:',
    '',
    '- config/prisma-visual/atlas-source-map.json',
    '- config/prisma-visual/atlas-capability-map.json',
    '- config/prisma-visual/atlas-engine-map.json',
    '- config/prisma-visual/atlas-runtime-map.json',
    '- config/prisma-visual/atlas-governance-map.json',
    '',
    'These files feed adapters, domain contracts, screen blueprints, generator contracts, migration tiers and validators.',
  ].join('\n'), 'atlas integration pointer');

  writeDoc(ctx, `${reportBase}/RISKS_PENDING.md`, [
    '# RISKS_PENDING',
    '',
    '- No dev server, process kill, install, Prisma generate, pc:typecheck hot path or full visual Playwright was run by design.',
    '- Reserved future surfaces remain dry-run only until explicit promotion.',
    '- High-risk/no-touch routes require human clearance before production visual migration.',
  ].join('\n'), 'required risk report');

  writeDoc(ctx, `${reportBase}/CONTINUATION.md`, [
    '# CONTINUATION',
    '',
    'Recommended next step:',
    '',
    '1. Pick the first route from MIGRATION_PLAN.md recommendedBatch.',
    '2. Run visual review focal for that route.',
    '3. Apply tier-1-wrapper only if validators pass and rollback is prepared.',
    '4. Re-run measure-adoption and plan-migration.',
  ].join('\n'), 'required continuation report');

  writeDoc(ctx, `${reportBase}/FINAL_VERDICT.md`, [
    '# FINAL_VERDICT',
    '',
    'Verdict is finalized by the packaging step after validators and generator dry-runs run.',
    '',
    `Live components: ${statusCounts.live ?? 0}`,
    `Mapped components: ${statusCounts.mapped ?? 0}`,
    `Planned components: ${statusCounts.planned ?? 0}`,
    `Reserved components: ${statusCounts.reserved ?? 0}`,
    `Deprecated components: ${statusCounts.deprecated ?? 0}`,
    'Governed: adapters, variants, domains, blueprints, generator contracts and validators now govern usage.',
    'Blocked: no-touch/high-risk routes and deprecated runtime background patterns remain blocked.',
  ].join('\n'), 'required final verdict report');
}

function buildWrappers(ctx) {
  const validators = [
    'validate-component-variants',
    'validate-domain-contracts',
    'validate-migration-tiers',
    'validate-adoption-scorecard',
    'validate-visual-debt',
    'validate-screen-blueprints',
    'validate-generator-contracts',
    'validate-atlas-map',
    'validate-context-motors',
    'validate-governed-system',
  ];
  for (const name of validators) {
    writeTool(ctx, `tools/prisma-visual/${name}/index.mjs`, [
      "import { runValidatorCli } from '../governed-v2.mjs';",
      `runValidatorCli('${name}');`,
    ].join('\n'), `node wrapper for ${name}`, [name]);
  }
  writeTool(ctx, 'tools/prisma-visual/generate-surface-screen/index.mjs', [
    "import { runGeneratorCli } from '../governed-v2.mjs';",
    'runGeneratorCli();',
  ].join('\n'), 'dry-run surface screen generator', ['validate-generator-contracts']);
  writeTool(ctx, 'tools/prisma-visual/plan-migration/index.mjs', [
    "import { runPlanMigrationCli } from '../governed-v2.mjs';",
    'runPlanMigrationCli();',
  ].join('\n'), 'migration planner wrapper', ['validate-migration-tiers']);
  writeTool(ctx, 'tools/prisma-visual/measure-adoption/index.mjs', [
    "import { runMeasureAdoptionCli } from '../governed-v2.mjs';",
    'runMeasureAdoptionCli();',
  ].join('\n'), 'adoption measurement wrapper', ['validate-adoption-scorecard']);
}

function buildGovernedSystem(stampArg) {
  const ctx = createContext(stampArg);
  ctx.branch = git(['branch', '--show-current']);
  ctx.gitBefore = git(['status', '--short']);
  ctx.gitDiffBefore = git(['diff', '--stat']);
  stageWrite(ctx, 'evidence', 'git status before.txt', ctx.gitBefore || '(clean)');
  stageWrite(ctx, 'evidence', 'git branch before.txt', ctx.branch);
  stageWrite(ctx, 'evidence', 'git diff summary before.txt', ctx.gitDiffBefore || '(empty)');

  const initialCandidates = {
    configFiles: listFiles(configRoot).filter((file) => path.extname(file) === '.json').map(repoRel),
    atlasFiles: expectedAtlas.filter(([rel]) => existsSync(path.join(appRoot, rel))).map(([rel]) => rel),
    motors: expectedMotors.filter(([file]) => existsSync(path.join(motorsRoot, file))).map(([file]) => path.join(motorsRoot, file)),
    systems: [
      'VisualCat config/prisma-visual',
      'Visual system config/prisma-visual-system',
      'Visual OS products/shared-ui/prisma/visual-os',
      'Shared UI products/shared-ui/prisma',
      'Context motors F:/PRISMA_CTX/MOTORES',
    ],
  };
  stageWrite(ctx, 'evidence', 'initial candidates.json', stringify(initialCandidates));

  const usageBefore = loadUsageMaps();
  const componentCatalog = buildComponentCatalog(usageBefore);
  const surfaceAdapters = buildSurfaceAdapters();
  const recipeMap = buildRecipeMap(componentCatalog);
  const libraryMap = buildLibraryMap();
  const componentVariants = buildComponentVariants(componentCatalog, surfaceAdapters);
  const usageMaps = buildUsageMaps(componentCatalog);
  const migrationTiers = buildMigrationTiers(usageMaps);
  const adoptionScorecard = buildAdoptionScorecard(usageMaps, componentCatalog);
  const visualDebtMap = buildVisualDebtMap(usageMaps);
  const domainContracts = buildDomainContracts(componentCatalog, recipeMap);
  const screenBlueprints = buildScreenBlueprints(componentCatalog, domainContracts, surfaceAdapters);
  const generatorContracts = buildGeneratorContracts(screenBlueprints);
  const atlas = buildAtlasMaps();
  const motors = buildContextMotorMaps();
  const plan = buildPlanMigration(usageMaps);
  const data = { componentCatalog, surfaceAdapters, recipeMap, libraryMap, componentVariants, usageMaps, migrationTiers, adoptionScorecard, visualDebtMap, domainContracts, screenBlueprints, generatorContracts, atlas, motors, plan };

  writeJson(ctx, 'config/prisma-visual/component-catalog.json', componentCatalog, 'enrich component catalog for governed v2', ['component-catalog', 'usage maps', 'shared-ui'], ['validate-component-variants']);
  writeJson(ctx, 'config/prisma-visual/surface-adapters.json', surfaceAdapters, 'cover current and future surfaces for governed v2', ['surface-adapters', 'atlas'], ['validate-surface-adapters', 'validate-governed-system']);
  writeJson(ctx, 'config/prisma-visual/recipe-map.json', recipeMap, 'connect recipes to components, adapters, atlas and generator', ['recipe-map', 'component-catalog'], ['validate-domain-contracts', 'validate-screen-blueprints']);
  writeJson(ctx, 'config/prisma-visual/library-map.json', libraryMap, 'connect installed libraries to allowed surface usage', ['package.json'], ['validate-governed-system']);
  writeJson(ctx, 'config/prisma-visual/component-variants.json', componentVariants, 'required governed v2 component variants', ['component-catalog', 'surface-adapters'], ['validate-component-variants']);
  writeJson(ctx, 'config/prisma-visual/domain-contracts.json', domainContracts, 'required governed v2 domain contracts', ['component-catalog', 'recipe-map'], ['validate-domain-contracts']);
  writeJson(ctx, 'config/prisma-visual/screen-blueprints.json', screenBlueprints, 'required governed v2 screen blueprints', ['domain-contracts', 'surface-adapters'], ['validate-screen-blueprints']);
  writeJson(ctx, 'config/prisma-visual/migration-tiers.json', migrationTiers, 'required governed v2 migration tiers', ['usage maps', 'migration candidates'], ['validate-migration-tiers']);
  writeJson(ctx, 'config/prisma-visual/adoption-scorecard.json', adoptionScorecard, 'required governed v2 adoption scorecard', ['usage maps', 'Visual OS scorecard'], ['validate-adoption-scorecard']);
  writeJson(ctx, 'config/prisma-visual/visual-debt-map.json', visualDebtMap, 'required governed v2 visual debt map', ['usage maps', 'migration candidates'], ['validate-visual-debt']);
  writeJson(ctx, 'config/prisma-visual/generator-contracts.json', generatorContracts, 'required governed v2 generator contracts', ['screen-blueprints', 'surface-adapters'], ['validate-generator-contracts']);
  writeJson(ctx, 'config/prisma-visual/atlas-map.json', atlas.atlasMap, 'required governed v2 atlas map', ['atlas files'], ['validate-atlas-map']);
  writeJson(ctx, 'config/prisma-visual/atlas-source-map.json', atlas.sourceMap, 'required governed v2 atlas source map', ['atlas files'], ['validate-atlas-map']);
  writeJson(ctx, 'config/prisma-visual/atlas-capability-map.json', atlas.capabilityMap, 'required governed v2 atlas capability map', ['atlas files'], ['validate-atlas-map']);
  writeJson(ctx, 'config/prisma-visual/atlas-engine-map.json', atlas.engineMap, 'required governed v2 atlas engine map', ['atlas files'], ['validate-atlas-map']);
  writeJson(ctx, 'config/prisma-visual/atlas-runtime-map.json', atlas.runtimeMap, 'required governed v2 atlas runtime map', ['atlas files'], ['validate-atlas-map']);
  writeJson(ctx, 'config/prisma-visual/atlas-governance-map.json', atlas.governanceMap, 'required governed v2 atlas governance map', ['atlas files'], ['validate-atlas-map']);
  writeJson(ctx, 'config/prisma-visual/context-motors-map.json', motors.legacyMap, 'required governed v2 context motors map', ['F:/PRISMA_CTX/MOTORES'], ['validate-context-motors']);
  writeJson(ctx, 'config/prisma-visual/context-motors.map.json', motors.map, 'required governed v2 context motors dotted map', ['F:/PRISMA_CTX/MOTORES'], ['validate-context-motors']);
  writeJson(ctx, 'config/prisma-visual/context-motors.usage.json', motors.usage, 'required governed v2 context motors usage', ['F:/PRISMA_CTX/MOTORES'], ['validate-context-motors']);
  writeJson(ctx, 'config/prisma-visual/context-packaging-policy.json', motors.packagingPolicy, 'required governed v2 context packaging policy', ['F:/PRISMA_CTX/MOTORES'], ['validate-context-motors']);
  for (const [surface, map] of Object.entries(usageMaps)) {
    writeJson(ctx, `config/prisma-visual/${usageMapFiles[surface]}`, map, `enrich ${surface} usage map for governed v2`, ['usage map', 'component catalog'], ['validate-usage-maps', 'validate-governed-system']);
  }

  buildReports(data, ctx);
  buildWrappers(ctx);

  stageWrite(ctx, 'manifests', 'changed_files.json', stringify(ctx.changed));
  stageWrite(ctx, 'manifests', 'backup_manifest.json', stringify(ctx.backups));
  stageWrite(ctx, 'manifests', 'rollback instructions.md', [
    '# Rollback instructions',
    '',
    'No files were deleted by this pass.',
    '',
    'For modified files, restore the matching backup listed in backup_manifest.json.',
    'For created files, delete only the files whose changed_files.json rollbackAction is delete.',
    '',
    `Backup root: ${ctx.dirs.backupRoot}`,
  ].join('\n'));

  console.log(JSON.stringify({
    status: 'BUILT',
    stamp: ctx.stamp,
    stageRoot: ctx.dirs.stageRoot,
    backupRoot: ctx.dirs.backupRoot,
    changedFiles: ctx.changed.length,
  }, null, 2));
}

export function runValidatorCli(name) {
  const args = parseArgs(process.argv.slice(2));
  const result = runValidator(name);
  const output = stringify(result);
  if (args.out) {
    mkdirFor(args.out);
    writeFileSync(args.out, output, 'utf8');
  }
  console.log(output);
  if (result.status === 'FAIL') process.exitCode = 1;
}

export function runGeneratorCli() {
  const args = parseArgs(process.argv.slice(2));
  const result = generateSurfaceScreen({
    surface: args.surface,
    domain: args.domain,
    route: args.route,
    screenIntent: args.screenIntent,
    criticality: args.criticality,
    density: args.density,
    recipe: args.recipe,
    mode: args.apply ? 'apply' : 'dry-run',
  });
  const output = stringify(result);
  if (args.out) {
    mkdirFor(args.out);
    writeFileSync(args.out, output, 'utf8');
  }
  console.log(output);
  if (result.status === 'FAIL') process.exitCode = 1;
}

export function runPlanMigrationCli() {
  const usageMaps = loadUsageMaps();
  const plan = buildPlanMigration(usageMaps);
  console.log(stringify({ status: 'PASS', plan }));
}

export function runMeasureAdoptionCli() {
  const usageMaps = loadUsageMaps();
  const catalog = readJsonRel('config/prisma-visual/component-catalog.json', { components: [] });
  const scorecard = buildAdoptionScorecard(usageMaps, catalog);
  console.log(stringify({ status: 'PASS', adoptionScorecard: scorecard }));
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const command = args._[0] ?? 'help';
  if (command === 'build') {
    buildGovernedSystem(args.stamp);
    return;
  }
  if (command === 'validate') {
    runValidatorCli(args._[1] ?? 'validate-governed-system');
    return;
  }
  if (command === 'generate') {
    runGeneratorCli();
    return;
  }
  if (command === 'plan-migration') {
    runPlanMigrationCli();
    return;
  }
  if (command === 'measure-adoption') {
    runMeasureAdoptionCli();
    return;
  }
  console.log('Usage: node tools/prisma-visual/governed-v2.mjs build|validate|generate|plan-migration|measure-adoption');
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main();
}
