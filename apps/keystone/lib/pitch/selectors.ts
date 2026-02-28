import type { JobResult } from '@hitech/contracts';
import { PITCH_DECK_FIXTURES } from './deck';
import { toQueryString } from './query';
import type {
  DoubleEngineViewModel,
  HitechOsViewModel,
  IndustrialFlowViewModel,
  PitchIndexViewModel,
  PitchQueryState,
  PitchRouteId,
  PitchRouteNavigation,
  PitchRouteNavItem,
  ValuationViewModel,
} from './types';

function toHref(slug: string, query: PitchQueryState): string {
  const queryString = toQueryString(query);
  return queryString.length > 0 ? `${slug}?${queryString}` : slug;
}

function sortByOrder<T extends { readonly order: number }>(items: ReadonlyArray<T>): ReadonlyArray<T> {
  return [...items].sort((left, right) => left.order - right.order);
}

function mapRouteToNavItem(
  route: (typeof PITCH_DECK_FIXTURES.routes)[number],
  currentId: PitchRouteId,
  query: PitchQueryState,
): PitchRouteNavItem {
  return {
    id: route.id,
    href: toHref(route.slug, query),
    title: route.title,
    subtitle: route.subtitle,
    order: route.order,
    isCurrent: route.id === currentId,
  };
}

function findCurrentRoute(currentId: PitchRouteId): (typeof PITCH_DECK_FIXTURES.routes)[number] {
  const current = PITCH_DECK_FIXTURES.routes.find((route) => route.id === currentId);
  if (!current) {
    throw new Error(`Unknown route id: ${currentId}`);
  }
  return current;
}

function groupResultsByStatus(results: ReadonlyArray<JobResult>): Record<string, number> {
  const summary: Record<string, number> = {
    queued: 0,
    running: 0,
    completed: 0,
    failed: 0,
  };

  for (const result of results) {
    summary[result.status] = (summary[result.status] ?? 0) + 1;
  }

  return summary;
}

function percentage(part: number, whole: number): number {
  if (whole === 0) {
    return 0;
  }
  return Number(((part / whole) * 100).toFixed(1));
}

function withRouteHref<T extends { readonly id: PitchRouteId; readonly title: string; readonly subtitle: string; readonly order: number }>(
  routes: ReadonlyArray<T>,
  query: PitchQueryState,
): ReadonlyArray<T & { readonly href: string }> {
  return routes.map((route) => ({
    ...route,
    href: toHref(route.id === 'pitch-index' ? '/pitch' : `/pitch/${route.id}`, query),
  }));
}

export function selectPitchIndexViewModel(query: PitchQueryState): PitchIndexViewModel {
  const hero = {
    eyebrow: 'Pitch Deck',
    title: 'Keystone Pitch Navigation',
    subtitle:
      'Typed fixture-driven routing for chapter walkthroughs with deterministic query-state controls.',
    bullets: [
      'All chapter copy and metrics are served from typed fixture selectors.',
      'Layer mode/profile/debug are resolved server-side and propagated via provider context.',
      'Navigation links preserve query-state across chapter transitions.',
    ],
  };

  const routeCards = sortByOrder(
    PITCH_DECK_FIXTURES.routes
      .filter((route) => route.id !== 'pitch-index')
      .map((route) => ({
        id: route.id,
        title: route.title,
        subtitle: route.subtitle,
        href: toHref(route.slug, query),
        order: route.order,
      })),
  );

  return {
    hero,
    routeCards,
  };
}

export function selectRouteNavigation(
  currentId: PitchRouteId,
  query: PitchQueryState,
): PitchRouteNavigation {
  const items = sortByOrder(
    PITCH_DECK_FIXTURES.routes.map((route) => mapRouteToNavItem(route, currentId, query)),
  );

  const current = items.find((item) => item.id === currentId);
  if (!current) {
    throw new Error(`Route navigation could not find current route: ${currentId}`);
  }

  const currentIndex = items.findIndex((item) => item.id === currentId);

  return {
    current,
    items,
    prev: currentIndex > 0 ? items[currentIndex - 1] : null,
    next: currentIndex < items.length - 1 ? items[currentIndex + 1] : null,
  };
}

export function selectDoubleEngineViewModel(): DoubleEngineViewModel {
  const fixtures = PITCH_DECK_FIXTURES.doubleEngine;

  return {
    hero: fixtures.hero,
    engines: fixtures.engines,
    strategyNarrative: fixtures.strategyNarrative,
    kpiBands: fixtures.kpiBands.map((band) => ({
      ...band,
      gap: Number((band.target - band.current).toFixed(2)),
    })),
  };
}

export function selectIndustrialFlowViewModel(): IndustrialFlowViewModel {
  const fixtures = PITCH_DECK_FIXTURES.industrialFlow;

  return {
    hero: fixtures.hero,
    stages: fixtures.stages,
    processGuardrails: fixtures.processGuardrails,
    flowMetrics: fixtures.flowMetrics,
  };
}

export function selectHitechOsViewModel(): HitechOsViewModel {
  const fixtures = PITCH_DECK_FIXTURES.hitechOs;
  return {
    hero: fixtures.hero,
    modules: fixtures.modules,
    contracts: fixtures.contracts,
    reliabilityNarrative: fixtures.reliabilityNarrative,
  };
}

export function selectValuationViewModel(): ValuationViewModel {
  const fixtures = PITCH_DECK_FIXTURES.valuation;
  return {
    hero: fixtures.hero,
    contractVersion: fixtures.contractVersion,
    scenarios: fixtures.scenarios,
    riskNotes: fixtures.riskNotes,
    bridgeSeries: fixtures.bridgeSeries,
  };
}

export function selectIndustrialFlowStatusCards(): ReadonlyArray<{
  readonly id: string;
  readonly stage: string;
  readonly total: number;
  readonly completed: number;
  readonly running: number;
  readonly failed: number;
  readonly completionRate: number;
}> {
  return PITCH_DECK_FIXTURES.industrialFlow.stages.map((stage) => {
    const summary = groupResultsByStatus(stage.results);
    const total = stage.results.length;
    const completed = summary.completed;
    const running = summary.running;
    const failed = summary.failed;

    return {
      id: stage.id,
      stage: stage.name,
      total,
      completed,
      running,
      failed,
      completionRate: percentage(completed, total),
    };
  });
}

export function selectEngineScoreboard(): ReadonlyArray<{
  readonly id: string;
  readonly name: string;
  readonly profile: string;
  readonly fitScore: number;
  readonly opexIndex: number;
  readonly throughputIndex: number;
  readonly riskIndex: number;
  readonly headroom: number;
  readonly efficiencyBand: 'high' | 'medium' | 'low';
}> {
  return PITCH_DECK_FIXTURES.doubleEngine.engines.map((engine) => {
    const headroom = Number((100 - engine.fitScore).toFixed(1));
    const efficiency = engine.throughputIndex - engine.opexIndex;
    const efficiencyBand = efficiency > 18 ? 'high' : efficiency > 5 ? 'medium' : 'low';

    return {
      id: engine.id,
      name: engine.name,
      profile: engine.profile,
      fitScore: engine.fitScore,
      opexIndex: engine.opexIndex,
      throughputIndex: engine.throughputIndex,
      riskIndex: engine.riskIndex,
      headroom,
      efficiencyBand,
    };
  });
}

export function selectValuationLeaderboard(): ReadonlyArray<{
  readonly id: string;
  readonly label: string;
  readonly multiple: number;
  readonly revenueRunRateM: number;
  readonly confidence: number;
  readonly impliedValueM: number;
  readonly confidenceWeightedValueM: number;
}> {
  return [...PITCH_DECK_FIXTURES.valuation.scenarios]
    .map((scenario) => {
      const impliedValueM = Number((scenario.multiple * scenario.revenueRunRateM).toFixed(2));
      const confidenceWeightedValueM = Number(
        (impliedValueM * (scenario.confidence / 100)).toFixed(2),
      );

      return {
        id: scenario.id,
        label: scenario.label,
        multiple: scenario.multiple,
        revenueRunRateM: scenario.revenueRunRateM,
        confidence: scenario.confidence,
        impliedValueM,
        confidenceWeightedValueM,
      };
    })
    .sort((left, right) => right.confidenceWeightedValueM - left.confidenceWeightedValueM);
}

export function selectHitechOsHealthMatrix(): ReadonlyArray<{
  readonly id: string;
  readonly label: string;
  readonly owner: string;
  readonly status: string;
  readonly checks: number;
  readonly timestampUtc: string;
}> {
  return PITCH_DECK_FIXTURES.hitechOs.modules.map((module) => ({
    id: module.id,
    label: module.label,
    owner: module.owner,
    status: module.health.status,
    checks: module.health.checks.length,
    timestampUtc: module.health.timestampUtc,
  }));
}

export function selectRouteCardsForRail(query: PitchQueryState): ReadonlyArray<{
  readonly id: PitchRouteId;
  readonly title: string;
  readonly subtitle: string;
  readonly href: string;
  readonly order: number;
}> {
  return withRouteHref(PITCH_DECK_FIXTURES.routes, query).map((route) => ({
    id: route.id,
    title: route.title,
    subtitle: route.subtitle,
    href: route.href,
    order: route.order,
  }));
}

export function selectCurrentRouteMeta(routeId: PitchRouteId) {
  return findCurrentRoute(routeId);
}

export function selectRouteQueryExamples(routeId: PitchRouteId): ReadonlyArray<{
  readonly id: string;
  readonly label: string;
  readonly href: string;
}> {
  const route = findCurrentRoute(routeId);

  return [
    {
      id: `${routeId}-neutral-all`,
      label: 'Neutral / All Layers',
      href: toHref(route.slug, { layers: 'all', layerProfile: 'neutral', debug: '0' }),
    },
    {
      id: `${routeId}-fx-list`,
      label: 'FX / List Mode',
      href: `${route.slug}?layers=list&layerProfile=fx&layerList=surfaceBase,glassTint,chartGlow,motionPanels&debug=0`,
    },
    {
      id: `${routeId}-perf-debug`,
      label: 'Perf / Debug',
      href: toHref(route.slug, { layers: 'all', layerProfile: 'perf', debug: '1' }),
    },
  ];
}

export function buildDefaultPitchQueryState(
  seed?: Partial<PitchQueryState>,
): PitchQueryState {
  return {
    layers: seed?.layers ?? 'all',
    layerProfile: seed?.layerProfile ?? 'neutral',
    debug: seed?.debug ?? '0',
  };
}

export function selectIndustrialFlowRequestVolumeByStage(): ReadonlyArray<{
  readonly id: string;
  readonly name: string;
  readonly requestCount: number;
  readonly resultCount: number;
  readonly pendingCount: number;
}> {
  return PITCH_DECK_FIXTURES.industrialFlow.stages.map((stage) => {
    const requestCount = stage.requests.length;
    const resultCount = stage.results.length;
    const pendingCount = Math.max(0, requestCount - resultCount);

    return {
      id: stage.id,
      name: stage.name,
      requestCount,
      resultCount,
      pendingCount,
    };
  });
}

export function selectValuationBridgeTotals(): {
  readonly totalDeltaM: number;
  readonly positiveDeltaM: number;
  readonly negativeDeltaM: number;
} {
  const steps = PITCH_DECK_FIXTURES.valuation.bridgeSeries;
  const totalDeltaM = Number(steps.reduce((sum, step) => sum + step.deltaM, 0).toFixed(2));
  const positiveDeltaM = Number(
    steps
      .filter((step) => step.deltaM > 0)
      .reduce((sum, step) => sum + step.deltaM, 0)
      .toFixed(2),
  );
  const negativeDeltaM = Number(
    steps
      .filter((step) => step.deltaM < 0)
      .reduce((sum, step) => sum + step.deltaM, 0)
      .toFixed(2),
  );

  return {
    totalDeltaM,
    positiveDeltaM,
    negativeDeltaM,
  };
}

export function selectEngineCapabilityNotes(): ReadonlyArray<{
  readonly id: string;
  readonly name: string;
  readonly notes: ReadonlyArray<string>;
}> {
  return PITCH_DECK_FIXTURES.doubleEngine.engines.map((engine) => ({
    id: engine.id,
    name: engine.name,
    notes: engine.capabilities.notes,
  }));
}

export function selectHitechOsModuleIO(): ReadonlyArray<{
  readonly id: string;
  readonly label: string;
  readonly inputs: ReadonlyArray<string>;
  readonly outputs: ReadonlyArray<string>;
}> {
  return PITCH_DECK_FIXTURES.hitechOs.modules.map((module) => ({
    id: module.id,
    label: module.label,
    inputs: module.inputs,
    outputs: module.outputs,
  }));
}

export function selectValuationScenarioBands(): ReadonlyArray<{
  readonly id: string;
  readonly label: string;
  readonly band: 'core' | 'stretch' | 'defensive';
  readonly confidence: number;
}> {
  return PITCH_DECK_FIXTURES.valuation.scenarios.map((scenario) => ({
    id: scenario.id,
    label: scenario.label,
    band:
      scenario.confidence >= 78
        ? 'core'
        : scenario.confidence >= 62
          ? 'stretch'
          : 'defensive',
    confidence: scenario.confidence,
  }));
}

export function selectAllSummaryCounters() {
  const engines = PITCH_DECK_FIXTURES.doubleEngine.engines.length;
  const stageCount = PITCH_DECK_FIXTURES.industrialFlow.stages.length;
  const moduleCount = PITCH_DECK_FIXTURES.hitechOs.modules.length;
  const scenarioCount = PITCH_DECK_FIXTURES.valuation.scenarios.length;

  return {
    engines,
    stageCount,
    moduleCount,
    scenarioCount,
    totalSignals: engines + stageCount + moduleCount + scenarioCount,
  };
}
