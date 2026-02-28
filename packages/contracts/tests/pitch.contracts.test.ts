import { strict as assert } from "node:assert";
import { test } from "node:test";
import {
  PITCH_DOUBLE_ENGINE_TITLE,
  PITCH_HITECH_OS_TITLE,
  PITCH_INDUSTRIAL_FLOW_ANNUAL_PROFIT_USD,
  PITCH_INDUSTRIAL_FLOW_CYCLE_MONTHS,
  PITCH_INDUSTRIAL_FLOW_MONTHLY_PROFIT_USD,
  PITCH_INDUSTRIAL_FLOW_TITLE,
  PITCH_ROUTE_DOUBLE_ENGINE,
  PITCH_ROUTE_HITECH_OS,
  PITCH_ROUTE_INDUSTRIAL_FLOW,
  PITCH_ROUTE_VALUATION,
  PITCH_VALUATION_TITLE
} from "../src/domain/pitch/constants.js";
import {
  assertPitchDeckMatchesFixture,
  collectPitchStringMap,
  comparePitchDeckAgainstFixture,
  createPitchCopyFingerprint
} from "../src/domain/pitch/driftGuard.js";
import { PITCH_DECK_FIXTURE } from "../src/domain/pitch/fixtures.js";
import {
  annualizeMonthlyValue,
  buildCycleWidgetPoints,
  buildKpiWidgets,
  computeMonthsToCoverModules,
  normalizePitchText
} from "../src/domain/pitch/helpers.js";
import { parsePitchDeck, safeParsePitchDeck } from "../src/domain/pitch/schemas.js";
import {
  selectPitchBundle,
  selectPitchDeck,
  selectPitchScreen01,
  selectPitchScreen02,
  selectPitchScreen03,
  selectPitchScreen04,
  selectPitchScreenByRoute
} from "../src/domain/pitch/selectors.js";

function collectStrings(input: unknown, output: string[] = []): string[] {
  if (typeof input === "string") {
    output.push(input);
    return output;
  }
  if (Array.isArray(input)) {
    for (const item of input) {
      collectStrings(item, output);
    }
    return output;
  }
  if (input && typeof input === "object") {
    for (const value of Object.values(input)) {
      collectStrings(value, output);
    }
  }
  return output;
}

test("fixtures parse with strong schema", () => {
  const parsed = parsePitchDeck(PITCH_DECK_FIXTURE);
  assert.equal(parsed.screens.length, 4);

  const safe = safeParsePitchDeck(PITCH_DECK_FIXTURE);
  assert.equal(safe.success, true);
});

test("fixtures have no empty strings", () => {
  const values = collectStrings(PITCH_DECK_FIXTURE);
  assert.ok(values.length > 0);
  for (const value of values) {
    assert.notEqual(value.trim(), "");
  }
});

test("helpers annualization returns expected value", () => {
  assert.equal(annualizeMonthlyValue(PITCH_INDUSTRIAL_FLOW_MONTHLY_PROFIT_USD), PITCH_INDUSTRIAL_FLOW_ANNUAL_PROFIT_USD);
});

test("helpers build cycle points for 35-month cycle", () => {
  const months = computeMonthsToCoverModules(420, 12);
  assert.equal(months, 35);

  const points = buildCycleWidgetPoints({
    totalModules: 420,
    monthlyModules: 12,
    monthsToProject: PITCH_INDUSTRIAL_FLOW_CYCLE_MONTHS
  });

  assert.equal(points.length, 35);
  assert.equal(points[34]?.servicedModulesInCycle, 420);
  assert.equal(points[34]?.cycleCompleted, true);
});

test("selectors provide typed outputs for all screens", () => {
  const byRoute01 = selectPitchScreenByRoute(PITCH_ROUTE_DOUBLE_ENGINE);
  const byRoute02 = selectPitchScreenByRoute(PITCH_ROUTE_INDUSTRIAL_FLOW);
  const byRoute03 = selectPitchScreenByRoute(PITCH_ROUTE_HITECH_OS);
  const byRoute04 = selectPitchScreenByRoute(PITCH_ROUTE_VALUATION);

  assert.equal(byRoute01.title, PITCH_DOUBLE_ENGINE_TITLE);
  assert.equal(byRoute02.title, PITCH_INDUSTRIAL_FLOW_TITLE);
  assert.equal(byRoute03.title, PITCH_HITECH_OS_TITLE);
  assert.equal(byRoute04.title, PITCH_VALUATION_TITLE);

  const screen01 = selectPitchScreen01();
  const screen02 = selectPitchScreen02();
  const screen03 = selectPitchScreen03();
  const screen04 = selectPitchScreen04();

  assert.equal(screen01.motors.length, 2);
  assert.equal(screen01.split.leftPercent + screen01.split.rightPercent, 100);
  assert.equal(screen02.cycleWidget.points.length, 35);
  assert.equal(screen03.features.length, 7);
  assert.equal(screen04.table.rows.length, 2);

  const bundle = selectPitchBundle();
  assert.equal(bundle.orderedScreens.length, 4);
});

test("drift guard is stable for fixture", () => {
  const report = comparePitchDeckAgainstFixture(PITCH_DECK_FIXTURE);
  assert.equal(report.hasDrift, false);
  assert.equal(report.mismatches.length, 0);

  const fingerprint = createPitchCopyFingerprint(PITCH_DECK_FIXTURE);
  assert.ok(fingerprint.startsWith("pitch-copy-fingerprint-v1:"));

  assertPitchDeckMatchesFixture(PITCH_DECK_FIXTURE);
});

test("drift guard detects intentional mutation", () => {
  const mutated = {
    ...PITCH_DECK_FIXTURE,
    screens: [
      {
        ...PITCH_DECK_FIXTURE.screens[0],
        implicitMessage: "No soy proveedor. Soy software."
      },
      ...PITCH_DECK_FIXTURE.screens.slice(1)
    ]
  };

  const report = comparePitchDeckAgainstFixture(mutated);
  assert.equal(report.hasDrift, true);
  assert.ok(report.mismatches.length > 0);
  assert.throws(() => assertPitchDeckMatchesFixture(mutated));
});

test("normalization and KPI widgets are deterministic", () => {
  assert.equal(normalizePitchText("  test\n  value  "), "test value");
  const widgets = buildKpiWidgets(PITCH_DECK_FIXTURE.screens[1].kpis);
  assert.equal(widgets.length, 5);
  assert.equal(widgets[4]?.numericValue, 1092000);
});

test("deck selector returns canonical fixture", () => {
  const deck = selectPitchDeck();
  assert.equal(deck.screens[0].route, PITCH_ROUTE_DOUBLE_ENGINE);
});

test("string map has deterministic ordering after sort", () => {
  const entries = collectPitchStringMap(PITCH_DECK_FIXTURE);
  const sorted = entries.slice().sort((left, right) => left.key.localeCompare(right.key));
  for (let index = 1; index < sorted.length; index += 1) {
    assert.ok(sorted[index - 1]!.key <= sorted[index]!.key);
  }
});
