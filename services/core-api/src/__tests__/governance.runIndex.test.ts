import assert from "node:assert/strict";
import { mkdtemp, mkdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import type { Dirent } from "node:fs";
import { describe, it } from "node:test";
import { RunIndex } from "../adapters/runIndex.ts";

function createDirent(name: string, kind: "file" | "directory"): Dirent {
  return {
    name,
    isDirectory: () => kind === "directory",
    isFile: () => kind === "file",
    isBlockDevice: () => false,
    isCharacterDevice: () => false,
    isFIFO: () => false,
    isSocket: () => false,
    isSymbolicLink: () => false
  } as Dirent;
}

async function createTempRunsRoot(): Promise<string> {
  const root = await mkdtemp(path.join(tmpdir(), "core-api-governance-runs-"));
  await mkdir(path.join(root, "factory_20260224_100000_aaaaaaaa_001"), { recursive: true });
  await mkdir(path.join(root, "factory_20260224_100001_aaaaaaaa_002", "A_worker"), {
    recursive: true
  });
  await mkdir(path.join(root, "factory_20260224_100001_aaaaaaaa_002", "E_worker"), {
    recursive: true
  });
  await mkdir(path.join(root, "factory_20260224_100001_aaaaaaaa_002", "Z_integrator"), {
    recursive: true
  });
  await mkdir(path.join(root, "RUN_PHASE1_EXTRACT_004"), { recursive: true });
  await mkdir(path.join(root, "unsafe run id"), { recursive: true });
  await writeFile(
    path.join(root, "factory_20260224_100001_aaaaaaaa_002", "RUN_MANIFEST.json"),
    "{}\n",
    "utf8"
  );
  await writeFile(
    path.join(root, "LATEST_RUN_ID.txt"),
    "factory_20260224_100001_aaaaaaaa_002\n",
    "utf8"
  );
  return root;
}

describe("RunIndex", () => {
  it("lists runs deterministically and includes bundle metadata", async () => {
    const runsRoot = await createTempRunsRoot();
    try {
      const index = new RunIndex({
        runsRoot,
        latestRunIdPath: path.join(runsRoot, "LATEST_RUN_ID.txt")
      });

      const payload = await index.listRuns();
      assert.equal(payload.mode, "local");
      assert.equal(payload.deterministic, true);
      assert.equal(payload.latestRunId, "factory_20260224_100001_aaaaaaaa_002");
      assert.deepEqual(
        payload.runs.map((item) => item.runId),
        [
          "factory_20260224_100000_aaaaaaaa_001",
          "factory_20260224_100001_aaaaaaaa_002",
          "RUN_PHASE1_EXTRACT_004"
        ]
      );

      const withBundles = payload.runs.find(
        (item) => item.runId === "factory_20260224_100001_aaaaaaaa_002"
      );
      assert.ok(withBundles);
      assert.equal(withBundles?.hasRunManifest, true);
      assert.equal(withBundles?.hasEWorkerBundle, true);
      assert.equal(withBundles?.hasZIntegratorBundle, true);
      assert.deepEqual(withBundles?.bundleDirectories, ["A_worker", "E_worker", "Z_integrator"]);
      assert.equal(
        payload.warnings.some((warning) => warning.code === "RUN_ID_SKIPPED_UNSAFE"),
        true
      );
    } finally {
      await rm(runsRoot, { recursive: true, force: true });
    }
  });

  it("returns deterministic empty list when runs root does not exist", async () => {
    const missingRoot = path.join(tmpdir(), "missing-governance-runs-root-does-not-exist");
    const index = new RunIndex({
      runsRoot: missingRoot,
      latestRunIdPath: path.join(missingRoot, "LATEST_RUN_ID.txt")
    });

    const first = await index.listRuns();
    const second = await index.listRuns();
    assert.deepEqual(first, second);
    assert.deepEqual(first.runs, []);
    assert.equal(
      first.warnings.some((warning) => warning.code === "RUNS_ROOT_MISSING"),
      true
    );
  });

  it("keeps warning payload deterministic for read failures", async () => {
    const fsMock = {
      readdir: async (_pathValue: string, _options: { withFileTypes: true }): Promise<Dirent[]> => {
        const error = new Error("readdir failure");
        (error as Error & { code?: string }).code = "EACCES";
        throw error;
      },
      readFile: async (_pathValue: string, _encoding: "utf8"): Promise<string> => {
        const error = new Error("read failure");
        (error as Error & { code?: string }).code = "EACCES";
        throw error;
      }
    };

    const index = new RunIndex({
      runsRoot: "/virtual/runs",
      latestRunIdPath: "/virtual/runs/LATEST_RUN_ID.txt",
      fs: fsMock
    });

    const result = await index.listRuns();
    assert.equal(result.latestRunId, null);
    assert.deepEqual(result.runs, []);
    assert.deepEqual(
      result.warnings.map((warning) => warning.code),
      ["LATEST_RUN_ID_READ_FAILED", "RUNS_ROOT_READ_FAILED"]
    );
  });

  it("still emits deterministic summaries when per-run directory cannot be read", async () => {
    const runsRoot = path.resolve("/virtual/runs");
    const latestRunIdPath = path.join(runsRoot, "LATEST_RUN_ID.txt");
    const runId = "factory_20260224_120000_deadbeef_001";
    const runPath = path.join(runsRoot, runId);

    const fsMock = {
      readdir: async (pathValue: string, _options: { withFileTypes: true }): Promise<Dirent[]> => {
        if (pathValue === runsRoot) {
          return [createDirent(runId, "directory")];
        }
        const error = new Error("per-run read failure");
        (error as Error & { code?: string }).code = "EACCES";
        throw error;
      },
      readFile: async (pathValue: string, _encoding: "utf8"): Promise<string> => {
        if (pathValue === latestRunIdPath) {
          return `${runId}\n`;
        }
        throw Object.assign(new Error("read failure"), { code: "EACCES" });
      }
    };

    const index = new RunIndex({
      runsRoot,
      latestRunIdPath,
      fs: fsMock
    });

    const result = await index.listRuns();
    assert.equal(result.runs.length, 1);
    assert.equal(result.runs[0]?.runPath, runPath.split(path.sep).join("/"));
    assert.equal(result.runs[0]?.hasRunManifest, false);
    assert.deepEqual(result.runs[0]?.bundleDirectories, []);
    assert.equal(result.warnings.length, 0);
  });
});
