import { Clock3, FileDiff, RefreshCw, Send } from "lucide-react";

import { EmptyState } from "@components/ui/empty-state";
import { StateBadge } from "@components/ui/state-badge";
import { type DispatchJob, type Submission, type SyncEvent } from "@/lib/core/types";
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

export function ActivityTimeline({
  submissions = [],
  syncEvents = [],
  dispatchJobs = [],
  emptyTitle = "No activity yet",
  emptyDescription = "New submissions, dispatch attempts and sync signals will land here once the record starts moving.",
  className
}: ActivityTimelineProps) {
  const events = createTimelineEntries({ submissions, syncEvents, dispatchJobs });

  if (events.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} compact className={className} />;
  }

  return (
    <div className={className}>
      <ol className="grid gap-3">
        {events.map((event, index) => (
          <li key={event.id} className="relative pl-11">
            {index < events.length - 1 ? <div className="pointer-events-none absolute left-[1.05rem] top-10 h-[calc(100%-1rem)] w-px bg-gradient-to-b from-white/16 via-white/10 to-transparent" /> : null}
            <div className="absolute left-0 top-1 inline-flex h-8 w-8 items-center justify-center rounded-2xl border border-white/10 bg-surface/75 text-accent shadow-[0_8px_30px_rgba(0,0,0,0.18)]">
              {iconForKind(event.kind)}
            </div>
            <div className="rounded-2xl border border-white/10 bg-surface/52 p-4 shadow-glass backdrop-blur-xl">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2 text-xs uppercase tracking-[0.16em] text-muted">
                    <span>{event.kind}</span>
                    <span className="text-white/25">•</span>
                    <span>{formatDateTime(event.createdAt)}</span>
                    {event.meta ? (
                      <>
                        <span className="text-white/25">•</span>
                        <span>{event.meta}</span>
                      </>
                    ) : null}
                  </div>
                  <div className="mt-2 text-sm font-semibold text-text">{event.title}</div>
                  {event.description ? <p className="mt-1 text-sm leading-6 text-muted">{event.description}</p> : null}
                </div>
                {event.state ? <StateBadge state={event.state} /> : null}
              </div>
              {event.detail ? (
                <div className="mt-4 rounded-xl border border-white/10 bg-canvas/30 p-3 text-xs text-muted">
                  <pre className="overflow-x-auto whitespace-pre-wrap break-words text-xs text-text">{event.detail}</pre>
                </div>
              ) : null}
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
