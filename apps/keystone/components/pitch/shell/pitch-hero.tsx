import { Badge, cn } from "@hitech/ui-kit";
import type { PitchHeroMetric, PitchHeroModel } from "./types";

function toneClass(tone: PitchHeroMetric["tone"]): string {
  if (tone === "gold") {
    return "pitch-kpi-card--amber";
  }

  if (tone === "teal") {
    return "pitch-kpi-card--teal";
  }

  if (tone === "cyan") {
    return "pitch-kpi-card--violet";
  }

  return "pitch-kpi-card--neutral";
}

export interface PitchHeroProps {
  readonly model: PitchHeroModel;
  readonly className?: string;
}

export function PitchHero({ model, className }: PitchHeroProps) {
  return (
    <header className={cn("pitch-glass-card pitch-neon-edge p-5 lg:p-6", className)}>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="grid gap-3">
          <div className="flex flex-wrap items-center gap-2">
            <Badge>{model.kicker}</Badge>
            <Badge tone="accent">{model.deckIdentity.label}</Badge>
            <span className="rounded-full border border-[rgba(2,111,134,0.25)] px-2 py-1 text-xs text-[color:rgba(4,18,25,0.78)]">
              {model.deckIdentity.value}
            </span>
          </div>
          <h1 className="pitch-hero-title">{model.title}</h1>
          <p className="pitch-hero-subtitle">{model.subtitle}</p>
        </div>
      </div>

      <div className="mt-5 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
        {model.metrics.map((metric) => (
          <article
            key={metric.id}
            className={cn(
              "pitch-kpi-card pitch-focus-ring rounded-[var(--pitch-radius-md)] border px-3 py-2",
              toneClass(metric.tone),
              metric.id === "stage-2" ? "pitch-stage2-kpi-halo" : undefined
            )}
          >
            <p className="m-0 text-[0.68rem] uppercase tracking-[0.11em]">{metric.label}</p>
            <p className="m-0 mt-1 text-base font-semibold">{metric.value}</p>
          </article>
        ))}
      </div>
    </header>
  );
}
