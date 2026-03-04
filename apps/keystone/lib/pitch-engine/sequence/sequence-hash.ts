import { stableHash } from "../shared/deterministic.js";
import type { DirectorSequence } from "./sequence-types.js";
import { canonicalizeSequence } from "./sequence-serializer.js";

export interface SequenceHashOptions {
  readonly prefix?: string;
}

export function hashSequence(sequence: DirectorSequence, options: SequenceHashOptions = {}): string {
  const canonical = canonicalizeSequence(sequence);
  const digest = stableHash(canonical as never);
  const prefix = options.prefix ?? "seq_v1";
  return `${prefix}_${digest}`;
}

export function compareSequenceHashes(left: DirectorSequence, right: DirectorSequence): boolean {
  return hashSequence(left) === hashSequence(right);
}
