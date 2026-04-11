import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { mkdtemp, mkdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { tmpdir } from "node:os";
import type { Dirent, Stats } from "node:fs";
import { describe, it } from "node:test";
import { ArtifactStore } from "../adapters/artifactStore.ts";

function sha256(text: string): string {
  return createHash("sha256").update(Buffer.from(text, "utf8")).digest("hex");
}

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

function createStats(kind: "file" | "directory", size = 0): Stats {
  return {
    isFile: () => kind === "file",
    isDirectory: () => kind === "directory",
    isBlockDevice: () => false,
    isCharacterDevice: () => false,
    isFIFO: () => false,
    isSocket: () => false,
    isSymbolicLink: () => false,
    size
  } as Stats;
}

async function createRunArtifactsFixture(): Promise<{ runsRoot: string; runId: string }> {
  const runsRoot = await mkdtemp(path.join(tmpdir(), "core-api-governance-artifacts-"));
  const runId = "factory_20260224_140000_aaaaaaaa_001";
  const runRoot = path.join(runsRoot, runId);

  await mkdir(path.join(runRoot, "A_worker", "LOGS"), { recursive: true });
  await mkdir(path.join(runRoot, "E_worker"), { recursive: true });
  await mkdir(path.join(runRoot, "Z_integrator"), { recursive: true });
  await writeFile(path.join(runRoot, "RUN_MANIFEST.json"), '{\n  "run_id": "fixture"\n}\n', "utf8");
  await writeFile(path.join(runRoot, "A_worker", "SUMMARY.md"), "# Summary\n", "utf8");
  await writeFile(
    path.join(runRoot, "A_worker", "LOGS", "INDEX.json"),
    '{\n  "events": []\n}\n',
    "utf8"
  );
  await writeFile(
    path.join(runRoot, "E_worker", "STATUS.json"),
    '{\n  "status": "PASS"\n}\n',
    "utf8"
  );
  await writeFile(path.join(runRoot, "Z_integrator", "FINAL_REPORT.txt"), "final-report\n", "utf8");

  return {
    runsRoot,
    runId
  };
}

describe("ArtifactStore", () => {
  it("returns deterministic invalid-run response for unsafe run IDs", async () => {
    const store = new ArtifactStore({
      runsRoot: "/virtual/runs"
    });

    const result = await store.listRunArtifacts("../escape");
    assert.equal(result.status, "invalid_run_id");
    assert.equal(result.runExists, false);
    assert.deepEqual(result.artifacts, []);
    assert.equal(result.warnings[0]?.code, "INVALID_RUN_ID");
  });

  it("returns deterministic missing-run fallback", async () => {
    const store = new ArtifactStore({
      runsRoot: "/virtual/runs"
    });

    const first = await store.listRunArtifacts("factory_20260224_150000_bbbbbbbb_001");
    const second = await store.listRunArtifacts("factory_20260224_150000_bbbbbbbb_001");
    assert.deepEqual(first, second);
    assert.equal(first.status, "missing_run");
    assert.equal(first.runExists, false);
    assert.equal(
      first.warnings.some((warning) => warning.code === "RUN_DIRECTORY_MISSING"),
      true
    );
  });

  it("builds deterministic sorted artifact manifest with hashes for files", async () => {
    const fixture = await createRunArtifactsFixture();
    try {
      const store = new ArtifactStore({
        runsRoot: fixture.runsRoot
      });

      const payload = await store.listRunArtifacts(fixture.runId);
      assert.equal(payload.status, "ok");
      assert.equal(payload.runExists, true);
      assert.equal(payload.warnings.length, 0);

      const relativePaths = payload.artifacts.map((entry) => entry.relativePath);
      assert.deepEqual(
        relativePaths,
        [...relativePaths].sort((left, right) => left.localeCompare(right))
      );
      assert.equal(relativePaths.includes("RUN_MANIFEST.json"), true);
      assert.equal(relativePaths.includes("A_worker"), true);
      assert.equal(relativePaths.includes("A_worker/SUMMARY.md"), true);
      assert.equal(relativePaths.includes("A_worker/LOGS/INDEX.json"), true);

      const summary = payload.artifacts.find(
        (entry) => entry.relativePath === "A_worker/SUMMARY.md"
      );
      assert.ok(summary);
      assert.equal(summary?.kind, "file");
      assert.equal(summary?.sha256, sha256("# Summary\n"));

      const manifest = payload.artifacts.find(
        (entry) => entry.relativePath === "RUN_MANIFEST.json"
      );
      assert.ok(manifest);
      assert.equal(manifest?.kind, "file");
      assert.equal(manifest?.sha256, sha256('{\n  "run_id": "fixture"\n}\n'));
    } finally {
      await rm(fixture.runsRoot, { recursive: true, force: true });
    }
  });

  it("handles filesystem read failures deterministically", async () => {
    const runsRoot = path.resolve("/virtual/runs");
    const runId = "factory_20260224_160000_cccccccc_001";
    const runPath = path.join(runsRoot, runId);
    const manifestPath = path.join(runPath, "RUN_MANIFEST.json");
    const eWorkerPath = path.join(runPath, "E_worker");
    const statusPath = path.join(eWorkerPath, "STATUS.json");

    const fsMock = {
      readdir: async (pathValue: string, _options: { withFileTypes: true }): Promise<Dirent[]> => {
        if (pathValue === runPath) {
          return [createDirent("RUN_MANIFEST.json", "file"), createDirent("E_worker", "directory")];
        }
        if (pathValue === eWorkerPath) {
          return [createDirent("STATUS.json", "file")];
        }
        throw Object.assign(new Error("readdir failure"), { code: "EACCES" });
      },
      lstat: async (pathValue: string): Promise<Stats> => {
        if (pathValue === runPath) {
          return createStats("directory");
        }
        if (pathValue === eWorkerPath) {
          return createStats("directory");
        }
        if (pathValue === manifestPath) {
          return createStats("file", 10);
        }
        if (pathValue === statusPath) {
          return createStats("file", 8);
        }
        throw Object.assign(new Error("lstat failure"), { code: "EACCES" });
      },
      readFile: async (pathValue: string): Promise<Buffer> => {
        if (pathValue === manifestPath) {
          throw Object.assign(new Error("cannot read manifest"), { code: "EACCES" });
        }
        if (pathValue === statusPath) {
          return Buffer.from('{"ok":true}\n', "utf8");
        }
        throw Object.assign(new Error("cannot read"), { code: "EACCES" });
      }
    };

    const store = new ArtifactStore({
      runsRoot,
      fs: fsMock
    });

    const payload = await store.listRunArtifacts(runId);
    assert.equal(payload.status, "ok");
    assert.equal(payload.runExists, true);
    assert.equal(
      payload.artifacts.some((entry) => entry.kind === "unreadable"),
      true
    );
    assert.equal(
      payload.warnings.some((warning) => warning.code === "ARTIFACT_FILE_READ_FAILED"),
      true
    );
    assert.deepEqual(
      payload.artifacts.map((entry) => entry.relativePath),
      [...payload.artifacts.map((entry) => entry.relativePath)].sort((left, right) =>
        left.localeCompare(right)
      )
    );
  });
});
