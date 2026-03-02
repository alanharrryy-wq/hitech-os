"use client";

import { GlassCard, InsetPanel, Input, ScrollArea } from "@hitech/ui-kit";
import type { ImportReceivingPanelContext, ShipmentControlBoardFields } from "./types";
import { Chip, DropdownField } from "./primitives";

export interface ShipmentControlBoardPanelProps {
  readonly context: ImportReceivingPanelContext;
}

function setTextField(
  context: ImportReceivingPanelContext,
  key: keyof ShipmentControlBoardFields,
  value: string
) {
  context.actions.setField(key, value);
}

export function ShipmentControlBoardPanel({ context }: ShipmentControlBoardPanelProps) {
  const { state, actions } = context;
  const fields = state.fields;

  return (
    <GlassCard className="p-4" tone="default" backdrop="medium">
      <InsetPanel
        title="Shipment Control Board Panel"
        description="Editable AWB/BL, ETA/ATA, incoterm, carrier and port fields"
      >
        <div className="grid gap-3 lg:grid-cols-2">
          <DropdownField
            label="Manifest"
            value={state.selectedManifestId}
            options={state.manifests.slice(0, 220).map((manifest) => ({
              value: manifest.id,
              label: `${manifest.id} | ${manifest.awbBl} | ${manifest.status}`
            }))}
            onChange={actions.setSelectedManifest}
          />

          <label className="grid gap-1.5">
            <span className="text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
              AWB / BL
            </span>
            <Input
              value={fields.awbBl}
              onChange={(event) => setTextField(context, "awbBl", event.target.value)}
            />
          </label>

          <label className="grid gap-1.5">
            <span className="text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
              ETA
            </span>
            <Input
              value={fields.eta}
              onChange={(event) => setTextField(context, "eta", event.target.value)}
            />
          </label>

          <label className="grid gap-1.5">
            <span className="text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
              ATA
            </span>
            <Input
              value={fields.ata}
              onChange={(event) => setTextField(context, "ata", event.target.value)}
            />
          </label>

          <DropdownField
            label="Incoterm"
            value={fields.incoterm}
            options={["EXW", "FCA", "CPT", "CIP", "DAP", "DDP"].map((item) => ({
              value: item,
              label: item
            }))}
            onChange={(value) => actions.setField("incoterm", value as ShipmentControlBoardFields["incoterm"])}
          />

          <label className="grid gap-1.5">
            <span className="text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
              Carrier
            </span>
            <Input
              value={fields.carrier}
              onChange={(event) => setTextField(context, "carrier", event.target.value)}
            />
          </label>

          <label className="grid gap-1.5">
            <span className="text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
              Port
            </span>
            <Input
              value={fields.port}
              onChange={(event) => setTextField(context, "port", event.target.value)}
            />
          </label>

          <label className="grid gap-1.5">
            <span className="text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
              Quantity Declared
            </span>
            <Input
              type="number"
              value={String(fields.quantityDeclared)}
              onChange={(event) => actions.setField("quantityDeclared", Number(event.target.value || 0))}
            />
          </label>

          <label className="grid gap-1.5">
            <span className="text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
              Quantity Received
            </span>
            <Input
              type="number"
              value={String(fields.quantityReceived)}
              onChange={(event) => actions.setField("quantityReceived", Number(event.target.value || 0))}
            />
          </label>

          <label className="grid gap-1.5">
            <span className="text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
              Lot Declared
            </span>
            <Input
              value={fields.lotDeclared}
              onChange={(event) => setTextField(context, "lotDeclared", event.target.value)}
            />
          </label>

          <label className="grid gap-1.5">
            <span className="text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
              Lot Received
            </span>
            <Input
              value={fields.lotReceived}
              onChange={(event) => setTextField(context, "lotReceived", event.target.value)}
            />
          </label>
        </div>

        <div className="mt-3 grid gap-2 rounded-xl border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-2)/0.42)] p-3">
          <button
            type="button"
            onClick={() => actions.setField("temperatureExcursion", !fields.temperatureExcursion)}
            className="flex items-center justify-between gap-2 rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.86)] px-3 py-2 text-left"
          >
            <span className="text-sm text-[hsl(var(--ui-text-1))]">Temperature excursion</span>
            <Chip tone={fields.temperatureExcursion ? "danger" : "success"}>
              {fields.temperatureExcursion ? "ON" : "OFF"}
            </Chip>
          </button>
          <ScrollArea className="h-[120px] pr-2">
            <ul className="m-0 list-disc space-y-1 pl-5 text-xs text-[hsl(var(--ui-text-2))]">
              <li>Any field change updates risk panel and next gate panel instantly.</li>
              <li>
                Quantity or lot mismatch automatically creates a deviation ticket placeholder and
                routes flow to hold.
              </li>
              <li>
                Excursion toggle forces QUARANTINE regardless of customs checklist completeness.
              </li>
            </ul>
          </ScrollArea>
        </div>
      </InsetPanel>
    </GlassCard>
  );
}
