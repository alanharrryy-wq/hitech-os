        import fs from 'node:fs';
        import path from 'node:path';
        import { sha256Text } from './checksums.mjs';
        import { redact } from './redaction.mjs';
        export function createEvidence(ctx, gateId, type, summary, payload) {
          const evidenceId = `${gateId}_${type}_${ctx.evidenceCounter++}`;
          const raw = typeof payload === 'string' ? payload : JSON.stringify(payload, null, 2);
          const safeRaw = redact(raw);
          const safePayload = typeof payload === 'string' ? safeRaw : JSON.parse(safeRaw);
          const body = { schemaVersion: '1.0', runId: ctx.runId, evidenceId, gateId, type, summary, createdAt: new Date().toISOString(), payload: safePayload };
          const relPath = path.join('evidence', `${evidenceId}.json`);
          const absPath = path.join(ctx.runDir, relPath);
          fs.mkdirSync(path.dirname(absPath), { recursive: true });
          fs.writeFileSync(absPath, JSON.stringify(body, null, 2) + '\\n', 'utf8');
          const entry = { evidenceId, gateId, type, path: relPath.split(String.fromCharCode(92)).join('/'), sha256: sha256Text(JSON.stringify(body)), summary };
          fs.appendFileSync(path.join(ctx.runDir, 'QUALITY_EVIDENCE_LEDGER.jsonl'), JSON.stringify(entry) + '\\n', 'utf8');
          return entry;
        }
