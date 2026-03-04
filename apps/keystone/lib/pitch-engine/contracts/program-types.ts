export const PITCH_PROGRAM_SCHEMA_VERSION = 1 as const;

export const DIRECTOR_MODES = ["off", "lite", "full", "debug"] as const;
export type DirectorCapabilityMode = (typeof DIRECTOR_MODES)[number];

export const TRANSITION_TYPES = ["cut", "fade", "crossfade", "wipe", "dipToBlack"] as const;
export type PitchTransitionType = (typeof TRANSITION_TYPES)[number];

export const EASING_TYPES = ["linear", "easeIn", "easeOut", "easeInOut"] as const;
export type PitchEasingType = (typeof EASING_TYPES)[number];

export const PRESET_IDS = [
  "cinematic",
  "investor",
  "performance",
  "minimal",
  "debug",
  "neutral"
] as const;

export type PitchPresetId = (typeof PRESET_IDS)[number];

export type SceneProfile = PitchPresetId;

export interface SceneViewport {
  readonly width: number;
  readonly height: number;
  readonly deviceScaleFactor?: number;
}

export interface SceneMotion {
  readonly enabled: boolean;
  readonly intensity: "none" | "low" | "medium" | "high";
  readonly reducedMotionPolicy?: "respect" | "ignore";
}

export interface SceneRecord {
  readonly sceneId: string;
  readonly route: string;
  readonly query: Readonly<Record<string, string>>;
  readonly viewport: SceneViewport;
  readonly profile: SceneProfile;
  readonly layers: readonly string[];
  readonly motion: SceneMotion;
}

export interface SceneRefById {
  readonly type: "sceneId";
  readonly sceneId: string;
}

export interface SceneRefInline {
  readonly type: "inlineScene";
  readonly scene: SceneRecord;
}

export type PitchSceneRef = SceneRefById | SceneRefInline;

export interface PitchStepTransition {
  readonly type: PitchTransitionType;
  readonly ms: number;
  readonly easing: PitchEasingType;
}

export interface PitchStepExpectations {
  readonly requiredDataAttributes?: readonly string[];
  readonly requiredLayers?: readonly string[];
  readonly minEnabledLayers?: number;
}

export interface PitchStepDirector {
  readonly sequenceId?: string;
  readonly apply?: boolean;
}

export interface PitchStep {
  readonly stepId: string;
  readonly title: string;
  readonly label?: string;
  readonly sceneRef: PitchSceneRef;
  readonly durationMs: number;
  readonly transition: PitchStepTransition;
  readonly presetId?: PitchPresetId;
  readonly markers?: readonly string[];
  readonly director?: PitchStepDirector;
  readonly expectations?: PitchStepExpectations;
}

export interface PitchChapterMarker {
  readonly chapterId: string;
  readonly label: string;
  readonly stepId: string;
}

export interface PitchProgramCapabilityRequest {
  readonly director: DirectorCapabilityMode;
}

export interface PitchProgramMetadata {
  readonly source?: string;
  readonly gitHash?: string;
  readonly notes?: string;
}

export interface PitchProgramV1 {
  readonly schemaVersion: typeof PITCH_PROGRAM_SCHEMA_VERSION;
  readonly programId: string;
  readonly title: string;
  readonly description?: string;
  readonly tags: readonly string[];
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly defaultPresetId?: PitchPresetId;
  readonly chapters?: readonly PitchChapterMarker[];
  readonly steps: readonly PitchStep[];
  readonly capabilityRequest?: PitchProgramCapabilityRequest;
  readonly metadata?: PitchProgramMetadata;
}

export type PitchProgram = PitchProgramV1;

export interface ProgramValidationError {
  readonly path: string;
  readonly message: string;
  readonly code?: string;
}

export interface ProgramValidationResult {
  readonly ok: boolean;
  readonly program?: PitchProgram;
  readonly errors: readonly ProgramValidationError[];
}
