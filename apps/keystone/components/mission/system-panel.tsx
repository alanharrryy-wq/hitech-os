"use client";

import type { WidgetsQueryResponse } from "@hitech/contracts";
import { Badge, EmptyState, InsetPanel, ScrollArea } from "@hitech/ui-kit";
import { useKeystoneUiStore } from "../../lib/store/ui-store";

export interface SystemPanelProps {
  readonly data: WidgetsQueryResponse | undefined;
  readonly isLoading: boolean;
  readonly isError: boolean;
}

function widgetKindTone(kind: string): "neutral" | "accent" | "success" | "warning" | "danger" {
  if (kind === "stat") {
    return "accent";
  }
  if (kind === "table") {
    return "success";
  }
  if (kind === "feed") {
    return "warning";
  }
  if (kind.includes("placeholder")) {
    return "neutral";
  }
  return "neutral";
}

export function SystemPanel({ data, isLoading, isError }: SystemPanelProps) {
  const selectedWidgetId = useKeystoneUiStore((state) => state.selectedWidgetId);
  const setSelectedWidgetId = useKeystoneUiStore((state) => state.setSelectedWidgetId);

  if (isError) {
    return (
      <EmptyState
        title="System unavailable"
        description="Widgets API route did not return valid payload."
      />
    );
  }

  if (isLoading) {
    return (
      <InsetPanel title="System" description="Widget registry and layout diagnostics">
        <p className="m-0 text-sm keystone-muted">Loading widget contracts...</p>
      </InsetPanel>
    );
  }

  const widgets = data?.widgets ?? [];
  const layoutBreakpoints = data?.layout?.breakpoints ?? [];

  return (
    <InsetPanel title="System" description="Widget inventory + layout contract summary">
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-[var(--ui-core-radius-sm)] border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] p-3">
            <p className="keystone-kicker">Widgets</p>
            <p className="keystone-stat-value">{widgets.length}</p>
            <p className="m-0 text-xs keystone-muted">Registered in widgets endpoint</p>
          </div>
          <div className="rounded-[var(--ui-core-radius-sm)] border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] p-3">
            <p className="keystone-kicker">Breakpoints</p>
            <p className="keystone-stat-value">{layoutBreakpoints.length}</p>
            <p className="m-0 text-xs keystone-muted">Layout variants validated by contracts</p>
          </div>
        </div>
        {widgets.length === 0 ? (
          <EmptyState title="No widgets" description="No widget fixtures were returned by API." />
        ) : (
          <ScrollArea className="h-[240px] pr-2">
            <div className="space-y-2">
              {widgets.map((widget) => {
                const selected = selectedWidgetId === widget.id;
                return (
                  <button
                    key={widget.id}
                    type="button"
                    className={`w-full rounded-[var(--ui-core-radius-sm)] border p-3 text-left transition-colors ${
                      selected
                        ? "border-[hsl(var(--ui-accent))] bg-[hsl(var(--ui-accent-soft))]"
                        : "border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] hover:bg-[hsl(var(--ui-surface-2))]"
                    }`}
                    onClick={() => {
                      setSelectedWidgetId(widget.id);
                    }}
                  >
                    <div className="mb-2 flex items-center justify-between gap-2">
                      <p className="m-0 text-sm font-medium">{widget.title}</p>
                      <Badge tone={widgetKindTone(widget.kind)}>{widget.kind}</Badge>
                    </div>
                    <p className="m-0 text-xs keystone-muted">{widget.id}</p>
                  </button>
                );
              })}
            </div>
          </ScrollArea>
        )}
      </div>
    </InsetPanel>
  );
}
