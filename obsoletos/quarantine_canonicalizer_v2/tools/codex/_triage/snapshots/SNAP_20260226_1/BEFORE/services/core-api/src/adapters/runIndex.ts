import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import type { Dirent } from "node:fs";
import {
  type GovernanceIssue,
  type GovernanceRunSummary,
  type GovernanceRunsListResponse,
  isSafeRunId,
  normalizeRunId,
  sortDeterministicRunIds,
  sortIssuesDeterministically,
  toPosixPath
} from "../contracts/governance.ts";

interface RunIndexFs {
  readdir: (pathValue: string, options: { withFileTypes: true }) => Promise<Dirent[]>;
  readFile: (pathValue: string, encoding: "utf8") => Promise<string>;
}

const NODE_FS: RunIndexFs = {
  readdir,
  readFile
};

export interface RunIndexOptions {
  runsRoot: string;
  latestRunIdPath: string;
  fs?: RunIndexFs;
}

function isNotFoundError(error: unknown): boolean {
  return Boolean(
    error &&
      typeof error === "object" &&
      "code" in error &&
      typeof (error as { code?: unknown }).code === "string" &&
      (error as { code: string }).code === "ENOENT"
  );
}

function createWarning(code: string, message: string, target: string): GovernanceIssue {
  return {
    code,
    message,
    severity: "warn",
    target
  };
}

function compareRunSummary(left: GovernanceRunSummary, right: GovernanceRunSummary): number {
  return left.runId.localeCompare(right.runId);
}

export class RunIndex {
  readonly #runsRoot: string;
  readonly #latestRunIdPath: string;
  readonly #fs: RunIndexFs;

  constructor(options: RunIndexOptions) {
    this.#runsRoot = path.resolve(options.runsRoot);
    this.#latestRunIdPath = path.resolve(options.latestRunIdPath);
    this.#fs = options.fs ?? NODE_FS;
  }

  async #readLatestRunId(warnings: GovernanceIssue[]): Promise<string | null> {
    try {
      const value = await this.#fs.readFile(this.#latestRunIdPath, "utf8");
      const normalized = normalizeRunId(value);
      if (!normalized) {
        warnings.push(
          createWarning(
            "LATEST_RUN_ID_EMPTY",
            "LATEST_RUN_ID.txt exists but is empty",
            toPosixPath(this.#latestRunIdPath)
          )
        );
        return null;
      }
      return normalized;
    } catch (error) {
      if (!isNotFoundError(error)) {
        warnings.push(
          createWarning(
            "LATEST_RUN_ID_READ_FAILED",
            "Failed to read latest run id marker; deterministic fallback applied",
            toPosixPath(this.#latestRunIdPath)
          )
        );
      }
      return null;
    }
  }

  async #listRunDirs(warnings: GovernanceIssue[]): Promise<string[]> {
    try {
      const entries = await this.#fs.readdir(this.#runsRoot, { withFileTypes: true });
      const runIds = entries
        .filter((entry) => entry.isDirectory())
        .map((entry) => entry.name)
        .filter((runId) => {
          if (isSafeRunId(runId)) {
            return true;
          }
          warnings.push(
            createWarning(
              "RUN_ID_SKIPPED_UNSAFE",
              "Skipped run directory that does not satisfy deterministic run id policy",
              toPosixPath(path.join(this.#runsRoot, runId))
            )
          );
          return false;
        });

      return sortDeterministicRunIds(runIds);
    } catch (error) {
      if (isNotFoundError(error)) {
        warnings.push(
          createWarning(
            "RUNS_ROOT_MISSING",
            "Runs root does not exist; returning empty deterministic list",
            toPosixPath(this.#runsRoot)
          )
        );
        return [];
      }

      warnings.push(
        createWarning(
          "RUNS_ROOT_READ_FAILED",
          "Failed to list runs root; returning empty deterministic list",
          toPosixPath(this.#runsRoot)
        )
      );
      return [];
    }
  }

  async #buildSummary(runId: string): Promise<GovernanceRunSummary> {
    const runPath = path.join(this.#runsRoot, runId);

    let entries: Dirent[] = [];
    try {
      entries = await this.#fs.readdir(runPath, { withFileTypes: true });
    } catch {
      entries = [];
    }

    const hasRunManifest = entries.some(
      (entry) => entry.isFile() && entry.name === "RUN_MANIFEST.json"
    );
    const bundleDirectories = entries
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name)
      .filter((name) => name.endsWith("_worker") || name === "Z_integrator")
      .sort((left, right) => left.localeCompare(right));

    return {
      runId,
      runPath: toPosixPath(runPath),
      hasRunManifest,
      hasEWorkerBundle: bundleDirectories.includes("E_worker"),
      hasZIntegratorBundle: bundleDirectories.includes("Z_integrator"),
      bundleDirectories
    };
  }

  async listRuns(): Promise<GovernanceRunsListResponse> {
    const warnings: GovernanceIssue[] = [];
    const latestRunId = await this.#readLatestRunId(warnings);
    const runIds = await this.#listRunDirs(warnings);

    const summaries = await Promise.all(runIds.map((runId) => this.#buildSummary(runId)));
    summaries.sort(compareRunSummary);

    return {
      mode: "local",
      deterministic: true,
      runsRoot: toPosixPath(this.#runsRoot),
      latestRunId,
      runs: summaries,
      warnings: sortIssuesDeterministically(warnings)
    };
  }
}
