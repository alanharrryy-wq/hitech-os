import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { evaluateScenarioManifest } from '../core/scenario-runner.mjs';

function scenarioProblems(scenario, index) {
  const problems = [];
  const prefix = scenario?.id || `SCENARIO_${index + 1}`;

  for (const field of ['id', 'title', 'vertical', 'layer', 'owner']) {
    if (!scenario || !scenario[field]) problems.push(`${prefix} missing ${field}`);
  }

  if (!Array.isArray(scenario?.preconditions) || scenario.preconditions.length === 0) problems.push(`${prefix} missing preconditions`);
  if (!Array.isArray(scenario?.expectedEvidence) || scenario.expectedEvidence.length === 0) problems.push(`${prefix} missing expectedEvidence`);
  if (!Array.isArray(scenario?.checks) || scenario.checks.length === 0) problems.push(`${prefix} missing checks`);
  if (scenario?.mutates !== false) problems.push(`${prefix} must declare mutates:false`);
  if (scenario?.requiresCloudflare !== false) problems.push(`${prefix} must declare requiresCloudflare:false`);
  if (scenario?.startsServices !== false) problems.push(`${prefix} must declare startsServices:false`);

  return problems;
}

export async function run(ctx) {
  const pack = evaluateScenarioManifest(ctx, path.join(ctx.qualityRoot, 'scenarios', 'scenario-manifest.json'));
  const scenarios = Array.isArray(pack.manifest.scenarios) ? pack.manifest.scenarios : [];
  const problems = scenarios.flatMap((scenario, index) => scenarioProblems(scenario, index));

  if (!scenarios.length) problems.push('scenario-manifest.json has no scenarios.');

  const evidence = [createEvidence(ctx, 'Q16', 'scenario_manifest_integrity', 'Scenario manifest schema, safety declarations and check structure', {
    manifestPath: pack.manifestPath,
    scenarioCount: scenarios.length,
    problems,
    scenarioIds: scenarios.map(s => s.id)
  })];

  const findings = problems.map((problem, index) => finding({
    id: `Q16_SCENARIO_MANIFEST_${index + 1}`,
    severity: 'S1',
    layer: 'Scenario',
    title: 'Scenario manifest integrity problem',
    detail: problem,
    file: 'quality/scenarios/scenario-manifest.json',
    evidence,
    recommendation: 'Fix scenario declaration. Every scenario must be explicit, non-mutating and evidence-based.'
  }));

  return {
    gateId: 'Q16',
    title: 'Scenario Manifest Integrity',
    status: findings.length ? 'BLOCKED' : 'READY',
    summary: `${scenarios.length} scenarios validated, ${problems.length} manifest problems.`,
    findings,
    evidence
  };
}
