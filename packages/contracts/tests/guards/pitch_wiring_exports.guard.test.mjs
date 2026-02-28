import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../../../");
const contractsIndexPath = path.join(repoRoot, "packages/contracts/src/index.ts");

test("contracts index exposes pitch wiring contract", () => {
  const content = fs.readFileSync(contractsIndexPath, "utf8");

  assert.match(content, /CONTRACT_DOMAIN_PITCH_MODULE_PATH/, "Missing domain pitch module path export");
  assert.match(content, /CONTRACT_FIXTURES_PITCH_MODULE_PATH/, "Missing fixtures pitch module path export");
  assert.match(content, /export\s+const\s+pitch\s*:/, "Missing `pitch` wiring export");
  assert.match(content, /loadDomainModule\s*:\s*\(\)\s*=>\s*import\(/, "Missing lazy domain loader");
  assert.match(content, /loadFixturesModule\s*:\s*\(\)\s*=>\s*import\(/, "Missing lazy fixtures loader");
});
