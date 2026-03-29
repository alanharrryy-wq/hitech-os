import { PITCH_DECK_FIXTURE, PITCH_SCREEN_FIXTURES } from "@hitech/contracts";
import { LayerFlagsProvider } from "@hitech/ui-kit";
import { PitchShell } from "../../../components/pitch";
import { ShipmentsReceivingControlRoom } from "../../../components/pitch/run2";
import { buildPitchShellFrameModel } from "../../../components/pitch/view-model/pitch-shell-model";
import {
  resolvePitchSearchParams,
  resolvePitchLayerFlags,
  type PitchSearchParamsProps
} from "../../../lib/pitch/layer-resolution";

export const dynamic = "force-dynamic";

export default async function PitchShipmentsReceivingPage({ searchParams }: PitchSearchParamsProps) {
  const resolved = resolvePitchLayerFlags(await resolvePitchSearchParams(searchParams));
  const deck = PITCH_DECK_FIXTURE;
  const screen = PITCH_SCREEN_FIXTURES["06-shipments-receiving"];
  const shellModel = buildPitchShellFrameModel(screen.slug);

  return (
    <LayerFlagsProvider initialResolved={resolved}>
      <PitchShell model={{ ...shellModel, nav: { ...shellModel.nav, links: deck.navigation.links } }}>
        <ShipmentsReceivingControlRoom screen={screen} />
      </PitchShell>
    </LayerFlagsProvider>
  );
}
