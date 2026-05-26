import type { ReactNode } from "react";

export function HumanEmptyState({
  title,
  explanation,
  action,
}: {
  title: string;
  explanation: string;
  action?: ReactNode;
}) {
  return (
    <div className="prisma-empty-state" data-prisma-state="empty">
      <h3>{title}</h3>
      <p>{explanation}</p>
      {action}
    </div>
  );
}

export function HumanErrorState({
  title,
  explanation,
  action,
  technicalDetail,
}: {
  title: string;
  explanation: string;
  action?: ReactNode;
  technicalDetail?: ReactNode;
}) {
  return (
    <div className="prisma-error-state" data-prisma-state="error">
      <h3>{title}</h3>
      <p>{explanation}</p>
      {action}
      {technicalDetail && (
        <details>
          <summary>Ver detalle técnico</summary>
          <div>{technicalDetail}</div>
        </details>
      )}
    </div>
  );
}
