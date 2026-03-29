import { access, copyFile, mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import type { Browser } from "@playwright/test";
import { createPixelDiff } from "./diff.js";
import { ARTIFACTS_ROOT, BASELINES_ROOT, resolveRunId, resolveSceneRunDir } from "./paths.js";
import {
  classifyVisualChange,
  type SceneImprovementReport,
  writeSceneReport
} from "./report.js";
import { parseSceneLayerParams, type VisualSceneDefinition } from "./scene-manifest.js";
import { captureScene } from "./scene-capture.js";

export interface CompareSceneInput {
  readonly browser: Browser;
  readonly scene: VisualSceneDefinition;
  readonly baseUrl: string;
  readonly updateBaseline: boolean;
  readonly runId?: string;
}

async function exists(filePath: string): Promise<boolean> {
  try {
    await access(filePath);
    return true;
  } catch {
    return false;
  }
}

function resolveScenePaths(scene: VisualSceneDefinition, runId: string): {
  readonly sceneDir: string;
  readonly beforePath: string;
  readonly afterPath: string;
  readonly diffPath: string;
  readonly baselinePath: string;
  readonly consoleLogPath: string;
  readonly networkLogPath: string;
} {
  const sceneDir = resolveSceneRunDir(scene.id, runId);
  const beforePath = path.join(sceneDir, "before.png");
  const afterPath = path.join(sceneDir, "after.png");
  const diffPath = path.join(sceneDir, "diff.png");
  const baselinePath = path.join(BASELINES_ROOT, `${scene.id}__${scene.viewport}.png`);
  const consoleLogPath = path.join(sceneDir, "console.log");
  const networkLogPath = path.join(sceneDir, "network.log");

  return {
    sceneDir,
    beforePath,
    afterPath,
    diffPath,
    baselinePath,
    consoleLogPath,
    networkLogPath
  };
}

async function prepareBeforeSnapshot(
  baselineExists: boolean,
  baselinePath: string,
  beforePath: string,
  afterPath: string,
  updateBaseline: boolean,
  notes: string[]
): Promise<string> {
  if (baselineExists) {
    await copyFile(baselinePath, beforePath);

    if (updateBaseline) {
      notes.push("Baseline existed and was updated with AFTER snapshot.");
    } else {
      notes.push("Baseline existed and was used as BEFORE snapshot.");
    }

    return beforePath;
  }

  await copyFile(afterPath, beforePath);
  notes.push("Baseline was missing; BEFORE snapshot bootstrapped from AFTER snapshot.");

  if (updateBaseline) {
    notes.push("Update mode enabled; baseline file created.");
  } else {
    notes.push("Baseline auto-created for future comparisons.");
  }

  return beforePath;
}

function formatConsoleLogs(messages: readonly { type: string; text: string }[]): string {
  if (messages.length === 0) {
    return "(no console messages)\n";
  }

  return `${messages.map((message) => `[${message.type}] ${message.text}`).join("\n")}\n`;
}

function formatNetworkLogs(requests: readonly { method: string; url: string; status?: number }[]): string {
  if (requests.length === 0) {
    return "(no network responses captured)\n";
  }

  return `${requests
    .map((entry) => `${entry.method} ${entry.status ?? "-"} ${entry.url}`)
    .join("\n")}\n`;
}

export async function compareScene(input: CompareSceneInput): Promise<SceneImprovementReport> {
  const { scene, baseUrl, updateBaseline } = input;
  const runId = resolveRunId(input.runId);
  const paths = resolveScenePaths(scene, runId);
  const notes: string[] = [];

  await mkdir(paths.sceneDir, { recursive: true });
  await mkdir(path.dirname(paths.baselinePath), { recursive: true });

  const capture = await captureScene({
    browser: input.browser,
    scene,
    baseUrl,
    outputPath: paths.afterPath
  });

  await Promise.all([
    writeFile(paths.consoleLogPath, formatConsoleLogs(capture.consoleMessages), "utf8"),
    writeFile(paths.networkLogPath, formatNetworkLogs(capture.networkRequests), "utf8")
  ]);

  const baselineExists = await exists(paths.baselinePath);
  const beforeComparisonPath = await prepareBeforeSnapshot(
    baselineExists,
    paths.baselinePath,
    paths.beforePath,
    paths.afterPath,
    updateBaseline,
    notes
  );

  const diff = await createPixelDiff(beforeComparisonPath, paths.afterPath, paths.diffPath);
  const classification = classifyVisualChange(diff.percentChanged);
  const params = parseSceneLayerParams(scene);

  if (classification.category === "NO_CHANGE") {
    notes.push("No visual difference detected for this scene.");
  }

  if (!baselineExists || updateBaseline) {
    await copyFile(paths.afterPath, paths.baselinePath);
  }

  const report: SceneImprovementReport = {
    id: scene.id,
    runId,
    route: scene.route,
    query: scene.canonicalQuery,
    viewport: scene.viewport,
    url: capture.sceneUrl,
    layers: params.layers,
    layerProfile: params.layerProfile,
    motion: params.motion,
    timestamp: new Date().toISOString(),
    environment: {
      node: process.version,
      platform: `${process.platform}-${process.arch}`,
      browser: capture.browserVersion,
      baseUrl
    },
    artifactDir: paths.sceneDir,
    baselinePath: paths.baselinePath,
    beforePath: paths.beforePath,
    afterPath: paths.afterPath,
    diffPath: paths.diffPath,
    category: classification.category,
    changeBand: classification.band,
    evidenceScore: classification.evidenceScore,
    notes,
    diff
  };

  await writeSceneReport(paths.sceneDir, report);
  return report;
}

export async function writeRunMetadata(
  runId: string,
  reports: readonly SceneImprovementReport[]
): Promise<void> {
  await mkdir(ARTIFACTS_ROOT, { recursive: true });
  await writeFile(
    path.join(ARTIFACTS_ROOT, "run-metadata.json"),
    `${JSON.stringify(
      {
        runId,
        generatedAt: new Date().toISOString(),
        scenes: reports.map((report) => ({
          id: report.id,
          category: report.category,
          percentChanged: report.diff.percentChanged,
          artifactDir: report.artifactDir
        }))
      },
      null,
      2
    )}\n`,
    "utf8"
  );
}
