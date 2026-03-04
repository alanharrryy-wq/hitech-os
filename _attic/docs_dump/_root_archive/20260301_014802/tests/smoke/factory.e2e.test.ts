import { strict as assert } from "node:assert";
import { existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import * as path from "node:path";
import { test } from "node:test";
import { AgentRegistry, ContextGuard, CoreOrchestrator, DeterministicExecutor } from "../../factory/A_core";
import { FactoryAgent, AgentExecutionResult } from "../../factory/contracts/AgentInterface";
import { WorkerExecutionContext } from "../../factory/contracts/FactoryContracts";
import { hashText, Sha256HashProvider } from "../../factory/shared/Hashing";
import { FinalReportBuilder, ResultAggregator } from "../../factory/Z_aggregator";

class MockDeterministicAgent implements FactoryAgent {
  readonly workerId: string;
  readonly description: string;
  readonly deterministicOrderHint: number;
  readonly boundaries: FactoryAgent["boundaries"];
  readonly capabilities: FactoryAgent["capabilities"];
  private readonly ownedFilePath: string;

  constructor(workerId: string, orderHint: number, ownedFilePath: string) {
    this.workerId = workerId;
    this.description = `${workerId} deterministic smoke worker`;
    this.deterministicOrderHint = orderHint;
    this.ownedFilePath = ownedFilePath;
    this.boundaries = {
      allowedReadRoots: [`factory/${workerId}`, "factory/contracts", "factory/shared"],
      allowedWriteRoots: [`factory/${workerId}`],
      deniesCrossWorkerBundles: true,
    };
    this.capabilities = {
      supportsDryRun: true,
      supportsSnapshotOutput: true,
      emitsDiffs: true,
    };
  }

  async execute(context: WorkerExecutionContext): Promise<AgentExecutionResult> {
    const payloadToken = JSON.stringify(context.payload);
    const outputToken = `${context.runId}:${this.workerId}:${payloadToken}`;
    const checksum = hashText(outputToken);
    const inheritedKeys = Object.keys(context.inheritedState).sort((left, right) => left.localeCompare(right));

    return {
      workerId: this.workerId,
      status: "PASS",
      summary: `${this.workerId} executed deterministically`,
      fileChanges: [
        {
          workerId: this.workerId,
          path: this.ownedFilePath,
          kind: "modified",
          sha256: checksum,
          bytes: outputToken.length,
          summary: `${this.workerId} deterministic output`,
        },
      ],
      checks: [
        {
          name: "determinism_smoke",
          required: true,
          rc: 0,
          details: "Deterministic output generated from immutable context.",
        },
      ],
      metadata: {
        inheritedKeys,
      },
      output: {
        worker: this.workerId,
        checksum,
        inheritedKeys,
      },
    };
  }
}

test("factory orchestration remains deterministic for identical inputs", async () => {
  const hasher = new Sha256HashProvider();
  const registry = new AgentRegistry();
  const contextGuard = new ContextGuard(hasher);
  const executor = new DeterministicExecutor(contextGuard, hasher);
  const orchestrator = new CoreOrchestrator({
    registry,
    contextGuard,
    executor,
    hasher,
  });

  orchestrator.registerAgent(
    new MockDeterministicAgent("A_core", 1, "factory/A_core/CoreOrchestrator.ts"),
  );
  orchestrator.registerAgent(
    new MockDeterministicAgent("B_tooling", 2, "factory/B_tooling/ToolingPolicy.ts"),
  );

  const runRequest = {
    runId: "run_20260222_120000_deadbeef_001",
    baseRef: "HEAD",
    executionSeed: "seed-0001",
    payload: {
      objective: "deterministic smoke",
      retries: 0,
      modules: ["A_core", "B_tooling"] as const,
    },
    requestedWorkers: ["A_core", "B_tooling"] as const,
  };

  const firstRun = await orchestrator.execute(runRequest);
  const secondRun = await orchestrator.execute(runRequest);

  assert.equal(firstRun.reportHash, secondRun.reportHash, "execution report hash must be stable");
  assert.deepEqual(
    firstRun.report.records.map((record) => record.workerId),
    ["A_core", "B_tooling"],
    "worker order must remain deterministic",
  );

  const featureFlagStates = Object.values(firstRun.report.featureFlags);
  for (const state of featureFlagStates) {
    assert.equal(state, false, "feature flags must default to OFF");
  }

  const aggregator = new ResultAggregator(hasher);
  const firstAggregate = aggregator.aggregate(firstRun.results);
  const secondAggregate = aggregator.aggregate(secondRun.results);
  assert.equal(firstAggregate.aggregateHash, secondAggregate.aggregateHash, "aggregate hash must be stable");

  const reportBuilder = new FinalReportBuilder(hasher);
  const firstFinalReport = reportBuilder.build({
    executionReport: firstRun.report,
    aggregatedResult: firstAggregate,
    trace: firstRun.trace,
  });
  const secondFinalReport = reportBuilder.build({
    executionReport: secondRun.report,
    aggregatedResult: secondAggregate,
    trace: secondRun.trace,
  });
  assert.equal(firstFinalReport.hash, secondFinalReport.hash, "final report hash must be stable");

  const tempRoot = mkdtempSync(path.join(tmpdir(), "hitech-factory-smoke-"));
  try {
    const artifact = reportBuilder.writeFinalReport(
      tempRoot,
      "tools/codex/runs/run_20260222_120000_deadbeef_001/Z_aggregator/FINAL_REPORT.txt",
      {
        executionReport: firstRun.report,
        aggregatedResult: firstAggregate,
        trace: firstRun.trace,
      },
    );
    assert.equal(artifact.hash, firstFinalReport.hash, "written report hash must match built report hash");

    const reportPath = path.join(
      tempRoot,
      "tools",
      "codex",
      "runs",
      "run_20260222_120000_deadbeef_001",
      "Z_aggregator",
      "FINAL_REPORT.txt",
    );
    assert.ok(existsSync(reportPath), "FINAL_REPORT.txt must be generated");
    const diskText = readFileSync(reportPath, "utf8");
    assert.equal(hashText(diskText), firstFinalReport.hash, "disk report hash must be deterministic");
  } finally {
    rmSync(tempRoot, { recursive: true, force: true });
  }
});
