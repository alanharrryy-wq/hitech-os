import path from "node:path";
import { fileURLToPath } from "node:url";

const THIS_DIR = path.dirname(fileURLToPath(import.meta.url));

export const KEYSTONE_ROOT = path.resolve(THIS_DIR, "../..");
export const REPO_ROOT = path.resolve(KEYSTONE_ROOT, "../..");

export const SCENES_MANIFEST_PATH = path.join(REPO_ROOT, "docs", "visual-scenes", "SCENES.json");
export const BASELINES_ROOT = path.join(
  REPO_ROOT,
  "docs",
  "visual-baselines",
  "ui-improvement-scenes"
);

export const ARTIFACTS_ROOT = path.join(REPO_ROOT, "artifacts", "keystone-scene-studio");
export const ARTIFACTS_SCENES_ROOT = path.join(ARTIFACTS_ROOT, "scenes");

export function resolveRunId(explicit?: string): string {
  if (explicit && explicit.trim().length > 0) {
    return explicit.trim();
  }

  const envRunId = process.env["SCENE_STUDIO_RUN_ID"];
  if (envRunId && envRunId.trim().length > 0) {
    return envRunId.trim();
  }

  return new Date().toISOString().replaceAll(":", "-");
}

export function resolveSceneRunDir(sceneId: string, runId: string): string {
  return path.join(ARTIFACTS_SCENES_ROOT, sceneId, runId);
}
