export const KNOWN_PITCH_ROUTES = [
  "/pitch",
  "/pitch/01-double-engine",
  "/pitch/02-industrial-flow",
  "/pitch/03-hitech-os",
  "/pitch/04-valuation"
] as const;

// Import the correct SceneRecord type from scene-schema
export type { SceneRecord } from "./scene-studio/scene-schema";

// Re-export from scene-bridge
export {
  isDiagnosticsResponseMessage,
  isAllowedSceneStudioOrigin,
  SCENE_STUDIO_RESPONSE_DIAGNOSTICS,
  isDiagnosticsRequestMessage,
  SCENE_STUDIO_REQUEST_DIAGNOSTICS,
  type SceneDiagnosticsPayload,
} from "./scene-studio/scene-bridge";

// Re-export from scene-url
export {
  buildCanonicalSceneQuery,
  buildCanonicalSceneUrl,
  parseSceneUrlState,
  resolveSceneQueryPrecedence,
} from "./scene-studio/scene-url";

// Re-export from scene-query
export { parseSceneQueryToObject } from "./scene-studio/scene-query";

// Re-export from scene-access
export { resolveSceneStudioAccess } from "./scene-studio/scene-access";

// Re-export from scene-store
export {
  InMemorySceneStore,
  LocalSceneStore,
  parseSceneExport,
  serializeSceneExport,
  type SceneImportMode,
  type SceneImportResult,
} from "./scene-studio/scene-store";

// Re-export from default-scenes
export { createDefaultSceneLibrary } from "./scene-studio/default-scenes";

// Re-export from scene-id
export {
  createDuplicateSceneId,
  ensureSceneId,
} from "./scene-studio/scene-id";

// Re-export from scene-diagnostics
export { buildSceneDiagnosticsPayload } from "./scene-studio/scene-diagnostics";

// Re-export from scene-validator
export { validateSceneDiagnostics } from "./scene-studio/scene-validator";

// Re-export from scene-tags
export { buildSceneTagIndex, searchScenes } from "./scene-studio/scene-tags";

// Re-export from scene-schema
export {
  inferLayersFromQuery,
  normalizeSceneInput,
  validateScene,
} from "./scene-studio/scene-schema";

// Re-export from scene-migrations
export { migrateScene, migrateScenes } from "./scene-studio/scene-migrations";
