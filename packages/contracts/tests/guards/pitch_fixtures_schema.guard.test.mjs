import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

function resolveRepoRoot() {
  return path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../../../");
}

function walkFiles(rootDir) {
  if (!fs.existsSync(rootDir)) {
    return [];
  }

  const stack = [rootDir];
  const files = [];

  while (stack.length > 0) {
    const current = stack.pop();
    if (!current) {
      continue;
    }

    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const absPath = path.join(current, entry.name);

      if (entry.isDirectory()) {
        if (entry.name === "dist" || entry.name === "node_modules") {
          continue;
        }
        stack.push(absPath);
        continue;
      }

      if (entry.isFile()) {
        files.push(absPath);
      }
    }
  }

  return files.sort((left, right) => left.localeCompare(right));
}

const repoRoot = resolveRepoRoot();
const contractsRoot = path.join(repoRoot, "packages/contracts");
const generatedSchemasDir = path.join(contractsRoot, "schemas/generated");
const fixtureRoots = [path.join(contractsRoot, "src/fixtures"), path.join(contractsRoot, "fixtures")];

const schemaCandidates = walkFiles(generatedSchemasDir).filter(
  (filePath) => filePath.endsWith(".json") && /pitch/i.test(path.basename(filePath))
);

const fixtureCandidates = fixtureRoots
  .flatMap((rootDir) => walkFiles(rootDir))
  .filter((filePath) => filePath.endsWith(".json") && /pitch/i.test(path.basename(filePath)));

const skipReason =
  schemaCandidates.length === 0
    ? "No pitch JSON schema found yet in packages/contracts/schemas/generated"
    : fixtureCandidates.length === 0
      ? "No pitch fixtures found yet in packages/contracts fixtures folders"
      : null;

test("pitch fixture/schema guard dependency probe", () => {
  assert.ok(true, skipReason ?? "pitch schema + fixtures present");
});

test(
  "pitch fixtures parse against pitch JSON schema (when present)",
  { skip: skipReason ?? false },
  async () => {
    const { default: Ajv } = await import("ajv");

    const schemaPath = schemaCandidates[0];
    if (!schemaPath) {
      throw new Error("Schema path disappeared after dependency probe");
    }

    const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));
    const ajv = new Ajv({
      allErrors: true,
      strict: false,
      allowUnionTypes: true,
      validateFormats: true
    });

    const validate = ajv.compile(schema);

    for (const fixturePath of fixtureCandidates) {
      const raw = fs.readFileSync(fixturePath, "utf8");
      const parsed = JSON.parse(raw);

      const variants = Array.isArray(parsed) ? parsed : [parsed];

      for (const payload of variants) {
        const valid = validate(payload);
        assert.equal(
          valid,
          true,
          [
            `Schema: ${path.relative(repoRoot, schemaPath)}`,
            `Fixture: ${path.relative(repoRoot, fixturePath)}`,
            "Errors:",
            ...(validate.errors ?? []).map((entry) => `${entry.instancePath} ${entry.message}`)
          ].join("\n")
        );
      }
    }
  }
);
