import fs from 'node:fs';
import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { pathExists, listFiles, readTextSafe, rel, toPosix } from '../core/paths.mjs';
function includesAny(text, terms) { const lower = String(text).toLowerCase(); return terms.some(t => lower.includes(String(t).toLowerCase())); }

    export async function run(ctx) {
      const candidates = ['products/tablet/app/app/api/health/route.ts', 'products/mobile/app/app/api/mobile/health/route.ts', 'products/pc/app/app/api/backoffice/audit/route.ts'];
      const checks = candidates.map(p => ({ path: p, exists: pathExists(path.join(ctx.repoRoot, p)) }));
      const writeTest = path.join(ctx.runDir, 'evidence', 'observability-write-test.tmp');
      fs.mkdirSync(path.dirname(writeTest), { recursive: true });
      fs.writeFileSync(writeTest, 'ok', 'utf8');
      const evidence = [createEvidence(ctx, 'Q9', 'observability_surface', 'Observability and evidence write surface', { checks, evidenceWriteTest: fs.existsSync(writeTest) })];
      const findings = [];
      if (!fs.existsSync(writeTest)) findings.push(finding({ id: 'Q9_EVIDENCE_WRITE_FAILED', severity: 'S1', layer: 'Quality', title: 'Evidence write failed', detail: 'PQOS could not write evidence into run directory.' }));
      if (checks.every(c => !c.exists)) findings.push(finding({ id: 'Q9_HEALTH_SURFACE_MISSING', severity: 'S3', layer: 'Observability', title: 'Health surface not detected', detail: 'No expected health/audit route was found.', recommendation: 'Add or declare health surfaces in a later phase.' }));
      return { gateId: 'Q9', title: 'Observability Static', status: findings.some(f => ['S0','S1'].includes(f.severity)) ? 'BLOCKED' : 'READY', summary: `${checks.filter(c => c.exists).length}/${checks.length} observability route signals found.`, findings, evidence };
    }
