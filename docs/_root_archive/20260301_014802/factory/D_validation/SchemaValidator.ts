import {
  BundleCheckResult,
  BundleFileChange,
  IntegratorBundle,
  WorkerBundle,
  assertBundleFileChange,
  assertBundleStatus,
  assertIntegratorBundle,
  assertWorkerBundle,
  normalizeBundleChanges,
} from "../contracts/BundleSchema";
import {
  DeterministicExecutionReport,
  assertExecutionReport,
} from "../contracts/ExecutionReport";
import { JsonObject } from "../shared/DeterministicJson";
import { compareRepoPaths } from "../shared/Pathing";

export type ValidationSeverity = "error" | "warning";

export interface ValidationIssue {
  readonly code: string;
  readonly path: string;
  readonly message: string;
  readonly severity: ValidationSeverity;
}

export interface ValidationResult {
  readonly valid: boolean;
  readonly issues: readonly ValidationIssue[];
  readonly summary: JsonObject;
}

function compareIssues(left: ValidationIssue, right: ValidationIssue): number {
  const byPath = left.path.localeCompare(right.path);
  if (byPath !== 0) {
    return byPath;
  }
  const byCode = left.code.localeCompare(right.code);
  if (byCode !== 0) {
    return byCode;
  }
  return left.message.localeCompare(right.message);
}

function buildResult(issues: readonly ValidationIssue[]): ValidationResult {
  const sortedIssues = [...issues].sort(compareIssues);
  const errorCount = sortedIssues.filter((issue) => issue.severity === "error").length;
  const warningCount = sortedIssues.length - errorCount;
  return {
    valid: errorCount === 0,
    issues: sortedIssues,
    summary: {
      issueCount: sortedIssues.length,
      errorCount,
      warningCount,
    },
  };
}

function pushIssue(
  issues: ValidationIssue[],
  issue: Omit<ValidationIssue, "severity"> & { readonly severity?: ValidationSeverity },
): void {
  issues.push({
    ...issue,
    severity: issue.severity ?? "error",
  });
}

function validateSortedChanges(
  changes: readonly BundleFileChange[],
  pathLabel: string,
  issues: ValidationIssue[],
): void {
  const normalized = normalizeBundleChanges(changes);
  const actualPaths = changes.map((change) => change.path);
  const expectedPaths = normalized.map((change) => change.path);
  for (const [index, actualPath] of actualPaths.entries()) {
    const expectedPath = expectedPaths[index];
    if (expectedPath === undefined) {
      continue;
    }
    if (compareRepoPaths(actualPath, expectedPath) !== 0) {
      pushIssue(issues, {
        code: "NON_DETERMINISTIC_CHANGE_ORDER",
        path: `${pathLabel}[${index}]`,
        message: `Expected ${expectedPath} but received ${actualPath}.`,
      });
    }
  }
}

function validateCheckNames(
  checks: readonly BundleCheckResult[],
  pathLabel: string,
  issues: ValidationIssue[],
): void {
  const names = checks.map((check) => check.name);
  const sorted = [...names].sort((left, right) => left.localeCompare(right));
  for (const [index, name] of names.entries()) {
    const expected = sorted[index];
    if (expected === undefined) {
      continue;
    }
    if (name !== expected) {
      pushIssue(issues, {
        code: "NON_DETERMINISTIC_CHECK_ORDER",
        path: `${pathLabel}[${index}]`,
        message: `Expected ${expected} but found ${name}.`,
      });
    }
  }
}

export class SchemaValidator {
  validateWorkerBundle(bundle: WorkerBundle): ValidationResult {
    const issues: ValidationIssue[] = [];
    try {
      assertWorkerBundle(bundle, "workerBundle");
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Unknown bundle schema error.";
      pushIssue(issues, {
        code: "WORKER_BUNDLE_SCHEMA",
        path: "workerBundle",
        message,
      });
      return buildResult(issues);
    }

    validateSortedChanges(bundle.changes, "workerBundle.changes", issues);
    validateCheckNames(bundle.checks, "workerBundle.checks", issues);
    return buildResult(issues);
  }

  validateIntegratorBundle(bundle: IntegratorBundle): ValidationResult {
    const issues: ValidationIssue[] = [];
    try {
      assertIntegratorBundle(bundle, "integratorBundle");
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Unknown integrator schema error.";
      pushIssue(issues, {
        code: "INTEGRATOR_BUNDLE_SCHEMA",
        path: "integratorBundle",
        message,
      });
      return buildResult(issues);
    }

    validateSortedChanges(bundle.changes, "integratorBundle.changes", issues);
    validateCheckNames(bundle.checks, "integratorBundle.checks", issues);
    return buildResult(issues);
  }

  validateExecutionReport(report: DeterministicExecutionReport): ValidationResult {
    const issues: ValidationIssue[] = [];
    try {
      assertExecutionReport(report, "executionReport");
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Unknown execution report schema error.";
      pushIssue(issues, {
        code: "EXECUTION_REPORT_SCHEMA",
        path: "executionReport",
        message,
      });
      return buildResult(issues);
    }

    for (const [index, record] of report.records.entries()) {
      assertBundleStatus(record.status, `executionReport.records[${index}].status`);
      if (record.changedPaths.length === 0) {
        pushIssue(issues, {
          code: "EMPTY_CHANGED_PATHS",
          path: `executionReport.records[${index}].changedPaths`,
          message: "Each record must include deterministic changed paths.",
        });
      }
      const sortedPaths = [...record.changedPaths].sort((left, right) => compareRepoPaths(left, right));
      for (const [pathIndex, pathValue] of record.changedPaths.entries()) {
        const expectedPath = sortedPaths[pathIndex];
        if (expectedPath !== undefined && compareRepoPaths(pathValue, expectedPath) !== 0) {
          pushIssue(issues, {
            code: "NON_DETERMINISTIC_REPORT_PATH_ORDER",
            path: `executionReport.records[${index}].changedPaths[${pathIndex}]`,
            message: `Expected ${expectedPath} but found ${pathValue}.`,
          });
        }
      }
    }

    return buildResult(issues);
  }

  validateChangeList(changes: readonly BundleFileChange[]): ValidationResult {
    const issues: ValidationIssue[] = [];
    for (const [index, change] of changes.entries()) {
      try {
        assertBundleFileChange(change, `changes[${index}]`);
      } catch (error: unknown) {
        const message = error instanceof Error ? error.message : "Unknown change schema error.";
        pushIssue(issues, {
          code: "CHANGE_SCHEMA",
          path: `changes[${index}]`,
          message,
        });
      }
    }
    validateSortedChanges(changes, "changes", issues);
    return buildResult(issues);
  }
}
