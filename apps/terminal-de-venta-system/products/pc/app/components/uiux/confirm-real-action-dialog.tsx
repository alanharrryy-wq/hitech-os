"use client";

import { useState } from "react";

export function ConfirmRealActionDialog({
  title,
  explanation,
  consequence,
  confirmLabel = "Confirmar acción",
  cancelHref = "#",
  onConfirm
}: {
  title: string;
  explanation: string;
  consequence: string;
  confirmLabel?: string;
  cancelHref?: string;
  onConfirm?: () => void;
}) {
  const [acknowledged, setAcknowledged] = useState(false);

  return (
    <section className="card" data-prisma-component="ConfirmRealActionDialog" role="group" aria-label={title}>
      <div className="kicker">confirmación requerida</div>
      <h2 className="section-title">{title}</h2>
      <p className="section-copy">{explanation}</p>
      <p className="section-copy"><strong>Esto puede cambiar:</strong> {consequence}</p>
      <label className="list-item" style={{ cursor: "pointer" }}>
        <input type="checkbox" checked={acknowledged} onChange={(event) => setAcknowledged(event.currentTarget.checked)} />
        <span style={{ marginLeft: 8 }}>Entiendo la consecuencia y quiero continuar.</span>
      </label>
      <div className="inline-list" style={{ marginTop: 12 }}>
        <button className="btn btn-primary" type="button" disabled={!acknowledged} onClick={onConfirm}>
          {confirmLabel}
        </button>
        <a className="btn btn-secondary" href={cancelHref}>Cancelar</a>
      </div>
    </section>
  );
}
