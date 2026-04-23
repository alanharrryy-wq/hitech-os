import { AppShell } from "@components/layout/app-shell";
import { Badge } from "@components/ui/badge";
import { TableSimple } from "@components/ui/table-simple";
import { getPcDashboard } from "@/lib/services/dashboard";
import { formatNumber } from "@/lib/utils";
import { pcMessages } from "@/lib/i18n/messages/es";

const toneByStatus: Record<string, "ok" | "warn" | "danger"> = {
  [pcMessages.statuses.critical]: "danger",
  [pcMessages.statuses.failed]: "danger",
  [pcMessages.statuses.risk]: "warn",
  [pcMessages.statuses.pending]: "warn",
  [pcMessages.statuses.sent]: "ok",
  [pcMessages.statuses.ordered]: "ok",
  [pcMessages.statuses.partial]: "warn"
};

export default function HomePage() {
  const dashboard = getPcDashboard();

  return (
    <AppShell currentPath="/">
      <section className="hero">
        <div className="hero-header">
          <div className="hero-copy">
            <div className="kicker">{pcMessages.home.kicker}</div>
            <h1 className="hero-title">{dashboard.hero.title}</h1>
            <p>{dashboard.hero.subtitle}</p>
          </div>
          <div className="inline-list">
            <span className="chip">Twin PC 6.1.1</span>
            <span className="chip">Modo ejecutivo</span>
            <span className="chip">es-MX</span>
          </div>
        </div>

        <div className="hero-badges">
          {dashboard.hero.pills.map((pill) => (
            <span key={pill} className="alert-chip">
              {pill}
            </span>
          ))}
        </div>
      </section>

      <section className="dashboard-grid">
        {dashboard.summaryCards.map((card) => (
          <article key={card.label} className="card metric-card">
            <div className="card-title-row">
              <div>
                <div className="kicker">Resumen</div>
                <div className="card-title">{card.label}</div>
              </div>
              <span className="card-icon" aria-hidden="true">
                {card.icon}
              </span>
            </div>
            <div className="metric">{card.value}</div>
            <div className="metric-note">{card.note}</div>
            <div className="metric-details">
              {card.details.map((detail) => (
                <div key={detail.label} className="metric-detail">
                  <span className="subtle">{detail.label}</span>
                  <strong>{detail.value}</strong>
                </div>
              ))}
            </div>
          </article>
        ))}

        <article className="card grid-span-8">
          <div className="section-head">
            <div>
              <div className="kicker">Prioridad comercial</div>
              <h2 className="section-title">{pcMessages.home.openOrdersTitle}</h2>
              <div className="section-copy">{pcMessages.home.openOrdersSubtitle}</div>
            </div>
            <div className="table-tags">
              <span className="inline-chip">Top 4 del turno</span>
              <span className="inline-chip">Margen visible</span>
            </div>
          </div>
          <TableSimple
            columns={pcMessages.home.openOrdersColumns}
            rows={dashboard.openOrders.map((row) => ({
              SKU: row.po,
              Producto: row.supplier,
              Unidades: row.lines,
              Ingreso: row.eta,
              Margen: row.status
            }))}
          />
        </article>

        <article className="card grid-span-4">
          <div className="section-head">
            <div>
              <div className="kicker">Acción rápida</div>
              <h2 className="section-title">{pcMessages.home.categoryMixTitle}</h2>
              <div className="section-copy">{pcMessages.home.categoryMixSubtitle}</div>
            </div>
          </div>

          <div className="dashboard-actions">
            {dashboard.actionCards.map((item) => (
              <div key={item.title} className="action-card">
                <span className="card-icon" aria-hidden="true">
                  ✧
                </span>
                <strong>{item.title}</strong>
                <span>{item.description}</span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <div className="alert-strip">
        <strong>{dashboard.alertStrip.title}</strong>
        <span className="subtle">{dashboard.alertStrip.subtitle}</span>
      </div>

      <section className="grid cols-2">
        <article className="card">
          <div className="section-head">
            <div>
              <div className="kicker">Cobertura</div>
              <h2 className="section-title">{pcMessages.home.criticalStockTitle}</h2>
              <div className="section-copy">{pcMessages.home.criticalStockSubtitle}</div>
            </div>
            <div className="inline-list">
              <span className="inline-chip">{dashboard.lowStock.length} SKUs críticos</span>
            </div>
          </div>
          <div className="list">
            {dashboard.lowStock.map((row) => (
              <div key={row.sku} className="list-item">
                <div>
                  <div style={{ fontWeight: 600 }}>{row.name}</div>
                  <div className="subtle">
                    {row.sku} • {row.location} • {formatNumber(Number(row.days))} días
                  </div>
                </div>
                <Badge tone={toneByStatus[row.status] ?? "warn"}>{row.status}</Badge>
              </div>
            ))}
          </div>
        </article>

        <article className="card">
          <div className="section-head">
            <div>
              <div className="kicker">Latido del sistema</div>
              <h2 className="section-title">{pcMessages.home.pendingSyncTitle}</h2>
              <div className="section-copy">{pcMessages.home.pendingSyncSubtitle}</div>
            </div>
            <div className="inline-list">
              <span className="inline-chip">Outbox visible</span>
              <span className="inline-chip">Latencia al día</span>
            </div>
          </div>
          <TableSimple
            columns={pcMessages.home.pendingSyncColumns}
            rows={dashboard.pendingSync.map((row) => ({
              Evento: row.id,
              Tipo: row.topic,
              Antigüedad: row.age,
              Estado: row.status
            }))}
          />
        </article>
      </section>
    </AppShell>
  );
}
