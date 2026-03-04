export type CapabilityMode = "off" | "lite" | "full" | "debug";

export type CapabilityDegradeReason =
  | "reduced-motion"
  | "perf"
  | "viewport"
  | "user-request"
  | "production"
  | "debug-missing"
  | "env-missing"
  | "capability-missing";

export interface CapabilityStatus {
  readonly requestedMode: CapabilityMode;
  readonly appliedMode: CapabilityMode;
  readonly degradeReasons: CapabilityDegradeReason[];
  readonly isDev: boolean;
  readonly isRouteAllowed: boolean;
  readonly isApiAllowed: boolean;
  readonly debugTokenPresent: boolean;
  readonly envOverrideEnabled: boolean;
}

export type TimelineTrackType =
  | "camera"
  | "overlay"
  | "motion"
  | "layers"
  | "lighting"
  | "subtitle"
  | "audio"
  | "annotation";

export type MarkerType = "Reveal" | "Settle" | "CTA";

export interface TimelineValuePoint {
  readonly key: string;
  readonly value: string | number | boolean;
}

export interface TimelineKeyframe {
  readonly id: string;
  readonly t: number;
  readonly easing: "linear" | "ease-in" | "ease-out" | "ease-in-out";
  readonly values: TimelineValuePoint[];
}

export interface TimelineTrack {
  readonly id: string;
  readonly label: string;
  readonly kind: TimelineTrackType;
  readonly enabled: boolean;
  readonly keyframes: TimelineKeyframe[];
}

export interface TimelineMarker {
  readonly id: string;
  readonly label: string;
  readonly type: MarkerType;
  readonly t: number;
  readonly note: string;
}

export interface SequenceTransition {
  readonly id: string;
  readonly fromSequenceId: string;
  readonly toSequenceId: string;
  readonly mode:
    | "cut"
    | "crossfade"
    | "slide-left"
    | "slide-right"
    | "zoom-in"
    | "zoom-out";
  readonly durationMs: number;
}

export interface DirectorTimeline {
  readonly durationMs: number;
  readonly tracks: TimelineTrack[];
  readonly markers: TimelineMarker[];
  readonly transitions: SequenceTransition[];
}

export interface SequenceDiagnostics {
  readonly renderCost: "low" | "medium" | "high";
  readonly qualityWarnings: string[];
  readonly lastRenderAt: string | null;
  readonly lastRenderId: string | null;
}

export interface PitchSequence {
  readonly id: string;
  readonly sceneId: string;
  readonly name: string;
  readonly description: string;
  readonly cinematicPresetId: string;
  readonly timeline: DirectorTimeline;
  readonly diagnostics: SequenceDiagnostics;
  readonly createdAt: string;
  readonly updatedAt: string;
}

export interface SceneFlagSnapshot {
  readonly resolvedFlags: string[];
  readonly unknownTokens: string[];
}

export interface SceneRecorderSnapshot {
  readonly route: string;
  readonly canonicalUrl: string;
  readonly title: string;
  readonly capturedAt: string;
  readonly flagSnapshot: SceneFlagSnapshot;
  readonly viewport: {
    readonly width: number;
    readonly height: number;
    readonly dpr: number;
  };
}

export interface PitchScene {
  readonly id: string;
  readonly name: string;
  readonly route: string;
  readonly canonicalUrl: string;
  readonly description: string;
  readonly tags: string[];
  readonly defaultSequenceId: string | null;
  readonly recorderSnapshot: SceneRecorderSnapshot | null;
  readonly createdAt: string;
  readonly updatedAt: string;
}

export interface ProgramDiagnostics {
  readonly source: "fixture" | "import" | "user" | "recorded";
  readonly lastSaveError: string | null;
  readonly warnings: string[];
  readonly artifactLinks: string[];
}

export interface PitchProgram {
  readonly id: string;
  readonly name: string;
  readonly description: string;
  readonly owner: string;
  readonly version: string;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly scenes: PitchScene[];
  readonly sequences: PitchSequence[];
  readonly diagnostics: ProgramDiagnostics;
}

export interface ProgramLibraryState {
  readonly programs: PitchProgram[];
  readonly selectedProgramId: string | null;
  readonly selectedSceneId: string | null;
  readonly selectedSequenceId: string | null;
}

export interface TransportState {
  readonly isPlaying: boolean;
  readonly isLooping: boolean;
  readonly currentMs: number;
  readonly durationMs: number;
  readonly playbackRate: 0.5 | 1 | 1.25 | 1.5 | 2;
  readonly markerJumpId: string | null;
}

export interface OperatorHudStatus {
  readonly serverStatus: "starting" | "ready" | "error";
  readonly lastRunStatus: "unknown" | "ok" | "fail";
  readonly lastRunPath: string | null;
  readonly lastErrorTail: string | null;
  readonly lastArtifactRunId: string | null;
  readonly updatedAt: string;
}

export interface ArtifactDiffFrame {
  readonly beforePath: string | null;
  readonly afterPath: string | null;
  readonly diffPath: string | null;
  readonly width: number;
  readonly height: number;
}

export interface ArtifactTriageItem {
  readonly id: string;
  readonly runId: string;
  readonly sceneId: string;
  readonly sequenceId: string;
  readonly status: "pending" | "accepted" | "rejected";
  readonly score: number;
  readonly notesPath: string | null;
  readonly diff: ArtifactDiffFrame;
  readonly createdAt: string;
  readonly updatedAt: string;
}

export interface ArtifactRunIndex {
  readonly runId: string;
  readonly createdAt: string;
  readonly sourcePath: string;
  readonly items: ArtifactTriageItem[];
}

export interface TriageActionResult {
  readonly ok: boolean;
  readonly action: "accept" | "reject" | "rerun" | "notes";
  readonly command: string;
  readonly stdout: string;
  readonly stderr: string;
  readonly exitCode: number;
  readonly notesPath: string | null;
  readonly updatedItem: ArtifactTriageItem | null;
}

export interface BridgeEnvelope {
  readonly type: "pitch-engine:scene-snapshot";
  readonly payload: SceneRecorderSnapshot;
}

export interface ReplayPreviewPayload {
  readonly type: "pitch-engine:replay-state";
  readonly payload: {
    readonly sequenceId: string;
    readonly currentMs: number;
    readonly durationMs: number;
    readonly isPlaying: boolean;
    readonly markerId: string | null;
  };
}

export interface SupportBundle {
  readonly generatedAt: string;
  readonly app: "keystone";
  readonly route: "/dev/pitch-engine";
  readonly selectedProgram: PitchProgram | null;
  readonly selectedScene: PitchScene | null;
  readonly selectedSequence: PitchSequence | null;
  readonly capabilityStatus: CapabilityStatus;
  readonly operatorHud: OperatorHudStatus;
  readonly artifactRuns: ArtifactRunIndex[];
  readonly diagnostics: {
    readonly selectedProgramStats: {
      readonly scenes: number;
      readonly sequences: number;
      readonly markers: number;
      readonly keyframes: number;
    };
    readonly links: string[];
    readonly dodResultPath: string | null;
  };
  readonly environment: {
    readonly userAgent: string;
    readonly viewport: {
      readonly width: number;
      readonly height: number;
      readonly dpr: number;
    };
    readonly flags: string[];
  };
}

export interface TimelinePresetScript {
  readonly id: string;
  readonly label: string;
  readonly style: "cinematic" | "documentary" | "product" | "compliance";
  readonly description: string;
  readonly durationMs: number;
  readonly markers: Array<{
    readonly type: MarkerType;
    readonly t: number;
    readonly label: string;
    readonly note: string;
  }>;
  readonly tracks: Array<{
    readonly kind: TimelineTrackType;
    readonly label: string;
    readonly enabled: boolean;
    readonly keyframes: Array<{
      readonly t: number;
      readonly easing: "linear" | "ease-in" | "ease-out" | "ease-in-out";
      readonly values: TimelineValuePoint[];
    }>;
  }>;
}

export interface RecorderActionState {
  readonly lastSnapshot: SceneRecorderSnapshot | null;
  readonly undoAvailable: boolean;
  readonly lastRecordMessage: string | null;
  readonly secureOrigin: string | null;
  readonly rejectedMessages: number;
}

export interface PitchEngineUiState {
  readonly capabilityStatus: CapabilityStatus;
  readonly library: ProgramLibraryState;
  readonly transport: TransportState;
  readonly operatorHud: OperatorHudStatus;
  readonly recorder: RecorderActionState;
  readonly triageRuns: ArtifactRunIndex[];
  readonly selectedTriageItemId: string | null;
  readonly timelineWipePercent: number;
  readonly timelineZoom: number;
  readonly timelinePan: {
    readonly x: number;
    readonly y: number;
  };
  readonly reducedMotionApplied: boolean;
  readonly uiError: string | null;
}

export interface ProgramCreateInput {
  readonly name: string;
  readonly description: string;
  readonly owner: string;
}

export interface ProgramImportInput {
  readonly program: PitchProgram;
}

export interface ProgramUpdateInput {
  readonly name?: string;
  readonly description?: string;
  readonly owner?: string;
  readonly version?: string;
  readonly program?: PitchProgram;
}

export interface SequenceCreateInput {
  readonly baseSceneId: string;
  readonly name: string;
  readonly description: string;
  readonly presetId: string;
}

export interface MarkerCreateInput {
  readonly sequenceId: string;
  readonly type: MarkerType;
  readonly label: string;
  readonly t: number;
  readonly note: string;
}

export interface RecorderRequest {
  readonly snapshot: SceneRecorderSnapshot;
  readonly createSequence: boolean;
  readonly sequenceName: string;
  readonly sequencePresetId: string;
}

export interface TriageActionRequest {
  readonly action: "accept" | "reject" | "rerun" | "notes";
  readonly runId: string;
  readonly sceneId: string;
  readonly sequenceId: string;
  readonly notes?: string;
}

export interface TriageCommandContext {
  readonly runId: string;
  readonly sceneId: string;
  readonly sequenceId: string;
  readonly action: "accept" | "reject" | "rerun";
}

export interface TriageNotesContext {
  readonly runId: string;
  readonly sceneId: string;
  readonly sequenceId: string;
  readonly notes: string;
}

export interface CapabilityEvaluationInput {
  readonly requestedMode: CapabilityMode;
  readonly isDevEnvironment: boolean;
  readonly debugTokenPresent: boolean;
  readonly envOverrideEnabled: boolean;
  readonly viewportWidth: number;
  readonly prefersReducedMotion: boolean;
  readonly deviceMemoryGb: number | null;
  readonly hardwareConcurrency: number | null;
}

export interface CapabilityEvaluationResult {
  readonly requestedMode: CapabilityMode;
  readonly appliedMode: CapabilityMode;
  readonly degradeReasons: CapabilityDegradeReason[];
}

export interface ProgramSelection {
  readonly programId: string | null;
  readonly sceneId: string | null;
  readonly sequenceId: string | null;
}

export interface SceneStudioSceneRef {
  readonly id: string;
  readonly name: string;
  readonly route: string;
  readonly summary: string;
}

export interface SceneStudioTimelineViewModel {
  readonly scenes: SceneStudioSceneRef[];
  readonly programs: PitchProgram[];
  readonly selectedProgramId: string | null;
  readonly selectedSceneId: string | null;
  readonly selectedSequenceId: string | null;
  readonly scrubMs: number;
  readonly scrubMaxMs: number;
  readonly activePresetId: string | null;
}

export interface SceneStudioAccessRequest {
  readonly debugToken: boolean;
  readonly envOverride: boolean;
  readonly requestedMode: CapabilityMode;
  readonly isProductionBuild: boolean;
}

export interface SceneStudioAccessResult {
  readonly allowed: boolean;
  readonly capability: CapabilityStatus;
}
