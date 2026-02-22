import { AgentExecutionResult } from "../contracts/AgentInterface";
import {
  BundleFileChange,
  BundleStatus,
  normalizeBundleChanges,
  summarizeBundleChanges,
} from "../contracts/BundleSchema";
import { JsonObject } from "../shared/DeterministicJson";
import { HashProvider, hashJsonValue } from "../shared/Hashing";
import { compareRepoPaths } from "../shared/Pathing";

export interface AggregatedFileSummary {
  readonly path: string;
  readonly workers: readonly string[];
  readonly kinds: readonly string[];
  readonly totalBytes: number;
  readonly hashes: readonly string[];
}

export interface AggregatedResult {
  readonly status: BundleStatus;
  readonly mergedChanges: readonly BundleFileChange[];
  readonly fileSummaries: readonly AggregatedFileSummary[];
  readonly conflicts: readonly string[];
  readonly diffPatch: string;
  readonly summary: JsonObject;
  readonly aggregateHash: string;
}

function deriveStatus(results: readonly AgentExecutionResult[], conflicts: readonly string[]): BundleStatus {
  if (results.some((result) => result.status === "FAIL")) {
    return "FAIL";
  }
  if (results.some((result) => result.status === "BLOCKED") || conflicts.length > 0) {
    return "BLOCKED";
  }
  if (results.some((result) => result.status === "WARN")) {
    return "WARN";
  }
  return "PASS";
}

function renderDeterministicDiff(changes: readonly BundleFileChange[]): string {
  const lines: string[] = [];
  for (const change of changes) {
    const kindToken = change.kind.toUpperCase().padEnd(8, " ");
    lines.push(`${kindToken} ${change.path} (${change.workerId}) sha256:${change.sha256}`);
  }
  return lines.join("\n");
}

function summarizeByFile(changes: readonly BundleFileChange[]): readonly AggregatedFileSummary[] {
  const byPath = new Map<string, BundleFileChange[]>();
  for (const change of changes) {
    const existing = byPath.get(change.path);
    if (existing === undefined) {
      byPath.set(change.path, [change]);
      continue;
    }
    existing.push(change);
  }

  const summaries: AggregatedFileSummary[] = [];
  const sortedPaths = Array.from(byPath.keys()).sort(compareRepoPaths);
  for (const pathValue of sortedPaths) {
    const changesForPath = byPath.get(pathValue);
    if (changesForPath === undefined) {
      continue;
    }
    const workers = Array.from(new Set(changesForPath.map((change) => change.workerId))).sort((left, right) =>
      left.localeCompare(right),
    );
    const kinds = Array.from(new Set(changesForPath.map((change) => change.kind))).sort((left, right) =>
      left.localeCompare(right),
    );
    const hashes = Array.from(new Set(changesForPath.map((change) => change.sha256))).sort((left, right) =>
      left.localeCompare(right),
    );
    const totalBytes = changesForPath.reduce((total, change) => total + change.bytes, 0);
    summaries.push({
      path: pathValue,
      workers,
      kinds,
      totalBytes,
      hashes,
    });
  }
  return summaries;
}

function findConflicts(fileSummaries: readonly AggregatedFileSummary[]): readonly string[] {
  const conflicts = fileSummaries
    .filter((summary) => summary.workers.length > 1)
    .map((summary) => summary.path)
    .sort(compareRepoPaths);
  return conflicts;
}

export class ResultAggregator {
  private readonly hasher: HashProvider;

  constructor(hasher: HashProvider) {
    this.hasher = hasher;
  }

  aggregate(results: readonly AgentExecutionResult[]): AggregatedResult {
    if (results.length === 0) {
      throw new Error("ResultAggregator requires at least one result.");
    }

    const orderedResults = [...results].sort((left, right) => left.workerId.localeCompare(right.workerId));
    const allChanges = normalizeBundleChanges(
      orderedResults.flatMap((result) => result.fileChanges),
    );
    const fileSummaries = summarizeByFile(allChanges);
    const conflicts = findConflicts(fileSummaries);
    const status = deriveStatus(orderedResults, conflicts);
    const diffPatch = renderDeterministicDiff(allChanges);

    const summary: JsonObject = {
      status,
      workersProcessed: orderedResults.length,
      changeSummary: summarizeBundleChanges(allChanges),
      conflictCount: conflicts.length,
    };

    const hashPayload: JsonObject = {
      status,
      mergedChanges: allChanges.map((change) => ({
        workerId: change.workerId,
        path: change.path,
        kind: change.kind,
        sha256: change.sha256,
        bytes: change.bytes,
        summary: change.summary,
      })),
      fileSummaries: fileSummaries.map((fileSummary) => ({
        path: fileSummary.path,
        workers: fileSummary.workers,
        kinds: fileSummary.kinds,
        totalBytes: fileSummary.totalBytes,
        hashes: fileSummary.hashes,
      })),
      conflicts: [...conflicts],
      summary,
    };

    const aggregateHash = hashJsonValue(
      hashPayload,
      this.hasher,
    );

    return {
      status,
      mergedChanges: allChanges,
      fileSummaries,
      conflicts,
      diffPatch,
      summary,
      aggregateHash,
    };
  }
}
