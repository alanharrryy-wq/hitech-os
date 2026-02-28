import {
  HitechOsPanel,
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
  selectHitechOsViewModel,
  selectRouteNavigation,
  selectRouteQueryExamples,
  toReadonlySearchParams,
} from '../../../lib/pitch';

interface PageProps {
  readonly searchParams?: Record<string, string | ReadonlyArray<string> | undefined>;
}

export default async function PitchHitechOsPage({ searchParams }: PageProps) {
  const query = resolvePitchQueryState(searchParams);
  const layerResolution = resolveLayerFlags(toReadonlySearchParams(searchParams));
  const navigation = selectRouteNavigation('03-hitech-os', query);
  const model = selectHitechOsViewModel();
  const examples = selectRouteQueryExamples('03-hitech-os');
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
        <HitechOsPanel model={model} />
        <RouteLinkSet navigation={navigation} examples={examples} />
      </PitchShell>
    </LayerFlagsProvider>
  );
}
