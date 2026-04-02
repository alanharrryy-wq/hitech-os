"use client";

import { AlertTriangle, CheckCircle2, Clock3, RefreshCw } from "lucide-react";
import { useState } from "react";

import { Badge } from "@components/ui/badge";
import { Button } from "@components/ui/button";
import { Surface } from "@components/ui/surface";
import { type DispatchJob, type SyncEvent } from "@/lib/core/types";
import { formatDateTime } from "@/lib/utils";

interface SyncCenterProps {
  jobs: DispatchJob[];
  events: SyncEvent[];
}

export function SyncCenter({ jobs, events }: SyncCenterProps) {
  const [busyJob, setBusyJob] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

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
      setMessage(`Retry executed for job ${jobId}`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Retry failed");
    } finally {
      setBusyJob(null);
    }
  }

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Surface title="Dispatch Jobs" subtitle="Outbound action execution states with retry controls.">
        <div className="grid gap-2">
          {jobs.length === 0 ? (
            <div className="rounded-xl border border-dashed border-white/20 p-4 text-sm text-muted">No dispatch jobs yet.</div>
          ) : (
            jobs.map((job) => (
              <div key={job.id} className="rounded-xl border border-white/10 bg-canvas/35 p-3">
                <div className="mb-1 flex items-center justify-between">
                  <div className="text-sm text-text">{job.recordId}</div>
                  <Badge tone={job.status === "succeeded" ? "success" : job.status === "failed" ? "danger" : "warning"}>
                    {job.status}
                  </Badge>
                </div>
                <div className="mb-2 text-xs text-muted">adapter: {job.adapterId} • attempts: {job.attempts}</div>
                <div className="mb-2 text-xs text-muted">updated: {formatDateTime(job.updatedAt)}</div>
                {job.error ? (
                  <div className="mb-2 rounded-md border border-danger/40 bg-danger/10 px-2 py-1 text-xs text-danger">{job.error}</div>
                ) : null}
                <div className="flex gap-2">
                  <Button
                    variant="secondary"
                    className="h-8 px-2.5 text-xs"
                    disabled={busyJob !== null || job.status !== "failed"}
                    onClick={() => retry(job.id)}
                  >
                    <RefreshCw className="mr-1 h-3.5 w-3.5" />
                    {busyJob === job.id ? "Retrying..." : "Retry"}
                  </Button>
                </div>
              </div>
            ))
          )}
        </div>
      </Surface>

      <Surface title="Sync Events" subtitle="Inbound and outbound sync audit with status visibility.">
        <div className="grid gap-2">
          {events.length === 0 ? (
            <div className="rounded-xl border border-dashed border-white/20 p-4 text-sm text-muted">No sync events yet.</div>
          ) : (
            events.map((event) => (
              <div key={event.id} className="rounded-xl border border-white/10 bg-canvas/35 p-3">
                <div className="mb-1 flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm text-text">
                    {event.status === "synced" ? (
                      <CheckCircle2 className="h-4 w-4 text-success" />
                    ) : event.status === "failed" ? (
                      <AlertTriangle className="h-4 w-4 text-danger" />
                    ) : (
                      <Clock3 className="h-4 w-4 text-warning" />
                    )}
                    {event.summary}
                  </div>
                  <Badge tone={event.status === "synced" ? "success" : event.status === "failed" ? "danger" : "warning"}>
                    {event.status}
                  </Badge>
                </div>
                <div className="text-xs text-muted">
                  {event.direction} • {event.adapterId} • {formatDateTime(event.createdAt)}
                </div>
                {event.error ? <div className="mt-1 text-xs text-danger">{event.error}</div> : null}
              </div>
            ))
          )}
        </div>
      </Surface>

      {message ? (
        <Surface className="lg:col-span-2">
          <p className="text-sm text-text">{message}</p>
        </Surface>
      ) : null}
    </div>
  );
}
