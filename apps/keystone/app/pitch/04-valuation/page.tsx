import {
  LayerDebugPanel,
  LayerFlagsProvider,
  PitchHeroBlock,
  PitchQueryPills,
  PitchShell,
  RouteLinkSet,
  ValuationPanel,
} from '../../../components/pitch';
import {
  resolveLayerFlags,
  resolvePitchQueryState,
  selectRouteNavigation,
  selectRouteQueryExamples,
  selectValuationViewModel,
  toReadonlySearchParams,
} from '../../../lib/pitch';

interface PageProps {
  readonly searchParams?: Record<string, string | ReadonlyArray<string> | undefined>;
}

export default async function PitchValuationPage({ searchParams }: PageProps) {
  const query = resolvePitchQueryState(searchParams);
  const layerResolution = resolveLayerFlags(toReadonlySearchParams(searchParams));
  const navigation = selectRouteNavigation('04-valuation', query);
  const model = selectValuationViewModel();
  const examples = selectRouteQueryExamples('04-valuation');
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
        <ValuationPanel model={model} />
        <RouteLinkSet navigation={navigation} examples={examples} />
      </PitchShell>
    </LayerFlagsProvider>
  );
}
