"use client";

import type { ReactNode } from "react";
import type { BadgeProps } from "@hitech/ui-kit";
import { Badge, Button, InsetPanel, cn } from "@hitech/ui-kit";
import {
  DEMO_DOCUMENTS,
  formatDocumentLifecycleLabel,
  formatRoleLabel,
  type DemoDocumentId,
  type DemoDocumentLifecycle,
  type DemoRole,
  type DemoSupplierStatus,
  type PitchDemoState
} from "../../lib/pitch/demo-state";

const DOCUMENT_TONE: Record<DemoDocumentLifecycle, NonNullable<BadgeProps["tone"]>> = {
  PRESENT: "success",
  MISSING: "danger",
  EXPIRED: "warning"
};

const CONTROL_ROLES: readonly DemoRole[] = ["admin", "operator", "auditor"];
const CONTROL_SUPPLIER_STATUSES: readonly DemoSupplierStatus[] = ["APPROVED", "BLOCKED"];

const SUPPLIER_TONE: Record<DemoSupplierStatus, NonNullable<BadgeProps["tone"]>> = {
  ACTIVE: "success",
  APPROVED: "success",
  BLOCKED: "danger"
};

export interface PitchDemoControlPanelProps {
  readonly state: PitchDemoState;
  readonly onRoleChange: (role: DemoRole) => void;
  readonly onSupplierStatusChange: (status: DemoSupplierStatus) => void;
  readonly onToggleDocumentLifecycle: (documentId: DemoDocumentId) => void;
  readonly onTempExcursionChange: (nextValue: boolean) => void;
  readonly title?: string;
  readonly description?: string;
  readonly extraActions?: ReactNode;
  readonly className?: string;
}

function roleButtonClass(selected: boolean): string {
  return selected
    ? "border-[hsl(var(--ui-accent))] bg-[hsl(var(--ui-accent-soft))] text-[hsl(var(--ui-accent))]"
    : "border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))]";
}

export function PitchDemoControlPanel({
  state,
  onRoleChange,
  onSupplierStatusChange,
  onToggleDocumentLifecycle,
  onTempExcursionChange,
  title = "Interactive demo controls",
  description = "In-memory deterministic controls only. No backend writes.",
  extraActions,
  className
}: PitchDemoControlPanelProps) {
  return (
    <InsetPanel
      className={cn("grid gap-4", className)}
      title={title}
      description={description}
      actions={extraActions}
    >
      <section className="grid gap-2">
        <p className="m-0 text-xs uppercase tracking-[0.08em] text-[hsl(var(--ui-text-3))]">Role</p>
        <div className="flex flex-wrap gap-2">
          {CONTROL_ROLES.map((role) => (
            <Button
              key={role}
              variant="outline"
              size="sm"
              className={roleButtonClass(state.role === role)}
              onClick={() => onRoleChange(role)}
            >
              {formatRoleLabel(role)}
            </Button>
          ))}
        </div>
      </section>

      <section className="grid gap-2">
        <p className="m-0 text-xs uppercase tracking-[0.08em] text-[hsl(var(--ui-text-3))]">
          Supplier status
        </p>
        <div className="flex flex-wrap items-center gap-2">
          {CONTROL_SUPPLIER_STATUSES.map((status) => {
            const active = state.supplierStatus === status;
            return (
              <Button
                key={status}
                variant={active ? "subtle" : "outline"}
                size="sm"
                className={cn(
                  active ? "border-[hsl(var(--ui-border-2))] font-semibold" : undefined
                )}
                onClick={() => onSupplierStatusChange(status)}
              >
                {status}
              </Button>
            );
          })}
          <Badge tone={SUPPLIER_TONE[state.supplierStatus]}>{state.supplierStatus}</Badge>
        </div>
      </section>

      <section className="grid gap-2">
        <p className="m-0 text-xs uppercase tracking-[0.08em] text-[hsl(var(--ui-text-3))]">
          Temperature excursion
        </p>
        <div className="flex items-center gap-2">
          <Button
            variant={state.tempExcursion ? "solid" : "outline"}
            size="sm"
            className={cn(
              state.tempExcursion
                ? "border-[hsl(var(--ui-danger))] bg-[hsl(var(--ui-danger))] text-white hover:bg-[hsl(var(--ui-danger)/0.9)]"
                : undefined
            )}
            onClick={() => onTempExcursionChange(!state.tempExcursion)}
          >
            {state.tempExcursion ? "Excursion active" : "Excursion clear"}
          </Button>
          <Badge tone={state.tempExcursion ? "danger" : "success"}>
            {state.tempExcursion ? "ON" : "OFF"}
          </Badge>
        </div>
      </section>

      <section className="grid gap-2">
        <p className="m-0 text-xs uppercase tracking-[0.08em] text-[hsl(var(--ui-text-3))]">
          Document vault toggles
        </p>
        <div className="grid gap-2 md:grid-cols-3">
          {DEMO_DOCUMENTS.map((document) => {
            const lifecycle = state.documents[document.id];
            return (
              <Button
                key={document.id}
                variant="outline"
                className="h-auto items-start justify-between gap-3 p-3 text-left"
                onClick={() => onToggleDocumentLifecycle(document.id)}
              >
                <span className="grid gap-1">
                  <span className="text-sm font-semibold text-[hsl(var(--ui-text-1))]">
                    {document.label}
                  </span>
                  <span className="text-xs text-[hsl(var(--ui-text-3))]">
                    Click to cycle PRESENT → MISSING → EXPIRED
                  </span>
                </span>
                <Badge tone={DOCUMENT_TONE[lifecycle]}>
                  {formatDocumentLifecycleLabel(lifecycle)}
                </Badge>
              </Button>
            );
          })}
        </div>
      </section>
    </InsetPanel>
  );
}
