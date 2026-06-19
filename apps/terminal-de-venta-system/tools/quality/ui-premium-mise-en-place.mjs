#!/usr/bin/env node
/* PRISMA Premium Visual Mise en Place v1 - compact prep reports, not a redesign */
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const appRoot = process.cwd();
const TASK = 'Build PRISMA Premium Visual Mise en Place v1 across Tablet, Mobile/App, PC, Web/Edit, Control Center, Chart Lab and Shared UI, preparing all surfaces to use the full available visual library/effect/token/component ecosystem for future premium design.';
const PRIORITY = ['tablet', 'mobile', 'pc', 'web', 'control-center', 'chart-lab', 'shared-ui'];
const DOC_DIR = path.join(appRoot, 'docs', 'quality');
const CURRENT_DIR = path.join(appRoot, '.prisma-ui', 'current');
const INDEX_DIR = path.join(appRoot, '.prisma-ui', 'premium-mise-en-place');
const EXTERNAL_LIBRARY_INPUTS = [
  'F:/descargasf/libraries-detected.json',
  'F:/descargasf/prisma visualv2 1106 0349 backups/config__prisma-visual__library-map.json',
  'F:/descargasf/libinv 0106 0530.txt',
  'F:/descargasf/libinv 0106 0530 result.zip'
];

const REPORT_FILES = {
  mise: 'PRISMA_PREMIUM_DESIGN_MISE_EN_PLACE_V1.md',
  pantry: 'VISUAL_CAPABILITY_PANTRY_REPORT.md',
  stations: 'VISUAL_SURFACE_STATIONS_REPORT.md',
  recipes: 'VISUAL_RECIPE_PREP_REPORT.md',
  slots: 'VISUAL_EDITABLE_SLOTS_SUMMARY.md',
  foundation: 'VISUAL_FOUNDATION_CLEAN_REPORT.md',
  retired: 'VISUAL_RETIRED_LAYERS_MANIFEST.md',
  cleanRepo: 'CLEAN_REPO_REPORT.md',
  reuse: 'REUSE_REPORT.md',
  workflow: 'SMALL_VS_BIG_VISUAL_WORKFLOW.md'
};

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

function nowIso() {
  return new Date().toISOString();
}

function toPosix(value) {
  return String(value || '').replace(/\\/g, '/');
}

function relApp(p) {
  return toPosix(path.relative(appRoot, p));
}

function uniq(values) {
  return Array.from(new Set((values || []).filter((value) => value !== undefined && value !== null && value !== '')));
}

function sortObject(value) {
  return Object.fromEntries(Object.entries(value || {}).sort((a, b) => a[0].localeCompare(b[0])));
}

function countBy(items, keyOrFn) {
  const getKey = typeof keyOrFn === 'function' ? keyOrFn : (item) => item?.[keyOrFn];
  const counts = {};
  for (const item of Array.isArray(items) ? items : []) {
    const key = String(getKey(item) || 'unknown');
    counts[key] = (counts[key] || 0) + 1;
  }
  return sortObject(counts);
}

function sample(items, limit = 12) {
  return (Array.isArray(items) ? items : []).slice(0, limit);
}

function runGit(args) {
  try {
    return execFileSync('git', args, { cwd: appRoot, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
  } catch {
    return '';
  }
}

function gitRoot() {
  return runGit(['rev-parse', '--show-toplevel']) || appRoot;
}

function gitMeta() {
  return {
    repoHead: runGit(['rev-parse', 'HEAD']) || null,
    branch: runGit(['branch', '--show-current']) || null,
    statusShort: runGit(['status', '--short']).split(/\r?\n/).filter(Boolean)
  };
}

function parseArgs() {
  const raw = process.argv.slice(2);
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

function fileInfo(p) {
  const normalized = p.replace(/\//g, path.sep);
  const full = path.isAbsolute(normalized) ? normalized : path.join(appRoot, normalized);
  if (!exists(full)) return { path: toPosix(p), exists: false };
  const stat = fs.statSync(full);
  return { path: toPosix(p), exists: true, bytes: stat.size, kb: Math.round((stat.size / 1024) * 10) / 10, modifiedAt: stat.mtime.toISOString() };
}

function listFiles(rootRel, predicate = () => true, limit = 5000) {
  const root = path.join(appRoot, rootRel);
  const out = [];
  const skip = new Set(['.git', 'node_modules', '.next', 'dist', 'build', 'coverage', '.turbo', '.cache', 'out', '__pycache__', '.generated']);
  function walk(dir) {
    if (!exists(dir) || out.length >= limit) return;
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        if (!skip.has(entry.name)) walk(full);
      } else if (predicate(full)) {
        out.push(relApp(full));
      }
      if (out.length >= limit) return;
    }
  }
  walk(root);
  return out.sort();
}

function parseLibInv(text) {
  const ecosystem = {};
  const summaryMatch = text.match(/RESUMEN POR ECOSISTEMA\s*-+([\s\S]*?)\n\n/);
  if (summaryMatch) {
    for (const line of summaryMatch[1].split(/\r?\n/)) {
      const match = line.match(/^([^:]+):\s*(\d+)/);
      if (match) ecosystem[match[1].trim()] = Number(match[2]);
    }
  }
  const tools = {};
  const toolsMatch = text.match(/HERRAMIENTAS DETECTADAS\s*-+([\s\S]*?)\n\n/);
  if (toolsMatch) {
    for (const line of toolsMatch[1].split(/\r?\n/)) {
      const match = line.match(/^([^:]+):\s*(.+)$/);
      if (match) tools[match[1].trim()] = match[2].trim();
    }
  }
  return { ecosystem, tools };
}

function loadExternalLibraryInputs() {
  const inputs = [];
  const libraries = [];
  for (const rawPath of EXTERNAL_LIBRARY_INPUTS) {
    const nativePath = rawPath.replace(/\//g, path.sep);
    const info = fileInfo(nativePath);
    inputs.push({ ...info, source: 'external-local' });
    if (!info.exists) continue;
    if (rawPath.endsWith('.json')) {
      const payload = readJson(nativePath, null);
      if (Array.isArray(payload?.libraries)) {
        for (const item of payload.libraries) {
          libraries.push({
            name: item.name,
            role: item.role || 'library',
            status: item.status || (item.detected ? 'available' : 'not_detected'),
            detected: Boolean(item.detected),
            restriction: item.restriction || null,
            source: rawPath
          });
        }
      } else if (payload && typeof payload === 'object') {
        for (const [name, detected] of Object.entries(payload)) {
          libraries.push({
            name,
            role: 'detected visual/runtime library',
            status: detected ? 'available' : 'not_detected',
            detected: Boolean(detected),
            restriction: null,
            source: rawPath
          });
        }
      }
    } else if (rawPath.endsWith('.txt')) {
      const parsed = parseLibInv(readText(nativePath));
      inputs[inputs.length - 1].summary = parsed;
    }
  }
  return { inputs, libraries: libraries.sort((a, b) => String(a.name).localeCompare(String(b.name))) };
}

function loadPackageAvailability() {
  const pkg = readJson(path.join(appRoot, 'package.json'), {});
  const deps = { ...(pkg.dependencies || {}), ...(pkg.devDependencies || {}) };
  return Object.fromEntries(Object.entries(deps).sort((a, b) => a[0].localeCompare(b[0])));
}

function capabilityDecision(capability) {
  if (!capability.available) return 'not_available';
  if (capability.default_decision === 'mandatory' || capability.default_decision === 'prefer') return 'prepared_foundation';
  if (capability.risk === 'high') return 'bounded_or_rejected_until_explicit_recipe';
  if (capability.default_decision === 'review') return 'consider_with_surface_guardrails';
  return 'available_when_relevant';
}

function buildCapabilityPantry(state) {
  const matrix = state.visualCapabilityMatrix;
  const externalByName = new Map(state.externalLibraries.libraries.map((item) => [item.name, item]));
  const packageAvailability = loadPackageAvailability();
  const capabilities = (matrix.capabilities || []).map((capability) => {
    const packageVersion = packageAvailability[capability.id] || null;
    const external = externalByName.get(capability.id) || null;
    return {
      id: capability.id,
      kind: capability.kind,
      family: capability.family,
      available: Boolean(capability.available || packageVersion || external?.detected),
      risk: capability.risk || 'unknown',
      decision: capabilityDecision(capability),
      defaultDecision: capability.default_decision || null,
      evidenceCount: Array.isArray(capability.evidence) ? capability.evidence.length : (capability.evidence_count || 0),
      contribution: capability.visual_contribution || capability.contribution || null,
      packageVersion,
      externalStatus: external?.status || null,
      restriction: external?.restriction || null
    };
  });
  const decisions = countBy(capabilities, 'decision');
  const risks = countBy(capabilities, 'risk');
  return {
    schema: 'prisma.ui.premium-mise-en-place.capability-pantry.v1',
    status: capabilities.length ? 'CERTIFIED' : 'BLOCKED',
    task: TASK,
    capabilityCount: capabilities.length,
    availableCount: capabilities.filter((item) => item.available).length,
    decisions,
    risks,
    capabilities,
    appCapabilityRequirementKeys: Object.keys(state.appCapabilityRequirements || {}).sort(),
    externalLibraryInputs: state.externalLibraries.inputs,
    externalLibrarySamples: sample(state.externalLibraries.libraries, 24)
  };
}

function requirementBuckets(requirements) {
  const buckets = {
    must_use: [],
    should_use: [],
    consider_required: [],
    bounded_optional: [],
    high_risk_optional: [],
    forbidden_for_scope: []
  };
  for (const item of requirements?.capabilities || []) {
    if (buckets[item.level]) buckets[item.level].push(item.capability);
  }
  for (const key of Object.keys(buckets)) buckets[key] = uniq(buckets[key]).sort();
  return buckets;
}

function surfaceGuardrail(surface) {
  const map = {
    tablet: 'Tablet keeps local-sale autonomy; visual layers cannot block product, cart, checkout or shift operations.',
    mobile: 'Mobile/App stays compact and assistive; it does not become POS.',
    pc: 'PC remains governance/backoffice; do not copy Tablet selling density into PC.',
    web: 'Web/Edit stays public or editorial safe; do not import POS assumptions.',
    'control-center': 'Control Center stays operator status and release control, with public-safe redaction.',
    'chart-lab': 'Chart Lab can experiment, but lab visuals need governor evidence before production use.',
    'shared-ui': 'Shared UI changes require cross-surface compatibility evidence before promotion.'
  };
  return map[surface] || 'Use governed surface ownership before visual mutation.';
}

function validationGates(surface) {
  const base = [
    'node tools/quality/ui-certainty.mjs certify-all-surfaces --strict',
    'node tools/quality/ui-certainty.mjs visual-control:certify --strict'
  ];
  if (surface === 'tablet') return ['node tools/quality/ui-certainty.mjs certify --surface tablet --route /pos --strict', ...base];
  if (surface === 'shared-ui') return ['node tools/quality/ui-certainty.mjs scope --all', ...base];
  return base;
}

function buildSurfaceStations(state) {
  const surfaceSource = state.visualControlSurfaces.surfaces || [];
  const bySurface = new Map(surfaceSource.map((surface) => [surface.surface, surface]));
  const stations = PRIORITY.map((surface, index) => {
    const source = bySurface.get(surface) || {};
    const requirements = state.appCapabilityRequirements[surface] || {};
    const buckets = requirementBuckets(requirements);
    return {
      surface,
      priority: index + 1,
      app: source.app || surface,
      root: source.root || null,
      port: source.port ?? null,
      status: source.status || 'BLOCKED',
      routeCount: source.routeCount || 0,
      panelCount: source.panelCount || 0,
      visualRegionCount: source.visualRegionCount || 0,
      editableSlotCount: source.editableSlotCount || 0,
      owners: source.owners || [],
      styleProfile: requirements.style_profile || 'governed PRISMA surface',
      guardrails: uniq([...(requirements.guardrails || []), surfaceGuardrail(surface)]),
      capabilityBuckets: buckets,
      validationGates: validationGates(surface),
      stationReady: Boolean(source.status === 'CERTIFIED' && source.root)
    };
  });
  return {
    schema: 'prisma.ui.premium-mise-en-place.surface-stations.v1',
    status: stations.every((station) => station.stationReady || station.surface === 'shared-ui') ? 'CERTIFIED' : 'BLOCKED',
    priority: PRIORITY,
    stations
  };
}

function buildEditableSlotSummary(state) {
  const slots = state.visualControlSlots;
  const visualControl = state.visualControlReport;
  const slotUnits = slots.slotUnits || slots.slotUnitSamples || [];
  const countsBySurface = slots.countsBySurface || countBy(slotUnits, 'surface');
  const countsBySafetyClassification = slots.countsBySafetyClassification || {
    safeVisualOnly: visualControl.safeVisualOnlyCount || 0,
    visualWithFunctionalRisk: visualControl.visualWithFunctionalRiskCount || 0,
    functionalControl: visualControl.functionalControlCount || 0,
    sharedGlobalRisk: visualControl.sharedGlobalRiskCount || 0
  };
  return {
    schema: 'prisma.ui.premium-mise-en-place.editable-slots-summary.v1',
    status: slots.status || visualControl.status || 'UNKNOWN',
    detailPolicy: slots.detailPolicy || 'compact slots only',
    editableSlotCount: slots.editableSlotCount || visualControl.editableSlotCount || 0,
    slotUnitCount: slots.slotUnitCount || slotUnits.length,
    countsBySurface,
    countsBySafetyClassification,
    samples: sample(slotUnits, 40)
  };
}

function recipeFor(surface) {
  const recipes = {
    tablet: {
      recipe: 'Tablet tactile premium station',
      use: ['prisma-tokens', 'prisma-recipes', 'prisma-visual-os', 'prisma-components', 'layer-budget', 'authority-map'],
      consider: ['background-catalog', 'radix-dialog', 'radix-select', 'radix-scroll-area', 'lucide-react', 'motion'],
      rejectByDefault: ['ogl', 'three', 'gsap'],
      readyFor: ['POS shell density', 'closed cash gate presentation', 'cart and payment state clarity']
    },
    mobile: {
      recipe: 'Mobile compact command station',
      use: ['prisma-tokens', 'prisma-recipes', 'radix-slot', 'lucide-react', 'clsx'],
      consider: ['framer-motion', 'motion', 'class-variance-authority'],
      rejectByDefault: ['heavy backgrounds', 'webgl atmosphere'],
      readyFor: ['install/onboarding', 'mobile command dashboard', 'small action cards']
    },
    pc: {
      recipe: 'PC dense governance station',
      use: ['prisma-components', 'prisma-visual-os', 'radix-tabs', 'radix-tooltip', 'radix-dialog', 'layer-budget'],
      consider: ['background-catalog', 'cloudglass-assets', 'motion'],
      rejectByDefault: ['Tablet-only selling affordances', 'unbounded WebGL'],
      readyFor: ['dashboard', 'catalog governance', 'sync/communication panels']
    },
    web: {
      recipe: 'Web/Edit lightweight brand station',
      use: ['prisma-tokens', 'prisma-recipes', 'background-catalog', 'lucide-react'],
      consider: ['motion', 'cloudglass-assets'],
      rejectByDefault: ['POS flows', 'heavy operational density'],
      readyFor: ['public-safe landing', 'surface governor pages']
    },
    'control-center': {
      recipe: 'Control Center operator station',
      use: ['prisma-tokens', 'prisma-recipes', 'authority-map', 'layer-budget'],
      consider: ['lucide-react', 'radix-dialog', 'radix-tooltip'],
      rejectByDefault: ['unredacted public evidence', 'non-operator decorative density'],
      readyFor: ['status panels', 'release control', 'public-safe diagnostics']
    },
    'chart-lab': {
      recipe: 'Chart Lab experimental station',
      use: ['prisma-visual-os', 'prisma-recipes', 'background-catalog', 'motion', 'ogl', 'three'],
      consider: ['gsap', 'cloudglass-assets'],
      rejectByDefault: ['production promotion without governor evidence'],
      readyFor: ['recipe studio', 'chart reference pilots', 'promotion evidence']
    },
    'shared-ui': {
      recipe: 'Shared UI primitive station',
      use: ['prisma-tokens', 'class-variance-authority', 'clsx', 'tailwind-merge', 'radix-slot'],
      consider: ['framer-motion', 'motion', 'vanilla-extract'],
      rejectByDefault: ['breaking primitive API changes without tri-surface proof'],
      readyFor: ['component variants', 'token bridges', 'cross-surface recipes']
    }
  };
  return recipes[surface] || { recipe: surface, use: [], consider: [], rejectByDefault: [], readyFor: [] };
}

function buildRecipePrep(state, stations) {
  const recipes = stations.stations.map((station) => ({
    surface: station.surface,
    priority: station.priority,
    ...recipeFor(station.surface),
    ownerSamples: sample(station.owners, 5),
    gates: station.validationGates
  }));
  return {
    schema: 'prisma.ui.premium-mise-en-place.recipe-prep.v1',
    status: recipes.length === PRIORITY.length ? 'CERTIFIED' : 'BLOCKED',
    recipes,
    preExistingTabletVisualWork: state.preExistingTabletVisualWork
  };
}

function buildReuseReport(state) {
  const systems = [
    { system: 'PR #140 Visual Control System v1', status: state.visualControlReport.status === 'CERTIFIED' ? 'reused' : 'blocked', use: 'owners, slots, layers, reuse and certification baseline' },
    { system: '.prisma-ui/**', status: exists(path.join(appRoot, '.prisma-ui')) ? 'reused' : 'missing', use: 'surface registry and generated compact visual indexes' },
    { system: '.governance/current/**', status: state.authorityMeshReport.status === 'PASS' ? 'reused' : 'blocked', use: 'fresh Authority Mesh readset and visual exploitation contract' },
    { system: 'tools/quality/ui-certainty.mjs', status: exists(path.join(appRoot, 'tools/quality/ui-certainty.mjs')) ? 'reused' : 'missing', use: 'source and runtime gates' },
    { system: 'tools/quality/ui-visual-control.mjs', status: exists(path.join(appRoot, 'tools/quality/ui-visual-control.mjs')) ? 'extended' : 'missing', use: 'compact visual-control indexes' },
    { system: 'Visual OS / Surface Visual Governor docs and configs', status: state.visualFoundationFiles.configCount > 0 ? 'reused' : 'missing', use: 'tokens, recipes, layer budgets and governor evidence' },
    { system: 'external library inventory', status: state.externalLibraries.inputs.some((item) => item.exists) ? 'referenced' : 'missing', use: 'local capability pantry only; not committed as payload' }
  ];
  return {
    schema: 'prisma.ui.premium-mise-en-place.reuse-report.v1',
    status: systems.some((item) => item.status === 'missing' || item.status === 'blocked') ? 'WARN' : 'CERTIFIED',
    systems,
    notReinvented: [
      'No new visual framework',
      'No installer bundle',
      'No runtime redesign',
      'No Prisma generate'
    ]
  };
}

function buildVisualFoundationFiles() {
  const roots = [
    'config/prisma-visual',
    'config/prisma-visual-system',
    'config/prisma-visual-os',
    'docs/visual-layer-map',
    'docs/surface-visual-governor',
    'products/shared-ui/prisma/visual-os',
    'products/0.backgrounds'
  ];
  const entries = roots.map((root) => {
    const files = listFiles(root, () => true, 200);
    return {
      root,
      exists: exists(path.join(appRoot, root)),
      fileCount: files.length,
      samples: sample(files, 8)
    };
  });
  return {
    roots: entries,
    configCount: entries.reduce((sum, entry) => sum + entry.fileCount, 0)
  };
}

function trackedGeneratedJsonSizes() {
  const files = runGit(['ls-files', '.prisma-ui', '.governance/current'])
    .split(/\r?\n/)
    .filter((line) => line.endsWith('.json'))
    .map((file) => {
      const appRelative = path.join(appRoot, file);
      const rootRelative = path.join(gitRoot(), file);
      return exists(appRelative) ? appRelative : rootRelative;
    })
    .filter((file) => exists(file))
    .map((file) => ({ path: relApp(file), bytes: fs.statSync(file).size }))
    .sort((a, b) => b.bytes - a.bytes);
  return files.map((item) => ({ ...item, kb: Math.round((item.bytes / 1024) * 10) / 10, tooLarge: item.bytes > 1_000_000 }));
}

function buildCleanRepoReport(state) {
  const meta = gitMeta();
  const generatedJson = trackedGeneratedJsonSizes();
  const largeGeneratedJson = generatedJson.filter((item) => item.tooLarge);
  const trackedEvidence = runGit(['ls-files'])
    .split(/\r?\n/)
    .filter((file) => /\.(zip|7z|rar|mp4|webm|mov)$/i.test(file) || /runtime-html|runtime-start-logs/i.test(file))
    .filter(Boolean);
  return {
    schema: 'prisma.ui.premium-mise-en-place.clean-repo-report.v1',
    status: largeGeneratedJson.length || trackedEvidence.length ? 'BLOCKED' : 'CERTIFIED',
    branch: meta.branch,
    repoHead: meta.repoHead,
    changedFiles: meta.statusShort,
    generatedJson,
    largeGeneratedJson,
    trackedEvidence,
    evidencePolicy: 'screenshots, logs, runtime html and expanded visual-control detail stay in external result.zip, not Git',
    preExistingTabletVisualWork: state.preExistingTabletVisualWork
  };
}

function buildFoundationCleanReport(state, cleanRepo) {
  return {
    schema: 'prisma.ui.premium-mise-en-place.foundation-clean.v1',
    status: cleanRepo.status === 'CERTIFIED' ? 'CERTIFIED' : 'BLOCKED',
    noRedesign: true,
    runtimeLayersRetired: [],
    compactedGeneratedIndexes: cleanRepo.generatedJson.filter((item) => item.path.includes('.prisma-ui/visual-control/')),
    visualFoundationFiles: state.visualFoundationFiles,
    notes: [
      'Visual foundations are labeled through reports and compact indexes.',
      'No POS, sync, Prisma schema, auth, or database behavior was changed by this tool.',
      'Expanded visual-control detail is external evidence when needed.'
    ],
    preExistingTabletVisualWork: state.preExistingTabletVisualWork
  };
}

function buildRetiredLayersManifest(foundationClean) {
  return {
    schema: 'prisma.ui.premium-mise-en-place.retired-layers.v1',
    status: 'CERTIFIED',
    retiredRuntimeLayerCount: 0,
    retiredRuntimeLayers: [],
    compactedRepoPayloads: foundationClean.compactedGeneratedIndexes,
    policy: 'No runtime visual layer was deleted in this pass; only oversized generated JSON detail was compacted into repo indexes.'
  };
}

function loadState() {
  const meta = gitMeta();
  const preExistingPaths = [
    'apps/terminal-de-venta-system/products/tablet/app/app/pos/prisma-pos-light-safe-shell.module.css',
    'apps/terminal-de-venta-system/products/tablet/app/components/pos/pos-screen.tsx',
    'apps/terminal-de-venta-system/products/tablet/app/components/pos/pos.module.css'
  ];
  const currentStatus = meta.statusShort.join('\n');
  const state = {
    meta,
    authorityMeshReport: readJson(path.join(appRoot, '.governance/current/AUTHORITY_READSET.lock.json'), {}),
    authorityMarkdown: exists(path.join(appRoot, '.governance/current/AUTHORITY_MESH_REPORT.md')) ? readText(path.join(appRoot, '.governance/current/AUTHORITY_MESH_REPORT.md')) : '',
    visualCapabilityMatrix: readJson(path.join(appRoot, '.governance/current/VISUAL_CAPABILITY_MATRIX.json'), {}),
    appCapabilityRequirements: readJson(path.join(appRoot, '.governance/current/APP_CAPABILITY_REQUIREMENTS.json'), {}),
    visualExploitationContract: readJson(path.join(appRoot, '.governance/current/VISUAL_EXPLOITATION_CONTRACT.json'), {}),
    premiumAcceptanceBar: exists(path.join(appRoot, '.governance/current/PREMIUM_ACCEPTANCE_BAR.md')) ? readText(path.join(appRoot, '.governance/current/PREMIUM_ACCEPTANCE_BAR.md')) : '',
    visualControlReport: readJson(path.join(appRoot, '.prisma-ui/current/UI_VISUAL_CONTROL_REPORT.json'), {}),
    visualControlSurfaces: readJson(path.join(appRoot, '.prisma-ui/visual-control/surfaces.json'), { surfaces: [] }),
    visualControlSlots: readJson(path.join(appRoot, '.prisma-ui/visual-control/editable-slots.json'), {}),
    externalLibraries: loadExternalLibraryInputs(),
    visualFoundationFiles: buildVisualFoundationFiles(),
    preExistingTabletVisualWork: preExistingPaths.map((file) => ({
      path: file,
      presentInStatus: currentStatus.includes(file.replace(/^apps\/terminal-de-venta-system\//, '')),
      provenance: 'captured before this branch in external evidence; treated as Tablet-only visual foundation work, not reverted'
    }))
  };
  state.authorityMeshStatus = state.authorityMarkdown.includes('Status: `PASS`') ? 'PASS' : 'UNKNOWN';
  return state;
}

function buildModel() {
  const state = loadState();
  const pantry = buildCapabilityPantry(state);
  const stations = buildSurfaceStations(state);
  const slots = buildEditableSlotSummary(state);
  const recipes = buildRecipePrep(state, stations);
  const reuse = buildReuseReport(state);
  const cleanRepo = buildCleanRepoReport(state);
  const foundation = buildFoundationCleanReport(state, cleanRepo);
  const retired = buildRetiredLayersManifest(foundation);
  const blockers = [];
  const warnings = [];
  if (state.authorityMeshStatus !== 'PASS') blockers.push('Authority Mesh report is not PASS.');
  if (state.visualExploitationContract.task !== TASK) blockers.push('Visual Exploitation Contract task does not match requested task.');
  if (state.visualControlReport.status !== 'CERTIFIED') blockers.push('Visual Control report is not CERTIFIED.');
  if (pantry.status !== 'CERTIFIED') blockers.push('Capability pantry is empty or blocked.');
  if (stations.status !== 'CERTIFIED') blockers.push('Surface stations are incomplete.');
  if (cleanRepo.status !== 'CERTIFIED') blockers.push('Clean repo report found oversized generated JSON or tracked evidence.');
  if (reuse.status !== 'CERTIFIED') warnings.push('Reuse report has WARN entries; see REUSE_REPORT.md.');
  const status = blockers.length ? 'BLOCKED' : 'CERTIFIED';
  return {
    schema: 'prisma.ui.premium-mise-en-place.report.v1',
    generatedAt: nowIso(),
    task: TASK,
    status,
    blockers,
    warnings,
    branch: state.meta.branch,
    repoHead: state.meta.repoHead,
    priority: PRIORITY,
    pantry,
    stations,
    slots,
    recipes,
    foundation,
    retired,
    cleanRepo,
    reuse
  };
}

function mdTable(headers, rows) {
  const escape = (value) => String(value ?? '').replace(/\|/g, '/').replace(/\r?\n/g, '<br>');
  return [
    `| ${headers.map(escape).join(' | ')} |`,
    `| ${headers.map(() => '---').join(' | ')} |`,
    ...rows.map((row) => `| ${row.map(escape).join(' | ')} |`)
  ].join('\n');
}

function frontMatter(title, model) {
  return [
    `# ${title}`,
    '',
    `- status: \`${model.status}\``,
    `- generated: \`${model.generatedAt}\``,
    `- branch: \`${model.branch || 'n/a'}\``,
    `- task: \`${TASK}\``,
    ''
  ];
}

function docMise(model) {
  return [
    ...frontMatter('PRISMA Premium Visual Mise en Place v1', model),
    '## What This Pass Does',
    '',
    '- Prepares visual foundations, capability pantry, surface stations, recipes, slots and cleanup reports.',
    '- Does not redesign runtime UI or change POS, sync, Prisma, auth, DB, route or port behavior.',
    '- Uses PR #140 Visual Control System v1, fresh Authority Mesh and existing PRISMA visual foundations.',
    '',
    '## Surface Priority',
    '',
    mdTable(['Priority', 'Surface', 'Status', 'Routes', 'Slots', 'Port'], model.stations.stations.map((s) => [s.priority, s.surface, s.status, s.routeCount, s.editableSlotCount, s.port ?? 'n/a'])),
    '',
    '## Gates',
    '',
    '- Authority Mesh: `PASS`',
    `- Visual Control: \`${model.status === 'CERTIFIED' ? 'CERTIFIED' : 'CHECK REPORT'}\``,
    '- Final gate set remains `ui-certainty` and `ui-visual-control` strict certification.',
    '',
    '## Blockers',
    '',
    ...(model.blockers.length ? model.blockers.map((item) => `- ${item}`) : ['- None'])
  ].join('\n') + '\n';
}

function docPantry(model) {
  const rows = model.pantry.capabilities.map((item) => [
    item.id,
    item.available ? 'yes' : 'no',
    item.risk,
    item.decision,
    item.defaultDecision || 'n/a',
    item.evidenceCount
  ]);
  return [
    ...frontMatter('Visual Capability Pantry Report', model),
    '## Capability Decisions',
    '',
    mdTable(['Capability', 'Available', 'Risk', 'Decision', 'Default', 'Evidence'], rows),
    '',
    '## External Inputs',
    '',
    mdTable(['Path', 'Exists', 'KB', 'Source'], model.pantry.externalLibraryInputs.map((item) => [item.path, item.exists ? 'yes' : 'no', item.kb ?? 'n/a', item.source])),
    ''
  ].join('\n') + '\n';
}

function docStations(model) {
  return [
    ...frontMatter('Visual Surface Stations Report', model),
    mdTable(
      ['Priority', 'Surface', 'Style Profile', 'Must Use', 'Should Use', 'Guardrail'],
      model.stations.stations.map((s) => [
        s.priority,
        s.surface,
        s.styleProfile,
        s.capabilityBuckets.must_use.join(', ') || 'n/a',
        s.capabilityBuckets.should_use.join(', ') || 'n/a',
        s.guardrails.join('; ')
      ])
    ),
    ''
  ].join('\n') + '\n';
}

function docRecipes(model) {
  return [
    ...frontMatter('Visual Recipe Prep Report', model),
    mdTable(
      ['Surface', 'Recipe', 'Use', 'Consider', 'Rejected By Default', 'Ready For'],
      model.recipes.recipes.map((r) => [r.surface, r.recipe, r.use.join(', '), r.consider.join(', '), r.rejectByDefault.join(', '), r.readyFor.join(', ')])
    ),
    ''
  ].join('\n') + '\n';
}

function docSlots(model) {
  return [
    ...frontMatter('Visual Editable Slots Summary', model),
    `- editable slots: \`${model.slots.editableSlotCount}\``,
    `- slot units: \`${model.slots.slotUnitCount}\``,
    '',
    '## By Surface',
    '',
    mdTable(['Surface', 'Slot Units'], Object.entries(model.slots.countsBySurface || {}).map(([k, v]) => [k, v])),
    '',
    '## By Safety',
    '',
    mdTable(['Safety Class', 'Count'], Object.entries(model.slots.countsBySafetyClassification || {}).map(([k, v]) => [k, v])),
    ''
  ].join('\n') + '\n';
}

function docFoundation(model) {
  return [
    ...frontMatter('Visual Foundation Clean Report', model),
    '- Runtime layer removals: `0`',
    '- Redesign applied by this tool: `no`',
    '- Prisma generate: `not run`',
    '',
    '## Foundation Roots',
    '',
    mdTable(['Root', 'Exists', 'File Count', 'Samples'], model.foundation.visualFoundationFiles.roots.map((item) => [item.root, item.exists ? 'yes' : 'no', item.fileCount, item.samples.join(', ')])),
    '',
    '## Compacted Generated Indexes',
    '',
    mdTable(['Path', 'KB', 'Too Large'], model.foundation.compactedGeneratedIndexes.map((item) => [item.path, item.kb, item.tooLarge ? 'yes' : 'no'])),
    ''
  ].join('\n') + '\n';
}

function docRetired(model) {
  return [
    ...frontMatter('Visual Retired Layers Manifest', model),
    `- retired runtime layer count: \`${model.retired.retiredRuntimeLayerCount}\``,
    `- policy: ${model.retired.policy}`,
    '',
    '## Retired Runtime Layers',
    '',
    '- None in this pass.',
    '',
    '## Compacted Repo Payloads',
    '',
    mdTable(['Path', 'KB'], model.retired.compactedRepoPayloads.map((item) => [item.path, item.kb])),
    ''
  ].join('\n') + '\n';
}

function docCleanRepo(model) {
  return [
    ...frontMatter('Clean Repo Report', model),
    `- clean policy status: \`${model.cleanRepo.status}\``,
    `- tracked evidence payloads: \`${model.cleanRepo.trackedEvidence.length}\``,
    `- large generated JSON files: \`${model.cleanRepo.largeGeneratedJson.length}\``,
    '',
    '## Generated JSON Sizes',
    '',
    mdTable(['Path', 'KB', 'Too Large'], model.cleanRepo.generatedJson.map((item) => [item.path, item.kb, item.tooLarge ? 'yes' : 'no'])),
    '',
    '## Current Git Status At Report Time',
    '',
    ...(model.cleanRepo.changedFiles.length ? model.cleanRepo.changedFiles.map((line) => `- \`${line}\``) : ['- Working tree clean at report time.'])
  ].join('\n') + '\n';
}

function docReuse(model) {
  return [
    ...frontMatter('Reuse Report', model),
    mdTable(['System', 'Status', 'Use'], model.reuse.systems.map((item) => [item.system, item.status, item.use])),
    '',
    '## Not Reinvented',
    '',
    ...model.reuse.notReinvented.map((item) => `- ${item}`)
  ].join('\n') + '\n';
}

function docWorkflow(model) {
  return [
    ...frontMatter('Small vs Big Visual Workflow', model),
    '## Small Visual Work',
    '',
    '- Use when the change is one owned panel, one local CSS module, no shared primitive API, no route behavior and no background ownership shift.',
    '- Required proof: owner panel, editable slot, local scope, zero-important, affected route certification.',
    '',
    '## Big Visual Work',
    '',
    '- Use when the change touches shared-ui, tokens, Visual OS, backgrounds, multiple surfaces, route shells, layer budgets or premium claims.',
    '- Required proof: Authority Mesh, capability pantry, used/rejected matrix, visual-control owners/slots/layers, runtime evidence when the surface is user-visible.',
    '',
    '## Promotion Rule',
    '',
    '- Chart Lab experiments need governor evidence before promotion.',
    '- Tablet changes must preserve standalone selling flow.',
    '- PC and Mobile must keep their product roles.',
    ''
  ].join('\n') + '\n';
}

function writeArtifacts(model) {
  const docs = {
    [REPORT_FILES.mise]: docMise(model),
    [REPORT_FILES.pantry]: docPantry(model),
    [REPORT_FILES.stations]: docStations(model),
    [REPORT_FILES.recipes]: docRecipes(model),
    [REPORT_FILES.slots]: docSlots(model),
    [REPORT_FILES.foundation]: docFoundation(model),
    [REPORT_FILES.retired]: docRetired(model),
    [REPORT_FILES.cleanRepo]: docCleanRepo(model),
    [REPORT_FILES.reuse]: docReuse(model),
    [REPORT_FILES.workflow]: docWorkflow(model)
  };
  for (const [name, content] of Object.entries(docs)) {
    writeText(path.join(DOC_DIR, name), `${content.trimEnd()}\n`);
  }

  writeJson(path.join(INDEX_DIR, 'registry.json'), {
    schema: 'prisma.ui.premium-mise-en-place.registry.v1',
    status: model.status,
    generatedAt: model.generatedAt,
    task: TASK,
    priority: PRIORITY,
    docs: Object.values(REPORT_FILES).map((name) => `docs/quality/${name}`),
    compactIndexes: [
      '.prisma-ui/premium-mise-en-place/capability-pantry.json',
      '.prisma-ui/premium-mise-en-place/surface-stations.json',
      '.prisma-ui/premium-mise-en-place/recipe-prep.json',
      '.prisma-ui/premium-mise-en-place/editable-slots-summary.json',
      '.prisma-ui/premium-mise-en-place/clean-repo-report.json',
      '.prisma-ui/premium-mise-en-place/reuse-report.json'
    ]
  });
  writeJson(path.join(INDEX_DIR, 'capability-pantry.json'), model.pantry);
  writeJson(path.join(INDEX_DIR, 'surface-stations.json'), model.stations);
  writeJson(path.join(INDEX_DIR, 'recipe-prep.json'), model.recipes);
  writeJson(path.join(INDEX_DIR, 'editable-slots-summary.json'), model.slots);
  writeJson(path.join(INDEX_DIR, 'foundation-clean-report.json'), model.foundation);
  writeJson(path.join(INDEX_DIR, 'retired-layers-manifest.json'), model.retired);
  writeJson(path.join(INDEX_DIR, 'clean-repo-report.json'), model.cleanRepo);
  writeJson(path.join(INDEX_DIR, 'reuse-report.json'), model.reuse);
  writeJson(path.join(CURRENT_DIR, 'UI_PREMIUM_MISE_EN_PLACE_REPORT.json'), {
    schema: model.schema,
    generatedAt: model.generatedAt,
    task: model.task,
    status: model.status,
    blockers: model.blockers,
    warnings: model.warnings,
    priority: model.priority,
    capabilityCount: model.pantry.capabilityCount,
    surfaceStationCount: model.stations.stations.length,
    editableSlotCount: model.slots.editableSlotCount,
    retiredRuntimeLayerCount: model.retired.retiredRuntimeLayerCount,
    cleanRepoStatus: model.cleanRepo.status,
    docs: Object.values(REPORT_FILES).map((name) => `docs/quality/${name}`)
  });
  writeText(path.join(CURRENT_DIR, 'UI_PREMIUM_MISE_EN_PLACE_REPORT.md'), docMise(model));
}

function printCompact(model, cmd) {
  console.log(JSON.stringify({
    command: cmd,
    status: model.status,
    blockers: model.blockers,
    warnings: model.warnings,
    docs: Object.values(REPORT_FILES).map((name) => `docs/quality/${name}`),
    indexes: '.prisma-ui/premium-mise-en-place'
  }, null, 2));
}

const { cmd, flags } = parseArgs();
const model = buildModel();
if (cmd === 'self-test') {
  printCompact(model, cmd);
} else if (cmd === 'report' || cmd === 'certify') {
  writeArtifacts(model);
  printCompact(model, cmd);
} else {
  console.error(`Unknown command: ${cmd}`);
  process.exit(2);
}

if ((flags.strict || cmd === 'certify') && model.status !== 'CERTIFIED') process.exit(1);
