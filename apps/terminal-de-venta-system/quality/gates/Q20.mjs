import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { evaluateScenarioManifest } from '../core/scenario-runner.mjs';

export async function run(ctx) {
  const pack = evaluateScenarioManifest(ctx, path.join(ctx.qualityRoot, 'scenarios', 'scenario-manifest.json'));
  const falseGreen = pack.results.filter(r => r.status === 'READY' && r.actualEvidenceCount <= 0);
  const mutating = pack.results.filter(r => r.mutates || r.requiresCloudflare || r.startsServices);
  const missing = pack.results.filter(r => r.status === 'MISSING');
  const partial = pack.results.filter(r => r.status === 'PARTIAL');

  const evidence = [createEvidence(ctx, 'Q20', 'scenario_no_fake_green', 'Scenario no-fake-green audit: every READY scenario must have actual evidence and no scenario may mutate', {
    aggregate: pack.aggregate,
    falseGreen,
    mutating,
    missing: missing.map(s => ({ scenarioId: s.scenarioId, layer: s.layer, confidence: s.confidence })),
    partial: partial.map(s => ({ scenarioId: s.scenarioId, layer: s.layer, confidence: s.confidence }))
  })];

  const findings = [];

  for (const scenario of falseGreen) {
    findings.push(finding({
      id: `Q20_FALSE_GREEN_${scenario.scenarioId}`,
      severity: 'S1',
      layer: scenario.layer,
      title: 'Scenario is green without evidence',
      detail: `${scenario.scenarioId} is READY but actualEvidenceCount is ${scenario.actualEvidenceCount}.`,
      file: 'quality/scenarios/scenario-manifest.json',
      evidence,
      recommendation: 'Do not mark scenario READY until real evidence exists.'
    }));
  }

  for (const scenario of mutating) {
    findings.push(finding({
      id: `Q20_MUTATING_SCENARIO_${scenario.scenarioId}`,
      severity: 'S1',
      layer: scenario.layer,
      title: 'Scenario violates non-mutating policy',
      detail: `${scenario.scenarioId} mutates=${scenario.mutates}, startsServices=${scenario.startsServices}, requiresCloudflare=${scenario.requiresCloudflare}.`,
      file: 'quality/scenarios/scenario-manifest.json',
      evidence,
      recommendation: 'Scenario gates must be dry evidence only in Phase 3.'
    }));
  }

  for (const scenario of missing) {
    findings.push(finding({
      id: `Q20_SCENARIO_MISSING_EVIDENCE_${scenario.scenarioId}`,
      severity: 'S2',
      layer: scenario.layer,
      title: 'Scenario has no usable evidence',
      detail: `${scenario.scenarioId} is MISSING.`,
      file: 'quality/scenarios/scenario-manifest.json',
      evidence,
      recommendation: 'Add real source evidence or keep the scenario explicitly incomplete.'
    }));
  }

  for (const scenario of partial) {
    findings.push(finding({
      id: `Q20_SCENARIO_PARTIAL_EVIDENCE_${scenario.scenarioId}`,
      severity: 'S3',
      layer: scenario.layer,
      title: 'Scenario evidence is partial',
      detail: `${scenario.scenarioId} is PARTIAL with confidence ${scenario.confidence}.`,
      file: 'quality/scenarios/scenario-manifest.json',
      evidence,
      recommendation: 'Complete the scenario evidence before treating it as operationally proven.'
    }));
  }

  return {
    gateId: 'Q20',
    title: 'Scenario No-Fake-Green',
    status: findings.some(f => ['S0', 'S1'].includes(f.severity)) ? 'BLOCKED' : 'READY',
    summary: `${pack.aggregate.ready}/${pack.aggregate.scenarioCount} scenarios ready, ${pack.aggregate.partial} partial, ${pack.aggregate.missing} missing.`,
    findings,
    evidence
  };
}
