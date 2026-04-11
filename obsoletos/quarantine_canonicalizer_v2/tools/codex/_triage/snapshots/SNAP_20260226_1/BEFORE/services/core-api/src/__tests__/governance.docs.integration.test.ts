import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, it } from "node:test";
import {
  GOVERNANCE_STAGE_S1_REQUIREMENT_IDS,
  createGovernanceStageSnapshot
} from "../contracts/governance.ts";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "../../../..");

async function readRepoFile(relativePath: string): Promise<string> {
  return readFile(path.join(repoRoot, relativePath), "utf8");
}

describe("governance docs integration", () => {
  it("keeps stage S1 requirement IDs aligned with docs/CONTRACT headings", async () => {
    const contractText = await readRepoFile("docs/CONTRACT.md");
    const matches = [...contractText.matchAll(/^### (S1_[A-Z]+) —/gm)];
    const docIds = matches.map((match) => match[1]);

    assert.deepEqual(docIds, [...GOVERNANCE_STAGE_S1_REQUIREMENT_IDS]);
  });

  it("keeps stage S1 requirement IDs aligned with KERNEL_CONTEXT stage skeleton", async () => {
    const kernelContextText = await readRepoFile("KERNEL_CONTEXT.md");
    const stageLineMatch = kernelContextText.match(/^-\s*Stage 1:\s*(.+)$/m);
    assert.ok(stageLineMatch);
    const kernelIds = (stageLineMatch?.[1] ?? "")
      .split(",")
      .map((value) => value.trim().replace(/`/g, ""))
      .filter((value) => value.startsWith("S1_"));

    assert.deepEqual(kernelIds, [...GOVERNANCE_STAGE_S1_REQUIREMENT_IDS]);
  });

  it("exposes a stage snapshot that references docs as root authority", () => {
    const snapshot = createGovernanceStageSnapshot("S1");
    assert.ok(snapshot);
    assert.equal(
      snapshot?.requirements.every((requirement) => requirement.sourcePath === "docs/CONTRACT.md"),
      true
    );
    assert.equal(
      snapshot?.requirements.every((requirement) => requirement.sourceAnchor.startsWith("### S1_")),
      true
    );
  });
});
