"use client";

import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, ChevronLeft, ChevronRight, LoaderCircle, Save } from "lucide-react";
import { useMemo, useState } from "react";
import type { ComponentType } from "react";

import { Badge } from "@components/ui/badge";
import { Button } from "@components/ui/button";
import { Input } from "@components/ui/input";
import { Select } from "@components/ui/select";
import { Surface } from "@components/ui/surface";
import { Textarea } from "@components/ui/textarea";
import { getFieldById } from "@/lib/core/schema-registry";
import { stateLabel } from "@/lib/core/record-view";
import { type ExternalRecord, type RecordTypeSchema } from "@/lib/core/types";
import { validateStepPayload } from "@/lib/core/validation";
import { isFieldVisible } from "@/lib/core/visibility";

interface FlowRunnerProps {
  schema: RecordTypeSchema;
  initialRecord?: ExternalRecord | null;
}

export function FlowRunner({ schema, initialRecord }: FlowRunnerProps) {
  const [stepIndex, setStepIndex] = useState(0);
  const [recordId, setRecordId] = useState<string | null>(initialRecord?.id ?? null);
  const [secureToken, setSecureToken] = useState<string | null>(initialRecord?.secureToken ?? null);
  const [recordState, setRecordState] = useState<ExternalRecord["state"]>(initialRecord?.state ?? "draft");
  const [values, setValues] = useState<Record<string, unknown>>(initialRecord?.fields ?? {});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [notice, setNotice] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const step = schema.flow.steps[stepIndex];
  const MotionDiv = motion.div as unknown as ComponentType<any>;
  const primaryListField = schema.views.listFields[0] ?? schema.fields[0]?.id ?? "title";
  if (!step) {
    return (
      <Surface title="Flow configuration issue">
        <p className="text-sm text-danger">No steps configured for this schema.</p>
      </Surface>
    );
  }
  const activeStep = step;
  const isFinalStep = stepIndex === schema.flow.steps.length - 1;

  const progress = ((stepIndex + 1) / Math.max(1, schema.flow.steps.length)) * 100;

  const visibleFieldIds = useMemo(
    () =>
      activeStep.fieldIds.filter((fieldId) => {
        const field = getFieldById(schema, fieldId);
        return isFieldVisible(field, values, "external_user");
      }),
    [schema, activeStep.fieldIds, values]
  );

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
        await fetch(`/api/records/${targetRecordId}/attachments`, {
          method: "POST",
          body: formData
        });
      }

      handleValue(fieldId, `${candidate.length} attachment(s)`);
    }
  }

  async function persist(submit: boolean) {
    setSubmitting(true);
    setNotice(null);

    const validation = validateStepPayload(schema, activeStep.id, values, "external_user");
    if (!validation.ok) {
      setErrors(validation.errors);
      setSubmitting(false);
      return false;
    }

    const payload = {
      schemaId: schema.id,
      stepId: activeStep.id,
      submit,
      fields: values,
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
            fields: values,
            stepId: activeStep.id,
            state: submit ? "submitted" : recordState
          })
        });
        const body = await response.json();
        if (!response.ok) throw new Error(body.error ?? "Record update failed");

        setRecordState(body.record.state);
        await uploadAttachmentsIfAny(recordId);
      }

      setNotice(submit ? "Submission sent successfully." : "Draft saved successfully.");
      return true;
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Unexpected error while saving.");
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
    <div className="grid gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
      <Surface
        className="min-h-[24rem]"
        title={activeStep.title}
        subtitle={activeStep.description}
        actions={<Badge tone="accent">Step {stepIndex + 1}</Badge>}
      >
        <div className="mb-5 h-1.5 rounded-full bg-white/8">
          <MotionDiv
            className="h-full rounded-full bg-accent/70"
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.35, ease: "easeOut" }}
          />
        </div>

        <AnimatePresence mode="wait">
          <MotionDiv
            key={activeStep.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.22 }}
            className="grid gap-4"
          >
            {visibleFieldIds.map((fieldId) => {
              const field = getFieldById(schema, fieldId);
              const value = values[field.id];
              const error = errors[field.id];

              return (
                <label key={field.id} className="grid gap-1.5">
                  <div className="flex items-center gap-2 text-sm font-medium text-text">
                    {field.label}
                    {field.required ? <span className="text-danger">*</span> : null}
                  </div>
                  {field.helpText ? <div className="text-xs text-muted">{field.helpText}</div> : null}

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
                    <div className="flex h-10 items-center rounded-xl border border-white/12 bg-surface/60 px-3">
                      <input
                        type="checkbox"
                        checked={value === true}
                        onChange={(event) => handleValue(field.id, event.target.checked)}
                        className="h-4 w-4 rounded border-white/20 bg-canvas/90"
                      />
                      <span className="ml-2 text-sm text-muted">Toggle</span>
                    </div>
                  ) : field.kind === "file" ? (
                    <Input type="file" multiple onChange={(event) => handleValue(field.id, event.target.files ?? null)} />
                  ) : field.kind === "number" ? (
                    <Input
                      type="number"
                      value={typeof value === "number" ? value : ""}
                      onChange={(event) => handleValue(field.id, Number(event.target.value))}
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

                  {error ? <div className="text-xs text-danger">{error}</div> : null}
                </label>
              );
            })}
          </MotionDiv>
        </AnimatePresence>

        <div className="mt-6 flex flex-wrap items-center gap-2 border-t border-white/10 pt-4">
          <Button
            variant="ghost"
            disabled={submitting || stepIndex === 0}
            onClick={() => setStepIndex((current) => Math.max(0, current - 1))}
          >
            <ChevronLeft className="mr-1 h-4 w-4" />
            Back
          </Button>
          {!isFinalStep ? (
            <Button variant="primary" disabled={submitting} onClick={handleNext}>
              {submitting ? <LoaderCircle className="mr-1 h-4 w-4 animate-spin" /> : <ChevronRight className="mr-1 h-4 w-4" />}
              Save & Continue
            </Button>
          ) : (
            <Button variant="primary" disabled={submitting} onClick={handleSubmit}>
              {submitting ? <LoaderCircle className="mr-1 h-4 w-4 animate-spin" /> : <CheckCircle2 className="mr-1 h-4 w-4" />}
              Submit
            </Button>
          )}
          <Button variant="secondary" disabled={submitting} onClick={() => persist(false)}>
            <Save className="mr-1 h-4 w-4" />
            Save Draft
          </Button>
        </div>
      </Surface>

      <div className="grid gap-4">
        <Surface title="Flow Status" subtitle="Current progress and session metadata.">
          <div className="grid gap-2 text-sm text-muted">
            <div className="flex items-center justify-between rounded-lg bg-canvas/35 px-3 py-2">
              <span>State</span>
              <Badge tone="accent">{stateLabel(recordState)}</Badge>
            </div>
            <div className="flex items-center justify-between rounded-lg bg-canvas/35 px-3 py-2">
              <span>Step</span>
              <span className="text-text">{stepIndex + 1}/{schema.flow.steps.length}</span>
            </div>
            <div className="rounded-lg bg-canvas/35 px-3 py-2">
              <div className="mb-1 text-[11px] uppercase tracking-[0.08em] text-muted">Record id</div>
              <div className="break-all text-xs text-text">{recordId ?? "Not created yet"}</div>
            </div>
            <div className="rounded-lg bg-canvas/35 px-3 py-2">
              <div className="mb-1 text-[11px] uppercase tracking-[0.08em] text-muted">Secure token</div>
              <div className="break-all text-xs text-text">{secureToken ?? "Will be generated when first saved"}</div>
            </div>
          </div>
        </Surface>

        <Surface title="Step Navigator" subtitle="Jump between configured flow steps.">
          <div className="grid gap-2">
            {schema.flow.steps.map((entry, index) => (
              <button
                key={entry.id}
                type="button"
                onClick={() => setStepIndex(index)}
                className={`rounded-lg border px-3 py-2 text-left transition ${
                  index === stepIndex
                    ? "border-accent/45 bg-accent/12"
                    : "border-white/10 bg-canvas/35 hover:border-white/20 hover:bg-canvas/45"
                }`}
              >
                <div className="text-sm font-medium text-text">{entry.title}</div>
                <div className="text-xs text-muted">{entry.description}</div>
              </button>
            ))}
          </div>
        </Surface>

        {notice ? (
          <Surface title="Latest Message">
            <p className="text-sm text-text">{notice}</p>
          </Surface>
        ) : null}
      </div>
    </div>
  );
}
