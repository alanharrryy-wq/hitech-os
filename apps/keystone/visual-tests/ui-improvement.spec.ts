import { test } from "@playwright/test";
import { ARTIFACTS_ROOT, resolveRunId } from "./helpers/paths.js";
import { writeSummaryReport } from "./helpers/report.js";
import { filterSceneManifest, loadSceneManifest } from "./helpers/scene-manifest.js";
import { compareScene, writeRunMetadata } from "./helpers/scene-compare.js";

const UPDATE_BASELINE = process.env["UI_IMPROVEMENT_UPDATE_BASELINE"] === "1";
const STRICT_MODE = process.env["UI_IMPROVEMENT_STRICT"] === "1";
const STRICT_THRESHOLD = Number(process.env["UI_IMPROVEMENT_STRICT_THRESHOLD"] ?? "5");
const BASE_URL = process.env["UI_IMPROVEMENT_BASE_URL"] ?? "http://127.0.0.1:3100";
const RUN_ID = resolveRunId(process.env["SCENE_STUDIO_RUN_ID"]);

const manifest = await loadSceneManifest();
const sceneFilterIds = (process.env["SCENE_STUDIO_FILTER_IDS"] ?? "")
  .split(",")
  .map((value) => value.trim())
  .filter((value) => value.length > 0);
const sceneFilterTags = (process.env["SCENE_STUDIO_FILTER_TAGS"] ?? "")
  .split(",")
  .map((value) => value.trim())
  .filter((value) => value.length > 0);
const sceneFilterRoute = (process.env["SCENE_STUDIO_FILTER_ROUTE"] ?? "").trim();
const smokeOnly = process.env["SCENE_STUDIO_SMOKE"] === "1";

const scenes = filterSceneManifest(manifest, {
  ...(sceneFilterIds.length > 0 ? { ids: sceneFilterIds } : {}),
  ...(sceneFilterTags.length > 0 ? { tags: sceneFilterTags } : {}),
  ...(sceneFilterRoute ? { route: sceneFilterRoute } : {}),
  smoke: smokeOnly
});
const reports: Awaited<ReturnType<typeof compareScene>>[] = [];

test.describe("UI Improvement Validation", () => {
  test.describe.configure({ mode: "serial" });

  test("manifest selection has at least one scene", async () => {
    if (scenes.length === 0) {
      throw new Error("No scenes selected. Check SCENE_STUDIO filters and manifest data.");
    }
  });

  for (const scene of scenes) {
    test(`scene:${scene.id}`, async ({ browser }) => {
      const report = await compareScene({
        browser,
        scene,
        baseUrl: BASE_URL,
        updateBaseline: UPDATE_BASELINE,
        runId: RUN_ID
      });

      reports.push(report);

      if (STRICT_MODE && report.diff.percentChanged > STRICT_THRESHOLD) {
        throw new Error(
          `Strict mode failed for scene "${scene.id}": ${report.diff.percentChanged.toFixed(4)}% > ${STRICT_THRESHOLD.toFixed(4)}%`
        );
      }
    });
  }

  test.afterAll(async () => {
    await writeSummaryReport(ARTIFACTS_ROOT, reports);
    await writeRunMetadata(RUN_ID, reports);
  });
});
