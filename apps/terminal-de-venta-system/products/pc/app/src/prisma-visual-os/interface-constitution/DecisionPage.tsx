import type { ReactNode } from "react";
import type { PrismaInterfaceContract } from "./types";

export function DecisionPage({
  contract,
  children,
  className = "",
}: {
  contract: PrismaInterfaceContract;
  children: ReactNode;
  className?: string;
}) {
  return (
    <main
      className={`prisma-decision-page ${className}`}
      data-prisma-interface={contract.id}
      data-prisma-route={contract.route}
      data-prisma-surface={contract.surface}
      data-prisma-visual-budget={contract.visualBudget}
    >
      {children}
    </main>
  );
}

export function DecisionHeader({
  title,
  subtitle,
  status,
  lastPulse,
  actions,
}: {
  title: string;
  subtitle: string;
  status?: string;
  lastPulse?: string;
  actions?: ReactNode;
}) {
  return (
    <header className="prisma-decision-header" data-prisma-panel-role="decision-header">
      <div>
        <p className="prisma-eyebrow">PRISMA PC</p>
        <h1>{title}</h1>
        <p>{subtitle}</p>
        {(status || lastPulse) && (
          <div className="prisma-status-line">
            {status && <span>{status}</span>}
            {lastPulse && <span>Última actualización: {lastPulse}</span>}
          </div>
        )}
      </div>
      {actions && <div className="prisma-decision-actions">{actions}</div>}
    </header>
  );
}
