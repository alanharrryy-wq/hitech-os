import fs from 'node:fs';
import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { listFiles, toPosix } from '../core/paths.mjs';

function readSafe(p) { try { return fs.readFileSync(p, 'utf8'); } catch { return ''; } }
function rel(ctx, p) { return toPosix(path.relative(ctx.repoRoot, p)); }

const SECRET_PATTERNS = [
  { id: 'PRIVATE_KEY', pattern: /-----BEGIN [A-Z ]*PRIVATE KEY-----/ },
  { id: 'GITHUB_TOKEN', pattern: /ghp_[A-Za-z0-9_]{20,}/ },
  { id: 'OPENAI_KEY', pattern: /sk-[A-Za-z0-9_-]{20,}/ },
  { id: 'SLACK_TOKEN', pattern: /xox[baprs]-[A-Za-z0-9-]{20,}/ }
];

const DANGEROUS_COMMAND_PATTERNS = [
  { id: 'RM_RF_ROOTISH', pattern: /\brm\s+-rf\s+['"]?(?:[A-Z]:[\\/]|\/)(?:\s|$)/i },
  { id: 'REMOVE_ITEM_FORCE_RECURSE', pattern: /\bRemove-Item\b(?=.*\b-Recurse\b)(?=.*\b-Force\b)/i },
  { id: 'RMDIR_FORCE_ROOTISH', pattern: /\brmdir\b(?=.*\/s)(?=.*\/q).*?[A-Z]:[\\/]/i }
];

function shouldSkipDestructiveLine(relPath, line) {
  const p = relPath.replaceAll('\\', '/').toLowerCase();
  const l = line.trim();
  if (p === 'quality/gates/q13.mjs') return true;
  if (l.includes('DANGEROUS_COMMAND_PATTERNS')) return true;
  if (l.includes('REMOVE_ITEM_FORCE_RECURSE') || l.includes('RM_RF_ROOTISH')) return true;
  if (l.startsWith('//') || l.startsWith('*')) return true;
  return false;
}

function lineHits(text, relPath, patterns, skipLineFn = () => false) {
  const hits = [];
  const lines = text.split(/\r?\n/);
  lines.forEach((line, index) => {
    if (skipLineFn(relPath, line)) return;
    for (const rule of patterns) {
      if (rule.pattern.test(line)) hits.push({ ruleId: rule.id, line: index + 1, sample: line.trim().slice(0, 220) });
    }
  });
  return hits;
}

export async function run(ctx) {
  const roots = ['quality', 'products', 'shared', 'prisma', 'tools/prisma', 'prisma-control-center/internal/py'].map(r => path.join(ctx.repoRoot, r));
  const secretHits = [];
  const destructiveHits = [];
  let scanned = 0;

  for (const root of roots) {
    for (const file of listFiles(root, { maxBytes: ctx.config.scan.maxFileBytes, extensions: ctx.config.scan.extensions, ignore: ctx.config.ignore })) {
      scanned++;
      const relative = rel(ctx, file);
      const text = readSafe(file);
      for (const h of lineHits(text, relative, SECRET_PATTERNS)) secretHits.push({ file: relative, ...h });
      for (const h of lineHits(text, relative, DANGEROUS_COMMAND_PATTERNS, shouldSkipDestructiveLine)) destructiveHits.push({ file: relative, ...h });
    }
  }

  const evidence = [createEvidence(ctx, 'Q13', 'security_safety_static_v3', 'Secret and destructive-command static scan with scanner self-pattern suppression', {
    scannedFiles: scanned,
    secretHits,
    destructiveHits,
    suppressedSelfScanner: true
  })];

  const findings = [];
  for (const h of secretHits) {
    findings.push(finding({
      id: `Q13_SECRET_${findings.length + 1}`,
      severity: 'S1',
      layer: 'Security',
      title: 'Secret marker detected',
      detail: `Secret-like content found in ${h.file}:${h.line}.`,
      file: h.file,
      evidence,
      recommendation: 'Remove the secret and rotate it if it is real.'
    }));
  }
  for (const h of destructiveHits) {
    findings.push(finding({
      id: `Q13_DESTRUCTIVE_${findings.length + 1}`,
      severity: 'S1',
      layer: 'Safety',
      title: 'Dangerous destructive command signal',
      detail: `Potential broad destructive command in ${h.file}:${h.line}.`,
      file: h.file,
      evidence,
      recommendation: 'Wrap destructive actions with explicit allowlist, dry-run, backup and rollback.'
    }));
  }

  return {
    gateId: 'Q13',
    title: 'Security & Safety Static V3',
    status: findings.length ? 'BLOCKED' : 'READY',
    summary: `${secretHits.length} secret signals, ${destructiveHits.length} destructive command signals.`,
    findings,
    evidence
  };
}
