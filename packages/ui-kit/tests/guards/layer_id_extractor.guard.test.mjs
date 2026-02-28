import assert from "node:assert/strict";
import { test } from "node:test";
import { LAYER_ID_SYNTAX_CASES } from "./layer_id_syntax_corpus.fixture.mjs";
import { extractLayerIdsFromText } from "./layer_id_guard_helpers.mjs";

test("layer-id extractor guard corpus stays stable", () => {
  assert.equal(LAYER_ID_SYNTAX_CASES.length, 5400, "Expected deterministic 5400-case corpus");
});

test("layer-id extractor handles JSX, attrs, and @layer syntax", () => {
  for (const scenario of LAYER_ID_SYNTAX_CASES) {
    const resolved = extractLayerIdsFromText(scenario.source);
    assert.deepEqual(
      resolved,
      scenario.expected,
      `Extractor mismatch for ${scenario.name}; source=${scenario.source}`
    );
  }
});
