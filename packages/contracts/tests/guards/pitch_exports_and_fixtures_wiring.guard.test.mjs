import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../../../");
const contractsIndexPath = path.join(repoRoot, "packages/contracts/src/index.ts");
const fixturesIndexPath = path.join(repoRoot, "packages/contracts/src/fixtures/index.ts");

test("contracts exports fixtures wiring and pitch wiring symbols", () => {
  const contractsIndex = fs.readFileSync(contractsIndexPath, "utf8");
  const fixturesIndex = fs.readFileSync(fixturesIndexPath, "utf8");

  assert.match(contractsIndex, /export\s+\*\s+from\s+"\.\/fixtures\/index\.js";/);
  assert.match(contractsIndex, /CONTRACT_DOMAIN_PITCH_MODULE_PATH/);
  assert.match(contractsIndex, /CONTRACT_FIXTURES_MODULE_PATH/);
  assert.match(contractsIndex, /loadFixturesIndexModule/);

  assert.match(fixturesIndex, /CONTRACT_FIXTURES_PITCH_MODULE_PATH/);
  assert.match(fixturesIndex, /export\s+const\s+fixtures\s*:/);
  assert.match(fixturesIndex, /loadPitchModule\(\)\s*:\s*Promise<unknown>/);
});
