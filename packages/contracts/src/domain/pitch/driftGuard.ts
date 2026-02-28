import { PITCH_COPY_FINGERPRINT_VERSION } from "./constants.js";
import { PITCH_DECK_FIXTURE } from "./fixtures.js";
import { normalizePitchText } from "./helpers.js";
import type { PitchDeck, PitchDriftEntry, PitchDriftReport, PitchStringMapEntry } from "./types.js";

function pushString(entries: PitchStringMapEntry[], key: string, value: string): void {
  entries.push({ key, value: normalizePitchText(value) });
}

export function collectPitchStringMap(deck: PitchDeck): readonly PitchStringMapEntry[] {
  const entries: PitchStringMapEntry[] = [];

  pushString(entries, "domain", deck.domain);
  pushString(entries, "version", deck.version);

  for (let index = 0; index < deck.screens.length; index += 1) {
    const screen = deck.screens[index];
    pushString(entries, `screen.${index}.id`, screen.id);
    pushString(entries, `screen.${index}.route`, screen.route);
    pushString(entries, `screen.${index}.title`, screen.title);

    if (screen.id === "double-engine") {
      for (let bulletIndex = 0; bulletIndex < screen.columns.left.length; bulletIndex += 1) {
        pushString(entries, `screen.${index}.columns.left.${bulletIndex}`, screen.columns.left[bulletIndex]);
      }
      for (let bulletIndex = 0; bulletIndex < screen.columns.right.length; bulletIndex += 1) {
        pushString(entries, `screen.${index}.columns.right.${bulletIndex}`, screen.columns.right[bulletIndex]);
      }
      pushString(entries, `screen.${index}.microcopy.left`, screen.microcopy.left);
      pushString(entries, `screen.${index}.microcopy.right`, screen.microcopy.right);
      pushString(entries, `screen.${index}.implicitMessage`, screen.implicitMessage);
      continue;
    }

    if (screen.id === "industrial-flow") {
      pushString(entries, `screen.${index}.kpis.annualProfitCompactText`, screen.kpis.annualProfitCompactText);
      pushString(entries, `screen.${index}.cycle.statement`, screen.cycle.statement);
      pushString(entries, `screen.${index}.microcopy`, screen.microcopy);
      continue;
    }

    if (screen.id === "hitech-os") {
      for (let bulletIndex = 0; bulletIndex < screen.bullets.length; bulletIndex += 1) {
        pushString(entries, `screen.${index}.bullets.${bulletIndex}`, screen.bullets[bulletIndex]);
      }
      pushString(entries, `screen.${index}.strongPhrase`, screen.strongPhrase);
      continue;
    }

    for (let lineIndex = 0; lineIndex < screen.blockOne.length; lineIndex += 1) {
      pushString(entries, `screen.${index}.blockOne.${lineIndex}`, screen.blockOne[lineIndex]);
    }
    for (let lineIndex = 0; lineIndex < screen.blockTwo.length; lineIndex += 1) {
      pushString(entries, `screen.${index}.blockTwo.${lineIndex}`, screen.blockTwo[lineIndex]);
    }
    pushString(entries, `screen.${index}.combinedLine`, screen.combinedLine);
    for (let lineIndex = 0; lineIndex < screen.blockThree.length; lineIndex += 1) {
      pushString(entries, `screen.${index}.blockThree.${lineIndex}`, screen.blockThree[lineIndex]);
    }

    for (let rowIndex = 0; rowIndex < screen.table.rows.length; rowIndex += 1) {
      const row = screen.table.rows[rowIndex];
      pushString(entries, `screen.${index}.table.rows.${rowIndex}.model`, row.model);
      pushString(entries, `screen.${index}.table.rows.${rowIndex}.multiple`, row.multiple);
      pushString(entries, `screen.${index}.table.rows.${rowIndex}.risk`, row.risk);
      pushString(entries, `screen.${index}.table.rows.${rowIndex}.scalability`, row.scalability);
    }
  }

  return entries;
}

function fnv1a32(value: string): string {
  let hash = 0x811c9dc5;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 0x01000193);
  }
  return (hash >>> 0).toString(16).padStart(8, "0");
}

export function createPitchCopyFingerprint(deck: PitchDeck): string {
  const map = collectPitchStringMap(deck)
    .slice()
    .sort((left, right) => left.key.localeCompare(right.key));
  const payload = map.map((entry) => `${entry.key}=${entry.value}`).join("\n");
  return `${PITCH_COPY_FINGERPRINT_VERSION}:${fnv1a32(payload)}`;
}

export function comparePitchDeckAgainstFixture(deck: PitchDeck): PitchDriftReport {
  const expectedEntries = collectPitchStringMap(PITCH_DECK_FIXTURE)
    .slice()
    .sort((left, right) => left.key.localeCompare(right.key));
  const actualEntries = collectPitchStringMap(deck)
    .slice()
    .sort((left, right) => left.key.localeCompare(right.key));

  const expectedMap = new Map(expectedEntries.map((entry) => [entry.key, entry.value] as const));
  const actualMap = new Map(actualEntries.map((entry) => [entry.key, entry.value] as const));

  const allKeys = [...new Set([...expectedMap.keys(), ...actualMap.keys()])].sort((a, b) => a.localeCompare(b));
  const mismatches: PitchDriftEntry[] = [];

  for (const key of allKeys) {
    const expected = expectedMap.get(key) ?? "";
    const actual = actualMap.get(key) ?? "";
    if (expected !== actual) {
      mismatches.push({ key, expected, actual });
    }
  }

  return {
    hasDrift: mismatches.length > 0,
    fingerprintExpected: createPitchCopyFingerprint(PITCH_DECK_FIXTURE),
    fingerprintActual: createPitchCopyFingerprint(deck),
    mismatches
  };
}

export function assertPitchDeckMatchesFixture(deck: PitchDeck): void {
  const report = comparePitchDeckAgainstFixture(deck);
  if (report.hasDrift) {
    const preview = report.mismatches
      .slice(0, 3)
      .map((entry) => `${entry.key}: expected="${entry.expected}" actual="${entry.actual}"`)
      .join(" | ");
    throw new Error(`Pitch drift detected: ${preview}`);
  }
}
