"use client";

import { GlassCard, InsetPanel, ScrollArea } from "@hitech/ui-kit";
import type { InventoryFoundationPanelContext } from "./types";
import { Chip } from "./primitives";
import { getDocumentLifecycleTone } from "./store";

export interface DocumentVaultPanelProps {
  readonly context: InventoryFoundationPanelContext;
}

export function DocumentVaultPanel({ context }: DocumentVaultPanelProps) {
  const { state, computed, actions } = context;
  const readiness = computed.readiness;
  const holdReasons = readiness.holdReasons;
  const criticalHoldReasons = holdReasons.filter((reason) => reason.severity === "critical");

  return (
    <GlassCard className="p-4" tone="default" backdrop="medium">
      <InsetPanel
        title="Document Vault Panel"
        description="Click any document to cycle: present -> missing -> in-progress -> expired"
      >
        <div className="flex flex-wrap items-center gap-2">
          {readiness.chips.map((chip) => (
            <Chip key={chip.lifecycle} tone={chip.tone}>
              {chip.lifecycle.toUpperCase()} {chip.count}
            </Chip>
          ))}
        </div>

        <ScrollArea className="mt-3 h-[340px] pr-2">
          <div className="grid gap-2">
            {state.documents.slice(0, 260).map((document) => {
              const docState = state.documentStates[document.id];
              const lifecycle = docState?.lifecycle ?? "missing";
              return (
                <button
                  key={document.id}
                  type="button"
                  onClick={() => actions.cycleDocumentLifecycle(document.id)}
                  className="group cursor-pointer rounded-xl border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.86)] p-3 text-left transition-all hover:border-[hsl(var(--ui-accent)/0.55)] hover:shadow-[0_0_14px_hsl(var(--ui-accent)/0.14)]"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <p className="m-0 text-sm font-semibold text-[hsl(var(--ui-text-1))]">
                      {document.label}
                    </p>
                    <div className="flex items-center gap-2">
                      <Chip tone={getDocumentLifecycleTone(lifecycle)}>{lifecycle.toUpperCase()}</Chip>
                      {document.critical ? <Chip tone="danger">CRITICAL</Chip> : null}
                    </div>
                  </div>
                  <p className="m-0 mt-1 text-xs text-[hsl(var(--ui-text-2))]">
                    Owner {document.ownerRole.toUpperCase()} | Category {document.category} | Expiry{" "}
                    {document.expiryDate}
                  </p>
                  <p className="m-0 mt-1 text-[11px] text-[hsl(var(--ui-text-3))]">
                    {docState?.comment ?? "No update comment."}
                  </p>
                </button>
              );
            })}
          </div>
        </ScrollArea>

        {holdReasons.length > 0 ? (
          <div className="mt-3 grid gap-2 rounded-xl border border-[hsl(var(--ui-warning))] bg-[hsl(var(--ui-warning)/0.08)] p-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="m-0 text-sm font-semibold text-[hsl(var(--ui-text-1))]">
                HOLD: compliance gate active
              </p>
              <Chip tone={criticalHoldReasons.length > 0 ? "danger" : "warning"}>
                {criticalHoldReasons.length > 0 ? "CRITICAL HOLD" : "HOLD"}
              </Chip>
            </div>
            <ul className="m-0 list-disc space-y-1 pl-5 text-xs text-[hsl(var(--ui-text-2))]">
              {holdReasons.map((reason) => (
                <li key={reason.id}>
                  {reason.reason} Next: {reason.nextStep}
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="m-0 mt-3 rounded-xl border border-[hsl(var(--ui-success))] bg-[hsl(var(--ui-success)/0.08)] p-3 text-sm font-semibold text-[hsl(var(--ui-success))]">
            Vault clear. All critical documents are present and the hold banner is lifted.
          </p>
        )}
      </InsetPanel>
    </GlassCard>
  );
}
