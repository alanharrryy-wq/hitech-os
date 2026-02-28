import assert from "node:assert/strict";
import { test } from "node:test";
import { PITCH_COPY_PHRASE_CASES } from "./pitch_copy_phrase_corpus.generated.mjs";
import { looksLikeHumanCopy, normalizeHumanPhrase } from "./pitch_hardcode_guard_helpers.mjs";

test("pitch copy phrase corpus has expected deterministic size", () => {
  assert.equal(PITCH_COPY_PHRASE_CASES.length, 6000, "Expected deterministic phrase corpus of 6000 cases");
});

test("pitch copy phrase normalization remains deterministic", () => {
  for (const entry of PITCH_COPY_PHRASE_CASES) {
    const normalized = normalizeHumanPhrase(entry.raw);
    assert.equal(normalized, entry.normalized, `Normalization mismatch at case ${entry.id}`);
    assert.equal(looksLikeHumanCopy(entry.raw), entry.human, `Human-copy classifier mismatch at case ${entry.id}`);
  }
});
