import fs from 'node:fs';
import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';

const REQUIRED_GATES = ['Q21', 'Q22', 'Q23', 'Q24', 'Q25'];

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
      errors.push(`Unexpected token outside JSON object near: ${raw.slice(i, i + 80).replace(/\s+/g, ' ')}`);
      break;
    }

    const start = i;
    let depth = 0;
    let inString = false;
    let escaped = false;

    for (; i < raw.length; i += 1) {
      const ch = raw[i];

      if (inString) {
        if (escaped) escaped = false;
        else if (ch === '\\') escaped = true;
        else if (ch === '"') inString = false;
        continue;
      }

      if (ch === '"') { inString = true; continue; }
      if (ch === '{') depth += 1;
      if (ch === '}') depth -= 1;

      if (depth === 0) {
        const candidate = raw.slice(start, i + 1);
        try { entries.push(JSON.parse(candidate)); }
        catch (error) { errors.push(`JSON parse error at object ${entries.length + 1}: ${error.message}`); }
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

function evidenceFilesByGate(ctx) {
  const dir = evidenceDir(ctx);
  const out = Object.fromEntries(REQUIRED_GATES.map(g => [g, []]));
  if (!fs.existsSync(dir)) return out;

  for (const name of fs.readdirSync(dir)) {
    for (const gate of REQUIRED_GATES) {
      if (name.startsWith(`${gate}_`) && name.endsWith('.json')) {
        out[gate].push(name);
      }
    }
  }

  return out;
}

export async function run(ctx) {
  const preliminary = parseLedger(ctx);
  const evidenceFiles = evidenceFilesByGate(ctx);

  const preSummary = {
    ledgerExists: preliminary.exists,
    ledgerEntryCount: preliminary.entries.length,
    ledgerParseErrors: preliminary.errors,
    evidenceFiles
  };

  const evidence = [createEvidence(ctx, 'Q25', 'audit_trail_completeness_check', 'Audit trail completeness across Phase 4 data truth gates', preSummary)];

  const parsed = parseLedger(ctx);
  const filesByGate = evidenceFilesByGate(ctx);
  const gates = {};

  for (const gate of REQUIRED_GATES) {
    const ledgerHits = parsed.entries.filter(entry => entry.gateId === gate || String(entry.evidenceId || '').startsWith(`${gate}_`));
    const fileHits = filesByGate[gate] || [];
    const currentGateEvidence = gate === 'Q25' ? evidence.length : 0;

    gates[gate] = {
      ledgerHits: ledgerHits.length,
      fileHits: fileHits.length,
      currentGateEvidence,
      present: ledgerHits.length > 0 || fileHits.length > 0 || currentGateEvidence > 0
    };
  }

  const findings = [];

  for (const error of parsed.errors) {
    findings.push(finding({
      id: `Q25_LEDGER_PARSE_${findings.length + 1}`,
      severity: 'S3',
      layer: 'Audit',
      title: 'Audit ledger parse issue',
      detail: error,
      file: 'QUALITY_EVIDENCE_LEDGER.jsonl',
      evidence,
      recommendation: 'Ledger parser supports literal \\n separators. Inspect malformed entry if this persists.'
    }));
  }

  for (const gate of REQUIRED_GATES) {
    if (!gates[gate].present) {
      findings.push(finding({
        id: `Q25_MISSING_GATE_${gate}`,
        severity: 'S2',
        layer: 'Audit',
        title: 'Audit trail missing Phase 4 gate evidence',
        detail: `${gate} did not appear in ledger or evidence files for this run.`,
        file: 'QUALITY_EVIDENCE_LEDGER.jsonl',
        evidence,
        recommendation: `Ensure ${gate} runs before Q25 and produces evidence through createEvidence.`
      }));
    }
  }

  return {
    gateId: 'Q25',
    title: 'Audit Trail Completeness',
    status: findings.some(f => ['S0', 'S1'].includes(f.severity)) ? 'BLOCKED' : 'READY',
    summary: `${Object.values(gates).filter(g => g.present).length}/${REQUIRED_GATES.length} Phase 4 gates have audit evidence.`,
    findings,
    evidence
  };
}
