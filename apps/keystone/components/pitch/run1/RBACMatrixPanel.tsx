"use client";

import { Input, GlassCard, InsetPanel, ScrollArea } from "@hitech/ui-kit";
import type { InventoryFoundationPanelContext } from "./types";
import { Chip, DropdownField, InfoTooltip } from "./primitives";

const FILTER_OPTIONS = [
  { value: "all", label: "All gates" },
  { value: "open", label: "Open only" },
  { value: "review", label: "Review only" },
  { value: "blocked", label: "Blocked only" }
] as const;

export interface RBACMatrixPanelProps {
  readonly context: InventoryFoundationPanelContext;
}

function gateTone(gate: "open" | "review" | "blocked"): "success" | "warning" | "danger" {
  if (gate === "open") {
    return "success";
  }
  if (gate === "review") {
    return "warning";
  }
  return "danger";
}

export function RBACMatrixPanel({ context }: RBACMatrixPanelProps) {
  const { state, computed, actions } = context;

  return (
    <GlassCard className="p-4" tone="default" backdrop="medium">
      <InsetPanel title="RBAC Matrix Panel" description="Search + gate filters + why-gated reasons">
        <div className="grid gap-3 sm:grid-cols-[1fr_220px]">
          <label className="grid gap-1.5">
            <span className="text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
              Search role/capability
            </span>
            <Input
              value={state.rbacSearch}
              placeholder="operator, quarantine, release..."
              onChange={(event) => actions.setRbacSearch(event.target.value)}
            />
          </label>
          <DropdownField
            label="Gate filter"
            value={state.rbacGateFilter}
            options={FILTER_OPTIONS}
            onValueChange={(value) => actions.setRbacGateFilter(value as typeof state.rbacGateFilter)}
          />
        </div>

        <div className="mt-3 rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-2)/0.45)] p-3">
          <p className="m-0 text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
            Why gated summary
          </p>
          <ul className="m-0 mt-2 list-disc space-y-1 pl-5 text-xs text-[hsl(var(--ui-text-2))]">
            {computed.rbacGateSummary.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </div>

        <ScrollArea className="mt-3 h-[360px] pr-2">
          <div className="grid gap-3">
            {computed.filteredRbacRows.map((row) => (
              <article
                key={row.role}
                className="rounded-xl border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.88)] p-3"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <p className="m-0 text-sm font-semibold text-[hsl(var(--ui-text-1))]">
                      {row.displayName}
                    </p>
                    <InfoTooltip
                      trigger={
                        <button
                          type="button"
                          className="rounded-full border border-[hsl(var(--ui-border-2))] px-2 py-0.5 text-[10px] uppercase tracking-[0.08em] text-[hsl(var(--ui-text-3))]"
                        >
                          why
                        </button>
                      }
                      content={<p className="m-0 max-w-[280px] text-xs">{row.tooltip}</p>}
                    />
                  </div>
                  <Chip tone={gateTone(row.gate)}>{row.gate.toUpperCase()}</Chip>
                </div>

                <div className="mt-2 grid gap-2">
                  {row.capabilities.map((capability) => (
                    <div
                      key={capability.id}
                      className="rounded-md border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-2)/0.5)] p-2"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <p className="m-0 text-xs font-semibold text-[hsl(var(--ui-text-1))]">
                          {capability.label}
                        </p>
                        <Chip tone="accent">{capability.domain}</Chip>
                      </div>
                      <p className="m-0 mt-1 text-xs text-[hsl(var(--ui-text-2))]">
                        {capability.reason}
                      </p>
                    </div>
                  ))}
                </div>

                <div className="mt-2 rounded-md border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-2)/0.35)] p-2">
                  <p className="m-0 text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
                    Active gate reasons
                  </p>
                  <ul className="m-0 mt-1 list-disc space-y-1 pl-5 text-xs text-[hsl(var(--ui-text-2))]">
                    {row.reasons.map((reason) => (
                      <li key={reason}>{reason}</li>
                    ))}
                  </ul>
                </div>
              </article>
            ))}
            {computed.filteredRbacRows.length === 0 ? (
              <p className="m-0 rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-2)/0.35)] p-3 text-xs text-[hsl(var(--ui-text-2))]">
                No RBAC rows match current search/filter.
              </p>
            ) : null}
          </div>
        </ScrollArea>
      </InsetPanel>
    </GlassCard>
  );
}
