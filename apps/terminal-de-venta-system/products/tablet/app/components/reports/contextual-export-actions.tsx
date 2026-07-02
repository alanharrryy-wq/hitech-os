"use client";

import { useMemo, useState } from "react";
import type {
  ExportAction,
  ExportHistoryEntry,
  ExportSurface
} from "@/lib/contextual-export-reports/contextual-export-contract";
import {
  buildExportActions,
  rememberExport,
  surfaceCopy
} from "@/lib/contextual-export-reports/contextual-export-view-model";
import styles from "./contextual-export.module.css";

type ContextualExportActionsProps = {
  surface: ExportSurface;
};

function exportAriaLabel(action: ExportAction) {
  return `${action.label}. ${action.description}`;
}

export function ContextualExportActions({ surface }: ContextualExportActionsProps) {
  const actions = useMemo(() => buildExportActions(surface), [surface]);
  const [history, setHistory] = useState<ExportHistoryEntry[]>([]);

  function track(action: ExportAction) {
    setHistory((current) =>
      rememberExport(current, {
        id: action.id,
        label: action.label,
        href: action.href,
        format: action.format,
        surface,
        createdAt: new Date().toISOString()
      })
    );
  }

  return (
    <details className={styles.card} aria-labelledby={`contextual-export-${surface}`}>
      <summary className={styles.summary}>
        <span>Exportar</span>
        <strong id={`contextual-export-${surface}`}>Descargar reporte</strong>
        <small>{surfaceCopy(surface)}</small>
      </summary>

      <div className={styles.actions}>
        {actions.map((action) => (
          <a
            key={action.id}
            href={action.href}
            aria-label={exportAriaLabel(action)}
            onClick={() => track(action)}
            className={action.risk === "warn" ? styles.warn : undefined}
          >
            {action.label}
            <small>{action.description}</small>
          </a>
        ))}
      </div>

      {history.length > 0 ? (
        <ul className={styles.history} aria-label="Exportaciones preparadas en esta vista">
          {history.map((item) => (
            <li key={item.id}>
              {item.label} preparado <small>{item.format.toUpperCase()}</small>
            </li>
          ))}
        </ul>
      ) : null}
    </details>
  );
}
