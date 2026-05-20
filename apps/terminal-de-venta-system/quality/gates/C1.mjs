import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { exists, packageScripts, pathMatrix } from '../core/customer-assurance.mjs';

export const gateId = 'C1';
export const title = 'Customer Readiness Gate';

const REQUIRED_QUALITY_FILES = [
  'profiles/client-readiness.json',
  'profiles/demo.json',
  'profiles/first-run.json',
  'profiles/support-pack.json',
  'profiles/upgrade.json',
  'docs/customer-assurance-layer.md',
  'docs/client-readiness.md',
  'docs/demo-mode.md',
  'docs/support-pack.md',
  'docs/upgrade-rollback-customer.md',
  'policies/customer-assurance-policy.json'
];

export async function run(ctx) {
  const qualityChecks = REQUIRED_QUALITY_FILES.map((relativePath) => ({
    path: `quality/${relativePath}`,
    exists: exists(path.join(ctx.qualityRoot, relativePath))
  }));
  const rootMatrix = pathMatrix(ctx);
  const scripts = packageScripts(ctx);
  const suggestedScripts = ['quality:client-readiness', 'quality:demo', 'quality:first-run', 'quality:support-pack', 'quality:upgrade', 'quality:watch'];
  const missingScripts = suggestedScripts.filter((name) => !scripts.scripts || !scripts.scripts[name]);
  const evidence = [createEvidence(ctx, 'C1', 'customer_readiness_matrix', 'Customer readiness package, repo shape, and customer scripts scan', {
    qualityChecks,
    rootMatrix,
    rootPackageParseOk: scripts.ok,
    rootPackageScriptNames: scripts.scriptNames,
    missingSuggestedRootScripts: missingScripts
  })];
  const findings = [];
  for (const item of qualityChecks.filter((item) => !item.exists)) {
    findings.push(finding({
      id: `C1_MISSING_${item.path.replace(/[^A-Za-z0-9]+/g, '_')}`,
      severity: 'S1',
      layer: 'Quality',
      title: 'Customer assurance asset missing',
      detail: `${item.path} is required by Customer Assurance Layer.`,
      file: item.path,
      evidence,
      recommendation: 'Restore the customer assurance bundle asset before promoting to customers.'
    }));
  }
  if (!scripts.ok) {
    findings.push(finding({
      id: 'C1_ROOT_PACKAGE_UNREADABLE',
      severity: 'S2',
      layer: 'Quality',
      title: 'Root package.json cannot be parsed',
      detail: scripts.error || 'Root package.json was missing or invalid.',
      file: 'package.json',
      evidence,
      recommendation: 'Fix package.json so customer readiness commands can be exposed cleanly.'
    }));
  }
  for (const scriptName of missingScripts) {
    findings.push(finding({
      id: `C1_SUGGESTED_SCRIPT_${scriptName.replace(/[^A-Za-z0-9]+/g, '_')}`,
      severity: 'S3',
      layer: 'Quality',
      title: 'Suggested customer quality script not wired at repo root',
      detail: `${scriptName} is not present in root package.json scripts. The quality CLI can still run directly.`,
      file: 'package.json',
      evidence,
      recommendation: 'Optionally add root scripts that call node quality/bin/prisma-quality.mjs with the matching profile.'
    }));
  }
  return {
    gateId: 'C1',
    title,
    status: findings.some((item) => ['S0', 'S1'].includes(item.severity)) ? 'BLOCKED' : findings.length ? 'READY_WITH_WARNINGS' : 'READY',
    summary: `${qualityChecks.filter((item) => item.exists).length}/${qualityChecks.length} customer assurance assets present; ${missingScripts.length} suggested root scripts missing.`,
    findings,
    evidence
  };
}
