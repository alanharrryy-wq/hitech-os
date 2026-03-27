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

interface ValuationPanelCopy {
  readonly eyebrow: string;
  readonly title: string;
  readonly narrative: string;
  readonly bullets: readonly string[];
  readonly bottomBox1?: string;
  readonly bottomBox2?: string;
}

const GUARDIAN_SUMMARY_LINE =
  "Participación económica Guardian: 17% de utilidad libre por 36 meses, sin equity permanente.";

const VALUATION_PANELS_COPY: readonly ValuationPanelCopy[] = [
  {
    eyebrow: "TRADICIONAL",
    title: "Unidad Industrial Tradicional",
    narrative: "Base industrial rentable con flujo, utilidad y disciplina operativa comprobables.",
    bullets: [
      "Ingreso mensual a 12 módulos: $228,000",
      "Utilidad mensual al 40%: $91,200",
      "Utilidad anualizada: $1,094,400",
      "La valuación base industrial se sostiene por flujo y ejecución",
      "Negocio rentable, pero con múltiplo limitado sin capa de software"
    ]
  },
  {
    eyebrow: "INDUSTRIAL + SOFTWARE",
    title: "Infraestructura Industrial + Software Propietario",
    narrative:
      "El wedge inicial habilita un contrato de mayor escala, operación recurrente y una tesis de valor más fuerte.",
    bullets: [
      "Wedge inicial: 6 módulos en 30 días = $114,000",
      "Utilidad estimada del wedge al 40%: $45,600",
      "La entrega habilita el contrato Guardian",
      "Proyección: 419 módulos a $19,000 por módulo en 3 años",
      "Utilidad libre proyectada: 48% - 55%"
    ]
  },
  {
    eyebrow: "ESTRUCTURA DE INVERSIÓN",
    title: "Estructura de Inversión",
    narrative:
      "Dos rutas claras para el inversionista: salida con rendimiento o participación económica limitada al contrato Guardian.",
    bullets: [
      "Etapa 1: inversión de $100k hoy para ejecutar el wedge y entregar 6 módulos a SRG en 30 días",
      "SRG paga a 60 días, lo que activa flujo comercial y operativo",
      "Ruta A: salida estimada en 4 a 6 meses con retorno total de $125k",
      "Ruta B: al entregar los módulos, se abre una segunda inversión de +$200k para escalar el contrato Guardian",
      "Total cash aportado en Ruta B: $300k",
      "La propuesta no es equity permanente",
      "El inversionista participa con 17% de la utilidad libre del contrato Guardian durante 36 meses",
      "Ingreso proyectado Guardian: $7.96M",
      "Utilidad libre proyectada: $3.82M - $4.38M",
      "Participación estimada al 17%: $649,618 - $744,354 en 3 años"
    ],
    bottomBox1: "Etapa 1: $100k — Wedge, entrega a SRG y salida estimada con $125k",
    bottomBox2: "Etapa 2: +$200k — 17% de utilidad libre de Guardian por 36 meses, sin equity permanente"
  }
] as const;

export function Screen04ValuationCinematic({ screen, className }: Screen04ValuationCinematicProps) {
  const model = buildScreen04ViewModel(screen);

  return (
    <PitchSection
      id="valuation"
      eyebrow={model.kicker}
      title={model.title}
      description="Deal en 2 etapas: $100k → entrega 30d → +$200k con factura SRG → participación económica Guardian."
      className={className}
      actions={<PitchDataChip label="Valuation" value={GUARDIAN_SUMMARY_LINE} tone="gold" />}
    >
      <PitchCardGrid columns={3} className="pitch-valuation-block-grid">
        {VALUATION_PANELS_COPY.map((panel, index) => (
          <PitchCardGridItem
            key={panel.title}
            title={panel.title}
            description={panel.narrative}
            kicker={panel.eyebrow}
            tone={index === 0 ? "neutral" : index === 1 ? "cyan" : "gold"}
            className="pitch-valuation-block-item"
          >
            {panel.bullets.length > 0 ? (
              <ul className="pitch-valuation-block-list m-0 text-sm text-[color:rgba(4,18,25,0.76)]">
                {panel.bullets.map((item) => (
                  <li key={item} className="pitch-valuation-block-list-item">{item}</li>
                ))}
              </ul>
            ) : null}
            {panel.bottomBox1 ? (
              <p className="pitch-valuation-phase-pill m-0 text-xs">{panel.bottomBox1}</p>
            ) : null}
            {panel.bottomBox2 ? (
              <p className="pitch-valuation-phase-pill m-0 text-xs">{panel.bottomBox2}</p>
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
          <h3 className="m-0 text-sm font-semibold text-[color:var(--pitch-ink)]">Participación Económica Guardian</h3>
          <ValuationEquityVisual />
        </article>
      </div>

      <PitchExpandablePanel title="Tabla comparativa de decisión" subtitle="Referencia contractual visible" defaultOpen>
        <p className="m-0 mb-3 text-xs text-[color:rgba(4,18,25,0.68)]">
          Referencia contractual para comparar la base industrial tradicional frente al escenario Industrial + Software
          con participación económica Guardian.
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
        <p className="m-0 text-lg font-semibold text-[color:var(--pitch-ink)]">{GUARDIAN_SUMMARY_LINE}</p>
      </div>
    </PitchSection>
  );
}
