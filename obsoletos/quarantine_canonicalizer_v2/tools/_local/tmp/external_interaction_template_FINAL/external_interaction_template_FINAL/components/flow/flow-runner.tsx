"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  FileUp,
  LoaderCircle,
  LockKeyhole,
  Save,
  Shield,
  Sparkles,
  Workflow
} from "lucide-react";
import { useMemo, useState } from "react";
import type { ComponentType } from "react";

import { Button } from "@components/ui/button";
import { StateBadge } from "@components/ui/state-badge";
import { Input } from "@components/ui/input";
import { Select } from "@components/ui/select";
import { StatCard } from "@components/ui/stat-card";
import { Surface } from "@components/ui/surface";
import { Textarea } from "@components/ui/textarea";
import { getFieldById } from "@/lib/core/schema-registry";
import { stateDescription } from "@/lib/core/record-view";
import { type ExternalRecord, type RecordTypeSchema, type StepDefinition } from "@/lib/core/types";
import { validateStepPayload } from "@/lib/core/validation";
import { isFieldVisible } from "@/lib/core/visibility";
import { cn, formatRelativeTime } from "@/lib/utils";

interface FlowRunnerProps {
  schema: RecordTypeSchema;
  initialRecord?: ExternalRecord | null;
}

function hasMeaningfulValue(value: unknown): boolean {
  if (value === undefined || value === null) return false;
  if (typeof value === "string") return value.trim().length > 0;
  if (typeof value === "number") return !Number.isNaN(value);
  if (typeof value === "boolean") return true;
  if (value instanceof FileList) return value.length > 0;
  if (Array.isArray(value)) return value.length > 0;
  return true;
}

function getVisibleStepFields(schema: RecordTypeSchema, step: StepDefinition, values: Record<string, unknown>) {
  return step.fieldIds.filter((fieldId) => {
    const field = getFieldById(schema, fieldId);
    return isFieldVisible(field, values, "external_user");
  });
}

function getStepSummary(schema: RecordTypeSchema, step: StepDefinition, values: Record<string, unknown>) {
  const visibleFieldIds = getVisibleStepFields(schema, step, values);
  const requiredFieldIds = visibleFieldIds.filter((fieldId) => getFieldById(schema, fieldId).required);
  const completedRequired = requiredFieldIds.filter((fieldId) => hasMeaningfulValue(values[fieldId])).length;
  const complete = requiredFieldIds.length > 0 ? completedRequired === requiredFieldIds.length : visibleFieldIds.every((fieldId) => hasMeaningfulValue(values[fieldId]));

  return {
    visibleFieldIds,
    requiredTotal: requiredFieldIds.length,
    completedRequired,
    complete
  };
}

function resolveInitialStepIndex(schema: RecordTypeSchema, values: Record<string, unknown>) {
  const summaries = schema.flow.steps.map((step) => getStepSummary(schema, step, values));
  const firstIncomplete = summaries.findIndex((summary) => !summary.complete);
  return firstIncomplete === -1 ? Math.max(0, schema.flow.steps.length - 1) : firstIncomplete;
}

function serializePersistableValues(values: Record<string, unknown>) {
  return Object.fromEntries(
    Object.entries(values).map(([fieldId, value]) => {
      if (value instanceof FileList) {
        return [fieldId, value.length > 0 ? `${value.length} attachment(s)` : ""];
      }
      return [fieldId, value];
    })
  );
}

export function FlowRunner({ schema, initialRecord }: FlowRunnerProps) {
  const initialValues = initialRecord?.fields ?? {};
  const [stepIndex, setStepIndex] = useState(() => resolveInitialStepIndex(schema, initialValues));
  const [recordId, setRecordId] = useState<string | null>(initialRecord?.id ?? null);
  const [secureToken, setSecureToken] = useState<string | null>(initialRecord?.secureToken ?? null);
  const [recordState, setRecordState] = useState<ExternalRecord["state"]>(initialRecord?.state ?? "draft");
  const [values, setValues] = useState<Record<string, unknown>>(initialValues);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [notice, setNotice] = useState<{ tone: "success" | "danger"; message: string } | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [lastSavedAt, setLastSavedAt] = useState<string | Date | null>(initialRecord?.updatedAt ?? null);

  const step = schema.flow.steps[stepIndex];
  const MotionDiv = motion.div as unknown as ComponentType<any>;
  const primaryListField = schema.views.listFields[0] ?? schema.fields[0]?.id ?? "title";

  const stepSummaries = useMemo(
    () => schema.flow.steps.map((entry) => ({ step: entry, ...getStepSummary(schema, entry, values) })),
    [schema, values]
  );

  if (!step) {
    return (
      <Surface title="Flow configuration issue" variant="elevated">
        <p className="text-sm text-danger">No steps configured for this schema.</p>
      </Surface>
    );
  }

  const activeStep = step;
  const isFinalStep = stepIndex === schema.flow.steps.length - 1;
  const activeStepSummary = stepSummaries[stepIndex];
  const remainingRequired = stepSummaries.reduce((total, entry) => total + Math.max(0, entry.requiredTotal - entry.completedRequired), 0);
  const progressTotals = stepSummaries.reduce(
    (accumulator, entry) => {
      const weight = Math.max(1, entry.requiredTotal);
      accumulator.total += weight;
      accumulator.completed += entry.requiredTotal === 0 ? (entry.complete ? 1 : 0) : entry.completedRequired;
      return accumulator;
    },
    { total: 0, completed: 0 }
  );
  const progress = progressTotals.total === 0 ? 0 : (progressTotals.completed / progressTotals.total) * 100;
  const visibleFieldIds = activeStepSummary?.visibleFieldIds ?? [];
  const persistableValues = serializePersistableValues(values);
  const nextStepTitle = schema.flow.steps[stepIndex + 1]?.title;
  const errorCount = Object.keys(errors).length;

  function handleValue(fieldId: string, value: unknown) {
    setValues((current) => ({ ...current, [fieldId]: value }));
    setErrors((current) => {
      if (!current[fieldId]) return current;
      const clone = { ...current };
      delete clone[fieldId];
      return clone;
    });
  }

  async function uploadAttachmentsIfAny(targetRecordId: string) {
    const uploadFields = visibleFieldIds.filter((fieldId) => getFieldById(schema, fieldId).kind === "file");

    for (const fieldId of uploadFields) {
      const candidate = values[fieldId];
      if (!(candidate instanceof FileList) || candidate.length === 0) continue;

      for (const file of Array.from(candidate)) {
        const formData = new FormData();
        formData.append("file", file);
        const response = await fetch(`/api/records/${targetRecordId}/attachments`, {
          method: "POST",
          body: formData
        });

        if (!response.ok) {
          const body = await response.json().catch(() => ({ error: "Attachment upload failed" }));
          throw new Error(body.error ?? `Attachment '${file.name}' failed to upload`);
        }
      }

      handleValue(fieldId, `${candidate.length} attachment(s)`);
    }
  }

  async function persist(submit: boolean) {
    setSubmitting(true);
    setNotice(null);

    const validation = validateStepPayload(schema, activeStep.id, values, "external_user");
    if (!validation.ok) {
      setErrors("errors" in validation ? validation.errors : {});
      setNotice({ tone: "danger", message: "Check the highlighted fields before continuing." });
      setSubmitting(false);
      return false;
    }

    const payload = {
      schemaId: schema.id,
      stepId: activeStep.id,
      submit,
      fields: persistableValues,
      title: typeof values[primaryListField] === "string" ? String(values[primaryListField]) : undefined
    };

    try {
      if (!recordId) {
        const response = await fetch("/api/records", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify(payload)
        });
        const body = await response.json();
        if (!response.ok) throw new Error(body.error ?? "Record creation failed");

        setRecordId(body.record.id);
        setSecureToken(body.record.secureToken);
        setRecordState(body.record.state);

        await uploadAttachmentsIfAny(body.record.id);
      } else {
        const response = await fetch(`/api/records/${recordId}`, {
          method: "PATCH",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            fields: persistableValues,
            stepId: activeStep.id,
            state: submit ? "submitted" : recordState
          })
        });
        const body = await response.json();
        if (!response.ok) throw new Error(body.error ?? "Record update failed");

        setRecordState(body.record.state);
        await uploadAttachmentsIfAny(recordId);
      }

      const savedAt = new Date().toISOString();
      setLastSavedAt(savedAt);
      setNotice({
        tone: "success",
        message: submit ? "Submission sent successfully." : "Draft saved successfully."
      });
      return true;
    } catch (error) {
      setNotice({
        tone: "danger",
        message: error instanceof Error ? error.message : "Unexpected error while saving."
      });
      return false;
    } finally {
      setSubmitting(false);
    }
  }

  async function handleNext() {
    const ok = await persist(false);
    if (!ok) return;
    if (!isFinalStep) {
      setStepIndex((current) => Math.min(current + 1, schema.flow.steps.length - 1));
    }
  }

  async function handleSubmit() {
    const ok = await persist(true);
    if (ok) {
      setRecordState("submitted");
    }
  }

  return (
    <div className="grid gap-5 xl:grid-cols-[minmax(0,1.55fr)_360px]">
      <Surface variant="elevated" className="min-h-[28rem]">
        <div className="flex flex-col gap-5 border-b border-border/70 pb-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div className="space-y-2">
              <div className="eyebrow">Step {stepIndex + 1} of {schema.flow.steps.length}</div>
              <h2 className="text-[1.8rem] font-semibold tracking-[-0.04em] text-heading">{activeStep.title}</h2>
              {activeStep.description ? <p className="max-w-2xl text-sm leading-6 text-muted">{activeStep.description}</p> : null}
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <StateBadge state={recordState} />
              <div className="rounded-full border border-border/70 bg-surface/85 px-3 py-1.5 text-sm text-muted">
                {Math.round(progress)}% complete
              </div>
            </div>
          </div>

          <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
            {stepSummaries.map((entry, index) => {
              const active = index === stepIndex;
              const completed = entry.complete;
              const statusLabel =
                entry.requiredTotal === 0
                  ? completed
                    ? "Ready"
                    : "Not started"
                  : `${entry.completedRequired}/${entry.requiredTotal} required`;

              return (
                <button
                  key={entry.step.id}
                  type="button"
                  onClick={() => setStepIndex(index)}
                  className={cn(
                    "rounded-[18px] border p-3 text-left transition",
                    active
                      ? "border-accent/45 bg-accent/10 shadow-soft"
                      : completed
                        ? "border-success/25 bg-success/8 hover:border-success/35"
                        : "border-border/70 bg-surface/72 hover:border-strong/80 hover:bg-surface/85"
                  )}
                >
                  <div className="flex items-center gap-2">
                    <div
                      className={cn(
                        "flex h-8 w-8 items-center justify-center rounded-full border text-sm font-semibold",
                        active
                          ? "border-accent/35 bg-accent/12 text-accent"
                          : completed
                            ? "border-success/35 bg-success/12 text-success"
                            : "border-border/70 bg-elevated/80 text-muted"
                      )}
                    >
                      {completed ? <CheckCircle2 className="h-4 w-4" /> : index + 1}
                    </div>
                    <div className="min-w-0">
                      <div className="truncate text-sm font-medium text-heading">{entry.step.title}</div>
                      <div className="truncate text-xs text-muted">{statusLabel}</div>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>

          <div className="h-2 rounded-full bg-surface/80">
            <MotionDiv
              className="h-full rounded-full bg-accent"
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.35, ease: "easeOut" }}
            />
          </div>
        </div>

        {notice ? (
          <div
            className={cn(
              "mt-5 rounded-[20px] border px-4 py-3 text-sm",
              notice.tone === "success"
                ? "border-success/25 bg-success/10 text-success"
                : "border-danger/25 bg-danger/10 text-danger"
            )}
          >
            {notice.message}
          </div>
        ) : null}

        {errorCount > 0 ? (
          <div className="mt-5 rounded-[20px] border border-warning/25 bg-warning/10 px-4 py-3 text-sm text-warning">
            {errorCount} field{errorCount === 1 ? " needs" : "s need"} attention before this step can continue.
          </div>
        ) : null}

        <AnimatePresence mode="wait">
          <MotionDiv
            key={activeStep.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.22 }}
            className="mt-6 grid gap-4 md:grid-cols-2"
          >
            {visibleFieldIds.map((fieldId) => {
              const field = getFieldById(schema, fieldId);
              const value = values[field.id];
              const error = errors[field.id];
              const wideField = field.kind === "textarea" || field.kind === "file";

              return (
                <div key={field.id} className={cn("surface-muted p-4", wideField && "md:col-span-2")}>
                  <label className="grid gap-3">
                    <div className="space-y-1.5">
                      <div className="flex flex-wrap items-center gap-2 text-sm font-medium text-heading">
                        {field.label}
                        {field.required ? <span className="rounded-full bg-danger/12 px-2 py-0.5 text-[11px] text-danger">Required</span> : null}
                      </div>
                      {field.helpText ? <div className="text-xs leading-5 text-muted">{field.helpText}</div> : null}
                    </div>

                    {field.kind === "textarea" ? (
                      <Textarea
                        value={typeof value === "string" ? value : ""}
                        onChange={(event) => handleValue(field.id, event.target.value)}
                        placeholder={field.placeholder}
                      />
                    ) : field.kind === "select" ? (
                      <Select value={typeof value === "string" ? value : ""} onChange={(event) => handleValue(field.id, event.target.value)}>
                        <option value="">Select...</option>
                        {(field.options ?? []).map((option) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </Select>
                    ) : field.kind === "checkbox" ? (
                      <button
                        type="button"
                        onClick={() => handleValue(field.id, value !== true)}
                        className={cn(
                          "flex min-h-14 items-center justify-between rounded-[18px] border px-4 py-3 text-left transition",
                          value === true
                            ? "border-accent/40 bg-accent/10"
                            : "border-border/75 bg-surface/92 hover:border-strong/80"
                        )}
                      >
                        <div>
                          <div className="text-sm font-medium text-heading">{value === true ? "Enabled" : "Disabled"}</div>
                          <div className="text-xs text-muted">Use this toggle only when the step requires it.</div>
                        </div>
                        <div
                          className={cn(
                            "flex h-7 w-12 items-center rounded-full border px-1 transition",
                            value === true ? "border-accent/40 bg-accent/14" : "border-border/70 bg-elevated/80"
                          )}
                        >
                          <div className={cn("h-5 w-5 rounded-full bg-heading transition", value === true ? "translate-x-5" : "translate-x-0")} />
                        </div>
                      </button>
                    ) : field.kind === "file" ? (
                      <div className="rounded-[18px] border border-dashed border-border/80 bg-surface/80 p-4">
                        <div className="mb-3 flex items-center gap-2 text-sm text-muted">
                          <FileUp className="h-4 w-4" />
                          Add supporting files when needed.
                        </div>
                        <Input type="file" multiple onChange={(event) => handleValue(field.id, event.target.files ?? null)} />
                        {value instanceof FileList && value.length > 0 ? (
                          <div className="mt-3 grid gap-1 text-xs text-muted">
                            <div>{value.length} file{value.length === 1 ? "" : "s"} selected</div>
                            {Array.from(value)
                              .slice(0, 3)
                              .map((file) => (
                                <div key={file.name} className="truncate">{file.name}</div>
                              ))}
                          </div>
                        ) : typeof value === "string" && value ? (
                          <div className="mt-3 text-xs text-muted">{value}</div>
                        ) : null}
                      </div>
                    ) : field.kind === "number" ? (
                      <Input
                        type="number"
                        value={typeof value === "number" ? value : typeof value === "string" ? value : ""}
                        onChange={(event) => handleValue(field.id, event.target.value === "" ? "" : Number(event.target.value))}
                        placeholder={field.placeholder}
                      />
                    ) : field.kind === "date" ? (
                      <Input
                        type="date"
                        value={typeof value === "string" ? value : ""}
                        onChange={(event) => handleValue(field.id, event.target.value)}
                      />
                    ) : (
                      <Input
                        value={typeof value === "string" ? value : ""}
                        onChange={(event) => handleValue(field.id, event.target.value)}
                        placeholder={field.placeholder}
                      />
                    )}

                    {error ? <div className="text-xs font-medium text-danger">{error}</div> : null}
                  </label>
                </div>
              );
            })}
          </MotionDiv>
        </AnimatePresence>

        <div className="mt-8 rounded-[22px] border border-border/70 bg-surface/84 p-4 shadow-inset">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="space-y-1">
              <div className="text-sm font-medium text-heading">One clear next move</div>
              <div className="text-sm text-muted">
                Save progress as a draft, move to the next step{nextStepTitle ? ` (${nextStepTitle})` : ""}, or submit the record when everything is ready.
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <Button
                variant="ghost"
                disabled={submitting || stepIndex === 0}
                onClick={() => setStepIndex((current) => Math.max(0, current - 1))}
              >
                <ChevronLeft className="h-4 w-4" />
                Back
              </Button>
              <Button variant="secondary" disabled={submitting} onClick={() => persist(false)}>
                <Save className="h-4 w-4" />
                Save Draft
              </Button>
              {!isFinalStep ? (
                <Button variant="primary" disabled={submitting} onClick={handleNext}>
                  {submitting ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <ChevronRight className="h-4 w-4" />}
                  Save and Continue
                </Button>
              ) : (
                <Button variant="primary" disabled={submitting} onClick={handleSubmit}>
                  {submitting ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
                  Submit for Review
                </Button>
              )}
            </div>
          </div>
        </div>
      </Surface>

      <div className="grid gap-5 self-start xl:sticky xl:top-24">
        <Surface title="Session summary" subtitle="Keep the essentials visible while completing the flow.">
          <div className="grid gap-3">
            <StatCard label="Progress" value={`${Math.round(progress)}%`} meta={`Step ${stepIndex + 1} of ${schema.flow.steps.length}`} tone="accent" icon={<Workflow className="h-5 w-5" />} />
            <StatCard label="Required remaining" value={String(remainingRequired)} meta="Open required inputs still missing across the flow." tone={remainingRequired === 0 ? "success" : "warning"} icon={<Sparkles className="h-5 w-5" />} />
            <div className="surface-muted px-3 py-3">
              <div className="metric-label">Current state</div>
              <div className="mt-2"><StateBadge state={recordState} /></div>
              <div className="mt-2 text-sm text-muted">{stateDescription(recordState)}</div>
            </div>
            <div className="surface-muted px-3 py-3">
              <div className="metric-label">Record id</div>
              <div className="mt-1 break-all text-sm text-heading">{recordId ?? "Created after the first save."}</div>
            </div>
            <div className="surface-muted px-3 py-3">
              <div className="metric-label">Resume token</div>
              <div className="mt-1 break-all text-sm text-heading">{secureToken ?? "Generated once the record is first saved."}</div>
            </div>
            <div className="surface-muted px-3 py-3">
              <div className="metric-label">Last save</div>
              <div className="mt-1 text-sm text-heading">{lastSavedAt ? formatRelativeTime(lastSavedAt) : "Not saved yet."}</div>
            </div>
          </div>
        </Surface>

        <Surface title="Why this feels safe" subtitle="A few cues that reduce uncertainty while users move through the flow.">
          <div className="grid gap-3">
            <div className="surface-muted flex gap-3 px-3 py-3">
              <Shield className="mt-0.5 h-4 w-4 shrink-0 text-accent" />
              <div>
                <div className="text-sm font-medium text-heading">Inline validation</div>
                <div className="mt-1 text-sm text-muted">Required fields are checked before the flow moves forward.</div>
              </div>
            </div>
            <div className="surface-muted flex gap-3 px-3 py-3">
              <LockKeyhole className="mt-0.5 h-4 w-4 shrink-0 text-accent" />
              <div>
                <div className="text-sm font-medium text-heading">Resume token</div>
                <div className="mt-1 text-sm text-muted">A secure token appears after the first save so work can resume later.</div>
              </div>
            </div>
            <div className="surface-muted flex gap-3 px-3 py-3">
              <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-accent" />
              <div>
                <div className="text-sm font-medium text-heading">Clear next action</div>
                <div className="mt-1 text-sm text-muted">The footer keeps draft save, step progress, and final submission distinct.</div>
              </div>
            </div>
          </div>
        </Surface>
      </div>
    </div>
  );
}
