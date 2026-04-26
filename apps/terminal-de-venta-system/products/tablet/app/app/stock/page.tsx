import { AppShell } from "@components/layout/app-shell";
import { SectionCard } from "@components/ui/section-card";
import { StatCard } from "@components/ui/stat-card";
import { StatusBadge } from "@components/ui/status-badge";
import { TableSimple } from "@components/ui/table-simple";
import { getStockConsole } from "@/lib/services/stock";
import { formatInt, formatMoney } from "@/lib/utils";
import { tabletMessages } from "@/lib/i18n/messages/es";

export const dynamic = "force-dynamic";

export default async function Page() {
  const page = tabletMessages.pages.stock;
  const stock = await getStockConsole();

  return (
    <AppShell currentPath="/stock">
      <section className="hero hero-split">
        <div>
          <div className="kicker">{page.kicker}</div>
          <h1 style={{ margin: 0 }}>{page.title}</h1>
          <div className="subtle">{page.subtitle}</div>
        </div>
        <div className="hero-side">
          <div className="mini-stat">
            <span className="mini-stat-label">quiebre caliente</span>
            <strong>{stock.hotSpot.sku}</strong>
            <span className="subtle">{stock.hotSpot.name} · {stock.hotSpot.hoursLeft} h de cobertura</span>
          </div>
          <div className="mini-stat">
            <span className="mini-stat-label">reabasto sugerido</span>
            <strong>{formatInt(stock.hotSpot.suggestedUnits)} uds</strong>
            <span className="subtle">{stock.hotSpot.suggestedSource}</span>
          </div>
        </div>
      </section>

      <div className="grid cols-4">
        <StatCard label="SKUs monitoreados" value={formatInt(stock.kpis.monitoredSkus)} note="señal operativa del turno" />
        <StatCard label="quiebres activos" value={formatInt(stock.kpis.stockouts)} note="venta en riesgo o ya frenada" />
        <StatCard label="cobertura baja" value={formatInt(stock.kpis.lowCoverage)} note="menos de 6 horas de colchón" />
        <StatCard label="barcode con bronca" value={formatInt(stock.kpis.barcodeIssues)} note="captura manual o duplicidad" />
      </div>

      <div className="grid cols-2">
        <SectionCard title="Quiebres y presión de venta" subtitle="Lo que ya pide atención antes de que caja termine vendiendo humo.">
          <TableSimple
            columns={["SKU", "Producto", "Stock", "Venta/h", "Señal"]}
            rows={stock.watchlist.map((item) => ({
              SKU: item.sku,
              Producto: item.name,
              Stock: `${formatInt(item.onHand)} uds`,
              "Venta/h": item.velocity,
              Señal: <StatusBadge tone={item.tone}>{item.signal}</StatusBadge>
            }))}
          />
        </SectionCard>

        <SectionCard title="Reabasto express" subtitle="Sugerencias cortas para no mandar al operador a una búsqueda arqueológica.">
          <TableSimple
            columns={["SKU", "Reposición", "Cobertura", "Origen"]}
            rows={stock.replenishment.map((item) => ({
              SKU: item.sku,
              Reposición: `${formatInt(item.recommendedUnits)} uds`,
              Cobertura: item.coverage,
              Origen: item.source
            }))}
          />
        </SectionCard>
      </div>

      <div className="grid cols-2">
        <SectionCard title="Barcodes y precio" subtitle="Huecos típicos que revientan en caja justo cuando la fila ya parece procesión.">
          <div className="stack-list">
            {stock.barcodeAlerts.map((alert) => (
              <div key={alert.title} className="stack-item">
                <div className="stack-item-head">
                  <strong>{alert.title}</strong>
                  <StatusBadge tone={alert.tone}>{alert.level}</StatusBadge>
                </div>
                <div className="subtle">{alert.description}</div>
                <div className="code">{alert.action}</div>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Pulso por pasillo" subtitle="Vista ligera para venta y supervisor sin convertir tablet en backoffice con esteroides.">
          <div className="stack-list compact">
            {stock.aislePulse.map((aisle) => (
              <div key={aisle.name} className="queue-card">
                <div className="stack-item-head">
                  <div>
                    <strong>{aisle.name}</strong>
                    <div className="subtle">{aisle.note}</div>
                  </div>
                  <StatusBadge tone={aisle.tone}>{aisle.signal}</StatusBadge>
                </div>
                <div className="latency-bar">
                  <div className="latency-fill" style={{ width: `${aisle.pressure}%` }} />
                </div>
                <div className="pill-row">
                  <span className="signal-pill">quiebres {formatInt(aisle.stockouts)}</span>
                  <span className="signal-pill">baja cobertura {formatInt(aisle.lowCoverage)}</span>
                  <span className="signal-pill">venta/h {aisle.velocity}</span>
                </div>
              </div>
            ))}
          </div>
        </SectionCard>
      </div>

      <SectionCard title="Acciones touch-first" subtitle="Atajos que dejan lista la siguiente ronda sin meter al cajero en un laberinto de taps.">
        <div className="action-grid">
          {page.quickActions.map((item) => (
            <div key={item.title} className="action-tile">
              <div className="action-kicker">{item.kicker}</div>
              <strong>{item.title}</strong>
              <div className="subtle">{item.description}</div>
            </div>
          ))}
        </div>
      </SectionCard>
    </AppShell>
  );
}
