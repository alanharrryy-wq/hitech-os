import { PITCH_DECK_FIXTURE, PITCH_SCREEN_FIXTURES } from "@hitech/contracts";
import { LayerFlagsProvider } from "@hitech/ui-kit";
import { PitchLayerDevTools, PitchShell, ScreenIndustrialFlow } from "../../../components/pitch";
import {
  resolvePitchLayerFlags,
  type PitchSearchParamsProps
} from "../../../lib/pitch/layer-resolution";

export const dynamic = "force-dynamic";

export default async function PitchIndustrialFlowPage({ searchParams }: PitchSearchParamsProps) {
  const resolvedSearchParams = await Promise.resolve(searchParams ?? {});
  const resolved = resolvePitchLayerFlags(resolvedSearchParams as any);
  const deck = PITCH_DECK_FIXTURE;
  const screen = PITCH_SCREEN_FIXTURES["02-industrial-flow"];

  return (
    <LayerFlagsProvider initialResolved={resolved}>
      <PitchShell
        title="Keystone Pitch Deck"
        subtitle="MOTOR 1 — FLUJO INDUSTRIAL RECURRENTE"
        nav={{ links: deck.navigation.links, activeSlug: screen.slug }}
      >
        <ScreenIndustrialFlow screen={screen} />
      </PitchShell>
      <PitchLayerDevTools visible={resolved.debug} />
    </LayerFlagsProvider>
  );
}
