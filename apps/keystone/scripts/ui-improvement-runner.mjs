import { spawnSync } from "node:child_process";
import process from "node:process";

const args = process.argv.slice(2);
const passthroughIndex = args.indexOf("--");
const updateBaseline = args.includes("--update-baseline");
const strict = args.includes("--strict");
const strictThresholdArg = args.find((arg) => arg.startsWith("--strict-threshold="));
const serverModeArg = args.find((arg) => arg.startsWith("--server-mode="));

const customArgs = new Set(
  [updateBaseline ? "--update-baseline" : "", strict ? "--strict" : ""].filter(Boolean)
);
if (strictThresholdArg) {
  customArgs.add(strictThresholdArg);
}
if (serverModeArg) {
  customArgs.add(serverModeArg);
}

const passthroughArgs =
  passthroughIndex >= 0
    ? args.slice(passthroughIndex + 1)
    : args.filter((arg) => !customArgs.has(arg));

const env = {
  ...process.env,
  ...(updateBaseline ? { UI_IMPROVEMENT_UPDATE_BASELINE: "1" } : {}),
  ...(strict ? { UI_IMPROVEMENT_STRICT: "1" } : {}),
  ...(strictThresholdArg
    ? { UI_IMPROVEMENT_STRICT_THRESHOLD: strictThresholdArg.split("=")[1] ?? "" }
    : {}),
  ...(serverModeArg ? { UI_IMPROVEMENT_SERVER_MODE: serverModeArg.split("=")[1] ?? "" } : {})
};

const commandArgs = ["exec", "playwright", "test", "--config", "playwright.config.ts", ...passthroughArgs];
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
