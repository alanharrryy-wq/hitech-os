import assert from "node:assert/strict";
import path from "node:path";
import { test } from "node:test";
import {
  analyzePitchHardcodeViolations,
  collectAllowedPhrases,
  collectFiles,
  resolveRepoRoot,
  toRelativePosix
} from "./pitch_hardcode_guard_helpers.mjs";

const repoRoot = resolveRepoRoot(import.meta.url);
const pitchPageRoot = path.join(repoRoot, "apps/keystone/app/pitch");

const fixtureCandidates = [
  path.join(repoRoot, "packages/contracts/src/domain/pitch/fixtures.ts"),
  path.join(repoRoot, "packages/contracts/src/domain/pitch/constants.ts"),
  path.join(
    repoRoot,
    "tools/codex/runs/20260228_183257_093E/A_core/FILES/packages/contracts/src/domain/pitch/fixtures.ts"
  ),
  path.join(
    repoRoot,
    "tools/codex/runs/20260228_183257_093E/A_core/FILES/packages/contracts/src/domain/pitch/constants.ts"
  ),
  path.join(
    repoRoot,
    "tools/codex/runs/20260228_164549_2F73/A_core/FILES/packages/contracts/src/domain/pitch/fixtures.ts"
  ),
  path.join(
    repoRoot,
    "tools/codex/runs/20260228_164549_2F73/A_core/FILES/packages/contracts/src/domain/pitch/constants.ts"
  )
];

test("pitch pages do not hardcode copy outside contracts fixtures", () => {
  const pitchPages = collectFiles(pitchPageRoot, /\.(?:ts|tsx)$/);
  const allowed = collectAllowedPhrases(fixtureCandidates);

  if (pitchPages.length === 0) {
    assert.ok(true, "apps/keystone/app/pitch does not exist yet in this worktree");
    return;
  }

  assert.ok(
    allowed.size > 0,
    "No contract fixture phrases found; cannot validate page-copy hardcode guard deterministically"
  );

  const violations = analyzePitchHardcodeViolations({
    sourceFiles: pitchPages,
    allowedPhrases: allowed
  });

  assert.deepEqual(
    violations,
    [],
    [
      "Detected pitch page copy literals not found in contracts fixtures:",
      ...violations.slice(0, 50).map((entry) => {
        return `- ${toRelativePosix(repoRoot, entry.filePath)} :: \"${entry.literal}\"`;
      }),
      violations.length > 50 ? `... +${violations.length - 50} more` : ""
    ]
      .filter((line) => line.length > 0)
      .join("\n")
  );
});
