"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { AlertTriangle, CheckCircle2, Clock3, RefreshCw, RotateCcw, Wrench } from "lucide-react";
import { useMemo, useState } from "react";

import { Badge } from "@components/ui/badge";
import { Button } from "@components/ui/button";
import { EmptyState } from "@components/ui/empty-state";
import { FilterPills } from "@components/ui/filter-pills";
import { PageHeader } from "@components/ui/page-header";
import { StatCard } from "@components/ui/stat-card";
import { Surface } from "@components/ui/surface";
import { type DispatchJob, type SyncEvent } from "@/lib/core/types";
import { formatDateTime } from "@/lib/utils";

interface SyncCenterProps {
  jobs: DispatchJob[];
  events: SyncEvent[];
}

export function SyncCenter({ jobs, events }: SyncCenterProps) {
  const router = useRouter();
  const [busyJob, setBusyJob] = useState<string | null>(null);
  const [message, setMessage] = useState<{ tone: "success" | "danger"; text: string } | null>(null);
  const [jobFilter, setJobFilter] = useState<"all" | DispatchJob["status"]>("all");
  const [eventFilter, setEventFilter] = useState<"all" | SyncEvent["status"]>("all");

  const metrics = useMemo(
    () => ({
      pendingJobs: jobs.filter((job) => job.status === "pending" || job.status === "running").length,
      failedJobs: jobs.filter((job) => job.status === "failed").length,
      syncedEvents: events.filter((event) => event.status === "synced").length,
      retryableEvents: events.filter((event) => event.status === "retryable").length
    }),
    [jobs, events]
  );

  const visibleJobs = useMemo(
    () => (jobFilter === "all" ? jobs : jobs.filter((job) => job.status === jobFilter)),
    [jobFilter, jobs]
  );
  const visibleEvents = useMemo(
    () => (eventFilter === "all" ? events : events.filter((event) => event.status === eventFilter)),
    [eventFilter, events]
  );

  const jobFilterItems = useMemo(
    () => [
      { value: "all" as const, label: "All", count: jobs.length },
      { value: "failed" as const, label: "Failed", count: jobs.filter((job) => job.status === "failed").length },
      { value: "pending" as const, label: "Pending", count: jobs.filter((job) => job.status === "pending").length },
      { value: "running" as const, label: "Running", count: jobs.filter((job) => job.status === "running").length },
      { value: "succeeded" as const, label: "Succeeded", count: jobs.filter((job) => job.status === "succeeded").length }
    ],
    [jobs]
  );

  const eventFilterItems = useMemo(
    () => [
      { value: "all" as const, label: "All", count: events.length },
      { value: "retryable" as const, label: "Retryable", count: events.filter((event) => event.status === "retryable").length },
      { value: "pending" as const, label: "Pending", count: events.filter((event) => event.status === "pending").length },
      { value: "synced" as const, label: "Synced", count: events.filter((event) => event.status === "synced").length },
      { value: "failed" as const, label: "Failed", count: events.filter((event) => event.status === "failed").length }
    ],
    [events]
  );

  async function retry(jobId: string) {
    setBusyJob(jobId);
    setMessage(null);
    try {
      const response = await fetch(`/api/sync/jobs/${jobId}/retry`, {
        method: "POST"
      });
      const body = await response.json();
      if (!response.ok) {
        throw new Error(body.error ?? "Retry failed");
      }
      setMessage({ tone: "success", text: `Retry executed for job ${jobId}.` });
      router.refresh();
    } catch (error) {
      setMessage({ tone: "danger", text: error instanceof Error ? error.message : "Retry failed" });
    } finally {
      setBusyJob(null);
    }
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Sync center"
        title="Operational visibility for dispatch and sync health"
        description="Inspect outbound execution, watch retryable failures, and keep the audit trail readable at a glance."
        actions={
          <Button variant="ghost" size="sm" onClick={() => router.refresh()}>
            <RefreshCw className="h-4 w-4" />
            Refresh data
          </Button>
        }
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Pending jobs" value={metrics.pendingJobs.toString()} meta="Queued or currently running." tone="warning" icon={<Clock3 className="h-5 w-5" />} />
        <StatCard label="Failed jobs" value={metrics.failedJobs.toString()} meta="Ready for retry when appropriate." tone="danger" icon={<AlertTriangle className="h-5 w-5" />} />
        <StatCard label="Synced events" value={metrics.syncedEvents.toString()} meta="Successfully completed sync outcomes." tone="success" icon={<CheckCircle2 className="h-5 w-5" />} />
        <StatCard label="Retryable events" value={metrics.retryableEvents.toString()} meta="Need another outbound pass." tone="accent" icon={<RotateCcw className="h-5 w-5" />} />
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <Surface
          title="Dispatch jobs"
          subtitle="Outbound action execution states with retry controls."
          variant="shell"
          actions={<FilterPills options={jobFilterItems} value={jobFilter} onChange={setJobFilter} />}
        >
          <div className="grid gap-3">
            {visibleJobs.length === 0 ? (
              <EmptyState
                eyebrow="Dispatch queue"
                icon={<Wrench className="h-6 w-6" />}
                title="No dispatch jobs match the current filter"
                description="Switch the filter, retry failed work, or return later when a new outbound action is created."
                className="min-h-[18rem]"
              />
            ) : (
              visibleJobs.map((job) => (
                <div key={job.id} className="surface-muted p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <Link href={`/record/${job.recordId}`} className="text-sm font-medium text-heading transition hover:text-accent">
                        {job.recordId}
                      </Link>
                      <div className="mt-1 text-xs text-muted">Adapter {job.adapterId} • Attempts {job.attempts}</div>
                    </div>
                    <Badge tone={job.status === "succeeded" ? "success" : job.status === "failed" ? "danger" : "warning"}>
                      {job.status}
                    </Badge>
                  </div>
                  <div className="mt-3 text-xs text-muted">Updated {formatDateTime(job.updatedAt)}</div>
                  {job.error ? (
                    <div className="mt-3 rounded-[16px] border border-danger/25 bg-danger/10 px-3 py-2 text-xs text-danger">{job.error}</div>
                  ) : null}
                  <div className="mt-4 flex gap-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      disabled={busyJob !== null || job.status !== "failed"}
                      onClick={() => retry(job.id)}
                    >
                      <RefreshCw className="h-4 w-4" />
                      {busyJob === job.id ? "Retrying..." : "Retry"}
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        </Surface>

        <Surface
          title="Sync events"
          subtitle="Inbound and outbound audit trail with clearer status visibility."
          variant="shell"
          actions={<FilterPills options={eventFilterItems} value={eventFilter} onChange={setEventFilter} />}
        >
          <div className="grid gap-3">
            {visibleEvents.length === 0 ? (
              <EmptyState
                eyebrow="Audit trail"
                icon={<Clock3 className="h-6 w-6" />}
                title="No sync events match the current filter"
                description="The current filter is empty. Clear it or wait for the next inbound or outbound event."
                className="min-h-[18rem]"
              />
            ) : (
              visibleEvents.map((event) => (
                <div key={event.id} className="surface-muted p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 text-sm font-medium text-heading">
                        {event.status === "synced" ? (
                          <CheckCircle2 className="h-4 w-4 text-success" />
                        ) : event.status === "failed" ? (
                          <AlertTriangle className="h-4 w-4 text-danger" />
                        ) : (
                          <Clock3 className="h-4 w-4 text-warning" />
                        )}
                        <span className="truncate">{event.summary}</span>
                      </div>
                      <div className="mt-2 text-xs text-muted">
                        <Link href={`/record/${event.recordId}`} className="transition hover:text-heading">
                          {event.recordId}
                        </Link>
                        <span className="mx-1">•</span>
                        {event.direction}
                        <span className="mx-1">•</span>
                        {event.adapterId}
                        <span className="mx-1">•</span>
                        {formatDateTime(event.createdAt)}
                      </div>
                    </div>
                    <Badge tone={event.status === "synced" ? "success" : event.status === "failed" ? "danger" : "warning"}>
                      {event.status}
                    </Badge>
                  </div>
                  {event.error ? <div className="mt-3 text-xs text-danger">{event.error}</div> : null}
                </div>
              ))
            )}
          </div>
        </Surface>
      </div>

      {message ? (
        <Surface className={message.tone === "success" ? "border-success/25" : "border-danger/25"}>
          <p className={message.tone === "success" ? "text-sm text-success" : "text-sm text-danger"}>{message.text}</p>
        </Surface>
      ) : null}
    </div>
  );
}
