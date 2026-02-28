import { describe, expect, it } from 'vitest';
import { deriveFeatureFlagsFromLayers, resolveLayerFlags } from '../../../lib/pitch';

describe('resolveLayerFlags basic behavior', () => {
  it('resolves all mode with neutral profile', () => {
    const result = resolveLayerFlags({ layers: 'all', layerProfile: 'neutral', debug: '0' });

    expect(result.mode).toBe('all');
    expect(result.profile).toBe('neutral');
    expect(result.debug).toBe(false);
    expect(result.selectedLayers.length).toBeGreaterThan(5);
    expect(result.flags.surfaceBase).toBe(true);
    expect(result.flags.chartGrid).toBe(true);
  });

  it('resolves none mode with zero active layers', () => {
    const result = resolveLayerFlags({ layers: 'none', layerProfile: 'fx', debug: '0' });

    expect(result.mode).toBe('none');
    expect(result.selectedLayers.length).toBe(0);
    expect(result.flags.surfaceBase).toBe(false);
    expect(result.flags.chartGlow).toBe(false);
  });

  it('resolves list mode from layerList', () => {
    const result = resolveLayerFlags({
      layers: 'list',
      layerProfile: 'neutral',
      debug: '0',
      layerList: 'surfaceBase,chartGrid,perfCompact',
    });

    expect(result.mode).toBe('list');
    expect(result.flags.surfaceBase).toBe(true);
    expect(result.flags.chartGrid).toBe(true);
    expect(result.flags.perfCompact).toBe(true);
    expect(result.flags.glassTint).toBe(false);
  });

  it('forces debug layers when debug=1', () => {
    const result = resolveLayerFlags({
      layers: 'none',
      layerProfile: 'perf',
      debug: '1',
    });

    expect(result.debug).toBe(true);
    expect(result.flags.debugOutline).toBe(true);
    expect(result.flags.debugMetrics).toBe(true);
  });

  it('derives feature flags from resolved layers', () => {
    const result = resolveLayerFlags({
      layers: 'list',
      layerProfile: 'fx',
      layerList: 'surfaceElevated,glassTint,perfDeferred',
      debug: '0',
    });

    const flags = deriveFeatureFlagsFromLayers(result);

    expect(flags.enableAiExecution).toBe(true);
    expect(flags.enableCapabilitiesProxy).toBe(true);
    expect(flags.enableExperimentalUi).toBe(true);
    expect(flags.enableHealthDashboard).toBe(false);
  });
});
