import fs from 'node:fs';
import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';

function readSafe(file) {
  try { return fs.readFileSync(file, 'utf8'); } catch { return ''; }
}

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

function explicitModels(contract) {
  const raw = contract.requiredSchemaModels || contract.schemaModels || contract.schema?.models || [];
  return Array.isArray(raw) ? raw : [];
}

function explicitFields(contract) {
  const raw = contract.requiredSchemaFields || contract.schemaFields || contract.schema?.fields || [];
  return Array.isArray(raw) ? raw : [];
}

function listMigrations(repoRoot) {
  const dir = path.join(repoRoot, 'prisma', 'migrations');
  if (!fs.existsSync(dir)) return [];
  try {
    return fs.readdirSync(dir, { withFileTypes: true })
      .filter(entry => entry.isDirectory())
      .map(entry => entry.name)
      .sort();
  } catch {
    return [];
  }
}

export async function run(ctx) {
  const registryPath = path.join(ctx.qualityRoot, 'data', 'data-contract-registry.json');
  const schemaPath = path.join(ctx.repoRoot, 'prisma', 'schema.prisma');
  const registry = readJsonSafe(registryPath);
  const contracts = contractList(registry);
  const schemaText = readSafe(schemaPath);
  const migrations = listMigrations(ctx.repoRoot);
  const findings = [];
  const checks = [];

  for (const [index, contract] of contracts.entries()) {
    const id = getId(contract, index);
    const models = explicitModels(contract);
    const fields = explicitFields(contract);
    const missingModels = [];
    const missingFields = [];

    for (const model of models) {
      const pattern = new RegExp(`model\\s+${String(model).replace(/[.*+?^${}()|[\\]\\\\]/g, '\\$&')}\\b`);
      if (!pattern.test(schemaText)) missingModels.push(model);
    }

    for (const field of fields) {
      if (!schemaText.includes(String(field))) missingFields.push(field);
    }

    checks.push({ id, models, fields, missingModels, missingFields });
  }

  const evidence = [createEvidence(ctx, 'Q24', 'schema_drift_guard', 'Schema drift guard. Migration existence is evidence-only; warnings require explicit drift.', {
    schemaPath: 'prisma/schema.prisma',
    schemaExists: Boolean(schemaText),
    migrationCount: migrations.length,
    migrations,
    contractCount: contracts.length,
    checks
  })];

  if (!schemaText) {
    findings.push(finding({
      id: 'Q24_SCHEMA_MISSING',
      severity: 'S3',
      layer: 'Data',
      title: 'Prisma schema not found',
      detail: 'prisma/schema.prisma was not found, so schema drift checks are limited.',
      file: 'prisma/schema.prisma',
      evidence,
      recommendation: 'Add schema.prisma or document the actual schema source of truth.'
    }));
  }

  for (const item of checks) {
    for (const model of item.missingModels) {
      findings.push(finding({
        id: `Q24_MISSING_SCHEMA_MODEL_${item.id}_${model}`,
        severity: 'S3',
        layer: 'Data',
        title: 'Declared schema model missing',
        detail: `${item.id} explicitly requires schema model ${model}, but it was not found.`,
        file: 'quality/data/data-contract-registry.json',
        evidence,
        recommendation: 'Add the model to schema.prisma or remove/adjust the explicit requirement.'
      }));
    }

    for (const field of item.missingFields) {
      findings.push(finding({
        id: `Q24_MISSING_SCHEMA_FIELD_${item.id}_${String(field).replace(/[^a-z0-9_]/ig, '_')}`,
        severity: 'S3',
        layer: 'Data',
        title: 'Declared schema field missing',
        detail: `${item.id} explicitly requires schema field ${field}, but it was not found.`,
        file: 'quality/data/data-contract-registry.json',
        evidence,
        recommendation: 'Add the field to schema.prisma or remove/adjust the explicit requirement.'
      }));
    }
  }

  return {
    gateId: 'Q24',
    title: 'Schema Drift & Migration Guard',
    status: findings.some(f => ['S0', 'S1'].includes(f.severity)) ? 'BLOCKED' : 'READY',
    summary: `Schema ${schemaText ? 'found' : 'missing'}, ${migrations.length} migration(s) recorded as evidence, ${findings.length} explicit drift warning(s).`,
    findings,
    evidence
  };
}
