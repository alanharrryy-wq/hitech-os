"use client";

import { GlassCard, InsetPanel, ScrollArea } from "@hitech/ui-kit";
import type { InventoryFoundationPanelContext, SupplierLifecycle, SupplierProfile } from "./types";
import { Chip, NeonButton } from "./primitives";
import { getSupplierLifecycleTone } from "./store";

const SUPPLIER_LIFECYCLE_ORDER: readonly SupplierLifecycle[] = ["approved", "active", "blocked"];

function nextLifecycle(current: SupplierLifecycle): SupplierLifecycle {
  const index = SUPPLIER_LIFECYCLE_ORDER.indexOf(current);
  return SUPPLIER_LIFECYCLE_ORDER[(index + 1) % SUPPLIER_LIFECYCLE_ORDER.length] ?? "approved";
}

function groupSuppliersByLifecycle(suppliers: readonly SupplierProfile[]) {
  return {
    approved: suppliers.filter((supplier) => supplier.lifecycle === "approved"),
    active: suppliers.filter((supplier) => supplier.lifecycle === "active"),
    blocked: suppliers.filter((supplier) => supplier.lifecycle === "blocked")
  } as const;
}

export interface SupplierStatusPanelProps {
  readonly context: InventoryFoundationPanelContext;
}

export function SupplierStatusPanel({ context }: SupplierStatusPanelProps) {
  const { state, computed, actions } = context;
  const grouped = groupSuppliersByLifecycle(state.suppliers);
  const selected = computed.selectedSupplier;

  return (
    <GlassCard className="p-4" tone="default" backdrop="medium">
      <InsetPanel
        title="Supplier Status Panel"
        description="Approved/active/blocked suppliers with direct gate impact"
      >
        <div className="grid gap-3 lg:grid-cols-[1.2fr_1fr]">
          <div className="grid gap-3">
            <div className="grid gap-2 sm:grid-cols-3">
              <article className="rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.84)] p-2.5">
                <p className="m-0 text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
                  Approved
                </p>
                <p className="m-0 mt-1 text-lg font-semibold text-[hsl(var(--ui-text-1))]">
                  {grouped.approved.length}
                </p>
              </article>
              <article className="rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.84)] p-2.5">
                <p className="m-0 text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
                  Active
                </p>
                <p className="m-0 mt-1 text-lg font-semibold text-[hsl(var(--ui-text-1))]">
                  {grouped.active.length}
                </p>
              </article>
              <article className="rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.84)] p-2.5">
                <p className="m-0 text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
                  Blocked
                </p>
                <p className="m-0 mt-1 text-lg font-semibold text-[hsl(var(--ui-text-1))]">
                  {grouped.blocked.length}
                </p>
              </article>
            </div>

            <ScrollArea className="h-[280px] pr-2">
              <div className="grid gap-2">
                {state.suppliers.slice(0, 240).map((supplier) => (
                  <article
                    key={supplier.code}
                    className="rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.86)] p-2.5"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <button
                        type="button"
                        onClick={() => actions.setSupplierCode(supplier.code)}
                        className="cursor-pointer rounded border border-transparent px-1 text-left text-xs font-semibold text-[hsl(var(--ui-text-1))] transition-colors hover:border-[hsl(var(--ui-border-2))]"
                      >
                        {supplier.code}
                      </button>
                      <Chip tone={getSupplierLifecycleTone(supplier.lifecycle)}>
                        {supplier.lifecycle.toUpperCase()}
                      </Chip>
                    </div>
                    <p className="m-0 mt-1 text-[11px] text-[hsl(var(--ui-text-2))]">
                      QA {supplier.qaScore} | {supplier.country} | lots {supplier.activeLots}
                    </p>
                  </article>
                ))}
              </div>
            </ScrollArea>
          </div>

          <aside className="grid gap-3 rounded-xl border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-2)/0.4)] p-3">
            <p className="m-0 text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
              Selected Supplier Control
            </p>
            <p className="m-0 text-sm font-semibold text-[hsl(var(--ui-text-1))]">
              {selected?.code ?? "No supplier selected"}
            </p>
            <p className="m-0 text-xs text-[hsl(var(--ui-text-2))]">
              {selected
                ? `${selected.legalName} | Route ${selected.route} | Last audit ${selected.lastAuditDate}`
                : "Pick a supplier from the left list."}
            </p>

            {selected ? (
              <>
                <div className="grid gap-2">
                  <div className="flex items-center justify-between gap-2 rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.84)] p-2">
                    <p className="m-0 text-xs text-[hsl(var(--ui-text-2))]">Current lifecycle</p>
                    <Chip tone={getSupplierLifecycleTone(selected.lifecycle)}>
                      {selected.lifecycle.toUpperCase()}
                    </Chip>
                  </div>
                  <NeonButton
                    variant="outline"
                    onClick={() =>
                      actions.setSupplierLifecycle(selected.code, nextLifecycle(selected.lifecycle))
                    }
                  >
                    Cycle Lifecycle
                  </NeonButton>
                </div>
                <ul className="m-0 list-disc space-y-1 pl-5 text-xs text-[hsl(var(--ui-text-2))]">
                  {selected.notes.map((note) => (
                    <li key={note}>{note}</li>
                  ))}
                </ul>
              </>
            ) : null}
          </aside>
        </div>
      </InsetPanel>
    </GlassCard>
  );
}
