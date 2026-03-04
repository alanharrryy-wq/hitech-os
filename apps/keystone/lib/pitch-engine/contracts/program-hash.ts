import { stableHash } from "../shared/deterministic.js";
import type { PitchProgram } from "./program-types.js";
import { canonicalizePitchProgram } from "./program-serializer.js";

export interface ProgramHashOptions {
  readonly prefix?: string;
}

export function hashPitchProgram(
  program: PitchProgram,
  options: ProgramHashOptions = {}
): string {
  const canonical = canonicalizePitchProgram(program);
  const digest = stableHash(canonical as never);
  const prefix = options.prefix ?? "pgm_v1";
  return `${prefix}_${digest}`;
}

export function compareProgramHashes(left: PitchProgram, right: PitchProgram): boolean {
  return hashPitchProgram(left) === hashPitchProgram(right);
}
