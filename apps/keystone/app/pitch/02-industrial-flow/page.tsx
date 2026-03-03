import { PITCH_DECK_FIXTURE, PITCH_SCREEN_FIXTURES } from "@hitech/contracts";
import { LayerDebugPanel, LayerFlagsProvider } from "@hitech/ui-kit";
import { PitchShell, ScreenIndustrialFlow } from "../../../components/pitch";
import { buildPitchShellFrameModel } from "../../../components/pitch/view-model/pitch-shell-model";
import {
  resolvePitchLayerFlags,
  type PitchSearchParamsProps
} from "../../../lib/pitch/layer-resolution";

export const dynamic = "force-dynamic";

export default function PitchIndustrialFlowPage({ searchParams }: PitchSearchParamsProps) {
  const resolved = resolvePitchLayerFlags(searchParams);
  const debugVisible = resolved.debug && process.env.NODE_ENV !== "production";
  const deck = PITCH_DECK_FIXTURE;
  const screen = PITCH_SCREEN_FIXTURES["02-industrial-flow"];
  const shellModel = buildPitchShellFrameModel(screen.slug);

  return (
    <LayerFlagsProvider initialResolved={resolved}>
      <PitchShell model={{ ...shellModel, nav: { ...shellModel.nav, links: deck.navigation.links } }}>
        <ScreenIndustrialFlow screen={screen} />
      </PitchShell>
      {debugVisible ? <LayerDebugPanel /> : null}
    </LayerFlagsProvider>
  );
}
