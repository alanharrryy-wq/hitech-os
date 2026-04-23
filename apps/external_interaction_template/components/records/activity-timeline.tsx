"use client";

import { Clock3, FileDiff, RefreshCw, Send } from "lucide-react";

import { EmptyState } from "@components/ui/empty-state";
import { StateBadge } from "@components/ui/state-badge";
import { type DispatchJob, type Submission, type SyncEvent } from "@/lib/core/types";
import { useT } from "@/lib/i18n/use-t";
import { createTimelineEntries } from "@/lib/ui/record-contracts";
import { formatDateTime } from "@/lib/utils";

export interface ActivityTimelineProps {
  submissions?: Submission[];
  syncEvents?: SyncEvent[];
  dispatchJobs?: DispatchJob[];
  emptyTitle?: string;
  emptyDescription?: string;
  className?: string;
}

function iconForKind(kind: "submission" | "dispatch" | "sync") {
  switch (kind) {
    case "submission":
      return <FileDiff className="h-4 w-4" />;
    case "dispatch":
      return <Send className="h-4 w-4" />;
    case "sync":
      return <RefreshCw className="h-4 w-4" />;
    default:
      return <Clock3 className="h-4 w-4" />;
  }
}

function parseDetail(detail: string): Array<{ id: string; label?: string; value: string }> {
  return detail
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line, index) => {
      const separatorIndex = line.indexOf(": ");
      if (separatorIndex > 0) {
        return {
          id: `line-${index}`,
          label: line.slice(0, separatorIndex),
          value: line.slice(separatorIndex + 2)
        };
      }
      return {
        id: `line-${index}`,
        value: line
      };
    });
}

export function ActivityTimeline({
  submissions = [],
  syncEvents = [],
  dispatchJobs = [],
  emptyTitle,
  emptyDescription,
  className
}: ActivityTimelineProps) {
  const t = useT();
  const events = createTimelineEntries({ submissions, syncEvents, dispatchJobs });
  const resolvedEmptyTitle = emptyTitle ?? t("timeline.empty.title");
  const resolvedEmptyDescription = emptyDescription ?? t("timeline.empty.description");

  if (events.length === 0) {
    return <EmptyState title={resolvedEmptyTitle} description={resolvedEmptyDescription} compact className={className} />;
  }

  return (
    <div className={className}>
      <ol className="grid gap-2.5">
        {events.map((event, index) => (
          <li key={event.id} className="relative pl-10">
            {index < events.length - 1 ? (
              <div
                className="pointer-events-none absolute left-[0.9rem] top-9 h-[calc(100%-0.9rem)] w-px"
                style={{ background: "linear-gradient(to bottom, var(--theme-table-divider), var(--theme-table-divider), transparent)" }}
              />
            ) : null}
            <div className="surface-muted absolute left-0 top-1 inline-flex h-7 w-7 items-center justify-center text-accent">
              {iconForKind(event.kind)}
            </div>
            <div className="surface-panel p-3.5">
              <div className="flex flex-wrap items-start justify-between gap-2.5">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2 text-xs uppercase tracking-[0.16em] text-muted">
                    <span>{t(`timeline.kind.${event.kind}`)}</span>
                    <span className="text-white/25">•</span>
                    <span>{formatDateTime(event.createdAt)}</span>
                    {event.meta ? (
                      <>
                        <span className="text-white/25">•</span>
                        <span>{event.meta}</span>
                      </>
                    ) : null}
                  </div>
                  <div className="mt-1.5 text-sm font-semibold text-text">{event.title}</div>
                  {event.description ? <p className="mt-1 text-sm leading-5 text-muted">{event.description}</p> : null}
                </div>
                {event.state ? <StateBadge state={event.state} /> : null}
              </div>
              {event.detail ? (
                <div className="surface-muted mt-3 p-2.5 text-xs text-muted">
                  <div className="grid gap-1.5">
                    {parseDetail(event.detail).map((line) => (
                      <div key={line.id} className="flex flex-wrap items-start gap-2 text-sm leading-5">
                        {line.label ? <span className="font-medium text-subtle">{line.label}:</span> : null}
                        <span className="text-text">{line.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
