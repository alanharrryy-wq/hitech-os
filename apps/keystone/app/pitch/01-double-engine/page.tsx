import {
  DoubleEnginePanel,
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
  selectDoubleEngineViewModel,
  selectRouteNavigation,
  selectRouteQueryExamples,
  toReadonlySearchParams,
} from '../../../lib/pitch';

interface PageProps {
  readonly searchParams?: Record<string, string | ReadonlyArray<string> | undefined>;
}

export default async function PitchDoubleEnginePage({ searchParams }: PageProps) {
  const query = resolvePitchQueryState(searchParams);
  const layerResolution = resolveLayerFlags(toReadonlySearchParams(searchParams));
  const navigation = selectRouteNavigation('01-double-engine', query);
  const model = selectDoubleEngineViewModel();
  const examples = selectRouteQueryExamples('01-double-engine');
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
        <DoubleEnginePanel model={model} />
        <RouteLinkSet navigation={navigation} examples={examples} />
      </PitchShell>
    </LayerFlagsProvider>
  );
}
