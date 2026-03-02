import { PITCH_DECK_FIXTURE, PITCH_SCREEN_FIXTURES } from "@hitech/contracts";
import { LayerDebugPanel, LayerFlagsProvider } from "@hitech/ui-kit";
import { PitchShell } from "../../../components/pitch/pitch-shell";
import { InventoryFoundationControlRoom } from "../../../components/pitch/run1";
import {
  resolvePitchLayerFlags,
  type PitchSearchParamsProps
} from "../../../lib/pitch/layer-resolution";

export const dynamic = "force-dynamic";

export default function PitchInventoryFoundationPage({ searchParams }: PitchSearchParamsProps) {
  const resolved = resolvePitchLayerFlags(searchParams);
  const deck = PITCH_DECK_FIXTURE;
  const screen = PITCH_SCREEN_FIXTURES["05-inventory-foundation"];

  return (
    <LayerFlagsProvider initialResolved={resolved}>
      <PitchShell
        title="Keystone Pitch Deck"
        subtitle={screen.title}
        nav={{ links: deck.navigation.links, activeSlug: screen.slug }}
      >
        <InventoryFoundationControlRoom screen={screen} />
      </PitchShell>
      {resolved.debug ? <LayerDebugPanel /> : null}
    </LayerFlagsProvider>
  );
}
