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

interface DeterministicSeries {
  readonly coverage: readonly number[];
  readonly evidence: readonly number[];
  readonly bars: ReadonlyArray<{
    readonly label: string;
    readonly value: number;
    readonly tone: "teal" | "gold" | "cyan";
  }>;
  readonly readiness: number;
}

const SCREEN_02_SEED = "core-hitech-02";
const BAR_LABELS = [
  "Standards deployed",
  "Inspections executed",
  "Work orders logged",
  "Training records",
  "Audit closures"
] as const;

const SYSTEM_KPIS = [
  {
    label: "Risk Method",
    value: "PHA + ATS/JSA",
    note: "Probability x Severity matrix in every critical workflow.",
    tone: "teal" as const
  },
  {
    label: "Permit-to-Work",
    value: "Active",
    note: "Controlled permits with accountable approvals by role.",
    tone: "cyan" as const
  },
  {
    label: "Document Control",
    value: "Versioned",
    note: "Unique IDs + authorized repository + release governance.",
    tone: "teal" as const
  },
  {
    label: "Evidence Trail",
    value: "Audit-Ready",
    note: "Every action logs what, who, when and operational result.",
    tone: "cyan" as const
  },
  {
    label: "Corrective Actions",
    value: "Closed-loop",
    note: "PDCA cadence tracked until closure and standard update.",
    tone: "teal" as const
  }
] as const;

const CONTROL_CHIPS = [
  { label: "OSHA/ANSI/NFPA", tone: "teal" as const },
  { label: "NOM-STPS + ISO 45001/14001", tone: "gold" as const },
  { label: "Governance by role", tone: "cyan" as const },
  { label: "PHA + ATS/JSA", tone: "teal" as const },
  { label: "Version control + ID único", tone: "gold" as const },
  { label: "SmartService + ServiceLogix", tone: "cyan" as const },
  { label: "HealthRadar + ConditionScore", tone: "teal" as const },
  { label: "FailMatrix evidence loop", tone: "gold" as const }
] as const;

function hashSeed(seedText: string): number {
  let hash = 0x811c9dc5;

  for (let index = 0; index < seedText.length; index += 1) {
    hash ^= seedText.charCodeAt(index);
    hash = Math.imul(hash, 0x01000193);
  }

  return hash >>> 0;
}

function mulberry32(seed: number): () => number {
  let state = seed >>> 0;

  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let t = Math.imul(state ^ (state >>> 15), state | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function generateTrend(
  random: () => number,
  start: number,
  points: number,
  minStep: number,
  maxStep: number,
  maxDrop: number
): readonly number[] {
  const values: number[] = [start];
  const phase = random() * Math.PI * 2;

  for (let index = 1; index < points; index += 1) {
    const previous = values[index - 1] ?? start;
    const step = minStep + random() * (maxStep - minStep);
    const progress = index / (points - 1 || 1);
    const wave = Math.sin(progress * Math.PI * 1.75 + phase) * 0.45;
    const jitter = (random() - 0.5) * 0.85;
    const projected = previous + step + wave + jitter;
    const bounded = Math.max(previous - maxDrop, projected);
    const next = Number(Math.min(96, Math.max(70, bounded)).toFixed(1));
    values.push(next);
  }

  const first = values[0] ?? start;
  const last = values[values.length - 1] ?? start;
  if (last <= first) {
    values[values.length - 1] = Number((first + minStep + 1.2).toFixed(1));
  }

  return values;
}

function buildDeterministicSeries(seedText: string): DeterministicSeries {
  const random = mulberry32(hashSeed(seedText));
  const coverage = generateTrend(random, 74.2, 12, 0.55, 1.35, 0.7);
  const evidence = generateTrend(random, 73.4, 12, 0.7, 1.6, 0.7);
  const bars = BAR_LABELS.map((label, index) => {
    const base = 78 + index * 2.15;
    const value = Math.round(Math.min(93, Math.max(72, base + (random() - 0.5) * 8.4)));
    const tone: DeterministicSeries["bars"][number]["tone"] =
      index % 3 === 0 ? "teal" : index % 3 === 1 ? "gold" : "cyan";
    return {
      label,
      value,
      tone
    };
  });
  const readiness = 88 + Math.round(random() * 6);

  return {
    coverage,
    evidence,
    bars,
    readiness
  };
}

const SCREEN_02_SERIES = buildDeterministicSeries(SCREEN_02_SEED);

export function Screen02IndustrialFlowCinematic({ className }: Screen02IndustrialFlowCinematicProps) {
  return (
    <PitchSection
      id="industrial-flow"
      eyebrow="PITCH SCREEN 02"
      title="Institutional-grade Operations System"
      description="Not hero-based execution: governed, standardized, auditable and scalable multi-site control."
      className={className}
      actions={
        <div className="flex flex-wrap items-center gap-2">
          <PitchDataChip label="Control Loop" value="Plan → Execute → Verify → Improve" tone="teal" />
          <PitchDataChip label="Operational Posture" value="International-grade / audit-ready" tone="gold" />
        </div>
      }
    >
      <PitchCardGrid columns={4}>
        {SYSTEM_KPIS.map((kpi) => (
          <PitchCardGridItem
            key={kpi.label}
            title={kpi.value}
            description={kpi.note}
            kicker={kpi.label}
            tone={kpi.tone}
          />
        ))}
      </PitchCardGrid>

      <div className="grid gap-3 xl:grid-cols-[1.3fr_1fr]">
        <article className="pitch-glass-card pitch-neon-edge grid gap-3 rounded-[var(--pitch-radius-lg)] p-4">
          <header className="grid gap-1">
            <h3 className="m-0 text-lg font-semibold text-[color:var(--pitch-ink)]">
              Operational Control Loop (Plan → Execute → Verify → Improve)
            </h3>
            <p className="m-0 text-sm text-[color:var(--pitch-muted)]">
              Riesgo controlado + evidencia por defecto + mejora continua (PDCA).
            </p>
          </header>

          <div className="grid gap-3 lg:grid-cols-2">
            <PitchSparkline
              points={SCREEN_02_SERIES.coverage}
              label="Standardization Coverage"
              stroke="var(--pitch-governance-cobalt)"
              fill="var(--pitch-governance-fill)"
            />
            <PitchSparkline
              points={SCREEN_02_SERIES.evidence}
              label="Evidence Depth"
              stroke="var(--pitch-accent-amber-muted)"
              fill="var(--pitch-accent-amber-fill)"
            />
          </div>

          <PitchMiniBars
            series={SCREEN_02_SERIES.bars}
            max={100}
          />

          <PitchExpandablePanel
            title="Institutional Controls"
            subtitle="CORE governance + standards alignment + evidence by default"
            defaultOpen
          >
            <PitchKpiChipCloud
              items={CONTROL_CHIPS}
            />
          </PitchExpandablePanel>
        </article>

        <aside className="grid gap-3">
          <article className="pitch-glass-card pitch-neon-edge grid gap-2 rounded-[var(--pitch-radius-lg)] p-4">
            <h4 className="m-0 text-sm font-semibold text-[color:var(--pitch-ink)]">Operational Readiness Index</h4>
            <PitchRadialGauge
              value={SCREEN_02_SERIES.readiness}
              label="Cadence + control + evidence"
              valueLabel="OK"
              tone="teal"
              className="justify-self-center"
            />
            <p className="m-0 text-center text-xs text-[color:var(--pitch-muted)]">
              Cadence + control + evidence (audit-ready)
            </p>
          </article>

          <article className="pitch-glass-card pitch-neon-edge grid gap-2 rounded-[var(--pitch-radius-lg)] p-4">
            <h4 className="m-0 text-sm font-semibold text-[color:var(--pitch-ink)]">Institutional-grade Operations</h4>
            <p className="m-0 text-sm text-[color:var(--pitch-muted)]">
              Hitech opera bajo CORE: gobernanza, estándares internacionales y control documental.
            </p>
            <p className="m-0 text-sm text-[color:var(--pitch-muted)]">
              Cada actividad deja evidencia trazable (qué, quién, cuándo, resultado) y alimenta mejora continua
              (PDCA).
            </p>
            <p className="m-0 text-sm text-[color:var(--pitch-muted)]">
              El backbone digital convierte políticas en ejecución medible y auditable.
            </p>
            <p className="m-0 text-sm font-medium text-[color:var(--pitch-ink)]">
              Resultado: operación sólida, estandarizada y lista para escalar multi-sitio (nivel corporativo
              internacional).
            </p>
          </article>
        </aside>
      </div>
    </PitchSection>
  );
}
