import { access, readdir, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import process from "node:process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "../../..");

const claimsRoot = path.join(repoRoot, "docs", "quality", "IMPROVEMENT_CLAIMS");
const artifactsRoot = path.join(repoRoot, "artifacts", "keystone-scene-studio", "scenes");

const claimArg = process.argv.slice(2).find((arg) => arg.startsWith("--claim-id="));
const explicitClaimId = claimArg ? claimArg.slice("--claim-id=".length) : "";

async function exists(filePath) {
  try {
    await access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function resolveClaimId() {
  if (explicitClaimId) {
    return explicitClaimId;
  }

  const files = (await readdir(claimsRoot, { withFileTypes: true }))
    .filter((entry) => entry.isFile() && entry.name.endsWith(".md"))
    .map((entry) => entry.name)
    .sort((left, right) => right.localeCompare(left));

  const latest = files[0];
  if (!latest) {
    throw new Error("No improvement claim files were found.");
  }

  return latest.replace(/\.md$/, "");
}

async function collectRunArtifacts(runId) {
  const sceneDirs = await readdir(artifactsRoot, { withFileTypes: true });
  const runDirs = [];

  for (const sceneEntry of sceneDirs) {
    if (!sceneEntry.isDirectory()) {
      continue;
    }

    const sceneRunPath = path.join(artifactsRoot, sceneEntry.name, runId);
    if (await exists(sceneRunPath)) {
      runDirs.push({
        sceneId: sceneEntry.name,
        runPath: sceneRunPath
      });
    }
  }

  return runDirs;
}

async function validateRunArtifacts(runId) {
  const runDirs = await collectRunArtifacts(runId);
  if (runDirs.length === 0) {
    throw new Error(`Claim ${runId} has no generated scene artifacts.`);
  }

  const errors = [];

  for (const run of runDirs) {
    const diffPath = path.join(run.runPath, "diff.png");
    const reportPath = path.join(run.runPath, "report.md");
    const jsonPath = path.join(run.runPath, "report.json");

    if (!(await exists(diffPath))) {
      errors.push(`[${run.sceneId}] missing diff.png`);
    }

    if (!(await exists(reportPath)) || !(await exists(jsonPath))) {
      errors.push(`[${run.sceneId}] missing report.md or report.json`);
    }
  }

  if (errors.length > 0) {
    throw new Error(errors.join("\n"));
  }

  return runDirs.length;
}

async function main() {
  const runId = await resolveClaimId();
  const claimPath = path.join(claimsRoot, `${runId}.md`);

  if (!(await exists(claimPath))) {
    throw new Error(`Claim file not found: ${claimPath}`);
  }

  const claimText = await readFile(claimPath, "utf8");
  if (!claimText.includes("# Improvement Claim")) {
    throw new Error(`Claim file ${claimPath} does not follow required convention.`);
  }

  const count = await validateRunArtifacts(runId);
  process.stdout.write(`Proof gate passed for claim ${runId}. scenes=${count}\n`);
}

await main();
