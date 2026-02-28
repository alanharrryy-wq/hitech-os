import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { extractLayerIds, findFiles, parseLayerIdsRegistry } from "./keystone_guard_helpers.mjs";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../../../");
const keystoneSrc = path.join(repoRoot, "apps/keystone/src");
const uiKitIndexPath = path.join(repoRoot, "packages/ui-kit/src/index.ts");
const uiKitStylesPath = path.join(repoRoot, "packages/ui-kit/src/styles.css");

const layerIdsCandidates = [
  path.join(repoRoot, "packages/ui-kit/src/layers/layerIds.ts"),
  path.join(repoRoot, "packages/ui-kit/src/layers/layerIds.tsx"),
  path.join(repoRoot, "packages/ui-kit/src/layerIds.ts")
];

function readIfExists(filePath) {
  return fs.existsSync(filePath) ? fs.readFileSync(filePath, "utf8") : null;
}

test("ui-kit wiring is exposed for keystone integration", () => {
  const indexContent = readIfExists(uiKitIndexPath);
  const stylesContent = readIfExists(uiKitStylesPath);

  assert.notEqual(indexContent, null, "Missing packages/ui-kit/src/index.ts");
  assert.notEqual(stylesContent, null, "Missing packages/ui-kit/src/styles.css");

  assert.match(indexContent, /export\s+const\s+layers\s*:/, "Missing layers wiring export in ui-kit index");
  assert.match(
    stylesContent,
    /@import\s+["']\.\/layers\.css["'];/,
    "Missing layers.css import in ui-kit styles.css"
  );
});

test("keystone layer IDs (when present) are declared in ui-kit registry", () => {
  if (!fs.existsSync(keystoneSrc)) {
    assert.ok(true, "apps/keystone/src is not present yet; guard stays pending without failing build");
    return;
  }

  const sourceFiles = findFiles(keystoneSrc);
  const used = new Map();

  for (const filePath of sourceFiles) {
    const ids = extractLayerIds(fs.readFileSync(filePath, "utf8"));
    for (const id of ids) {
      const hits = used.get(id) ?? [];
      hits.push(path.relative(repoRoot, filePath));
      used.set(id, hits);
    }
  }

  const usedIds = [...used.keys()].sort((left, right) => left.localeCompare(right));

  const layerIdsPath = layerIdsCandidates.find((candidate) => fs.existsSync(candidate)) ?? null;
  if (!layerIdsPath) {
    assert.equal(
      usedIds.length,
      0,
      [
        "Keystone uses layer IDs but no ui-kit static registry was found.",
        "Expected registry candidates:",
        ...layerIdsCandidates.map((candidate) => `- ${path.relative(repoRoot, candidate)}`),
        "Detected layer IDs:",
        ...usedIds.map((id) => `- ${id}: ${(used.get(id) ?? []).join(", ")}`)
      ].join("\n")
    );
    return;
  }

  const registryIds = parseLayerIdsRegistry(fs.readFileSync(layerIdsPath, "utf8"));
  const registrySet = new Set(registryIds);
  const missing = usedIds.filter((id) => !registrySet.has(id));

  assert.deepEqual(
    missing,
    [],
    [
      `Registry: ${path.relative(repoRoot, layerIdsPath)}`,
      "Layer IDs used in apps/keystone/src but missing in static list:",
      ...missing.map((id) => `- ${id}: ${(used.get(id) ?? []).join(", ")}`)
    ].join("\n")
  );
});
