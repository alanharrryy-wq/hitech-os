import fs from 'node:fs';
import path from 'node:path';

const DEFAULT_EXTENSIONS = new Set(['.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.json', '.md', '.mdx', '.sql', '.py', '.txt']);
const IGNORE_SEGMENTS = new Set(['node_modules', '.next', '.git', 'dist', 'build', 'coverage', '.turbo', '.prisma_backups']);

export function readJsonSafe(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (error) {
    return { __error: error.message || String(error) };
  }
}

function toPosix(value) {
  return String(value).replaceAll('\\', '/');
}

function exists(repoRoot, relPath) {
  return fs.existsSync(path.join(repoRoot, relPath));
}

function shouldIgnore(filePath) {
  const parts = toPosix(filePath).split('/');
  return parts.some(part => IGNORE_SEGMENTS.has(part));
}

function safeRead(filePath, maxBytes = 350000) {
  try {
    const stat = fs.statSync(filePath);
    if (!stat.isFile() || stat.size > maxBytes) return '';
    return fs.readFileSync(filePath, 'utf8');
  } catch {
    return '';
  }
}

function walk(root, opts = {}) {
  const out = [];
  const maxFiles = opts.maxFiles || 700;
  const extensions = opts.extensions || DEFAULT_EXTENSIONS;

  function visit(dir) {
    if (out.length >= maxFiles) return;
    if (!fs.existsSync(dir) || shouldIgnore(dir)) return;

    let entries = [];
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }

    for (const entry of entries) {
      if (out.length >= maxFiles) return;
      const full = path.join(dir, entry.name);
      if (shouldIgnore(full)) continue;

      if (entry.isDirectory()) {
        visit(full);
      } else if (entry.isFile()) {
        const ext = path.extname(entry.name).toLowerCase();
        if (extensions.has(ext)) out.push(full);
      }
    }
  }

  visit(root);
  return out;
}

function listFiles(repoRoot, roots, opts = {}) {
  const files = [];
  for (const relRoot of roots || []) {
    const abs = path.join(repoRoot, relRoot);
    files.push(...walk(abs, opts));
  }
  return files.slice(0, opts.maxFiles || 700);
}

function pathExistsCheck(ctx, check) {
  const ok = exists(ctx.repoRoot, check.path);
  return {
    checkId: check.id,
    type: check.type,
    ok,
    evidenceCount: ok ? 1 : 0,
    evidence: ok ? [{ path: check.path, kind: 'path' }] : [],
    detail: ok ? `${check.path} exists.` : `${check.path} not found.`
  };
}

function anyPathExistsCheck(ctx, check) {
  const paths = Array.isArray(check.paths) ? check.paths : [];
  const found = paths.filter(p => exists(ctx.repoRoot, p));
  const minFound = Number(check.minFound || 1);
  const ok = found.length >= minFound;

  return {
    checkId: check.id,
    type: check.type,
    ok,
    evidenceCount: found.length,
    evidence: found.map(p => ({ path: p, kind: 'path' })),
    detail: `${found.length}/${paths.length} paths found; minimum ${minFound}.`
  };
}

function termScanCheck(ctx, check) {
  const terms = Array.isArray(check.terms) ? check.terms : [];
  const roots = Array.isArray(check.roots) ? check.roots : [];
  const minTerms = Number(check.minTerms || 1);
  const files = listFiles(ctx.repoRoot, roots, { maxFiles: check.maxFiles || 700 });
  const termHits = {};
  const fileHits = [];

  for (const term of terms) termHits[term] = 0;

  for (const file of files) {
    const text = safeRead(file).toLowerCase();
    if (!text) continue;

    const hitTerms = [];
    for (const term of terms) {
      const needle = String(term).toLowerCase();
      if (text.includes(needle)) {
        termHits[term] += 1;
        hitTerms.push(term);
      }
    }

    if (hitTerms.length) {
      fileHits.push({
        path: toPosix(path.relative(ctx.repoRoot, file)),
        terms: hitTerms.slice(0, 12)
      });
    }
  }

  const matchedTerms = Object.entries(termHits).filter(([, count]) => count > 0).map(([term]) => term);
  const ok = matchedTerms.length >= minTerms;

  return {
    checkId: check.id,
    type: check.type,
    ok,
    evidenceCount: matchedTerms.length,
    evidence: fileHits.slice(0, 50),
    termHits,
    matchedTerms,
    filesScanned: files.length,
    detail: `${matchedTerms.length}/${terms.length} terms found; minimum ${minTerms}.`
  };
}

function portManifestContainsCheck(ctx, check) {
  const manifestPath = path.join(ctx.qualityRoot, 'runtime', 'runtime-port-manifest.json');
  const manifest = readJsonSafe(manifestPath);
  const services = Array.isArray(manifest.services) ? manifest.services : [];
  const found = services.find(s => s.id === check.serviceId && Number(s.defaultPort) === Number(check.port));
  const ok = Boolean(found);

  return {
    checkId: check.id,
    type: check.type,
    ok,
    evidenceCount: ok ? 1 : 0,
    evidence: ok ? [{ serviceId: found.id, port: Number(found.defaultPort), layer: found.layer }] : [],
    detail: ok ? `${check.serviceId} uses port ${check.port}.` : `${check.serviceId}:${check.port} not found in runtime manifest.`
  };
}

export function evaluateCheck(ctx, check) {
  if (!check || !check.type) {
    return { checkId: check?.id || 'UNKNOWN', type: 'unknown', ok: false, evidenceCount: 0, evidence: [], detail: 'Invalid check.' };
  }

  if (check.type === 'pathExists') return pathExistsCheck(ctx, check);
  if (check.type === 'anyPathExists') return anyPathExistsCheck(ctx, check);
  if (check.type === 'termScan') return termScanCheck(ctx, check);
  if (check.type === 'portManifestContains') return portManifestContainsCheck(ctx, check);

  return { checkId: check.id, type: check.type, ok: false, evidenceCount: 0, evidence: [], detail: `Unsupported check type ${check.type}.` };
}

export function evaluateScenario(ctx, scenario) {
  const checks = Array.isArray(scenario.checks) ? scenario.checks : [];
  const checkResults = checks.map(check => evaluateCheck(ctx, check));
  const passed = checkResults.filter(r => r.ok).length;
  const total = checkResults.length;
  const actualEvidenceCount = checkResults.reduce((acc, r) => acc + Number(r.evidenceCount || 0), 0);
  const confidence = total ? Math.round((passed / total) * 100) / 100 : 0;

  let status = 'MISSING';
  if (total > 0 && passed === total && actualEvidenceCount > 0) status = 'READY';
  else if (passed > 0 || actualEvidenceCount > 0) status = 'PARTIAL';

  return {
    scenarioId: scenario.id,
    title: scenario.title,
    vertical: scenario.vertical,
    layer: scenario.layer,
    owner: scenario.owner,
    tags: scenario.tags || [],
    mutates: Boolean(scenario.mutates),
    requiresCloudflare: Boolean(scenario.requiresCloudflare),
    startsServices: Boolean(scenario.startsServices),
    status,
    confidence,
    passedChecks: passed,
    totalChecks: total,
    actualEvidenceCount,
    expectedEvidence: scenario.expectedEvidence || [],
    checkResults
  };
}

export function evaluateScenarioManifest(ctx, manifestPath = null) {
  const resolvedManifestPath = manifestPath || path.join(ctx.qualityRoot, 'scenarios', 'scenario-manifest.json');
  const manifest = readJsonSafe(resolvedManifestPath);
  const scenarios = Array.isArray(manifest.scenarios) ? manifest.scenarios : [];
  const results = scenarios.map(scenario => evaluateScenario(ctx, scenario));
  const aggregate = {
    scenarioCount: results.length,
    ready: results.filter(r => r.status === 'READY').length,
    partial: results.filter(r => r.status === 'PARTIAL').length,
    missing: results.filter(r => r.status === 'MISSING').length,
    mutating: results.filter(r => r.mutates).length,
    cloudflareRequired: results.filter(r => r.requiresCloudflare).length,
    startsServices: results.filter(r => r.startsServices).length,
    averageConfidence: results.length ? Math.round((results.reduce((acc, r) => acc + r.confidence, 0) / results.length) * 100) / 100 : 0
  };

  return {
    manifestPath: toPosix(path.relative(ctx.repoRoot, resolvedManifestPath)),
    manifest,
    results,
    aggregate
  };
}
