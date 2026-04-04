import { PITCH_DECK_FIXTURE, PITCH_SCREEN_FIXTURES } from "@hitech/contracts";
import { LayerFlagsProvider } from "@hitech/ui-kit";
import { PitchLayerDevTools, PitchShell, ScreenDoubleEngine } from "../../../components/pitch";
import {
  resolvePitchSearchParams,
  resolvePitchLayerFlags,
  type PitchSearchParamsProps
} from "../../../lib/pitch/layer-resolution";

export const dynamic = "force-dynamic";

export default async function PitchDoubleEnginePage({ searchParams }: PitchSearchParamsProps) {
  const resolved = resolvePitchLayerFlags(await resolvePitchSearchParams(searchParams));
  const deck = PITCH_DECK_FIXTURE;
  const screen = PITCH_SCREEN_FIXTURES["01-double-engine"];

  return (
    <LayerFlagsProvider initialResolved={resolved}>
      <PitchShell
        title="Keystone Pitch Deck"
        subtitle="HITECH — ARQUITECTURA DE DOBLE MOTOR"
        nav={{ links: deck.navigation.links, activeSlug: screen.slug }}
      >
        <ScreenDoubleEngine screen={screen} />
      </PitchShell>
      <PitchLayerDevTools visible={resolved.debug} />
    </LayerFlagsProvider>
  );
}
