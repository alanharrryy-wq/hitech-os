"use client";

import { useRouter } from "next/navigation";
import {
  ArrowUpRight,
  DownloadCloud,
  FileText,
  RefreshCw,
  Send,
  ShieldCheck,
  TimerReset
} from "lucide-react";
import { useMemo, useState } from "react";

import { ActivityTimeline } from "@components/records/activity-timeline";
import { Badge } from "@components/ui/badge";
import { Button } from "@components/ui/button";
import { PageHeader } from "@components/ui/page-header";
import { Select } from "@components/ui/select";
import { StateBadge } from "@components/ui/state-badge";
import { StatCard } from "@components/ui/stat-card";
import { Surface } from "@components/ui/surface";
import { Textarea } from "@components/ui/textarea";
import { getFieldById } from "@/lib/core/schema-registry";
import { stateDescription, stateLabel } from "@/lib/core/record-view";
import {
  type Attachment,
  type DispatchJob,
  type ExternalRecord,
  type RecordTypeSchema,
  type Submission,
  type SyncEvent
} from "@/lib/core/types";
import { isActionAvailable } from "@/lib/core/state";
import { cn, formatBytes, formatDateTime, formatRelativeTime, formatValue } from "@/lib/utils";

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
  const [feedback, setFeedback] = useState<{ tone: "success" | "danger"; message: string } | null>(null);
  const [role, setRole] = useState<"external_user" | "reviewer" | "approver" | "operator">("operator");
  const [actionNote, setActionNote] = useState("");

  const availableActions = useMemo(
    () => schema.actions.filter((action) => isActionAvailable(record.state, action, { role })),
    [record.state, role, schema.actions]
  );

  const latestSync = syncEvents[0];
  const latestDispatch = dispatchJobs[0];
  const requiresNote = availableActions.some((action) => action.requiresComment);

  async function runAction(actionId: string) {
    const action = availableActions.find((entry) => entry.id === actionId);
    if (!action) return;

    if (action.requiresComment && !actionNote.trim()) {
      setFeedback({
        tone: "danger",
        message: `Add a short operator note before running '${action.label}'.`
      });
      return;
    }

    setFeedback(null);
    setBusyAction(actionId);
    try {
      const response = await fetch(`/api/records/${record.id}/action`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-actor-role": role
        },
        body: JSON.stringify({ actionId, note: actionNote.trim() || undefined })
      });
      const body = await response.json();
      if (!response.ok) {
        throw new Error(body.error ?? "Action failed");
      }
      setFeedback({ tone: "success", message: `${action.label} executed successfully.` });
      setActionNote("");
      router.refresh();
    } catch (error) {
      setFeedback({
        tone: "danger",
        message: error instanceof Error ? error.message : "Action failed"
      });
    } finally {
      setBusyAction(null);
    }
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Record detail"
        title={record.title}
        description={schema.summary}
        stats={
          <>
            <StateBadge state={record.state} />
            <Badge tone="accent">{schema.title}</Badge>
            <Badge>Updated {formatRelativeTime(record.updatedAt)}</Badge>
            <Badge>{attachments.length} attachment{attachments.length === 1 ? "" : "s"}</Badge>
          </>
        }
        actions={
          <>
            <Button variant="ghost" size="sm" onClick={() => router.push("/inbox")}>
              Inbox
            </Button>
            <Button variant="ghost" size="sm" onClick={() => router.refresh()}>
              <RefreshCw className="h-4 w-4" />
              Refresh
            </Button>
            <Button variant="secondary" size="sm" onClick={() => router.push("/sync")}>
              <ArrowUpRight className="h-4 w-4" />
              Open Sync Center
            </Button>
          </>
        }
      />

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1.55fr)_360px]">
        <div className="grid gap-5">
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard label="Current state" value={stateLabel(record.state)} meta={stateDescription(record.state)} tone="accent" />
            <StatCard label="Activity" value={submissions.length.toString()} meta="Timeline entries captured so far." />
            <StatCard label="Attachments" value={attachments.length.toString()} meta="Files linked to the record." />
            <StatCard
              label="Latest sync"
              value={latestSync ? latestSync.status : "none"}
              meta={latestSync ? latestSync.summary : "No sync events recorded yet."}
              tone={latestSync?.status === "synced" ? "success" : latestSync?.status === "retryable" || latestSync?.status === "failed" ? "danger" : "warning"}
            />
          </div>

          <Surface
            title="Business details"
            subtitle="Grouped by meaning instead of raw field order so the record reads like a decision-ready document."
            variant="shell"
          >
            <div className="grid gap-4 lg:grid-cols-2">
              {schema.views.detailSections.map((section) => (
                <div key={section.id} className="surface-muted p-4 sm:p-5">
                  <div className="mb-4">
                    <h3 className="text-base font-semibold tracking-[-0.02em] text-heading">{section.title}</h3>
                  </div>
                  <div className="grid gap-3">
                    {section.fieldIds.map((fieldId) => {
                      const field = getFieldById(schema, fieldId);
                      const raw = record.fields[fieldId];
                      const value = formatValue(raw);
                      const multiline = typeof raw === "string" && raw.length > 60;
                      return (
                        <div key={fieldId} className={cn("surface-muted px-3 py-3", multiline && "items-start")}>
                          <div className={cn("flex gap-4", multiline ? "flex-col" : "items-center justify-between")}>
                            <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-subtle">{field.label}</div>
                            <div className={cn("text-sm text-heading", multiline && "leading-6")}>{value}</div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </Surface>

          <Surface
            title="Activity timeline"
            subtitle="Submissions, state transitions, and operator notes arranged for quick historical reading."
            variant="shell"
          >
            <ActivityTimeline submissions={submissions} syncEvents={syncEvents} dispatchJobs={dispatchJobs} />
          </Surface>
        </div>

        <div className="grid gap-5 self-start xl:sticky xl:top-24">
          <Surface title="Record controls" subtitle="Switch execution role, add operator context, and trigger the next state." variant="elevated">
            <label className="grid gap-2 text-sm text-muted">
              <span className="eyebrow">Actor role</span>
              <Select
                value={role}
                onChange={(event) => setRole(event.target.value as "external_user" | "reviewer" | "approver" | "operator")}
              >
                <option value="external_user">external_user</option>
                <option value="reviewer">reviewer</option>
                <option value="approver">approver</option>
                <option value="operator">operator</option>
              </Select>
            </label>

            <label className="mt-4 grid gap-2 text-sm text-muted">
              <span className="eyebrow">Operator note</span>
              <Textarea
                value={actionNote}
                onChange={(event) => setActionNote(event.target.value)}
                placeholder={requiresNote ? "Required for reject or request changes actions." : "Optional execution note."}
                className="min-h-24"
              />
            </label>

            {requiresNote ? (
              <div className="mt-4 rounded-[18px] border border-warning/20 bg-warning/10 px-4 py-3 text-sm text-warning">
                One or more available actions require a note before execution.
              </div>
            ) : null}

            <div className="mt-5 grid gap-2.5">
              {availableActions.length === 0 ? (
                <div className="surface-muted p-4 text-sm text-muted">No actions are available for the selected role and current state.</div>
              ) : (
                availableActions.map((action) => (
                  <Button
                    key={action.id}
                    variant={action.intent === "danger" ? "danger" : action.intent === "primary" ? "primary" : "secondary"}
                    disabled={busyAction !== null}
                    onClick={() => runAction(action.id)}
                    className="justify-between"
                  >
                    <span className="flex items-center gap-2">
                      {action.kind === "dispatch" ? <Send className="h-4 w-4" /> : <ShieldCheck className="h-4 w-4" />}
                      {busyAction === action.id ? "Running..." : action.label}
                    </span>
                    {action.requiresComment ? <Badge tone="warning">Note required</Badge> : null}
                  </Button>
                ))
              )}
            </div>

            {feedback ? (
              <div
                className={cn(
                  "mt-4 rounded-[18px] border px-4 py-3 text-sm",
                  feedback.tone === "success"
                    ? "border-success/25 bg-success/10 text-success"
                    : "border-danger/25 bg-danger/10 text-danger"
                )}
              >
                {feedback.message}
              </div>
            ) : null}
          </Surface>

          <Surface title="Operational summary" subtitle="Keep the key metadata visible while working through decisions.">
            <div className="grid gap-3">
              <div className="surface-muted px-3 py-3">
                <div className="metric-label">Record id</div>
                <div className="mt-1 break-all text-sm text-heading">{record.id}</div>
              </div>
              <div className="surface-muted px-3 py-3">
                <div className="metric-label">Secure token</div>
                <div className="mt-1 break-all text-sm text-heading">{record.secureToken}</div>
              </div>
              <div className="surface-muted px-3 py-3">
                <div className="metric-label">Created</div>
                <div className="mt-1 text-sm text-heading">{formatDateTime(record.createdAt)}</div>
              </div>
              <div className="surface-muted px-3 py-3">
                <div className="metric-label">Submitted</div>
                <div className="mt-1 text-sm text-heading">{formatDateTime(record.submittedAt)}</div>
              </div>
              <div className="surface-muted px-3 py-3">
                <div className="metric-label">Last sync</div>
                <div className="mt-1 text-sm text-heading">{formatDateTime(record.lastSyncAt)}</div>
              </div>
            </div>
          </Surface>

          <Surface title="Attachments" subtitle="File evidence attached to the record.">
            <div className="grid gap-2.5 text-sm">
              {attachments.length === 0 ? (
                <div className="surface-muted p-4 text-muted">No attachments linked to this record.</div>
              ) : (
                attachments.map((attachment) => (
                  <div key={attachment.id} className="surface-muted flex items-center justify-between gap-3 px-3 py-3">
                    <div className="min-w-0">
                      <div className="truncate font-medium text-heading">{attachment.name}</div>
                      <div className="mt-1 text-xs text-muted">
                        {formatBytes(attachment.size)} • {formatDateTime(attachment.createdAt)}
                      </div>
                    </div>
                    <FileText className="h-4 w-4 shrink-0 text-subtle" />
                  </div>
                ))
              )}
            </div>
          </Surface>

          <Surface title="Dispatch & sync" subtitle="Operational trail for outbound work and external acknowledgements.">
            <div className="grid gap-4">
              <div className="grid gap-2.5">
                <div className="eyebrow">Dispatch jobs</div>
                {dispatchJobs.length === 0 ? (
                  <div className="surface-muted p-4 text-sm text-muted">No dispatch jobs have been created.</div>
                ) : (
                  dispatchJobs.slice(0, 4).map((job) => (
                    <div key={job.id} className="surface-muted px-3 py-3">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="text-sm font-medium text-heading">{job.adapterId}</div>
                          <div className="mt-1 text-xs text-muted">Attempts {job.attempts} • {formatDateTime(job.updatedAt)}</div>
                        </div>
                        <Badge tone={job.status === "succeeded" ? "success" : job.status === "failed" ? "danger" : "warning"}>{job.status}</Badge>
                      </div>
                      {job.error ? <div className="mt-2 text-xs text-danger">{job.error}</div> : null}
                    </div>
                  ))
                )}
              </div>

              <div className="keyline" />

              <div className="grid gap-2.5">
                <div className="eyebrow">Sync events</div>
                {syncEvents.length === 0 ? (
                  <div className="surface-muted p-4 text-sm text-muted">No sync events recorded yet.</div>
                ) : (
                  syncEvents.slice(0, 5).map((event) => (
                    <div key={event.id} className="surface-muted px-3 py-3">
                      <div className="flex items-start justify-between gap-3">
                        <div className="space-y-1">
                          <div className="text-sm font-medium text-heading">{event.summary}</div>
                          <div className="text-xs text-muted">
                            {event.adapterId} • {formatDateTime(event.createdAt)}
                          </div>
                        </div>
                        <Badge tone={event.status === "synced" ? "success" : event.status === "failed" ? "danger" : "warning"}>{event.status}</Badge>
                      </div>
                      {event.error ? <div className="mt-2 text-xs text-danger">{event.error}</div> : null}
                    </div>
                  ))
                )}
              </div>

              <div className="flex flex-wrap gap-2 pt-1">
                <Button variant="ghost" size="sm" onClick={() => router.push("/sync")}>
                  <DownloadCloud className="h-4 w-4" />
                  Open Sync Center
                </Button>
                <Button variant="ghost" size="sm" onClick={() => router.refresh()}>
                  <TimerReset className="h-4 w-4" />
                  Refresh record
                </Button>
              </div>
            </div>
          </Surface>
        </div>
      </div>
    </div>
  );
}
