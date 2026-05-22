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

type Props = {
  preview: SalesResetPreview;
};

function countEntries(counts: Record<string, number>) {
  return Object.entries(counts).filter(([, value]) => Number(value) > 0);
}

export function SalesResetPanel({ preview }: Props) {
  const [confirmation, setConfirmation] = useState("");
  const [operatorNote, setOperatorNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [result, setResult] = useState<ResetResult | null>(null);
  const canSubmit = confirmation === preview.confirmationPhrase && !busy;
  const activeCounts = useMemo(() => countEntries(preview.counts), [preview.counts]);

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
          confirmation,
          operatorNote
        })
      });
      setResult(response.data.result);
      setMessage("Reset seguro ejecutado. Licencia, catálogo, inventario y configuración se conservaron.");
      setConfirmation("");
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
        <Metric label="Confirmación" value={preview.confirmationPhrase} />
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

      <form className={styles.refreshForm} onSubmit={submit}>
        <label className={styles.metricLabel} htmlFor="sales-reset-confirmation">Frase exacta</label>
        <input
          id="sales-reset-confirmation"
          value={confirmation}
          onChange={(event: ChangeEvent<HTMLInputElement>) => setConfirmation(event.target.value)}
          placeholder={preview.confirmationPhrase}
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
        <p className={styles.helper}>El botón queda bloqueado hasta escribir la frase exacta. Esta acción genera un evento de auditoría local.</p>
      </form>

      {message ? <div className={styles.warning}>{message}</div> : null}
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
