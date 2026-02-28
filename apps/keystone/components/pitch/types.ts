import type {
  PitchDeck,
  PitchNavigationLink,
  PitchScreen,
  PitchScreen01,
  PitchScreen02,
  PitchScreen03,
  PitchScreen04
} from "@hitech/contracts";

export interface PitchRouteParams {
  readonly searchParams?: Record<string, string | string[] | undefined>;
}

export interface PitchScreenPageProps {
  readonly deck: PitchDeck;
  readonly screen: PitchScreen;
}

export interface PitchHeaderModel {
  readonly title: string;
  readonly subtitle?: string;
  readonly eyebrow?: string;
  readonly orderLabel?: string;
}

export interface PitchNavModel {
  readonly links: readonly PitchNavigationLink[];
  readonly activeSlug?: PitchScreen["slug"];
}

export interface EngineColumnModel {
  readonly heading: string;
  readonly bullets: readonly string[];
  readonly microcopy: readonly string[];
}

export interface DoubleEngineScreenModel {
  readonly title: string;
  readonly left: EngineColumnModel;
  readonly right: EngineColumnModel;
  readonly implicitMessage: string;
}

export interface IndustrialFlowScreenModel {
  readonly title: string;
  readonly kpis: ReadonlyArray<{ label: string; value: string; note?: string }>;
  readonly cycleLabel: string;
  readonly microcopy: string;
}

export interface HiTechOsScreenModel {
  readonly title: string;
  readonly features: readonly string[];
  readonly strongLine: string;
}

export interface ValuationScreenModel {
  readonly title: string;
  readonly blocks: ReadonlyArray<{
    heading: string;
    items: readonly string[];
    phase1?: string;
    phase2?: string;
  }>;
  readonly combinedLine: string;
  readonly comparisonHeaders: readonly string[];
  readonly comparisonRows: ReadonlyArray<readonly string[]>;
}

export function toDoubleEngineModel(screen: PitchScreen01): DoubleEngineScreenModel {
  return {
    title: screen.title,
    left: {
      heading: screen.leftColumn.heading,
      bullets: screen.leftColumn.bullets.map((entry) => entry.text),
      microcopy: screen.leftColumn.microcopy.map((entry) => entry.text)
    },
    right: {
      heading: screen.rightColumn.heading,
      bullets: screen.rightColumn.bullets.map((entry) => entry.text),
      microcopy: screen.rightColumn.microcopy.map((entry) => entry.text)
    },
    implicitMessage: screen.implicitMessage.text
  };
}

export function toIndustrialFlowModel(screen: PitchScreen02): IndustrialFlowScreenModel {
  return {
    title: screen.title,
    kpis: screen.kpis.map((kpi) => ({
      label: kpi.label,
      value: kpi.value,
      ...(kpi.note ? { note: kpi.note } : {})
    })),
    cycleLabel: screen.cycleLabel.text,
    microcopy: screen.microcopy.text
  };
}

export function toHiTechOsModel(screen: PitchScreen03): HiTechOsScreenModel {
  return {
    title: screen.title,
    features: screen.features.map((entry) => entry.text),
    strongLine: screen.strongLine.text
  };
}

export function toValuationModel(screen: PitchScreen04): ValuationScreenModel {
  return {
    title: screen.title,
    blocks: screen.blocks.map((block) => ({
      heading: block.heading,
      items: block.items.map((entry) => entry.text),
      ...(block.phase1 ? { phase1: block.phase1 } : {}),
      ...(block.phase2 ? { phase2: block.phase2 } : {})
    })),
    combinedLine: screen.combinedValuationLine.text,
    comparisonHeaders: screen.comparison.headers,
    comparisonRows: screen.comparison.rows
  };
}
