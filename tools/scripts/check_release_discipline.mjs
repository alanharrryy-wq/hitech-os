#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import process from "node:process";
import { loadDependencyPolicyModel, resolveRepoRoot, toPosix } from "./lib/dependency_policy.mjs";

const repoRoot = resolveRepoRoot(import.meta.url);

function parseArgs(argv) {
  const args = {
    base: process.env.AFFECTED_BASE ?? null,
    head: process.env.AFFECTED_HEAD ?? "HEAD",
    policy: "policies/release.json",
    dependenciesPolicy: "policies/dependencies.json",
    workspace: "pnpm-workspace.yaml",
    output: null,
    strict: false,
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

    if (token === "--dependencies-policy" && next) {
      args.dependenciesPolicy = next;
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

function readJson(relativePath) {
  return JSON.parse(readFileSync(path.resolve(repoRoot, relativePath), "utf8"));
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
        mode: "triple-dot",
        files: runGitDiff(base, head, true)
      };
    } catch {
      return {
        mode: "two-dot-fallback",
        files: runGitDiff(base, head, false)
      };
    }
  }

  return {
    mode: "two-dot",
    files: runGitDiff(base, head, false)
  };
}

function pathMatchesRule(filePath, rule) {
  if (rule.endsWith("/")) {
    return filePath.startsWith(rule);
  }
  return filePath === rule;
}

function readJsonFromGitRef(ref, relativePath) {
  try {
    const output = execFileSync("git", ["show", `${ref}:${relativePath}`], {
      cwd: repoRoot,
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"]
    });
    return JSON.parse(output);
  } catch {
    return null;
  }
}

function validateReleasePolicy(policy) {
  const errors = [];
  const warnings = [];

  if (!policy || typeof policy !== "object") {
    return {
      errors: ["policy is missing or not a JSON object"],
      warnings
    };
  }

  if (policy.policy_id !== "release") {
    errors.push("policy_id must equal 'release'");
  }

  if (!Array.isArray(policy.release_critical_paths) || policy.release_critical_paths.length === 0) {
    errors.push("release_critical_paths must be a non-empty array");
  }

  if (!Array.isArray(policy.change_note_paths) || policy.change_note_paths.length === 0) {
    errors.push("change_note_paths must be a non-empty array");
  }
  if (
    Object.prototype.hasOwnProperty.call(policy, "release_evidence_paths") &&
    !Array.isArray(policy.release_evidence_paths)
  ) {
    errors.push("release_evidence_paths must be an array when present");
  }

  if (
    Object.prototype.hasOwnProperty.call(policy, "blocking_checks") &&
    !Array.isArray(policy.blocking_checks)
  ) {
    errors.push("blocking_checks must be an array when present");
  }

  if (
    policy.versioning_mode === "lockstep" &&
    !["full-workspace", "grouped-provisional"].includes(String(policy.lockstep_scope ?? ""))
  ) {
    warnings.push("lockstep_scope should be set to 'full-workspace' or 'grouped-provisional'");
  }

  return { errors, warnings };
}

function collectManifestChangeDetails(base, head, manifestPaths) {
  const details = [];
  for (const manifestPath of manifestPaths) {
    const before = readJsonFromGitRef(base, manifestPath);
    const after = readJsonFromGitRef(head, manifestPath);
    const beforeVersion = before && typeof before.version === "string" ? before.version : null;
    const afterVersion = after && typeof after.version === "string" ? after.version : null;
    const beforePrivate = before && typeof before.private === "boolean" ? before.private : null;
    const afterPrivate = after && typeof after.private === "boolean" ? after.private : null;

    details.push({
      file: manifestPath,
      package_name_before: before && typeof before.name === "string" ? before.name : null,
      package_name_after: after && typeof after.name === "string" ? after.name : null,
      version_before: beforeVersion,
      version_after: afterVersion,
      version_changed: beforeVersion !== afterVersion,
      private_before: beforePrivate,
      private_after: afterPrivate,
      private_changed: beforePrivate !== afterPrivate
    });
  }

  return details;
}

function distinctVersions(manifestDetails) {
  return [...new Set(manifestDetails.map((entry) => entry.version_after).filter(Boolean))].sort((a, b) =>
    a.localeCompare(b)
  );
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const policy = readJson(args.policy);
  const policyValidation = validateReleasePolicy(policy);
  const depsModel = loadDependencyPolicyModel({
    repoRoot,
    policyPath: args.dependenciesPolicy,
    workspacePath: args.workspace
  });

  const depsPolicyErrors = [...depsModel.validation.errors];
  if (
    depsModel.workspace.pattern_sync.only_in_policy.length > 0 ||
    depsModel.workspace.pattern_sync.only_in_pnpm_workspace.length > 0
  ) {
    depsPolicyErrors.push("workspace pattern drift between dependencies policy and pnpm-workspace.yaml");
  }

  const releaseCriticalPaths = Array.isArray(policy.release_critical_paths)
    ? policy.release_critical_paths
    : [];
  const publicApiPaths = Array.isArray(policy.public_api_paths) ? policy.public_api_paths : [];
  const changeNotePaths = Array.isArray(policy.change_note_paths) ? policy.change_note_paths : [];
  const releaseEvidencePaths = Array.isArray(policy.release_evidence_paths)
    ? policy.release_evidence_paths
    : changeNotePaths;
  const requireChangeNoteForReleaseCritical =
    policy.require_change_note_for_release_critical !== false;
  const requireChangeNoteForPublicApi = policy.require_change_note_for_public_api === true;
  const requireChangeNoteForManifestChanges = policy.require_change_note_for_manifest_changes === true;
  const requireReleaseIntentForVersionChange =
    policy.require_release_intent_for_version_change === true;
  const blockingChecks = new Set(
    Array.isArray(policy.blocking_checks) ? policy.blocking_checks.map((value) => String(value)) : []
  );

  const { mode, files: changedFiles } = collectChangedFiles(args.base, args.head, args.useTripleDot);

  const releaseCriticalChanges = changedFiles.filter((filePath) =>
    releaseCriticalPaths.some((rule) => pathMatchesRule(filePath, rule))
  );
  const publicApiChanges = changedFiles.filter((filePath) =>
    publicApiPaths.some((rule) => pathMatchesRule(filePath, rule))
  );
  const changeNoteChanges = changedFiles.filter((filePath) =>
    changeNotePaths.some((rule) => pathMatchesRule(filePath, rule))
  );
  const releaseEvidenceChanges = changedFiles.filter((filePath) =>
    releaseEvidencePaths.some((rule) => pathMatchesRule(filePath, rule))
  );

  const workspaceRoots = new Set(depsModel.workspace.roots);
  const packageManifestChanges = changedFiles
    .filter((filePath) => filePath.endsWith("/package.json"))
    .filter((filePath) => workspaceRoots.has(filePath.split("/", 1)[0] ?? ""));
  const manifestDetails = collectManifestChangeDetails(args.base, args.head, packageManifestChanges);
  const versionChangedManifests = manifestDetails.filter((entry) => entry.version_changed);
  const releaseEvidencePresent = releaseEvidenceChanges.length > 0;

  const violations = [];
  if (requireChangeNoteForReleaseCritical && releaseCriticalChanges.length > 0 && !releaseEvidencePresent) {
    violations.push({
      id: "missing_change_note_release_critical",
      severity: "error",
      message: "Release-critical paths changed without release evidence (CHANGELOG/docs/releases)"
    });
  }

  if (requireChangeNoteForPublicApi && publicApiChanges.length > 0 && !releaseEvidencePresent) {
    violations.push({
      id: "missing_change_note_public_api",
      severity: "error",
      message: "Public API paths changed without release evidence"
    });
  }

  if (requireChangeNoteForManifestChanges && manifestDetails.length > 0 && !releaseEvidencePresent) {
    violations.push({
      id: "missing_change_note_manifest_changes",
      severity: "warn",
      message: "Workspace package manifests changed without release evidence"
    });
  }

  if (requireReleaseIntentForVersionChange && versionChangedManifests.length > 0 && !releaseEvidencePresent) {
    violations.push({
      id: "version_change_without_release_intent",
      severity: "warn",
      message: "Workspace package versions changed without release evidence"
    });
  }

  const distinctWorkspaceVersions = distinctVersions(manifestDetails);
  if (
    policy.versioning_mode === "lockstep" &&
    policy.lockstep_scope === "full-workspace" &&
    distinctWorkspaceVersions.length > 1
  ) {
    violations.push({
      id: "lockstep_version_drift",
      severity: "error",
      message: "Lockstep full-workspace mode expects a single workspace version value"
    });
  }

  const strictShouldFail =
    args.strict &&
    (policyValidation.errors.length > 0 ||
      depsPolicyErrors.length > 0 ||
      violations.some((violation) => blockingChecks.has(violation.id)));

  const reportOnlyDefault = policy.report_only_default !== false;
  const report = {
    schema_version: 2,
    generated_at_utc: new Date().toISOString(),
    policy_path: toPosix(path.relative(repoRoot, path.resolve(repoRoot, args.policy))),
    dependencies_policy_path: toPosix(
      path.relative(repoRoot, path.resolve(repoRoot, args.dependenciesPolicy))
    ),
    strict_mode: args.strict,
    report_only_default: reportOnlyDefault,
    diff: {
      base: args.base,
      head: args.head,
      mode,
      changed_file_count: changedFiles.length
    },
    release_policy_validation: {
      error_count: policyValidation.errors.length,
      warning_count: policyValidation.warnings.length,
      errors: policyValidation.errors,
      warnings: policyValidation.warnings
    },
    dependencies_policy_validation: {
      error_count: depsPolicyErrors.length,
      errors: depsPolicyErrors
    },
    versioning: {
      mode: String(policy.versioning_mode ?? "insufficient_evidence"),
      lockstep_scope: String(policy.lockstep_scope ?? "insufficient_evidence"),
      distinct_workspace_versions: distinctWorkspaceVersions,
      manifest_changes_considered: manifestDetails.length
    },
    changes: {
      release_critical: releaseCriticalChanges,
      public_api: publicApiChanges,
      change_notes: changeNoteChanges,
      release_evidence: releaseEvidenceChanges,
      package_manifests: packageManifestChanges
    },
    manifest_change_details: manifestDetails,
    checks: {
      require_change_note_for_release_critical: requireChangeNoteForReleaseCritical,
      require_change_note_for_public_api: requireChangeNoteForPublicApi,
      require_change_note_for_manifest_changes: requireChangeNoteForManifestChanges,
      require_release_intent_for_version_change: requireReleaseIntentForVersionChange,
      release_evidence_present: releaseEvidencePresent
    },
    blocking_checks: [...blockingChecks].sort((left, right) => left.localeCompare(right)),
    violations,
    status:
      policyValidation.errors.length > 0 || depsPolicyErrors.length > 0
        ? "fail"
        : violations.length === 0
          ? "pass"
          : strictShouldFail
            ? "fail"
            : "warn",
    insufficient_evidence: []
  };

  const serialized = `${JSON.stringify(report, null, 2)}\n`;
  process.stdout.write(serialized);

  if (args.output) {
    const outputPath = path.resolve(repoRoot, args.output);
    mkdirSync(path.dirname(outputPath), { recursive: true });
    writeFileSync(outputPath, serialized, "utf8");
  }

  if (strictShouldFail) {
    process.stderr.write("[release-discipline] FAILED\n");
    process.exit(1);
  }
}

main();
