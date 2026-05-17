import fs from 'node:fs';
import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { pathExists, listFiles, toPosix } from '../core/paths.mjs';

function readSafe(p) { try { return fs.readFileSync(p, 'utf8'); } catch { return ''; } }
function rel(ctx, p) { return toPosix(path.relative(ctx.repoRoot, p)); }

const NON_RUNTIME_SEGMENTS = ['/tools/', '/fixtures/', '/docs/', '/__tests__/', '/test/', '/tests/'];
const RUNTIME_EXTENSIONS = new Set(['.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs']);

function normalized(relPath) {
  return `/${relPath.replaceAll('\\', '/')}`.toLowerCase();
}

function isNonRuntimeContext(relPath) {
  const p = normalized(relPath);
  if (p.endsWith('/readme.md') || p.endsWith('.md') || p.endsWith('.mdx')) return true;
  return NON_RUNTIME_SEGMENTS.some(segment => p.includes(segment));
}

function isRuntimeTabletFile(relPath) {
  const p = normalized(relPath);
  if (isNonRuntimeContext(relPath)) return false;
  const ext = path.extname(relPath).toLowerCase();
  if (!RUNTIME_EXTENSIONS.has(ext)) return false;
  return p.includes('/products/tablet/app/app/') || p.includes('/products/tablet/app/src/') || p.includes('/products/tablet/app/components/');
}

function stripComments(text) {
  return text
    .replace(/\/\*[\s\S]*?\*\//g, '')
    .replace(/^\s*\/\/.*$/gm, '');
}

function lineNumber(text, index) {
  return text.slice(0, index).split(/\r?\n/).length;
}

function uniqueHits(hits) {
  const seen = new Set();
  const out = [];
  for (const hit of hits) {
    const key = `${hit.ruleId}|${hit.file}|${hit.line}|${String(hit.match).toLowerCase()}`;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(hit);
  }
  return out;
}

const HARD_RULES = [
  {
    id: 'TABLET_IMPORTS_PC_WORKSPACE',
    layer: 'Architecture',
    boundary: 'Tablet -> PC',
    severity: 'S0',
    title: 'Tablet runtime imports or references PC workspace path',
    pattern: /(?:from\s+['\"][^'\"]*(?:products[\\/]+pc[\\/]+app|(?:\.\.\/[\.\.\/]*pc)(?:\/|$)|@pc(?:\/|$))[^'\"]*['\"]|import\s*\([^)]*(?:products[\\/]+pc[\\/]+app|@pc(?:\/|$)))/ig
  },
  {
    id: 'TABLET_CALLS_BACKOFFICE_API',
    layer: 'Architecture',
    boundary: 'Tablet -> PC API',
    severity: 'S0',
    title: 'Tablet runtime calls backoffice API directly',
    pattern: /(?:fetch|axios|http|request)\s*\([^)]*(?:\/api\/backoffice|backoffice\/api|backofficeUrl|BACKOFFICE_URL)/ig
  },
  {
    id: 'TABLET_IMPORTS_MOBILE_WORKSPACE',
    layer: 'Architecture',
    boundary: 'Tablet -> Mobile',
    severity: 'S0',
    title: 'Tablet runtime imports or references Mobile workspace path',
    pattern: /(?:from\s+['\"][^'\"]*(?:products[\\/]+mobile[\\/]+app|(?:\.\.\/[\.\.\/]*mobile)(?:\/|$)|@mobile(?:\/|$))[^'\"]*['\"]|import\s*\([^)]*(?:products[\\/]+mobile[\\/]+app|@mobile(?:\/|$)))/ig
  },
  {
    id: 'TABLET_IMPORTS_CONTROL_CENTER',
    layer: 'Architecture',
    boundary: 'Tablet -> Control',
    severity: 'S0',
    title: 'Tablet runtime imports or references Control Center implementation',
    pattern: /(?:from\s+['\"][^'\"]*(?:prisma-control-center|control-center)[^'\"]*['\"]|import\s*\([^)]*(?:prisma-control-center|control-center))/ig
  },
  {
    id: 'TABLET_REQUIRES_CLOUDFLARE_ENDPOINT',
    layer: 'Cloudflare',
    boundary: 'Tablet -> Cloudflare',
    severity: 'S1',
    title: 'Tablet runtime requires Cloudflare or public tunnel endpoint',
    pattern: /(?:fetch|axios|http|request)\s*\([^)]*(?:workers\.dev|cloudflare|cloudflared|tunnel required|public endpoint required)/ig
  }
];

const TEXTUAL_SIGNALS = [
  { id: 'TEXT_BACKOFFICE', pattern: /\bbackoffice\b/ig },
  { id: 'TEXT_PC_GOVERNANCE', pattern: /\bPC governance\b/ig },
  { id: 'TEXT_MOBILE_SUPERVISION', pattern: /\bMobile supervision\b/ig },
  { id: 'TEXT_CONTROL_AUDIT', pattern: /\bControl audit\b/ig }
];

function collectMatches(text, rules, file) {
  const hits = [];
  for (const rule of rules) {
    rule.pattern.lastIndex = 0;
    let match;
    while ((match = rule.pattern.exec(text)) !== null) {
      hits.push({
        ruleId: rule.id,
        file,
        line: lineNumber(text, match.index),
        match: String(match[0]).replace(/\s+/g, ' ').slice(0, 220),
        severity: rule.severity,
        layer: rule.layer,
        title: rule.title,
        boundary: rule.boundary
      });
    }
  }
  return uniqueHits(hits);
}

export async function run(ctx) {
  const tabletRoot = path.join(ctx.repoRoot, ctx.config.roots.tablet);
  const files = pathExists(tabletRoot)
    ? listFiles(tabletRoot, { maxBytes: ctx.config.scan.maxFileBytes, extensions: ['.ts','.tsx','.js','.jsx','.mjs','.cjs','.json','.md','.mdx'], ignore: ctx.config.ignore })
    : [];

  const hardRuntimeHits = [];
  const textualRuntimeSignals = [];
  const nonRuntimeContextSignals = [];

  for (const file of files) {
    const relative = rel(ctx, file);
    const raw = readSafe(file);
    const text = stripComments(raw);
    if (isRuntimeTabletFile(relative)) {
      hardRuntimeHits.push(...collectMatches(text, HARD_RULES, relative));
      textualRuntimeSignals.push(...collectMatches(text, TEXTUAL_SIGNALS, relative));
    } else {
      nonRuntimeContextSignals.push(...collectMatches(text, [...HARD_RULES, ...TEXTUAL_SIGNALS], relative));
    }
  }

  const evidence = [createEvidence(ctx, 'Q1', 'architecture_boundary_scan_v4', 'Boundary scan calibrated to block only hard runtime dependencies, not labels or documentation words', {
    scannedFiles: files.length,
    hardRuntimeHits,
    textualRuntimeSignals,
    nonRuntimeContextSignals
  })];

  const findings = hardRuntimeHits.map((h, index) => finding({
    id: `Q1_${h.ruleId}_${index + 1}`,
    severity: h.severity,
    layer: h.layer || 'Architecture',
    title: h.title,
    detail: `${h.boundary} hard dependency signal in runtime Tablet file ${h.file}:${h.line}: ${h.match}`,
    file: h.file,
    evidence,
    recommendation: 'Remove hard runtime dependency or move it behind an optional local-first adapter declared in PQOS policy.'
  }));

  return {
    gateId: 'Q1',
    title: 'Architecture Boundaries Static V4',
    status: findings.some(f => ['S0','S1'].includes(f.severity)) ? 'BLOCKED' : 'READY',
    summary: `${hardRuntimeHits.length} hard runtime boundary signals, ${textualRuntimeSignals.length} runtime textual signals evidence-only, ${nonRuntimeContextSignals.length} non-runtime context signals.`,
    findings,
    evidence
  };
}
