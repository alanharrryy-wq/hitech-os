#!/usr/bin/env node
import { mkdirSync, readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import path from "node:path";
import process from "node:process";
import {
  loadDependencyPolicyModel,
  resolveRepoRoot,
  rootOfProjectPath,
  toPosix
} from "./lib/dependency_policy.mjs";

const repoRoot = resolveRepoRoot(import.meta.url);
const sourceExtensions = new Set([".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs"]);

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
    }
  }

  return args;
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

function detectTargetRoot({
  relativeFile,
  specifier,
  workspaceRoots,
  packageNameToProject
}) {
  if (specifier.startsWith(".")) {
    const absoluteFile = path.join(repoRoot, relativeFile);
    const absoluteTarget = path.resolve(path.dirname(absoluteFile), specifier);
    const relativeTarget = toPosix(path.relative(repoRoot, absoluteTarget));
    if (relativeTarget.startsWith("..")) {
      return null;
    }
    return rootOfProjectPath(relativeTarget);
  }

  if (specifier.startsWith("@hitech/")) {
    const targetProject = packageNameToProject.get(specifier);
    if (!targetProject) {
      return null;
    }
    return rootOfProjectPath(targetProject);
  }

  for (const root of workspaceRoots) {
    if (specifier === root || specifier.startsWith(`${root}/`)) {
      return root;
    }
  }

  return null;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const model = loadDependencyPolicyModel({
    repoRoot,
    policyPath: args.policy,
    workspacePath: args.workspace
  });

  const policyValidationErrors = [...model.validation.errors];
  const policyValidationWarnings = [...model.validation.warnings];
  if (
    model.workspace.pattern_sync.only_in_policy.length > 0 ||
    model.workspace.pattern_sync.only_in_pnpm_workspace.length > 0
  ) {
    policyValidationErrors.push(
      "workspace pattern drift between dependencies policy and pnpm-workspace.yaml"
    );
  }

  const boundaryModel = model.policy.boundary_model ?? {};
  const workspaceRoots = model.workspace.roots;
  const configuredScanRoots = Array.isArray(model.policy.boundary_source_scan_roots)
    ? model.policy.boundary_source_scan_roots
        .map((value) => String(value).trim())
        .filter((value) => value.length > 0)
    : [];
  const sourceScanRoots =
    configuredScanRoots.length > 0
      ? configuredScanRoots.filter((root) => workspaceRoots.includes(root))
      : workspaceRoots;
  const boundaryViolations = [];
  const unmatchedSpecifiers = [];
  const filesScanned = [];

  for (const root of sourceScanRoots) {
    const absoluteRoot = path.join(repoRoot, root);
    if (!statSync(absoluteRoot, { throwIfNoEntry: false })) {
      continue;
    }

    const files = listFiles(absoluteRoot)
      .map((filePath) => toPosix(path.relative(repoRoot, filePath)))
      .sort((left, right) => left.localeCompare(right));

    for (const relativeFile of files) {
      filesScanned.push(relativeFile);
      const sourceRoot = rootOfProjectPath(relativeFile);
      const allowedTargets = Array.isArray(boundaryModel[sourceRoot]) ? boundaryModel[sourceRoot] : [];

      const content = readFileSync(path.join(repoRoot, relativeFile), "utf8");
      const specifiers = collectSpecifiers(content);

      for (const { specifier, line } of specifiers) {
        const targetRoot = detectTargetRoot({
          relativeFile,
          specifier,
          workspaceRoots,
          packageNameToProject: model.packageNameToProject
        });

        if (!targetRoot || targetRoot === sourceRoot) {
          continue;
        }

        if (allowedTargets.length === 0) {
          unmatchedSpecifiers.push(`${relativeFile}:${line} imports '${specifier}' (no boundary model for ${sourceRoot})`);
          continue;
        }

        if (!allowedTargets.includes(targetRoot)) {
          boundaryViolations.push(
            `${relativeFile}:${line} imports '${specifier}' (${sourceRoot} -> ${targetRoot} not allowed by dependencies policy)`
          );
        }
      }
    }
  }

  boundaryViolations.sort((left, right) => left.localeCompare(right));
  unmatchedSpecifiers.sort((left, right) => left.localeCompare(right));

  const report = {
    schema_version: 2,
    generated_at_utc: new Date().toISOString(),
    policy_path: toPosix(path.relative(repoRoot, path.resolve(repoRoot, args.policy))),
    workspace_path: toPosix(path.relative(repoRoot, path.resolve(repoRoot, args.workspace))),
    workspace_model: {
      roots: model.workspace.roots,
      source_scan_roots: sourceScanRoots,
      effective_patterns: model.workspace.effective_patterns,
      pattern_sync: model.workspace.pattern_sync,
      retired_entries_present: model.workspace.retired_entries_present
    },
    validation: {
      policy_error_count: policyValidationErrors.length,
      policy_warning_count: policyValidationWarnings.length,
      policy_errors: policyValidationErrors,
      policy_warnings: policyValidationWarnings
    },
    scan: {
      file_count: filesScanned.length
    },
    boundary_violations: {
      count: boundaryViolations.length,
      entries: boundaryViolations
    },
    unresolved_boundary_sources: {
      count: unmatchedSpecifiers.length,
      entries: unmatchedSpecifiers
    },
    status:
      policyValidationErrors.length > 0 || boundaryViolations.length > 0 || unmatchedSpecifiers.length > 0
        ? "fail"
        : "pass"
  };

  if (args.output) {
    const serialized = `${JSON.stringify(report, null, 2)}\n`;
    const outputPath = path.resolve(repoRoot, args.output);
    mkdirSync(path.dirname(outputPath), { recursive: true });
    writeFileSync(outputPath, serialized, "utf8");
  }

  if (report.status !== "pass") {
    process.stderr.write("[workspace:validate] FAILED\n");
    for (const error of policyValidationErrors) {
      process.stderr.write(` - policy: ${error}\n`);
    }
    for (const violation of boundaryViolations) {
      process.stderr.write(` - ${violation}\n`);
    }
    for (const unresolved of unmatchedSpecifiers.slice(0, 200)) {
      process.stderr.write(` - ${unresolved}\n`);
    }
    process.exit(1);
  }

  process.stdout.write(`[workspace:validate] OK (${filesScanned.length} files scanned)\n`);
}

main();
