#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "../..");

const packageFiles = [
  "package.json",
  "apps/demo-engine/package.json",
  "factory/package.json",
  "packages/contracts/package.json",
  "packages/tooling/package.json",
  "packages/ui-kit/package.json",
  "services/ai-agent/package.json",
  "services/core-api/package.json",
  "tools/health/package.json",
  "tools/scripts/package.json"
];

const dependencySections = ["dependencies", "devDependencies", "optionalDependencies"];

function isPinnedVersion(version) {
  if (version.startsWith("workspace:")) {
    return true;
  }
  if (version.startsWith("file:") || version.startsWith("link:")) {
    return true;
  }
  if (version === "latest" || version === "*") {
    return false;
  }
  return !/^[~^<>*]|\bx\b|\*/.test(version);
}

function isSorted(keys) {
  const sorted = [...keys].sort((left, right) => left.localeCompare(right));
  return keys.every((value, index) => value === sorted[index]);
}

const issues = [];
const skippedManifests = [];
let scannedManifestCount = 0;

for (const relativePath of packageFiles) {
  const absolutePath = path.join(repoRoot, relativePath);
  if (!existsSync(absolutePath)) {
    skippedManifests.push(relativePath);
    continue;
  }

  const content = readFileSync(absolutePath, "utf8");
  const parsed = JSON.parse(content);
  scannedManifestCount += 1;

  for (const section of dependencySections) {
    const deps = parsed[section];
    if (!deps || typeof deps !== "object") {
      continue;
    }

    const names = Object.keys(deps);
    if (!isSorted(names)) {
      issues.push(`${relativePath}: ${section} keys must be sorted`);
    }

    for (const name of names) {
      const version = String(deps[name]);
      if (!isPinnedVersion(version)) {
        issues.push(`${relativePath}: ${section}.${name} has non-pinned version '${version}'`);
      }
    }
  }
}

issues.sort((left, right) => left.localeCompare(right));

if (issues.length > 0) {
  console.error("[deps:check] FAILED");
  for (const issue of issues) {
    console.error(` - ${issue}`);
  }
  if (skippedManifests.length > 0) {
    console.error(` - skipped missing manifests: ${skippedManifests.join(", ")}`);
  }
  process.exit(1);
}

if (skippedManifests.length > 0) {
  console.warn(`[deps:check] skipped missing manifests: ${skippedManifests.join(", ")}`);
}
console.log(`[deps:check] OK (${scannedManifestCount} package manifests)`);
