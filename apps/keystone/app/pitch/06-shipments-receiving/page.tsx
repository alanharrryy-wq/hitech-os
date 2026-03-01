import { PITCH_DECK_FIXTURE, PITCH_SCREEN_FIXTURES } from "@hitech/contracts";
import { LayerDebugPanel, LayerFlagsProvider } from "@hitech/ui-kit";
import { PitchShell, ScreenShipmentsReceiving } from "../../../components/pitch";
import {
  resolvePitchLayerFlags,
  type PitchSearchParamsProps
} from "../../../lib/pitch/layer-resolution";

export const dynamic = "force-dynamic";

export default function PitchShipmentsReceivingPage({ searchParams }: PitchSearchParamsProps) {
  const resolved = resolvePitchLayerFlags(searchParams);
  const deck = PITCH_DECK_FIXTURE;
  const screen = PITCH_SCREEN_FIXTURES["06-shipments-receiving"];

  return (
    <LayerFlagsProvider initialResolved={resolved}>
      <PitchShell
        title="Keystone Pitch Deck"
        subtitle={screen.title}
        nav={{ links: deck.navigation.links, activeSlug: screen.slug }}
      >
        <ScreenShipmentsReceiving screen={screen} />
      </PitchShell>
      {resolved.debug ? <LayerDebugPanel /> : null}
    </LayerFlagsProvider>
  );
}
