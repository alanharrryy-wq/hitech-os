import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import {
  DoubleEnginePanel,
  HitechOsPanel,
  LayerDebugPanel,
  LayerFlagsProvider,
  PitchHeroBlock,
  PitchIndexCards,
  PitchQueryPills,
  PitchShell,
  RouteLinkSet,
  ValuationPanel,
} from '..';
import {
  buildDefaultPitchQueryState,
  resolveLayerFlags,
  selectDoubleEngineViewModel,
  selectHitechOsViewModel,
  selectPitchIndexViewModel,
  selectRouteNavigation,
  selectRouteQueryExamples,
  selectValuationViewModel,
} from '../../../lib/pitch';

function render(input: React.ReactElement): string {
  return renderToStaticMarkup(input);
}

describe('component composition snapshots', () => {
  it('renders pitch shell with navigation and children', () => {
    const query = buildDefaultPitchQueryState({ layers: 'all', layerProfile: 'neutral', debug: '0' });
    const navigation = selectRouteNavigation('01-double-engine', query);

    const html = render(
      <PitchShell
        title={navigation.current.title}
        subtitle={navigation.current.subtitle}
        navigation={navigation}
        queryPills={<PitchQueryPills query={query} />}
      >
        <PitchHeroBlock
          eyebrow="Test"
          title="Shell Render"
          subtitle="Snapshot subtitle"
          bullets={['one', 'two', 'three']}
        />
      </PitchShell>,
    );

    expect(html).toContain('Shell Render');
    expect(html).toContain('layers=all');
    expect(html).toContain('01 · Double Engine');
  });

  it('renders index cards using selector model', () => {
    const model = selectPitchIndexViewModel({
      layers: 'all',
      layerProfile: 'neutral',
      debug: '0',
    });

    const html = render(<PitchIndexCards model={model} />);

    expect(html).toContain('01 · Double Engine');
    expect(html).toContain('02 · Industrial Flow');
    expect(html).toContain('03 · Hitech OS');
    expect(html).toContain('04 · Valuation');
  });

  it('renders double engine panel with large fixture matrix', () => {
    const model = selectDoubleEngineViewModel();
    const html = render(<DoubleEnginePanel model={model} />);

    expect(html).toContain('Engine Capability Matrix');
    expect(html).toContain('KPI Band Tracker');
    expect(html).toContain('Strategy Narrative');
    expect(html).toContain('Engine Track 01');
  });

  it('renders hitech os panel with modules and contracts', () => {
    const model = selectHitechOsViewModel();
    const html = render(<HitechOsPanel model={model} />);

    expect(html).toContain('Contract Registry');
    expect(html).toContain('Module Map');
    expect(html).toContain('Reliability Narrative');
    expect(html).toContain('HealthReportSchema');
  });

  it('renders valuation panel with scenario board', () => {
    const model = selectValuationViewModel();
    const html = render(<ValuationPanel model={model} />);

    expect(html).toContain('Scenario Board');
    expect(html).toContain('Bridge Series');
    expect(html).toContain('Contract Version');
    expect(html).toContain('Scenario Track 01');
  });

  it('renders route link set with query examples', () => {
    const query = buildDefaultPitchQueryState({ layers: 'all', layerProfile: 'fx', debug: '1' });
    const navigation = selectRouteNavigation('04-valuation', query);
    const examples = selectRouteQueryExamples('04-valuation');

    const html = render(<RouteLinkSet navigation={navigation} examples={examples} />);

    expect(html).toContain('Query Presets');
    expect(html).toContain('Perf / Debug');
    expect(html).toContain('No next route');
  });

  it('renders debug panel under provider context', () => {
    const value = resolveLayerFlags({
      layers: 'list',
      layerProfile: 'perf',
      layerList: 'surfaceBase,chartGrid,perfDeferred',
      debug: '1',
    });

    const html = render(
      <LayerFlagsProvider value={value}>
        <LayerDebugPanel />
      </LayerFlagsProvider>,
    );

    expect(html).toContain('Layer Debug Panel');
    expect(html).toContain('mode=list');
    expect(html).toContain('debug=1');
    expect(html).toContain('surfaceBase');
  });
});
