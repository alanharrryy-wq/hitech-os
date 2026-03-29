import { execSync, spawnSync } from "node:child_process";
import process from "node:process";

const diffBase = process.env["SCENE_CI_DIFF_BASE"] ?? "HEAD~1";

function readChangedFiles() {
  try {
    const output = execSync(`git diff --name-only ${diffBase} HEAD`, {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"]
    });

    return output
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter((line) => line.length > 0);
  } catch {
    return [];
  }
}

const changedFiles = readChangedFiles();
const shouldRunVisual = changedFiles.some((file) =>
  file.startsWith("apps/keystone/app/pitch/") ||
  file.startsWith("apps/keystone/components/pitch/") ||
  file.startsWith("packages/ui-kit/src/layers/")
);

if (!shouldRunVisual) {
  process.stdout.write("No Keystone pitch/layer changes detected. Visual smoke run skipped.\n");
  process.exit(0);
}

process.stdout.write("Keystone pitch/layer changes detected. Running visual smoke suite...\n");

const result = spawnSync("pnpm", ["--filter", "@hitech/keystone", "keystone:scene:visual:smoke"], {
  stdio: "inherit",
  shell: process.platform === "win32"
});

process.exit(result.status ?? 1);
