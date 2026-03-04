import { LayerFlagsProvider } from "@hitech/ui-kit";
import { PitchRouteChooser, PitchShell } from "../../components/pitch";
import { PitchLayerDevTools } from "../../components/pitch/debug/pitch-layer-dev-tools";
import { buildPitchShellFrameModel } from "../../components/pitch/view-model/pitch-shell-model";
import {
  resolvePitchSearchParams,
  resolvePitchLayerFlags,
  type PitchSearchParamsProps
} from "../../lib/pitch/layer-resolution";

export const dynamic = "force-dynamic";

export default async function PitchIndexPage({ searchParams }: PitchSearchParamsProps) {
  const resolved = resolvePitchLayerFlags(await resolvePitchSearchParams(searchParams));
  const debugVisible = resolved.debug && process.env.NODE_ENV !== "production";
  const shellModel = buildPitchShellFrameModel();

  return (
    <LayerFlagsProvider initialResolved={resolved}>
      <PitchShell model={shellModel}>
        {debugVisible ? (
          <PitchRouteChooser />
        ) : (
          <section className="pitch-static-card pitch-glass-card pitch-neon-edge rounded-[var(--pitch-radius-lg)] p-4">
            <h2 className="m-0 text-base font-semibold text-[color:var(--pitch-ink)]">Pitch Index bloqueado</h2>
            <p className="m-0 mt-2 text-sm text-[color:var(--pitch-muted)]">
              El menú de rutas con redirección está disponible solo en debug (`?debug=1`).
            </p>
          </section>
        )}
      </PitchShell>
      <PitchLayerDevTools visible={debugVisible} />
    </LayerFlagsProvider>
  );
}
