import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { redact } from './redaction.mjs';
import { writeJson } from './safe-json.mjs';

const TEXT_EXTENSIONS = new Set(['.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.json', '.md', '.mdx', '.py', '.prisma', '.sql', '.ps1', '.cmd', '.yml', '.yaml']);
const DEFAULT_IGNORE = ['node_modules', '.git', '.next', 'dist', 'build', 'coverage', '.prisma_backups', 'logs'];
const CRITICAL_RELATIVE_PATHS = [
  'package.json',
  'pnpm-workspace.yaml',
  'products/tablet/app/package.json',
  'products/tablet/app/next.config.mjs',
  'products/tablet/app/app',
  'products/pc/app/package.json',
  'products/mobile/app/package.json',
  'products/chart-lab/app/package.json',
  'shared',
  'prisma/schema.prisma',
  'quality/bin/prisma-quality.mjs',
  'quality/prisma-quality.manifest.json',
  'quality/profiles/client-readiness.json',
  'quality/docs/customer-assurance-layer.md'
];

export function exists(filePath) {
  try { fs.accessSync(filePath); return true; } catch { return false; }
}

export function isDir(filePath) {
  try { return fs.statSync(filePath).isDirectory(); } catch { return false; }
}

export function readText(filePath) {
  try { return fs.readFileSync(filePath, 'utf8'); } catch { return ''; }
}

export function readJsonSafe(filePath) {
  try { return { ok: true, value: JSON.parse(readText(filePath)), error: null }; }
  catch (error) { return { ok: false, value: null, error: error?.message || String(error) }; }
}

export function toPosix(value) {
  return String(value || '').replace(/\\/g, '/');
}

export function rel(ctx, filePath) {
  return toPosix(path.relative(ctx.repoRoot, filePath));
}

function shouldIgnore(filePath, ignoreParts = []) {
  const normalized = toPosix(filePath).toLowerCase();
  return ignoreParts.some((part) => normalized.includes(toPosix(part).toLowerCase()));
}

export function listTextFiles(rootDir, options = {}) {
  const out = [];
  const maxBytes = options.maxBytes ?? 1048576;
  const maxFiles = options.maxFiles ?? 3000;
  const ignore = options.ignore ?? DEFAULT_IGNORE;
  const extensions = options.extensions ? new Set(options.extensions) : TEXT_EXTENSIONS;
  function walk(dir) {
    if (out.length >= maxFiles || !isDir(dir) || shouldIgnore(dir, ignore)) return;
    let entries = [];
    try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
    for (const entry of entries) {
      if (out.length >= maxFiles) break;
      const full = path.join(dir, entry.name);
      if (shouldIgnore(full, ignore)) continue;
      if (entry.isDirectory()) walk(full);
      else if (entry.isFile()) {
        let stat = null;
        try { stat = fs.statSync(full); } catch { continue; }
        if (stat.size <= maxBytes && extensions.has(path.extname(entry.name).toLowerCase())) out.push(full);
      }
    }
  }
  walk(rootDir);
  return out;
}

export function scanRepoText(ctx, roots = ['products', 'shared', 'prisma', 'quality'], options = {}) {
  const files = [];
  for (const rootName of roots) {
    const abs = path.join(ctx.repoRoot, rootName);
    if (!exists(abs)) continue;
    files.push(...listTextFiles(abs, {
      maxBytes: ctx.config?.scan?.maxFileBytes || 1048576,
      extensions: ctx.config?.scan?.extensions || Array.from(TEXT_EXTENSIONS),
      ignore: ctx.config?.ignore || DEFAULT_IGNORE,
      maxFiles: options.maxFiles ?? 3000
    }));
  }
  return files;
}

export function sha256Text(value) {
  return crypto.createHash('sha256').update(String(value), 'utf8').digest('hex');
}

export function sha256File(filePath) {
  try { return sha256Text(fs.readFileSync(filePath)); } catch { return null; }
}

export function pathMatrix(ctx, relPaths = CRITICAL_RELATIVE_PATHS) {
  return relPaths.map((relativePath) => {
    const abs = path.join(ctx.repoRoot, relativePath);
    return {
      path: toPosix(relativePath),
      exists: exists(abs),
      isDirectory: isDir(abs),
      sha256: exists(abs) && !isDir(abs) ? sha256File(abs) : null
    };
  });
}

export function packageScripts(ctx, packagePath = path.join(ctx.repoRoot, 'package.json')) {
  const parsed = readJsonSafe(packagePath);
  const scripts = parsed.ok && parsed.value && typeof parsed.value === 'object' ? (parsed.value.scripts || {}) : {};
  return { ok: parsed.ok, error: parsed.error, scriptNames: Object.keys(scripts).sort(), scripts };
}

export function customerSnapshot(ctx) {
  const matrix = pathMatrix(ctx);
  const rootPackage = packageScripts(ctx);
  const qualityManifest = readJsonSafe(path.join(ctx.qualityRoot, 'prisma-quality.manifest.json'));
  const importantFiles = matrix.filter((item) => item.exists && item.sha256).map((item) => ({ path: item.path, sha256: item.sha256 }));
  const surfaceFiles = scanRepoText(ctx, ['products', 'shared', 'prisma', 'quality'], { maxFiles: 1200 });
  const corpus = surfaceFiles.map((file) => readText(file).toLowerCase()).join('\n');
  const tokens = ['outbox', 'idempot', 'demo', 'training', 'support pack', 'rollback', 'client-readiness', 'quality_evidence_ledger'];
  const tokenCounts = Object.fromEntries(tokens.map((token) => [token, corpus.split(token).length - 1]));
  return {
    schemaVersion: '1.0',
    createdAt: new Date().toISOString(),
    repoRoot: ctx.repoRoot,
    qualityVersion: qualityManifest.value?.systemVersion || qualityManifest.value?.version || 'unknown',
    pathMatrix: matrix,
    rootPackage: { ok: rootPackage.ok, scriptNames: rootPackage.scriptNames },
    importantFiles,
    scannedTextFiles: surfaceFiles.length,
    tokenCounts
  };
}

export function writeRunJson(ctx, fileName, value) {
  const abs = path.join(ctx.runDir, fileName);
  writeJson(abs, value);
  return abs;
}

export function latestPreviousRun(ctx) {
  if (!ctx.outDir || !exists(ctx.outDir)) return null;
  let dirs = [];
  try {
    dirs = fs.readdirSync(ctx.outDir, { withFileTypes: true })
      .filter((entry) => entry.isDirectory() && entry.name.startsWith('PRISMA_QUALITY_OS_'))
      .map((entry) => path.join(ctx.outDir, entry.name))
      .filter((dir) => path.resolve(dir) !== path.resolve(ctx.runDir || ''))
      .sort()
      .reverse();
  } catch { return null; }
  return dirs[0] || null;
}

export function loadPreviousCustomerSnapshot(ctx) {
  const previous = latestPreviousRun(ctx);
  if (!previous) return { found: false, runDir: null, snapshot: null };
  const snapshotPath = path.join(previous, 'CUSTOMER_ASSURANCE_SNAPSHOT.json');
  const parsed = readJsonSafe(snapshotPath);
  if (!parsed.ok) return { found: false, runDir: previous, snapshot: null, error: parsed.error };
  return { found: true, runDir: previous, snapshot: parsed.value };
}

export function diffSnapshots(previous, current) {
  if (!previous || !current) return { compared: false, changed: [], added: [], removed: [] };
  const before = new Map((previous.importantFiles || []).map((item) => [item.path, item.sha256]));
  const after = new Map((current.importantFiles || []).map((item) => [item.path, item.sha256]));
  const changed = [];
  const added = [];
  const removed = [];
  for (const [key, hash] of after.entries()) {
    if (!before.has(key)) added.push(key);
    else if (before.get(key) !== hash) changed.push(key);
  }
  for (const key of before.keys()) if (!after.has(key)) removed.push(key);
  return { compared: true, changed, added, removed };
}

export function redactProof() {
  const samples = {
    openai: 'OPENAI_API_KEY=' + 's' + 'k-' + 'abcdefghijklmnopqrstuvwxyz1234567890',
    github: 'GITHUB_TOKEN=' + 'g' + 'hp_' + 'abcdefghijklmnopqrstuvwxyz123456',
    password: 'password=' + 'my-secret-password',
    authorization: 'authorization: ' + 'Bearer ' + 'abcdefghijklmnopqrstuvwxyz'
  };
  const redacted = Object.fromEntries(Object.entries(samples).map(([key, value]) => [key, redact(value)]));
  const leaks = Object.values(redacted).filter((value) => /sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9_]{20,}|my-secret-password|Bearer abcdef/i.test(value));
  return { samples: redacted, leakCount: leaks.length };
}

export function ensureCustomerSupportManifest(ctx, summary) {
  const manifest = {
    schemaVersion: '1.0',
    createdAt: new Date().toISOString(),
    runId: ctx.runId,
    profile: ctx.profile,
    purpose: 'Customer support pack manifest. Zip the full PRISMA_QUALITY_OS run directory for handoff.',
    includes: [
      'QUALITY_REPORT.json',
      'QUALITY_DECISION.json',
      'QUALITY_FINDINGS.json',
      'QUALITY_EVIDENCE_LEDGER.jsonl',
      'QUALITY_MACHINE_SUMMARY.json',
      'ENVIRONMENT_SNAPSHOT.json',
      'COMMANDS_RUN.json',
      'CHECKSUMS.csv',
      'evidence/*.json',
      'CUSTOMER_ASSURANCE_SNAPSHOT.json',
      'CUSTOMER_EVIDENCE_LEDGER.json'
    ],
    excludes: [
      'raw databases',
      'customer PII exports',
      'full .env files',
      'tokens and secrets',
      'node_modules',
      'build artifacts'
    ],
    redaction: 'All evidence payloads pass through quality/core/redaction.mjs.',
    summary
  };
  writeRunJson(ctx, 'CUSTOMER_SUPPORT_PACK_MANIFEST.json', manifest);
  return manifest;
}

export function writeCustomerEvidenceLedger(ctx, gateResults) {
  const ledger = {
    schemaVersion: '1.0',
    createdAt: new Date().toISOString(),
    runId: ctx.runId,
    profile: ctx.profile,
    qualityRoot: ctx.qualityRoot,
    repoRoot: ctx.repoRoot,
    gates: (gateResults || []).map((gate) => ({
      gateId: gate.gateId,
      title: gate.title,
      status: gate.status,
      findingCount: (gate.findings || []).length,
      evidenceCount: (gate.evidence || []).length,
      evidenceIds: (gate.evidence || []).map((item) => item.evidenceId || item.path || item.summary).filter(Boolean)
    }))
  };
  writeRunJson(ctx, 'CUSTOMER_EVIDENCE_LEDGER.json', ledger);
  return ledger;
}
