import { describe, expect, it } from 'vitest';
import {
  PITCH_DECK_FIXTURES,
  selectAllSummaryCounters,
  selectDoubleEngineViewModel,
  selectEngineCapabilityNotes,
  selectEngineScoreboard,
  selectHitechOsHealthMatrix,
  selectHitechOsModuleIO,
  selectHitechOsViewModel,
  selectIndustrialFlowRequestVolumeByStage,
  selectIndustrialFlowStatusCards,
  selectIndustrialFlowViewModel,
  selectPitchIndexViewModel,
  selectRouteNavigation,
  selectRouteQueryExamples,
  selectValuationBridgeTotals,
  selectValuationLeaderboard,
  selectValuationScenarioBands,
  selectValuationViewModel,
} from '../../../lib/pitch';

describe('selector contracts', () => {
  it('index model returns all route cards except index', () => {
    const model = selectPitchIndexViewModel({
      layers: 'all',
      layerProfile: 'neutral',
      debug: '0',
    });

    expect(model.routeCards.length).toBe(PITCH_DECK_FIXTURES.routes.length - 1);
    for (const card of model.routeCards) {
      expect(card.href.startsWith('/pitch/')).toBe(true);
      expect(card.title.length).toBeGreaterThan(1);
    }
  });

  it('route navigation resolves prev and next', () => {
    const nav = selectRouteNavigation('02-industrial-flow', {
      layers: 'all',
      layerProfile: 'neutral',
      debug: '0',
    });

    expect(nav.current.id).toBe('02-industrial-flow');
    expect(nav.prev?.id).toBe('01-double-engine');
    expect(nav.next?.id).toBe('03-hitech-os');
  });

  it('double engine selector computes kpi gaps', () => {
    const model = selectDoubleEngineViewModel();
    expect(model.engines.length).toBeGreaterThan(10);

    for (const band of model.kpiBands) {
      expect(band.gap).toBeGreaterThanOrEqual(0);
      expect(band.target).toBeGreaterThanOrEqual(band.current);
    }
  });

  it('industrial flow selector exposes stages with requests and results', () => {
    const model = selectIndustrialFlowViewModel();

    expect(model.stages.length).toBeGreaterThan(4);
    for (const stage of model.stages) {
      expect(stage.requests.length).toBeGreaterThan(0);
      expect(stage.results.length).toBeGreaterThan(0);
      expect(stage.targetSlaHours).toBeGreaterThan(0);
    }
  });

  it('hitech os selector exposes modules and contracts', () => {
    const model = selectHitechOsViewModel();

    expect(model.modules.length).toBeGreaterThan(5);
    expect(model.contracts).toContain('HealthReportSchema');

    for (const module of model.modules) {
      expect(module.inputs.length).toBeGreaterThan(0);
      expect(module.outputs.length).toBeGreaterThan(0);
      expect(module.health.checks.length).toBeGreaterThan(0);
    }
  });

  it('valuation selector exposes scenarios and bridge data', () => {
    const model = selectValuationViewModel();

    expect(model.scenarios.length).toBeGreaterThan(10);
    expect(model.bridgeSeries.length).toBeGreaterThan(3);
    expect(model.contractVersion.protocolVersion.length).toBeGreaterThan(0);
  });

  it('status cards and volume selectors return aligned stage ids', () => {
    const statusCards = selectIndustrialFlowStatusCards();
    const volumeCards = selectIndustrialFlowRequestVolumeByStage();

    expect(statusCards.length).toBe(volumeCards.length);

    for (const card of statusCards) {
      const volume = volumeCards.find((item) => item.id === card.id);
      expect(volume).toBeDefined();
      expect(card.total).toBeGreaterThan(0);
    }
  });

  it('leaderboard and scenario bands are deterministic', () => {
    const leaderboard = selectValuationLeaderboard();
    const bands = selectValuationScenarioBands();

    expect(leaderboard.length).toBe(bands.length);

    for (let index = 1; index < leaderboard.length; index += 1) {
      expect(leaderboard[index - 1]!.confidenceWeightedValueM).toBeGreaterThanOrEqual(
        leaderboard[index]!.confidenceWeightedValueM,
      );
    }

    for (const band of bands) {
      expect(['core', 'stretch', 'defensive']).toContain(band.band);
      expect(band.confidence).toBeGreaterThanOrEqual(0);
      expect(band.confidence).toBeLessThanOrEqual(100);
    }
  });

  it('auxiliary selector sets are non-empty', () => {
    const notes = selectEngineCapabilityNotes();
    const io = selectHitechOsModuleIO();
    const counters = selectAllSummaryCounters();
    const queryExamples = selectRouteQueryExamples('04-valuation');

    expect(notes.length).toBeGreaterThan(0);
    expect(io.length).toBeGreaterThan(0);
    expect(counters.totalSignals).toBeGreaterThan(0);
    expect(queryExamples.length).toBe(3);
  });

  it('bridge totals reconcile positive and negative contributions', () => {
    const totals = selectValuationBridgeTotals();

    expect(totals.totalDeltaM).toBeCloseTo(
      totals.positiveDeltaM + totals.negativeDeltaM,
      6,
    );
  });
});
