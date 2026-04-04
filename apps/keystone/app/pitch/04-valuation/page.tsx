import { PITCH_DECK_FIXTURE, PITCH_SCREEN_FIXTURES } from "@hitech/contracts";
import { LayerFlagsProvider } from "@hitech/ui-kit";
import { PitchLayerDevTools, PitchShell, ScreenValuation } from "../../../components/pitch";
import {
  resolvePitchSearchParams,
  resolvePitchLayerFlags,
  type PitchSearchParamsProps
} from "../../../lib/pitch/layer-resolution";

export const dynamic = "force-dynamic";

export default async function PitchValuationPage({ searchParams }: PitchSearchParamsProps) {
  const resolved = resolvePitchLayerFlags(await resolvePitchSearchParams(searchParams));
  const deck = PITCH_DECK_FIXTURE;
  const screen = PITCH_SCREEN_FIXTURES["04-valuation"];

  return (
    <LayerFlagsProvider initialResolved={resolved}>
      <PitchShell
        title="Keystone Pitch Deck"
        subtitle="ESTRUCTURA FINANCIERA + VALUACIÓN"
        nav={{ links: deck.navigation.links, activeSlug: screen.slug }}
      >
        <ScreenValuation screen={screen} />
      </PitchShell>
      <PitchLayerDevTools visible={resolved.debug} />
    </LayerFlagsProvider>
  );
}
