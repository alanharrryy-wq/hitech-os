import type { PitchProgram, PitchStep, SceneRecord } from "../contracts/program-types.js";
import { resolvePresetChain } from "../presets/preset-registry.js";
import type { SceneAdapter } from "./scene-adapter.js";

export interface StepExpectationResult {
  readonly ok: boolean;
  readonly reasons: readonly string[];
}

export interface ResolvedPitchStep {
  readonly step: PitchStep;
  readonly scene: SceneRecord;
  readonly durationMs: number;
  readonly transition: PitchStep["transition"];
  readonly presetId: string;
  readonly expectation: StepExpectationResult;
}

function resolveStepScene(step: PitchStep, adapter: SceneAdapter): SceneRecord {
  if (step.sceneRef.type === "inlineScene") {
    return adapter.canonicalizeScene(step.sceneRef.scene);
  }

  const found = adapter.getSceneById(step.sceneRef.sceneId);
  if (!found) {
    throw new Error(`step '${step.stepId}' references unknown scene '${step.sceneRef.sceneId}'`);
  }

  return adapter.canonicalizeScene(found);
}

function resolveExpectation(step: PitchStep, scene: SceneRecord): StepExpectationResult {
  const expectations = step.expectations;
  if (!expectations) {
    return {
      ok: true,
      reasons: []
    };
  }

  const reasons: string[] = [];

  if (expectations.requiredLayers) {
    const enabledLayers = new Set(scene.layers);
    for (const layer of expectations.requiredLayers) {
      if (!enabledLayers.has(layer)) {
        reasons.push(`missing-layer:${layer}`);
      }
    }
  }

  if (expectations.minEnabledLayers !== undefined && scene.layers.length < expectations.minEnabledLayers) {
    reasons.push(
      `min-enabled-layers:${scene.layers.length}<${expectations.minEnabledLayers}`
    );
  }

  if (expectations.requiredDataAttributes) {
    const queryKeys = new Set(Object.keys(scene.query));
    for (const dataAttribute of expectations.requiredDataAttributes) {
      if (!queryKeys.has(dataAttribute)) {
        reasons.push(`missing-data-attribute:${dataAttribute}`);
      }
    }
  }

  return {
    ok: reasons.length === 0,
    reasons
  };
}

export function resolveProgramStep(input: {
  readonly program: PitchProgram;
  readonly stepIndex: number;
  readonly adapter: SceneAdapter;
}): ResolvedPitchStep {
  const step = input.program.steps[input.stepIndex];
  if (!step) {
    throw new Error(`step index '${input.stepIndex}' is out of range`);
  }

  const scene = resolveStepScene(step, input.adapter);
  const preset = resolvePresetChain({
    stepPresetId: step.presetId,
    programDefaultPresetId: input.program.defaultPresetId
  });

  return {
    step,
    scene,
    durationMs: step.durationMs,
    transition: step.transition,
    presetId: preset.id,
    expectation: resolveExpectation(step, scene)
  };
}

export function resolveAllProgramSteps(input: {
  readonly program: PitchProgram;
  readonly adapter: SceneAdapter;
}): readonly ResolvedPitchStep[] {
  return input.program.steps.map((_, stepIndex) =>
    resolveProgramStep({
      program: input.program,
      stepIndex,
      adapter: input.adapter
    })
  );
}
