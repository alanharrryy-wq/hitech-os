"use client";

import { GlassCard, InsetPanel } from "@hitech/ui-kit";
import type { InventoryFoundationPanelContext } from "./types";
import { Chip } from "./primitives";

export interface ReadinessScorePanelProps {
  readonly context: InventoryFoundationPanelContext;
}

function toneByPercentage(percentage: number): "success" | "warning" | "danger" {
  if (percentage >= 75) {
    return "success";
  }
  if (percentage >= 55) {
    return "warning";
  }
  return "danger";
}

export function ReadinessScorePanel({ context }: ReadinessScorePanelProps) {
  const readiness = context.computed.readiness;
  const ringColor =
    readiness.percentage >= 75
      ? "hsl(var(--ui-success))"
      : readiness.percentage >= 55
        ? "hsl(var(--ui-warning))"
        : "hsl(var(--ui-danger))";

  return (
    <GlassCard className="p-4" tone="default" backdrop="medium">
      <InsetPanel
        title="Readiness Score Panel"
        description="Deterministic weighted breakdown from live field/document/supplier gates"
      >
        <div className="grid gap-4 lg:grid-cols-[220px_1fr]">
          <div className="grid place-items-center">
            <div
              className="relative grid h-44 w-44 place-items-center rounded-full border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.85)] transition-all duration-300"
              style={{
                backgroundImage: `conic-gradient(${ringColor} 0 ${readiness.percentage}%, hsl(var(--ui-surface-3)) ${readiness.percentage}% 100%)`
              }}
            >
              <div className="grid h-32 w-32 place-items-center rounded-full bg-[hsl(var(--ui-surface-1))]">
                <p className="m-0 text-3xl font-semibold text-[hsl(var(--ui-text-1))]">
                  {readiness.percentage}
                </p>
                <p className="m-0 -mt-1 text-[11px] uppercase tracking-[0.12em] text-[hsl(var(--ui-text-3))]">
                  readiness
                </p>
              </div>
            </div>
            <div className="mt-3 flex items-center justify-center gap-2">
              <Chip tone={toneByPercentage(readiness.percentage)}>
                {readiness.totalScore}/{readiness.maxScore}
              </Chip>
              <Chip tone={context.computed.canProceedToRun2 ? "success" : "warning"}>
                {context.computed.canProceedToRun2 ? "Proceed gate open" : "Proceed gate hold"}
              </Chip>
            </div>
          </div>

          <div className="grid gap-2">
            {readiness.breakdown.map((item) => (
              <article
                key={item.id}
                className="rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.88)] p-3"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="m-0 text-sm font-semibold text-[hsl(var(--ui-text-1))]">
                    {item.label}
                  </p>
                  <Chip tone={item.score >= item.maxScore * 0.7 ? "success" : "warning"}>
                    {item.score}/{item.maxScore}
                  </Chip>
                </div>
                <p className="m-0 mt-1 text-xs text-[hsl(var(--ui-text-2))]">{item.reason}</p>
                <p className="m-0 mt-1 text-[11px] text-[hsl(var(--ui-text-3))]">
                  Next: {item.nextAction}
                </p>
              </article>
            ))}
          </div>
        </div>
      </InsetPanel>
    </GlassCard>
  );
}
