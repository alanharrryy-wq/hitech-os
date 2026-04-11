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
import { mapDispatchStatusLabel, mapSyncStatusLabel } from "@/lib/i18n/enum-labels";
import { useT } from "@/lib/i18n/use-t";
import { localizeSchemaActionLabel, localizeSchemaSectionTitle, localizeSchemaSummary, localizeSchemaTitle } from "@/lib/ui/schema-display";
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
  const t = useT();
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<{ tone: "success" | "danger"; message: string } | null>(null);
  const [role, setRole] = useState<"external_user" | "reviewer" | "approver" | "operator">("operator");
  const [actionNote, setActionNote] = useState("");
  const schemaTitle = localizeSchemaTitle(schema, t);
  const schemaSummary = localizeSchemaSummary(schema, t);

  const availableActions = useMemo(
    () => schema.actions.filter((action) => isActionAvailable(record.state, action, { role })),
    [record.state, role, schema.actions]
  );

  const latestSync = syncEvents[0];
  const requiresNote = availableActions.some((action) => action.requiresComment);

  async function runAction(actionId: string) {
    const action = availableActions.find((entry) => entry.id === actionId);
    if (!action) return;
    const actionLabel = localizeSchemaActionLabel(schema.id, action.id, action.label, t);

    if (action.requiresComment && !actionNote.trim()) {
      setFeedback({
        tone: "danger",
        message: t("record.controls.noteRequiredForAction", { action: actionLabel })
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
        throw new Error(body.error ?? t("record.controls.actionFailed"));
      }
      setFeedback({ tone: "success", message: t("record.controls.actionSuccess", { action: actionLabel }) });
      setActionNote("");
      router.refresh();
    } catch (error) {
      setFeedback({
        tone: "danger",
        message: error instanceof Error ? error.message : t("record.controls.actionFailed")
      });
    } finally {
      setBusyAction(null);
    }
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow={t("record.header.eyebrow")}
        title={record.title}
        description={schemaSummary}
        stats={
          <>
            <StateBadge state={record.state} />
            <Badge tone="accent">{schemaTitle}</Badge>
            <Badge>{t("record.header.updated", { value: formatRelativeTime(record.updatedAt) })}</Badge>
            <Badge>{t(attachments.length === 1 ? "record.header.attachments.one" : "record.header.attachments.many", { count: attachments.length })}</Badge>
          </>
        }
        actions={
          <>
            <Button variant="ghost" size="sm" onClick={() => router.push("/inbox")}>
              {t("record.header.actions.inbox")}
            </Button>
            <Button variant="ghost" size="sm" onClick={() => router.refresh()}>
              <RefreshCw className="h-4 w-4" />
              {t("record.header.actions.refresh")}
            </Button>
            <Button variant="secondary" size="sm" onClick={() => router.push("/sync")}>
              <ArrowUpRight className="h-4 w-4" />
              {t("record.header.actions.openSync")}
            </Button>
          </>
        }
      />

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1.58fr)_340px]">
        <div className="grid gap-4">
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard label={t("record.stats.currentState.label")} value={stateLabel(record.state)} meta={stateDescription(record.state)} tone="accent" />
            <StatCard label={t("record.stats.activity.label")} value={submissions.length.toString()} meta={t("record.stats.activity.meta")} />
            <StatCard label={t("record.stats.attachments.label")} value={attachments.length.toString()} meta={t("record.stats.attachments.meta")} />
            <StatCard
              label={t("record.stats.latestSync.label")}
              value={latestSync ? mapSyncStatusLabel(latestSync.status, t) : t("record.stats.latestSync.none")}
              meta={latestSync ? latestSync.summary : t("record.stats.latestSync.metaEmpty")}
              tone={latestSync?.status === "synced" ? "success" : latestSync?.status === "retryable" || latestSync?.status === "failed" ? "danger" : "warning"}
            />
          </div>

          <Surface
            title={t("record.details.title")}
            subtitle={t("record.details.subtitle")}
            variant="shell"
            padding="sm"
          >
            <div className="grid gap-3.5 lg:grid-cols-2">
              {schema.views.detailSections.map((section) => (
                <div key={section.id} className="surface-muted p-3.5 sm:p-4">
                  <div className="mb-3">
                    <h3 className="text-[15px] font-semibold tracking-[-0.02em] text-heading">{localizeSchemaSectionTitle(schema.id, section.id, section.title, t)}</h3>
                  </div>
                  <div className="grid gap-2.5">
                    {section.fieldIds.map((fieldId) => {
                      const field = getFieldById(schema, fieldId);
                      const raw = record.fields[fieldId];
                      const value = formatValue(raw);
                      const multiline = typeof raw === "string" && raw.length > 60;
                      return (
                        <div key={fieldId} className={cn("surface-muted px-3 py-2.5", multiline && "items-start")}>
                          <div className={cn("flex gap-3", multiline ? "flex-col" : "items-center justify-between")}>
                            <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-subtle">{field.label}</div>
                            <div className={cn("text-sm text-heading", multiline && "leading-5")}>{value}</div>
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
            title={t("timeline.surface.title")}
            subtitle={t("timeline.surface.subtitle")}
            variant="shell"
            padding="sm"
          >
            <ActivityTimeline submissions={submissions} syncEvents={syncEvents} dispatchJobs={dispatchJobs} />
          </Surface>
        </div>

        <div className="grid gap-5 self-start xl:sticky xl:top-24">
          <Surface title={t("record.controls.title")} subtitle={t("record.controls.subtitle")} variant="elevated" padding="sm">
            <label className="grid gap-2 text-sm text-muted">
              <span className="eyebrow">{t("record.controls.actorRole")}</span>
              <Select
                value={role}
                onChange={(event) => setRole(event.target.value as "external_user" | "reviewer" | "approver" | "operator")}
              >
                <option value="external_user">{t("runtime.role.external_user")}</option>
                <option value="reviewer">{t("runtime.role.reviewer")}</option>
                <option value="approver">{t("runtime.role.approver")}</option>
                <option value="operator">{t("runtime.role.operator")}</option>
              </Select>
            </label>

            <label className="mt-3.5 grid gap-2 text-sm text-muted">
              <span className="eyebrow">{t("record.controls.operatorNote")}</span>
              <Textarea
                value={actionNote}
                onChange={(event) => setActionNote(event.target.value)}
                placeholder={requiresNote ? t("record.controls.notePlaceholderRequired") : t("record.controls.notePlaceholderOptional")}
                className="min-h-24"
              />
            </label>

            {requiresNote ? (
              <div className="mt-3.5 rounded-[18px] border border-warning/20 bg-warning/10 px-4 py-2.5 text-sm text-warning">
                {t("record.controls.requiresNoteHint")}
              </div>
            ) : null}

            <div className="mt-4 grid gap-2.5">
              {availableActions.length === 0 ? (
                <div className="surface-muted p-3.5 text-sm text-muted">{t("record.controls.noActions")}</div>
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
                      {busyAction === action.id
                        ? t("record.controls.running")
                        : localizeSchemaActionLabel(schema.id, action.id, action.label, t)}
                    </span>
                    {action.requiresComment ? <Badge tone="warning">{t("record.controls.noteRequiredBadge")}</Badge> : null}
                  </Button>
                ))
              )}
            </div>

            {feedback ? (
              <div
                className={cn(
                  "mt-3.5 rounded-[18px] border px-4 py-2.5 text-sm",
                  feedback.tone === "success"
                    ? "border-success/25 bg-success/10 text-success"
                    : "border-danger/25 bg-danger/10 text-danger"
                )}
              >
                {feedback.message}
              </div>
            ) : null}
          </Surface>

          <Surface title={t("record.summary.title")} subtitle={t("record.summary.subtitle")} padding="sm">
            <div className="grid gap-2.5">
              <div className="surface-muted px-3 py-2.5">
                <div className="metric-label">{t("record.summary.recordId")}</div>
                <div className="mt-1 break-all text-sm text-heading">{record.id}</div>
              </div>
              <div className="surface-muted px-3 py-2.5">
                <div className="metric-label">{t("record.summary.secureToken")}</div>
                <div className="mt-1 break-all text-sm text-heading">{record.secureToken}</div>
              </div>
              <div className="surface-muted px-3 py-2.5">
                <div className="metric-label">{t("record.summary.created")}</div>
                <div className="mt-1 text-sm text-heading">{formatDateTime(record.createdAt)}</div>
              </div>
              <div className="surface-muted px-3 py-2.5">
                <div className="metric-label">{t("record.summary.submitted")}</div>
                <div className="mt-1 text-sm text-heading">{formatDateTime(record.submittedAt)}</div>
              </div>
              <div className="surface-muted px-3 py-2.5">
                <div className="metric-label">{t("record.summary.lastSync")}</div>
                <div className="mt-1 text-sm text-heading">{formatDateTime(record.lastSyncAt)}</div>
              </div>
            </div>
          </Surface>

          <Surface title={t("record.attachments.title")} subtitle={t("record.attachments.subtitle")} padding="sm">
            <div className="grid gap-2.5 text-sm">
              {attachments.length === 0 ? (
                <div className="surface-muted p-3.5 text-muted">{t("record.attachments.empty")}</div>
              ) : (
                attachments.map((attachment) => (
                  <div key={attachment.id} className="surface-muted flex items-center justify-between gap-3 px-3 py-2.5">
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

          <Surface title={t("record.dispatchSync.title")} subtitle={t("record.dispatchSync.subtitle")} padding="sm">
            <div className="grid gap-3.5">
              <div className="grid gap-2.5">
                <div className="eyebrow">{t("record.dispatchSync.dispatchJobs")}</div>
                {dispatchJobs.length === 0 ? (
                  <div className="surface-muted p-3.5 text-sm text-muted">{t("record.dispatchSync.dispatchJobsEmpty")}</div>
                ) : (
                  dispatchJobs.slice(0, 4).map((job) => (
                    <div key={job.id} className="surface-muted px-3 py-2.5">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="text-sm font-medium text-heading">{job.adapterId}</div>
                          <div className="mt-1 text-xs text-muted">{t("record.dispatchSync.attemptsAndUpdated", { attempts: job.attempts, value: formatDateTime(job.updatedAt) })}</div>
                        </div>
                        <Badge tone={job.status === "succeeded" ? "success" : job.status === "failed" ? "danger" : "warning"}>
                          {mapDispatchStatusLabel(job.status, t)}
                        </Badge>
                      </div>
                      {job.error ? <div className="mt-2 text-xs text-danger">{job.error}</div> : null}
                    </div>
                  ))
                )}
              </div>

              <div className="keyline" />

              <div className="grid gap-2.5">
                <div className="eyebrow">{t("record.dispatchSync.syncEvents")}</div>
                {syncEvents.length === 0 ? (
                  <div className="surface-muted p-3.5 text-sm text-muted">{t("record.dispatchSync.syncEventsEmpty")}</div>
                ) : (
                  syncEvents.slice(0, 5).map((event) => (
                    <div key={event.id} className="surface-muted px-3 py-2.5">
                      <div className="flex items-start justify-between gap-3">
                        <div className="space-y-1">
                          <div className="text-sm font-medium text-heading">{event.summary}</div>
                          <div className="text-xs text-muted">
                            {event.adapterId} • {formatDateTime(event.createdAt)}
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

              <div className="flex flex-wrap gap-2 pt-0.5">
                <Button variant="ghost" size="sm" onClick={() => router.push("/sync")}>
                  <DownloadCloud className="h-4 w-4" />
                  {t("record.dispatchSync.openSync")}
                </Button>
                <Button variant="ghost" size="sm" onClick={() => router.refresh()}>
                  <TimerReset className="h-4 w-4" />
                  {t("record.dispatchSync.refreshRecord")}
                </Button>
              </div>
            </div>
          </Surface>
        </div>
      </div>
    </div>
  );
}
