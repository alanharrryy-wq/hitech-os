import { buildPitchDeckViewModel } from "../../../lib/pitch/deck-view-model";
import { PitchCardGrid } from "../layout/pitch-card-grid";
import { PitchSection } from "../layout/pitch-section";
import { PitchDataChip } from "../layout/pitch-data-chip";
import { PitchMiniBars } from "../visuals/pitch-mini-bars";
import { PitchRouteCard } from "./pitch-route-card";

export interface PitchRouteChooserProps {
  readonly className?: string;
}

export function PitchRouteChooser({ className }: PitchRouteChooserProps) {
  const model = buildPitchDeckViewModel();

  return (
    <PitchSection
      id="pitch-route-chooser"
      eyebrow="Pitch Index"
      title="Premium Route Chooser"
      description="Selecciona una pantalla del deck con contexto de intención e impacto para inversión."
      {...(className ? { className } : {})}
      stickyHeading={false}
      actions={
        <div className="flex flex-wrap items-center gap-2">
          <PitchDataChip label="Recommended" value={String(model.recommendedPath.length)} tone="gold" />
          <PitchDataChip label="Total screens" value={String(model.totalScreens)} tone="teal" />
        </div>
      }
    >
      <PitchCardGrid columns={3}>
        {model.indexRoutes.map((route) => (
          <PitchRouteCard key={route.slug} route={route} />
        ))}
      </PitchCardGrid>

      <div className="pitch-glass-card pitch-neon-edge grid gap-3 rounded-[var(--pitch-radius-lg)] p-4">
        <h3 className="m-0 text-base font-semibold text-[color:var(--pitch-ink)]">Recommended investor path</h3>
        <p className="m-0 text-sm text-[color:rgba(4,18,25,0.74)]">
          Ruta sugerida para presentar tesis híbrida, tracción operativa, moat digital y lógica de valuación.
        </p>
        <div className="flex flex-wrap items-center gap-2">
          {model.recommendedPath.map((route) => (
            <PitchDataChip
              key={route.slug}
              label={route.order.toString().padStart(2, "0")}
              value={route.routeBadge}
              tone="cyan"
            />
          ))}
        </div>
        <PitchMiniBars
          series={model.recommendedPath.map((route, index) => ({
            label: route.routeBadge,
            value: (index + 1) * 18,
            tone: index % 2 === 0 ? "teal" : "gold"
          }))}
          max={100}
        />
      </div>
    </PitchSection>
  );
}
