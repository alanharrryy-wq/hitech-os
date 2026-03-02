import { Badge, cn } from "@hitech/ui-kit";
import type { PitchHeroMetric, PitchHeroModel } from "./types";

function toneClass(tone: PitchHeroMetric["tone"]): string {
  if (tone === "gold") {
    return "border-[rgba(171,123,38,0.32)] bg-[rgba(171,123,38,0.12)] text-[color:#553E13]";
  }

  if (tone === "teal") {
    return "border-[rgba(2,111,134,0.35)] bg-[rgba(2,111,134,0.12)] text-[color:#026F86]";
  }

  if (tone === "cyan") {
    return "border-[rgba(2,167,202,0.35)] bg-[rgba(2,167,202,0.12)] text-[color:#025C6D]";
  }

  return "border-[rgba(4,18,25,0.2)] bg-[rgba(4,18,25,0.05)] text-[color:#041219]";
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
        {model.metrics.map((metric, index) => (
          <article
            key={metric.id}
            className={cn(
              "pitch-focus-ring rounded-[var(--pitch-radius-md)] border px-3 py-2 transition-shadow hover:shadow-[0_10px_20px_rgba(2,111,134,0.14)]",
              toneClass(metric.tone),
              `pitch-halo-level-${Math.max(1, Math.min(240, (index + 1) * 12))}`
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
