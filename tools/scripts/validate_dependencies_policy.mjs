#!/usr/bin/env node
import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import { loadDependencyPolicyModel, resolveRepoRoot, toPosix } from "./lib/dependency_policy.mjs";

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

    if (token === "--strict") {
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

  const errors = [...model.validation.errors];
  const warnings = [...model.validation.warnings];

  if (
    model.workspace.pattern_sync.only_in_policy.length > 0 ||
    model.workspace.pattern_sync.only_in_pnpm_workspace.length > 0
  ) {
    errors.push("workspace pattern drift between dependencies policy and pnpm-workspace.yaml");
  }

  if (model.workspace.roots.length === 0) {
    errors.push("no workspace roots resolved from dependency policy");
  }

  const report = {
    schema_version: 1,
    generated_at_utc: new Date().toISOString(),
    strict_mode: args.strict,
    policy_path: toPosix(path.relative(repoRoot, path.resolve(repoRoot, args.policy))),
    workspace_path: toPosix(path.relative(repoRoot, path.resolve(repoRoot, args.workspace))),
    workspace: {
      roots: model.workspace.roots,
      effective_patterns: model.workspace.effective_patterns,
      policy_patterns: model.workspace.policy_patterns,
      pnpm_workspace_patterns: model.workspace.pnpm_workspace_patterns,
      pattern_sync: model.workspace.pattern_sync,
      retired_entries: model.workspace.retired_entries,
      retired_entries_present: model.workspace.retired_entries_present,
      discovery_anomalies: model.workspace.discovery_anomalies,
      project_count: model.projects.size
    },
    validation: {
      error_count: errors.length,
      warning_count: warnings.length,
      errors,
      warnings
    },
    status: errors.length > 0 ? "fail" : warnings.length > 0 ? "warn" : "pass"
  };

  const serialized = `${JSON.stringify(report, null, 2)}\n`;
  process.stdout.write(serialized);

  if (args.output) {
    const outputPath = path.resolve(repoRoot, args.output);
    mkdirSync(path.dirname(outputPath), { recursive: true });
    writeFileSync(outputPath, serialized, "utf8");
  }

  if (errors.length > 0 || (args.strict && warnings.length > 0)) {
    process.stderr.write("[dependencies-policy] FAILED\n");
    process.exit(1);
  }
}

main();
