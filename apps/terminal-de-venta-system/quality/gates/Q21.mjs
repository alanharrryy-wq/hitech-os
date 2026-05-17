import fs from 'node:fs';
import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { pathExists, toPosix } from '../core/paths.mjs';

function readJsonSafe(p) { try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch (error) { return { __error: error.message || String(error) }; } }
function rel(ctx, p) { return toPosix(path.relative(ctx.repoRoot, p)); }

export async function run(ctx) {
  const registryPath = path.join(ctx.qualityRoot, 'data', 'data-contract-registry.json');
  const registry = readJsonSafe(registryPath);
  const findings = [];
  const evidence = [];

  // Check registry file exists and is valid JSON
  if (registry.__error) {
    findings.push(finding({
      id: 'Q21_REGISTRY_PARSE_ERROR',
      severity: 'S0',
      layer: 'Quality',
      title: 'Data contract registry is invalid or missing',
      detail: `${registryPath}: ${registry.__error}`,
      file: registryPath,
      recommendation: 'Ensure quality/data/data-contract-registry.json exists and is valid JSON.'
    }));
    return {
      gateId: 'Q21',
      title: 'Data Contract Registry',
      status: 'BLOCKED',
      summary: 'Registry file missing or invalid.',
      findings,
      evidence
    };
  }

  // Validate registry structure
  if (!Array.isArray(registry.dataContracts)) {
    findings.push(finding({
      id: 'Q21_REGISTRY_STRUCTURE_INVALID',
      severity: 'S0',
      layer: 'Quality',
      title: 'Data contract registry structure is invalid',
      detail: 'Registry must have dataContracts array',
      file: registryPath,
      recommendation: 'Add dataContracts array to registry.'
    }));
    return {
      gateId: 'Q21',
      title: 'Data Contract Registry',
      status: 'BLOCKED',
      summary: 'Registry structure invalid.',
      findings,
      evidence
    };
  }

  // Expected contracts
  const expectedContracts = new Set([
    'DC_TABLET_OPERATIONS',
    'DC_PC_GOVERNANCE',
    'DC_MOBILE_SUPERVISION',
    'DC_CORE_LEDGER',
    'DC_CONTROL_AUDIT'
  ]);

  const registeredIds = new Set(registry.dataContracts.map(c => c.contractId));
  const evidencePayload = {
    registry_version: registry.registryVersion || 'unknown',
    total_contracts_registered: registry.dataContracts.length,
    expected_contracts: Array.from(expectedContracts),
    registered_contracts: Array.from(registeredIds),
    contracts: []
  };

  // Validate each contract
  for (const contract of registry.dataContracts) {
    const contractSummary = {
      contractId: contract.contractId,
      layer: contract.layer,
      status: 'VALID',
      issues: []
    };

    // Check required fields
    const requiredContractFields = [
      'contractId',
      'layer',
      'dataOwner',
      'sourceOfTruth',
      'requiredFields',
      'trustLevel',
      'integrityMode',
      'mutationPolicy',
      'status'
    ];

    for (const field of requiredContractFields) {
      if (!(field in contract)) {
        contractSummary.issues.push(`missing field: ${field}`);
        contractSummary.status = 'INVALID';
      }
    }

    // Validate requiredFields array
    if (!Array.isArray(contract.requiredFields) || contract.requiredFields.length === 0) {
      contractSummary.issues.push('requiredFields must be non-empty array');
      contractSummary.status = 'INVALID';
    }

    // Validate trust level
    const validTrustLevels = ['T0_SOVEREIGN', 'T1_CERTIFIED', 'T2_SUPERVISED', 'T0_IMMUTABLE'];
    if (!validTrustLevels.includes(contract.trustLevel)) {
      contractSummary.issues.push(`invalid trustLevel: ${contract.trustLevel}`);
      contractSummary.status = 'INVALID';
    }

    // Validate integrity mode
    const validIntegrityModes = ['immutable', 'write-once', 'append-only', 'queryable'];
    if (!validIntegrityModes.includes(contract.integrityMode)) {
      contractSummary.issues.push(`invalid integrityMode: ${contract.integrityMode}`);
      contractSummary.status = 'INVALID';
    }

    // Validate mutation policy
    const validMutationPolicies = [
      'capture-only',
      'audit-trail-required',
      'read-only',
      'never',
      'append-only'
    ];
    if (!validMutationPolicies.includes(contract.mutationPolicy)) {
      contractSummary.issues.push(`invalid mutationPolicy: ${contract.mutationPolicy}`);
      contractSummary.status = 'INVALID';
    }

    // Validate status
    if (!['ACTIVE', 'DEPRECATED', 'DRAFT'].includes(contract.status)) {
      contractSummary.issues.push(`invalid status: ${contract.status}`);
      contractSummary.status = 'INVALID';
    }

    evidencePayload.contracts.push(contractSummary);

    // Create findings for invalid contracts
    if (contractSummary.status === 'INVALID') {
      findings.push(finding({
        id: `Q21_CONTRACT_INVALID_${contract.contractId}`,
        severity: 'S1',
        layer: contract.layer || 'Quality',
        title: `Data contract ${contract.contractId} is invalid`,
        detail: contractSummary.issues.join('; '),
        file: registryPath,
        recommendation: 'Fix contract definition in data-contract-registry.json'
      }));
    }

    // Check if inactive contracts are flagged
    if (contract.status !== 'ACTIVE') {
      findings.push(finding({
        id: `Q21_CONTRACT_NOT_ACTIVE_${contract.contractId}`,
        severity: 'S2',
        layer: contract.layer || 'Quality',
        title: `Data contract ${contract.contractId} is not ACTIVE`,
        detail: `Status is ${contract.status}. Phase 4 requires all contracts to be ACTIVE.`,
        file: registryPath,
        recommendation: 'Either activate the contract or remove it from Phase 4.'
      }));
    }
  }

  // Check for missing expected contracts
  for (const expectedId of expectedContracts) {
    if (!registeredIds.has(expectedId)) {
      findings.push(finding({
        id: `Q21_MISSING_CONTRACT_${expectedId}`,
        severity: 'S1',
        layer: 'Quality',
        title: `Missing required contract: ${expectedId}`,
        detail: `${expectedId} is required for Phase 4 but not found in registry.`,
        file: registryPath,
        recommendation: 'Add contract to data-contract-registry.json or acknowledge as not applicable.'
      }));
    }
  }

  // Create evidence
  const evid = createEvidence(ctx, 'Q21', 'data_contract_registry_validation', 'Data contract registry validation', evidencePayload);
  evidence.push(evid);

  return {
    gateId: 'Q21',
    title: 'Data Contract Registry',
    status: findings.some(f => ['S0', 'S1'].includes(f.severity)) ? 'BLOCKED' : 'READY',
    summary: `${registeredIds.size}/${expectedContracts.size} expected contracts registered, ${evidencePayload.contracts.filter(c => c.status === 'VALID').length} valid.`,
    findings,
    evidence
  };
}
