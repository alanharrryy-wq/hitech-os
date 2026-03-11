import path from "node:path";

export const GOVERNANCE_STAGE_ID_S1 = "S1" as const;
export const GOVERNANCE_SUPPORTED_STAGE_IDS = Object.freeze([GOVERNANCE_STAGE_ID_S1]);
export type GovernanceStageId = (typeof GOVERNANCE_SUPPORTED_STAGE_IDS)[number];

export const GOVERNANCE_STAGE_S1_REQUIREMENT_IDS = Object.freeze([
  "S1_DEF",
  "S1_BLP",
  "S1_INV",
  "S1_GATE",
  "S1_POL",
  "S1_DEBT",
  "S1_IDX",
  "S1_OUT",
  "S1_FAIL",
  "S1_PROM"
] as const);

export type GovernanceStageS1RequirementId = (typeof GOVERNANCE_STAGE_S1_REQUIREMENT_IDS)[number];

export type GovernanceIssueSeverity = "info" | "warn" | "error";

export interface GovernanceIssue {
  code: string;
  message: string;
  severity: GovernanceIssueSeverity;
  target: string;
}

export interface GovernanceStageRequirement {
  id: GovernanceStageS1RequirementId;
  title: string;
  sourcePath: string;
  sourceAnchor: string;
  summary: string;
  obligations: string[];
}

export interface GovernanceStageSnapshot {
  stageId: GovernanceStageId;
  deterministic: true;
  offlineFirst: true;
  featureFlagsDefaultOff: true;
  requirementIds: GovernanceStageS1RequirementId[];
  requirements: GovernanceStageRequirement[];
}

export interface GovernanceRunSummary {
  runId: string;
  runPath: string;
  hasRunManifest: boolean;
  hasLegacyAliasBundles: boolean;
  hasZAggregatorBundle: boolean;
  bundleDirectories: string[];
  legacyAliasBundles: string[];
}

export interface GovernanceRunsListResponse {
  mode: "local";
  deterministic: true;
  runsRoot: string;
  latestRunId: string | null;
  runs: GovernanceRunSummary[];
  warnings: GovernanceIssue[];
}

export type GovernanceArtifactKind = "file" | "directory" | "symlink" | "other" | "unreadable";

export interface GovernanceArtifactManifestEntry {
  relativePath: string;
  absolutePath: string;
  kind: GovernanceArtifactKind;
  sizeBytes: number | null;
  sha256: string | null;
}

export type GovernanceArtifactsManifestStatus =
  | "ok"
  | "missing_run"
  | "invalid_run_id"
  | "read_error";

export interface GovernanceArtifactsManifestResponse {
  mode: "local";
  deterministic: true;
  runId: string;
  runPath: string;
  runExists: boolean;
  status: GovernanceArtifactsManifestStatus;
  artifacts: GovernanceArtifactManifestEntry[];
  warnings: GovernanceIssue[];
}

export const GOVERNANCE_RUN_ID_PATTERN = /^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$/;

export function compareLexicographic(left: string, right: string): number {
  return left.localeCompare(right);
}

export function toPosixPath(value: string): string {
  return value.split(path.sep).join("/");
}

export function normalizeRunId(runId: string): string {
  return runId.trim();
}

export function isSafeRunId(runId: string): boolean {
  return GOVERNANCE_RUN_ID_PATTERN.test(normalizeRunId(runId));
}

export function sortDeterministicRunIds(runIds: readonly string[]): string[] {
  return [...runIds]
    .map((runId) => normalizeRunId(runId))
    .filter((runId) => runId.length > 0)
    .sort(compareLexicographic);
}

export function sortIssuesDeterministically(issues: readonly GovernanceIssue[]): GovernanceIssue[] {
  return [...issues].sort((left, right) => {
    const byCode = compareLexicographic(left.code, right.code);
    if (byCode !== 0) {
      return byCode;
    }

    const byTarget = compareLexicographic(left.target, right.target);
    if (byTarget !== 0) {
      return byTarget;
    }

    const byMessage = compareLexicographic(left.message, right.message);
    if (byMessage !== 0) {
      return byMessage;
    }

    return compareLexicographic(left.severity, right.severity);
  });
}

export function sortArtifactsDeterministically(
  artifacts: readonly GovernanceArtifactManifestEntry[]
): GovernanceArtifactManifestEntry[] {
  return [...artifacts].sort((left, right) => {
    const byPath = compareLexicographic(left.relativePath, right.relativePath);
    if (byPath !== 0) {
      return byPath;
    }

    const byKind = compareLexicographic(left.kind, right.kind);
    if (byKind !== 0) {
      return byKind;
    }

    const leftSize = left.sizeBytes ?? -1;
    const rightSize = right.sizeBytes ?? -1;
    return leftSize - rightSize;
  });
}

export const GOVERNANCE_STAGE_S1_REQUIREMENTS: GovernanceStageRequirement[] = Object.freeze([
  {
    id: "S1_DEF",
    title: "Service Contracts",
    sourcePath: "docs/CONTRACT.md",
    sourceAnchor: "### S1_DEF — Stage Definition",
    summary: "Core and agent services must expose deterministic baseline contracts.",
    obligations: Object.freeze([
      "Core API includes /health, /flags, and /jobs endpoints.",
      "AI agent includes /health and /jobs/run endpoints.",
      "Fallback behavior is deterministic when integrations fail."
    ])
  },
  {
    id: "S1_BLP",
    title: "Blueprint Model",
    sourcePath: "docs/CONTRACT.md",
    sourceAnchor: "### S1_BLP — Blueprint Model (P1 scope)",
    summary: "App behavior remains bound to deterministic feature flags and health views.",
    obligations: Object.freeze([
      "Web app has a home surface and a health dashboard surface.",
      "Feature flag behavior defaults to OFF.",
      "UI consumes package primitives rather than ad-hoc runtime contracts."
    ])
  },
  {
    id: "S1_INV",
    title: "Repo Inventory Model",
    sourcePath: "docs/CONTRACT.md",
    sourceAnchor: "### S1_INV — Repo Inventory Model",
    summary: "Tooling remains local-first and deterministic with explicit failure outputs.",
    obligations: Object.freeze([
      "Health tooling runs with no external dependencies.",
      "Source scans use deterministic sorted reporting.",
      "Tool scripts do not mutate state outside repository boundaries."
    ])
  },
  {
    id: "S1_GATE",
    title: "Functional Gates",
    sourcePath: "docs/CONTRACT.md",
    sourceAnchor: "### S1_GATE — Functional Gates v1",
    summary: "Baseline checks and smoke workflows are deterministic and local.",
    obligations: Object.freeze([
      "Contracts schema checks pass in check mode.",
      "Health gate passes without external services.",
      "Core API smoke flow executes locally."
    ])
  },
  {
    id: "S1_POL",
    title: "Policy Strictness",
    sourcePath: "docs/CONTRACT.md",
    sourceAnchor: "### S1_POL — Policy Strictness (P1)",
    summary: "Formatting/lint/test policy remains explicit and reproducible.",
    obligations: Object.freeze([
      "Node lint and formatting rules are tracked in-repo.",
      "Python style rules are explicit in pyproject when present.",
      "Script conventions remain stable and predictable."
    ])
  },
  {
    id: "S1_DEBT",
    title: "Debt System",
    sourcePath: "docs/CONTRACT.md",
    sourceAnchor: "### S1_DEBT — Debt System v0",
    summary: "Security defaults remain safe and secrets stay out of repo history.",
    obligations: Object.freeze([
      "No secrets are committed.",
      "Service defaults remain safe for local development.",
      "No telemetry is enabled by default."
    ])
  },
  {
    id: "S1_IDX",
    title: "Index Scope",
    sourcePath: "docs/CONTRACT.md",
    sourceAnchor: "### S1_IDX — INDEX_PRO Scope v0",
    summary: "Dependencies remain minimal and predictable for deterministic builds.",
    obligations: Object.freeze([
      "Dependency list is intentionally small.",
      "Major/minor versions are pinned where practical.",
      "Heavy dependencies are avoided in shared packages."
    ])
  },
  {
    id: "S1_OUT",
    title: "Output Minimum Contract",
    sourcePath: "docs/CONTRACT.md",
    sourceAnchor: "### S1_OUT — Output Minimum Contract",
    summary: "Version and compatibility changes require explicit migration planning.",
    obligations: Object.freeze([
      "Breaking changes require migration notes.",
      "Enum removals require compatibility planning.",
      "Field renames should use compatibility windows."
    ])
  },
  {
    id: "S1_FAIL",
    title: "Failure Modes",
    sourcePath: "docs/CONTRACT.md",
    sourceAnchor: "### S1_FAIL — Failure Modes (P1 only)",
    summary: "PR gates require deterministic evidence for quality and policy adherence.",
    obligations: Object.freeze([
      "No prohibited source artifacts.",
      "Feature flags remain OFF by default unless approved.",
      "Contract-affecting changes include schema updates."
    ])
  },
  {
    id: "S1_PROM",
    title: "Promotion Rules",
    sourcePath: "docs/CONTRACT.md",
    sourceAnchor: "### S1_PROM — Promotion Rules (P1)",
    summary: "Incident flow is explicit and deterministic with documented repair steps.",
    obligations: Object.freeze([
      "Health failures are remediated immediately and rerun.",
      "Schema drift is resolved through canonical regeneration flow.",
      "Recurring issues are documented in NOTEBOOK with owner/date."
    ])
  }
]);

export function createGovernanceStageSnapshot(stageId: string): GovernanceStageSnapshot | null {
  if (normalizeRunId(stageId) !== GOVERNANCE_STAGE_ID_S1) {
    return null;
  }

  return {
    stageId: GOVERNANCE_STAGE_ID_S1,
    deterministic: true,
    offlineFirst: true,
    featureFlagsDefaultOff: true,
    requirementIds: [...GOVERNANCE_STAGE_S1_REQUIREMENT_IDS],
    requirements: GOVERNANCE_STAGE_S1_REQUIREMENTS.map((requirement) => ({
      ...requirement,
      obligations: [...requirement.obligations]
    }))
  };
}

export function createInvalidRunIdArtifactsResponse(input: {
  runId: string;
  runsRoot: string;
  reason?: string;
}): GovernanceArtifactsManifestResponse {
  const normalized = normalizeRunId(input.runId);
  return {
    mode: "local",
    deterministic: true,
    runId: normalized,
    runPath: toPosixPath(path.join(input.runsRoot, normalized)),
    runExists: false,
    status: "invalid_run_id",
    artifacts: [],
    warnings: sortIssuesDeterministically([
      {
        code: "INVALID_RUN_ID",
        message: input.reason ?? "runId is invalid for deterministic local reads",
        severity: "error",
        target: normalized
      }
    ])
  };
}
