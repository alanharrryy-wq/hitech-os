import type { ReactNode } from "react";
import type { PrismaPanelContract } from "./types";

export function DecisionPanel({
  contract,
  title,
  children,
  className = "",
}: {
  contract: PrismaPanelContract;
  title?: string;
  children: ReactNode;
  className?: string;
}) {
  const evidence =
    typeof contract.evidence === "string"
      ? contract.evidence
      : contract.evidence?.source || contract.evidence?.query || "";

  return (
    <section
      className={`prisma-decision-panel ${className}`}
      data-prisma-panel={contract.id}
      data-prisma-panel-role={contract.role}
      data-prisma-priority={contract.priority || "normal"}
      data-prisma-action={contract.action || ""}
      data-prisma-evidence={evidence}
      data-prisma-visual-budget={contract.visualBudget || ""}
    >
      {title && <h2>{title}</h2>}
      {children}
    </section>
  );
}

export function AttentionSummary({
  items,
}: {
  items: Array<{ label: string; detail?: string; priority?: "low" | "normal" | "high" | "critical" }>;
}) {
  return (
    <div className="prisma-attention-summary" data-prisma-panel-role="attention-summary">
      {items.slice(0, 5).map((item, index) => (
        <article key={`${item.label}-${index}`} data-prisma-priority={item.priority || "normal"}>
          <strong>{item.label}</strong>
          {item.detail && <p>{item.detail}</p>}
        </article>
      ))}
    </div>
  );
}

export function NextBestAction({
  title,
  reason,
  children,
}: {
  title: string;
  reason: string;
  children?: ReactNode;
}) {
  return (
    <aside className="prisma-next-best-action" data-prisma-panel-role="next-best-action">
      <p className="prisma-eyebrow">Acción recomendada</p>
      <h2>{title}</h2>
      <p>{reason}</p>
      {children && <div className="prisma-decision-actions">{children}</div>}
    </aside>
  );
}
