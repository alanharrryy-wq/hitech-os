import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { evaluateScenarioManifest } from '../core/scenario-runner.mjs';

export async function run(ctx) {
  const pack = evaluateScenarioManifest(ctx, path.join(ctx.qualityRoot, 'scenarios', 'scenario-manifest.json'));
  const industrial = pack.results.filter(r => r.scenarioId === 'SCN_INDUSTRIAL_CRS_RECTIFIER_EVENT' || r.tags.includes('industrial') || r.tags.includes('crs'));

  const evidence = [createEvidence(ctx, 'Q19', 'industrial_crs_scenario', 'Industrial CRS rectifier scenario evidence and anti-POS proof', {
    aggregate: pack.aggregate,
    industrial
  })];

  const findings = [];

  if (!industrial.length) {
    findings.push(finding({
      id: 'Q19_INDUSTRIAL_SCENARIO_MISSING',
      severity: 'S2',
      layer: 'Industrial',
      title: 'Industrial CRS scenario missing',
      detail: 'No Industrial CRS/rectifier scenario declared.',
      file: 'quality/scenarios/scenario-manifest.json',
      evidence,
      recommendation: 'Declare SCN_INDUSTRIAL_CRS_RECTIFIER_EVENT to prove PRISMA is not just POS.'
    }));
  }

  for (const scenario of industrial) {
    if (scenario.status === 'MISSING') {
      findings.push(finding({
        id: `Q19_INDUSTRIAL_EVIDENCE_MISSING_${scenario.scenarioId}`,
        severity: 'S2',
        layer: 'Industrial',
        title: 'Industrial CRS evidence missing',
        detail: `${scenario.scenarioId} has no CRS/rectifier evidence. This is acceptable as a warning in Phase 3 but must not be called complete.`,
        file: 'quality/scenarios/scenario-manifest.json',
        evidence,
        recommendation: 'Add actual CRS, rectifier, asset, site, technician, measurement, alert and evidence surfaces.'
      }));
    } else if (scenario.status === 'PARTIAL') {
      findings.push(finding({
        id: `Q19_INDUSTRIAL_EVIDENCE_PARTIAL_${scenario.scenarioId}`,
        severity: 'S3',
        layer: 'Industrial',
        title: 'Industrial CRS evidence partial',
        detail: `${scenario.scenarioId} is partial with confidence ${scenario.confidence}.`,
        file: 'quality/scenarios/scenario-manifest.json',
        evidence,
        recommendation: 'Complete the CRS scenario with asset, reading, responsible, status and evidence trail.'
      }));
    }
  }

  return {
    gateId: 'Q19',
    title: 'Industrial CRS Scenario',
    status: findings.some(f => ['S0', 'S1'].includes(f.severity)) ? 'BLOCKED' : 'READY',
    summary: `${industrial.length} industrial scenario(s), ${industrial.filter(s => s.status === 'READY').length} ready.`,
    findings,
    evidence
  };
}
