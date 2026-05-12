import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { evaluateScenarioManifest } from '../core/scenario-runner.mjs';

const REQUIRED_LAYERS = ['Tablet', 'PC', 'Mobile', 'Control'];

export async function run(ctx) {
  const pack = evaluateScenarioManifest(ctx, path.join(ctx.qualityRoot, 'scenarios', 'scenario-manifest.json'));
  const byLayer = Object.fromEntries(REQUIRED_LAYERS.map(layer => [layer, pack.results.filter(r => r.layer === layer)]));
  const missingLayers = REQUIRED_LAYERS.filter(layer => byLayer[layer].length === 0);
  const weakLayers = REQUIRED_LAYERS.filter(layer => byLayer[layer].length > 0 && !byLayer[layer].some(s => s.status === 'READY' || s.status === 'PARTIAL'));

  const evidence = [createEvidence(ctx, 'Q18', 'cross_layer_evidence_trace', 'Cross-layer evidence trace across Tablet, PC, Mobile and Control scenarios', {
    aggregate: pack.aggregate,
    byLayer,
    missingLayers,
    weakLayers
  })];

  const findings = [];

  for (const layer of missingLayers) {
    findings.push(finding({
      id: `Q18_LAYER_SCENARIO_MISSING_${layer}`,
      severity: 'S2',
      layer,
      title: 'Layer scenario missing',
      detail: `No scenario declared for ${layer}.`,
      file: 'quality/scenarios/scenario-manifest.json',
      evidence,
      recommendation: 'Declare a non-mutating scenario for this layer with expected evidence.'
    }));
  }

  for (const layer of weakLayers) {
    findings.push(finding({
      id: `Q18_LAYER_EVIDENCE_WEAK_${layer}`,
      severity: 'S3',
      layer,
      title: 'Layer scenario evidence weak',
      detail: `${layer} has scenario declaration but no usable evidence.`,
      file: 'quality/scenarios/scenario-manifest.json',
      evidence,
      recommendation: 'Connect the layer to actual route, component, policy or evidence surfaces.'
    }));
  }

  return {
    gateId: 'Q18',
    title: 'Cross-Layer Evidence Trace',
    status: findings.some(f => ['S0', 'S1'].includes(f.severity)) ? 'BLOCKED' : 'READY',
    summary: `${REQUIRED_LAYERS.length - missingLayers.length}/${REQUIRED_LAYERS.length} required layers represented.`,
    findings,
    evidence
  };
}
