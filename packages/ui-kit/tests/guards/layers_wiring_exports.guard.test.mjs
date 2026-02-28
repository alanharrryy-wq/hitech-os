import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../../../");
const uiKitIndexPath = path.join(repoRoot, "packages/ui-kit/src/index.ts");
const uiKitStylesPath = path.join(repoRoot, "packages/ui-kit/src/styles.css");

test("ui-kit barrel exposes layers wiring and core components", () => {
  const indexText = fs.readFileSync(uiKitIndexPath, "utf8");

  assert.match(indexText, /UI_KIT_REQUIRED_COMPONENT_EXPORTS/);
  assert.match(indexText, /UI_KIT_LAYERS_MODULE_PATH/);
  assert.match(indexText, /UI_KIT_LAYERS_IDS_MODULE_PATH/);
  assert.match(indexText, /UI_KIT_LAYERS_CSS_PATH/);
  assert.match(indexText, /export\s+const\s+layers\s*:/);
});

test("ui-kit styles import layers.css", () => {
  const stylesText = fs.readFileSync(uiKitStylesPath, "utf8");
  assert.match(stylesText, /@import\s+["']\.\/layers\.css["'];/);
});
