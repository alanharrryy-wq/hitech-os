#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

function parseArgs(argv) {
  const parsed = {
    runId: process.env.RUN_ID ?? "",
    failIfNoRunId: false
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--run-id") {
      parsed.runId = argv[i + 1] ?? parsed.runId;
      i += 1;
    }
    if (arg === "--fail-if-no-run-id") {
      parsed.failIfNoRunId = true;
    }
  }

  return parsed;
}

function runGit(args) {
  const result = spawnSync("git", args, {
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"]
  });

  if (result.status !== 0) {
    throw new Error(result.stderr.trim() || `git ${args.join(" ")} failed with ${result.status}`);
  }

  return result.stdout;
}

function collectChangedPaths() {
  const porcelain = runGit(["status", "--porcelain"])
    .split(/\r?\n/u)
    .map((line) => line.trimEnd())
    .filter((line) => line.length > 0);

  const paths = [];

  for (const line of porcelain) {
    if (line.length < 4) {
      continue;
    }

    const payload = line.slice(3);
    if (payload.includes(" -> ")) {
      const parts = payload.split(" -> ");
      const last = parts[parts.length - 1];
      if (last) {
        paths.push(last.replace(/\\/g, "/"));
      }
      continue;
    }

    paths.push(payload.replace(/\\/g, "/"));
  }

  return [...new Set(paths)].sort((a, b) => a.localeCompare(b));
}

const UI_TOUCH_PATTERNS = [
  /^apps\/keystone\/app\/pitch\//u,
  /^apps\/keystone\/components\/pitch\//u,
  /^apps\/keystone\/app\/dev\/(pitch-engine|scene-studio)\//u
];

function isUiTouch(filePath) {
  return UI_TOUCH_PATTERNS.some((pattern) => pattern.test(filePath));
}

function exists(filePath) {
  return fs.existsSync(path.resolve(process.cwd(), filePath));
}

function readIfExists(filePath) {
  const abs = path.resolve(process.cwd(), filePath);
  if (!fs.existsSync(abs)) {
    return "";
  }
  return fs.readFileSync(abs, "utf8");
}

function evaluateProof(runId, uiTouched) {
  if (!uiTouched) {
    return {
      claimRequired: false,
      claimPath: "",
      claimExists: true,
      artifactProofFound: true,
      notes: ["UI-affecting paths were not touched; claim/proof gate not required."]
    };
  }

  const claimPath = runId ? `docs/quality/IMPROVEMENT_CLAIMS/${runId}.md` : "";
  const claimExists = claimPath.length > 0 ? exists(claimPath) : false;

  const artifactsIndexCandidates = [
    "artifacts/keystone-pitch-engine/index.json",
    "artifacts/keystone-pitch-engine/verification_last.json",
    "docs/quality/PITCH_ENGINE_ACCEPTANCE.md"
  ];

  const claimText = claimExists ? readIfExists(claimPath) : "";
  const acceptanceText = readIfExists("docs/quality/PITCH_ENGINE_ACCEPTANCE.md");

  const artifactProofFound =
    artifactsIndexCandidates.some((candidate) => exists(candidate)) ||
    claimText.includes("artifacts/keystone-pitch-engine") ||
    acceptanceText.includes("artifacts/keystone-pitch-engine");

  const notes = [];
  if (!claimExists) {
    notes.push(
      `Missing claim file: ${claimPath || "docs/quality/IMPROVEMENT_CLAIMS/<RUN_ID>.md"}`
    );
  }
  if (!artifactProofFound) {
    notes.push("Missing artifact proof reference (index/report path not found). ");
  }

  return {
    claimRequired: true,
    claimPath,
    claimExists,
    artifactProofFound,
    notes
  };
}

function main() {
  const args = parseArgs(process.argv.slice(2));

  if (!args.runId && args.failIfNoRunId) {
    console.log("FAIL pitch_engine_gate run-id is required when --fail-if-no-run-id is set");
    process.exit(1);
  }

  const changedPaths = collectChangedPaths();
  const uiTouchedPaths = changedPaths.filter((item) => isUiTouch(item));
  const uiTouched = uiTouchedPaths.length > 0;

  const proof = evaluateProof(args.runId, uiTouched);

  const pass = !uiTouched || (proof.claimExists && proof.artifactProofFound);

  const report = {
    gate: "pitch_engine_gate",
    runId: args.runId,
    pass,
    uiTouched,
    changedPaths,
    uiTouchedPaths,
    claimRequired: proof.claimRequired,
    claimPath: proof.claimPath,
    claimExists: proof.claimExists,
    artifactProofFound: proof.artifactProofFound,
    notes: proof.notes
  };

  const statusLine = `${pass ? "PASS" : "FAIL"} pitch_engine_gate ui_touched=${uiTouchedPaths.length} changed=${changedPaths.length}`;
  console.log(statusLine);
  console.log(JSON.stringify(report, null, 2));

  process.exit(pass ? 0 : 1);
}

main();
