import fs from 'node:fs';
import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { writeCustomerEvidenceLedger } from '../core/customer-assurance.mjs';

export const gateId = 'C7';
export const title = 'Customer Evidence Ledger';

function parseLedger(filePath) {
  const raw = fs.existsSync(filePath) ? fs.readFileSync(filePath, 'utf8') : '';
  const lines = raw.split(/\r?\n/).filter((line) => line.trim());
  const entries = [];
  const errors = [];
  lines.forEach((line, index) => {
    try { entries.push(JSON.parse(line)); }
    catch (error) { errors.push({ line: index + 1, error: error?.message || String(error) }); }
  });
  return { exists: fs.existsSync(filePath), lineCount: lines.length, entries, errors };
}

export async function run(ctx) {
  const priorGates = ctx.partialGateResults || [];
  const customerLedger = writeCustomerEvidenceLedger(ctx, priorGates);
  const rawLedger = parseLedger(path.join(ctx.runDir, 'QUALITY_EVIDENCE_LEDGER.jsonl'));
  const gatesWithoutEvidence = priorGates.filter((gate) => gate.status === 'READY' && (!gate.evidence || !gate.evidence.length)).map((gate) => gate.gateId);
  const blockedWithoutFindings = priorGates.filter((gate) => ['BLOCKED', 'ERROR'].includes(gate.status) && (!gate.findings || !gate.findings.length)).map((gate) => gate.gateId);
  const evidence = [createEvidence(ctx, 'C7', 'customer_evidence_ledger', 'Customer evidence ledger completeness and no-fake-green customer audit', {
    customerLedger,
    rawLedger: { exists: rawLedger.exists, lineCount: rawLedger.lineCount, parseErrors: rawLedger.errors },
    priorGateCount: priorGates.length,
    gatesWithoutEvidence,
    blockedWithoutFindings
  })];
  const findings = [];
  for (const error of rawLedger.errors) {
    findings.push(finding({
      id: `C7_LEDGER_PARSE_${error.line}`,
      severity: 'S2',
      layer: 'Audit',
      title: 'Evidence ledger line is not parseable JSON',
      detail: `QUALITY_EVIDENCE_LEDGER.jsonl line ${error.line}: ${error.error}`,
      file: 'QUALITY_EVIDENCE_LEDGER.jsonl',
      evidence,
      recommendation: 'Fix evidence writer output before using this run as customer evidence.'
    }));
  }
  for (const gateId of gatesWithoutEvidence) {
    findings.push(finding({
      id: `C7_NO_EVIDENCE_${gateId}`,
      severity: 'S1',
      layer: 'Quality',
      title: 'Customer gate passed without evidence',
      detail: `${gateId} reported READY without evidence.`,
      evidence,
      recommendation: 'Every customer-facing green must carry evidence.'
    }));
  }
  for (const gateId of blockedWithoutFindings) {
    findings.push(finding({
      id: `C7_BLOCKED_NO_FINDINGS_${gateId}`,
      severity: 'S1',
      layer: 'Quality',
      title: 'Customer gate blocked without findings',
      detail: `${gateId} reported BLOCKED/ERROR without actionable findings.`,
      evidence,
      recommendation: 'Blocked customer gates must explain what failed and what to do next.'
    }));
  }
  return {
    gateId: 'C7',
    title,
    status: findings.some((item) => ['S0', 'S1'].includes(item.severity)) ? 'BLOCKED' : findings.length ? 'READY_WITH_WARNINGS' : 'READY',
    summary: `${priorGates.length} prior gates ledgered; ${rawLedger.lineCount} raw evidence ledger entries parsed with ${rawLedger.errors.length} parse errors.`,
    findings,
    evidence
  };
}
