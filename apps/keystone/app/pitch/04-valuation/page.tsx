import { PITCH_DECK_FIXTURE, PITCH_SCREEN_FIXTURES } from "@hitech/contracts";
import { LayerFlagsProvider } from "@hitech/ui-kit";
import { PitchShell, ScreenValuation } from "../../../components/pitch";
import { PitchLayerDevTools } from "../../../components/pitch/debug/pitch-layer-dev-tools";
import { buildPitchShellFrameModel } from "../../../components/pitch/view-model/pitch-shell-model";
import {
  resolvePitchSearchParams,
  resolvePitchLayerFlags,
  type PitchSearchParamsProps
} from "../../../lib/pitch/layer-resolution";

export const dynamic = "force-dynamic";

export default async function PitchValuationPage({ searchParams }: PitchSearchParamsProps) {
  const resolved = resolvePitchLayerFlags(await resolvePitchSearchParams(searchParams));
  const debugVisible = resolved.debug && process.env.NODE_ENV !== "production";
  const deck = PITCH_DECK_FIXTURE;
  const screen = PITCH_SCREEN_FIXTURES["04-valuation"];
  const shellModel = buildPitchShellFrameModel(screen.slug);

  return (
    <LayerFlagsProvider initialResolved={resolved}>
      <PitchShell
        model={{ ...shellModel, nav: { ...shellModel.nav, links: deck.navigation.links } }}
        enableKeyboardNav={false}
      >
        <ScreenValuation screen={screen} />
      </PitchShell>
      <PitchLayerDevTools visible={debugVisible} />
    </LayerFlagsProvider>
  );
}
