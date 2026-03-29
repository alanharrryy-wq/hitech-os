#!/usr/bin/env node
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "../..");

const DEFAULT_INPUTS = {
  affected: "tools/_local/reports/ci/affected_projects.json",
  codeowners: "tools/_local/reports/ci/codeowners_coverage.json",
  dependencyPolicy: "tools/_local/reports/ci/dependencies_policy_validation.json",
  cycles: "tools/_local/reports/ci/dependency_cycles.json",
  release: "tools/_local/reports/ci/release_discipline.json",
  sensitive: "tools/_local/reports/ci/sensitive_paths.json",
  hygiene: "tools/_local/reports/ci/repo_hygiene.json",
  graph: "tools/graphviz/graphs/scope_summary.json",
  graphTopRisk: "tools/graphviz/graphs/scope_top_risks.json"
};

function parseArgs(argv) {
  const args = {
    output: "tools/_local/reports/ci/engineering_health.json"
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    const next = argv[index + 1];

    if (token === "--output" && next) {
      args.output = next;
      index += 1;
    }
  }

  return args;
}

function readJsonIfExists(relativePath) {
  const absolutePath = path.resolve(repoRoot, relativePath);
  if (!existsSync(absolutePath)) {
    return null;
  }

  try {
    return JSON.parse(readFileSync(absolutePath, "utf8"));
  } catch {
    return null;
  }
}

function numericEnv(name) {
  const value = process.env[name];
  if (!value) {
    return null;
  }

  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function boolEnv(name) {
  const value = process.env[name];
  if (value === "true") {
    return true;
  }
  if (value === "false") {
    return false;
  }
  return null;
}

function main() {
  const args = parseArgs(process.argv.slice(2));

  const affected = readJsonIfExists(DEFAULT_INPUTS.affected);
  const codeowners = readJsonIfExists(DEFAULT_INPUTS.codeowners);
  const dependencyPolicy = readJsonIfExists(DEFAULT_INPUTS.dependencyPolicy);
  const cycles = readJsonIfExists(DEFAULT_INPUTS.cycles);
  const release = readJsonIfExists(DEFAULT_INPUTS.release);
  const sensitive = readJsonIfExists(DEFAULT_INPUTS.sensitive);
  const hygiene = readJsonIfExists(DEFAULT_INPUTS.hygiene);
  const graph = readJsonIfExists(DEFAULT_INPUTS.graph);
  const graphTopRisk = readJsonIfExists(DEFAULT_INPUTS.graphTopRisk);

  const checkoutSeconds = numericEnv("CI_METRIC_CHECKOUT_SECONDS");
  const installSeconds = numericEnv("CI_METRIC_INSTALL_SECONDS");
  const guardrailSeconds = numericEnv("CI_METRIC_GUARDRAILS_SECONDS");
  const buildSeconds = numericEnv("CI_METRIC_BUILD_SECONDS");
  const testSeconds = numericEnv("CI_METRIC_TEST_SECONDS");
  const publishSeconds = numericEnv("CI_METRIC_PUBLISH_SECONDS");
  const artifactSeconds = numericEnv("CI_METRIC_ARTIFACT_SECONDS");
  const totalSeconds = numericEnv("CI_METRIC_TOTAL_SECONDS");
  const turboCacheHit = boolEnv("CI_METRIC_TURBO_CACHE_HIT");
  const pnpmCacheHit = boolEnv("CI_METRIC_PNPM_CACHE_HIT");

  const metrics = {
    pipeline_seconds: {
      checkout: checkoutSeconds,
      install: installSeconds,
      guardrails: guardrailSeconds,
      build: buildSeconds,
      test: testSeconds,
      publish: publishSeconds,
      artifact_upload: artifactSeconds,
      total: totalSeconds
    },
    pipeline_duration_targets_seconds: {
      p50_target: 900,
      p95_target: 1800
    },
    cache: {
      dependency_cache_hit_rate: pnpmCacheHit === null ? null : pnpmCacheHit ? 1 : 0,
      build_cache_hit_rate: turboCacheHit === null ? null : turboCacheHit ? 1 : 0,
      pnpm_cache_hit: pnpmCacheHit,
      turbo_cache_hit: turboCacheHit,
      notes:
        "single-run cache metrics are sampled as hit/miss booleans; stable hit-rate requires historical aggregation"
    },
    flakiness: {
      indicator: null,
      notes: "requires historical CI run telemetry"
    },
    affected_project_count: affected?.affected?.all?.length ?? null,
    affected_global_trigger: affected?.global_trigger ?? null,
    dependency_cycle_count: cycles?.cycles?.total ?? null,
    new_dependency_cycle_count: cycles?.cycles?.new_cycle_count ?? null,
    boundary_policy_violation_count: cycles?.boundary_policy?.violation_count ?? null,
    dependency_policy_error_count: dependencyPolicy?.validation?.error_count ?? null,
    codeowners_single_owner_mode: codeowners?.single_owner_mode ?? null,
    codeowners_owner_count: codeowners?.owner_count ?? null,
    release_violation_count: release?.violations?.length ?? null,
    release_status: release?.status ?? null,
    sensitive_paths_changed_count: sensitive?.sensitive_paths?.changed_count ?? null,
    sensitive_unowned_count: sensitive?.sensitive_paths?.unowned_count ?? null,
    secret_finding_count: sensitive?.secret_scan?.finding_count ?? null,
    graph_focus_clean_folder_count: graph?.counts?.focus_clean_active_folders ?? null,
    graph_noise_folder_count: graph?.counts?.noise_active_folders ?? null,
    graph_priority_hotspot_count: graph?.risk_overview?.top_hotspot_count ?? null,
    graph_top_risk_score: graphTopRisk?.top_risks?.[0]?.risk_score ?? null,
    repo_large_file_count: hygiene?.counts?.large_file_count ?? null,
    repo_lfs_candidate_count: hygiene?.counts?.lfs_candidate_count ?? null
  };

  const requiredForBaseline = [
    "pipeline_seconds.checkout",
    "pipeline_seconds.install",
    "pipeline_seconds.guardrails",
    "pipeline_seconds.total",
    "pipeline_seconds.artifact_upload",
    "affected_project_count",
    "dependency_cycle_count",
    "codeowners_owner_count",
    "release_violation_count",
    "secret_finding_count",
    "graph_focus_clean_folder_count",
    "graph_noise_folder_count",
    "repo_large_file_count"
  ];

  const missingMetrics = requiredForBaseline.filter((key) => {
    const segments = key.split(".");
    let cursor = metrics;
    for (const segment of segments) {
      if (!cursor || typeof cursor !== "object" || !(segment in cursor)) {
        return true;
      }
      cursor = cursor[segment];
    }
    return cursor === null || cursor === undefined;
  });

  const report = {
    schema_version: 2,
    generated_at_utc: new Date().toISOString(),
    context: {
      repository: path.basename(repoRoot),
      event_name: process.env.GITHUB_EVENT_NAME ?? null,
      ref: process.env.GITHUB_REF ?? null,
      sha: process.env.GITHUB_SHA ?? null,
      run_id: process.env.GITHUB_RUN_ID ?? null,
      run_attempt: process.env.GITHUB_RUN_ATTEMPT ?? null
    },
    metrics,
    contract: {
      required_metric_keys: requiredForBaseline,
      missing_required_metric_keys: missingMetrics,
      completeness_ratio:
        requiredForBaseline.length === 0
          ? 1
          : Number(
              ((requiredForBaseline.length - missingMetrics.length) / requiredForBaseline.length).toFixed(3)
            ),
      notes:
        missingMetrics.length === 0
          ? "baseline contract complete for this run"
          : "some baseline metrics are unavailable for this run context"
    },
    source_reports: DEFAULT_INPUTS
  };

  const serialized = `${JSON.stringify(report, null, 2)}\n`;
  process.stdout.write(serialized);

  const outputPath = path.resolve(repoRoot, args.output);
  mkdirSync(path.dirname(outputPath), { recursive: true });
  writeFileSync(outputPath, serialized, "utf8");
}

main();
