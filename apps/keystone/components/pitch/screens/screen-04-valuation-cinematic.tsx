import type { PitchScreen04 } from "@hitech/contracts";
import { Table, TableBody, TableCell, TableHead, TableHeaderCell, TableRow } from "@hitech/ui-kit";
import { buildScreen04ViewModel } from "../../../lib/pitch/deck-view-model";
import { PitchCardGrid, PitchCardGridItem } from "../layout/pitch-card-grid";
import { PitchDataChip } from "../layout/pitch-data-chip";
import { PitchExpandablePanel } from "../layout/pitch-expandable-panel";
import { PitchSection } from "../layout/pitch-section";
import {
  ValuationDeriskVisual,
  ValuationEquityVisual,
  ValuationTimelineVisual
} from "../valuation-visuals";

export interface Screen04ValuationCinematicProps {
  readonly screen?: PitchScreen04;
  readonly className?: string;
}

export function Screen04ValuationCinematic({ screen, className }: Screen04ValuationCinematicProps) {
  const model = buildScreen04ViewModel(screen);

  return (
    <PitchSection
      id="valuation"
      eyebrow={model.kicker}
      title={model.title}
      description="Deal en 2 etapas: $100k → entrega 30d → +$200k con factura SRG → opción de equity."
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
        <article className="pitch-static-card pitch-glass-card pitch-neon-edge grid gap-2 rounded-[var(--pitch-radius-lg)] p-4">
          <h3 className="m-0 text-sm font-semibold text-[color:var(--pitch-ink)]">Ciclo de caja (D0→D30→D90)</h3>
          <ValuationTimelineVisual />
        </article>

        <article className="pitch-static-card pitch-glass-card pitch-neon-edge grid gap-2 rounded-[var(--pitch-radius-lg)] p-4">
          <h3 className="m-0 text-sm font-semibold text-[color:var(--pitch-ink)]">De-risk por evidencia</h3>
          <ValuationDeriskVisual />
        </article>

        <article className="pitch-static-card pitch-glass-card pitch-neon-edge grid rounded-[var(--pitch-radius-lg)] p-4">
          <h3 className="m-0 text-sm font-semibold text-[color:var(--pitch-ink)]">Equity outcome (cap 4–6M)</h3>
          <ValuationEquityVisual />
        </article>
      </div>

      <PitchExpandablePanel title="Canonical valuation table" subtitle="Contract fixtures visible" defaultOpen>
        <p className="m-0 mb-3 text-xs text-[color:rgba(4,18,25,0.68)]">
          Canonical valuation table: referencia contractual; el equity final depende de cap 4–6M y ejecución 12/mes.
        </p>
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
