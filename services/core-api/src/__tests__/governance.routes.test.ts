import assert from "node:assert/strict";
import { mkdtemp, mkdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { describe, it } from "node:test";
import { buildServer } from "../server.ts";
import type { AiAgentClient } from "../lib/aiAgentClient.ts";

async function readJson(response: Response): Promise<unknown> {
  const text = await response.text();
  return text.trim().length === 0 ? {} : (JSON.parse(text) as unknown);
}

async function startServerForRunsRoot(runsRoot: string): Promise<{
  baseUrl: string;
  close: () => Promise<void>;
}> {
  const agentStub = {
    getCapabilities: async () => ({
      ok: false as const,
      statusCode: 503,
      errorCode: "UNUSED",
      message: "unused"
    }),
    runJob: async () => ({
      ok: false as const,
      statusCode: 503,
      errorCode: "UNUSED",
      message: "unused"
    }),
    health: async () => ({
      ok: false as const,
      statusCode: 503,
      errorCode: "UNUSED",
      message: "unused"
    })
  } as unknown as AiAgentClient;

  const { server } = buildServer({
    runtimeConfig: {
      host: "127.0.0.1",
      port: 0,
      governanceRunsRoot: runsRoot,
      governanceLatestRunIdPath: path.join(runsRoot, "LATEST_RUN_ID.txt")
    },
    agentClient: agentStub
  });

  await new Promise<void>((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => resolve());
  });

  const address = server.address();
  if (!address || typeof address === "string") {
    throw new Error("unable to determine test server address");
  }

  return {
    baseUrl: `http://127.0.0.1:${address.port}`,
    close: () =>
      new Promise<void>((resolve, reject) => {
        server.close((error) => {
          if (error) {
            reject(error);
            return;
          }
          resolve();
        });
      })
  };
}

async function createGovernanceRunsFixture(): Promise<{ runsRoot: string; runId: string }> {
  const runsRoot = await mkdtemp(path.join(tmpdir(), "core-api-governance-routes-"));
  const runId = "factory_20260224_170000_aaaaaaaa_001";

  await mkdir(path.join(runsRoot, runId, "E_worker"), { recursive: true });
  await mkdir(path.join(runsRoot, runId, "Z_integrator"), { recursive: true });
  await writeFile(
    path.join(runsRoot, runId, "RUN_MANIFEST.json"),
    '{\n  "run_id": "fixture"\n}\n',
    "utf8"
  );
  await writeFile(path.join(runsRoot, runId, "E_worker", "SUMMARY.md"), "# worker\n", "utf8");
  await writeFile(path.join(runsRoot, "LATEST_RUN_ID.txt"), `${runId}\n`, "utf8");

  return {
    runsRoot,
    runId
  };
}

describe("governance routes", () => {
  it("serves deterministic S1 governance stage payload", async () => {
    const fixture = await createGovernanceRunsFixture();
    const started = await startServerForRunsRoot(fixture.runsRoot);
    try {
      const response = await fetch(`${started.baseUrl}/governance/stage/S1`);
      assert.equal(response.status, 200);
      const payload = (await readJson(response)) as {
        stageId: string;
        requirementIds: string[];
      };

      assert.equal(payload.stageId, "S1");
      assert.deepEqual(payload.requirementIds, [
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
      ]);
    } finally {
      await started.close();
      await rm(fixture.runsRoot, { recursive: true, force: true });
    }
  });

  it("returns governance run list with deterministic local metadata", async () => {
    const fixture = await createGovernanceRunsFixture();
    const started = await startServerForRunsRoot(fixture.runsRoot);
    try {
      const response = await fetch(`${started.baseUrl}/governance/runs`);
      assert.equal(response.status, 200);
      const payload = (await readJson(response)) as {
        latestRunId: string | null;
        runs: Array<{
          runId: string;
          hasRunManifest: boolean;
          hasLegacyEWorkerBundle: boolean;
          hasZAggregatorBundle: boolean;
        }>;
      };

      assert.equal(payload.latestRunId, fixture.runId);
      assert.equal(payload.runs.length, 1);
      assert.equal(payload.runs[0]?.runId, fixture.runId);
      assert.equal(payload.runs[0]?.hasRunManifest, true);
      assert.equal(payload.runs[0]?.hasLegacyEWorkerBundle, true);
      assert.equal(payload.runs[0]?.hasZAggregatorBundle, true);
    } finally {
      await started.close();
      await rm(fixture.runsRoot, { recursive: true, force: true });
    }
  });

  it("returns governance artifact manifest for existing and missing runs", async () => {
    const fixture = await createGovernanceRunsFixture();
    const started = await startServerForRunsRoot(fixture.runsRoot);
    try {
      const foundResponse = await fetch(
        `${started.baseUrl}/governance/runs/${fixture.runId}/artifacts`
      );
      assert.equal(foundResponse.status, 200);
      const foundPayload = (await readJson(foundResponse)) as {
        runExists: boolean;
        status: string;
        artifacts: Array<{ relativePath: string }>;
      };

      assert.equal(foundPayload.runExists, true);
      assert.equal(foundPayload.status, "ok");
      assert.equal(
        foundPayload.artifacts.some((entry) => entry.relativePath === "RUN_MANIFEST.json"),
        true
      );
      assert.equal(
        foundPayload.artifacts.some((entry) => entry.relativePath === "E_worker/SUMMARY.md"),
        true
      );

      const missingResponse = await fetch(
        `${started.baseUrl}/governance/runs/factory_20260224_170000_aaaaaaaa_099/artifacts`
      );
      assert.equal(missingResponse.status, 200);
      const missingPayload = (await readJson(missingResponse)) as {
        runExists: boolean;
        status: string;
        artifacts: Array<unknown>;
      };
      assert.equal(missingPayload.runExists, false);
      assert.equal(missingPayload.status, "missing_run");
      assert.deepEqual(missingPayload.artifacts, []);
    } finally {
      await started.close();
      await rm(fixture.runsRoot, { recursive: true, force: true });
    }
  });

  it("returns deterministic 400 payload for invalid run IDs", async () => {
    const fixture = await createGovernanceRunsFixture();
    const started = await startServerForRunsRoot(fixture.runsRoot);
    try {
      const response = await fetch(
        `${started.baseUrl}/governance/runs/${encodeURIComponent("../escape")}/artifacts`
      );
      assert.equal(response.status, 400);
      const payload = (await readJson(response)) as {
        status: string;
        warnings: Array<{ code: string }>;
      };

      assert.equal(payload.status, "invalid_run_id");
      assert.equal(payload.warnings[0]?.code, "INVALID_RUN_ID");
    } finally {
      await started.close();
      await rm(fixture.runsRoot, { recursive: true, force: true });
    }
  });
});
