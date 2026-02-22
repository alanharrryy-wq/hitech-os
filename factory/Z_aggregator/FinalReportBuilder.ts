import { mkdirSync, writeFileSync } from "node:fs";
import * as path from "node:path";
import { DeterministicExecutionReport } from "../contracts/ExecutionReport";
import { HashProvider, hashText } from "../shared/Hashing";
import { assertRepoRelativePath } from "../shared/Pathing";
import { AggregatedResult } from "./ResultAggregator";

export interface FinalReportInput {
  readonly executionReport: DeterministicExecutionReport;
  readonly aggregatedResult: AggregatedResult;
  readonly trace: readonly {
    readonly workerId: string;
    readonly position: number;
    readonly contextHash: string;
    readonly outputHash: string;
    readonly status: string;
  }[];
}

export interface FinalReportArtifact {
  readonly text: string;
  readonly hash: string;
}

function renderSection(title: string, bodyLines: readonly string[]): string {
  return [`## ${title}`, ...bodyLines, ""].join("\n");
}

function renderTrace(
  trace: FinalReportInput["trace"],
): readonly string[] {
  if (trace.length === 0) {
    return ["(no trace records)"];
  }
  return trace
    .slice()
    .sort((left, right) => left.position - right.position)
    .map((record) => {
      return [
        `- [${record.position}] ${record.workerId} -> ${record.status}`,
        `  context: ${record.contextHash}`,
        `  output : ${record.outputHash}`,
      ].join("\n");
    });
}

function renderFileSummaries(input: AggregatedResult): readonly string[] {
  if (input.fileSummaries.length === 0) {
    return ["(no changed files)"];
  }
  return input.fileSummaries.map((summary) => {
    return [
      `- ${summary.path}`,
      `  workers: ${summary.workers.join(", ")}`,
      `  kinds: ${summary.kinds.join(", ")}`,
      `  bytes: ${summary.totalBytes}`,
      `  hashes: ${summary.hashes.join(", ")}`,
    ].join("\n");
  });
}

function renderConflicts(input: AggregatedResult): readonly string[] {
  if (input.conflicts.length === 0) {
    return ["- none"];
  }
  return input.conflicts.map((conflictPath) => `- ${conflictPath}`);
}

export class FinalReportBuilder {
  private readonly hasher: HashProvider;

  constructor(hasher: HashProvider) {
    this.hasher = hasher;
  }

  build(input: FinalReportInput): FinalReportArtifact {
    const headerLines = [
      `RUN_ID: ${input.executionReport.runId}`,
      `BASE_REF: ${input.executionReport.baseRef}`,
      `EXECUTION_SEED: ${input.executionReport.executionSeed}`,
      `AGGREGATE_STATUS: ${input.aggregatedResult.status}`,
      `AGGREGATE_HASH: ${input.aggregatedResult.aggregateHash}`,
    ];

    const featureFlagLines = Object.keys(input.executionReport.featureFlags)
      .sort((left, right) => left.localeCompare(right))
      .map((key) => {
        const value = input.executionReport.featureFlags[key as keyof typeof input.executionReport.featureFlags];
        return `- ${key}: ${value ? "ON" : "OFF"}`;
      });

    const sections = [
      renderSection("Final Summary", headerLines),
      renderSection("Feature Flags", featureFlagLines),
      renderSection("Execution Trace", renderTrace(input.trace)),
      renderSection("File Summaries", renderFileSummaries(input.aggregatedResult)),
      renderSection("Conflicts", renderConflicts(input.aggregatedResult)),
      renderSection("Diff", input.aggregatedResult.diffPatch.split("\n")),
    ];

    const text = sections.join("\n").trimEnd() + "\n";
    const hash = hashText(text, this.hasher);
    return {
      text,
      hash,
    };
  }

  writeFinalReport(
    repoRoot: string,
    reportPath: string,
    input: FinalReportInput,
  ): FinalReportArtifact {
    const normalizedReportPath = assertRepoRelativePath(reportPath, "reportPath");
    const absolutePath = path.resolve(repoRoot, normalizedReportPath);
    const absoluteDir = path.dirname(absolutePath);
    mkdirSync(absoluteDir, { recursive: true });
    const artifact = this.build(input);
    writeFileSync(absolutePath, artifact.text, { encoding: "utf8" });
    return artifact;
  }
}
