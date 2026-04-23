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
import { mapDispatchStatusLabel, mapSyncStatusLabel } from "@/lib/i18n/enum-labels";
import { useT } from "@/lib/i18n/use-t";
import { formatDateTime } from "@/lib/utils";

interface SyncCenterProps {
  jobs: DispatchJob[];
  events: SyncEvent[];
}

export function SyncCenter({ jobs, events }: SyncCenterProps) {
  const router = useRouter();
  const t = useT();
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
      { value: "all" as const, label: t("sync.filters.all"), count: jobs.length },
      { value: "failed" as const, label: t("sync.filters.failed"), count: jobs.filter((job) => job.status === "failed").length },
      { value: "pending" as const, label: t("sync.filters.pending"), count: jobs.filter((job) => job.status === "pending").length },
      { value: "running" as const, label: t("sync.filters.running"), count: jobs.filter((job) => job.status === "running").length },
      { value: "succeeded" as const, label: t("sync.filters.succeeded"), count: jobs.filter((job) => job.status === "succeeded").length }
    ],
    [jobs, t]
  );

  const eventFilterItems = useMemo(
    () => [
      { value: "all" as const, label: t("sync.filters.all"), count: events.length },
      { value: "retryable" as const, label: t("sync.filters.retryable"), count: events.filter((event) => event.status === "retryable").length },
      { value: "pending" as const, label: t("sync.filters.pending"), count: events.filter((event) => event.status === "pending").length },
      { value: "synced" as const, label: t("sync.filters.synced"), count: events.filter((event) => event.status === "synced").length },
      { value: "failed" as const, label: t("sync.filters.failed"), count: events.filter((event) => event.status === "failed").length }
    ],
    [events, t]
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
        throw new Error(body.error ?? t("sync.retry.error"));
      }
      setMessage({ tone: "success", text: t("sync.retry.success", { jobId }) });
      router.refresh();
    } catch (error) {
      setMessage({ tone: "danger", text: error instanceof Error ? error.message : t("sync.retry.error") });
    } finally {
      setBusyJob(null);
    }
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow={t("sync.header.eyebrow")}
        title={t("sync.header.title")}
        description={t("sync.header.description")}
        compact
        actions={
          <Button variant="ghost" size="sm" onClick={() => router.refresh()}>
            <RefreshCw className="h-4 w-4" />
            {t("sync.header.refreshData")}
          </Button>
        }
      />

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label={t("sync.metrics.pendingJobs.label")} value={metrics.pendingJobs.toString()} meta={t("sync.metrics.pendingJobs.meta")} tone="warning" icon={<Clock3 className="h-5 w-5" />} />
        <StatCard label={t("sync.metrics.failedJobs.label")} value={metrics.failedJobs.toString()} meta={t("sync.metrics.failedJobs.meta")} tone="danger" icon={<AlertTriangle className="h-5 w-5" />} />
        <StatCard label={t("sync.metrics.syncedEvents.label")} value={metrics.syncedEvents.toString()} meta={t("sync.metrics.syncedEvents.meta")} tone="success" icon={<CheckCircle2 className="h-5 w-5" />} />
        <StatCard label={t("sync.metrics.retryableEvents.label")} value={metrics.retryableEvents.toString()} meta={t("sync.metrics.retryableEvents.meta")} tone="accent" icon={<RotateCcw className="h-5 w-5" />} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Surface
          title={t("sync.sections.dispatch.title")}
          subtitle={t("sync.sections.dispatch.subtitle")}
          variant="shell"
          padding="sm"
          actions={<FilterPills options={jobFilterItems} value={jobFilter} onChange={setJobFilter} size="sm" />}
        >
          <div className="grid gap-3">
            {visibleJobs.length === 0 ? (
              <EmptyState
                eyebrow={t("sync.empty.dispatch.eyebrow")}
                icon={<Wrench className="h-6 w-6" />}
                title={t("sync.empty.dispatch.title")}
                description={t("sync.empty.dispatch.description")}
                className="min-h-[16rem]"
              />
            ) : (
              visibleJobs.map((job) => (
                <div key={job.id} className="surface-muted p-3.5">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <Link href={`/record/${job.recordId}`} className="text-sm font-medium text-heading transition hover:text-accent">
                        {job.recordId}
                      </Link>
                      <div className="mt-1 text-xs text-muted">{t("sync.job.adapterAttempts", { adapterId: job.adapterId, attempts: job.attempts })}</div>
                    </div>
                    <Badge tone={job.status === "succeeded" ? "success" : job.status === "failed" ? "danger" : "warning"}>
                      {mapDispatchStatusLabel(job.status, t)}
                    </Badge>
                  </div>
                  <div className="mt-2 text-xs text-muted">{t("sync.job.updated", { value: formatDateTime(job.updatedAt) })}</div>
                  {job.error ? (
                    <div className="ui-notice ui-notice-danger mt-2 px-3 py-2 text-xs">{job.error}</div>
                  ) : null}
                  <div className="mt-3 flex gap-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      disabled={busyJob !== null || job.status !== "failed"}
                      onClick={() => retry(job.id)}
                    >
                      <RefreshCw className="h-4 w-4" />
                      {busyJob === job.id ? t("sync.retry.running") : t("sync.retry.button")}
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        </Surface>

        <Surface
          title={t("sync.sections.events.title")}
          subtitle={t("sync.sections.events.subtitle")}
          variant="shell"
          padding="sm"
          actions={<FilterPills options={eventFilterItems} value={eventFilter} onChange={setEventFilter} size="sm" />}
        >
          <div className="grid gap-3">
            {visibleEvents.length === 0 ? (
              <EmptyState
                eyebrow={t("sync.empty.events.eyebrow")}
                icon={<Clock3 className="h-6 w-6" />}
                title={t("sync.empty.events.title")}
                description={t("sync.empty.events.description")}
                className="min-h-[16rem]"
              />
            ) : (
              visibleEvents.map((event) => (
                <div key={event.id} className="surface-muted p-3.5">
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
                      <div className="mt-1.5 text-xs text-muted">
                        <Link href={`/record/${event.recordId}`} className="transition hover:text-heading">
                          {event.recordId}
                        </Link>
                        <span className="mx-1">•</span>
                        {t(`sync.direction.${event.direction}`)}
                        <span className="mx-1">•</span>
                        {event.adapterId}
                        <span className="mx-1">•</span>
                        {formatDateTime(event.createdAt)}
                      </div>
                    </div>
                    <Badge tone={event.status === "synced" ? "success" : event.status === "failed" ? "danger" : "warning"}>
                      {mapSyncStatusLabel(event.status, t)}
                    </Badge>
                  </div>
                  {event.error ? <div className="mt-2 text-xs text-danger">{event.error}</div> : null}
                </div>
              ))
            )}
          </div>
        </Surface>
      </div>

      {message ? (
        <Surface className={message.tone === "success" ? "border-success/30" : "border-danger/30"}>
          <p className={message.tone === "success" ? "text-sm text-success" : "text-sm text-danger"}>{message.text}</p>
        </Surface>
      ) : null}
    </div>
  );
}
