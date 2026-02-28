import assert from "node:assert/strict";
import path from "node:path";
import { test } from "node:test";
import {
  collectFiles,
  collectUsedLayerIds,
  parseCanonicalLayerIds,
  resolveRepoRoot,
  toRelativePosix
} from "./layer_ids_canonical_guard_helpers.mjs";

const repoRoot = resolveRepoRoot(import.meta.url);

const layerIdRegistryCandidates = [
  path.join(repoRoot, "packages/ui-kit/src/layers/layerIds.ts"),
  path.join(repoRoot, "tools/codex/runs/20260228_183257_093E/B_tooling/FILES/packages/ui-kit/src/layers/layerIds.ts"),
  path.join(repoRoot, "tools/codex/runs/20260228_164549_2F73/B_tooling/FILES/packages/ui-kit/src/layers/layerIds.ts")
];

const scanRoots = [
  path.join(repoRoot, "apps/keystone/app/pitch"),
  path.join(repoRoot, "apps/keystone/components/pitch"),
  path.join(repoRoot, "apps/keystone/lib/pitch")
];

test("only canonical layer IDs are used across keystone pitch surfaces", () => {
  const files = scanRoots.flatMap((rootDir) => collectFiles(rootDir));
  const usage = collectUsedLayerIds(files);
  const usedIds = [...usage.keys()].sort((left, right) => left.localeCompare(right));

  const canonicalIds = parseCanonicalLayerIds(layerIdRegistryCandidates);
  const canonicalSet = new Set(canonicalIds);

  if (usedIds.length === 0) {
    assert.ok(true, "No layer IDs detected under keystone pitch roots in this worktree");
    return;
  }

  assert.ok(
    canonicalIds.length > 0,
    [
      "Layer IDs are used but no canonical registry was found.",
      "Checked candidates:",
      ...layerIdRegistryCandidates.map((candidate) => `- ${toRelativePosix(repoRoot, candidate)}`)
    ].join("\n")
  );

  const missing = usedIds.filter((id) => !canonicalSet.has(id));

  assert.deepEqual(
    missing,
    [],
    [
      "Detected non-canonical layer IDs:",
      ...missing.map((id) => {
        const refs = usage
          .get(id)
          ?.slice(0, 10)
          .map((filePath) => toRelativePosix(repoRoot, filePath))
          .join(", ");
        return `- ${id}: ${refs ?? "<no refs>"}`;
      })
    ].join("\n")
  );
});
