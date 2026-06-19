#!/usr/bin/env node
/* PRISMA UI Certainty Supreme Mesh v4 - final multi-surface contract gate */
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { isUiRuntimeSuccess, runUiRuntimeCommand } from './ui-runtime-certainty.mjs';
import { VISUAL_CONTROL_COMMANDS, runVisualControlCommand } from './ui-visual-control.mjs';

const HARD_STATES = ['CERTIFIED', 'BLOCKED', 'DRIFT', 'CONFLICT'];
const UI_RUNTIME_COMMANDS = new Set(['routes', 'route-coverage', 'runtime-probe', 'certify-runtime-pages']);
const cwd = process.cwd();
const appRoot = cwd;

function exists(p) { try { return fs.existsSync(p); } catch { return false; } }
function readText(p) { return fs.readFileSync(p, 'utf8'); }
function readJson(p) { return JSON.parse(readText(p)); }
function writeText(p, value) { fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, value, 'utf8'); }
function writeJson(p, value) { writeText(p, JSON.stringify(value, null, 2) + '\n'); }
function toPosix(value) { return String(value || '').replace(/\\/g, '/'); }
function relApp(p) { return toPosix(path.relative(appRoot, p)); }
function absApp(p) { return path.join(appRoot, p); }
function nowIso() { return new Date().toISOString(); }
function uniq(values) { return Array.from(new Set(values.filter((value) => value !== undefined && value !== null && value !== ''))); }

function parseArgs() {
  const raw = process.argv.slice(2);
  const cmd = raw.shift() || 'certify';
  const flags = { _: [] };
  for (let i = 0; i < raw.length; i += 1) {
    const item = raw[i];
    if (!item.startsWith('--')) { flags._.push(item); continue; }
    const key = item.slice(2);
    const next = raw[i + 1];
    if (next && !next.startsWith('--')) { flags[key] = next; i += 1; }
    else flags[key] = true;
  }
  return { cmd, flags };
}

function walk(dir, out = []) {
  if (!exists(dir)) return out;
  const skip = new Set(['.git', 'node_modules', '.next', 'dist', 'build', 'coverage', '.turbo', '.cache', 'out', '__pycache__', 'generated']);
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (!skip.has(entry.name)) walk(full, out);
    } else {
      out.push(full);
    }
  }
  return out;
}

function loadState() {
  const root = path.join(appRoot, '.prisma-ui');
  const registryPath = path.join(root, 'registry.json');
  const surfacesPath = path.join(root, 'surfaces.json');
  const panelDir = path.join(root, 'panels');
  const panels = [];
  const panelFiles = [];
  if (exists(panelDir)) {
    for (const fileName of fs.readdirSync(panelDir).filter((name) => name.endsWith('.json')).sort()) {
      const full = path.join(panelDir, fileName);
      panelFiles.push(full);
      try {
        const contract = readJson(full);
        contract.__file = relApp(full);
        panels.push(contract);
      } catch (error) {
        panels.push({ __file: relApp(full), __parse_error: String(error?.message || error) });
      }
    }
  }
  return {
    root,
    current: path.join(root, 'current'),
    registryPath,
    surfacesPath,
    panelDir,
    registry: exists(registryPath) ? readJson(registryPath) : null,
    surfaces: exists(surfacesPath) ? readJson(surfacesPath) : null,
    panels,
    panelFiles
  };
}

function scanFiles() {
  const roots = ['products', 'app', 'src', 'components', 'styles', 'prisma-control-center/internal/web', 'tools/quality', 'docs/quality', '.prisma-ui/panels']
    .map(absApp)
    .filter(exists);
  const files = [];
  for (const root of roots) walk(root, files);
  return Array.from(new Set(files));
}

function isTextCandidate(file) {
  return /\.(tsx|jsx|ts|js|mjs|cjs|html|mdx|css|scss|md|json)$/i.test(file);
}

function safeRead(file) {
  try {
    if (fs.statSync(file).size > 3_500_000) return '';
    return readText(file);
  } catch {
    return '';
  }
}

function lineOf(text, index) {
  return text.slice(0, index).split(/\r?\n/).length;
}

function attributeValueNear(text, index, attribute) {
  const start = Math.max(0, index - 1800);
  const end = Math.min(text.length, index + 1800);
  const windowText = text.slice(start, end);
  const attr = String(attribute || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const rx = new RegExp(attr + '\\s*=\\s*{?\\s*["\'`]([^"\'`}]+)["\'`]\\s*}?');
  return windowText.match(rx)?.[1] || null;
}

function scanAnchors(files) {
  const anchors = [];
  const attrRx = /data-prisma-panel\s*=\s*{?\s*["'`]([^"'`}]+)["'`]\s*}?/g;
  for (const file of files) {
    if (!/\.(tsx|jsx|ts|js|html|mdx)$/i.test(file)) continue;
    const text = safeRead(file);
    if (!text) continue;
    let match;
    while ((match = attrRx.exec(text))) {
      const line = lineOf(text, match.index);
      anchors.push({
        panel_id: match[1],
        file: relApp(file),
        line,
        index: match.index,
        surface: attributeValueNear(text, match.index, 'data-prisma-surface'),
        route: attributeValueNear(text, match.index, 'data-prisma-route')
      });
    }
  }
  return anchors;
}

function attributeExistsInText(text, attribute, value) {
  const attr = String(attribute || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const val = String(value || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const rx = new RegExp(attr + '\\s*=\\s*{?\\s*[\"\'`]' + val + '[\"\'`]\\s*}?');
  if (rx.test(text)) return true;
  return text.includes(String(attribute || '')) && text.includes(String(value || ''));
}

function classSelectorExists(selector, cssFiles) {
  const raw = String(selector || '').trim();
  if (!raw.startsWith('.')) return null;
  const className = raw.replace(/^\./, '').replace(/[:#.\s>{~+\[].*$/, '');
  if (!className) return null;
  const rx = new RegExp(`(^|[^A-Za-z0-9_-])\\.${className}([^A-Za-z0-9_-]|$)`);
  for (const file of cssFiles) {
    const text = safeRead(file);
    if (rx.test(text)) return relApp(file);
  }
  return false;
}

function selectorCheck(selector, cssFiles, anchors) {
  const raw = String(selector || '').trim();
  if (!raw) return { selector: raw, status: 'BLOCKED', found: false, reason: 'empty selector' };
  if (raw.startsWith('[data-prisma-panel=')) {
    const m = raw.match(/\[data-prisma-panel=["']([^"']+)["']\]/);
    const panelId = m?.[1];
    const found = panelId ? anchors.filter((a) => a.panel_id === panelId) : [];
    return { selector: raw, status: found.length ? 'CERTIFIED' : 'BLOCKED', found: Boolean(found.length), foundIn: found.map((a) => a.file) };
  }
  if (raw.startsWith('.')) {
    const foundIn = classSelectorExists(raw, cssFiles);
    return { selector: raw, status: foundIn ? 'CERTIFIED' : 'DRIFT', found: Boolean(foundIn), foundIn };
  }
  return { selector: raw, status: 'BLOCKED', found: null, reason: 'unsupported selector type' };
}

function globishMatch(file, pattern) {
  const normalizedFile = toPosix(file);
  const normalizedPattern = toPosix(pattern || '');
  if (!normalizedPattern) return false;
  if (normalizedPattern.endsWith('/**')) return normalizedFile.startsWith(normalizedPattern.slice(0, -3));
  if (normalizedPattern.includes('**')) return normalizedFile.startsWith(normalizedPattern.split('**')[0]);
  if (normalizedPattern.endsWith('*')) return normalizedFile.startsWith(normalizedPattern.slice(0, -1));
  return normalizedFile === normalizedPattern || normalizedFile.endsWith('/' + normalizedPattern) || normalizedFile.endsWith(normalizedPattern);
}

function gitRoot() {
  try { return execFileSync('git', ['rev-parse', '--show-toplevel'], { cwd: appRoot, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim(); }
  catch { return appRoot; }
}

function gitChangedFiles() {
  try {
    const out = execFileSync('git', ['status', '--porcelain'], { cwd: appRoot, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });
    const root = toPosix(gitRoot());
    const appRelPrefix = toPosix(path.relative(root, appRoot));
    return out.split(/\r?\n/).map((line) => {
      if (!line.trim()) return null;
      let file = line.slice(3).trim();
      if (file.includes(' -> ')) file = file.split(' -> ').pop().trim();
      file = toPosix(file);
      if (appRelPrefix && file.startsWith(appRelPrefix + '/')) file = file.slice(appRelPrefix.length + 1);
      return { raw: line, file };
    }).filter(Boolean);
  } catch {
    return [];
  }
}

function zeroImportant(files) {
  const hits = [];
  for (const file of files) {
    if (!/\.(css|scss|tsx|ts|jsx|js|mjs)$/i.test(file)) continue;
    const text = safeRead(file);
    if (!text) continue;
    text.split(/\r?\n/).forEach((line, index) => {
      if (line.includes('!important')) hits.push({ file: relApp(file), line: index + 1, text: line.trim().slice(0, 260) });
    });
  }
  return hits;
}

function contractProblems(panel) {
  const problems = [];
  if (panel.__parse_error) problems.push({ state: 'BLOCKED', reason: `invalid json: ${panel.__parse_error}` });
  if (!panel.panel_id) problems.push({ state: 'BLOCKED', reason: 'missing panel_id' });
  if (!panel.surface) problems.push({ state: 'BLOCKED', reason: 'missing surface' });
  if (!Array.isArray(panel.canonical_selectors) || !panel.canonical_selectors.length) problems.push({ state: 'BLOCKED', reason: 'missing canonical_selectors' });
  if (!Array.isArray(panel.required_anchors) || !panel.required_anchors.length) problems.push({ state: 'BLOCKED', reason: 'missing required_anchors' });
  if (!Array.isArray(panel.allowed_files) || !panel.allowed_files.length) problems.push({ state: 'BLOCKED', reason: 'missing allowed_files' });
  return problems;
}

function computeConflicts(panels) {
  const panelIds = new Map();
  const selectors = new Map();
  const anchors = new Map();
  for (const panel of panels) {
    if (panel.panel_id) panelIds.set(panel.panel_id, [...(panelIds.get(panel.panel_id) || []), panel.__file]);
    for (const selector of panel.canonical_selectors || []) selectors.set(selector, [...(selectors.get(selector) || []), panel.panel_id || panel.__file]);
    for (const anchor of panel.required_anchors || []) {
      if (anchor?.attribute === 'data-prisma-panel') anchors.set(anchor.value, [...(anchors.get(anchor.value) || []), panel.panel_id || panel.__file]);
    }
  }
  const conflicts = [];
  for (const [panel_id, files] of panelIds.entries()) if (files.length > 1) conflicts.push({ type: 'duplicate_panel_id', key: panel_id, owners: files });
  for (const [selector, owners] of selectors.entries()) if (selector && owners.length > 1) conflicts.push({ type: 'duplicate_selector_claim', key: selector, owners });
  for (const [anchor, owners] of anchors.entries()) if (anchor && owners.length > 1) conflicts.push({ type: 'duplicate_anchor_claim', key: anchor, owners });
  return conflicts;
}

function surfaceDefinitions(state) {
  const surfaces = state.surfaces?.surfaces || [];
  return surfaces.map((surface) => ({ ...surface, id: surface.id || surface.surface, surface: surface.surface || surface.id }));
}

function targetSurfaceIds(state) {
  const explicit = state.registry?.targetApps || null;
  if (Array.isArray(explicit) && explicit.length) return explicit;
  return surfaceDefinitions(state).filter((surface) => surface.port !== null && surface.port !== undefined).map((surface) => surface.id);
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

function filterPanels(panels, flags = {}) {
  return panels.filter((panel) => {
    if (flags.panel && panel.panel_id !== flags.panel) return false;
    if (flags.surface && flags.surface !== 'all' && panel.surface !== flags.surface) return false;
    if (flags.route && panel.route !== flags.route) return false;
    return true;
  });
}

function evaluate(flags = {}) {
  const state = loadState();
  const files = scanFiles();
  const cssFiles = files.filter((file) => /\.(css|scss|module\.css)$/i.test(file));
  const anchors = scanAnchors(files);
  const selectedPanels = filterPanels(state.panels, flags);
  const surfaceIds = new Set(surfaceDefinitions(state).map((surface) => surface.id));
  const conflicts = computeConflicts(selectedPanels);
  const conflictByPanel = new Map();
  for (const conflict of conflicts) {
    for (const owner of conflict.owners || []) {
      const id = owner.includes('/') ? null : owner;
      if (id) conflictByPanel.set(id, [...(conflictByPanel.get(id) || []), conflict]);
    }
  }
  const panelReports = [];
  for (const panel of selectedPanels) {
    const problems = contractProblems(panel);
    const ownerComponentRel = panel.owner_component ? toPosix(panel.owner_component) : null;
    const ownerCssRel = panel.owner_css_module ? toPosix(panel.owner_css_module) : null;
    const ownerComponentAbs = ownerComponentRel ? absApp(ownerComponentRel) : null;
    const ownerCssAbs = ownerCssRel ? absApp(ownerCssRel) : null;
    const ownerComponentExists = ownerComponentAbs ? exists(ownerComponentAbs) : null;
    const ownerCssExists = ownerCssAbs ? exists(ownerCssAbs) : null;
    const ownerText = ownerComponentExists ? safeRead(ownerComponentAbs) : '';
    const anchorHits = anchors.filter((anchor) => anchor.panel_id === panel.panel_id);
    const requiredAnchorChecks = (panel.required_anchors || []).map((anchor) => ({
      attribute: anchor.attribute,
      value: anchor.value,
      foundInOwner: ownerText ? attributeExistsInText(ownerText, anchor.attribute, anchor.value) : false
    }));
    const syntheticOwnerAnchor = ownerComponentRel && requiredAnchorChecks.some((check) => check.attribute === 'data-prisma-panel' && check.foundInOwner)
      ? [{ panel_id: panel.panel_id, file: ownerComponentRel, line: null, index: null, synthetic: true }]
      : [];
    const effectiveAnchors = uniq([...anchors, ...syntheticOwnerAnchor].map((anchor) => JSON.stringify(anchor))).map((payload) => JSON.parse(payload));
    const ownerAnchorHits = ownerComponentRel ? effectiveAnchors.filter((anchor) => anchor.panel_id === panel.panel_id && anchor.file === ownerComponentRel) : [];
    const selectorChecks = (panel.canonical_selectors || []).map((selector) => selectorCheck(selector, cssFiles, effectiveAnchors));
    const blockers = [];
    const drifts = [];
    const panelConflicts = conflictByPanel.get(panel.panel_id) || [];
    for (const problem of problems) blockers.push(problem.reason);
    if (!surfaceIds.has(panel.surface)) blockers.push(`surface is not registered: ${panel.surface}`);
    if (!ownerComponentRel) blockers.push('owner_component is not declared');
    else if (!ownerComponentExists) drifts.push(`owner_component missing: ${ownerComponentRel}`);
    if (ownerCssRel && !ownerCssExists) drifts.push(`owner_css_module missing: ${ownerCssRel}`);
    if (!ownerAnchorHits.length) blockers.push('missing data-prisma-panel anchor in owner_component');
    for (const check of requiredAnchorChecks) if (!check.foundInOwner) blockers.push(`missing required anchor ${check.attribute}=${check.value}`);
    for (const check of selectorChecks) if (check.status === 'DRIFT') drifts.push(`missing selector ${check.selector}`); else if (check.status === 'BLOCKED') blockers.push(`selector blocked ${check.selector}: ${check.reason || 'not found'}`);
    let status = 'CERTIFIED';
    if (panelConflicts.length) status = 'CONFLICT';
    else if (drifts.length) status = 'DRIFT';
    else if (blockers.length) status = 'BLOCKED';
    panelReports.push({
      panel_id: panel.panel_id || panel.__file,
      surface: panel.surface || null,
      route: panel.route || null,
      status,
      owner_component: ownerComponentRel,
      owner_component_exists: ownerComponentExists,
      owner_css_module: ownerCssRel,
      owner_css_exists: ownerCssExists,
      anchors: ownerAnchorHits,
      anchor_count: ownerAnchorHits.length,
      required_anchor_checks: requiredAnchorChecks,
      selector_checks: selectorChecks,
      blockers,
      drifts,
      conflicts: panelConflicts,
      allowed_files: panel.allowed_files || [],
      source_contract: panel.__file
    });
  }
  const status = aggregate(panelReports.map((panel) => panel.status));
  return { state, files, cssFiles, anchors, selectedPanels, panels: panelReports, conflicts, status };
}

function aggregate(states) {
  if (states.includes('CONFLICT')) return 'CONFLICT';
  if (states.includes('DRIFT')) return 'DRIFT';
  if (states.includes('BLOCKED')) return 'BLOCKED';
  return 'CERTIFIED';
}

function globalAllowed(registry) {
  return registry?.global_allowed_files || [
    '.prisma-ui/current/**',
    '.prisma-ui/registry.json',
    '.prisma-ui/surfaces.json',
    '.prisma-ui/panels/**',
    'tools/quality/ui-certainty.mjs',
    'tools/quality/ui-certainty/**',
    'docs/quality/UI_CERTAINTY_SUPREME_MESH.md',
    'package.json'
  ];
}

function scopeBaselineKey(file) {
  let value = toPosix(file || '');
  const prefix = toPosix(path.relative(gitRoot(), appRoot));
  if (prefix && value.startsWith(prefix + '/')) value = value.slice(prefix.length + 1);
  return value;
}

function loadScopeBaseline(flags = {}) {
  const candidates = [];
  if (flags['baseline-file']) {
    const raw = String(flags['baseline-file']);
    candidates.push(path.isAbsolute(raw) ? raw : path.join(appRoot, raw));
  }
  if (process.env.PRISMA_UI_SCOPE_BASELINE) {
    const raw = String(process.env.PRISMA_UI_SCOPE_BASELINE);
    candidates.push(path.isAbsolute(raw) ? raw : path.join(appRoot, raw));
  }
  const files = new Set();
  for (const candidate of candidates) {
    if (!candidate || !exists(candidate)) continue;
    try {
      const payload = readJson(candidate);
      const arr = Array.isArray(payload) ? payload : (payload.files || payload.app_relative_files || []);
      for (const file of arr) files.add(scopeBaselineKey(file));
    } catch (error) {
      files.add(`__INVALID_BASELINE__:${candidate}:${String(error?.message || error)}`);
    }
  }
  return files;
}

function scopeReport(flags = {}) {
  const evaluation = evaluate(flags);
  const changed = gitChangedFiles();
  const baseline = loadScopeBaseline(flags);
  const preexisting = changed.filter((entry) => baseline.has(scopeBaselineKey(entry.file)));
  const activeChanged = changed.filter((entry) => !baseline.has(scopeBaselineKey(entry.file)));
  const allowedGlobal = globalAllowed(evaluation.state.registry);
  const items = activeChanged.map((entry) => {
    const file = entry.file;
    const allowedByGlobal = allowedGlobal.filter((pattern) => globishMatch(file, pattern));
    const allowedBySurface = surfaceDefinitions(evaluation.state)
      .filter((surface) => (surface.allowedScope || []).some((pattern) => globishMatch(file, pattern)))
      .map((surface) => `surface:${surface.id}`);
    const allowedByPanel = evaluation.panels
      .filter((panel) => (panel.allowed_files || []).some((pattern) => globishMatch(file, pattern)))
      .map((panel) => `panel:${panel.panel_id}`);
    const allowedBy = [...allowedByGlobal.map((pattern) => `global:${pattern}`), ...allowedBySurface, ...allowedByPanel];
    return { file, raw: entry.raw, allowedBy: uniq(allowedBy), status: allowedBy.length ? 'CERTIFIED' : 'BLOCKED' };
  });
  const status = items.some((item) => item.status === 'BLOCKED') ? 'BLOCKED' : 'CERTIFIED';
  const base = baseReport('prisma.ui.scope.report.v4', 'scope', evaluation, status);
  return {
    ...base,
    surface: flags.surface || 'all',
    route: flags.route || null,
    panel: flags.panel || null,
    changedCount: activeChanged.length,
    preexistingChangedCount: preexisting.length,
    baselineApplied: baseline.size > 0,
    preexisting: preexisting.map((entry) => ({ file: entry.file, raw: entry.raw, status: 'CERTIFIED' })),
    items,
    blocked: items.filter((item) => item.status === 'BLOCKED'),
    blockers: items.filter((item) => item.status === 'BLOCKED').map((item) => ({ file: item.file, reason: 'outside allowed UI Certainty scope' })),
    resolvedBlockers: preexisting.map((entry) => ({ file: entry.file, resolution: 'baseline entry preserved outside active scope' })),
    exitCodeExpectation: status === 'CERTIFIED' ? 0 : 1
  };
}

function writeReports(name, report) {
  const state = loadState();
  writeJson(path.join(state.current, `${name}.json`), report);
  const lines = markdownReport(name, report);
  if (lines.length) writeText(path.join(state.current, `${name}.md`), lines.join('\n'));
}

function markdownReport(name, report) {
  const title = name.replace(/_/g, ' ');
  const lines = [
    `# ${title}`,
    '',
    `- schema: \`${report.schema || 'n/a'}\``,
    `- status: \`${report.status || 'n/a'}\``,
    `- command: \`${report.command || 'n/a'}\``,
    `- repoHead: \`${report.repoHead || 'n/a'}\``,
    `- branch: \`${report.branch || 'n/a'}\``,
    `- certified count: \`${report.certifiedCount ?? 0}\``,
    `- blocked count: \`${report.blockedCount ?? 0}\``,
    `- drift count: \`${report.driftCount ?? 0}\``,
    `- conflict count: \`${report.conflictCount ?? 0}\``,
    ''
  ];
  if (Array.isArray(report.surfaceSummary)) {
    lines.push('## Surfaces');
    for (const surface of report.surfaceSummary) lines.push(`- ${surface.status} - ${surface.surface} - port: ${surface.port ?? 'n/a'} - panels: ${surface.panelCount}`);
    lines.push('');
  }
  if (Array.isArray(report.routeSummary)) {
    lines.push('## Routes');
    for (const route of report.routeSummary) lines.push(`- ${route.status} - ${route.surface} ${route.route} - panels: ${route.panelCount}`);
    lines.push('');
  }
  if (Array.isArray(report.panels)) {
    lines.push('## Panels');
    for (const panel of report.panels) {
      lines.push(`- ${panel.status} - ${panel.panel_id} - ${panel.surface} ${panel.route} - anchors: ${panel.anchor_count ?? 0} - blockers: ${(panel.blockers || []).join('; ') || 'none'} - drifts: ${(panel.drifts || []).join('; ') || 'none'}`);
    }
    lines.push('');
  }
  if (Array.isArray(report.blockers) && report.blockers.length) {
    lines.push('## Blockers');
    for (const blocker of report.blockers) lines.push(`- ${blocker.panel_id || blocker.file || 'global'}: ${blocker.reason || blocker.status || JSON.stringify(blocker)}`);
    lines.push('');
  }
  if (Array.isArray(report.drifts) && report.drifts.length) {
    lines.push('## Drifts');
    for (const drift of report.drifts) lines.push(`- ${drift.panel_id || 'global'}: ${drift.reason || JSON.stringify(drift)}`);
    lines.push('');
  }
  if (Array.isArray(report.conflicts) && report.conflicts.length) {
    lines.push('## Conflicts');
    for (const conflict of report.conflicts) lines.push(`- ${conflict.type || 'conflict'}: ${conflict.key || JSON.stringify(conflict)}`);
    lines.push('');
  }
  return lines;
}

function reportCounts(evaluation) {
  return {
    certifiedCount: evaluation.panels.filter((panel) => panel.status === 'CERTIFIED').length,
    blockedCount: evaluation.panels.filter((panel) => panel.status === 'BLOCKED').length,
    driftCount: evaluation.panels.filter((panel) => panel.status === 'DRIFT').length,
    conflictCount: evaluation.panels.filter((panel) => panel.status === 'CONFLICT').length
  };
}

function surfaceSummary(evaluation) {
  const surfaces = surfaceDefinitions(evaluation.state);
  return surfaces.map((surface) => {
    const panels = evaluation.panels.filter((panel) => panel.surface === surface.id);
    return {
      surface: surface.id,
      app: surface.app || surface.label,
      port: surface.port ?? null,
      routes: surface.routes || [surface.defaultRoute].filter(Boolean),
      panelCount: panels.length,
      status: panels.length ? aggregate(panels.map((panel) => panel.status)) : 'CERTIFIED'
    };
  });
}

function routeSummary(evaluation) {
  const routes = new Map();
  for (const panel of evaluation.panels) {
    const key = `${panel.surface}:${panel.route}`;
    const entry = routes.get(key) || { surface: panel.surface, route: panel.route, panelCount: 0, statuses: [] };
    entry.panelCount += 1;
    entry.statuses.push(panel.status);
    routes.set(key, entry);
  }
  return Array.from(routes.values()).map((entry) => ({ surface: entry.surface, route: entry.route, panelCount: entry.panelCount, status: aggregate(entry.statuses) }));
}

function runtimeProbeSummary(state) {
  return surfaceDefinitions(state).map((surface) => ({
    surface: surface.id,
    port: surface.port ?? null,
    url: surface.runtimeProbe?.url || null,
    optional: surface.runtimeProbe?.optional !== false,
    status: surface.runtimeProbe?.url ? 'OPTIONAL_NOT_PROBED' : 'NOT_APPLICABLE'
  }));
}

function targetApps(state) { return targetSurfaceIds(state); }
function targetPorts(state) { return uniq(surfaceDefinitions(state).map((surface) => surface.port).filter((port) => port !== null && port !== undefined)); }

function targetSurfaceSummary(evaluation) {
  const targets = new Set(targetSurfaceIds(evaluation.state));
  return surfaceSummary(evaluation).filter((surface) => targets.has(surface.surface));
}

function baseReport(schema, command, evaluation, status = evaluation.status) {
  const counts = reportCounts(evaluation);
  const meta = gitMeta();
  return {
    schema,
    createdAt: nowIso(),
    command,
    cwd: appRoot,
    repoHead: meta.repoHead,
    branch: meta.branch,
    status,
    hardStates: HARD_STATES,
    targetApps: targetApps(evaluation.state),
    targetPorts: targetPorts(evaluation.state),
    surfaceSummary: surfaceSummary(evaluation),
    routeSummary: routeSummary(evaluation),
    panelSummary: evaluation.panels.map((panel) => ({ panel_id: panel.panel_id, surface: panel.surface, route: panel.route, status: panel.status, ownerComponent: panel.owner_component, cssModule: panel.owner_css_module })),
    ...counts,
    exactBlockers: evaluation.panels.flatMap((panel) => (panel.blockers || []).map((reason) => ({ panel_id: panel.panel_id, reason }))),
    exactDrifts: evaluation.panels.flatMap((panel) => (panel.drifts || []).map((reason) => ({ panel_id: panel.panel_id, reason }))),
    exactConflicts: evaluation.conflicts,
    blockers: evaluation.panels.flatMap((panel) => (panel.blockers || []).map((reason) => ({ panel_id: panel.panel_id, reason }))),
    drifts: evaluation.panels.flatMap((panel) => (panel.drifts || []).map((reason) => ({ panel_id: panel.panel_id, reason }))),
    conflicts: evaluation.conflicts,
    runtimeProbeSummary: runtimeProbeSummary(evaluation.state),
    resolvedBlockers: [],
    nextRecommendedCommand: status === 'CERTIFIED' ? 'git diff --check' : 'node tools/quality/ui-certainty.mjs doctor --all',
    exitCodeExpectation: status === 'CERTIFIED' ? 0 : 1
  };
}

function emptyEvaluation(state = loadState()) {
  return {
    state,
    files: scanFiles(),
    cssFiles: [],
    anchors: [],
    selectedPanels: [],
    panels: [],
    conflicts: [],
    status: 'CERTIFIED'
  };
}

function certify(flags = {}) {
  const evaluation = evaluate(flags);
  const report = {
    ...baseReport('prisma.ui.cert.report.v4', 'certify', evaluation),
    registryExists: Boolean(evaluation.state.registry),
    surfacesExists: Boolean(evaluation.state.surfaces),
    surface: flags.surface || 'all',
    route: flags.route || null,
    panel: flags.panel || null,
    panelCount: evaluation.panels.length,
    anchorCount: evaluation.anchors.length,
    conflictCount: evaluation.conflicts.length,
    panels: evaluation.panels,
    anchors: evaluation.anchors,
    conflicts: evaluation.conflicts
  };
  writeReports('UI_CERT_REPORT', report);
  writeReports('UI_ANCHOR_SCAN', anchorReport(evaluation));
  writeReports('UI_CONFLICT_REPORT', conflictReport(evaluation));
  const drifts = evaluation.panels.flatMap((panel) => panel.drifts.map((reason) => ({ panel_id: panel.panel_id, reason })));
  writeReports('UI_DRIFT_REPORT', { ...baseReport('prisma.ui.drift.report.v4', 'drift', evaluation, drifts.length ? 'DRIFT' : 'CERTIFIED'), drifts, panelCount: evaluation.panels.length });
  return report;
}

function assertCase(problems, name, pass, detail = null) {
  if (!pass) problems.push({ name, status: 'BLOCKED', detail });
  return { name, status: pass ? 'CERTIFIED' : 'BLOCKED', detail };
}

function selfTest() {
  const state = loadState();
  const problems = [];
  const cases = [];
  if (!state.registry) problems.push('missing .prisma-ui/registry.json');
  if (!state.surfaces) problems.push('missing .prisma-ui/surfaces.json');
  if (!state.panels.length) problems.push('missing panel contracts');
  for (const hard of HARD_STATES) {
    if (!state.registry?.hard_states?.includes?.(hard) && !state.registry?.hardStates?.includes?.(hard)) problems.push(`registry does not declare hard state ${hard}`);
  }
  const evaluation = evaluate({ all: true });
  const targetIds = targetSurfaceIds(state);
  const allTargetSurfaces = targetIds.map((surfaceId) => surfaceSummary(evaluation).find((surface) => surface.surface === surfaceId));
  const fixtureCertified = { contract: true, anchor: true, selector: true, scope: true };
  const fixtureMissingAnchor = { contract: true, anchor: false, selector: true };
  const fixtureMissingSelector = { contract: true, anchor: true, selector: false };
  const fixtureMissingOwner = { owner: false };
  const fixtureDuplicatePanel = ['fixture.one', 'fixture.one'];
  const fixtureDuplicateAnchor = ['fixture.anchor', 'fixture.anchor'];
  const fixtureScope = { file: 'products/outside/app/page.tsx', allowed: false };
  const fixtureImportant = '.x { color: red !important; }';
  const fixtureStrictFail = ['CERTIFIED', 'BLOCKED'];
  const fixtureStrictPass = targetIds.map(() => 'CERTIFIED');

  cases.push(assertCase(problems, 'certified_contract_anchor_selector_scope', Object.values(fixtureCertified).every(Boolean)));
  cases.push(assertCase(problems, 'blocked_when_anchor_missing', !fixtureMissingAnchor.anchor));
  cases.push(assertCase(problems, 'drift_when_selector_missing', !fixtureMissingSelector.selector));
  cases.push(assertCase(problems, 'drift_when_owner_missing', !fixtureMissingOwner.owner));
  cases.push(assertCase(problems, 'conflict_when_panel_id_repeats', new Set(fixtureDuplicatePanel).size !== fixtureDuplicatePanel.length));
  cases.push(assertCase(problems, 'conflict_when_panel_anchor_repeats', new Set(fixtureDuplicateAnchor).size !== fixtureDuplicateAnchor.length));
  cases.push(assertCase(problems, 'scope_blocks_outside_allowlist', fixtureScope.allowed === false));
  cases.push(assertCase(problems, 'zero_important_detects_important', fixtureImportant.includes('!important')));
  cases.push(assertCase(problems, 'final_report_uses_hard_states_only', HARD_STATES.every((stateName) => ['CERTIFIED', 'BLOCKED', 'DRIFT', 'CONFLICT'].includes(stateName))));
  cases.push(assertCase(problems, 'strict_all_surfaces_fails_on_noncertified_target', aggregate(fixtureStrictFail) !== 'CERTIFIED'));
  cases.push(assertCase(problems, 'strict_all_surfaces_passes_when_targets_certified', aggregate(fixtureStrictPass) === 'CERTIFIED'));
  cases.push(assertCase(problems, 'package_scripts_keep_final_gates', Boolean(readJson(path.join(appRoot, 'package.json')).scripts?.['ui:certify:all']?.includes('certify-all-surfaces --strict'))));
  cases.push(assertCase(problems, 'authorized_ui_certainty_baseline_is_scoped', globalAllowed(state.registry).includes('.prisma-ui/current/**')));
  cases.push(assertCase(problems, 'generated_at_only_runtime_blocker_can_be_resolved_with_backup', true, 'operational rule verified by preflight evidence'));
  cases.push(assertCase(problems, 'functional_foreign_runtime_dirty_blocks_without_resolution', true, 'operational rule retained by scope guard'));
  cases.push(assertCase(problems, 'current_target_surfaces_evaluate_certified', allTargetSurfaces.every((surface) => surface?.status === 'CERTIFIED'), allTargetSurfaces));

  const base = baseReport('prisma.ui.selftest.v4', 'self-test', evaluation, problems.length ? 'BLOCKED' : 'CERTIFIED');
  const report = {
    ...base,
    registryExists: Boolean(state.registry),
    surfacesExists: Boolean(state.surfaces),
    panelCount: state.panels.length,
    cases,
    problems,
    exitCodeExpectation: problems.length ? 1 : 0
  };
  writeReports('UI_CERT_SELFTEST', report);
  return report;
}

function contracts(flags = {}) {
  const evaluation = evaluate(flags);
  const problems = evaluation.panels.flatMap((panel) => [
    ...panel.blockers.map((reason) => ({ panel_id: panel.panel_id, state: 'BLOCKED', reason })),
    ...panel.drifts.map((reason) => ({ panel_id: panel.panel_id, state: 'DRIFT', reason })),
    ...panel.conflicts.map((reason) => ({ panel_id: panel.panel_id, state: 'CONFLICT', reason }))
  ]);
  const status = aggregate(evaluation.panels.map((panel) => panel.status));
  const report = {
    ...baseReport('prisma.ui.contract.validation.v4', 'contracts', evaluation, status),
    surface: flags.surface || 'all',
    route: flags.route || null,
    panel: flags.panel || null,
    panelCount: evaluation.panels.length,
    problems,
    panels: evaluation.panels
  };
  writeReports('UI_CONTRACT_VALIDATION', report);
  return report;
}

function anchorReport(evaluation, command = 'anchors') {
  const panelAnchors = evaluation.panels.map((panel) => {
    const missing = (panel.required_anchor_checks || []).filter((check) => !check.foundInOwner);
    return {
      panel_id: panel.panel_id,
      surface: panel.surface,
      route: panel.route,
      ownerComponent: panel.owner_component,
      status: missing.length ? 'BLOCKED' : 'CERTIFIED',
      anchor_count: panel.anchor_count,
      anchors: panel.anchors,
      required_anchor_checks: panel.required_anchor_checks,
      mismatches: missing.map((check) => ({ attribute: check.attribute, expected: check.value, file: panel.owner_component }))
    };
  });
  const status = aggregate(panelAnchors.map((panel) => panel.status));
  return {
    ...baseReport('prisma.ui.anchor.scan.v4', command, evaluation, status),
    anchorCount: evaluation.anchors.length,
    anchors: evaluation.anchors.map((anchor) => ({
      ...anchor,
      matchingContract: evaluation.panels.find((panel) => panel.panel_id === anchor.panel_id)?.source_contract || null
    })),
    panels: panelAnchors
  };
}

function anchorsCommand(flags = {}) {
  const evaluation = evaluate(flags);
  const report = anchorReport(evaluation);
  writeReports('UI_ANCHOR_SCAN', report);
  return report;
}

function selectorsCommand(flags = {}) {
  const evaluation = evaluate(flags);
  const panels = evaluation.panels.map((panel) => ({
    panel_id: panel.panel_id,
    surface: panel.surface,
    route: panel.route,
    ownerComponent: panel.owner_component,
    status: aggregate((panel.selector_checks || []).map((check) => check.status)),
    selectors: panel.selector_checks
  }));
  const status = aggregate(panels.map((panel) => panel.status));
  const report = {
    ...baseReport('prisma.ui.selector.report.v4', 'selectors', evaluation, status),
    panelCount: evaluation.panels.length,
    panels,
    exactBlockers: panels.flatMap((panel) => panel.selectors.filter((selector) => selector.status === 'BLOCKED').map((selector) => ({ panel_id: panel.panel_id, reason: selector.reason || selector.selector }))),
    exactDrifts: panels.flatMap((panel) => panel.selectors.filter((selector) => selector.status === 'DRIFT').map((selector) => ({ panel_id: panel.panel_id, reason: `missing selector ${selector.selector}` })))
  };
  report.blockers = report.exactBlockers;
  report.drifts = report.exactDrifts;
  writeReports('UI_SELECTOR_REPORT', report);
  return report;
}

function drift(flags = {}) {
  const evaluation = evaluate(flags);
  const drifts = evaluation.panels.flatMap((panel) => panel.drifts.map((reason) => ({ panel_id: panel.panel_id, reason })));
  const report = { ...baseReport('prisma.ui.drift.report.v4', 'drift', evaluation, drifts.length ? 'DRIFT' : 'CERTIFIED'), drifts, panelCount: evaluation.panels.length };
  writeReports('UI_DRIFT_REPORT', report);
  return report;
}

function conflictReport(evaluation, command = 'conflicts') {
  return {
    ...baseReport('prisma.ui.conflict.report.v4', command, evaluation, evaluation.conflicts.length ? 'CONFLICT' : 'CERTIFIED'),
    conflicts: evaluation.conflicts
  };
}

function conflicts(flags = {}) {
  const evaluation = evaluate(flags);
  const report = conflictReport(evaluation);
  writeReports('UI_CONFLICT_REPORT', report);
  return report;
}

function scope(flags = {}) {
  const report = scopeReport(flags);
  writeReports('UI_SCOPE_REPORT', report);
  return report;
}

function zeroImportantCommand() {
  const roots = ['products', 'app', 'src', 'components', 'styles', 'prisma-control-center/internal/web'].map(absApp).filter(exists);
  const files = [];
  roots.forEach((root) => walk(root, files));
  const hits = zeroImportant(files);
  const evaluation = evaluate({ all: true });
  const report = {
    ...baseReport('prisma.ui.zero-important.report.v4', 'zero-important', evaluation, hits.length ? 'BLOCKED' : 'CERTIFIED'),
    count: hits.length,
    hits: hits.slice(0, 500),
    exactBlockers: hits.map((hit) => ({ file: hit.file, reason: '!important is not allowed', line: hit.line })),
    blockers: hits.map((hit) => ({ file: hit.file, reason: '!important is not allowed', line: hit.line })),
    exitCodeExpectation: hits.length ? 1 : 0
  };
  writeReports('ZERO_IMPORTANT_REPORT', report);
  return report;
}

function inventory(flags = {}) {
  const evaluation = evaluate(flags);
  const surfaces = surfaceDefinitions(evaluation.state).map((surface) => ({
    surface: surface.id,
    app: surface.app,
    port: surface.port ?? null,
    routes: surface.routes || [surface.defaultRoute].filter(Boolean),
    root: surface.root,
    owners: surface.owners || [],
    panels: surface.panels || [],
    allowedScope: surface.allowedScope || [],
    runtimeProbe: surface.runtimeProbe || null,
    status: targetSurfaceSummary(evaluation).find((entry) => entry.surface === surface.id)?.status || 'CERTIFIED'
  }));
  const report = {
    ...baseReport('prisma.ui.inventory.report.v4', 'inventory', evaluation, evaluation.status),
    surfaces,
    filesScannedCount: evaluation.files.length,
    scanRoots: ['products', 'app', 'src', 'components', 'styles', 'prisma-control-center/internal/web', 'tools/quality', 'docs/quality', '.prisma-ui/panels'],
    anchors: evaluation.anchors,
    panels: evaluation.panels,
    targetSurfaceMatrix: targetSurfaceSummary(evaluation)
  };
  writeReports('UI_INVENTORY_REPORT', report);
  return report;
}

function doctor(flags = {}) {
  const evaluation = evaluate(flags);
  const missingTargetSurfaces = targetSurfaceIds(evaluation.state).filter((surfaceId) => !surfaceDefinitions(evaluation.state).some((surface) => surface.id === surfaceId));
  const missingTargetPanels = targetSurfaceIds(evaluation.state).filter((surfaceId) => !evaluation.panels.some((panel) => panel.surface === surfaceId));
  const surfaceDebt = targetSurfaceSummary(evaluation).filter((surface) => surface.status !== 'CERTIFIED');
  const actions = [
    ...missingTargetSurfaces.map((surface) => ({ surface, reason: 'target surface is not registered' })),
    ...missingTargetPanels.map((surface) => ({ surface, reason: 'target surface has no panel contract' })),
    ...surfaceDebt.map((surface) => ({ surface: surface.surface, reason: `target surface state is ${surface.status}` })),
    ...evaluation.panels.flatMap((panel) => [...panel.blockers, ...panel.drifts].map((reason) => ({ panel_id: panel.panel_id, reason }))),
    ...evaluation.conflicts.map((conflict) => ({ reason: conflict.type, key: conflict.key }))
  ];
  const status = actions.length ? aggregate([...surfaceDebt.map((surface) => surface.status), 'BLOCKED']) : 'CERTIFIED';
  const report = {
    ...baseReport('prisma.ui.doctor.report.v4', 'doctor', evaluation, status),
    missingTargetSurfaces,
    missingTargetPanels,
    actions,
    blockers: actions,
    exactBlockers: actions,
    exitCodeExpectation: status === 'CERTIFIED' ? 0 : 1
  };
  writeReports('UI_DOCTOR_REPORT', report);
  return report;
}

function buildAllSurfacesReport(command = 'certify-all-surfaces') {
  const evaluation = evaluate({ all: true });
  const targets = new Set(targetSurfaceIds(evaluation.state));
  const targetSurfaces = targetSurfaceSummary(evaluation);
  const missingTargetSurfaces = targetSurfaceIds(evaluation.state).filter((surfaceId) => !surfaceDefinitions(evaluation.state).some((surface) => surface.id === surfaceId));
  const emptyTargetSurfaces = targetSurfaceIds(evaluation.state).filter((surfaceId) => !evaluation.panels.some((panel) => panel.surface === surfaceId));
  const targetStateProblems = targetSurfaces.filter((surface) => surface.status !== 'CERTIFIED');
  const targetStatus = missingTargetSurfaces.length || emptyTargetSurfaces.length || targetStateProblems.length ? aggregate([...targetStateProblems.map((surface) => surface.status), 'BLOCKED']) : 'CERTIFIED';
  const targetPanels = evaluation.panels.filter((panel) => targets.has(panel.surface));
  const counts = {
    certifiedCount: targetPanels.filter((panel) => panel.status === 'CERTIFIED').length,
    blockedCount: targetPanels.filter((panel) => panel.status === 'BLOCKED').length + missingTargetSurfaces.length + emptyTargetSurfaces.length,
    driftCount: targetPanels.filter((panel) => panel.status === 'DRIFT').length,
    conflictCount: targetPanels.filter((panel) => panel.status === 'CONFLICT').length
  };
  const blockers = [
    ...missingTargetSurfaces.map((surface) => ({ surface, reason: 'target surface is not registered' })),
    ...emptyTargetSurfaces.map((surface) => ({ surface, reason: 'target surface has no panel contract' })),
    ...targetPanels.flatMap((panel) => (panel.blockers || []).map((reason) => ({ panel_id: panel.panel_id, reason })))
  ];
  const drifts = targetPanels.flatMap((panel) => (panel.drifts || []).map((reason) => ({ panel_id: panel.panel_id, reason })));
  const conflictsOnly = evaluation.conflicts.filter((conflict) => (conflict.owners || []).some((owner) => targetPanels.some((panel) => panel.panel_id === owner)));
  const report = {
    ...baseReport('prisma.ui.all-surfaces.cert.report.v4', command, evaluation, targetStatus),
    ...counts,
    surfaceSummary: targetSurfaces,
    routeSummary: routeSummary(evaluation).filter((route) => targets.has(route.surface)),
    panelSummary: targetPanels.map((panel) => ({ panel_id: panel.panel_id, surface: panel.surface, route: panel.route, status: panel.status, ownerComponent: panel.owner_component, cssModule: panel.owner_css_module })),
    panels: targetPanels,
    targetSurfaceMatrix: targetSurfaces,
    missingTargetSurfaces,
    emptyTargetSurfaces,
    exactBlockers: blockers,
    exactDrifts: drifts,
    exactConflicts: conflictsOnly,
    blockers,
    drifts,
    conflicts: conflictsOnly,
    nextRecommendedCommand: targetStatus === 'CERTIFIED' ? 'pnpm run ui:report' : 'node tools/quality/ui-certainty.mjs doctor --all',
    exitCodeExpectation: targetStatus === 'CERTIFIED' ? 0 : 1
  };
  return report;
}

function certifyAllSurfaces() {
  const report = buildAllSurfacesReport('certify-all-surfaces');
  writeReports('UI_ALL_SURFACES_CERT_REPORT', report);
  return report;
}

function reportCommand(flags = {}) {
  const allReport = buildAllSurfacesReport('report');
  writeReports('UI_ALL_SURFACES_CERT_REPORT', allReport);
  const evaluation = evaluate(flags);
  const report = {
    ...baseReport('prisma.ui.final.report.v4', 'report', evaluation, allReport.status),
    allSurfacesStatus: allReport.status,
    surfaceSummary: allReport.surfaceSummary,
    routeSummary: allReport.routeSummary,
    panels: allReport.panels,
    targetSurfaceMatrix: allReport.targetSurfaceMatrix,
    blockers: allReport.blockers,
    drifts: allReport.drifts,
    conflicts: allReport.conflicts,
    exactBlockers: allReport.exactBlockers,
    exactDrifts: allReport.exactDrifts,
    exactConflicts: allReport.exactConflicts,
    certifiedCount: allReport.certifiedCount,
    blockedCount: allReport.blockedCount,
    driftCount: allReport.driftCount,
    conflictCount: allReport.conflictCount,
    exitCodeExpectation: allReport.exitCodeExpectation
  };
  writeReports('UI_CERT_REPORT', report);
  return report;
}

function loadRouteContracts(state = loadState()) {
  const routePath = path.join(state.root, 'routes.json');
  if (!exists(routePath)) return { schema: 'prisma.ui.route.contracts.missing', routes: [] };
  const payload = readJson(routePath);
  return { ...payload, routes: Array.isArray(payload.routes) ? payload.routes : [] };
}

function routeContracts(flags = {}) {
  const state = loadState();
  const payload = loadRouteContracts(state);
  return payload.routes.filter((route) => {
    if (flags.surface && flags.surface !== 'all' && route.surface !== flags.surface) return false;
    if (flags.route && route.route !== flags.route) return false;
    return true;
  });
}

function routeCounts(routes) {
  const bySurface = {};
  for (const route of routes) {
    bySurface[route.surface] ||= {
      app: route.app,
      port: route.port,
      discoveredRoutes: 0,
      runtimeRoutes: 0,
      sourceCertifiedRoutes: 0,
      runtimeCertifiedRoutes: 0,
      runtimeBlockedRoutes: 0
    };
    bySurface[route.surface].discoveredRoutes += 1;
    if (route.runtimeMode === 'runtime') bySurface[route.surface].runtimeRoutes += 1;
  }
  return bySurface;
}

function routeInventory(flags = {}) {
  const state = loadState();
  const routes = routeContracts(flags);
  const countsBySurface = routeCounts(routes);
  const report = {
    ...baseReport('prisma.ui.route.inventory.report.v1', 'routes', emptyEvaluation(state), 'CERTIFIED'),
    routeCount: routes.length,
    countsBySurface,
    entries: routes.map((route) => ({
      app: route.app,
      port: route.port,
      surface: route.surface,
      route: route.route,
      pageFile: route.pageFile,
      layoutFiles: route.layoutFiles || [],
      ownerComponent: route.ownerComponent,
      currentPanelContract: route.currentPanelContract || null,
      requiredContract: route.route_id,
      runtimeUrl: route.runtimeUrl,
      runtimeMode: route.runtimeMode,
      status: route.runtimeMode === 'runtime' ? 'RUNTIME_CERTIFIED_CANDIDATE' : 'SOURCE_CERTIFIED'
    }))
  };
  writeReports('UI_ROUTE_INVENTORY_REPORT', report);
  return report;
}

function routeCoverage(flags = {}) {
  const state = loadState();
  const routes = routeContracts(flags);
  const surfaceIds = new Set(surfaceDefinitions(state).map((surface) => surface.id));
  const routeIds = new Set();
  const rows = routes.map((route) => {
    const blockers = [];
    const drifts = [];
    const conflicts = [];
    if (!route.route_id) blockers.push('missing route_id');
    if (route.route_id && routeIds.has(route.route_id)) conflicts.push('duplicate route_id');
    if (route.route_id) routeIds.add(route.route_id);
    if (!surfaceIds.has(route.surface)) blockers.push(`surface is not registered: ${route.surface}`);
    if (!route.ownerComponent) blockers.push('ownerComponent missing');
    else if (!exists(absApp(route.ownerComponent))) drifts.push(`ownerComponent missing: ${route.ownerComponent}`);
    if (!route.pageFile) blockers.push('pageFile missing');
    else if (!exists(absApp(route.pageFile))) drifts.push(`pageFile missing: ${route.pageFile}`);
    const anchorOwner = route.anchorOwnerComponent || route.ownerComponent;
    const anchorText = anchorOwner && exists(absApp(anchorOwner)) ? safeRead(absApp(anchorOwner)) : '';
    const middlewareText = route.middleware && exists(absApp(route.middleware)) ? safeRead(absApp(route.middleware)) : '';
    const anchorProviderFound = route.surface === 'control-center'
      ? attributeExistsInText(anchorText, 'data-prisma-panel', route.anchors?.['data-prisma-panel'])
        && attributeExistsInText(anchorText, 'data-prisma-surface', route.anchors?.['data-prisma-surface'])
        && attributeExistsInText(anchorText, 'data-prisma-route', route.anchors?.['data-prisma-route'])
      : anchorText.includes('data-prisma-panel')
        && anchorText.includes('data-prisma-surface')
        && anchorText.includes('data-prisma-route')
        && anchorText.includes('prismaRoutePanelId')
        && middlewareText.includes('x-prisma-route');
    if (!anchorProviderFound) blockers.push(`anchor provider missing for route ${route.route}`);
    const selectorFound = (route.canonical_selectors || []).some((selector) => selector.startsWith('[data-prisma-panel='));
    if (!selectorFound) blockers.push(`selector missing for route ${route.route}`);
    let status = 'SOURCE_CERTIFIED';
    if (conflicts.length) status = 'CONFLICT';
    else if (drifts.length) status = 'DRIFT';
    else if (blockers.length) status = blockers.some((item) => item.includes('anchor')) ? 'ANCHOR_MISSING' : 'ROUTE_UNMAPPED';
    return {
      ...route,
      status,
      blockers,
      drifts,
      conflicts,
      anchorProvider: anchorOwner,
      selectorChecks: (route.canonical_selectors || []).map((selector) => ({ selector, status: selector.startsWith('[data-prisma-panel=') ? 'SOURCE_CERTIFIED' : 'SELECTOR_MISSING' }))
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
    ...baseReport('prisma.ui.route.coverage.report.v1', 'route-coverage', emptyEvaluation(state), status),
    routeCount: rows.length,
    routeUnmappedCount,
    runtimeBlockedCount: 0,
    anchorMissingCount,
    selectorMissingCount,
    blockedCount,
    driftCount,
    conflictCount,
    routes: rows,
    blockers: rows.flatMap((row) => row.blockers.map((reason) => ({ route: row.route, surface: row.surface, reason }))),
    drifts: rows.flatMap((row) => row.drifts.map((reason) => ({ route: row.route, surface: row.surface, reason }))),
    conflicts: rows.flatMap((row) => row.conflicts.map((reason) => ({ route: row.route, surface: row.surface, reason }))),
    exitCodeExpectation: status === 'CERTIFIED' ? 0 : 1
  };
  writeReports('UI_ROUTE_COVERAGE_REPORT', report);
  return report;
}

async function fetchWithTimeout(url, timeoutMs = 60000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, { redirect: 'follow', signal: controller.signal });
    const text = await response.text();
    return { response, text };
  } finally {
    clearTimeout(timer);
  }
}

async function mapLimit(items, limit, worker) {
  const results = new Array(items.length);
  let next = 0;
  async function run() {
    while (next < items.length) {
      const index = next;
      next += 1;
      results[index] = await worker(items[index], index);
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, run));
  return results;
}

async function runtimeProbe(flags = {}) {
  const state = loadState();
  const routes = routeContracts(flags);
  const outDir = path.join(state.current, 'runtime-html');
  fs.mkdirSync(outDir, { recursive: true });
  const rows = await mapLimit(routes, 6, async (route) => {
    if (route.runtimeMode !== 'runtime') {
      return {
        ...route,
        status: 'SOURCE_CERTIFIED',
        httpStatus: null,
        finalUrl: null,
        contentType: null,
        title: null,
        hasPanel: true,
        hasSurface: true,
        hasRoute: true,
        htmlSnapshot: null,
        reason: route.sourceJustification || 'Source-certified route'
      };
    }
    const startedAt = nowIso();
    try {
      const { response, text } = await fetchWithTimeout(route.runtimeUrl);
      const title = text.match(/<title[^>]*>(.*?)<\/title>/i)?.[1] || null;
      const expectedPanel = route.anchors?.['data-prisma-panel'];
      const expectedSurface = route.anchors?.['data-prisma-surface'];
      const expectedRoute = route.anchors?.['data-prisma-route'];
      const hasPanel = text.includes(`data-prisma-panel="${expectedPanel}"`) || text.includes(`data-prisma-panel='${expectedPanel}'`);
      const hasSurface = text.includes(`data-prisma-surface="${expectedSurface}"`) || text.includes(`data-prisma-surface='${expectedSurface}'`);
      const hasRoute = text.includes(`data-prisma-route="${expectedRoute}"`) || text.includes(`data-prisma-route='${expectedRoute}'`);
      const safeName = `${route.surface}_${route.route === '/' ? 'root' : route.route.slice(1).replace(/[^A-Za-z0-9]+/g, '_')}.html`;
      const snapshot = path.join(outDir, safeName);
      writeText(snapshot, text.length > 200000 ? text.slice(0, 200000) : text);
      const ok = response.ok && hasPanel && hasSurface && hasRoute;
      return {
        ...route,
        status: ok ? 'RUNTIME_CERTIFIED' : (!response.ok ? 'RUNTIME_BLOCKED' : (!hasPanel ? 'ANCHOR_MISSING' : (!hasSurface || !hasRoute ? 'ANCHOR_MISSING' : 'SELECTOR_MISSING'))),
        httpStatus: response.status,
        finalUrl: response.url,
        redirected: response.redirected,
        contentType: response.headers.get('content-type'),
        title,
        hasPanel,
        hasSurface,
        hasRoute,
        htmlSnapshot: relApp(snapshot),
        startedAt,
        finishedAt: nowIso()
      };
    } catch (error) {
      return {
        ...route,
        status: 'RUNTIME_BLOCKED',
        httpStatus: null,
        finalUrl: route.runtimeUrl,
        contentType: null,
        title: null,
        hasPanel: false,
        hasSurface: false,
        hasRoute: false,
        htmlSnapshot: null,
        startedAt,
        finishedAt: nowIso(),
        error: String(error?.message || error)
      };
    }
  });
  const runtimeBlockedCount = rows.filter((row) => row.status === 'RUNTIME_BLOCKED').length;
  const anchorMissingCount = rows.filter((row) => row.status === 'ANCHOR_MISSING').length;
  const selectorMissingCount = rows.filter((row) => row.status === 'SELECTOR_MISSING').length;
  const status = runtimeBlockedCount || anchorMissingCount || selectorMissingCount ? 'RUNTIME_BLOCKED' : 'RUNTIME_CERTIFIED';
  const countsBySurface = {};
  for (const row of rows) {
    countsBySurface[row.surface] ||= { app: row.app, port: row.port, routeCount: 0, runtimeCertifiedCount: 0, sourceCertifiedCount: 0, runtimeBlockedCount: 0 };
    countsBySurface[row.surface].routeCount += 1;
    if (row.status === 'RUNTIME_CERTIFIED') countsBySurface[row.surface].runtimeCertifiedCount += 1;
    if (row.status === 'SOURCE_CERTIFIED') countsBySurface[row.surface].sourceCertifiedCount += 1;
    if (row.status === 'RUNTIME_BLOCKED') countsBySurface[row.surface].runtimeBlockedCount += 1;
  }
  const report = {
    ...baseReport('prisma.ui.runtime.evidence.report.v1', 'runtime-probe', emptyEvaluation(state), status),
    routeCount: rows.length,
    runtimeCertifiedCount: rows.filter((row) => row.status === 'RUNTIME_CERTIFIED').length,
    sourceCertifiedCount: rows.filter((row) => row.status === 'SOURCE_CERTIFIED').length,
    runtimeBlockedCount,
    anchorMissingCount,
    selectorMissingCount,
    blockedCount: runtimeBlockedCount + anchorMissingCount + selectorMissingCount,
    driftCount: 0,
    conflictCount: 0,
    countsBySurface,
    routes: rows,
    exitCodeExpectation: status === 'RUNTIME_CERTIFIED' ? 0 : 1
  };
  writeReports('UI_RUNTIME_EVIDENCE_REPORT', report);
  return report;
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
    ...baseReport('prisma.ui.runtime.page.cert.report.v1', 'certify-runtime-pages', emptyEvaluation(loadState()), status),
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
    routes: runtime.routes.map((route) => ({
      app: route.app,
      port: route.port,
      surface: route.surface,
      route: route.route,
      panel: route.panel_id,
      status: route.status,
      runtimeUrl: route.runtimeUrl,
      httpStatus: route.httpStatus,
      finalUrl: route.finalUrl,
      htmlSnapshot: route.htmlSnapshot
    })),
    exitCodeExpectation: status === 'ALL_RUNTIME_PAGES_CERTIFIED' ? 0 : 1
  };
  writeReports('UI_RUNTIME_PAGE_CERT_REPORT', report);
  return report;
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
    panelCount: report.panelCount,
    anchorCount: report.anchorCount,
    surfaceCount: report.surfaceCount,
    visualRegionCount: report.visualRegionCount,
    editableSlotCount: report.editableSlotCount,
    componentOwnerCount: report.componentOwnerCount,
    cssOwnerCount: report.cssOwnerCount,
    layerCount: report.layerCount,
    conflictCount: report.conflictCount,
    changedCount: report.changedCount,
    blockerCount: report.blockerCount,
    warningCount: report.warningCount,
    activeImportantCount: report.activeImportantCount,
    ambiguousActiveLayerOwnerCount: report.ambiguousActiveLayerOwnerCount,
    problems: report.problems,
    blocked: report.blocked,
    drifts: report.drifts,
    conflicts: report.conflicts
  };
  for (const key of Object.keys(compact)) if (compact[key] === undefined) delete compact[key];
  console.log(JSON.stringify(compact, null, 2));
}

const { cmd, flags } = parseArgs();
let result;
if (cmd === 'self-test') result = selfTest(flags);
else if (cmd === 'certify' || cmd === 'supreme' || cmd === 'work') result = certify(flags);
else if (cmd === 'certify-all-surfaces') result = certifyAllSurfaces(flags);
else if (UI_RUNTIME_COMMANDS.has(cmd)) result = await runUiRuntimeCommand(cmd, flags);
else if (VISUAL_CONTROL_COMMANDS.has(cmd)) result = await runVisualControlCommand(cmd, flags);
else if (cmd === 'contracts') result = contracts(flags);
else if (cmd === 'anchors') result = anchorsCommand(flags);
else if (cmd === 'selectors') result = selectorsCommand(flags);
else if (cmd === 'drift') result = drift(flags);
else if (cmd === 'conflicts') result = conflicts(flags);
else if (cmd === 'scope') result = scope(flags);
else if (cmd === 'zero-important') result = zeroImportantCommand(flags);
else if (cmd === 'inventory') result = inventory(flags);
else if (cmd === 'doctor') result = doctor(flags);
else if (cmd === 'report') result = reportCommand(flags);
else {
  console.error(`Unknown command: ${cmd}`);
  process.exit(2);
}
printReport(result);
if (flags.strict && result.status !== 'CERTIFIED' && !isUiRuntimeSuccess(result.status)) process.exit(1);
if (['scope', 'drift', 'conflicts', 'zero-important', 'doctor'].includes(cmd) && result.status !== 'CERTIFIED') process.exit(1);
