"use client";

import { GlassCard, InsetPanel } from "@hitech/ui-kit";
import type { InventoryFoundationPanelContext } from "./types";
import { Chip, NeonButton } from "./primitives";

export interface FoundationDashboardProps {
  readonly context: InventoryFoundationPanelContext;
}

export function FoundationDashboard({ context }: FoundationDashboardProps) {
  const { state, computed } = context;
  const selectedSupplier = computed.selectedSupplier;
  const readiness = computed.readiness;

  return (
    <GlassCard className="p-4" tone="default" backdrop="medium">
      <InsetPanel
        title="Foundation Dashboard"
        description="Live RBAC + supplier + vault signal fusion"
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <Chip tone={computed.foundationGate === "open" ? "success" : "warning"}>
              Foundation {computed.foundationGate.toUpperCase()}
            </Chip>
            <Chip tone={computed.supplierGate === "open" ? "success" : "danger"}>
              Supplier {computed.supplierGate.toUpperCase()}
            </Chip>
            <Chip tone={computed.canProceedToRun2 ? "success" : "warning"}>
              {computed.canProceedToRun2 ? "READY FOR RUN2" : "RUN2 BLOCKED"}
            </Chip>
          </div>
        }
      >
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <article className="rounded-xl border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.82)] p-3">
            <p className="m-0 text-[11px] uppercase tracking-[0.08em] text-[hsl(var(--ui-text-3))]">
              Runtime Role
            </p>
            <p className="m-0 mt-2 text-base font-semibold text-[hsl(var(--ui-text-1))]">
              {state.role.toUpperCase()}
            </p>
            <p className="m-0 mt-1 text-xs text-[hsl(var(--ui-text-2))]">
              RBAC filter and gate decisions recalculate immediately.
            </p>
          </article>

          <article className="rounded-xl border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.82)] p-3">
            <p className="m-0 text-[11px] uppercase tracking-[0.08em] text-[hsl(var(--ui-text-3))]">
              Selected Supplier
            </p>
            <p className="m-0 mt-2 text-sm font-semibold text-[hsl(var(--ui-text-1))]">
              {selectedSupplier?.code ?? "UNASSIGNED"}
            </p>
            <p className="m-0 mt-1 text-xs text-[hsl(var(--ui-text-2))]">
              {selectedSupplier
                ? `${selectedSupplier.country} | QA ${selectedSupplier.qaScore} | ${selectedSupplier.lifecycle.toUpperCase()}`
                : "Supplier not found in deterministic registry."}
            </p>
          </article>

          <article className="rounded-xl border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.82)] p-3">
            <p className="m-0 text-[11px] uppercase tracking-[0.08em] text-[hsl(var(--ui-text-3))]">
              Readiness Score
            </p>
            <p className="m-0 mt-2 text-base font-semibold text-[hsl(var(--ui-text-1))]">
              {readiness.percentage}%
            </p>
            <p className="m-0 mt-1 text-xs text-[hsl(var(--ui-text-2))]">
              {readiness.totalScore}/{readiness.maxScore} weighted control points.
            </p>
          </article>

          <article className="rounded-xl border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.82)] p-3">
            <p className="m-0 text-[11px] uppercase tracking-[0.08em] text-[hsl(var(--ui-text-3))]">
              Active Holds
            </p>
            <p className="m-0 mt-2 text-base font-semibold text-[hsl(var(--ui-text-1))]">
              {readiness.holdReasons.length}
            </p>
            <p className="m-0 mt-1 text-xs text-[hsl(var(--ui-text-2))]">
              Critical docs, supplier status, lot history and field completeness.
            </p>
          </article>
        </div>
        <div className="mt-3 flex items-center justify-end">
          <NeonButton variant="outline" disabled={!computed.canProceedToRun2}>
            Proceed to Shipments
          </NeonButton>
        </div>
      </InsetPanel>
    </GlassCard>
  );
}
