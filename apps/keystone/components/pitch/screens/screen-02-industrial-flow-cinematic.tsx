import { buildScreen02ViewModel } from "../../../lib/pitch/deck-view-model";
import { PitchCardGrid, PitchCardGridItem } from "../layout/pitch-card-grid";
import { PitchDataChip } from "../layout/pitch-data-chip";
import { PitchExpandablePanel } from "../layout/pitch-expandable-panel";
import { PitchSection } from "../layout/pitch-section";
import { PitchKpiChipCloud } from "../visuals/pitch-kpi-chip-cloud";
import { PitchMiniBars } from "../visuals/pitch-mini-bars";
import { PitchRadialGauge } from "../visuals/pitch-radial-gauge";
import { PitchSparkline } from "../visuals/pitch-sparkline";

export interface Screen02IndustrialFlowCinematicProps {
  readonly className?: string;
}

const FLOW_CURVE = [18, 24, 29, 35, 38, 42, 47, 52, 55];
const COVERAGE_CURVE = [10, 12, 16, 22, 30, 39, 48, 57, 66];

export function Screen02IndustrialFlowCinematic({ className }: Screen02IndustrialFlowCinematicProps) {
  const model = buildScreen02ViewModel();

  return (
    <PitchSection
      id="industrial-flow"
      eyebrow={model.kicker}
      title={model.title}
      description="Ritmo industrial recurrente con cobertura cíclica, chips de economía unitaria y módulos visuales."
      className={className}
      actions={
        <div className="flex flex-wrap items-center gap-2">
          <PitchDataChip label="Cycle" value={`${model.derived.cycleMonths}m`} tone="teal" />
          <PitchDataChip label="Annualized Utility" value={`$${model.derived.annualizedUtilityMillions}M`} tone="gold" />
        </div>
      }
    >
      <PitchCardGrid columns={4}>
        {model.kpis.map((kpi, index) => (
          <PitchCardGridItem
            key={kpi.label}
            title={kpi.value}
            description={kpi.note}
            kicker={kpi.label}
            tone={index % 2 === 0 ? "teal" : "cyan"}
          />
        ))}
      </PitchCardGrid>

      <div className="grid gap-3 xl:grid-cols-[1.3fr_1fr]">
        <article className="pitch-glass-card pitch-neon-edge grid gap-3 rounded-[var(--pitch-radius-lg)] p-4">
          <header className="grid gap-1">
            <h3 className="m-0 text-lg font-semibold text-[color:var(--pitch-ink)]">Coverage cycle module</h3>
            <p className="m-0 text-sm text-[color:rgba(4,18,25,0.72)]">{model.cycleLabel}</p>
          </header>

          <div className="grid gap-3 lg:grid-cols-2">
            <PitchSparkline
              points={FLOW_CURVE}
              label="Flow continuity"
              stroke="#026F86"
              fill="rgba(2,111,134,0.14)"
            />
            <PitchSparkline
              points={COVERAGE_CURVE}
              label="Coverage depth"
              stroke="#AB7B26"
              fill="rgba(171,123,38,0.16)"
            />
          </div>

          <PitchMiniBars
            series={model.kpis.slice(0, 4).map((kpi, index) => ({
              label: kpi.label.replace("módulos", "mods"),
              value: (index + 1) * 22,
              tone: index % 2 === 0 ? "teal" : "gold"
            }))}
            max={100}
          />

          <PitchExpandablePanel title="Unit economics chips" subtitle="Local deterministic overlay" defaultOpen>
            <PitchKpiChipCloud
              items={model.derived.coverageChips.map((chip, index) => ({
                label: chip,
                tone: index % 3 === 0 ? "teal" : index % 3 === 1 ? "gold" : "cyan"
              }))}
            />
          </PitchExpandablePanel>
        </article>

        <aside className="grid gap-3">
          <article className="pitch-glass-card pitch-neon-edge grid place-items-center rounded-[var(--pitch-radius-lg)] p-4">
            <PitchRadialGauge
              value={Math.round((model.derived.cycleMonths / 35) * 100)}
              label="Cycle readiness"
              valueLabel={`${model.derived.cycleMonths}m`}
              tone="teal"
            />
          </article>

          <article className="pitch-glass-card pitch-neon-edge grid gap-2 rounded-[var(--pitch-radius-lg)] p-4">
            <h4 className="m-0 text-sm font-semibold text-[color:var(--pitch-ink)]">Market confidence note</h4>
            <p className="m-0 text-sm text-[color:rgba(4,18,25,0.74)]">{model.microcopy}</p>
          </article>
        </aside>
      </div>
    </PitchSection>
  );
}
