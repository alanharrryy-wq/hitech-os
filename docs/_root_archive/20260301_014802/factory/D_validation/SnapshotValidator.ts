import {
  JsonObject,
  JsonValue,
  canonicalizeJsonValue,
  isJsonObject,
} from "../shared/DeterministicJson";
import { HashProvider, hashJsonValue } from "../shared/Hashing";
import { deepFreeze } from "../shared/Immutability";

export interface SnapshotArtifact {
  readonly name: string;
  readonly hash: string;
  readonly payload: JsonObject;
}

export interface SnapshotComparisonIssue {
  readonly path: string;
  readonly expected: JsonValue | undefined;
  readonly actual: JsonValue | undefined;
}

export interface SnapshotComparisonResult {
  readonly matches: boolean;
  readonly expectedHash: string;
  readonly actualHash: string;
  readonly issues: readonly SnapshotComparisonIssue[];
}

function compareValues(
  expected: JsonValue,
  actual: JsonValue,
  pathLabel: string,
  issues: SnapshotComparisonIssue[],
): void {
  if (typeof expected !== typeof actual) {
    issues.push({ path: pathLabel, expected, actual });
    return;
  }

  if (expected === null || actual === null) {
    if (expected !== actual) {
      issues.push({ path: pathLabel, expected, actual });
    }
    return;
  }

  if (Array.isArray(expected) && Array.isArray(actual)) {
    const maxLength = Math.max(expected.length, actual.length);
    for (let index = 0; index < maxLength; index += 1) {
      const expectedValue = expected[index];
      const actualValue = actual[index];
      if (expectedValue === undefined || actualValue === undefined) {
        issues.push({
          path: `${pathLabel}[${index}]`,
          expected: expectedValue,
          actual: actualValue,
        });
        continue;
      }
      compareValues(expectedValue, actualValue, `${pathLabel}[${index}]`, issues);
    }
    return;
  }

  if (isJsonObject(expected) && isJsonObject(actual)) {
    const expectedKeys = Object.keys(expected);
    const actualKeys = Object.keys(actual);
    const allKeys = Array.from(new Set([...expectedKeys, ...actualKeys])).sort((left, right) =>
      left.localeCompare(right),
    );
    for (const key of allKeys) {
      const expectedValue = expected[key];
      const actualValue = actual[key];
      if (expectedValue === undefined || actualValue === undefined) {
        issues.push({
          path: `${pathLabel}.${key}`,
          expected: expectedValue,
          actual: actualValue,
        });
        continue;
      }
      compareValues(expectedValue, actualValue, `${pathLabel}.${key}`, issues);
    }
    return;
  }

  if (expected !== actual) {
    issues.push({ path: pathLabel, expected, actual });
  }
}

function compareIssues(
  left: SnapshotComparisonIssue,
  right: SnapshotComparisonIssue,
): number {
  return left.path.localeCompare(right.path);
}

export class SnapshotValidator {
  private readonly hasher: HashProvider;

  constructor(hasher: HashProvider) {
    this.hasher = hasher;
  }

  createSnapshot(name: string, payload: JsonObject): SnapshotArtifact {
    if (name.trim().length === 0) {
      throw new Error("Snapshot name must not be empty.");
    }
    const canonical = canonicalizeJsonValue(payload) as JsonObject;
    const hash = hashJsonValue(canonical, this.hasher);
    return deepFreeze({
      name,
      hash,
      payload: canonical,
    });
  }

  verifySnapshot(
    expectedHash: string,
    expectedPayload: JsonObject,
    actualPayload: JsonObject,
  ): SnapshotComparisonResult {
    const canonicalExpected = canonicalizeJsonValue(expectedPayload) as JsonObject;
    const canonicalActual = canonicalizeJsonValue(actualPayload) as JsonObject;
    const actualHash = hashJsonValue(canonicalActual, this.hasher);

    const issues: SnapshotComparisonIssue[] = [];
    compareValues(canonicalExpected, canonicalActual, "$", issues);
    const sortedIssues = issues.sort(compareIssues);
    return {
      matches: expectedHash === actualHash && sortedIssues.length === 0,
      expectedHash,
      actualHash,
      issues: sortedIssues,
    };
  }
}
