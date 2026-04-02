"use client";

import { useRouter } from "next/navigation";
import { Clock3, DownloadCloud, FileText, RefreshCw, Send, ShieldCheck } from "lucide-react";
import { useMemo, useState } from "react";

import { Badge } from "@components/ui/badge";
import { Button } from "@components/ui/button";
import { Surface } from "@components/ui/surface";
import { getFieldById } from "@/lib/core/schema-registry";
import { stateLabel, stateTone } from "@/lib/core/record-view";
import {
  type Attachment,
  type DispatchJob,
  type ExternalRecord,
  type RecordTypeSchema,
  type Submission,
  type SyncEvent
} from "@/lib/core/types";
import { isActionAvailable } from "@/lib/core/state";
import { formatDateTime } from "@/lib/utils";

interface RecordDetailProps {
  record: ExternalRecord;
  schema: RecordTypeSchema;
  submissions: Submission[];
  attachments: Attachment[];
  dispatchJobs: DispatchJob[];
  syncEvents: SyncEvent[];
}

export function RecordDetail({
  record,
  schema,
  submissions,
  attachments,
  dispatchJobs,
  syncEvents
}: RecordDetailProps) {
  const router = useRouter();
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [role, setRole] = useState<"external_user" | "reviewer" | "approver" | "operator">("operator");

  const availableActions = useMemo(
    () => schema.actions.filter((action) => isActionAvailable(record.state, action, { role })),
    [record.state, role, schema.actions]
  );

  async function runAction(actionId: string) {
    setFeedback(null);
    setBusyAction(actionId);
    try {
      const response = await fetch(`/api/records/${record.id}/action`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-actor-role": role
        },
        body: JSON.stringify({ actionId })
      });
      const body = await response.json();
      if (!response.ok) {
        throw new Error(body.error ?? "Action failed");
      }
      setFeedback(`Action '${actionId}' executed.`);
      router.refresh();
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : "Action failed");
    } finally {
      setBusyAction(null);
    }
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
      <div className="grid gap-4">
        <Surface
          title={record.title}
          subtitle={schema.summary}
          actions={
            <>
              <Badge tone={stateTone(record.state)}>{stateLabel(record.state)}</Badge>
              <Badge tone="accent">{schema.title}</Badge>
            </>
          }
        >
          <div className="grid gap-4 sm:grid-cols-2">
            {schema.views.detailSections.map((section) => (
              <div key={section.id} className="rounded-xl border border-white/10 bg-canvas/30 p-3">
                <div className="mb-2 text-sm font-semibold text-text">{section.title}</div>
                <div className="grid gap-1.5 text-xs">
                  {section.fieldIds.map((fieldId) => {
                    const field = getFieldById(schema, fieldId);
                    const raw = record.fields[fieldId];
                    const value =
                      raw === undefined || raw === null || raw === ""
                        ? "-"
                        : Array.isArray(raw)
                          ? `${raw.length} items`
                          : String(raw);
                    return (
                      <div key={fieldId} className="flex items-center justify-between gap-2 rounded-md bg-canvas/35 px-2 py-1.5">
                        <span className="text-muted">{field.label}</span>
                        <span className="text-right text-text">{value}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </Surface>

        <Surface title="Activity Timeline" subtitle="Submissions, updates and action traces.">
          <div className="grid gap-2">
            {submissions.length === 0 ? (
              <div className="rounded-xl border border-dashed border-white/20 bg-canvas/25 p-4 text-sm text-muted">No activity yet.</div>
            ) : (
              submissions.slice(0, 20).map((submission) => (
                <div key={submission.id} className="rounded-xl border border-white/10 bg-canvas/35 p-3">
                  <div className="mb-1 flex items-center gap-2 text-xs text-muted">
                    <Clock3 className="h-3.5 w-3.5" />
                    {formatDateTime(submission.createdAt)}
                  </div>
                  <pre className="overflow-x-auto text-xs text-text">{JSON.stringify(submission.payload, null, 2)}</pre>
                </div>
              ))
            )}
          </div>
        </Surface>
      </div>

      <div className="grid gap-4">
        <Surface title="Available Actions" subtitle="Rendered from schema + state + role.">
          <label className="mb-3 grid gap-1 text-xs text-muted">
            Actor role
            <select
              className="h-9 rounded-lg border border-white/10 bg-canvas/40 px-2 text-sm text-text"
              value={role}
              onChange={(event) =>
                setRole(event.target.value as "external_user" | "reviewer" | "approver" | "operator")
              }
            >
              <option value="external_user">external_user</option>
              <option value="reviewer">reviewer</option>
              <option value="approver">approver</option>
              <option value="operator">operator</option>
            </select>
          </label>

          <div className="grid gap-2">
            {availableActions.length === 0 ? (
              <div className="rounded-lg border border-dashed border-white/20 p-3 text-sm text-muted">
                No actions available for current role/state.
              </div>
            ) : (
              availableActions.map((action) => (
                <Button
                  key={action.id}
                  variant={action.intent === "danger" ? "danger" : action.intent === "primary" ? "primary" : "secondary"}
                  disabled={busyAction !== null}
                  onClick={() => runAction(action.id)}
                  className="justify-start"
                >
                  {action.kind === "dispatch" ? <Send className="mr-1.5 h-4 w-4" /> : <ShieldCheck className="mr-1.5 h-4 w-4" />}
                  {busyAction === action.id ? "Running..." : action.label}
                </Button>
              ))
            )}
          </div>

          {feedback ? <p className="mt-3 text-xs text-muted">{feedback}</p> : null}
        </Surface>

        <Surface title="Attachments" subtitle="File metadata linked to this record.">
          <div className="grid gap-2 text-sm">
            {attachments.length === 0 ? (
              <div className="rounded-lg border border-dashed border-white/20 p-3 text-muted">No attachments.</div>
            ) : (
              attachments.map((attachment) => (
                <div key={attachment.id} className="flex items-center justify-between rounded-lg bg-canvas/35 px-3 py-2">
                  <div className="min-w-0">
                    <div className="truncate text-text">{attachment.name}</div>
                    <div className="text-xs text-muted">{formatDateTime(attachment.createdAt)}</div>
                  </div>
                  <FileText className="h-4 w-4 text-muted" />
                </div>
              ))
            )}
          </div>
        </Surface>

        <Surface title="Dispatch / Sync" subtitle="Outbound job and sync trail visibility.">
          <div className="grid gap-2">
            {dispatchJobs.slice(0, 4).map((job) => (
              <div key={job.id} className="rounded-lg border border-white/10 bg-canvas/35 p-2.5 text-xs">
                <div className="mb-1 flex items-center justify-between">
                  <span className="text-text">{job.adapterId}</span>
                  <Badge tone={job.status === "succeeded" ? "success" : job.status === "failed" ? "danger" : "warning"}>
                    {job.status}
                  </Badge>
                </div>
                <div className="text-muted">attempts: {job.attempts}</div>
              </div>
            ))}
            {syncEvents.slice(0, 4).map((event) => (
              <div key={event.id} className="rounded-lg border border-white/10 bg-canvas/35 p-2.5 text-xs">
                <div className="mb-1 flex items-center justify-between">
                  <span className="text-text">{event.adapterId}</span>
                  <Badge tone={event.status === "synced" ? "success" : event.status === "failed" ? "danger" : "warning"}>
                    {event.status}
                  </Badge>
                </div>
                <div className="text-muted">{event.summary}</div>
              </div>
            ))}
            <Button variant="ghost" className="justify-start" onClick={() => router.push("/sync")}>
              <DownloadCloud className="mr-1.5 h-4 w-4" />
              Open Sync Center
            </Button>
            <Button variant="ghost" className="justify-start" onClick={() => router.refresh()}>
              <RefreshCw className="mr-1.5 h-4 w-4" />
              Refresh
            </Button>
          </div>
        </Surface>
      </div>
    </div>
  );
}
