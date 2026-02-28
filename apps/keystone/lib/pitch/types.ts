import type {
  AgentCapabilities,
  ContractVersionInfo,
  FeatureFlags,
  HealthReport,
  JobRequest,
  JobResult,
} from '@hitech/contracts';

export type PitchRouteId =
  | 'pitch-index'
  | '01-double-engine'
  | '02-industrial-flow'
  | '03-hitech-os'
  | '04-valuation';

export interface PitchRouteMeta {
  readonly id: PitchRouteId;
  readonly slug: string;
  readonly title: string;
  readonly subtitle: string;
  readonly order: number;
}

export interface PitchHeroBlock {
  readonly title: string;
  readonly subtitle: string;
  readonly eyebrow: string;
  readonly bullets: ReadonlyArray<string>;
}

export interface DoubleEngineEngineCard {
  readonly id: string;
  readonly name: string;
  readonly profile: string;
  readonly fitScore: number;
  readonly opexIndex: number;
  readonly throughputIndex: number;
  readonly riskIndex: number;
  readonly capabilities: AgentCapabilities;
}

export interface DoubleEngineDataset {
  readonly hero: PitchHeroBlock;
  readonly engines: ReadonlyArray<DoubleEngineEngineCard>;
  readonly strategyNarrative: ReadonlyArray<string>;
  readonly kpiBands: ReadonlyArray<{
    readonly id: string;
    readonly label: string;
    readonly current: number;
    readonly target: number;
  }>;
}

export interface IndustrialFlowStage {
  readonly id: string;
  readonly name: string;
  readonly owner: string;
  readonly targetSlaHours: number;
  readonly requests: ReadonlyArray<JobRequest>;
  readonly results: ReadonlyArray<JobResult>;
  readonly blockers: ReadonlyArray<string>;
}

export interface IndustrialFlowDataset {
  readonly hero: PitchHeroBlock;
  readonly stages: ReadonlyArray<IndustrialFlowStage>;
  readonly processGuardrails: ReadonlyArray<string>;
  readonly flowMetrics: ReadonlyArray<{
    readonly id: string;
    readonly name: string;
    readonly value: number;
    readonly unit: string;
  }>;
}

export interface HitechOsModule {
  readonly id: string;
  readonly label: string;
  readonly owner: string;
  readonly health: HealthReport;
  readonly inputs: ReadonlyArray<string>;
  readonly outputs: ReadonlyArray<string>;
  readonly safeguards: ReadonlyArray<string>;
}

export interface HitechOsDataset {
  readonly hero: PitchHeroBlock;
  readonly modules: ReadonlyArray<HitechOsModule>;
  readonly contracts: ReadonlyArray<string>;
  readonly reliabilityNarrative: ReadonlyArray<string>;
}

export interface ValuationScenario {
  readonly id: string;
  readonly label: string;
  readonly multiple: number;
  readonly revenueRunRateM: number;
  readonly confidence: number;
  readonly assumptions: ReadonlyArray<string>;
  readonly flags: FeatureFlags;
}

export interface ValuationDataset {
  readonly hero: PitchHeroBlock;
  readonly contractVersion: ContractVersionInfo;
  readonly scenarios: ReadonlyArray<ValuationScenario>;
  readonly riskNotes: ReadonlyArray<string>;
  readonly bridgeSeries: ReadonlyArray<{
    readonly id: string;
    readonly step: string;
    readonly deltaM: number;
  }>;
}

export interface PitchDeckFixtures {
  readonly routes: ReadonlyArray<PitchRouteMeta>;
  readonly doubleEngine: DoubleEngineDataset;
  readonly industrialFlow: IndustrialFlowDataset;
  readonly hitechOs: HitechOsDataset;
  readonly valuation: ValuationDataset;
}

export type LayerMode = 'none' | 'all' | 'list';
export type LayerProfile = 'neutral' | 'fx' | 'perf';

export type LayerName =
  | 'surfaceBase'
  | 'surfaceElevated'
  | 'glassEdge'
  | 'glassTint'
  | 'chartGrid'
  | 'chartGlow'
  | 'motionMicro'
  | 'motionPanels'
  | 'perfCompact'
  | 'perfDeferred'
  | 'debugOutline'
  | 'debugMetrics';

export type LayerFlags = Readonly<Record<LayerName, boolean>>;

export interface LayerResolutionResult {
  readonly mode: LayerMode;
  readonly profile: LayerProfile;
  readonly selectedLayers: ReadonlyArray<LayerName>;
  readonly debug: boolean;
  readonly flags: LayerFlags;
  readonly queryEcho: Readonly<Record<string, string>>;
}

export interface PitchQueryState {
  readonly layers: string;
  readonly layerProfile: LayerProfile;
  readonly debug: '0' | '1';
}

export interface PitchRouteNavItem {
  readonly id: PitchRouteId;
  readonly href: string;
  readonly title: string;
  readonly subtitle: string;
  readonly order: number;
  readonly isCurrent: boolean;
}

export interface PitchRouteNavigation {
  readonly current: PitchRouteNavItem;
  readonly items: ReadonlyArray<PitchRouteNavItem>;
  readonly prev: PitchRouteNavItem | null;
  readonly next: PitchRouteNavItem | null;
}

export interface PitchIndexViewModel {
  readonly hero: PitchHeroBlock;
  readonly routeCards: ReadonlyArray<{
    readonly id: PitchRouteId;
    readonly title: string;
    readonly subtitle: string;
    readonly href: string;
    readonly order: number;
  }>;
}

export interface DoubleEngineViewModel {
  readonly hero: PitchHeroBlock;
  readonly engines: ReadonlyArray<DoubleEngineEngineCard>;
  readonly strategyNarrative: ReadonlyArray<string>;
  readonly kpiBands: ReadonlyArray<{
    readonly id: string;
    readonly label: string;
    readonly current: number;
    readonly target: number;
    readonly gap: number;
  }>;
}

export interface IndustrialFlowViewModel {
  readonly hero: PitchHeroBlock;
  readonly stages: ReadonlyArray<IndustrialFlowStage>;
  readonly processGuardrails: ReadonlyArray<string>;
  readonly flowMetrics: ReadonlyArray<{
    readonly id: string;
    readonly name: string;
    readonly value: number;
    readonly unit: string;
  }>;
}

export interface HitechOsViewModel {
  readonly hero: PitchHeroBlock;
  readonly modules: ReadonlyArray<HitechOsModule>;
  readonly contracts: ReadonlyArray<string>;
  readonly reliabilityNarrative: ReadonlyArray<string>;
}

export interface ValuationViewModel {
  readonly hero: PitchHeroBlock;
  readonly contractVersion: ContractVersionInfo;
  readonly scenarios: ReadonlyArray<ValuationScenario>;
  readonly riskNotes: ReadonlyArray<string>;
  readonly bridgeSeries: ReadonlyArray<{
    readonly id: string;
    readonly step: string;
    readonly deltaM: number;
  }>;
}
