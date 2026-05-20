import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { exists, readJsonSafe, readText, rel, scanRepoText } from '../core/customer-assurance.mjs';

export const gateId = 'C5';
export const title = 'Upgrade and Rollback Readiness';

function migrationDestructiveHits(ctx) {
  const files = scanRepoText(ctx, ['prisma'], { maxFiles: 1200 }).filter((file) => file.toLowerCase().endsWith('.sql'));
  const hits = [];
  const pattern = /\b(drop\s+table|drop\s+column|truncate\s+table|delete\s+from)\b/i;
  for (const file of files) {
    const lines = readText(file).split(/\r?\n/);
    lines.forEach((line, index) => {
      if (pattern.test(line)) hits.push({ file: rel(ctx, file), line: index + 1, sample: line.trim().slice(0, 200) });
    });
  }
  return hits;
}

export async function run(ctx) {
  const manifest = readJsonSafe(path.join(ctx.qualityRoot, 'prisma-quality.manifest.json'));
  const requiredAssets = [
    'docs/upgrade-rollback-customer.md',
    'profiles/upgrade.json',
    'policies/customer-upgrade-policy.json',
    'scripts/repair_phase5_warnings.py'
  ].map((relativePath) => ({ path: `quality/${relativePath}`, exists: exists(path.join(ctx.qualityRoot, relativePath)) }));
  const destructiveHits = migrationDestructiveHits(ctx);
  const evidence = [createEvidence(ctx, 'C5', 'upgrade_rollback_readiness', 'Upgrade, rollback, manifest, and migration safety scan', {
    manifestOk: manifest.ok,
    version: manifest.value?.systemVersion || manifest.value?.version || 'unknown',
    requiredAssets,
    destructiveMigrationHits: destructiveHits
  })];
  const findings = [];
  if (!manifest.ok) {
    findings.push(finding({
      id: 'C5_MANIFEST_UNREADABLE',
      severity: 'S1',
      layer: 'Release',
      title: 'Quality manifest cannot be parsed',
      detail: manifest.error || 'Manifest parse failed.',
      file: 'quality/prisma-quality.manifest.json',
      evidence,
      recommendation: 'Fix manifest before customer upgrade.'
    }));
  }
  for (const item of requiredAssets.filter((item) => !item.exists)) {
    findings.push(finding({
      id: `C5_MISSING_${item.path.replace(/[^A-Za-z0-9]+/g, '_')}`,
      severity: item.path.includes('repair_phase5') ? 'S3' : 'S2',
      layer: 'Release',
      title: 'Upgrade or rollback asset missing',
      detail: `${item.path} is required for customer upgrade handoff.`,
      file: item.path,
      evidence,
      recommendation: 'Restore upgrade docs/profile/policy or document why this install shape does not need it.'
    }));
  }
  for (const hit of destructiveHits) {
    findings.push(finding({
      id: `C5_DESTRUCTIVE_MIGRATION_${findings.length + 1}`,
      severity: 'S1',
      layer: 'Core',
      title: 'Potential destructive migration in customer upgrade path',
      detail: `${hit.file}:${hit.line}: ${hit.sample}`,
      file: hit.file,
      evidence,
      recommendation: 'Keep customer upgrades additive-first or isolate destructive changes behind explicit backup/rollback and approval.'
    }));
  }
  return {
    gateId: 'C5',
    title,
    status: findings.some((item) => ['S0', 'S1'].includes(item.severity)) ? 'BLOCKED' : findings.length ? 'READY_WITH_WARNINGS' : 'READY',
    summary: `Quality version ${manifest.value?.systemVersion || manifest.value?.version || 'unknown'}; ${destructiveHits.length} destructive migration signals.`,
    findings,
    evidence
  };
}
