import { z } from "zod";

export const CapabilityModeSchema = z.enum(["off", "lite", "full", "debug"]);

export const CapabilityDegradeReasonSchema = z.enum([
  "reduced-motion",
  "perf",
  "viewport",
  "user-request",
  "production",
  "debug-missing",
  "env-missing",
  "capability-missing"
]);

export const TimelineValuePointSchema = z.object({
  key: z.string().min(1),
  value: z.union([z.string(), z.number(), z.boolean()])
});

export const TimelineKeyframeSchema = z.object({
  id: z.string().min(1),
  t: z.number().min(0),
  easing: z.enum(["linear", "ease-in", "ease-out", "ease-in-out"]),
  values: z.array(TimelineValuePointSchema)
});

export const TimelineTrackSchema = z.object({
  id: z.string().min(1),
  label: z.string().min(1),
  kind: z.enum([
    "camera",
    "overlay",
    "motion",
    "layers",
    "lighting",
    "subtitle",
    "audio",
    "annotation"
  ]),
  enabled: z.boolean(),
  keyframes: z.array(TimelineKeyframeSchema)
});

export const TimelineMarkerSchema = z.object({
  id: z.string().min(1),
  label: z.string().min(1),
  type: z.enum(["Reveal", "Settle", "CTA"]),
  t: z.number().min(0),
  note: z.string()
});

export const SequenceTransitionSchema = z.object({
  id: z.string().min(1),
  fromSequenceId: z.string().min(1),
  toSequenceId: z.string().min(1),
  mode: z.enum(["cut", "crossfade", "slide-left", "slide-right", "zoom-in", "zoom-out"]),
  durationMs: z.number().int().min(0)
});

export const DirectorTimelineSchema = z.object({
  durationMs: z.number().int().min(250),
  tracks: z.array(TimelineTrackSchema),
  markers: z.array(TimelineMarkerSchema),
  transitions: z.array(SequenceTransitionSchema)
});

export const SequenceDiagnosticsSchema = z.object({
  renderCost: z.enum(["low", "medium", "high"]),
  qualityWarnings: z.array(z.string()),
  lastRenderAt: z.string().nullable(),
  lastRenderId: z.string().nullable()
});

export const PitchSequenceSchema = z.object({
  id: z.string().min(1),
  sceneId: z.string().min(1),
  name: z.string().min(1),
  description: z.string(),
  cinematicPresetId: z.string().min(1),
  timeline: DirectorTimelineSchema,
  diagnostics: SequenceDiagnosticsSchema,
  createdAt: z.string().min(1),
  updatedAt: z.string().min(1)
});

export const SceneFlagSnapshotSchema = z.object({
  resolvedFlags: z.array(z.string()),
  unknownTokens: z.array(z.string())
});

export const SceneRecorderSnapshotSchema = z.object({
  route: z.string().min(1),
  canonicalUrl: z.string().min(1),
  title: z.string().min(1),
  capturedAt: z.string().min(1),
  flagSnapshot: SceneFlagSnapshotSchema,
  viewport: z.object({
    width: z.number().int().min(1),
    height: z.number().int().min(1),
    dpr: z.number().min(0.5)
  })
});

export const PitchSceneSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  route: z.string().min(1),
  canonicalUrl: z.string().min(1),
  description: z.string(),
  tags: z.array(z.string()),
  defaultSequenceId: z.string().nullable(),
  recorderSnapshot: SceneRecorderSnapshotSchema.nullable(),
  createdAt: z.string().min(1),
  updatedAt: z.string().min(1)
});

export const ProgramDiagnosticsSchema = z.object({
  source: z.enum(["fixture", "import", "user", "recorded"]),
  lastSaveError: z.string().nullable(),
  warnings: z.array(z.string()),
  artifactLinks: z.array(z.string())
});

export const PitchProgramSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  description: z.string(),
  owner: z.string().min(1),
  version: z.string().min(1),
  createdAt: z.string().min(1),
  updatedAt: z.string().min(1),
  scenes: z.array(PitchSceneSchema),
  sequences: z.array(PitchSequenceSchema),
  diagnostics: ProgramDiagnosticsSchema
});

export const OperatorHudStatusSchema = z.object({
  serverStatus: z.enum(["starting", "ready", "error"]),
  lastRunStatus: z.enum(["unknown", "ok", "fail"]),
  lastRunPath: z.string().nullable(),
  lastErrorTail: z.string().nullable(),
  lastArtifactRunId: z.string().nullable(),
  updatedAt: z.string()
});

export const CapabilityStatusSchema = z.object({
  requestedMode: CapabilityModeSchema,
  appliedMode: CapabilityModeSchema,
  degradeReasons: z.array(CapabilityDegradeReasonSchema),
  isDev: z.boolean(),
  isRouteAllowed: z.boolean(),
  isApiAllowed: z.boolean(),
  debugTokenPresent: z.boolean(),
  envOverrideEnabled: z.boolean()
});

export const ArtifactDiffFrameSchema = z.object({
  beforePath: z.string().nullable(),
  afterPath: z.string().nullable(),
  diffPath: z.string().nullable(),
  width: z.number().int().positive(),
  height: z.number().int().positive()
});

export const ArtifactTriageItemSchema = z.object({
  id: z.string().min(1),
  runId: z.string().min(1),
  sceneId: z.string().min(1),
  sequenceId: z.string().min(1),
  status: z.enum(["pending", "accepted", "rejected"]),
  score: z.number().min(0).max(1),
  notesPath: z.string().nullable(),
  diff: ArtifactDiffFrameSchema,
  createdAt: z.string(),
  updatedAt: z.string()
});

export const ArtifactRunIndexSchema = z.object({
  runId: z.string().min(1),
  createdAt: z.string().min(1),
  sourcePath: z.string().min(1),
  items: z.array(ArtifactTriageItemSchema)
});

export const BridgeEnvelopeSchema = z.object({
  type: z.literal("pitch-engine:scene-snapshot"),
  payload: SceneRecorderSnapshotSchema
});

export const ReplayPreviewPayloadSchema = z.object({
  type: z.literal("pitch-engine:replay-state"),
  payload: z.object({
    sequenceId: z.string(),
    currentMs: z.number(),
    durationMs: z.number(),
    isPlaying: z.boolean(),
    markerId: z.string().nullable()
  })
});

export const TimelinePresetScriptSchema = z.object({
  id: z.string().min(1),
  label: z.string().min(1),
  style: z.enum(["cinematic", "documentary", "product", "compliance"]),
  description: z.string(),
  durationMs: z.number().int().min(1000),
  markers: z.array(
    z.object({
      type: z.enum(["Reveal", "Settle", "CTA"]),
      t: z.number().min(0),
      label: z.string(),
      note: z.string()
    })
  ),
  tracks: z.array(
    z.object({
      kind: z.enum([
        "camera",
        "overlay",
        "motion",
        "layers",
        "lighting",
        "subtitle",
        "audio",
        "annotation"
      ]),
      label: z.string(),
      enabled: z.boolean(),
      keyframes: z.array(
        z.object({
          t: z.number(),
          easing: z.enum(["linear", "ease-in", "ease-out", "ease-in-out"]),
          values: z.array(TimelineValuePointSchema)
        })
      )
    })
  )
});

export const ProgramCreateInputSchema = z.object({
  name: z.string().min(3).max(120),
  description: z.string().max(500),
  owner: z.string().min(2).max(80)
});

export const ProgramUpdateInputSchema = z.object({
  name: z.string().min(3).max(120).optional(),
  description: z.string().max(500).optional(),
  owner: z.string().min(2).max(80).optional(),
  version: z.string().min(1).optional(),
  program: PitchProgramSchema.optional()
});

export const ProgramImportInputSchema = z.object({
  program: PitchProgramSchema
});

export const TriageActionRequestSchema = z.object({
  action: z.enum(["accept", "reject", "rerun", "notes"]),
  runId: z.string().min(1),
  sceneId: z.string().min(1),
  sequenceId: z.string().min(1),
  notes: z.string().optional()
});

export const SupportBundleRequestSchema = z.object({
  selectedProgramId: z.string().nullable(),
  selectedSceneId: z.string().nullable(),
  selectedSequenceId: z.string().nullable(),
  links: z.array(z.string()),
  capabilityStatus: CapabilityStatusSchema,
  operatorHud: OperatorHudStatusSchema,
  environment: z.object({
    userAgent: z.string(),
    viewport: z.object({
      width: z.number(),
      height: z.number(),
      dpr: z.number()
    }),
    flags: z.array(z.string())
  })
});

export const RecorderRequestSchema = z.object({
  snapshot: SceneRecorderSnapshotSchema,
  createSequence: z.boolean(),
  sequenceName: z.string(),
  sequencePresetId: z.string()
});

export type PitchProgram = z.infer<typeof PitchProgramSchema>;
export type PitchScene = z.infer<typeof PitchSceneSchema>;
export type PitchSequence = z.infer<typeof PitchSequenceSchema>;
export type CapabilityStatus = z.infer<typeof CapabilityStatusSchema>;
export type ArtifactRunIndex = z.infer<typeof ArtifactRunIndexSchema>;
export type ArtifactTriageItem = z.infer<typeof ArtifactTriageItemSchema>;
export type TimelinePresetScript = z.infer<typeof TimelinePresetScriptSchema>;
