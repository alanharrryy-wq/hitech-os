#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import process from "node:process";
import {
  buildWorkspaceDependencyGraph,
  loadDependencyPolicyModel,
  resolveRepoRoot,
  toPosix
} from "./lib/dependency_policy.mjs";

const repoRoot = resolveRepoRoot(import.meta.url);

const GLOBAL_PATH_PREFIXES = [".github/", ".husky/"];
const GLOBAL_PATHS = new Set([
  "package.json",
  "pnpm-lock.yaml",
  "pnpm-workspace.yaml",
  "turbo.json",
  "tsconfig.base.json",
  "tsconfig.json",
  ".editorconfig",
  ".eslintrc.cjs",
  "eslint.config.mjs",
  ".prettierrc",
  "prettier.config.cjs",
  "commitlint.config.cjs",
  "policies/dependencies.json"
]);

function parseArgs(argv) {
  const args = {
    base: process.env.AFFECTED_BASE ?? null,
    head: process.env.AFFECTED_HEAD ?? "HEAD",
    policy: "policies/dependencies.json",
    workspace: "pnpm-workspace.yaml",
    output: null,
    useTripleDot: true
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    const next = argv[index + 1];

    if (token === "--base" && next) {
      args.base = next;
      index += 1;
      continue;
    }

    if (token === "--head" && next) {
      args.head = next;
      index += 1;
      continue;
    }

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

    if (token === "--two-dot") {
      args.useTripleDot = false;
      continue;
    }
  }

  if (!args.base) {
    args.base = "HEAD~1";
  }

  return args;
}

function runGitDiff(base, head, tripleDot) {
  const refs = tripleDot ? `${base}...${head}` : `${base}..${head}`;
  const output = execFileSync("git", ["diff", "--name-only", refs], {
    cwd: repoRoot,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"]
  });
  return output
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .map((line) => toPosix(line));
}

function collectChangedFiles(base, head, preferTripleDot) {
  if (preferTripleDot) {
    try {
      return {
        files: runGitDiff(base, head, true),
        mode: "triple-dot"
      };
    } catch {
      return {
        files: runGitDiff(base, head, false),
        mode: "two-dot-fallback"
      };
    }
  }

  return {
    files: runGitDiff(base, head, false),
    mode: "two-dot"
  };
}

function fileHitsGlobalTrigger(relativePath) {
  if (GLOBAL_PATHS.has(relativePath)) {
    return true;
  }
  return GLOBAL_PATH_PREFIXES.some((prefix) => relativePath.startsWith(prefix));
}

function mapChangedFilesToProjects(changedFiles, projectPaths) {
  const sortedProjects = [...projectPaths].sort((left, right) => right.length - left.length);
  const fileToProject = new Map();
  const unmatchedFiles = [];
  let globalTrigger = false;

  for (const filePath of changedFiles) {
    if (fileHitsGlobalTrigger(filePath)) {
      globalTrigger = true;
      unmatchedFiles.push(filePath);
      continue;
    }

    const owner = sortedProjects.find(
      (projectPath) => filePath === projectPath || filePath.startsWith(`${projectPath}/`)
    );

    if (!owner) {
      unmatchedFiles.push(filePath);
      continue;
    }

    fileToProject.set(filePath, owner);
  }

  return { fileToProject, unmatchedFiles, globalTrigger };
}

function transitiveClosure(seeds, reverseGraph) {
  const visited = new Set();
  const queue = [...seeds];

  for (const seed of seeds) {
    visited.add(seed);
  }

  while (queue.length > 0) {
    const current = queue.shift();
    for (const dependent of reverseGraph.get(current) ?? []) {
      if (visited.has(dependent)) {
        continue;
      }
      visited.add(dependent);
      queue.push(dependent);
    }
  }

  return visited;
}

function buildReport({
  args,
  model,
  diffMode,
  changedFiles,
  forward,
  reverse,
  fileToProject,
  unmatchedFiles,
  globalTrigger,
  policyValidationErrors,
  policyValidationWarnings
}) {
  const directProjects = new Set(fileToProject.values());
  const allProjectPaths = [...model.projects.keys()].sort((left, right) => left.localeCompare(right));
  const unmatchedNonDocs = unmatchedFiles.filter((filePath) => !filePath.startsWith("docs/"));

  if (globalTrigger) {
    for (const projectPath of allProjectPaths) {
      directProjects.add(projectPath);
    }
  }

  const affectedProjects = transitiveClosure(directProjects, reverse);
  const transitiveOnly = [...affectedProjects].filter((projectPath) => !directProjects.has(projectPath));
  const unaffectedProjects = allProjectPaths.filter((projectPath) => !affectedProjects.has(projectPath));

  const fileOwnership = changedFiles.map((filePath) => ({
    file: filePath,
    ownerProject: fileToProject.get(filePath) ?? null
  }));

  const edges = [];
  for (const [from, targets] of forward.entries()) {
    for (const to of targets.values()) {
      edges.push({ from, to });
    }
  }
  edges.sort((left, right) => {
    const byFrom = left.from.localeCompare(right.from);
    if (byFrom !== 0) {
      return byFrom;
    }
    return left.to.localeCompare(right.to);
  });

  const projectCatalog = allProjectPaths.map((projectPath) => {
    const project = model.projects.get(projectPath);
    return {
      path: projectPath,
      packageName: project?.packageName ?? projectPath,
      manifestPath: project?.manifestPath ?? null
    };
  });

  return {
    schema_version: 2,
    generated_at_utc: new Date().toISOString(),
    policy_path: toPosix(path.relative(repoRoot, path.resolve(repoRoot, args.policy))),
    workspace_path: toPosix(path.relative(repoRoot, path.resolve(repoRoot, args.workspace))),
    policy_validation: {
      error_count: policyValidationErrors.length,
      warning_count: policyValidationWarnings.length,
      errors: policyValidationErrors,
      warnings: policyValidationWarnings
    },
    workspace_model: {
      roots: model.workspace.roots,
      effective_patterns: model.workspace.effective_patterns,
      pattern_sync: model.workspace.pattern_sync,
      retired_entries_present: model.workspace.retired_entries_present,
      discovery_anomalies: model.workspace.discovery_anomalies
    },
    diff: {
      base: args.base,
      head: args.head,
      mode: diffMode,
      changed_file_count: changedFiles.length
    },
    global_trigger: globalTrigger,
    global_trigger_reason: globalTrigger
      ? {
          unmatched_non_docs_count: unmatchedNonDocs.length
        }
      : null,
    workspace: {
      project_count: allProjectPaths.length,
      projects: projectCatalog,
      dependency_edges: edges
    },
    affected: {
      direct: [...directProjects].sort((left, right) => left.localeCompare(right)),
      transitive_only: transitiveOnly.sort((left, right) => left.localeCompare(right)),
      all: [...affectedProjects].sort((left, right) => left.localeCompare(right)),
      unaffected: unaffectedProjects
    },
    files: {
      ownership: fileOwnership,
      unmatched: unmatchedFiles.sort((left, right) => left.localeCompare(right))
    }
  };
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

  const { forward, reverse } = buildWorkspaceDependencyGraph(model.projects, model.packageNameToProject);
  const { files: changedFiles, mode: diffMode } = collectChangedFiles(
    args.base,
    args.head,
    args.useTripleDot
  );
  const { fileToProject, unmatchedFiles, globalTrigger } = mapChangedFilesToProjects(
    changedFiles,
    model.projects.keys()
  );
  const conservativeGlobal =
    globalTrigger || unmatchedFiles.some((filePath) => !filePath.startsWith("docs/"));

  const report = buildReport({
    args,
    model,
    diffMode,
    changedFiles,
    forward,
    reverse,
    fileToProject,
    unmatchedFiles,
    globalTrigger: conservativeGlobal,
    policyValidationErrors,
    policyValidationWarnings
  });

  const serialized = `${JSON.stringify(report, null, 2)}\n`;
  process.stdout.write(serialized);

  if (args.output) {
    const outputPath = path.resolve(repoRoot, args.output);
    mkdirSync(path.dirname(outputPath), { recursive: true });
    writeFileSync(outputPath, serialized, "utf8");
  }
}

main();
