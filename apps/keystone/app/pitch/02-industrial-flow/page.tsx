import {
  IndustrialFlowPanel,
  LayerDebugPanel,
  LayerFlagsProvider,
  PitchHeroBlock,
  PitchQueryPills,
  PitchShell,
  RouteLinkSet,
} from '../../../components/pitch';
import {
  resolveLayerFlags,
  resolvePitchQueryState,
  selectIndustrialFlowViewModel,
  selectRouteNavigation,
  selectRouteQueryExamples,
  toReadonlySearchParams,
} from '../../../lib/pitch';

interface PageProps {
  readonly searchParams?: Record<string, string | ReadonlyArray<string> | undefined>;
}

export default async function PitchIndustrialFlowPage({ searchParams }: PageProps) {
  const query = resolvePitchQueryState(searchParams);
  const layerResolution = resolveLayerFlags(toReadonlySearchParams(searchParams));
  const navigation = selectRouteNavigation('02-industrial-flow', query);
  const model = selectIndustrialFlowViewModel();
  const examples = selectRouteQueryExamples('02-industrial-flow');
  const showDebug = layerResolution.debug && process.env.NODE_ENV !== 'production';

  return (
    <LayerFlagsProvider value={layerResolution}>
      <PitchShell
        title={navigation.current.title}
        subtitle={navigation.current.subtitle}
        navigation={navigation}
        queryPills={<PitchQueryPills query={query} />}
        debugPanel={showDebug ? <LayerDebugPanel /> : undefined}
      >
        <PitchHeroBlock
          eyebrow={model.hero.eyebrow}
          title={model.hero.title}
          subtitle={model.hero.subtitle}
          bullets={model.hero.bullets}
        />
        <IndustrialFlowPanel model={model} />
        <RouteLinkSet navigation={navigation} examples={examples} />
      </PitchShell>
    </LayerFlagsProvider>
  );
}
