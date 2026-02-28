import type {
  PITCH_SCREEN_IDS,
  PITCH_SCREEN_ROUTES,
  PITCH_VALUATION_TABLE_HEADERS,
  PITCH_VALUATION_TABLE_ROWS
} from "./constants.js";

export type PitchDomainId = "pitch";
export type PitchScreenId = (typeof PITCH_SCREEN_IDS)[number];
export type PitchScreenRoute = (typeof PITCH_SCREEN_ROUTES)[number];

export interface PitchDeck {
  readonly domain: PitchDomainId;
  readonly version: string;
  readonly screens: readonly [
    PitchDoubleEngineScreen,
    PitchIndustrialFlowScreen,
    PitchHitechOsScreen,
    PitchValuationScreen
  ];
}

export interface PitchScreenBase<TId extends PitchScreenId, TRoute extends PitchScreenRoute> {
  readonly id: TId;
  readonly route: TRoute;
  readonly title: string;
}

export interface PitchDoubleEngineScreen extends PitchScreenBase<"double-engine", "/pitch/01-double-engine"> {
  readonly columns: {
    readonly left: readonly string[];
    readonly right: readonly string[];
  };
  readonly microcopy: {
    readonly left: string;
    readonly right: string;
  };
  readonly implicitMessage: string;
}

export interface PitchIndustrialFlowKpis {
  readonly totalModules: number;
  readonly monthlyModules: number;
  readonly monthlyBillingUsd: number;
  readonly monthlyProfitUsd: number;
  readonly annualProfitUsd: number;
  readonly annualProfitCompactText: string;
}

export interface PitchIndustrialFlowCycle {
  readonly months: number;
  readonly statement: string;
}

export interface PitchIndustrialFlowScreen
  extends PitchScreenBase<"industrial-flow", "/pitch/02-industrial-flow"> {
  readonly kpis: PitchIndustrialFlowKpis;
  readonly cycle: PitchIndustrialFlowCycle;
  readonly microcopy: string;
}

export interface PitchHitechOsScreen extends PitchScreenBase<"hitech-os", "/pitch/03-hitech-os"> {
  readonly bullets: readonly string[];
  readonly strongPhrase: string;
}

export type PitchValuationTableHeader = (typeof PITCH_VALUATION_TABLE_HEADERS)[number];
export type PitchValuationTableTuple = (typeof PITCH_VALUATION_TABLE_ROWS)[number];

export interface PitchValuationTableRow {
  readonly model: PitchValuationTableTuple[0];
  readonly multiple: PitchValuationTableTuple[1];
  readonly risk: PitchValuationTableTuple[2];
  readonly scalability: PitchValuationTableTuple[3];
}

export interface PitchValuationScreen extends PitchScreenBase<"valuation", "/pitch/04-valuation"> {
  readonly blockOne: readonly string[];
  readonly blockTwo: readonly string[];
  readonly combinedLine: string;
  readonly blockThree: readonly string[];
  readonly table: {
    readonly headers: readonly PitchValuationTableHeader[];
    readonly rows: readonly PitchValuationTableRow[];
  };
}

export type PitchScreen =
  | PitchDoubleEngineScreen
  | PitchIndustrialFlowScreen
  | PitchHitechOsScreen
  | PitchValuationScreen;

export interface PitchKpiWidget {
  readonly id: "totalModules" | "monthlyModules" | "monthlyBillingUsd" | "monthlyProfitUsd" | "annualProfitUsd";
  readonly label: string;
  readonly value: string;
  readonly numericValue: number;
}

export interface PitchCycleWidgetPoint {
  readonly monthIndex: number;
  readonly monthInCycle: number;
  readonly cycleNumber: number;
  readonly modulesServicedThisMonth: number;
  readonly servicedModulesInCycle: number;
  readonly remainingModulesInCycle: number;
  readonly cycleCompleted: boolean;
}

export interface PitchValuationRange {
  readonly low: number;
  readonly high: number;
  readonly multipleLow: number;
  readonly multipleHigh: number;
}

export interface PitchMotorColumnModel {
  readonly slot: "left" | "right";
  readonly widthPercent: 50;
  readonly motorId: "motor1" | "motor2";
  readonly title: string;
  readonly bullets: readonly string[];
  readonly microcopy: string;
}

export interface PitchDoubleEngineSelectorModel {
  readonly route: "/pitch/01-double-engine";
  readonly title: string;
  readonly split: {
    readonly leftPercent: 50;
    readonly rightPercent: 50;
  };
  readonly motors: readonly [PitchMotorColumnModel, PitchMotorColumnModel];
  readonly implicitMessage: string;
}

export interface PitchIndustrialFlowSelectorModel {
  readonly route: "/pitch/02-industrial-flow";
  readonly title: string;
  readonly kpiWidgets: readonly PitchKpiWidget[];
  readonly cycleWidget: {
    readonly months: number;
    readonly statement: string;
    readonly resetBehavior: "automatic";
    readonly points: readonly PitchCycleWidgetPoint[];
  };
  readonly annualization: {
    readonly monthlyProfitUsd: number;
    readonly annualProfitUsd: number;
    readonly annualProfitDisplay: string;
  };
  readonly microcopy: string;
}

export interface PitchHitechOsSelectorModel {
  readonly route: "/pitch/03-hitech-os";
  readonly title: string;
  readonly features: readonly {
    readonly id: string;
    readonly label: string;
  }[];
  readonly strongPhrase: string;
}

export interface PitchValuationSelectorModel {
  readonly route: "/pitch/04-valuation";
  readonly title: string;
  readonly blocks: {
    readonly blockOne: readonly string[];
    readonly blockTwo: readonly string[];
    readonly combinedLine: string;
    readonly blockThree: readonly string[];
  };
  readonly table: {
    readonly headers: readonly PitchValuationTableHeader[];
    readonly rows: readonly PitchValuationTableRow[];
  };
  readonly impliedIndustrialValuation: PitchValuationRange;
}

export interface PitchSelectorsBundle {
  readonly byRoute: Record<PitchScreenRoute, PitchScreen>;
  readonly orderedScreens: readonly PitchScreen[];
  readonly screen01: PitchDoubleEngineSelectorModel;
  readonly screen02: PitchIndustrialFlowSelectorModel;
  readonly screen03: PitchHitechOsSelectorModel;
  readonly screen04: PitchValuationSelectorModel;
}

export interface PitchStringMapEntry {
  readonly key: string;
  readonly value: string;
}

export interface PitchDriftEntry {
  readonly key: string;
  readonly expected: string;
  readonly actual: string;
}

export interface PitchDriftReport {
  readonly hasDrift: boolean;
  readonly fingerprintExpected: string;
  readonly fingerprintActual: string;
  readonly mismatches: readonly PitchDriftEntry[];
}
