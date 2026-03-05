"use client";

import type { ActivityQueryResponse } from "@hitech/contracts";
import { Badge, EmptyState, InsetPanel, ScrollArea } from "@hitech/ui-kit";

export interface ActivityPanelProps {
  readonly data: ActivityQueryResponse | undefined;
  readonly isLoading: boolean;
  readonly isError: boolean;
}

function formatActivityTimestamp(value: string): string {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed
    .toISOString()
    .replace("T", " ")
    .replace(/\.\d{3}Z$/, " UTC");
}

function severityTone(severity: string): "neutral" | "accent" | "success" | "warning" | "danger" {
  if (severity === "critical" || severity === "error") {
    return "danger";
  }
  if (severity === "warn") {
    return "warning";
  }
  if (severity === "info") {
    return "accent";
  }
  if (severity === "debug") {
    return "neutral";
  }
  return "neutral";
}

export function ActivityPanel({ data, isLoading, isError }: ActivityPanelProps) {
  if (isError) {
    return <EmptyState title="Activity unavailable" description="Could not load activity feed." />;
  }

  if (isLoading) {
    return (
      <InsetPanel title="Activity" description="Live event stream">
        <p className="m-0 text-sm keystone-muted">Loading activity feed...</p>
      </InsetPanel>
    );
  }

  const items = data?.items ?? [];

  if (items.length === 0) {
    return <EmptyState title="No activity" description="No events in current fixture set." />;
  }

  return (
    <InsetPanel title="Activity" description="Severity + actor + metadata snapshot">
      <ScrollArea className="h-[320px] pr-2">
        <div className="space-y-3">
          {items.map((item) => (
            <article
              key={item.id}
              className="rounded-[var(--ui-core-radius-sm)] border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1))] p-3"
            >
              <div className="mb-1 flex flex-wrap items-center gap-2">
                <Badge tone={severityTone(item.severity)}>{item.severity}</Badge>
                <span className="text-xs keystone-muted">{item.type}</span>
                <span className="ml-auto text-xs keystone-muted">
                  {formatActivityTimestamp(item.createdAt)}
                </span>
              </div>
              <p className="m-0 text-sm font-medium text-[hsl(var(--ui-text-1))]">{item.title}</p>
              <p className="m-0 mt-1 text-sm keystone-muted">{item.message}</p>
              <p className="m-0 mt-2 text-xs keystone-muted">Actor: {item.actor.displayName}</p>
            </article>
          ))}
        </div>
      </ScrollArea>
    </InsetPanel>
  );
}
