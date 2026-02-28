import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { test } from "node:test";
import {
  collectFiles,
  collectUsedLayerIds,
  firstExistingPath,
  parseStaticLayerIds,
  resolveRepoRoot,
  toRelativePosix
} from "./layer_id_guard_helpers.mjs";

const repoRoot = resolveRepoRoot(import.meta.url);

const layerIdsCandidates = [
  path.join(repoRoot, "packages/ui-kit/src/layers/layerIds.ts"),
  path.join(repoRoot, "packages/ui-kit/src/layers/layerIds.tsx"),
  path.join(repoRoot, "packages/ui-kit/src/layers/layerIds.mts"),
  path.join(repoRoot, "packages/ui-kit/src/layerIds.ts")
];

const scanRoots = [
  path.join(repoRoot, "packages/ui-kit/src"),
  path.join(repoRoot, "apps/web/src"),
  path.join(repoRoot, "apps/keystone/src")
];

test("all used layer IDs are declared in static layerIds.ts", () => {
  const filesToScan = scanRoots.flatMap((rootDir) => collectFiles(rootDir));
  const layerUsage = collectUsedLayerIds(filesToScan);
  const usedIds = [...layerUsage.keys()].sort((left, right) => left.localeCompare(right));

  const layerIdsFile = firstExistingPath(layerIdsCandidates);

  if (!layerIdsFile) {
    assert.equal(
      usedIds.length,
      0,
      [
        "Layer IDs are in use but no static registry file was found.",
        "Expected one of:",
        ...layerIdsCandidates.map((candidate) => `- ${toRelativePosix(repoRoot, candidate)}`),
        "Used IDs:",
        ...usedIds.map((id) => {
          const files = layerUsage.get(id) ?? [];
          const refs = files.slice(0, 5).map((entry) => toRelativePosix(repoRoot, entry)).join(", ");
          return `- ${id}: ${refs}`;
        })
      ].join("\n")
    );
    return;
  }

  const declaredIds = parseStaticLayerIds(fs.readFileSync(layerIdsFile, "utf8"));
  const declaredSet = new Set(declaredIds);

  const missing = usedIds.filter((id) => !declaredSet.has(id));

  assert.deepEqual(
    missing,
    [],
    [
      `layerIds registry file: ${toRelativePosix(repoRoot, layerIdsFile)}`,
      "Layer IDs used in source but missing in static registry:",
      ...missing.map((id) => {
        const files = layerUsage.get(id) ?? [];
        const refs = files.slice(0, 8).map((entry) => toRelativePosix(repoRoot, entry)).join(", ");
        return `- ${id}: ${refs}`;
      })
    ].join("\n")
  );

  assert.ok(declaredIds.length > 0, "layerIds.ts exists but no valid layer IDs were parsed");
});
