"use client";

import { Input, InsetPanel, GlassCard } from "@hitech/ui-kit";
import type {
  FoundationRole,
  InventoryFoundationFields,
  InventoryFoundationPanelContext
} from "./types";
import { DropdownField, NeonButton } from "./primitives";

const ROLE_OPTIONS: readonly FoundationRole[] = ["operator", "admin", "auditor"];

export interface LiveFieldPanelProps {
  readonly context: InventoryFoundationPanelContext;
}

function updateTextField(
  context: InventoryFoundationPanelContext,
  key: keyof InventoryFoundationFields,
  value: string
) {
  context.actions.setField(key, value);
}

export function LiveFieldPanel({ context }: LiveFieldPanelProps) {
  const { state, computed, actions } = context;
  const fields = state.fields;

  return (
    <GlassCard className="p-4" tone="default" backdrop="medium">
      <InsetPanel
        title="Live Field Panel"
        description="Interactive demo controls: inputs mirror instantly into readiness, RBAC and hold logic"
      >
        <div className="grid gap-3 lg:grid-cols-2">
          <label className="grid gap-1.5">
            <span className="text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
              SKU
            </span>
            <Input
              value={fields.sku}
              onChange={(event) => updateTextField(context, "sku", event.target.value)}
            />
          </label>

          <label className="grid gap-1.5">
            <span className="text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
              Lot
            </span>
            <Input
              value={fields.lot}
              onChange={(event) => updateTextField(context, "lot", event.target.value)}
            />
          </label>

          <label className="grid gap-1.5">
            <span className="text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
              Batch
            </span>
            <Input
              value={fields.batch}
              onChange={(event) => updateTextField(context, "batch", event.target.value)}
            />
          </label>

          <label className="grid gap-1.5">
            <span className="text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
              Barcode
            </span>
            <Input
              value={fields.barcode}
              onChange={(event) => updateTextField(context, "barcode", event.target.value)}
            />
          </label>

          <DropdownField
            label="Supplier"
            value={state.selectedSupplierCode}
            options={state.suppliers.slice(0, 200).map((supplier) => ({
              value: supplier.code,
              label: `${supplier.code} | ${supplier.lifecycle.toUpperCase()} | QA ${supplier.qaScore}`
            }))}
            onValueChange={actions.setSupplierCode}
          />

          <DropdownField
            label="Incoterm"
            value={fields.incoterm}
            options={["EXW", "FCA", "CPT", "CIP", "DAP", "DDP"].map((value) => ({
              value,
              label: value
            }))}
            onValueChange={(value) => actions.setField("incoterm", value as InventoryFoundationFields["incoterm"])}
          />

          <DropdownField
            label="Temperature Profile"
            value={fields.temperatureProfile}
            options={["2C-8C", "15C-25C", "-20C", "-70C", "Ambient Controlled"].map((value) => ({
              value,
              label: value
            }))}
            onValueChange={(value) =>
              actions.setField("temperatureProfile", value as InventoryFoundationFields["temperatureProfile"])
            }
          />

          <DropdownField
            label="Storage Condition"
            value={fields.storageCondition}
            options={["Cold Room A", "Cold Room B", "Ambient Cage", "Quarantine Bay", "DEA Cage"].map(
              (value) => ({
                value,
                label: value
              })
            )}
            onValueChange={(value) =>
              actions.setField("storageCondition", value as InventoryFoundationFields["storageCondition"])
            }
          />
        </div>

        <div className="mt-4 grid gap-3 rounded-xl border border-[hsl(var(--ui-border-1))] bg-[linear-gradient(125deg,hsl(var(--ui-surface-1)/0.95),hsl(var(--ui-surface-2)/0.84))] p-3">
          <p className="m-0 text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
            Runtime Role Switcher
          </p>
          <div className="flex flex-wrap items-center gap-2">
            {ROLE_OPTIONS.map((role) => (
              <NeonButton
                key={role}
                variant={state.role === role ? "solid" : "outline"}
                onClick={() => actions.setRole(role)}
              >
                {role.toUpperCase()}
              </NeonButton>
            ))}
          </div>
          <p className="m-0 text-xs text-[hsl(var(--ui-text-2))]">
            Current role impact:{" "}
            {computed.rbacGateSummary[0]
              ? computed.rbacGateSummary[0]
              : "No RBAC summary available for this role."}
          </p>
        </div>
      </InsetPanel>
    </GlassCard>
  );
}
