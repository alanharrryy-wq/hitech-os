"use client";

import type { PitchScreen05 } from "@hitech/contracts";
import type { BadgeProps } from "@hitech/ui-kit";
import { Badge, Button, GlassCard, Grid, GridItem, InsetPanel } from "@hitech/ui-kit";
import {
  DEMO_DOCUMENTS,
  formatDocumentLifecycleLabel,
  type DemoDocumentLifecycle
} from "../../lib/pitch/demo-state";
import { BulletList } from "./bullet-list";
import { FeatureCardGrid } from "./feature-card-grid";
import { KpiRow } from "./kpi-row";
import { PitchDemoControlPanel } from "./pitch-demo-control-panel";
import { PitchHeader } from "./pitch-header";
import { toInventoryFoundationModel } from "./types";
import { usePitchDemoController } from "./use-pitch-demo-controller";

type PitchStatus =
  PitchScreen05["foundationStatus"]["rbacMatrixSnapshot"]["rows"][number]["status"];
type DocumentLifecycle = ReturnType<
  typeof toInventoryFoundationModel
>["documentVaultBaseline"]["checklist"][number]["lifecycle"];

const STATUS_TONE: Record<PitchStatus, NonNullable<BadgeProps["tone"]>> = {
  DONE: "success",
  IN_PROGRESS: "warning",
  PENDING: "neutral",
  MISSING: "danger"
};

const LIFECYCLE_TONE: Record<DocumentLifecycle, NonNullable<BadgeProps["tone"]>> = {
  present: "success",
  missing: "danger",
  expired: "warning"
};

const DEMO_LIFECYCLE_TONE: Record<DemoDocumentLifecycle, NonNullable<BadgeProps["tone"]>> = {
  PRESENT: "success",
  MISSING: "danger",
  EXPIRED: "warning"
};

function statusLabel(status: PitchStatus): string {
  return status.toLowerCase().replaceAll("_", " ");
}

export interface ScreenInventoryFoundationProps {
  readonly screen: PitchScreen05;
}

export function ScreenInventoryFoundation({ screen }: ScreenInventoryFoundationProps) {
  const model = toInventoryFoundationModel(screen);
  const demo = usePitchDemoController({
    documents: {
      IMPORT_PERMIT: "MISSING"
    }
  });

  const isAdmin = demo.affordances.canApproveRelease;
  const supplierBlocked = demo.state.supplierStatus === "BLOCKED";
  const criticalDocumentIssues = DEMO_DOCUMENTS.filter(
    (document) => demo.state.documents[document.id] !== "PRESENT"
  );
  const hasHold = criticalDocumentIssues.length > 0;

  const readinessKpis = [
    ...model.readinessKpis,
    {
      label: "Runtime role",
      value: demo.state.role.toUpperCase(),
      note: isAdmin ? "Approve/Release controls enabled" : "Approve/Release controls disabled"
    },
    {
      label: "Supplier gate",
      value: demo.state.supplierStatus,
      note: supplierBlocked ? "Proceed CTA blocked" : "Proceed CTA enabled"
    }
  ];

  return (
    <Grid cols={12} gap="md">
      <GridItem span={12}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <PitchHeader
            model={{
              eyebrow: "PITCH SCREEN 5",
              orderLabel: "05",
              title: model.title,
              subtitle: "Interactive demo for RBAC, supplier status and document vault gating"
            }}
          />
        </GlassCard>
      </GridItem>

      <GridItem span={12}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <PitchDemoControlPanel
            state={demo.state}
            onRoleChange={demo.setRole}
            onSupplierStatusChange={demo.setSupplierStatus}
            onToggleDocumentLifecycle={demo.toggleDocumentLifecycle}
            onTempExcursionChange={demo.setTempExcursion}
            extraActions={
              <div className="flex flex-wrap items-center justify-end gap-2">
                <Badge tone={isAdmin ? "success" : "warning"}>
                  {isAdmin ? "Admin controls unlocked" : "Admin controls locked"}
                </Badge>
                <Badge tone={supplierBlocked ? "danger" : "success"}>
                  Supplier {demo.state.supplierStatus}
                </Badge>
                <Badge tone={hasHold ? "warning" : "success"}>{hasHold ? "HOLD" : "CLEAR"}</Badge>
              </div>
            }
          />
        </GlassCard>
      </GridItem>

      <GridItem span={12}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <InsetPanel title="Foundation readiness" description="RUN 1 static baseline KPIs">
            <KpiRow
              className="lg:grid-cols-5 xl:grid-cols-5"
              items={readinessKpis.map((kpi) => ({
                label: kpi.label,
                value: kpi.value,
                note: kpi.note
              }))}
            />
          </InsetPanel>
        </GlassCard>
      </GridItem>

      <GridItem span={12} spanLg={7}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <InsetPanel title={model.rbacMatrix.heading} description="RBAC matrix snapshot (3 roles)">
            <div className="grid gap-3">
              {model.rbacMatrix.rows.map((row) => (
                <article
                  key={row.role}
                  className="rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] p-3"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <p className="m-0 text-sm font-semibold text-[hsl(var(--ui-text-1))]">
                      {row.role}
                    </p>
                    <Badge tone={STATUS_TONE[row.status]}>{statusLabel(row.status)}</Badge>
                  </div>
                  <BulletList
                    bullets={row.permissions}
                    className="mt-2"
                    itemClassName="text-xs leading-5 text-[hsl(var(--ui-text-2))]"
                  />
                  <div className="mt-3 flex flex-wrap items-center gap-2">
                    <Button variant="subtle" size="sm" disabled={!isAdmin}>
                      Approve
                    </Button>
                    <Button variant="outline" size="sm" disabled={!isAdmin}>
                      Release
                    </Button>
                    {!isAdmin ? (
                      <Badge tone="warning">Admin role required</Badge>
                    ) : (
                      <Badge tone="success">Admin role active</Badge>
                    )}
                  </div>
                </article>
              ))}
            </div>
          </InsetPanel>
        </GlassCard>
      </GridItem>

      <GridItem span={12} spanLg={5}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <InsetPanel title={model.suppliers.heading} description="Approved vs Blocked">
            <div className="grid gap-3 sm:grid-cols-2">
              <section className="rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] p-3">
                <div className="flex items-center justify-between gap-2">
                  <p className="m-0 text-sm font-semibold text-[hsl(var(--ui-text-1))]">Approved</p>
                  <Badge tone="success">{model.suppliers.approved.length}</Badge>
                </div>
                <ul className="m-0 mt-2 grid list-none gap-2 p-0">
                  {model.suppliers.approved.map((supplier) => (
                    <li key={supplier} className="text-xs text-[hsl(var(--ui-text-2))]">
                      {supplier}
                    </li>
                  ))}
                  {model.suppliers.approved.length === 0 ? (
                    <li className="text-xs text-[hsl(var(--ui-text-3))]">No approved suppliers</li>
                  ) : null}
                </ul>
              </section>

              <section className="rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] p-3">
                <div className="flex items-center justify-between gap-2">
                  <p className="m-0 text-sm font-semibold text-[hsl(var(--ui-text-1))]">Blocked</p>
                  <Badge tone="danger">{model.suppliers.blocked.length}</Badge>
                </div>
                <ul className="m-0 mt-2 grid list-none gap-2 p-0">
                  {model.suppliers.blocked.map((supplier) => (
                    <li key={supplier} className="text-xs text-[hsl(var(--ui-text-2))]">
                      {supplier}
                    </li>
                  ))}
                  {model.suppliers.blocked.length === 0 ? (
                    <li className="text-xs text-[hsl(var(--ui-text-3))]">No blocked suppliers</li>
                  ) : null}
                </ul>
              </section>
            </div>
          </InsetPanel>
        </GlassCard>
      </GridItem>

      <GridItem span={12} spanLg={6}>
        <GlassCard className="p-4" tone="default" backdrop="off">
          <InsetPanel
            title={model.productsSkuBaseline.heading}
            description="Products/SKU baseline placeholders"
          >
            <FeatureCardGrid
              features={model.productsSkuBaseline.fields.map(
                (field) => `${field.label}: ${field.value}`
              )}
            />
          </InsetPanel>
        </GlassCard>
      </GridItem>

      <GridItem span={12} spanLg={6}>
        <GlassCard className="p-4" tone="muted" backdrop="off">
          <InsetPanel
            title={model.documentVaultBaseline.heading}
            description="Checklist with lifecycle chips"
          >
            <div className="grid gap-2">
              {DEMO_DOCUMENTS.map((document) => {
                const lifecycle = demo.state.documents[document.id];
                return (
                  <article
                    key={document.id}
                    className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] p-3"
                  >
                    <p className="m-0 text-sm text-[hsl(var(--ui-text-1))]">{document.label}</p>
                    <div className="flex items-center gap-2">
                      <Badge tone={DEMO_LIFECYCLE_TONE[lifecycle]}>
                        {formatDocumentLifecycleLabel(lifecycle)}
                      </Badge>
                      {document.critical ? <Badge tone="accent">critical</Badge> : null}
                    </div>
                  </article>
                );
              })}
              {model.documentVaultBaseline.checklist.map((item) => (
                <article
                  key={item.document}
                  className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] p-3"
                >
                  <p className="m-0 text-sm text-[hsl(var(--ui-text-1))]">{item.document}</p>
                  <div className="flex items-center gap-2">
                    <Badge tone={LIFECYCLE_TONE[item.lifecycle]}>{item.lifecycle}</Badge>
                    <Badge tone={STATUS_TONE[item.status]}>{statusLabel(item.status)}</Badge>
                  </div>
                </article>
              ))}
            </div>
            {hasHold ? (
              <div className="mt-3 rounded-lg border border-[hsl(var(--ui-warning))] bg-[hsl(var(--ui-warning)/0.08)] p-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="m-0 text-sm font-semibold text-[hsl(var(--ui-text-1))]">
                    HOLD: critical document compliance
                  </p>
                  <Badge tone="warning">HOLD</Badge>
                </div>
                <ul className="m-0 mt-2 list-disc space-y-1 pl-5 text-xs text-[hsl(var(--ui-text-2))]">
                  {criticalDocumentIssues.map((issue) => (
                    <li key={issue.id}>
                      {issue.label} is{" "}
                      {formatDocumentLifecycleLabel(demo.state.documents[issue.id])}
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </InsetPanel>
        </GlassCard>
      </GridItem>

      <GridItem span={12}>
        <GlassCard className="p-4" tone={supplierBlocked ? "raised" : "default"} backdrop="off">
          <InsetPanel
            title="Proceed gate"
            description="Supplier status controls whether shipment flow can continue"
            actions={
              <Badge tone={supplierBlocked ? "danger" : "success"}>
                {supplierBlocked ? "BLOCKED" : "OPEN"}
              </Badge>
            }
          >
            {supplierBlocked ? (
              <p className="m-0 rounded-lg border border-[hsl(var(--ui-danger))] bg-[hsl(var(--ui-danger)/0.08)] p-3 text-sm font-semibold text-[hsl(var(--ui-danger))]">
                Supplier is BLOCKED. Proceed to Shipments is disabled until status returns to
                APPROVED.
              </p>
            ) : (
              <p className="m-0 text-sm text-[hsl(var(--ui-text-2))]">
                Supplier is approved. Shipment workflow can continue to Screen 06.
              </p>
            )}
            <div className="mt-3">
              <Button disabled={!demo.affordances.canProceedToShipments}>
                Proceed to Shipments
              </Button>
            </div>
          </InsetPanel>
        </GlassCard>
      </GridItem>
    </Grid>
  );
}
