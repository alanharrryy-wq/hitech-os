import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { exists, readText, rel, scanRepoText } from '../core/customer-assurance.mjs';

export const gateId = 'C2';
export const title = 'Demo Mode Safety';

function lineHits(text, file, patterns) {
  const hits = [];
  const lines = String(text || '').split(/\r?\n/);
  lines.forEach((line, index) => {
    for (const pattern of patterns) {
      if (pattern.regex.test(line)) hits.push({ id: pattern.id, file, line: index + 1, sample: line.trim().slice(0, 220), severity: pattern.severity, title: pattern.title });
      pattern.regex.lastIndex = 0;
    }
  });
  return hits;
}

const HARD_PATTERNS = [
  { id: 'DEMO_DEFAULT_PRODUCTION', severity: 'S1', title: 'Demo appears enabled by default for production', regex: /demo\s*(mode|enabled)?\s*[:=]\s*(true|1|yes).*production/i },
  { id: 'DEMO_REAL_DB_RESET', severity: 'S1', title: 'Demo reset appears to target real database', regex: /(demo|training).{0,80}(reset|wipe|truncate|delete).{0,120}(real|production|prod|database_url)/i },
  { id: 'DEMO_SYNC_REAL_ENDPOINT', severity: 'S2', title: 'Demo flow may call real sync endpoint', regex: /(demo|training).{0,120}(sync|ingest|webhook).{0,120}(production|prod|real)/i }
];

const SOFT_PATTERNS = [
  { id: 'DEMO_SIGNAL', severity: 'S4', title: 'Demo or training signal found', regex: /\b(demo|training|capacitacion|seed)\b/i }
];

export async function run(ctx) {
  const files = scanRepoText(ctx, ['products', 'shared', 'prisma', 'tools'], { maxFiles: 2500 });
  const hardHits = [];
  const softHits = [];
  for (const file of files) {
    const relative = rel(ctx, file);
    const text = readText(file);
    hardHits.push(...lineHits(text, relative, HARD_PATTERNS));
    softHits.push(...lineHits(text, relative, SOFT_PATTERNS).slice(0, 3));
  }
  const requiredDocs = ['docs/demo-mode.md', 'profiles/demo.json', 'policies/demo-safety-policy.json'];
  const docChecks = requiredDocs.map((relativePath) => ({ path: `quality/${relativePath}`, exists: exists(path.join(ctx.qualityRoot, relativePath)) }));
  const evidence = [createEvidence(ctx, 'C2', 'demo_safety_scan', 'Demo/training isolation scan for customer-safe presentations', {
    scannedFiles: files.length,
    hardHits,
    softSignalCount: softHits.length,
    softSignals: softHits.slice(0, 50),
    docChecks
  })];
  const findings = [];
  for (const hit of hardHits) {
    findings.push(finding({
      id: `C2_${hit.id}_${findings.length + 1}`,
      severity: hit.severity,
      layer: 'Customer',
      title: hit.title,
      detail: `${hit.file}:${hit.line}: ${hit.sample}`,
      file: hit.file,
      evidence,
      recommendation: 'Keep demo/training data isolated from real DB, real sync, production folios, and customer records.'
    }));
  }
  for (const item of docChecks.filter((item) => !item.exists)) {
    findings.push(finding({
      id: `C2_MISSING_${item.path.replace(/[^A-Za-z0-9]+/g, '_')}`,
      severity: 'S2',
      layer: 'Customer',
      title: 'Demo safety asset missing',
      detail: `${item.path} is required for repeatable customer demos.`,
      file: item.path,
      evidence,
      recommendation: 'Restore demo safety docs/profile/policy before using PRISMA in sales demos.'
    }));
  }
  return {
    gateId: 'C2',
    title,
    status: findings.some((item) => ['S0', 'S1'].includes(item.severity)) ? 'BLOCKED' : findings.length ? 'READY_WITH_WARNINGS' : 'READY',
    summary: `${hardHits.length} hard demo risks, ${softHits.length} demo/training evidence signals across ${files.length} files.`,
    findings,
    evidence
  };
}
