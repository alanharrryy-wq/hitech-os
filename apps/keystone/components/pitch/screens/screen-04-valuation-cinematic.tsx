import { Table, TableBody, TableCell, TableHead, TableHeaderCell, TableRow } from "@hitech/ui-kit";
import { buildScreen04ViewModel } from "../../../lib/pitch/deck-view-model";
import { PitchCardGrid, PitchCardGridItem } from "../layout/pitch-card-grid";
import { PitchDataChip } from "../layout/pitch-data-chip";
import { PitchExpandablePanel } from "../layout/pitch-expandable-panel";
import { PitchSection } from "../layout/pitch-section";
import { PitchComparisonMeter } from "../visuals/pitch-comparison-meter";
import { PitchMiniBars } from "../visuals/pitch-mini-bars";
import { PitchRadialGauge } from "../visuals/pitch-radial-gauge";
import { PitchSparkline } from "../visuals/pitch-sparkline";

export interface Screen04ValuationCinematicProps {
  readonly className?: string;
}

const MULTIPLE_EXPANSION = [2.4, 2.6, 2.9, 3.2, 3.8, 4.4, 5.1, 5.7, 6.0];
const RISK_CURVE = [72, 66, 61, 57, 51, 47, 42, 38, 34];

export function Screen04ValuationCinematic({ className }: Screen04ValuationCinematicProps) {
  const model = buildScreen04ViewModel();

  return (
    <PitchSection
      id="valuation"
      eyebrow={model.kicker}
      title={model.title}
      description="Tres paneles narrativos para múltiplo, riesgo y escalabilidad sin perder tabla contractual."
      className={className}
      actions={<PitchDataChip label="Valuation" value={model.combinedLine} tone="gold" />}
    >
      <PitchCardGrid columns={3}>
        {model.blocks.map((block, index) => (
          <PitchCardGridItem
            key={block.heading}
            title={block.heading}
            description="Panel narrativo"
            kicker={model.derived.panelLabels[index] ?? `Panel ${index + 1}`}
            tone={index === 0 ? "neutral" : index === 1 ? "cyan" : "gold"}
          >
            {block.items.length > 0 ? (
              <ul className="m-0 list-disc space-y-1 pl-5 text-sm text-[color:rgba(4,18,25,0.76)]">
                {block.items.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : null}
            {block.phase1 ? (
              <p className="m-0 rounded-md border border-[rgba(2,111,134,0.2)] px-2 py-1 text-xs">{block.phase1}</p>
            ) : null}
            {block.phase2 ? (
              <p className="m-0 rounded-md border border-[rgba(2,111,134,0.2)] px-2 py-1 text-xs">{block.phase2}</p>
            ) : null}
          </PitchCardGridItem>
        ))}
      </PitchCardGrid>

      <div className="grid gap-3 xl:grid-cols-3">
        <article className="pitch-glass-card pitch-neon-edge grid gap-2 rounded-[var(--pitch-radius-lg)] p-4">
          <h3 className="m-0 text-sm font-semibold text-[color:var(--pitch-ink)]">Multiple expansion</h3>
          <PitchSparkline
            points={MULTIPLE_EXPANSION}
            label="2.5x -> 6x range"
            stroke="#AB7B26"
            fill="rgba(171,123,38,0.16)"
          />
          <PitchComparisonMeter
            leftLabel="Traditional"
            rightLabel="Hybrid"
            leftValue={25}
            rightValue={60}
          />
        </article>

        <article className="pitch-glass-card pitch-neon-edge grid gap-2 rounded-[var(--pitch-radius-lg)] p-4">
          <h3 className="m-0 text-sm font-semibold text-[color:var(--pitch-ink)]">Risk profile</h3>
          <PitchSparkline
            points={RISK_CURVE}
            label="Risk reduction trajectory"
            stroke="#026F86"
            fill="rgba(2,111,134,0.15)"
          />
          <PitchMiniBars
            series={[
              { label: "Traditional", value: model.derived.riskScale[0] ?? 60, tone: "gold" },
              { label: "Hybrid", value: model.derived.riskScale[1] ?? 40, tone: "teal" }
            ]}
            max={100}
          />
        </article>

        <article className="pitch-glass-card pitch-neon-edge grid place-items-center rounded-[var(--pitch-radius-lg)] p-4">
          <PitchRadialGauge
            value={model.derived.scalabilityScale[1] ?? 85}
            label="Scalability"
            valueLabel={`${model.derived.scalabilityScale[1] ?? 85}`}
            tone="cyan"
          />
        </article>
      </div>

      <PitchExpandablePanel title="Canonical valuation table" subtitle="Contract fixtures visible" defaultOpen>
        <div className="overflow-x-auto">
          <Table>
            <TableHead>
              <TableRow>
                {model.comparison.headers.map((header) => (
                  <TableHeaderCell key={header}>{header}</TableHeaderCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {model.comparison.rows.map((row, rowIndex) => (
                <TableRow key={`row-${rowIndex}`}>
                  {row.map((cell, cellIndex) => (
                    <TableCell key={`cell-${rowIndex}-${cellIndex}`}>{cell}</TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </PitchExpandablePanel>

      <div className="pitch-glass-card pitch-neon-edge rounded-[var(--pitch-radius-lg)] p-4">
        <p className="m-0 text-lg font-semibold text-[color:var(--pitch-ink)]">{model.combinedLine}</p>
      </div>
    </PitchSection>
  );
}
