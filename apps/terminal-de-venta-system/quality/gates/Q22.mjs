import fs from 'node:fs';
import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';

function runDir(ctx) {
  return ctx.runDir || ctx.outputDir || ctx.outDir || process.cwd();
}

function readSafe(file) {
  try { return fs.readFileSync(file, 'utf8'); } catch { return ''; }
}

function evidenceDir(ctx) {
  return path.join(runDir(ctx), 'evidence');
}

function ledgerPath(ctx) {
  return path.join(runDir(ctx), 'QUALITY_EVIDENCE_LEDGER.jsonl');
}

function parseJsonObjectStream(raw) {
  const entries = [];
  const errors = [];
  let i = 0;

  while (i < raw.length) {
    while (i < raw.length) {
      const ch = raw[i];
      if (/\s/.test(ch)) { i += 1; continue; }
      if (ch === '\\' && raw[i + 1] === 'n') { i += 2; continue; }
      break;
    }

    if (i >= raw.length) break;

    if (raw[i] !== '{') {
      const near = raw.slice(i, i + 80).replace(/\s+/g, ' ');
      errors.push(`Unexpected token outside JSON object near: ${near}`);
      break;
    }

    const start = i;
    let depth = 0;
    let inString = false;
    let escaped = false;

    for (; i < raw.length; i += 1) {
      const ch = raw[i];

      if (inString) {
        if (escaped) {
          escaped = false;
        } else if (ch === '\\') {
          escaped = true;
        } else if (ch === '"') {
          inString = false;
        }
        continue;
      }

      if (ch === '"') {
        inString = true;
        continue;
      }

      if (ch === '{') depth += 1;
      if (ch === '}') depth -= 1;

      if (depth === 0) {
        const candidate = raw.slice(start, i + 1);
        try {
          entries.push(JSON.parse(candidate));
        } catch (error) {
          errors.push(`JSON parse error at object ${entries.length + 1}: ${error.message}`);
        }
        i += 1;
        break;
      }
    }

    if (depth !== 0) {
      errors.push('Last JSON object is incomplete.');
      break;
    }
  }

  return { entries, errors };
}

function parseLedger(ctx) {
  const file = ledgerPath(ctx);
  const raw = readSafe(file);
  if (!raw.trim()) return { path: file, exists: fs.existsSync(file), entries: [], errors: [] };
  const parsed = parseJsonObjectStream(raw);
  return { path: file, exists: true, ...parsed };
}

function validSha(value) {
  return typeof value === 'string' && /^[a-f0-9]{64}$/i.test(value);
}

export async function run(ctx) {
  const parsed = parseLedger(ctx);
  const findings = [];
  const duplicateIds = [];
  const seen = new Set();
  const malformed = [];

  for (const entry of parsed.entries) {
    if (!entry.evidenceId) malformed.push({ reason: 'missing evidenceId', entry });
    if (!entry.gateId) malformed.push({ reason: 'missing gateId', entryId: entry.evidenceId || null });
    if (!entry.path) malformed.push({ reason: 'missing path', entryId: entry.evidenceId || null });
    if (!entry.summary) malformed.push({ reason: 'missing summary', entryId: entry.evidenceId || null });
    if (entry.sha256 && !validSha(entry.sha256)) malformed.push({ reason: 'invalid sha256', entryId: entry.evidenceId || null, sha256: entry.sha256 });

    if (entry.evidenceId) {
      if (seen.has(entry.evidenceId)) duplicateIds.push(entry.evidenceId);
      seen.add(entry.evidenceId);
    }
  }

  const evidenceFiles = fs.existsSync(evidenceDir(ctx))
    ? fs.readdirSync(evidenceDir(ctx)).filter(name => name.endsWith('.json')).sort()
    : [];

  const evidence = [createEvidence(ctx, 'Q22', 'evidence_ledger_check', 'Evidence ledger integrity with robust JSON object stream parser', {
    ledgerPath: 'QUALITY_EVIDENCE_LEDGER.jsonl',
    parser: 'json-object-stream-supports-real-newlines-literal-backslash-n-and-concatenated-json',
    exists: parsed.exists,
    entryCount: parsed.entries.length,
    parseErrors: parsed.errors,
    malformed,
    duplicateIds,
    evidenceFileCount: evidenceFiles.length,
    evidenceFiles: evidenceFiles.slice(0, 120)
  })];

  if (!parsed.exists) {
    findings.push(finding({
      id: 'Q22_LEDGER_MISSING',
      severity: 'S3',
      layer: 'Evidence',
      title: 'Evidence ledger missing',
      detail: 'QUALITY_EVIDENCE_LEDGER.jsonl was not found in the current run directory.',
      file: 'QUALITY_EVIDENCE_LEDGER.jsonl',
      evidence,
      recommendation: 'Confirm evidence writer is enabled for PQOS runs.'
    }));
  }

  for (const error of parsed.errors) {
    findings.push(finding({
      id: `Q22_LEDGER_PARSE_${findings.length + 1}`,
      severity: 'S3',
      layer: 'Evidence',
      title: 'Evidence ledger parse issue',
      detail: error,
      file: 'QUALITY_EVIDENCE_LEDGER.jsonl',
      evidence,
      recommendation: 'Ledger should be valid JSON object stream. Literal \\n separators are supported by Q22.'
    }));
  }

  for (const item of malformed.slice(0, 25)) {
    findings.push(finding({
      id: `Q22_LEDGER_ENTRY_MALFORMED_${findings.length + 1}`,
      severity: 'S3',
      layer: 'Evidence',
      title: 'Evidence ledger entry missing expected metadata',
      detail: `${item.reason} for ${item.entryId || 'unknown evidence entry'}.`,
      file: 'QUALITY_EVIDENCE_LEDGER.jsonl',
      evidence,
      recommendation: 'Ensure evidence entries include evidenceId, gateId, path, summary and sha256 when available.'
    }));
  }

  for (const dup of duplicateIds.slice(0, 25)) {
    findings.push(finding({
      id: `Q22_DUPLICATE_EVIDENCE_ID_${findings.length + 1}`,
      severity: 'S3',
      layer: 'Evidence',
      title: 'Duplicate evidence id in ledger',
      detail: `Duplicate evidenceId detected: ${dup}.`,
      file: 'QUALITY_EVIDENCE_LEDGER.jsonl',
      evidence,
      recommendation: 'Evidence ids should be unique within a run.'
    }));
  }

  return {
    gateId: 'Q22',
    title: 'Evidence Ledger Integrity',
    status: findings.some(f => ['S0', 'S1'].includes(f.severity)) ? 'BLOCKED' : 'READY',
    summary: `${parsed.entries.length} ledger entries parsed, ${parsed.errors.length} parse errors, ${malformed.length} malformed entries, ${duplicateIds.length} duplicates.`,
    findings,
    evidence
  };
}
