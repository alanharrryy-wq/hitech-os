import fs from 'node:fs';
import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { pathExists, listFiles, readTextSafe, rel, toPosix } from '../core/paths.mjs';
function includesAny(text, terms) { const lower = String(text).toLowerCase(); return terms.some(t => lower.includes(String(t).toLowerCase())); }

    export async function run(ctx) {
      const required = ['package.json','pnpm-workspace.yaml','products/tablet/app','products/pc/app','products/mobile/app','products/chart-lab/app','shared','prisma','quality'];
      const checks = required.map(r => ({ path: r, exists: pathExists(path.join(ctx.repoRoot, r)) }));
      const evidence = [createEvidence(ctx, 'Q0', 'repo_hygiene', 'Root structure and workspace presence', { checks })];
      const critical = new Set(['products/tablet/app','products/pc/app','products/mobile/app','prisma','quality']);
      const findings = checks.filter(c => !c.exists).map(c => finding({ id: `Q0_MISSING_${c.path.replaceAll('/','_')}`, severity: critical.has(c.path) ? 'S1' : 'S3', layer: 'Quality', title: 'Required project path missing', detail: `${c.path} was not found.`, file: c.path, recommendation: 'Restore or create the required project path.' }));
      return { gateId: 'Q0', title: 'Repo Hygiene', status: findings.some(f => ['S0','S1'].includes(f.severity)) ? 'BLOCKED' : 'READY', summary: `${checks.filter(c=>c.exists).length}/${checks.length} required paths found.`, findings, evidence };
    }
