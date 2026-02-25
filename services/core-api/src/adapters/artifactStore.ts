import { lstat, readdir, readFile } from "node:fs/promises";
import path from "node:path";
import { createHash } from "node:crypto";
import type { Dirent, Stats } from "node:fs";
import {
  type GovernanceArtifactManifestEntry,
  type GovernanceArtifactsManifestResponse,
  type GovernanceIssue,
  createInvalidRunIdArtifactsResponse,
  isSafeRunId,
  normalizeRunId,
  sortArtifactsDeterministically,
  sortIssuesDeterministically,
  toPosixPath
} from "../contracts/governance.ts";

interface ArtifactStoreFs {
  readdir: (pathValue: string, options: { withFileTypes: true }) => Promise<Dirent[]>;
  lstat: (pathValue: string) => Promise<Stats>;
  readFile: (pathValue: string) => Promise<Buffer>;
}

const NODE_FS: ArtifactStoreFs = {
  readdir,
  lstat,
  readFile
};

export interface ArtifactStoreOptions {
  runsRoot: string;
  fs?: ArtifactStoreFs;
}

interface WalkState {
  absolutePath: string;
  relativePath: string;
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

function isPathInsideRoot(root: string, candidate: string): boolean {
  const relative = path.relative(root, candidate);
  return relative === "" || (!relative.startsWith("..") && !path.isAbsolute(relative));
}

function createWarning(code: string, message: string, target: string): GovernanceIssue {
  return {
    code,
    message,
    severity: "warn",
    target
  };
}

function createError(code: string, message: string, target: string): GovernanceIssue {
  return {
    code,
    message,
    severity: "error",
    target
  };
}

function relativeToPosix(relativePath: string): string {
  return relativePath.split(path.sep).join("/");
}

function sha256(content: Buffer): string {
  return createHash("sha256").update(content).digest("hex");
}

function compareWalkState(left: WalkState, right: WalkState): number {
  return left.relativePath.localeCompare(right.relativePath);
}

export class ArtifactStore {
  readonly #runsRoot: string;
  readonly #fs: ArtifactStoreFs;

  constructor(options: ArtifactStoreOptions) {
    this.#runsRoot = path.resolve(options.runsRoot);
    this.#fs = options.fs ?? NODE_FS;
  }

  async #loadFileArtifact(
    absolutePath: string,
    relativePath: string,
    stats: Stats,
    warnings: GovernanceIssue[]
  ): Promise<GovernanceArtifactManifestEntry> {
    try {
      const content = await this.#fs.readFile(absolutePath);
      return {
        relativePath: relativeToPosix(relativePath),
        absolutePath: toPosixPath(absolutePath),
        kind: "file",
        sizeBytes: stats.size,
        sha256: sha256(content)
      };
    } catch {
      warnings.push(
        createWarning(
          "ARTIFACT_FILE_READ_FAILED",
          "Failed to read artifact file; checksum omitted",
          toPosixPath(absolutePath)
        )
      );
      return {
        relativePath: relativeToPosix(relativePath),
        absolutePath: toPosixPath(absolutePath),
        kind: "unreadable",
        sizeBytes: stats.size,
        sha256: null
      };
    }
  }

  async #inspectEntry(
    state: WalkState,
    dirent: Dirent,
    queue: WalkState[],
    artifacts: GovernanceArtifactManifestEntry[],
    warnings: GovernanceIssue[]
  ): Promise<void> {
    const absolutePath = path.join(state.absolutePath, dirent.name);
    const relativePath =
      state.relativePath.length === 0 ? dirent.name : path.join(state.relativePath, dirent.name);

    let stats: Stats;
    try {
      stats = await this.#fs.lstat(absolutePath);
    } catch {
      warnings.push(
        createWarning(
          "ARTIFACT_LSTAT_FAILED",
          "Failed to inspect artifact path",
          toPosixPath(absolutePath)
        )
      );
      artifacts.push({
        relativePath: relativeToPosix(relativePath),
        absolutePath: toPosixPath(absolutePath),
        kind: "unreadable",
        sizeBytes: null,
        sha256: null
      });
      return;
    }

    if (stats.isSymbolicLink()) {
      artifacts.push({
        relativePath: relativeToPosix(relativePath),
        absolutePath: toPosixPath(absolutePath),
        kind: "symlink",
        sizeBytes: null,
        sha256: null
      });
      return;
    }

    if (stats.isDirectory()) {
      artifacts.push({
        relativePath: relativeToPosix(relativePath),
        absolutePath: toPosixPath(absolutePath),
        kind: "directory",
        sizeBytes: 0,
        sha256: null
      });
      queue.push({
        absolutePath,
        relativePath
      });
      return;
    }

    if (stats.isFile()) {
      artifacts.push(await this.#loadFileArtifact(absolutePath, relativePath, stats, warnings));
      return;
    }

    artifacts.push({
      relativePath: relativeToPosix(relativePath),
      absolutePath: toPosixPath(absolutePath),
      kind: "other",
      sizeBytes: null,
      sha256: null
    });
  }

  async #walkRunDirectory(runPath: string): Promise<{
    artifacts: GovernanceArtifactManifestEntry[];
    warnings: GovernanceIssue[];
  }> {
    const queue: WalkState[] = [
      {
        absolutePath: runPath,
        relativePath: ""
      }
    ];
    const artifacts: GovernanceArtifactManifestEntry[] = [];
    const warnings: GovernanceIssue[] = [];

    while (queue.length > 0) {
      queue.sort(compareWalkState);
      const current = queue.shift();
      if (!current) {
        continue;
      }

      let entries: Dirent[] = [];
      try {
        entries = await this.#fs.readdir(current.absolutePath, { withFileTypes: true });
      } catch {
        warnings.push(
          createWarning(
            "ARTIFACT_DIR_READ_FAILED",
            "Failed to list artifact directory; continuing deterministic walk",
            toPosixPath(current.absolutePath)
          )
        );
        continue;
      }

      entries.sort((left, right) => left.name.localeCompare(right.name));
      for (const entry of entries) {
        await this.#inspectEntry(current, entry, queue, artifacts, warnings);
      }
    }

    return {
      artifacts: sortArtifactsDeterministically(artifacts),
      warnings: sortIssuesDeterministically(warnings)
    };
  }

  async listRunArtifacts(runId: string): Promise<GovernanceArtifactsManifestResponse> {
    const normalizedRunId = normalizeRunId(runId);
    if (!isSafeRunId(normalizedRunId)) {
      return createInvalidRunIdArtifactsResponse({
        runId: normalizedRunId,
        runsRoot: this.#runsRoot
      });
    }

    const runPath = path.resolve(this.#runsRoot, normalizedRunId);
    if (!isPathInsideRoot(this.#runsRoot, runPath)) {
      return createInvalidRunIdArtifactsResponse({
        runId: normalizedRunId,
        runsRoot: this.#runsRoot,
        reason: "runId resolves outside runs root"
      });
    }

    let runStats: Stats;
    try {
      runStats = await this.#fs.lstat(runPath);
    } catch (error) {
      if (isNotFoundError(error)) {
        return {
          mode: "local",
          deterministic: true,
          runId: normalizedRunId,
          runPath: toPosixPath(runPath),
          runExists: false,
          status: "missing_run",
          artifacts: [],
          warnings: sortIssuesDeterministically([
            createWarning(
              "RUN_DIRECTORY_MISSING",
              "Run directory does not exist; manifest uses deterministic empty fallback",
              toPosixPath(runPath)
            )
          ])
        };
      }

      return {
        mode: "local",
        deterministic: true,
        runId: normalizedRunId,
        runPath: toPosixPath(runPath),
        runExists: false,
        status: "read_error",
        artifacts: [],
        warnings: sortIssuesDeterministically([
          createError(
            "RUN_DIRECTORY_READ_FAILED",
            "Unable to inspect run directory",
            toPosixPath(runPath)
          )
        ])
      };
    }

    if (!runStats.isDirectory()) {
      return {
        mode: "local",
        deterministic: true,
        runId: normalizedRunId,
        runPath: toPosixPath(runPath),
        runExists: false,
        status: "read_error",
        artifacts: [],
        warnings: sortIssuesDeterministically([
          createError("RUN_PATH_NOT_DIRECTORY", "Run path is not a directory", toPosixPath(runPath))
        ])
      };
    }

    const walked = await this.#walkRunDirectory(runPath);
    return {
      mode: "local",
      deterministic: true,
      runId: normalizedRunId,
      runPath: toPosixPath(runPath),
      runExists: true,
      status: walked.warnings.some((warning) => warning.severity === "error") ? "read_error" : "ok",
      artifacts: walked.artifacts,
      warnings: walked.warnings
    };
  }
}
