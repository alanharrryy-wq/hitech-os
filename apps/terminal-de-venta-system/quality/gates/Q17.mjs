import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { evaluateScenarioManifest } from '../core/scenario-runner.mjs';

export async function run(ctx) {
  const pack = evaluateScenarioManifest(ctx, path.join(ctx.qualityRoot, 'scenarios', 'scenario-manifest.json'));
  const lifecycle = pack.results.filter(r => r.tags.includes('event-lifecycle') || r.scenarioId === 'SCN_CORE_EVENT_LIFECYCLE');

  const evidence = [createEvidence(ctx, 'Q17', 'operational_event_lifecycle', 'Operational lifecycle scenario evidence: entity, event, state, evidence and audit trail', {
    aggregate: pack.aggregate,
    lifecycle
  })];

  const findings = [];

  if (!lifecycle.length) {
    findings.push(finding({
      id: 'Q17_NO_LIFECYCLE_SCENARIO',
      severity: 'S1',
      layer: 'Core',
      title: 'Operational lifecycle scenario missing',
      detail: 'No event-lifecycle scenario was declared.',
      file: 'quality/scenarios/scenario-manifest.json',
      evidence,
      recommendation: 'Add SCN_CORE_EVENT_LIFECYCLE or equivalent operational lifecycle scenario.'
    }));
  }

  for (const scenario of lifecycle) {
    if (scenario.status === 'MISSING') {
      findings.push(finding({
        id: `Q17_LIFECYCLE_MISSING_${scenario.scenarioId}`,
        severity: 'S2',
        layer: scenario.layer,
        title: 'Operational lifecycle evidence missing',
        detail: `${scenario.scenarioId} has no usable lifecycle evidence.`,
        file: 'quality/scenarios/scenario-manifest.json',
        evidence,
        recommendation: 'Add or connect entity/event/state/evidence/audit surfaces. Do not fake this scenario green.'
      }));
    } else if (scenario.status === 'PARTIAL') {
      findings.push(finding({
        id: `Q17_LIFECYCLE_PARTIAL_${scenario.scenarioId}`,
        severity: 'S3',
        layer: scenario.layer,
        title: 'Operational lifecycle evidence partial',
        detail: `${scenario.scenarioId} is partial with confidence ${scenario.confidence}.`,
        file: 'quality/scenarios/scenario-manifest.json',
        evidence,
        recommendation: 'Complete lifecycle evidence for entity, event, status and audit trail.'
      }));
    }
  }

  return {
    gateId: 'Q17',
    title: 'Operational Event Lifecycle',
    status: findings.some(f => ['S0', 'S1'].includes(f.severity)) ? 'BLOCKED' : 'READY',
    summary: `${lifecycle.length} lifecycle scenario(s), ${lifecycle.filter(s => s.status === 'READY').length} ready.`,
    findings,
    evidence
  };
}
