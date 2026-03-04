import { stableStringify, sortUniqueStrings, type JsonValue } from "../shared/deterministic.js";
import { parsePitchProgram } from "./program-schema.js";
import { type PitchProgram, type PitchSceneRef, type SceneRecord } from "./program-types.js";

export interface ProgramCanonicalizationOptions {
  readonly sceneCanonicalizer?: (scene: SceneRecord) => SceneRecord;
}

function normalizeScene(scene: SceneRecord, options: ProgramCanonicalizationOptions): SceneRecord {
  const base: SceneRecord = {
    sceneId: scene.sceneId,
    route: scene.route,
    query: Object.fromEntries(
      Object.entries(scene.query)
        .map(([key, value]) => [key.trim(), value.trim()] as const)
        .filter(([key]) => key.length > 0)
        .sort(([left], [right]) => left.localeCompare(right))
    ),
    viewport: {
      width: scene.viewport.width,
      height: scene.viewport.height,
      deviceScaleFactor: scene.viewport.deviceScaleFactor
    },
    profile: scene.profile,
    layers: sortUniqueStrings(scene.layers),
    motion: {
      enabled: scene.motion.enabled,
      intensity: scene.motion.intensity,
      reducedMotionPolicy: scene.motion.reducedMotionPolicy
    }
  };

  return options.sceneCanonicalizer ? options.sceneCanonicalizer(base) : base;
}

function normalizeSceneRef(ref: PitchSceneRef, options: ProgramCanonicalizationOptions): PitchSceneRef {
  if (ref.type === "sceneId") {
    return {
      type: "sceneId",
      sceneId: ref.sceneId
    };
  }

  return {
    type: "inlineScene",
    scene: normalizeScene(ref.scene, options)
  };
}

export function canonicalizePitchProgram(
  program: PitchProgram,
  options: ProgramCanonicalizationOptions = {}
): PitchProgram {
  const steps = program.steps.map((step) => ({
    stepId: step.stepId,
    title: step.title,
    label: step.label,
    sceneRef: normalizeSceneRef(step.sceneRef, options),
    durationMs: step.durationMs,
    transition: {
      type: step.transition.type,
      ms: step.transition.ms,
      easing: step.transition.easing
    },
    presetId: step.presetId,
    markers: step.markers ? sortUniqueStrings(step.markers) : undefined,
    director: step.director
      ? {
          sequenceId: step.director.sequenceId,
          apply: step.director.apply
        }
      : undefined,
    expectations: step.expectations
      ? {
          requiredDataAttributes: step.expectations.requiredDataAttributes
            ? sortUniqueStrings(step.expectations.requiredDataAttributes)
            : undefined,
          requiredLayers: step.expectations.requiredLayers
            ? sortUniqueStrings(step.expectations.requiredLayers)
            : undefined,
          minEnabledLayers: step.expectations.minEnabledLayers
        }
      : undefined
  }));

  const stepIndex = new Map<string, number>(steps.map((step, index) => [step.stepId, index]));

  return {
    schemaVersion: program.schemaVersion,
    programId: program.programId,
    title: program.title,
    description: program.description,
    tags: sortUniqueStrings(program.tags),
    createdAt: program.createdAt,
    updatedAt: program.updatedAt,
    defaultPresetId: program.defaultPresetId,
    chapters: program.chapters
      ? [...program.chapters]
          .map((chapter) => ({
            chapterId: chapter.chapterId,
            label: chapter.label,
            stepId: chapter.stepId
          }))
          .sort((left, right) => {
            const leftOrder = stepIndex.get(left.stepId) ?? Number.MAX_SAFE_INTEGER;
            const rightOrder = stepIndex.get(right.stepId) ?? Number.MAX_SAFE_INTEGER;
            if (leftOrder !== rightOrder) {
              return leftOrder - rightOrder;
            }
            return left.chapterId.localeCompare(right.chapterId);
          })
      : undefined,
    steps,
    capabilityRequest: program.capabilityRequest
      ? {
          director: program.capabilityRequest.director
        }
      : undefined,
    metadata: program.metadata
      ? {
          source: program.metadata.source,
          gitHash: program.metadata.gitHash,
          notes: program.metadata.notes
        }
      : undefined
  };
}

export function serializePitchProgram(
  program: PitchProgram,
  options: ProgramCanonicalizationOptions = {}
): string {
  const canonical = canonicalizePitchProgram(program, options);
  return stableStringify(canonical as unknown as JsonValue);
}

export function parsePitchProgramJson(input: string): PitchProgram {
  const parsed = JSON.parse(input) as unknown;
  return parsePitchProgram(parsed);
}

export function deserializePitchProgram(
  input: string,
  options: ProgramCanonicalizationOptions = {}
): PitchProgram {
  const parsed = parsePitchProgramJson(input);
  return canonicalizePitchProgram(parsed, options);
}

export interface ProgramExportBundle {
  readonly canonical: PitchProgram;
  readonly serialized: string;
}

export function buildProgramExportBundle(
  program: PitchProgram,
  options: ProgramCanonicalizationOptions = {}
): ProgramExportBundle {
  const canonical = canonicalizePitchProgram(program, options);
  return {
    canonical,
    serialized: stableStringify(canonical as unknown as JsonValue)
  };
}
