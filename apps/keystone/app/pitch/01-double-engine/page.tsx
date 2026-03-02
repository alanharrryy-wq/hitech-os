import { PITCH_DECK_FIXTURE, PITCH_SCREEN_FIXTURES } from "@hitech/contracts";
import { LayerDebugPanel, LayerFlagsProvider, resolveLayerFlags } from "@hitech/ui-kit";
import { PitchShell, ScreenDoubleEngine } from "../../../components/pitch";
import { buildPitchShellFrameModel } from "../../../components/pitch/view-model/pitch-shell-model";
import type { PitchSearchParamsProps } from "../../../lib/pitch/layer-resolution";

export const dynamic = "force-dynamic";

export default function PitchDoubleEnginePage({ searchParams }: PitchSearchParamsProps) {
  const resolved = resolveLayerFlags(searchParams ?? {});
  const debugVisible = resolved.debug && process.env.NODE_ENV !== "production";
  const deck = PITCH_DECK_FIXTURE;
  const screen = PITCH_SCREEN_FIXTURES["01-double-engine"];
  const shellModel = buildPitchShellFrameModel(screen.slug);

  return (
    <LayerFlagsProvider initialResolved={resolved}>
      <PitchShell model={{ ...shellModel, nav: { ...shellModel.nav, links: deck.navigation.links } }}>
        <ScreenDoubleEngine screen={screen} />
      </PitchShell>
      {debugVisible ? <LayerDebugPanel /> : null}
    </LayerFlagsProvider>
  );
}
