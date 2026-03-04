import { createHash } from "node:crypto";
import { JsonValue, stringifyCanonicalJson } from "./DeterministicJson";

export interface HashProvider {
  sha256(payload: string): string;
}

export class Sha256HashProvider implements HashProvider {
  sha256(payload: string): string {
    return createHash("sha256").update(payload, "utf8").digest("hex");
  }
}

const DEFAULT_PROVIDER = new Sha256HashProvider();

export function hashText(
  payload: string,
  provider: HashProvider = DEFAULT_PROVIDER,
): string {
  return provider.sha256(payload);
}

export function hashJsonValue(
  payload: JsonValue,
  provider: HashProvider = DEFAULT_PROVIDER,
): string {
  return hashText(stringifyCanonicalJson(payload), provider);
}

export function joinHashesDeterministically(
  hashes: readonly string[],
  provider: HashProvider = DEFAULT_PROVIDER,
): string {
  const sorted = [...hashes].sort((left, right) => left.localeCompare(right));
  const normalized = sorted.join("|");
  return hashText(normalized, provider);
}
