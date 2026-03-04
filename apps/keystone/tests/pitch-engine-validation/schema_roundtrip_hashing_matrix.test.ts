import {
  PITCH_DECK_FIXTURE,
  PITCH_DECK_RESPONSE_FIXTURE,
  createPitchScreenMatrix,
  deserializePitchDeckFromJson,
  deserializePitchDeckResponseFromJson,
  serializePitchDeckResponseToJson,
  serializePitchDeckToJson,
  validatePitchDeck,
  validatePitchDeckResponse
} from "@hitech/contracts";
import { describe, expect, it } from "vitest";
import { hashJsonValue, joinHashesDeterministically } from "../../../../factory/shared/Hashing";
import { stringifyCanonicalJson } from "../../../../factory/shared/DeterministicJson";
import {
  SCHEMA_HASH_SCENARIOS,
  SCHEMA_MUTATION_SCENARIOS,
  SCHEMA_ROUNDTRIP_SCENARIOS
} from "./fixtures/schema_roundtrip_hash_scenarios.generated";

function cloneDeck() {
  return JSON.parse(JSON.stringify(PITCH_DECK_FIXTURE)) as typeof PITCH_DECK_FIXTURE;
}

function setAtPath(target: any, pathExpr: string, value: unknown) {
  const parts = pathExpr.replace(/\[(\d+)\]/g, ".$1").split(".");
  let cursor = target;
  for (let i = 0; i < parts.length - 1; i += 1) {
    const key = parts[i];
    if (key === undefined) { continue; }
    if (cursor === undefined || cursor === null) {
      throw new Error(`Invalid mutation path: ${pathExpr}`);
    }
    cursor = cursor[key];
  }
  const last = parts[parts.length - 1];
  if (last !== undefined) {
    cursor[last] = value as never;
  }
}

function isDeckValid(value: unknown): boolean {
  try {
    validatePitchDeck(value);
    return true;
  } catch {
    return false;
  }
}

describe("pitch-engine schema roundtrip + hashing validation", () => {
  it("keeps route discovery matrix stable and canonical", () => {
    const matrix = createPitchScreenMatrix();
    expect(matrix).toHaveLength(4);
    expect(matrix[0]?.slug).toBe("01-double-engine");
    expect(matrix[3]?.slug).toBe("04-valuation");
  });

  for (const scenario of SCHEMA_MUTATION_SCENARIOS) {
    it(`schema mutation ${scenario.id} (${scenario.note})`, () => {
      const mutated = cloneDeck();
      setAtPath(mutated, scenario.path, scenario.value);
      const first = isDeckValid(mutated);
      const second = isDeckValid(mutated);
      expect(first).toBe(second);
      expect(typeof first).toBe("boolean");
    });
  }

  for (const scenario of SCHEMA_ROUNDTRIP_SCENARIOS) {
    it(`roundtrip ${scenario.id}`, () => {
      const jsonDeck = serializePitchDeckToJson(PITCH_DECK_FIXTURE);
      const jsonResponse = serializePitchDeckResponseToJson(PITCH_DECK_RESPONSE_FIXTURE);

      const deckPayload = scenario.includeTrailingNewline ? `${jsonDeck}\n` : jsonDeck;
      const responsePayload = scenario.normalizeWhitespace
        ? JSON.stringify(JSON.parse(jsonResponse))
        : jsonResponse;

      const deckParsed = deserializePitchDeckFromJson(deckPayload.trim());
      const responseParsed = deserializePitchDeckResponseFromJson(responsePayload);

      const deckCanonical = stringifyCanonicalJson(deckParsed);
      const responseCanonical = stringifyCanonicalJson(responseParsed);

      expect(validatePitchDeck(deckParsed)).toBeTruthy();
      expect(validatePitchDeckResponse(responseParsed)).toBeTruthy();
      expect(deckCanonical.length).toBeGreaterThan(100);
      expect(responseCanonical.length).toBeGreaterThan(100);
      expect(joinHashesDeterministically([
        hashJsonValue(deckParsed),
        hashJsonValue(responseParsed),
        hashJsonValue({ mode: scenario.cloneMode, salt: scenario.hashJoinSalt })
      ])).toHaveLength(64);
    });
  }

  for (const scenario of SCHEMA_HASH_SCENARIOS) {
    it(`hash determinism ${scenario.id}`, () => {
      const left = hashJsonValue(scenario.left as any);
      const right = hashJsonValue(scenario.right as any);
      expect(left).toBe(right);
      expect(left).toHaveLength(64);
      const joinedA = joinHashesDeterministically(scenario.join);
      const joinedB = joinHashesDeterministically([...scenario.join].reverse());
      expect(joinedA).toBe(joinedB);
      expect(joinedA).toHaveLength(64);
    });
  }
});
