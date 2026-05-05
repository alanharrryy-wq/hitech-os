"use client";

import { useMemo } from "react";
import type { PrismaMobileClientSnapshot } from "@/lib/prisma-app/prisma-mobile-snapshot-contract";
import { buildPrismaMobileDecisionLedger } from "@/lib/prisma-app/prisma-mobile-decision-ledger";
import styles from "./prisma-mobile-dashboard.module.css";

type Props = {
  clientSnapshot: PrismaMobileClientSnapshot;
};

export function PrismaMobileDecisionLedger({ clientSnapshot }: Props) {
  const ledger = useMemo(() => buildPrismaMobileDecisionLedger(clientSnapshot), [clientSnapshot]);
  return (
    <section className={styles.decisionLedger} aria-label="Bitácora móvil de decisiones">
      <header className={styles.decisionLedgerHeader}>
        <div>
          <p className={styles.eyebrow}>PRISMA App · Bitácora del dueño</p>
          <h2>{ledger.headline}</h2>
          <p>{ledger.subheadline}</p>
        </div>
        <aside className={styles.decisionLedgerScore}>
          <span>Confianza</span>
          <strong>{ledger.trustLabel}</strong>
          <small>{ledger.generatedLabel}</small>
        </aside>
      </header>

      <div className={styles.decisionLedgerDigest}>
        <span>Resumen accionable</span>
        <strong>Lo que conviene dejar registrado</strong>
        <ul>{ledger.ownerDigest.map((line) => <li key={line}>{line}</li>)}</ul>
      </div>

      <div className={styles.decisionLedgerCardGrid} aria-label="Pruebas operativas de la bitácora">
        {ledger.proofCards.map((card) => (
          <article key={card.label}>
            <span>{card.label}</span>
            <strong>{card.value}</strong>
            <small>{card.detail}</small>
          </article>
        ))}
      </div>

      <div className={styles.decisionLedgerTimeline} aria-label="Línea de decisiones priorizadas">
        {ledger.entries.map((entry) => (
          <article key={entry.id} data-tone={entry.tone}>
            <div>
              <span>{entry.sequence.toString().padStart(2, "0")} · {entry.sourceLabel}</span>
              <h3>{entry.title}</h3>
              <p>{entry.summary}</p>
              <ul>{entry.evidence.map((item) => <li key={item}>{item}</li>)}</ul>
            </div>
            <div className={styles.decisionLedgerMeta}>
              <em>{entry.owner}</em>
              <strong>{entry.dueLabel}</strong>
              <small>{entry.nextStep}</small>
            </div>
          </article>
        ))}
      </div>

      <details className={styles.decisionLedgerExport}>
        <summary>Ver texto auditable para cierre o seguimiento</summary>
        <pre>{ledger.exportText}</pre>
      </details>
    </section>
  );
}
