import { Badge } from "@hitech/ui-kit";
import { buildScreen01ViewModel } from "../../../lib/pitch/deck-view-model";
import { PitchBulletCards } from "../layout/pitch-bullet-cards";
import { PitchCardGrid, PitchCardGridItem } from "../layout/pitch-card-grid";
import { PitchDataChip } from "../layout/pitch-data-chip";
import { PitchExpandablePanel } from "../layout/pitch-expandable-panel";
import { PitchSection } from "../layout/pitch-section";
import { PitchComparisonMeter } from "../visuals/pitch-comparison-meter";
import { PitchKpiChipCloud } from "../visuals/pitch-kpi-chip-cloud";
import { PitchMiniBars } from "../visuals/pitch-mini-bars";
import { PitchRadialGauge } from "../visuals/pitch-radial-gauge";
import { PitchSparkline } from "../visuals/pitch-sparkline";
import { PitchVsDivider } from "../visuals/pitch-vs-divider";

export interface Screen01DoubleEngineCinematicProps {
  readonly className?: string;
}

const INDUSTRIAL_SPARK = [24, 27, 31, 34, 37, 40, 42, 46];
const SOFTWARE_SPARK = [14, 16, 18, 22, 24, 28, 33, 39];

export function Screen01DoubleEngineCinematic({ className }: Screen01DoubleEngineCinematicProps) {
  const model = buildScreen01ViewModel();

  return (
    <PitchSection
      id="double-engine"
      eyebrow={model.kicker}
      title={model.title}
      description="Comparativa cinematográfica de motores industrial y software con densidad interactiva local."
      className={className}
      actions={
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone="accent">Hybrid Core</Badge>
          <PitchDataChip label="Balance Index" value={`${model.derived.balancedIndex}%`} tone="cyan" />
        </div>
      }
    >
      <div className="grid gap-3 xl:grid-cols-[1fr_auto_1fr]">
        <article className="pitch-glass-card pitch-neon-edge grid gap-3 rounded-[var(--pitch-radius-lg)] p-4">
          <header className="grid gap-1">
            <p className="m-0 text-[0.72rem] uppercase tracking-[0.11em] text-[color:rgba(4,18,25,0.62)]">Left Engine</p>
            <h3 className="m-0 text-lg font-semibold text-[color:var(--pitch-ink)]">{model.left.heading}</h3>
          </header>

          <PitchBulletCards bullets={model.left.bullets} tone="teal" />

          <PitchExpandablePanel title="Operational context" subtitle="Industrial baseline" defaultOpen>
            <div className="grid gap-2">
              {model.left.microcopy.map((line) => (
                <p key={line} className="m-0 text-xs text-[color:rgba(4,18,25,0.72)]">
                  {line}
                </p>
              ))}
            </div>
          </PitchExpandablePanel>

          <PitchSparkline
            points={INDUSTRIAL_SPARK}
            label="Industrial momentum"
            stroke="#026F86"
            fill="rgba(2,111,134,0.14)"
          />
        </article>

        <div className="grid content-start gap-3">
          <PitchVsDivider
            summary="No soy proveedor. Soy sistema."
            details={[
              "Motor industrial ancla ingresos recurrentes con base instalada.",
              "Motor digital protege margen por control y trazabilidad.",
              "El valor combinado reduce dependencia comercial puntual."
            ]}
          />
          <PitchRadialGauge
            value={model.derived.balancedIndex}
            label="Balance"
            valueLabel={`${model.derived.balancedIndex}%`}
            tone="gold"
          />
        </div>

        <article className="pitch-glass-card pitch-neon-edge grid gap-3 rounded-[var(--pitch-radius-lg)] p-4">
          <header className="grid gap-1">
            <p className="m-0 text-[0.72rem] uppercase tracking-[0.11em] text-[color:rgba(4,18,25,0.62)]">Right Engine</p>
            <h3 className="m-0 text-lg font-semibold text-[color:var(--pitch-ink)]">{model.right.heading}</h3>
          </header>

          <PitchBulletCards bullets={model.right.bullets} tone="cyan" />

          <PitchExpandablePanel title="Platform context" subtitle="Software defensibility" defaultOpen>
            <div className="grid gap-2">
              {model.right.microcopy.map((line) => (
                <p key={line} className="m-0 text-xs text-[color:rgba(4,18,25,0.72)]">
                  {line}
                </p>
              ))}
            </div>
          </PitchExpandablePanel>

          <PitchSparkline
            points={SOFTWARE_SPARK}
            label="Software capability rise"
            stroke="#02A7CA"
            fill="rgba(2,167,202,0.14)"
          />
        </article>
      </div>

      <PitchCardGrid columns={3}>
        <PitchCardGridItem
          title="Industrial KPIs"
          description="Indicadores de tracción y disciplina operativa"
          kicker="Engine 1"
          tone="teal"
        >
          <PitchMiniBars
            series={[
              { label: "Facturados", value: 19, tone: "teal" },
              { label: "Listos", value: 6, tone: "teal" },
              { label: "Mensuales", value: 12, tone: "gold" },
              { label: "Instalados", value: 42, tone: "cyan" }
            ]}
            max={50}
          />
        </PitchCardGridItem>

        <PitchCardGridItem
          title="Platform Coverage"
          description="Capacidades del motor digital en chips"
          kicker="Engine 2"
          tone="cyan"
        >
          <PitchKpiChipCloud
            items={model.derived.capabilityChips.map((chip, index) => ({
              label: chip,
              tone: index % 2 === 0 ? "cyan" : "teal"
            }))}
          />
        </PitchCardGridItem>

        <PitchCardGridItem
          title="Engine Weight"
          description="Participación conceptual en propuesta de valor"
          kicker="Blend"
          tone="gold"
        >
          <PitchComparisonMeter
            leftLabel="Industrial"
            rightLabel="Software"
            leftValue={model.derived.industrialCount}
            rightValue={model.derived.softwareCount}
          />
        </PitchCardGridItem>
      </PitchCardGrid>

      <div className="pitch-glass-card pitch-neon-edge rounded-[var(--pitch-radius-lg)] p-4">
        <p className="m-0 text-lg font-semibold text-[color:var(--pitch-ink)]">{model.implicitMessage}</p>
      </div>
    </PitchSection>
  );
}
