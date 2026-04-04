import { PITCH_DECK_FIXTURE, PITCH_SCREEN_FIXTURES } from "@hitech/contracts";
import { LayerFlagsProvider } from "@hitech/ui-kit";
import { PitchLayerDevTools, PitchShell, ScreenHiTechOs } from "../../../components/pitch";
import {
  resolvePitchSearchParams,
  resolvePitchLayerFlags,
  type PitchSearchParamsProps
} from "../../../lib/pitch/layer-resolution";

export const dynamic = "force-dynamic";

export default async function PitchHiTechOsPage({ searchParams }: PitchSearchParamsProps) {
  const resolved = resolvePitchLayerFlags(await resolvePitchSearchParams(searchParams));
  const deck = PITCH_DECK_FIXTURE;
  const screen = PITCH_SCREEN_FIXTURES["03-hitech-os"];

  return (
    <LayerFlagsProvider initialResolved={resolved}>
      <PitchShell
        title="Keystone Pitch Deck"
        subtitle="MOTOR 2 — HITECH OS (Infraestructura Digital)"
        nav={{ links: deck.navigation.links, activeSlug: screen.slug }}
      >
        <ScreenHiTechOs screen={screen} />
      </PitchShell>
      <PitchLayerDevTools visible={resolved.debug} />
    </LayerFlagsProvider>
  );
}
