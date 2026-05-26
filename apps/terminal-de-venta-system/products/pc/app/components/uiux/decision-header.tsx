import { getPrimaryRouteActions } from "@/uiux/decision-model";
import { HumanStatusBadge } from "./human-status-badge";

function headerActionKey(label: string, href: string, index: number) {
  return ["header-action", index, label, href].join("-");
}

export function DecisionHeader({
  title,
  subtitle,
  status,
  lastUpdated,
  currentPath = "/dashboard",
  actions
}: {
  title: string;
  subtitle: string;
  status: string;
  lastUpdated: string;
  currentPath?: string;
  actions?: Array<{ label: string; href: string; primary?: boolean }>;
}) {
  const resolvedActions = actions ?? getPrimaryRouteActions(currentPath);

  return (
    <section className="hero" data-prisma-component="DecisionHeader" data-route-intent="human-decision">
      <div className="hero-header">
        <div className="hero-copy">
          <div className="kicker">centro de decisiones</div>
          <h1 className="hero-title">{title}</h1>
          <p>{subtitle}</p>
        </div>
        <div className="inline-list" aria-label="Estado y acciones principales">
          <HumanStatusBadge status={status} label="Estado general" />
          <span className="chip">Actualizado: {lastUpdated}</span>
          {resolvedActions.slice(0, 2).map((action, index) => (
            <a key={headerActionKey(action.label, action.href, index)} className={action.primary ? "btn btn-primary" : "btn btn-secondary"} href={action.href}>
              {action.label}
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
