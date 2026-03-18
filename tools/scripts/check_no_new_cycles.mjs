#!/usr/bin/env node
import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import process from "node:process";
import {
  buildWorkspaceDependencyGraph,
  canonicalCycle,
  collectCycles,
  loadDependencyPolicyModel,
  resolveRepoRoot,
  rootOfProjectPath,
  summarizeHubs,
  toPosix
} from "./lib/dependency_policy.mjs";

const repoRoot = resolveRepoRoot(import.meta.url);

function parseArgs(argv) {
  const args = {
    policy: "policies/dependencies.json",
    workspace: "pnpm-workspace.yaml",
    output: null,
    strict: false
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

    if (token === "--strict" || token === "--fail-on-new-cycles") {
      args.strict = true;
    }
  }

  return args;
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

  const policy = model.policy;
  const boundaryModel = policy.boundary_model ?? {};
  const noNewCycles = policy.no_new_cycles !== false;

  const allowedCycles = Array.isArray(policy.allowed_workspace_cycles)
    ? policy.allowed_workspace_cycles.map((entry) =>
        Array.isArray(entry) ? canonicalCycle(entry) : String(entry)
      )
    : [];
  const allowedCycleSet = new Set(allowedCycles);

  const { forward, reverse } = buildWorkspaceDependencyGraph(model.projects, model.packageNameToProject);
  const cycles = collectCycles(forward);
  const cycleIds = cycles.map((nodes) => canonicalCycle(nodes));
  const newCycles = cycleIds.filter((cycleId) => !allowedCycleSet.has(cycleId));

  const dependencyEdges = [];
  const crossBoundaryEdges = [];
  const boundaryViolations = [];
  for (const [from, targets] of forward.entries()) {
    for (const to of targets) {
      dependencyEdges.push({ from, to });
      const fromRoot = rootOfProjectPath(from);
      const toRoot = rootOfProjectPath(to);
      const allowedTargets = Array.isArray(boundaryModel[fromRoot]) ? boundaryModel[fromRoot] : [];
      if (fromRoot !== toRoot) {
        crossBoundaryEdges.push({ from, to, from_root: fromRoot, to_root: toRoot });
      }
      if (allowedTargets.length > 0 && !allowedTargets.includes(toRoot)) {
        boundaryViolations.push({
          from,
          to,
          from_root: fromRoot,
          to_root: toRoot,
          allowed_roots: allowedTargets
        });
      }
    }
  }

  dependencyEdges.sort((left, right) => {
    const byFrom = left.from.localeCompare(right.from);
    if (byFrom !== 0) {
      return byFrom;
    }
    return left.to.localeCompare(right.to);
  });

  crossBoundaryEdges.sort((left, right) => {
    const byFrom = left.from.localeCompare(right.from);
    if (byFrom !== 0) {
      return byFrom;
    }
    return left.to.localeCompare(right.to);
  });

  boundaryViolations.sort((left, right) => {
    const byFrom = left.from.localeCompare(right.from);
    if (byFrom !== 0) {
      return byFrom;
    }
    return left.to.localeCompare(right.to);
  });

  const { fanInHubs, fanOutHubs } = summarizeHubs(forward, reverse);

  const strictShouldFail =
    args.strict &&
    (policyValidationErrors.length > 0 ||
      (noNewCycles && newCycles.length > 0));

  const report = {
    schema_version: 2,
    generated_at_utc: new Date().toISOString(),
    policy_path: toPosix(path.relative(repoRoot, path.resolve(repoRoot, args.policy))),
    workspace_path: toPosix(path.relative(repoRoot, path.resolve(repoRoot, args.workspace))),
    strict_mode: args.strict,
    workspace_model: {
      roots: model.workspace.roots,
      effective_patterns: model.workspace.effective_patterns,
      policy_patterns: model.workspace.policy_patterns,
      pnpm_workspace_patterns: model.workspace.pnpm_workspace_patterns,
      pattern_sync: model.workspace.pattern_sync,
      retired_entries: model.workspace.retired_entries,
      retired_entries_present: model.workspace.retired_entries_present,
      discovery_anomalies: model.workspace.discovery_anomalies
    },
    policy_validation: {
      error_count: policyValidationErrors.length,
      warning_count: policyValidationWarnings.length,
      errors: policyValidationErrors,
      warnings: policyValidationWarnings
    },
    workspace: {
      project_count: model.projects.size,
      edge_count: dependencyEdges.length
    },
    cycles: {
      enforcement_enabled: noNewCycles,
      total: cycles.length,
      allowed: allowedCycles.length,
      new_cycle_count: newCycles.length,
      cycle_ids: cycleIds,
      new_cycle_ids: newCycles,
      no_new_cycles_pass: newCycles.length === 0
    },
    hubs: {
      fan_in: fanInHubs,
      fan_out: fanOutHubs
    },
    cross_boundary_edges: {
      count: crossBoundaryEdges.length,
      sample: crossBoundaryEdges.slice(0, 200)
    },
    boundary_policy: {
      violation_count: boundaryViolations.length,
      violations_sample: boundaryViolations.slice(0, 200)
    },
    status:
      policyValidationErrors.length > 0
        ? "fail"
        : noNewCycles && newCycles.length > 0
          ? args.strict
            ? "fail"
            : "warn"
          : "pass"
  };

  const serialized = `${JSON.stringify(report, null, 2)}\n`;
  process.stdout.write(serialized);

  if (args.output) {
    const outputPath = path.resolve(repoRoot, args.output);
    mkdirSync(path.dirname(outputPath), { recursive: true });
    writeFileSync(outputPath, serialized, "utf8");
  }

  if (strictShouldFail) {
    process.stderr.write("[cycles] FAILED: dependency policy invalid or new workspace cycles detected\n");
    process.exit(1);
  }
}

main();
