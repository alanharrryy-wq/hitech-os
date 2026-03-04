import {
  canonicalizePitchProgram,
  deserializePitchProgram,
  serializePitchProgram
} from "./program-serializer.js";
import type { PitchProgram } from "./program-types.js";

export interface ProgramRoundtripResult {
  readonly serialized: string;
  readonly reparsed: PitchProgram;
  readonly semanticMatch: boolean;
}

export function roundtripPitchProgram(program: PitchProgram): ProgramRoundtripResult {
  const serialized = serializePitchProgram(program);
  const reparsed = deserializePitchProgram(serialized);

  const sourceCanonical = canonicalizePitchProgram(program);
  const reparsedCanonical = canonicalizePitchProgram(reparsed);

  return {
    serialized,
    reparsed,
    semanticMatch: serializePitchProgram(sourceCanonical) === serializePitchProgram(reparsedCanonical)
  };
}

export function assertProgramRoundtrip(program: PitchProgram): void {
  const result = roundtripPitchProgram(program);
  if (!result.semanticMatch) {
    throw new Error("Program roundtrip did not preserve semantics");
  }
}
