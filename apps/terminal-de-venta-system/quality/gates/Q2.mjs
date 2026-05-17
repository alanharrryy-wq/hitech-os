import fs from 'node:fs';
import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { pathExists, listFiles, readTextSafe, rel, toPosix } from '../core/paths.mjs';
function includesAny(text, terms) { const lower = String(text).toLowerCase(); return terms.some(t => lower.includes(String(t).toLowerCase())); }

    export async function run(ctx) {
      const registryPath = path.join(ctx.qualityRoot, 'contracts', 'contracts.json');
      const registry = JSON.parse(readTextSafe(registryPath));
      const ids = new Set();
      const problems = [];
      for (const c of registry.contracts || []) {
        if (!c.id) problems.push({ id: 'UNKNOWN', issue: 'missing id' });
        if (ids.has(c.id)) problems.push({ id: c.id, issue: 'duplicate id' });
        ids.add(c.id);
        for (const field of ['version','layer','defaultSeverity','ownedByGate']) if (!c[field]) problems.push({ id: c.id, issue: `missing ${field}` });
        if (!/^S[0-4]$/.test(c.defaultSeverity || '')) problems.push({ id: c.id, issue: 'invalid severity' });
      }
      const evidence = [createEvidence(ctx, 'Q2', 'contract_registry_validation', 'Contract registry validation and coverage matrix', { total: registry.contracts?.length || 0, problems })];
      const findings = problems.map((p, i) => finding({ id: `Q2_CONTRACT_${i+1}`, severity: 'S1', layer: 'Quality', title: 'Invalid contract registry entry', detail: `${p.id}: ${p.issue}`, file: 'quality/contracts/contracts.json', recommendation: 'Fix contract metadata before trusting gates.' }));
      return { gateId: 'Q2', title: 'Contract Registry', status: findings.length ? 'BLOCKED' : 'READY', summary: `${registry.contracts?.length || 0} contracts validated.`, findings, evidence };
    }
