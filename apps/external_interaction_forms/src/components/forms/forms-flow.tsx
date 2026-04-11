"use client";

import { useAnimate } from "framer-motion";
import { useEffect, useMemo, useState } from "react";
import {
  createDraft,
  submitFinal,
  updateByToken,
  uploadAttachment
} from "@/lib/api/forms-api";
import type { DraftRecordRef, Step1Input, Step2Input } from "@/lib/api/types";
import { brandConfig } from "@/lib/config/brand";
import {
  clearDraftLocal,
  loadDraftLocal,
  saveDraftLocal
} from "@/lib/storage/draft-storage";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils/cn";

type StepIndex = 1 | 2 | 3;

const emptyStep1: Step1Input = {
  request_title: "",
  request_description: "",
  request_priority: "medium",
  requester_name: "",
  requester_email: ""
};

const emptyStep2: Step2Input = {
  required_by: "",
  region: "",
  needs_attachment: false
};

type Step1Errors = Partial<Record<keyof Step1Input, string>>;

function parseError(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }

  return "No fue posible completar la solicitud. Intenta de nuevo.";
}

function validateStep1(values: Step1Input): Step1Errors {
  const errors: Step1Errors = {};

  if (!values.request_title.trim()) {
    errors.request_title = "Escribe un titulo para tu solicitud.";
  }

  if (!values.request_description.trim()) {
    errors.request_description = "Describe la solicitud con un poco mas de detalle.";
  }

  if (!values.requester_name.trim()) {
    errors.requester_name = "Comparte tu nombre.";
  }

  const emailValue = values.requester_email.trim();
  if (!emailValue) {
    errors.requester_email = "Comparte un correo de contacto.";
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailValue)) {
    errors.requester_email = "Ingresa un correo valido.";
  }

  return errors;
}

function StepIndicator({ step }: { readonly step: StepIndex }) {
  const labels: Array<{ readonly key: 1 | 2; readonly title: string }> = [
    { key: 1, title: "Tus datos y solicitud" },
    { key: 2, title: "Contexto" }
  ];

  return (
    <ol className="mb-6 grid grid-cols-2 gap-3 sm:mb-8">
      {labels.map((item) => {
        const active = step === item.key;
        const done = step > item.key || step === 3;
        return (
          <li
            key={item.key}
            className={cn(
              "rounded-2xl border px-3 py-3 sm:px-4",
              active ? "border-accent bg-accentSoft/55" : "border-line bg-soft/40"
            )}
          >
            <p className="m-0 text-[11px] uppercase tracking-[0.12em] text-muted">
              Paso {item.key}
            </p>
            <p className="mt-1 text-sm font-semibold text-ink">{item.title}</p>
            <p className="mt-1 text-xs text-muted">{done ? "Listo" : active ? "En curso" : "Pendiente"}</p>
          </li>
        );
      })}
    </ol>
  );
}

function FieldError({ message }: { readonly message?: string }) {
  if (!message) {
    return null;
  }

  return <p className="mt-2 text-xs font-medium text-danger">{message}</p>;
}

export function FormsFlow() {
  const [scope, animate] = useAnimate();
  const [step, setStep] = useState<StepIndex>(1);
  const [step1, setStep1] = useState<Step1Input>(emptyStep1);
  const [step2, setStep2] = useState<Step2Input>(emptyStep2);
  const [recordRef, setRecordRef] = useState<DraftRecordRef | null>(null);
  const [attachment, setAttachment] = useState<File | null>(null);
  const [step1Errors, setStep1Errors] = useState<Step1Errors>({});
  const [busy, setBusy] = useState(false);
  const [banner, setBanner] = useState<string | null>(null);

  useEffect(() => {
    const draft = loadDraftLocal();
    if (!draft) {
      return;
    }

    setStep1(draft.step1);
    setStep2(draft.step2);
    setRecordRef({
      recordId: draft.recordId,
      secureToken: draft.secureToken
    });
    setStep(2);
    setBanner("Recuperamos tu borrador local para que sigas donde te quedaste.");
  }, []);

  useEffect(() => {
    if (!recordRef || step === 3) {
      return;
    }

    saveDraftLocal({
      recordId: recordRef.recordId,
      secureToken: recordRef.secureToken,
      step1,
      step2,
      savedAtIso: new Date().toISOString()
    });
  }, [recordRef, step, step1, step2]);

  useEffect(() => {
    void animate(
      "[data-step-surface='active']",
      { opacity: [0, 1], y: [8, 0] },
      { duration: 0.22, ease: "easeOut" }
    );
  }, [animate, step]);

  const helperCopy = useMemo(() => {
    if (step === 1) {
      return "Comparte la informacion principal para crear un borrador seguro.";
    }
    if (step === 2) {
      return "Completa el contexto opcional antes del envio final.";
    }
    return brandConfig.successDescription;
  }, [step]);

  async function handleStep1Submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBanner(null);

    const errors = validateStep1(step1);
    setStep1Errors(errors);

    if (Object.keys(errors).length > 0) {
      return;
    }

    setBusy(true);
    try {
      const draftRef = await createDraft(step1);
      setRecordRef(draftRef);
      saveDraftLocal({
        recordId: draftRef.recordId,
        secureToken: draftRef.secureToken,
        step1,
        step2,
        savedAtIso: new Date().toISOString()
      });
      setStep(2);
      setBanner("Borrador creado. Puedes continuar con el contexto.");
    } catch (error) {
      setBanner(parseError(error));
    } finally {
      setBusy(false);
    }
  }

  async function handleStep2Submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!recordRef) {
      setBanner("No encontramos el token del borrador. Regresa al paso 1.");
      setStep(1);
      return;
    }

    setBusy(true);
    setBanner(null);
    try {
      await updateByToken(recordRef.secureToken, step2);

      if (step2.needs_attachment && attachment) {
        await uploadAttachment(recordRef.recordId, attachment);
      }

      await submitFinal(recordRef.secureToken, step2);
      clearDraftLocal();
      setStep(3);
      setAttachment(null);
      setBanner(null);
    } catch (error) {
      setBanner(parseError(error));
    } finally {
      setBusy(false);
    }
  }

  function resetAll() {
    clearDraftLocal();
    setStep(1);
    setStep1(emptyStep1);
    setStep2(emptyStep2);
    setStep1Errors({});
    setRecordRef(null);
    setAttachment(null);
    setBanner(null);
  }

  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-8 sm:px-6 sm:py-12">
      <section className="mb-6 rounded-3xl border border-line/80 bg-panel/70 px-5 py-4 shadow-soft sm:px-6">
        <p className="m-0 text-[11px] uppercase tracking-[0.14em] text-muted">
          Formulario publico
        </p>
        <h1 className="m-0 mt-1 text-3xl text-ink sm:text-4xl">{brandConfig.appName}</h1>
        <p className="mt-2 text-sm leading-6 text-muted">{brandConfig.tagline}</p>
      </section>

      <StepIndicator step={step} />

      <Card>
        <CardHeader>
          <CardTitle>{step === 1 ? "Tus datos y solicitud" : step === 2 ? "Contexto" : brandConfig.successTitle}</CardTitle>
          <CardDescription>{helperCopy}</CardDescription>
        </CardHeader>
        <CardContent>
          <div ref={scope}>
          {banner ? (
            <div className="mb-5 rounded-xl border border-accent/30 bg-accentSoft/55 px-4 py-3 text-sm text-ink">
              {banner}
            </div>
          ) : null}

          {step === 1 ? (
            <form onSubmit={handleStep1Submit} className="grid gap-4" data-step-surface="active">
                <div>
                  <Label htmlFor="request_title">Titulo de la solicitud</Label>
                  <Input
                    id="request_title"
                    value={step1.request_title}
                    onChange={(event) =>
                      setStep1((current) => ({ ...current, request_title: event.target.value }))
                    }
                    placeholder="Ej. Solicitud de apoyo operativo"
                    autoComplete="off"
                    required
                  />
                  <FieldError message={step1Errors.request_title} />
                </div>

                <div>
                  <Label htmlFor="request_description">Descripcion</Label>
                  <Textarea
                    id="request_description"
                    value={step1.request_description}
                    onChange={(event) =>
                      setStep1((current) => ({ ...current, request_description: event.target.value }))
                    }
                    placeholder="Explica brevemente que necesitas y por que."
                    required
                  />
                  <FieldError message={step1Errors.request_description} />
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <Label htmlFor="request_priority">Prioridad</Label>
                    <Select
                      id="request_priority"
                      value={step1.request_priority}
                      onChange={(event) =>
                        setStep1((current) => ({
                          ...current,
                          request_priority: event.target.value as Step1Input["request_priority"]
                        }))
                      }
                      required
                    >
                      <option value="low">low</option>
                      <option value="medium">medium</option>
                      <option value="high">high</option>
                      <option value="urgent">urgent</option>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="requester_name">Nombre</Label>
                    <Input
                      id="requester_name"
                      value={step1.requester_name}
                      onChange={(event) =>
                        setStep1((current) => ({ ...current, requester_name: event.target.value }))
                      }
                      placeholder="Tu nombre completo"
                      autoComplete="name"
                      required
                    />
                    <FieldError message={step1Errors.requester_name} />
                  </div>
                </div>

                <div>
                  <Label htmlFor="requester_email">Correo</Label>
                  <Input
                    id="requester_email"
                    type="email"
                    value={step1.requester_email}
                    onChange={(event) =>
                      setStep1((current) => ({ ...current, requester_email: event.target.value }))
                    }
                    placeholder="nombre@empresa.com"
                    autoComplete="email"
                    required
                  />
                  <FieldError message={step1Errors.requester_email} />
                </div>

                <Button type="submit" disabled={busy} className="mt-2 w-full sm:w-auto">
                  {busy ? "Creando borrador..." : "Guardar y continuar"}
                </Button>
              </form>
            ) : null}

          {step === 2 ? (
            <form onSubmit={handleStep2Submit} className="grid gap-4" data-step-surface="active">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <Label htmlFor="required_by">Fecha requerida</Label>
                    <Input
                      id="required_by"
                      type="date"
                      value={step2.required_by}
                      onChange={(event) =>
                        setStep2((current) => ({ ...current, required_by: event.target.value }))
                      }
                    />
                  </div>

                  <div>
                    <Label htmlFor="region">Region</Label>
                    <Select
                      id="region"
                      value={step2.region}
                      onChange={(event) =>
                        setStep2((current) => ({
                          ...current,
                          region: event.target.value as Step2Input["region"]
                        }))
                      }
                    >
                      <option value="">Sin region</option>
                      <option value="north">north</option>
                      <option value="south">south</option>
                      <option value="east">east</option>
                      <option value="west">west</option>
                      <option value="global">global</option>
                    </Select>
                  </div>
                </div>

                <div className="rounded-xl border border-line bg-soft/45 px-4 py-3">
                  <label className="inline-flex cursor-pointer items-center gap-3 text-sm font-medium text-ink">
                    <Checkbox
                      checked={step2.needs_attachment}
                      onChange={(event) =>
                        setStep2((current) => ({
                          ...current,
                          needs_attachment: event.target.checked
                        }))
                      }
                    />
                    Necesito agregar un archivo adjunto
                  </label>
                  {step2.needs_attachment ? (
                    <div className="mt-3">
                      <Input
                        type="file"
                        onChange={(event) => setAttachment(event.target.files?.[0] ?? null)}
                      />
                      <p className="mt-2 text-xs text-muted">
                        Si recargas la pagina, deberas seleccionar el archivo otra vez.
                      </p>
                    </div>
                  ) : null}
                </div>

                <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => setStep(1)}
                    className="w-full sm:w-auto"
                    disabled={busy}
                  >
                    Volver
                  </Button>
                  <Button type="submit" disabled={busy} className="w-full sm:w-auto">
                    {busy ? "Enviando..." : "Enviar solicitud"}
                  </Button>
                </div>
              </form>
            ) : null}

          {step === 3 ? (
            <div className="space-y-4" data-step-surface="active">
                <div className="rounded-2xl border border-success/35 bg-success/10 px-4 py-4">
                  <p className="m-0 text-xs uppercase tracking-[0.12em] text-success">Completado</p>
                  <h2 className="m-0 mt-1 text-3xl text-ink">{brandConfig.successTitle}</h2>
                  <p className="mt-2 text-sm leading-6 text-muted">{brandConfig.successDescription}</p>
                  {recordRef ? (
                    <p className="mt-3 text-xs text-muted">
                      Folio: <span className="font-semibold text-ink">{recordRef.recordId}</span>
                    </p>
                  ) : null}
                </div>

                <Button type="button" onClick={resetAll}>
                  Enviar otra solicitud
                </Button>
              </div>
            ) : null}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
