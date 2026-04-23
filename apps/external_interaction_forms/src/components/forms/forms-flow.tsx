"use client";

import { useAnimate } from "framer-motion";
import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  clearFormDraftLocal,
  getFormPlugin,
  listFormPlugins,
  loadFormDraftLocal,
  persistStepDraft,
  resolveFormTypeId,
  saveFormDraftLocal,
  submitFinalRecord,
  validateCurrentStep
} from "@/lib/forms";
import type {
  DraftRecordRef,
  FormFieldDefinition,
  FormFieldErrors,
  FormPluginDefinition,
  FormValues
} from "@/lib/forms/contracts";
import { cn } from "@/lib/utils/cn";

function parseError(error: unknown): string {
  if (error instanceof Error) return error.message;
  return "No fue posible completar la solicitud. Intenta de nuevo.";
}

function StepIndicator({
  plugin,
  stepIndex,
  completed
}: {
  plugin: FormPluginDefinition;
  stepIndex: number;
  completed: boolean;
}) {
  return (
    <ol className="mb-6 grid gap-3 sm:mb-8" style={{ gridTemplateColumns: `repeat(${plugin.steps.length}, minmax(0, 1fr))` }}>
      {plugin.steps.map((step, index) => {
        const active = stepIndex === index && !completed;
        const done = completed || stepIndex > index;

        return (
          <li
            key={step.id}
            className={cn(
              "rounded-2xl border px-3 py-3 sm:px-4",
              active ? "border-accent bg-accentSoft/55" : "border-line bg-soft/40"
            )}
          >
            <p className="m-0 text-[11px] uppercase tracking-[0.12em] text-muted">Paso {index + 1}</p>
            <p className="mt-1 text-sm font-semibold text-ink">{step.title}</p>
            <p className="mt-1 text-xs text-muted">{done ? "Listo" : active ? "En curso" : "Pendiente"}</p>
          </li>
        );
      })}
    </ol>
  );
}

function FieldError({ message }: { message?: string }) {
  if (!message) return null;
  return <p className="mt-2 text-xs font-medium text-danger">{message}</p>;
}

function visibleFields(stepFields: readonly FormFieldDefinition[], values: FormValues): FormFieldDefinition[] {
  return stepFields.filter((field) => {
    if (!field.visibleWhen) return true;
    return field.visibleWhen(values);
  });
}

export function FormsFlow({ initialFormTypeId }: { initialFormTypeId?: string }) {
  const [scope, animate] = useAnimate();
  const plugins = useMemo(() => listFormPlugins(), []);
  const [formTypeId, setFormTypeId] = useState(() => resolveFormTypeId(initialFormTypeId));
  const plugin = useMemo(() => getFormPlugin(formTypeId), [formTypeId]);

  if (plugin.steps.length === 0) {
    throw new Error(`Form plugin '${plugin.formTypeId}' has no steps`);
  }

  const [stepIndex, setStepIndex] = useState(0);
  const [values, setValues] = useState<FormValues>(() => plugin.defaults());
  const [files, setFiles] = useState<Record<string, File | null>>({});
  const [recordRef, setRecordRef] = useState<DraftRecordRef | null>(null);
  const [busy, setBusy] = useState(false);
  const [banner, setBanner] = useState<string | null>(null);
  const [errors, setErrors] = useState<FormFieldErrors>({});
  const [completed, setCompleted] = useState(false);

  const activeStep = (plugin.steps[stepIndex] ?? plugin.steps[0])!;
  const lastStepIndex = plugin.steps.length - 1;
  const isFinalStep = stepIndex === lastStepIndex;

  useEffect(() => {
    void animate("[data-step-surface='active']", { opacity: [0, 1], y: [8, 0] }, { duration: 0.22, ease: "easeOut" });
  }, [animate, formTypeId, stepIndex, completed]);

  useEffect(() => {
    const draft = loadFormDraftLocal();
    const defaults = plugin.defaults();

    if (draft && draft.formTypeId === plugin.formTypeId) {
      setValues({ ...defaults, ...draft.values });
      setRecordRef(draft.recordRef);
      setStepIndex(Math.min(Math.max(draft.stepIndex ?? 1, 0), plugin.steps.length - 1));
      setBanner("Recuperamos tu borrador local para que sigas donde te quedaste.");
    } else {
      setValues(defaults);
      setRecordRef(null);
      setStepIndex(0);
      setBanner(null);
    }

    setFiles({});
    setErrors({});
    setCompleted(false);
  }, [plugin]);

  useEffect(() => {
    if (!recordRef || completed) return;
    saveFormDraftLocal({
      formTypeId: plugin.formTypeId,
      recordRef,
      values,
      savedAtIso: new Date().toISOString(),
      stepIndex
    });
  }, [completed, plugin.formTypeId, recordRef, stepIndex, values]);

  const helperCopy = useMemo(() => {
    if (completed) return plugin.display.successDescription;
    return activeStep.description;
  }, [activeStep.description, completed, plugin.display.successDescription]);

  const stepFields = useMemo(() => visibleFields(activeStep.fields, values), [activeStep, values]);

  function setValue(fieldId: string, value: string | boolean) {
    setValues((current) => ({ ...current, [fieldId]: value }));
    setErrors((current) => {
      if (!current[fieldId]) return current;
      const next = { ...current };
      delete next[fieldId];
      return next;
    });
  }

  function setAttachment(fieldId: string, file: File | null) {
    setFiles((current) => ({ ...current, [fieldId]: file }));
    setErrors((current) => {
      if (!current[fieldId]) return current;
      const next = { ...current };
      delete next[fieldId];
      return next;
    });
  }

  async function handleStepSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!activeStep) return;

    setBanner(null);
    const validationErrors = validateCurrentStep(plugin, activeStep.id, values, files);
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length > 0) return;

    if (!recordRef && stepIndex > 0) {
      setBanner("No encontramos el token del borrador. Regresa al paso 1.");
      setStepIndex(0);
      return;
    }

    setBusy(true);
    try {
      if (!isFinalStep) {
        const persisted = await persistStepDraft({
          plugin,
          stepId: activeStep.id,
          values,
          existingRef: recordRef
        });

        setRecordRef(persisted.recordRef);
        setStepIndex((current) => Math.min(current + 1, lastStepIndex));
        setBanner("Borrador guardado. Puedes continuar con el siguiente paso.");
      } else {
        let activeRecordRef = recordRef;
        if (!activeRecordRef) {
          const created = await persistStepDraft({
            plugin,
            stepId: activeStep.id,
            values,
            existingRef: null
          });
          activeRecordRef = created.recordRef;
          setRecordRef(activeRecordRef);
        }

        const submitted = await submitFinalRecord({
          plugin,
          stepId: activeStep.id,
          values,
          files,
          recordRef: activeRecordRef
        });
        setRecordRef(submitted.recordRef);
        clearFormDraftLocal();
        setCompleted(true);
      }
    } catch (error) {
      setBanner(parseError(error));
    } finally {
      setBusy(false);
    }
  }

  function resetAll() {
    clearFormDraftLocal();
    setValues(plugin.defaults());
    setFiles({});
    setErrors({});
    setRecordRef(null);
    setStepIndex(0);
    setBanner(null);
    setCompleted(false);
  }

  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-8 sm:px-6 sm:py-12">
      <section className="mb-6 rounded-3xl border border-line/80 bg-panel/70 px-5 py-4 shadow-soft sm:px-6">
        <p className="m-0 text-[11px] uppercase tracking-[0.14em] text-muted">Formulario publico</p>
        <div className="mt-3 grid gap-3 sm:grid-cols-[minmax(0,1fr)_260px] sm:items-start">
          <div>
            <h1 className="m-0 text-3xl text-ink sm:text-4xl">{plugin.display.appName}</h1>
            <p className="mt-2 text-sm leading-6 text-muted">{plugin.display.tagline}</p>
          </div>
          <div>
            <Label htmlFor="form_type_select">Tipo de formulario</Label>
            <Select
              id="form_type_select"
              value={formTypeId}
              onChange={(event) => setFormTypeId(resolveFormTypeId(event.target.value))}
              disabled={busy}
            >
              {plugins.map((entry) => (
                <option key={entry.formTypeId} value={entry.formTypeId}>
                  {entry.display.menuLabel}
                </option>
              ))}
            </Select>
          </div>
        </div>
      </section>

      <StepIndicator plugin={plugin} stepIndex={stepIndex} completed={completed} />

      <Card>
        <CardHeader>
          <CardTitle>{completed ? plugin.display.successTitle : activeStep?.title}</CardTitle>
          <CardDescription>{helperCopy}</CardDescription>
        </CardHeader>
        <CardContent>
          <div ref={scope}>
            {banner ? (
              <div className="mb-5 rounded-xl border border-accent/30 bg-accentSoft/55 px-4 py-3 text-sm text-ink">{banner}</div>
            ) : null}

            {completed ? (
              <div className="space-y-4" data-step-surface="active">
                <div className="rounded-2xl border border-success/35 bg-success/10 px-4 py-4">
                  <p className="m-0 text-xs uppercase tracking-[0.12em] text-success">Completado</p>
                  <h2 className="m-0 mt-1 text-3xl text-ink">{plugin.display.successTitle}</h2>
                  <p className="mt-2 text-sm leading-6 text-muted">{plugin.display.successDescription}</p>
                  {recordRef ? (
                    <p className="mt-3 text-xs text-muted">
                      Folio: <span className="font-semibold text-ink">{recordRef.recordId}</span>
                    </p>
                  ) : null}
                </div>

                <Button type="button" onClick={resetAll}>
                  Enviar otro formulario
                </Button>
              </div>
            ) : (
              <form onSubmit={handleStepSubmit} className="grid gap-4" data-step-surface="active">
                {stepFields.map((field) => {
                  const value = values[field.id];
                  const error = errors[field.id];

                  if (field.kind === "checkbox") {
                    return (
                      <div key={field.id} className="rounded-xl border border-line bg-soft/45 px-4 py-3">
                        <label className="inline-flex cursor-pointer items-center gap-3 text-sm font-medium text-ink">
                          <Checkbox
                            checked={value === true}
                            onChange={(event) => setValue(field.id, event.target.checked)}
                          />
                          {field.label}
                        </label>
                        {field.helpText ? <p className="mt-2 text-xs text-muted">{field.helpText}</p> : null}
                        <FieldError message={error} />
                      </div>
                    );
                  }

                  if (field.kind === "file") {
                    return (
                      <div key={field.id}>
                        <Label htmlFor={field.id}>{field.label}</Label>
                        <Input
                          id={field.id}
                          type="file"
                          onChange={(event) => setAttachment(field.id, event.target.files?.[0] ?? null)}
                        />
                        {field.helpText ? <p className="mt-2 text-xs text-muted">{field.helpText}</p> : null}
                        <FieldError message={error} />
                      </div>
                    );
                  }

                  if (field.kind === "textarea") {
                    return (
                      <div key={field.id}>
                        <Label htmlFor={field.id}>{field.label}</Label>
                        <Textarea
                          id={field.id}
                          value={String(value ?? "")}
                          onChange={(event) => setValue(field.id, event.target.value)}
                          placeholder={field.placeholder}
                          required={field.required}
                        />
                        {field.helpText ? <p className="mt-2 text-xs text-muted">{field.helpText}</p> : null}
                        <FieldError message={error} />
                      </div>
                    );
                  }

                  if (field.kind === "select") {
                    return (
                      <div key={field.id}>
                        <Label htmlFor={field.id}>{field.label}</Label>
                        <Select
                          id={field.id}
                          value={String(value ?? "")}
                          onChange={(event) => setValue(field.id, event.target.value)}
                          required={field.required}
                        >
                          {field.options?.map((option) => (
                            <option key={option.value} value={option.value}>
                              {option.label}
                            </option>
                          ))}
                        </Select>
                        {field.helpText ? <p className="mt-2 text-xs text-muted">{field.helpText}</p> : null}
                        <FieldError message={error} />
                      </div>
                    );
                  }

                  return (
                    <div key={field.id}>
                      <Label htmlFor={field.id}>{field.label}</Label>
                      <Input
                        id={field.id}
                        type={field.kind === "email" ? "email" : field.kind === "date" ? "date" : "text"}
                        value={String(value ?? "")}
                        onChange={(event) => setValue(field.id, event.target.value)}
                        placeholder={field.placeholder}
                        required={field.required}
                        autoComplete={field.kind === "email" ? "email" : "off"}
                      />
                      {field.helpText ? <p className="mt-2 text-xs text-muted">{field.helpText}</p> : null}
                      <FieldError message={error} />
                    </div>
                  );
                })}

                <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                  {stepIndex > 0 ? (
                    <Button
                      type="button"
                      variant="ghost"
                      onClick={() => setStepIndex((current) => Math.max(current - 1, 0))}
                      className="w-full sm:w-auto"
                      disabled={busy}
                    >
                      Volver
                    </Button>
                  ) : null}

                  <Button type="submit" disabled={busy} className="w-full sm:w-auto">
                    {busy ? (isFinalStep ? "Enviando..." : "Guardando...") : activeStep?.submitLabel}
                  </Button>
                </div>
              </form>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
