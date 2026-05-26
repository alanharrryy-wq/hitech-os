import type { ReactNode } from "react";

export function ActionableTableShell({
  title,
  description,
  actions,
  children,
  empty,
  error,
}: {
  title: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
  empty?: ReactNode;
  error?: ReactNode;
}) {
  return (
    <section className="prisma-actionable-table" data-prisma-panel-role="table">
      <header>
        <div>
          <h2>{title}</h2>
          {description && <p>{description}</p>}
        </div>
        {actions && <div className="prisma-decision-actions">{actions}</div>}
      </header>
      {error ? (
        <div className="prisma-error-state">{error}</div>
      ) : children ? (
        <div className="prisma-table-scroll">{children}</div>
      ) : (
        <div className="prisma-empty-state">{empty || "No hay datos por mostrar."}</div>
      )}
    </section>
  );
}
