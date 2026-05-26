import type { RecommendedAction } from "./decision-types";

function actionKey(label: string, href: string, index: number) {
  return ["next-action", index, label, href].join("-");
}

function ActionLink({ label, href, primary }: { label: string; href: string; primary?: boolean }) {
  return (
    <a className={primary ? "btn btn-primary" : "btn btn-secondary"} href={href}>
      {label}
    </a>
  );
}

export function NextBestAction({ action }: { action: RecommendedAction }) {
  return (
    <section className="card" data-prisma-component="NextBestAction">
      <div className="section-head">
        <div>
          <div className="kicker">acción recomendada</div>
          <h2 className="section-title">{action.title}</h2>
          <div className="section-copy">Motivo: {action.motive}</div>
        </div>
      </div>
      <div className="inline-list">
        {action.actions.map((item, index) => (
          <ActionLink key={actionKey(item.label, item.href, index)} {...item} />
        ))}
      </div>
    </section>
  );
}
