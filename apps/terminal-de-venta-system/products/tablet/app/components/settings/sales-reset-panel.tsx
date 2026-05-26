"use client";

import { useMemo, useState, type ChangeEvent, type FormEvent } from "react";
import { requestJson } from "@/lib/pos/cart-state";
import type { SalesResetPreview } from "@/server/pos-api/sales-reset.prisma";
import styles from "@components/license/license-ui.module.css";

type ResetResult = {
  resetId: string;
  businessId: string;
  before: Record<string, number>;
  after: Record<string, number>;
  preservesLicenseConfig: boolean;
  preservesCatalogAndInventory: boolean;
};

type ConfigureResult = {
  businessId: string;
  configured: boolean;
  questionId: string;
  configuredAt: string;
};

type Props = {
  preview: SalesResetPreview;
};

function countEntries(counts: Record<string, number>) {
  return Object.entries(counts).filter(([, value]) => Number(value) > 0);
}

export function SalesResetPanel({ preview }: Props) {
  const initialQuestionId = preview.security.configuredQuestionId ?? preview.securityQuestions[0]?.id ?? "";
  const [questionId, setQuestionId] = useState<string>(initialQuestionId);
  const [securityAnswer, setSecurityAnswer] = useState("");
  const [adminPin, setAdminPin] = useState("");
  const [operatorNote, setOperatorNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [result, setResult] = useState<ResetResult | null>(null);
  const [configured, setConfigured] = useState(preview.security.configured);
  const [configuredAt, setConfiguredAt] = useState<string | null>(null);
  const canSubmit = configured && questionId && securityAnswer.trim().length >= 2 && /^\d{6}$/.test(adminPin) && !busy;
  const canConfigure = !configured && questionId && securityAnswer.trim().length >= 2 && /^\d{6}$/.test(adminPin) && !busy;
  const activeCounts = useMemo(() => countEntries(preview.counts), [preview.counts]);

  async function configureSecurity(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canConfigure) return;
    setBusy(true);
    setMessage(null);
    setResult(null);
    try {
      const response = await requestJson<{ result: ConfigureResult }>("/api/pos/admin/sales-reset", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          action: "configure_security",
          businessId: preview.businessId,
          questionId,
          securityAnswer,
          adminPin,
          operatorNote
        })
      });
      setConfigured(true);
      setConfiguredAt(response.data.result.configuredAt);
      setSecurityAnswer("");
      setAdminPin("");
      setMessage("Seguridad local configurada. El reset ya requiere pregunta de seguridad y PIN admin.");
    } catch (error) {
      const errorMessage = error && typeof error === "object" && "message" in error
        ? String((error as { message?: string }).message)
        : "No fue posible configurar la seguridad local.";
      setMessage(errorMessage);
    } finally {
      setBusy(false);
    }
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit) return;
    setBusy(true);
    setMessage(null);
    setResult(null);
    try {
      const response = await requestJson<{ result: ResetResult }>("/api/pos/admin/sales-reset", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          businessId: preview.businessId,
          questionId,
          securityAnswer,
          adminPin,
          operatorNote
        })
      });
      setResult(response.data.result);
      setMessage("Reset seguro ejecutado. Licencia, catálogo, inventario, usuarios, roles y configuración se conservaron. Se dejó alerta silenciosa en cola de soporte.");
      setSecurityAnswer("");
      setAdminPin("");
    } catch (error) {
      const errorMessage = error && typeof error === "object" && "message" in error
        ? String((error as { message?: string }).message)
        : "No fue posible ejecutar el reset seguro.";
      setMessage(errorMessage);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className={styles.card}>
      <p className={styles.eyebrow}>Herramienta bloqueada</p>
      <h2 className={styles.title}>Reset seguro de ventas locales</h2>
      <p className={styles.copy}>
        Borra únicamente ventas, caja y outbox de ventas de esta Tablet. No toca licencia, catálogo, inventario, usuarios ni configuración de runtime.
      </p>

      <div className={styles.metricGrid}>
        <Metric label="Negocio" value={preview.businessId} />
        <Metric label="Alcance" value="ventas + caja + outbox de ventas" />
        <Metric label="Seguridad" value={configured ? "pregunta + PIN admin" : "configuración inicial requerida"} />
        <Metric label="Vista previa" value={preview.generatedAt} />
      </div>

      <div className={styles.warningList}>
        {activeCounts.length ? activeCounts.map(([key, value]) => (
          <div key={key} className={styles.warning}>
            <strong>{key}</strong>: {value}
          </div>
        )) : (
          <div className={styles.warning}>No hay ventas/caja locales que borrar en este momento.</div>
        )}
      </div>

      <div className={styles.warningList}>
        {preview.preserves.map((item) => (
          <div key={item} className={styles.metric}>
            <span className={styles.metricLabel}>Se conserva</span>
            <span className={styles.metricValue}>{item}</span>
          </div>
        ))}
      </div>

      {!configured ? (
        <form className={styles.refreshForm} onSubmit={configureSecurity}>
          <label className={styles.metricLabel} htmlFor="sales-reset-question-setup">Pregunta de seguridad</label>
          <select
            id="sales-reset-question-setup"
            value={questionId}
            onChange={(event: ChangeEvent<HTMLSelectElement>) => setQuestionId(event.target.value)}
            style={{ width: "100%", minHeight: 46, margin: "8px 0 12px", padding: "0 12px" }}
          >
            {preview.securityQuestions.map((question) => (
              <option key={question.id} value={question.id}>{question.label}</option>
            ))}
          </select>
          <label className={styles.metricLabel} htmlFor="sales-reset-answer-setup">Respuesta de una palabra</label>
          <input
            id="sales-reset-answer-setup"
            value={securityAnswer}
            onChange={(event: ChangeEvent<HTMLInputElement>) => setSecurityAnswer(event.target.value)}
            placeholder="Una palabra privada"
            autoComplete="off"
            style={{ width: "100%", minHeight: 46, margin: "8px 0 12px", padding: "0 12px" }}
          />
          <label className={styles.metricLabel} htmlFor="sales-reset-pin-setup">PIN admin de 6 dígitos</label>
          <input
            id="sales-reset-pin-setup"
            value={adminPin}
            onChange={(event: ChangeEvent<HTMLInputElement>) => setAdminPin(event.target.value.replace(/\D/g, "").slice(0, 6))}
            inputMode="numeric"
            type="password"
            autoComplete="new-password"
            placeholder="000000"
            style={{ width: "100%", minHeight: 46, margin: "8px 0 12px", padding: "0 12px" }}
          />
          <label className={styles.metricLabel} htmlFor="sales-reset-note-setup">Nota operativa</label>
          <textarea
            id="sales-reset-note-setup"
            value={operatorNote}
            onChange={(event: ChangeEvent<HTMLTextAreaElement>) => setOperatorNote(event.target.value)}
            placeholder="Quién configuró esta protección y por qué"
            rows={3}
            style={{ width: "100%", margin: "8px 0 12px", padding: 12 }}
          />
          <button className={styles.primaryButton} type="submit" disabled={!canConfigure} aria-disabled={!canConfigure}>
            {busy ? "Configurando..." : "Configurar seguridad local"}
          </button>
          <p className={styles.helper}>El PIN y la respuesta se guardan como hash local; no se escribe la respuesta ni el PIN en auditoría.</p>
        </form>
      ) : (
      <form className={styles.refreshForm} onSubmit={submit}>
        <label className={styles.metricLabel} htmlFor="sales-reset-question">Pregunta de seguridad</label>
        <select
          id="sales-reset-question"
          value={questionId}
          onChange={(event: ChangeEvent<HTMLSelectElement>) => setQuestionId(event.target.value)}
          style={{ width: "100%", minHeight: 46, margin: "8px 0 12px", padding: "0 12px" }}
        >
          {preview.securityQuestions.map((question) => (
            <option key={question.id} value={question.id}>{question.label}</option>
          ))}
        </select>
        <label className={styles.metricLabel} htmlFor="sales-reset-answer">Respuesta de una palabra</label>
        <input
          id="sales-reset-answer"
          value={securityAnswer}
          onChange={(event: ChangeEvent<HTMLInputElement>) => setSecurityAnswer(event.target.value)}
          placeholder="Respuesta privada"
          autoComplete="off"
          style={{ width: "100%", minHeight: 46, margin: "8px 0 12px", padding: "0 12px" }}
        />
        <label className={styles.metricLabel} htmlFor="sales-reset-pin">PIN admin</label>
        <input
          id="sales-reset-pin"
          value={adminPin}
          onChange={(event: ChangeEvent<HTMLInputElement>) => setAdminPin(event.target.value.replace(/\D/g, "").slice(0, 6))}
          inputMode="numeric"
          type="password"
          autoComplete="current-password"
          placeholder="6 dígitos"
          style={{ width: "100%", minHeight: 46, margin: "8px 0 12px", padding: "0 12px" }}
        />
        <label className={styles.metricLabel} htmlFor="sales-reset-note">Nota operativa</label>
        <textarea
          id="sales-reset-note"
          value={operatorNote}
          onChange={(event: ChangeEvent<HTMLTextAreaElement>) => setOperatorNote(event.target.value)}
          placeholder="Motivo del reset para auditoría local"
          rows={3}
          style={{ width: "100%", margin: "8px 0 12px", padding: 12 }}
        />
        <button className={styles.primaryButton} type="submit" disabled={!canSubmit} aria-disabled={!canSubmit}>
          {busy ? "Ejecutando..." : "Ejecutar reset seguro"}
        </button>
        <p className={styles.helper}>
          El botón queda bloqueado hasta validar pregunta de seguridad y PIN admin. Esta acción genera auditoría local y alerta silenciosa para soporte.
        </p>
      </form>
      )}

      {message ? <div className={styles.warning}>{message}</div> : null}
      {configuredAt ? <div className={styles.warning}>Configuración aplicada: {configuredAt}</div> : null}
      {result ? (
        <details className={styles.metric}>
          <summary>Resumen auditado del reset</summary>
          <pre>{JSON.stringify({ resetId: result.resetId, before: result.before, after: result.after }, null, 2)}</pre>
        </details>
      ) : null}
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.metric}>
      <span className={styles.metricLabel}>{label}</span>
      <span className={styles.metricValue}>{value}</span>
    </div>
  );
}
