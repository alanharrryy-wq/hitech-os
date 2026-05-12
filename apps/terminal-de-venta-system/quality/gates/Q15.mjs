import fs from 'node:fs';
import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { pathExists, listFiles, readTextSafe, rel, toPosix } from '../core/paths.mjs';
function includesAny(text, terms) { const lower = String(text).toLowerCase(); return terms.some(t => lower.includes(String(t).toLowerCase())); }

    export async function run(ctx) {
      const previous = ctx.partialGateResults || [];
      const noEvidence = previous.filter(g => g.status === 'READY' && (!g.evidence || !g.evidence.length)).map(g => g.gateId);
      const skippedCritical = previous.filter(g => ['Q0','Q1','Q2','Q3','Q4','Q6','Q13'].includes(g.gateId) && ['SKIPPED','UNKNOWN','NOT_APPLICABLE'].includes(g.status)).map(g => g.gateId);
      const cloudflareBase = ['commit','pr','release'].includes(ctx.profile) && previous.some(g => JSON.stringify(g).toLowerCase().includes('cloudflare required'));
      const evidence = [createEvidence(ctx, 'Q15', 'release_governor_basic', 'No-fake-green and phase decision audit', { previousGateCount: previous.length, noEvidence, skippedCritical, cloudflareBase })];
      const findings = [];
      for (const g of noEvidence) findings.push(finding({ id: `Q15_NO_EVIDENCE_${g}`, severity: 'S1', layer: 'Quality', title: 'Gate passed without evidence', detail: `${g} passed without evidence.`, recommendation: 'Make gate emit evidence or block.' }));
      for (const g of skippedCritical) findings.push(finding({ id: `Q15_SKIPPED_${g}`, severity: 'S1', layer: 'Quality', title: 'Critical gate skipped', detail: `${g} is critical and cannot be skipped in profile ${ctx.profile}.` }));
      if (cloudflareBase) findings.push(finding({ id: 'Q15_CLOUDFLARE_BASE_BLOCKER', severity: 'S1', layer: 'Cloudflare', title: 'Cloudflare leaked into base profile', detail: 'Cloudflare cannot block base commit/pr/release profile.' }));
      return { gateId: 'Q15', title: 'Release Governor Basic', status: findings.length ? 'BLOCKED' : 'READY', summary: `${previous.length} prior gates audited.`, findings, evidence };
    }
