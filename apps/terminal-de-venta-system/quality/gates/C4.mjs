import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { ensureCustomerSupportManifest, exists, redactProof } from '../core/customer-assurance.mjs';

export const gateId = 'C4';
export const title = 'Support Pack Redaction and Exportability';

export async function run(ctx) {
  const redaction = redactProof();
  const requiredAssets = [
    'docs/support-pack.md',
    'profiles/support-pack.json',
    'policies/support-pack-redaction-policy.json'
  ].map((relativePath) => ({ path: `quality/${relativePath}`, exists: exists(path.join(ctx.qualityRoot, relativePath)) }));
  const supportManifest = ensureCustomerSupportManifest(ctx, {
    redactionLeakCount: redaction.leakCount,
    requiredAssets,
    customerSafe: redaction.leakCount === 0
  });
  const evidence = [createEvidence(ctx, 'C4', 'support_pack_readiness', 'Support pack redaction, manifest, and exportability scan', {
    redaction,
    requiredAssets,
    supportManifest
  })];
  const findings = [];
  if (redaction.leakCount > 0) {
    findings.push(finding({
      id: 'C4_REDACTION_LEAK',
      severity: 'S1',
      layer: 'Support',
      title: 'Support pack redaction failed synthetic secret proof',
      detail: `${redaction.leakCount} synthetic secret samples leaked after redaction.`,
      file: 'quality/core/redaction.mjs',
      evidence,
      recommendation: 'Fix redaction before generating customer support packs.'
    }));
  }
  for (const item of requiredAssets.filter((item) => !item.exists)) {
    findings.push(finding({
      id: `C4_MISSING_${item.path.replace(/[^A-Za-z0-9]+/g, '_')}`,
      severity: 'S2',
      layer: 'Support',
      title: 'Support pack asset missing',
      detail: `${item.path} is required for repeatable support handoff.`,
      file: item.path,
      evidence,
      recommendation: 'Restore support pack docs/profile/policy.'
    }));
  }
  return {
    gateId: 'C4',
    title,
    status: findings.some((item) => ['S0', 'S1'].includes(item.severity)) ? 'BLOCKED' : findings.length ? 'READY_WITH_WARNINGS' : 'READY',
    summary: `Support manifest generated; redaction synthetic leak count ${redaction.leakCount}.`,
    findings,
    evidence
  };
}
