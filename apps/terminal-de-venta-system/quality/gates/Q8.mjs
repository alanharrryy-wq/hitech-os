import fs from 'node:fs';
import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { pathExists, listFiles, toPosix } from '../core/paths.mjs';
import { workspaceScriptMatrix } from '../core/package-scripts.mjs';

function readSafe(p) { try { return fs.readFileSync(p, 'utf8'); } catch { return ''; } }
function readJsonSafe(p) { try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch (error) { return { __error: error.message || String(error) }; } }
function rel(ctx, p) { return toPosix(path.relative(ctx.repoRoot, p)); }

export async function run(ctx) {
  const mobileRoot = path.join(ctx.repoRoot, ctx.config.roots.mobile);
  const expectedRoutes = [
    'products/mobile/app/app/api/mobile/health/route.ts',
    'products/mobile/app/app/api/mobile/snapshot/route.ts',
    'products/mobile/app/app/api/mobile/data-quality/route.ts',
    'products/mobile/app/app/api/mobile/alerts/route.ts',
    'products/mobile/app/app/api/mobile/action-inbox/route.ts',
    'products/mobile/app/app/api/mobile/decision-ledger/route.ts',
    'products/mobile/app/app/api/mobile/health-radar/route.ts',
    'products/mobile/app/app/api/mobile/pulse-timeline/route.ts',
    'products/mobile/app/app/api/mobile/daily-brief/route.ts'
  ].map(p => ({ path: p, exists: pathExists(path.join(ctx.repoRoot, p)) }));
  const mobileFiles = pathExists(mobileRoot) ? listFiles(mobileRoot, { maxBytes: ctx.config.scan.maxFileBytes, extensions: ['.ts','.tsx','.js','.mjs'], ignore: ctx.config.ignore }) : [];
  const truthTerms = ['freshness', 'confidence', 'partial', 'offline', 'snapshot', 'data-quality', 'decision-ledger'];
  const termCounts = Object.fromEntries(truthTerms.map(t => [t, 0]));
  const mutationSignals = [];
  for (const file of mobileFiles) {
    const text = readSafe(file);
    const lower = text.toLowerCase();
    for (const term of truthTerms) if (lower.includes(term)) termCounts[term] += 1;
    if (/export\s+async\s+function\s+(POST|PUT|PATCH|DELETE)\b/.test(text)) mutationSignals.push(rel(ctx, file));
  }
  const evidence = [createEvidence(ctx, 'Q8', 'mobile_supervision_surface', 'Mobile supervision, truthfulness and mutation surface', { expectedRoutes, scannedFiles: mobileFiles.length, termCounts, mutationSignals })];
  const findings = [];
  const missingCore = expectedRoutes.filter(r => !r.exists && /health|snapshot|data-quality/.test(r.path));
  for (const r of missingCore) findings.push(finding({ id: `Q8_MOBILE_CORE_ROUTE_MISSING_${r.path.replaceAll('/','_')}`, severity: 'S2', layer: 'Mobile', title: 'Mobile supervision core route missing', detail: `${r.path} was not found.`, file: r.path, evidence, recommendation: 'Restore route or document alternate Mobile supervision contract.' }));
  if ((termCounts.freshness || 0) === 0 || (termCounts.confidence || 0) === 0) findings.push(finding({ id: 'Q8_MOBILE_TRUTH_TERMS_MISSING', severity: 'S3', layer: 'Mobile', title: 'Mobile truthfulness signals weak', detail: 'Freshness/confidence signals were not both detected.', evidence, recommendation: 'Ensure Mobile exposes freshness and confidence in its view models/API.' }));
  for (const file of mutationSignals) findings.push(finding({ id: `Q8_MOBILE_MUTATION_SIGNAL_${findings.length+1}`, severity: 'S3', layer: 'Mobile', title: 'Mobile mutation route signal', detail: `Mobile route exports a mutation verb in ${file}. This is evidence-only in Phase 2 unless it writes operational truth.`, file, evidence, recommendation: 'Confirm Mobile supervises/actions without becoming the authority of operational record.' }));
  return { gateId: 'Q8', title: 'Mobile Supervision Surface', status: findings.some(f => ['S0','S1'].includes(f.severity)) ? 'BLOCKED' : 'READY', summary: `${expectedRoutes.filter(r=>r.exists).length}/${expectedRoutes.length} Mobile supervision routes found.`, findings, evidence };
}
