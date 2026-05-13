import fs from 'node:fs';
import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';

function readJsonSafe(file) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch (error) { return { __error: error.message || String(error) }; }
}

function contractList(registry) {
  if (Array.isArray(registry.contracts)) return registry.contracts;
  if (Array.isArray(registry.dataContracts)) return registry.dataContracts;
  if (registry.contracts && typeof registry.contracts === 'object') return Object.entries(registry.contracts).map(([id, value]) => ({ id, ...value }));
  return [];
}

function getId(contract, index) {
  return contract.id || contract.contractId || contract.name || `CONTRACT_${index + 1}`;
}

function numberOrNull(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function confidence(contract) {
  return numberOrNull(contract.confidence)
    ?? numberOrNull(contract.confidenceScore)
    ?? numberOrNull(contract.confidenceModel?.confidence)
    ?? numberOrNull(contract.quality?.confidence)
    ?? null;
}

function confidenceThreshold(contract, registry) {
  return numberOrNull(contract.confidenceThreshold)
    ?? numberOrNull(contract.confidenceFloor)
    ?? numberOrNull(contract.confidenceModel?.threshold)
    ?? numberOrNull(registry.defaults?.confidenceFloor)
    ?? 0.55;
}

function freshnessWindow(contract, registry) {
  return numberOrNull(contract.freshnessWindowDays)
    ?? numberOrNull(contract.freshness?.windowDays)
    ?? numberOrNull(contract.freshnessRule?.maxAgeDays)
    ?? numberOrNull(registry.defaults?.freshnessWindowDays)
    ?? 7;
}

function lastVerified(contract) {
  return contract.lastVerified
    || contract.lastVerifiedAt
    || contract.verifiedAt
    || contract.freshness?.lastVerified
    || contract.freshnessRule?.lastVerified
    || null;
}

function ageDays(iso) {
  const timestamp = Date.parse(iso);
  if (!Number.isFinite(timestamp)) return null;
  const ms = Date.now() - timestamp;
  return Math.max(0, Math.floor(ms / (24 * 60 * 60 * 1000)));
}

export async function run(ctx) {
  const registryPath = path.join(ctx.qualityRoot, 'data', 'data-contract-registry.json');
  const registry = readJsonSafe(registryPath);
  const contracts = contractList(registry);
  const findings = [];
  const evaluations = [];

  for (const [index, contract] of contracts.entries()) {
    const id = getId(contract, index);
    const last = lastVerified(contract);
    const windowDays = freshnessWindow(contract, registry);
    const conf = confidence(contract);
    const threshold = confidenceThreshold(contract, registry);
    const age = last ? ageDays(last) : null;

    const evaluation = {
      id,
      owner: contract.owner || null,
      layer: contract.layer || null,
      lastVerified: last,
      freshnessWindowDays: windowDays,
      ageDays: age,
      confidence: conf,
      confidenceThreshold: threshold,
      stale: age !== null ? age > windowDays : false,
      confidenceLow: conf !== null ? conf < threshold : false
    };

    evaluations.push(evaluation);
  }

  const evidence = [createEvidence(ctx, 'Q23', 'freshness_confidence_model', 'Freshness and confidence validation for data contracts', {
    registryPath: 'quality/data/data-contract-registry.json',
    contractCount: contracts.length,
    evaluations
  })];

  if (!contracts.length) {
    findings.push(finding({
      id: 'Q23_NO_CONTRACTS',
      severity: 'S2',
      layer: 'Data',
      title: 'No data contracts found',
      detail: 'No contracts were found in quality/data/data-contract-registry.json.',
      file: 'quality/data/data-contract-registry.json',
      evidence,
      recommendation: 'Add data contracts with owner, layer, freshness and confidence metadata.'
    }));
  }

  for (const item of evaluations) {
    if (!item.lastVerified) {
      findings.push(finding({
        id: `Q23_MISSING_LAST_VERIFIED_${item.id}`,
        severity: 'S3',
        layer: item.layer || 'Data',
        title: 'Data contract missing lastVerified',
        detail: `${item.id} has no lastVerified timestamp.`,
        file: 'quality/data/data-contract-registry.json',
        evidence,
        recommendation: 'Add lastVerified/verifiedAt metadata or document why this contract is static.'
      }));
      continue;
    }

    if (item.ageDays === null) {
      findings.push(finding({
        id: `Q23_INVALID_LAST_VERIFIED_${item.id}`,
        severity: 'S3',
        layer: item.layer || 'Data',
        title: 'Data contract lastVerified is invalid',
        detail: `${item.id} has invalid lastVerified value: ${item.lastVerified}.`,
        file: 'quality/data/data-contract-registry.json',
        evidence,
        recommendation: 'Use an ISO-8601 timestamp for lastVerified.'
      }));
      continue;
    }

    if (item.ageDays > item.freshnessWindowDays) {
      findings.push(finding({
        id: `Q23_STALE_CONTRACT_${item.id}`,
        severity: 'S3',
        layer: item.layer || 'Data',
        title: 'Data contract freshness window exceeded',
        detail: `${item.id} was last verified ${item.ageDays} days ago; threshold is ${item.freshnessWindowDays} days.`,
        file: 'quality/data/data-contract-registry.json',
        evidence,
        recommendation: 'Re-verify this contract or adjust its freshness policy with justification.'
      }));
    }

    if (item.confidence !== null && item.confidence < item.confidenceThreshold) {
      findings.push(finding({
        id: `Q23_LOW_CONFIDENCE_${item.id}`,
        severity: 'S3',
        layer: item.layer || 'Data',
        title: 'Data contract confidence below threshold',
        detail: `${item.id} confidence is ${item.confidence}; threshold is ${item.confidenceThreshold}.`,
        file: 'quality/data/data-contract-registry.json',
        evidence,
        recommendation: 'Improve evidence coverage or lower threshold only with explicit policy justification.'
      }));
    }
  }

  return {
    gateId: 'Q23',
    title: 'Freshness & Confidence Model',
    status: findings.some(f => ['S0', 'S1'].includes(f.severity)) ? 'BLOCKED' : 'READY',
    summary: `${contracts.length} contracts evaluated, ${evaluations.filter(e => e.stale).length} stale, ${evaluations.filter(e => e.confidenceLow).length} low confidence.`,
    findings,
    evidence
  };
}
