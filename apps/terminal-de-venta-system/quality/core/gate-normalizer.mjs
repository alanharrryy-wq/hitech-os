import { finding } from './result-types.mjs';

const BLOCKING_SEVERITIES = new Set(['S0', 'S1']);
const WARNING_SEVERITIES = new Set(['S2', 'S3']);

function asArray(value) {
  if (!value) return [];
  return Array.isArray(value) ? value : [value];
}

function cleanId(value, fallback) {
  const raw = String(value || fallback || 'UNKNOWN_GATE').trim();
  return raw || 'UNKNOWN_GATE';
}

function normalizeStatus(status, findings) {
  const raw = String(status || '').trim().toUpperCase();
  if (raw === 'PASS') return 'READY';
  if (raw === 'WARN' || raw === 'WARNING') return 'READY_WITH_WARNINGS';
  if (raw === 'FAIL' || raw === 'FAILED') return 'BLOCKED';
  if (raw === 'ERROR') return 'ERROR';
  if (raw === 'SKIPPED') return 'SKIPPED';
  if (raw === 'NOT_APPLICABLE' || raw === 'N/A') return 'NOT_APPLICABLE';
  if (raw === 'DEGRADED') return 'DEGRADED';
  if (raw === 'BLOCKED') return 'BLOCKED';
  if (raw === 'READY_WITH_WARNINGS') return 'READY_WITH_WARNINGS';
  if (raw === 'READY') return 'READY';
  if (findings.some((item) => BLOCKING_SEVERITIES.has(item.severity))) return 'BLOCKED';
  if (findings.some((item) => WARNING_SEVERITIES.has(item.severity))) return 'READY_WITH_WARNINGS';
  return 'READY';
}

function normalizeFinding(raw, gateId, index, fallbackSeverity = 'S4') {
  if (raw && typeof raw === 'object' && raw.title && raw.detail) {
    return {
      id: cleanId(raw.id, `${gateId}_FINDING_${index + 1}`),
      severity: /^S[0-4]$/.test(raw.severity || '') ? raw.severity : fallbackSeverity,
      layer: raw.layer || 'Quality',
      title: raw.title,
      detail: String(raw.detail),
      evidence: asArray(raw.evidence),
      file: raw.file ?? null,
      recommendation: raw.recommendation || 'Review the gate evidence and remediate before release.'
    };
  }
  return finding({
    id: `${gateId}_FINDING_${index + 1}`,
    severity: fallbackSeverity,
    layer: 'Quality',
    title: `${gateId} finding`,
    detail: typeof raw === 'string' ? raw : JSON.stringify(raw),
    evidence: [],
    recommendation: 'Review the gate evidence and remediate before release.'
  });
}

function findingFromMessage(gateId, kind, message, index, severity) {
  return finding({
    id: `${gateId}_${kind}_${index + 1}`,
    severity,
    layer: 'Quality',
    title: `${gateId} ${kind.toLowerCase().replaceAll('_', ' ')}`,
    detail: String(message),
    recommendation: severity === 'S1'
      ? 'Resolve this blocker before claiming readiness.'
      : 'Review this warning before release handoff.'
  });
}

function normalizeEvidence(rawEvidence, gateId) {
  return asArray(rawEvidence).map((item, index) => {
    if (item && typeof item === 'object') return item;
    return {
      schemaVersion: '1.0',
      evidenceId: `${gateId}_INLINE_${index + 1}`,
      gateId,
      type: 'inline',
      summary: String(item),
      payload: { value: item }
    };
  });
}

export function normalizeGateResult(raw, fallbackGateId) {
  const source = raw && typeof raw === 'object' ? raw : {};
  const gateId = cleanId(source.gateId || source.id || source.code, fallbackGateId);
  const title = source.title || gateId;
  const evidence = normalizeEvidence(source.evidence, gateId);
  const baseFindings = asArray(source.findings).map((item, index) => normalizeFinding(item, gateId, index));
  const blockerFindings = asArray(source.blockers).map((item, index) => findingFromMessage(gateId, 'BLOCKER', item, index, 'S1'));
  const warningFindings = asArray(source.warnings).map((item, index) => findingFromMessage(gateId, 'WARNING', item, index, 'S3'));
  const findings = [...baseFindings, ...blockerFindings, ...warningFindings];
  let status = normalizeStatus(source.status, findings);
  if (findings.some((item) => BLOCKING_SEVERITIES.has(item.severity))) status = 'BLOCKED';
  else if (status === 'READY' && findings.some((item) => WARNING_SEVERITIES.has(item.severity))) status = 'READY_WITH_WARNINGS';
  const summary = source.summary || `${gateId}: ${findings.length} findings, ${evidence.length} evidence items`;
  return {
    ...source,
    gateId,
    title,
    status,
    summary,
    findings,
    evidence,
    normalizedFrom: source.gateId ? undefined : (source.id || source.code ? 'legacy-id-code' : 'fallback'),
    legacyStatus: source.status && source.status !== status ? source.status : undefined
  };
}

export function assertNoFakeGreen(gateResult) {
  const findings = asArray(gateResult.findings);
  if (gateResult.status === 'READY' && findings.some((item) => BLOCKING_SEVERITIES.has(item.severity))) {
    return `${gateResult.gateId} is READY with blocking findings.`;
  }
  if (gateResult.status === 'READY' && (!gateResult.evidence || gateResult.evidence.length === 0)) {
    return `${gateResult.gateId} is READY without evidence.`;
  }
  if (gateResult.status === 'BLOCKED' && findings.length === 0) {
    return `${gateResult.gateId} is BLOCKED without findings.`;
  }
  return null;
}
