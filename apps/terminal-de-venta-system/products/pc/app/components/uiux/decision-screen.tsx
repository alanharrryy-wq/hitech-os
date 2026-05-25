import type { ReactNode } from "react";
import { AppShell } from "@components/layout/app-shell";
import { DataTable } from "@components/backoffice/data-table";

type SummaryTone = "danger" | "warn" | "ok" | "info";

type SummaryCard = {
  title: string;
  eyebrow: string;
  tone: SummaryTone;
  lines: string[];
};

type RecommendedAction = {
  title: string;
  motive: string;
  actions: Array<{ label: string; href: string; primary?: boolean }>;
};

type EvidenceItem = {
  label: string;
  value: string;
};

type ChartInsight = {
  title: string;
  question: string;
  reading: string;
  action: string;
  bars: Array<{ label: string; value: string; level: "Alto" | "Medio" | "Bajo" }>;
};

const TONE_ICON: Record<SummaryTone, string> = {
  danger: "●",
  warn: "●",
  ok: "●",
  info: "●"
};

function ActionLink({ label, href, primary }: { label: string; href: string; primary?: boolean }) {
  return (
    <a className={primary ? "btn btn-primary" : "btn btn-secondary"} href={href}>
      {label}
    </a>
  );
}

function EvidenceDrawer({ items }: { items: EvidenceItem[] }) {
  return (
    <details className="card" data-prisma-component="EvidenceDrawer">
      <summary className="section-title">Ver evidencia técnica</summary>
      <div className="list" style={{ marginTop: 12 }}>
        {items.map((item) => (
          <div className="list-item" key={item.label}>
            <strong>{item.label}:</strong> {item.value}
          </div>
        ))}
      </div>
    </details>
  );
}

function InsightBars({ insight }: { insight: ChartInsight }) {
  return (
    <section className="card" data-prisma-component="ChartInsightCard">
      <div className="section-head">
        <div>
          <div className="kicker">{insight.title}</div>
          <h2 className="section-title">{insight.question}</h2>
          <div className="section-copy">{insight.reading}</div>
          <div className="section-copy">Acción sugerida: {insight.action}</div>
        </div>
      </div>
      <div className="list">
        {insight.bars.map((bar) => (
          <div className="list-item" key={bar.label}>
            <strong>{bar.label}</strong>
            <span style={{ display: "inline-block", minWidth: 180, marginLeft: 12 }}>{bar.value}</span>
            <span>{bar.level}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

export function DecisionScreen({
  currentPath,
  title,
  subtitle,
  status,
  lastUpdated,
  summaryCards,
  recommendedAction,
  tableTitle,
  tableSubtitle,
  columns,
  rows,
  evidence,
  children,
  insight
}: {
  currentPath: string;
  title: string;
  subtitle: string;
  status: string;
  lastUpdated: string;
  summaryCards: SummaryCard[];
  recommendedAction: RecommendedAction;
  tableTitle: string;
  tableSubtitle: string;
  columns: string[];
  rows: Array<Record<string, string | number>>;
  evidence: EvidenceItem[];
  children?: ReactNode;
  insight?: ChartInsight;
}) {
  return (
    <AppShell currentPath={currentPath}>
      <section className="hero" data-prisma-component="DecisionHeader">
        <div className="hero-header">
          <div className="hero-copy">
            <div className="kicker">centro de decisiones</div>
            <h1 className="hero-title">{title}</h1>
            <p>{subtitle}</p>
          </div>
          <div className="inline-list">
            <span className="chip">Estado general: {status}</span>
            <span className="chip">Actualizado: {lastUpdated}</span>
          </div>
        </div>
      </section>

      <section className="dashboard-grid" data-prisma-component="AttentionSummary">
        {summaryCards.map((card) => (
          <article className="card metric-card" key={card.title}>
            <div className="kicker">
              <span aria-hidden="true">{TONE_ICON[card.tone]} </span>
              {card.eyebrow}
            </div>
            <div className="card-title">{card.title}</div>
            <div className="list" style={{ marginTop: 12 }}>
              {card.lines.map((line) => (
                <div className="list-item" key={line}>{line}</div>
              ))}
            </div>
          </article>
        ))}
      </section>

      <section className="card" data-prisma-component="NextBestAction">
        <div className="section-head">
          <div>
            <div className="kicker">acción recomendada</div>
            <h2 className="section-title">{recommendedAction.title}</h2>
            <div className="section-copy">Motivo: {recommendedAction.motive}</div>
          </div>
        </div>
        <div className="inline-list">
          {recommendedAction.actions.map((action) => (
            <ActionLink key={action.label} {...action} />
          ))}
        </div>
      </section>

      {children}

      <section className="card" data-prisma-component="ActionableTable">
        <div className="section-head">
          <div>
            <div className="kicker">detalle operativo</div>
            <h2 className="section-title">{tableTitle}</h2>
            <div className="section-copy">{tableSubtitle}</div>
          </div>
        </div>
        <DataTable columns={columns} rows={rows} emptyMessage="No hay pendientes para esta vista." />
      </section>

      {insight ? <InsightBars insight={insight} /> : null}

      <EvidenceDrawer items={evidence} />
    </AppShell>
  );
}
