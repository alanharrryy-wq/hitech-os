#!/usr/bin/env node
/**
 * PRISMA Zero Priority Gate
 *
 * Purpose:
 *   Block priority override tokens in live runtime source.
 *
 * Important:
 *   This intentionally excludes docs, tooling, governance, generated reports and
 *   scanners. Documentation may mention forbidden tokens as policy text; the live
 *   UI source must not use them.
 */

import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const FORBIDDEN_TOKEN = '!important';
const REPORT_PREFIX = 'zero-important-gate';

const LIVE_INCLUDE_PREFIXES = [
  'apps/terminal-de-venta-system/products/',
  'apps/terminal-de-venta-system/app/',
  'apps/terminal-de-venta-system/src/',
  'apps/terminal-de-venta-system/components/',
  'apps/terminal-de-venta-system/styles/',
  'apps/terminal-de-venta-system/lib/',
  'apps/terminal-de-venta-system/shared/'
];

const EXCLUDE_PARTS = new Set([
  '.git',
  'node_modules',
  '.next',
  'dist',
  'build',
  'coverage',
  '.turbo',
  '.cache',
  'out',
  'generated',
  '.prisma',
  '__pycache__',
  'docs',
  'tools',
  '.prisma-ui',
  '.governance',
  'reports',
  'evidence'
]);

const SCAN_EXTENSIONS = new Set([
  '.css', '.scss', '.sass', '.less',
  '.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs'
]);

function normalizeRel(filePath) {
  return filePath.replace(/\\/g, '/').replace(/^\.\//, '');
}

function findRepoRoot(startDir) {
  let current = path.resolve(startDir);
  while (true) {
    if (fs.existsSync(path.join(current, '.git'))) return current;
    const parent = path.dirname(current);
    if (parent === current) return path.resolve(startDir);
    current = parent;
  }
}

function nowStamp() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}${pad(d.getHours())}${pad(d.getMinutes())}`;
}

function defaultOutRoot() {
  if (process.platform === 'win32') return 'F:\\descargasf';
  return process.env.PRISMA_OUT_ROOT || process.cwd();
}

function shouldScanRel(rel) {
  const n = normalizeRel(rel);
  const parts = n.split('/').filter(Boolean);
  if (parts.some((p) => EXCLUDE_PARTS.has(p))) return false;
  if (!LIVE_INCLUDE_PREFIXES.some((prefix) => n.startsWith(prefix))) return false;

  const ext = path.extname(n).toLowerCase();
  if (!SCAN_EXTENSIONS.has(ext)) return false;

  if (n.endsWith('.map')) return false;
  if (n.endsWith('.min.js')) return false;
  if (n.endsWith('.min.css')) return false;
  return true;
}

function runGitTrackedFiles(repoRoot) {
  try {
    const out = execFileSync('git', ['ls-files'], {
      cwd: repoRoot,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'pipe']
    });
    return out.split(/\r?\n/).map((x) => x.trim()).filter(Boolean);
  } catch {
    return null;
  }
}

function walkFiles(root) {
  const files = [];
  const stack = [root];
  while (stack.length) {
    const dir = stack.pop();
    let entries = [];
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      continue;
    }
    for (const entry of entries) {
      const full = path.join(dir, entry.name);
      const rel = normalizeRel(path.relative(root, full));
      const parts = rel.split('/').filter(Boolean);
      if (parts.some((p) => EXCLUDE_PARTS.has(p))) continue;
      if (entry.isDirectory()) stack.push(full);
      else if (entry.isFile()) files.push(rel);
    }
  }
  return files;
}

function stableJson(data) {
  return JSON.stringify(data, null, 2) + '\n';
}

function main() {
  const cwd = process.cwd();
  const repoRoot = findRepoRoot(cwd);
  const outRoot = process.env.PRISMA_OUT_ROOT || defaultOutRoot();
  const reportDir = path.join(outRoot, `${REPORT_PREFIX} ${nowStamp()}`);
  fs.mkdirSync(reportDir, { recursive: true });

  const tracked = runGitTrackedFiles(repoRoot);
  const allFiles = tracked || walkFiles(repoRoot);
  const candidates = allFiles
    .map(normalizeRel)
    .filter(shouldScanRel)
    .sort();

  const hits = [];
  for (const rel of candidates) {
    const full = path.join(repoRoot, rel);
    let stat;
    try {
      stat = fs.statSync(full);
    } catch {
      continue;
    }
    if (!stat.isFile() || stat.size > 2_500_000) continue;

    let text = '';
    try {
      text = fs.readFileSync(full, 'utf8');
    } catch {
      continue;
    }

    const lines = text.split(/\r?\n/);
    lines.forEach((line, index) => {
      if (line.includes(FORBIDDEN_TOKEN)) {
        hits.push({
          file: rel,
          line: index + 1,
          severity: 'high',
          text: line.trim().slice(0, 320)
        });
      }
    });
  }

  const report = {
    status: hits.length ? 'FAIL' : 'PASS',
    rule: 'live runtime source must not use priority override tokens',
    forbiddenToken: FORBIDDEN_TOKEN,
    repoRoot,
    invokedFrom: cwd,
    reportDir,
    scannerScope: {
      includePrefixes: LIVE_INCLUDE_PREFIXES,
      excludeParts: Array.from(EXCLUDE_PARTS).sort(),
      extensions: Array.from(SCAN_EXTENSIONS).sort()
    },
    trackedMode: tracked ? 'git ls-files' : 'filesystem fallback',
    scannedFiles: candidates.length,
    hitCount: hits.length,
    hits
  };

  fs.writeFileSync(path.join(reportDir, 'zero-important-report.json'), stableJson(report), 'utf8');
  fs.writeFileSync(
    path.join(reportDir, 'zero-important-report.md'),
    [
      '# Zero Priority Gate',
      '',
      `- status: \`${report.status}\``,
      `- scanned files: \`${report.scannedFiles}\``,
      `- hits: \`${report.hitCount}\``,
      `- report dir: \`${reportDir}\``,
      '',
      '## Scope',
      '',
      'This gate scans runtime UI/source only. It intentionally excludes docs, tooling, governance, generated reports and the quality scanners themselves.',
      '',
      '## Hits',
      '',
      ...(hits.length ? hits.map((h) => `- \`${h.file}:${h.line}\` ${h.text}`) : ['- none'])
    ].join('\n') + '\n',
    'utf8'
  );

  if (hits.length) {
    console.error('');
    console.error('ZERO PRIORITY GATE: FAIL');
    console.error('');
    console.error(`Found ${hits.length} forbidden priority override token occurrence(s) in live runtime source.`);
    console.error('Rule: live tracked source must not use priority override tokens.');
    console.error('Fix: resolve cascade, scope, owner selector, ordering or architecture instead of force.');
    console.error('');
    for (const h of hits) {
      console.error(`- ${h.file}:${h.line} [${h.severity}] ${h.text}`);
    }
    console.error(`Reports: ${reportDir}`);
    process.exit(1);
  }

  console.log('');
  console.log('ZERO PRIORITY GATE: PASS');
  console.log('');
  console.log(`Scanned ${candidates.length} live runtime source file(s).`);
  console.log(`Reports: ${reportDir}`);
  process.exit(0);
}

main();
