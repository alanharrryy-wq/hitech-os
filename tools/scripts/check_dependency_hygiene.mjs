#!/usr/bin/env node
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import process from "node:process";
import {
  loadDependencyPolicyModel,
  resolveRepoRoot,
  toPosix
} from "./lib/dependency_policy.mjs";

const repoRoot = resolveRepoRoot(import.meta.url);
const dependencySections = ["dependencies", "devDependencies", "optionalDependencies"];

function parseArgs(argv) {
  const args = {
    policy: "policies/dependencies.json",
    workspace: "pnpm-workspace.yaml",
    output: null
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    const next = argv[index + 1];

    if (token === "--policy" && next) {
      args.policy = next;
      index += 1;
      continue;
    }

    if (token === "--workspace" && next) {
      args.workspace = next;
      index += 1;
      continue;
    }

    if (token === "--output" && next) {
      args.output = next;
      index += 1;
      continue;
    }
  }

  return args;
}

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

function main() {
  const args = parseArgs(process.argv.slice(2));
  const model = loadDependencyPolicyModel({
    repoRoot,
    policyPath: args.policy,
    workspacePath: args.workspace
  });

  const policyErrors = [...model.validation.errors];
  const policyWarnings = [...model.validation.warnings];
  if (
    model.workspace.pattern_sync.only_in_policy.length > 0 ||
    model.workspace.pattern_sync.only_in_pnpm_workspace.length > 0
  ) {
    policyErrors.push("workspace pattern drift between dependencies policy and pnpm-workspace.yaml");
  }

  const packageFiles = [
    "package.json",
    ...[...model.projects.values()].map((project) => project.manifestPath)
  ].sort((left, right) => left.localeCompare(right));

  const issues = [];
  const missingPackageFiles = [];

  for (const relativePath of packageFiles) {
    const absolutePath = path.join(repoRoot, relativePath);
    if (!existsSync(absolutePath)) {
      missingPackageFiles.push(relativePath);
      continue;
    }

    const content = readFileSync(absolutePath, "utf8");
    const parsed = JSON.parse(content);

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
  missingPackageFiles.sort((left, right) => left.localeCompare(right));

  const report = {
    schema_version: 2,
    generated_at_utc: new Date().toISOString(),
    policy_path: toPosix(path.relative(repoRoot, path.resolve(repoRoot, args.policy))),
    workspace_path: toPosix(path.relative(repoRoot, path.resolve(repoRoot, args.workspace))),
    policy_validation: {
      error_count: policyErrors.length,
      warning_count: policyWarnings.length,
      errors: policyErrors,
      warnings: policyWarnings
    },
    workspace_model: {
      effective_patterns: model.workspace.effective_patterns,
      pattern_sync: model.workspace.pattern_sync,
      discovery_anomalies: model.workspace.discovery_anomalies,
      retired_entries_present: model.workspace.retired_entries_present
    },
    manifests: {
      checked_count: packageFiles.length - missingPackageFiles.length,
      missing_count: missingPackageFiles.length,
      missing: missingPackageFiles
    },
    issues: {
      count: issues.length,
      entries: issues
    },
    status: policyErrors.length > 0 || issues.length > 0 ? "fail" : "pass"
  };

  if (args.output) {
    const outputPath = path.resolve(repoRoot, args.output);
    mkdirSync(path.dirname(outputPath), { recursive: true });
    writeFileSync(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
  }

  if (policyErrors.length > 0 || issues.length > 0) {
    console.error("[deps:check] FAILED");
    for (const issue of policyErrors) {
      console.error(` - policy: ${issue}`);
    }
    for (const issue of issues) {
      console.error(` - ${issue}`);
    }
    process.exit(1);
  }

  if (policyWarnings.length > 0 || missingPackageFiles.length > 0) {
    if (policyWarnings.length > 0) {
      console.warn("[deps:check] warnings:");
      for (const warning of policyWarnings) {
        console.warn(` - policy: ${warning}`);
      }
    }
    if (missingPackageFiles.length > 0) {
      console.warn(`[deps:check] warning: skipped missing manifests (${missingPackageFiles.length})`);
      for (const relativePath of missingPackageFiles) {
        console.warn(` - ${relativePath}`);
      }
    }
  }

  console.log(`[deps:check] OK (${packageFiles.length - missingPackageFiles.length} package manifests)`);
}

main();
