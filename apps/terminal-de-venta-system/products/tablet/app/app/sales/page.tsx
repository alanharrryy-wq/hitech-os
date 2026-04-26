import { AppShell } from "@components/layout/app-shell";
import { ActionChip } from "@components/ui/action-chip";
import { FlowStep } from "@components/ui/flow-step";
import { SectionCard } from "@components/ui/section-card";
import { StatCard } from "@components/ui/stat-card";
import { StatusBadge } from "@components/ui/status-badge";
import { TableSimple } from "@components/ui/table-simple";
import { getSalesConsole } from "@/lib/services/sales";
import { getUxProKit } from "@/lib/services/ux-pro";
import { tabletMessages } from "@/lib/i18n/messages/es";
import { formatInt, formatMoney } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function SalesPage() {
  const page = tabletMessages.pages.sales;
  const sales = await getSalesConsole();
  const ux = getUxProKit();

  return (
    <AppShell currentPath="/sales">
      <section className="hero">
        <div className="kicker">{page.kicker}</div>
        <h1 style={{ margin: 0 }}>{page.title}</h1>
        <div className="subtle">{page.subtitle}</div>
      </section>

      <div className="grid cols-4">
        <StatCard label="Ventas netas" value={formatMoney(sales.kpis.netSales)} note="Sale.totalCents" />
        <StatCard label="Tickets" value={formatInt(sales.kpis.tickets)} note="Sale canónico" />
        <StatCard label="Ticket promedio" value={formatMoney(sales.kpis.avgTicket)} note="calculado desde líneas" />
        <StatCard label="Items" value={formatInt(sales.queue.waitingItems)} note="SaleLine.qty" />
      </div>

      <div className="grid cols-2">
        <SectionCard title="Cola express de venta" subtitle="Secuencia corta para escanear, ajustar y vender sin meter reversa cada rato.">
          <div className="stack-list compact">
            {ux.salesDeck.queue.map((item) => (
              <FlowStep key={item.title} step={item.step} title={item.title} description={item.description} tone={item.tone} aside={<span className="code">{item.aside}</span>} />
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Favoritos del turno" subtitle="SKU rapidos para que caja no ande buscando lo que siempre vende.">
          <div className="pill-set">
            {ux.salesDeck.favorites.map((item) => (
              <span key={item} className="pill">{item}</span>
            ))}
          </div>
          <div style={{ height: 12 }} />
          <div className="stack-list compact">
            {ux.salesDeck.suggestions.map((item, index) => (
              <ActionChip key={item} title={item} description="Atajo sugerido por comportamiento del turno y presion de stock." meta={`S-${index + 1}`} tone={index === 1 ? "warn" : "ok"} />
            ))}
          </div>
        </SectionCard>
      </div>

      <SectionCard title="KPIs del modulo" subtitle="El flow sigue amarrado a los indicadores que importan en caja.">
        <div className="pill-set">
          {page.bullets.map((item) => (
            <StatusBadge key={item} tone="ok">{item}</StatusBadge>
          ))}
        </div>
      </SectionCard>

      <SectionCard title="Tickets recientes" subtitle="Lectura runtime desde Prisma canónico.">
        <TableSimple
          columns={["Folio", "Total", "Items", "Cajero", "Estado"]}
          rows={sales.recentTickets.map((ticket) => ({
            Folio: ticket.folio,
            Total: formatMoney(ticket.total),
            Items: formatInt(ticket.items),
            Cajero: ticket.cashier,
            Estado: <StatusBadge tone={ticket.tone}>{ticket.status}</StatusBadge>
          }))}
        />
      </SectionCard>
    </AppShell>
  );
}
