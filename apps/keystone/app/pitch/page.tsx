import { LayerDebugPanel, LayerFlagsProvider, resolveLayerFlags } from "@hitech/ui-kit";
import { PitchRouteChooser, PitchShell } from "../../components/pitch";
import { buildPitchShellFrameModel } from "../../components/pitch/view-model/pitch-shell-model";
import type { PitchSearchParamsProps } from "../../lib/pitch/layer-resolution";

export const dynamic = "force-dynamic";

export default function PitchIndexPage({ searchParams }: PitchSearchParamsProps) {
  const resolved = resolveLayerFlags(searchParams ?? {});
  const debugVisible = resolved.debug && process.env.NODE_ENV !== "production";
  const shellModel = buildPitchShellFrameModel();

  return (
    <LayerFlagsProvider initialResolved={resolved}>
      <PitchShell model={shellModel}>
        <PitchRouteChooser />
      </PitchShell>
      {debugVisible ? <LayerDebugPanel /> : null}
    </LayerFlagsProvider>
  );
}
