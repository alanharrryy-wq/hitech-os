import fs from 'node:fs';
import path from 'node:path';
import { sha256Text } from './checksums.mjs';
import { redact } from './redaction.mjs';
import { writeJson } from './safe-json.mjs';

function safePayloadFrom(payload) {
  const raw = typeof payload === 'string' ? payload : JSON.stringify(payload, null, 2);
  const safeRaw = redact(raw);
  if (typeof payload === 'string') return safeRaw;
  try {
    return JSON.parse(safeRaw);
  } catch {
    return { redactedText: safeRaw };
  }
}

export function createEvidence(ctx, gateId, type, summary, payload) {
  const evidenceId = `${gateId}_${type}_${ctx.evidenceCounter++}`;
  const safePayload = safePayloadFrom(payload);
  const body = {
    schemaVersion: '1.0',
    runId: ctx.runId,
    evidenceId,
    gateId,
    type,
    summary,
    createdAt: new Date().toISOString(),
    payload: safePayload
  };
  const relPath = path.join('evidence', `${evidenceId}.json`);
  const absPath = path.join(ctx.runDir, relPath);
  fs.mkdirSync(path.dirname(absPath), { recursive: true });
  writeJson(absPath, body);
  const canonicalBody = JSON.stringify(body);
  const entry = {
    schemaVersion: '1.0',
    runId: ctx.runId,
    evidenceId,
    gateId,
    type,
    path: relPath.split(String.fromCharCode(92)).join('/'),
    sha256: sha256Text(canonicalBody),
    summary
  };
  fs.appendFileSync(path.join(ctx.runDir, 'QUALITY_EVIDENCE_LEDGER.jsonl'), `${JSON.stringify(entry)}\n`, 'utf8');
  return entry;
}
