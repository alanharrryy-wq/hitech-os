import type { ReactNode } from "react";
import type { PrismaEvidenceRef } from "./types";

export function EvidenceDrawer({
  title = "Ver evidencia técnica",
  evidence,
  children,
  defaultOpen = false,
}: {
  title?: string;
  evidence?: PrismaEvidenceRef;
  children?: ReactNode;
  defaultOpen?: boolean;
}) {
  return (
    <details className="prisma-evidence-drawer" data-prisma-panel-role="evidence" open={defaultOpen}>
      <summary>{title}</summary>
      <div className="prisma-evidence-body">
        {evidence && (
          <dl>
            {evidence.source && (
              <>
                <dt>Fuente</dt>
                <dd>{evidence.source}</dd>
              </>
            )}
            {evidence.query && (
              <>
                <dt>Consulta</dt>
                <dd>{evidence.query}</dd>
              </>
            )}
            {evidence.confidence && (
              <>
                <dt>Confianza</dt>
                <dd>{evidence.confidence}</dd>
              </>
            )}
            {evidence.freshness && (
              <>
                <dt>Actualización</dt>
                <dd>{evidence.freshness}</dd>
              </>
            )}
          </dl>
        )}
        {children}
      </div>
    </details>
  );
}
