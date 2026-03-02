"use client";

import { useMemo, useState } from "react";
import { Badge } from "@hitech/ui-kit";
import { buildScreen03ViewModel } from "../../../lib/pitch/deck-view-model";
import { PitchBulletCards } from "../layout/pitch-bullet-cards";
import { PitchCardGrid, PitchCardGridItem } from "../layout/pitch-card-grid";
import { PitchDataChip } from "../layout/pitch-data-chip";
import { PitchExpandablePanel } from "../layout/pitch-expandable-panel";
import { PitchSection } from "../layout/pitch-section";
import { PitchKpiChipCloud } from "../visuals/pitch-kpi-chip-cloud";
import { PitchMiniBars } from "../visuals/pitch-mini-bars";

export interface Screen03HiTechOsCinematicProps {
  readonly className?: string;
}

type RevealMode = "control" | "traceability" | "history";

const MODE_TO_CATEGORY: Record<RevealMode, string[]> = {
  control: ["operation", "quality"],
  traceability: ["traceability", "visibility"],
  history: ["operation", "vertical", "traceability"]
};

function modeLabel(mode: RevealMode): string {
  if (mode === "control") {
    return "Control";
  }

  if (mode === "traceability") {
    return "Traceability";
  }

  return "History";
}

export function Screen03HiTechOsCinematic({ className }: Screen03HiTechOsCinematicProps) {
  const model = buildScreen03ViewModel();
  const [mode, setMode] = useState<RevealMode>("control");

  const filtered = useMemo(() => {
    const categories = MODE_TO_CATEGORY[mode];
    return model.features.filter((feature) => categories.includes(feature.category));
  }, [mode, model.features]);

  return (
    <PitchSection
      id="hitech-os"
      eyebrow={model.kicker}
      title={model.title}
      description="Capacidades premium de plataforma con toggles interactivos de control, trazabilidad e historial."
      className={className}
      actions={
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone="accent">Platform Story</Badge>
          <PitchDataChip label="Capabilities" value={String(model.features.length)} tone="cyan" />
        </div>
      }
    >
      <div className="pitch-glass-card pitch-neon-edge grid gap-3 rounded-[var(--pitch-radius-lg)] p-4">
        <header className="grid gap-1">
          <h3 className="m-0 text-lg font-semibold text-[color:var(--pitch-ink)]">Interactive reveal</h3>
          <p className="m-0 text-sm text-[color:rgba(4,18,25,0.74)]">
            Alterna la narrativa para mostrar ángulos diferentes sin mutar copy contractual.
          </p>
        </header>

        <div className="flex flex-wrap items-center gap-2">
          {(["control", "traceability", "history"] as const).map((candidate) => {
            const active = mode === candidate;
            return (
              <button
                key={candidate}
                type="button"
                onClick={() => setMode(candidate)}
                className={`pitch-focus-ring rounded-full border px-3 py-1 text-xs font-semibold transition-colors ${
                  active
                    ? "border-[rgba(2,167,202,0.5)] bg-[rgba(2,167,202,0.16)] text-[color:#026F86]"
                    : "border-[rgba(2,111,134,0.24)] bg-[rgba(255,255,255,0.7)] text-[color:rgba(4,18,25,0.72)]"
                }`}
                aria-pressed={active}
              >
                {modeLabel(candidate)}
              </button>
            );
          })}
        </div>

        <PitchBulletCards bullets={filtered.map((feature) => feature.text)} tone="cyan" />
        <p className="sr-only">{model.features.map((feature) => feature.text).join(" | ")}</p>
      </div>

      <PitchCardGrid columns={3}>
        <PitchCardGridItem
          title="Capability tiles"
          description="Glass + specular cards for key features"
          kicker="Tiles"
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
          title="Category spread"
          description="How features distribute across capability clusters"
          kicker="Mix"
          tone="teal"
        >
          <PitchMiniBars
            series={Object.entries(model.derived.byCategory).map(([key, value], index) => ({
              label: key,
              value,
              tone: index % 2 === 0 ? "teal" : "gold"
            }))}
            max={4}
          />
        </PitchCardGridItem>

        <PitchCardGridItem
          title="Platform story"
          description="Narrative line anchored to contractual copy"
          kicker="Narrative"
          tone="gold"
        >
          <p className="m-0 text-sm leading-6 text-[color:rgba(4,18,25,0.78)]">{model.strongLine}</p>
        </PitchCardGridItem>
      </PitchCardGrid>

      <PitchExpandablePanel title="Control room emphasis" subtitle="Pharma control readiness" defaultOpen>
        <ul className="m-0 list-disc space-y-1 pl-5 text-sm text-[color:rgba(4,18,25,0.76)]">
          <li>Control: dashboard operativo y alertas preventivas automáticas.</li>
          <li>Traceability: historial técnico y calibración certificada CRS.</li>
          <li>History: panel cliente transparente y modo Industria Farmacéutica.</li>
        </ul>
      </PitchExpandablePanel>
    </PitchSection>
  );
}
