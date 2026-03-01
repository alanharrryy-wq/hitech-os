"use client";

import { Badge, Button, GlassCard, InsetPanel, cn } from "@hitech/ui-kit";
import { DEMO_ROLES, type DemoRole, type PitchDemoState } from "../../lib/pitch/demo-state";
import type { PitchDemoActions } from "../../lib/pitch/use-demo-state";

interface DemoToggleControlProps {
  readonly id: string;
  readonly label: string;
  readonly description: string;
  readonly checked: boolean;
  readonly onCheckedChange: (checked: boolean) => void;
}

function DemoToggleControl({
  id,
  label,
  description,
  checked,
  onCheckedChange
}: DemoToggleControlProps) {
  return (
    <label
      htmlFor={id}
      className="flex cursor-pointer items-start gap-3 rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] p-3"
    >
      <input
        id={id}
        type="checkbox"
        checked={checked}
        onChange={(event) => onCheckedChange(event.currentTarget.checked)}
        className="mt-1 h-4 w-4 accent-[hsl(var(--ui-accent))]"
      />
      <span className="grid gap-1">
        <span className="text-sm font-medium text-[hsl(var(--ui-text-1))]">{label}</span>
        <span className="text-xs leading-5 text-[hsl(var(--ui-text-3))]">{description}</span>
      </span>
    </label>
  );
}

export interface DemoControlsProps {
  readonly state: PitchDemoState;
  readonly actions: Pick<
    PitchDemoActions,
    "setRole" | "toggleSupplierStatus" | "toggleDocsComplete" | "toggleTempExcursion" | "reset"
  >;
  readonly className?: string;
}

export function DemoControls({ state, actions, className }: DemoControlsProps) {
  return (
    <GlassCard className={cn("p-4", className)} tone="default" backdrop="off">
      <InsetPanel
        title="Interactive demo controls"
        description="Deterministic toggles for role, onboarding, documents and receiving exceptions."
      >
        <form
          className="grid gap-4"
          onSubmit={(event) => event.preventDefault()}
          aria-label="Pitch demo controls"
        >
          <fieldset className="grid gap-2 border-0 p-0">
            <legend className="mb-1 text-xs uppercase tracking-[0.08em] text-[hsl(var(--ui-text-3))]">
              Role selector
            </legend>
            <label htmlFor="pitch-demo-role" className="text-sm text-[hsl(var(--ui-text-2))]">
              Active role
            </label>
            <select
              id="pitch-demo-role"
              value={state.role}
              onChange={(event) => actions.setRole(event.target.value as DemoRole)}
              className="h-10 rounded-[var(--ui-core-radius-sm)] border border-[hsl(var(--ui-border-2))] bg-[hsl(var(--ui-surface-1))] px-3 text-sm text-[hsl(var(--ui-text-1))]"
            >
              {DEMO_ROLES.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </select>
          </fieldset>

          <fieldset className="grid gap-2 border-0 p-0">
            <legend className="mb-1 text-xs uppercase tracking-[0.08em] text-[hsl(var(--ui-text-3))]">
              Runtime toggles
            </legend>
            <DemoToggleControl
              id="pitch-demo-supplier-status"
              label="Supplier status"
              description="Marks supplier onboarding as approved for all baseline suppliers."
              checked={state.supplierApproved}
              onCheckedChange={() => actions.toggleSupplierStatus()}
            />
            <DemoToggleControl
              id="pitch-demo-docs-complete"
              label="Docs complete"
              description="Completes document vault and customs-pack status for the demo flow."
              checked={state.docsComplete}
              onCheckedChange={() => actions.toggleDocsComplete()}
            />
            <DemoToggleControl
              id="pitch-demo-temp-excursion"
              label="Temp excursion"
              description="Injects a receiving exception that forces deviation and quarantine messaging."
              checked={state.tempExcursion}
              onCheckedChange={() => actions.toggleTempExcursion()}
            />
          </fieldset>

          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone={state.supplierApproved ? "success" : "neutral"}>
                Suppliers: {state.supplierApproved ? "approved" : "mixed"}
              </Badge>
              <Badge tone={state.docsComplete ? "success" : "warning"}>
                Docs: {state.docsComplete ? "complete" : "incomplete"}
              </Badge>
              <Badge tone={state.tempExcursion ? "danger" : "neutral"}>
                Excursion: {state.tempExcursion ? "active" : "off"}
              </Badge>
            </div>
            <Button variant="outline" size="sm" onClick={actions.reset}>
              Reset
            </Button>
          </div>
        </form>
      </InsetPanel>
    </GlassCard>
  );
}
