#!/usr/bin/env node
import { readFileSync, readdirSync, statSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "../..");

const scanRoots = ["apps", "services", "packages"];
const sourceExtensions = new Set([".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs"]);

const serviceAliases = new Set(["core-api", "ai-agent"]);
const appAliases = new Set(["web", "demo-engine"]);

function toPosix(value) {
  return value.replace(/\\/g, "/");
}

function listFiles(dir) {
  const entries = readdirSync(dir, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    const absolute = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (
        entry.name === "node_modules" ||
        entry.name === "dist" ||
        entry.name === "build" ||
        entry.name === ".turbo"
      ) {
        continue;
      }
      files.push(...listFiles(absolute));
      continue;
    }

    const extension = path.extname(entry.name).toLowerCase();
    if (sourceExtensions.has(extension)) {
      files.push(absolute);
    }
  }

  return files;
}

function getPackageArea(relativeFile) {
  const segments = relativeFile.split("/");
  const root = segments[0] ?? "";
  const packageName = segments[1] ?? "";
  return {
    root,
    packageName
  };
}

function resolveRelativeTarget(relativeFile, specifier) {
  const absoluteFile = path.join(repoRoot, relativeFile);
  const absoluteTarget = path.resolve(path.dirname(absoluteFile), specifier);
  const relativeTarget = toPosix(path.relative(repoRoot, absoluteTarget));
  if (relativeTarget.startsWith("..")) {
    return null;
  }
  return relativeTarget;
}

function resolveAliasTarget(specifier) {
  const match = specifier.match(/^@hitech\/([a-z0-9-]+)/i);
  if (!match) {
    return null;
  }

  const aliasName = match[1];
  if (serviceAliases.has(aliasName)) {
    return { area: "services", name: aliasName };
  }
  if (appAliases.has(aliasName)) {
    return { area: "apps", name: aliasName };
  }

  return { area: "packages", name: aliasName };
}

function collectSpecifiers(content) {
  const results = [];

  const importExportRegex = /(?:import|export)\s+(?:[^"'`]+?\s+from\s+)?["']([^"']+)["']/g;
  const requireRegex = /require\(\s*["']([^"']+)["']\s*\)/g;

  for (const regex of [importExportRegex, requireRegex]) {
    regex.lastIndex = 0;
    let match = regex.exec(content);
    while (match) {
      const full = match[0] ?? "";
      const specifier = match[1] ?? "";
      const start = match.index + full.indexOf(specifier);
      const line = content.slice(0, start).split(/\r?\n/).length;
      results.push({ specifier, line });
      match = regex.exec(content);
    }
  }

  return results;
}

function validateSpecifier(relativeFile, specifier, line) {
  const source = getPackageArea(relativeFile);
  const violations = [];

  const pushViolation = (reason) => {
    violations.push(`${relativeFile}:${line} imports '${specifier}' (${reason})`);
  };

  if (specifier.startsWith(".")) {
    const target = resolveRelativeTarget(relativeFile, specifier);
    if (!target) {
      return violations;
    }

    const targetArea = getPackageArea(target);

    if (
      source.root === "packages" &&
      (targetArea.root === "apps" || targetArea.root === "services")
    ) {
      pushViolation("packages may not import from apps/services");
      return violations;
    }

    if (
      source.root === "services" &&
      targetArea.root === "services" &&
      source.packageName !== targetArea.packageName
    ) {
      pushViolation("services may not import from other services directly");
      return violations;
    }

    if (source.root === "apps" && targetArea.root === "services") {
      pushViolation("apps may not import services directly");
      return violations;
    }

    return violations;
  }

  const aliasTarget = resolveAliasTarget(specifier);
  if (!aliasTarget) {
    return violations;
  }

  if (
    source.root === "packages" &&
    (aliasTarget.area === "apps" || aliasTarget.area === "services")
  ) {
    pushViolation("packages may only depend on packages");
    return violations;
  }

  if (
    source.root === "services" &&
    aliasTarget.area === "services" &&
    source.packageName !== aliasTarget.name
  ) {
    pushViolation("services may not depend on sibling services");
    return violations;
  }

  if (source.root === "apps" && aliasTarget.area === "services") {
    pushViolation("apps may not depend on services");
    return violations;
  }

  return violations;
}

const violations = [];

for (const root of scanRoots) {
  const absoluteRoot = path.join(repoRoot, root);
  if (!statSync(absoluteRoot, { throwIfNoEntry: false })) {
    continue;
  }

  const files = listFiles(absoluteRoot)
    .map((filePath) => toPosix(path.relative(repoRoot, filePath)))
    .sort((left, right) => left.localeCompare(right));

  for (const relativeFile of files) {
    const content = readFileSync(path.join(repoRoot, relativeFile), "utf8");
    const specifiers = collectSpecifiers(content);

    for (const { specifier, line } of specifiers) {
      violations.push(...validateSpecifier(relativeFile, specifier, line));
    }
  }
}

violations.sort((left, right) => left.localeCompare(right));

if (violations.length > 0) {
  console.error("[workspace:validate] FAILED");
  for (const violation of violations) {
    console.error(` - ${violation}`);
  }
  process.exit(1);
}

console.log("[workspace:validate] OK");
