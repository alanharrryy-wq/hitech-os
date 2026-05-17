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
  const pcRoot = path.join(ctx.repoRoot, ctx.config.roots.pc);
  const requiredPaths = [
    'products/pc/app/package.json',
    'products/pc/app/app/api/backoffice/audit/route.ts',
    'products/pc/app/app/api/backoffice/sync/route.ts',
    'products/pc/app/app/api/backoffice/sync/ingest/route.ts',
    'products/pc/app/app/dashboard/page.tsx'
  ].map(p => ({ path: p, exists: pathExists(path.join(ctx.repoRoot, p)) }));
  const pcFiles = pathExists(pcRoot) ? listFiles(pcRoot, { maxBytes: ctx.config.scan.maxFileBytes, extensions: ['.ts','.tsx','.js','.mjs'], ignore: ctx.config.ignore }) : [];
  const governanceTerms = ['audit', 'sync', 'ingest', 'dashboard', 'governance', 'conflict'];
  const termCounts = Object.fromEntries(governanceTerms.map(t => [t, 0]));
  for (const file of pcFiles) {
    const text = readSafe(file).toLowerCase();
    for (const term of governanceTerms) if (text.includes(term)) termCounts[term] += 1;
  }
  const evidence = [createEvidence(ctx, 'Q7', 'pc_governance_surface', 'PC governance and backoffice route surface', { requiredPaths, scannedFiles: pcFiles.length, termCounts })];
  const findings = [];
  for (const p of requiredPaths.filter(x => !x.exists)) {
    findings.push(finding({ id: `Q7_PC_SURFACE_MISSING_${p.path.replaceAll('/','_')}`, severity: 'S3', layer: 'PC', title: 'PC governance surface missing', detail: `${p.path} was not found.`, file: p.path, evidence, recommendation: 'Restore route/page or declare alternate governance surface.' }));
  }
  if ((termCounts.audit || 0) === 0) findings.push(finding({ id: 'Q7_AUDIT_SURFACE_NOT_DETECTED', severity: 'S3', layer: 'PC', title: 'Audit vocabulary not detected in PC source', detail: 'PC governance should expose audit language/surfaces.', evidence, recommendation: 'Confirm audit surface ownership.' }));
  return { gateId: 'Q7', title: 'PC Governance Surface', status: findings.some(f => ['S0','S1'].includes(f.severity)) ? 'BLOCKED' : 'READY', summary: `${requiredPaths.filter(p=>p.exists).length}/${requiredPaths.length} PC governance paths found.`, findings, evidence };
}
