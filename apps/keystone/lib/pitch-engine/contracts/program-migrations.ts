import { isoUtcNow } from "../shared/deterministic.js";
import { parsePitchProgram } from "./program-schema.js";
import { PITCH_PROGRAM_SCHEMA_VERSION, type PitchProgram } from "./program-types.js";

export interface ProgramMigrationRecord {
  readonly fromVersion: number | "unknown";
  readonly toVersion: number;
  readonly notes: readonly string[];
}

export interface ProgramMigrationResult {
  readonly program: PitchProgram;
  readonly migrations: readonly ProgramMigrationRecord[];
}

function getRawObject(input: unknown): Record<string, unknown> {
  if (input && typeof input === "object" && !Array.isArray(input)) {
    return input as Record<string, unknown>;
  }

  return {};
}

export function detectProgramVersion(input: unknown): number | "unknown" {
  const raw = getRawObject(input);
  const schemaVersion = raw.schemaVersion;

  if (typeof schemaVersion === "number" && Number.isInteger(schemaVersion) && schemaVersion > 0) {
    return schemaVersion;
  }

  return "unknown";
}

export function migrateProgramToV1(input: unknown): ProgramMigrationResult {
  const version = detectProgramVersion(input);

  if (version === PITCH_PROGRAM_SCHEMA_VERSION) {
    return {
      program: parsePitchProgram(input),
      migrations: []
    };
  }

  const raw = getRawObject(input);
  const fallbackCreatedAt = typeof raw.createdAt === "string" ? raw.createdAt : isoUtcNow();
  const fallbackUpdatedAt = typeof raw.updatedAt === "string" ? raw.updatedAt : fallbackCreatedAt;

  const candidate = {
    schemaVersion: PITCH_PROGRAM_SCHEMA_VERSION,
    programId: typeof raw.programId === "string" ? raw.programId : "program.migrated",
    title: typeof raw.title === "string" ? raw.title : "Migrated Program",
    description: typeof raw.description === "string" ? raw.description : undefined,
    tags: Array.isArray(raw.tags) ? raw.tags.filter((value) => typeof value === "string") : [],
    createdAt: fallbackCreatedAt,
    updatedAt: fallbackUpdatedAt,
    defaultPresetId: raw.defaultPresetId,
    chapters: raw.chapters,
    steps: Array.isArray(raw.steps) ? raw.steps : [],
    capabilityRequest: raw.capabilityRequest,
    metadata: raw.metadata
  };

  const parsed = parsePitchProgram(candidate);

  return {
    program: parsed,
    migrations: [
      {
        fromVersion: version,
        toVersion: PITCH_PROGRAM_SCHEMA_VERSION,
        notes: [
          "migration-stub: normalized missing schemaVersion to v1",
          "migration-stub: preserved known v1 fields and validated"
        ]
      }
    ]
  };
}

export function ensureProgramLatest(input: unknown): PitchProgram {
  return migrateProgramToV1(input).program;
}
