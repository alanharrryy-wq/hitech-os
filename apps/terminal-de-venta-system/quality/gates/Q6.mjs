import fs from 'node:fs';
import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { pathExists, listFiles, readTextSafe, rel, toPosix } from '../core/paths.mjs';
function includesAny(text, terms) { const lower = String(text).toLowerCase(); return terms.some(t => lower.includes(String(t).toLowerCase())); }

    export async function run(ctx) {
      const rootNames = ['tablet', 'pc', 'mobile', 'shared', 'prisma'];
      const roots = rootNames.map(name => path.join(ctx.repoRoot, ctx.config.roots[name])).filter(pathExists);
      const keywords = ['outbox', 'sync', 'ingest', 'idempot', 'conflict', 'checkpoint', 'replay', 'pending', 'failed'];
      const counts = Object.fromEntries(keywords.map(k => [k, 0]));
      let scanned = 0;
      for (const root of roots) for (const f of listFiles(root, { maxBytes: ctx.config.scan.maxFileBytes, extensions: ctx.config.scan.extensions, ignore: ctx.config.ignore })) { scanned++; const text = readTextSafe(f).toLowerCase(); for (const k of keywords) if (text.includes(k)) counts[k]++; }
      const evidence = [createEvidence(ctx, 'Q6', 'outbox_sync_surface', 'Outbox, sync, idempotency and checkpoint surface scan', { scannedFiles: scanned, counts })];
      const findings = [];
      if ((counts.outbox || 0) === 0) findings.push(finding({ id: 'Q6_OUTBOX_SURFACE_MISSING', severity: 'S1', layer: 'Core', title: 'Outbox surface not detected', detail: 'No outbox signal was detected in scanned source.', recommendation: 'Restore or declare outbox ownership before claiming sync integrity.' }));
      if ((counts.idempot || 0) === 0) findings.push(finding({ id: 'Q6_IDEMPOTENCY_SURFACE_MISSING', severity: 'S1', layer: 'Core', title: 'Idempotency surface not detected', detail: 'No idempotency signal was detected in scanned source.', recommendation: 'Restore idempotency guard or document equivalent mechanism.' }));
      return { gateId: 'Q6', title: 'Outbox & Sync Integrity Static', status: findings.length ? 'BLOCKED' : 'READY', summary: `Scanned ${scanned} files for sync surface.`, findings, evidence };
    }
