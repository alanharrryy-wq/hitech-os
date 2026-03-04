import { isoUtcNow } from "../shared/deterministic.js";
import { parseSequence } from "./sequence-schema.js";
import { SEQUENCE_SCHEMA_VERSION } from "./dsl.js";
import type { DirectorSequence, SequenceMigrationResult } from "./sequence-types.js";

function getRawObject(input: unknown): Record<string, unknown> {
  if (input && typeof input === "object" && !Array.isArray(input)) {
    return input as Record<string, unknown>;
  }

  return {};
}

export function detectSequenceVersion(input: unknown): number | "unknown" {
  const raw = getRawObject(input);
  const schemaVersion = raw.schemaVersion;

  if (typeof schemaVersion === "number" && Number.isInteger(schemaVersion) && schemaVersion > 0) {
    return schemaVersion;
  }

  return "unknown";
}

export function migrateSequenceToV1(input: unknown): SequenceMigrationResult {
  const version = detectSequenceVersion(input);

  if (version === SEQUENCE_SCHEMA_VERSION) {
    return {
      sequence: parseSequence(input),
      migrations: []
    };
  }

  const raw = getRawObject(input);
  const createdAt = typeof raw.createdAt === "string" ? raw.createdAt : isoUtcNow();
  const updatedAt = typeof raw.updatedAt === "string" ? raw.updatedAt : createdAt;

  const migratedCandidate = {
    sequenceId: typeof raw.sequenceId === "string" ? raw.sequenceId : "sequence.migrated",
    schemaVersion: SEQUENCE_SCHEMA_VERSION,
    createdAt,
    updatedAt,
    baseSceneRef: raw.baseSceneRef,
    timelineDSL: raw.timelineDSL,
    rules: raw.rules
  };

  const parsed = parseSequence(migratedCandidate);

  return {
    sequence: parsed,
    migrations: [
      {
        fromVersion: version,
        toVersion: SEQUENCE_SCHEMA_VERSION,
        notes: [
          "migration-stub: normalized schemaVersion to v1",
          "migration-stub: retained timeline DSL + rules"
        ]
      }
    ]
  };
}

export function ensureSequenceLatest(input: unknown): DirectorSequence {
  return migrateSequenceToV1(input).sequence;
}
