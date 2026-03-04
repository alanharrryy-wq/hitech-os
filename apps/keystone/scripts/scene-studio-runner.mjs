import { spawnSync } from "node:child_process";
import process from "node:process";

function parseArgValue(args, key) {
  const prefix = `--${key}=`;
  const match = args.find((arg) => arg.startsWith(prefix));
  return match ? match.slice(prefix.length) : undefined;
}

const args = process.argv.slice(2);
const passthroughIndex = args.indexOf("--");

const updateBaseline = args.includes("--update-baseline");
const strict = args.includes("--strict");
const smoke = args.includes("--smoke");
const full = args.includes("--full");
const serverMode = parseArgValue(args, "server-mode") ?? "prod";
const strictThreshold = parseArgValue(args, "strict-threshold");
const routeFilter = parseArgValue(args, "route");
const claimId = parseArgValue(args, "claim-id");
const runId = parseArgValue(args, "run-id") ?? claimId ?? new Date().toISOString().replaceAll(":", "-");

const sceneIds = args
  .filter((arg) => arg.startsWith("--scene-id="))
  .map((arg) => arg.slice("--scene-id=".length))
  .filter((value) => value.length > 0);

const sceneTags = args
  .filter((arg) => arg.startsWith("--tag="))
  .map((arg) => arg.slice("--tag=".length))
  .filter((value) => value.length > 0);

const consumed = new Set([
  "--update-baseline",
  "--strict",
  "--smoke",
  "--full",
  ...args.filter((arg) =>
    [
      "--strict-threshold=",
      "--route=",
      "--run-id=",
      "--claim-id=",
      "--server-mode=",
      "--scene-id=",
      "--tag="
    ]
      .some((prefix) => arg.startsWith(prefix))
  )
]);

const passthroughArgs =
  passthroughIndex >= 0
    ? args.slice(passthroughIndex + 1)
    : args.filter((arg) => !consumed.has(arg));

const env = {
  ...process.env,
  UI_IMPROVEMENT_SERVER_MODE: serverMode,
  SCENE_STUDIO_RUN_ID: runId,
  SCENE_STUDIO_SMOKE: smoke && !full ? "1" : "0",
  ...(updateBaseline ? { UI_IMPROVEMENT_UPDATE_BASELINE: "1" } : {}),
  ...(strict ? { UI_IMPROVEMENT_STRICT: "1" } : {}),
  ...(strictThreshold ? { UI_IMPROVEMENT_STRICT_THRESHOLD: strictThreshold } : {}),
  ...(routeFilter ? { SCENE_STUDIO_FILTER_ROUTE: routeFilter } : {}),
  ...(sceneIds.length > 0 ? { SCENE_STUDIO_FILTER_IDS: sceneIds.join(",") } : {}),
  ...(sceneTags.length > 0 ? { SCENE_STUDIO_FILTER_TAGS: sceneTags.join(",") } : {})
};

const commandArgs = [
  "exec",
  "playwright",
  "test",
  "--config",
  "playwright.config.ts",
  "visual-tests/ui-improvement.spec.ts",
  ...passthroughArgs
];

const result = spawnSync("pnpm", commandArgs, {
  cwd: process.cwd(),
  env,
  stdio: "inherit",
  shell: process.platform === "win32"
});

if (typeof result.status === "number") {
  process.exit(result.status);
}

if (result.error) {
  throw result.error;
}

process.exit(1);
