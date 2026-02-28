import {
  PITCH_LAYOUT_SPLIT_PERCENT,
  PITCH_ROUTE_DOUBLE_ENGINE,
  PITCH_ROUTE_HITECH_OS,
  PITCH_ROUTE_INDUSTRIAL_FLOW,
  PITCH_ROUTE_VALUATION
} from "./constants.js";
import { PITCH_DECK_FIXTURE, PITCH_SCREEN_BY_ROUTE } from "./fixtures.js";
import {
  annualizeMonthlyValue,
  buildCycleWidgetPoints,
  buildKpiWidgets,
  defaultIndustrialValuationRange,
  formatCurrencyCompact
} from "./helpers.js";
import type {
  PitchDeck,
  PitchDoubleEngineSelectorModel,
  PitchHitechOsSelectorModel,
  PitchIndustrialFlowSelectorModel,
  PitchScreen,
  PitchScreenRoute,
  PitchSelectorsBundle,
  PitchValuationSelectorModel
} from "./types.js";

export function selectPitchDeck(): PitchDeck {
  return PITCH_DECK_FIXTURE;
}

export function selectPitchScreenByRoute(route: PitchScreenRoute): PitchScreen {
  return PITCH_SCREEN_BY_ROUTE[route];
}

export function selectPitchScreensInOrder(): readonly PitchScreen[] {
  return PITCH_DECK_FIXTURE.screens;
}

export function selectPitchScreen01(): PitchDoubleEngineSelectorModel {
  const screen = selectPitchScreenByRoute(PITCH_ROUTE_DOUBLE_ENGINE);
  if (screen.id !== "double-engine") {
    throw new Error("Invariant violation: /pitch/01-double-engine must map to double-engine");
  }

  return {
    route: screen.route,
    title: screen.title,
    split: {
      leftPercent: PITCH_LAYOUT_SPLIT_PERCENT,
      rightPercent: PITCH_LAYOUT_SPLIT_PERCENT
    },
    motors: [
      {
        slot: "left",
        widthPercent: 50,
        motorId: "motor1",
        title: "Motor 1",
        bullets: screen.columns.left,
        microcopy: screen.microcopy.left
      },
      {
        slot: "right",
        widthPercent: 50,
        motorId: "motor2",
        title: "Motor 2",
        bullets: screen.columns.right,
        microcopy: screen.microcopy.right
      }
    ],
    implicitMessage: screen.implicitMessage
  };
}

export function selectPitchScreen02(): PitchIndustrialFlowSelectorModel {
  const screen = selectPitchScreenByRoute(PITCH_ROUTE_INDUSTRIAL_FLOW);
  if (screen.id !== "industrial-flow") {
    throw new Error("Invariant violation: /pitch/02-industrial-flow must map to industrial-flow");
  }

  const annualProfitUsd = annualizeMonthlyValue(screen.kpis.monthlyProfitUsd);

  return {
    route: screen.route,
    title: screen.title,
    kpiWidgets: buildKpiWidgets(screen.kpis),
    cycleWidget: {
      months: screen.cycle.months,
      statement: screen.cycle.statement,
      resetBehavior: "automatic",
      points: buildCycleWidgetPoints({
        totalModules: screen.kpis.totalModules,
        monthlyModules: screen.kpis.monthlyModules,
        monthsToProject: screen.cycle.months
      })
    },
    annualization: {
      monthlyProfitUsd: screen.kpis.monthlyProfitUsd,
      annualProfitUsd,
      annualProfitDisplay: formatCurrencyCompact(annualProfitUsd)
    },
    microcopy: screen.microcopy
  };
}

export function selectPitchScreen03(): PitchHitechOsSelectorModel {
  const screen = selectPitchScreenByRoute(PITCH_ROUTE_HITECH_OS);
  if (screen.id !== "hitech-os") {
    throw new Error("Invariant violation: /pitch/03-hitech-os must map to hitech-os");
  }

  return {
    route: screen.route,
    title: screen.title,
    features: screen.bullets.map((label, index) => ({
      id: `feature-${String(index + 1).padStart(2, "0")}`,
      label
    })),
    strongPhrase: screen.strongPhrase
  };
}

export function selectPitchScreen04(): PitchValuationSelectorModel {
  const screen = selectPitchScreenByRoute(PITCH_ROUTE_VALUATION);
  if (screen.id !== "valuation") {
    throw new Error("Invariant violation: /pitch/04-valuation must map to valuation");
  }

  return {
    route: screen.route,
    title: screen.title,
    blocks: {
      blockOne: screen.blockOne,
      blockTwo: screen.blockTwo,
      combinedLine: screen.combinedLine,
      blockThree: screen.blockThree
    },
    table: {
      headers: screen.table.headers,
      rows: screen.table.rows
    },
    impliedIndustrialValuation: defaultIndustrialValuationRange()
  };
}

export function selectPitchBundle(): PitchSelectorsBundle {
  return {
    byRoute: PITCH_SCREEN_BY_ROUTE,
    orderedScreens: selectPitchScreensInOrder(),
    screen01: selectPitchScreen01(),
    screen02: selectPitchScreen02(),
    screen03: selectPitchScreen03(),
    screen04: selectPitchScreen04()
  };
}
