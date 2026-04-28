import {
  PrismaActionCard,
  PrismaDataTable,
  PrismaEmptyState,
  PrismaFlowList,
  PrismaKpiStrip,
  PrismaPanel,
  PrismaPillCloud,
  PrismaPrimaryButton,
  PrismaQuickProductCard,
  PrismaSearchActionStrip,
  PrismaSecondaryButton,
  PrismaStatusBadge,
  PrismaTabletShell,
  PrismaTotalDisplay
} from "@components/prisma-dark-pos/prisma-route-ui";
import { products } from "@components/prisma-dark-pos/prisma-dark-pos-data";
import styles from "@components/prisma-dark-pos/prisma-dark-pos.module.css";
import { getSalesConsole } from "@/lib/services/sales";
import { getUxProKit } from "@/lib/services/ux-pro";
import { tabletMessages } from "@/lib/i18n/messages/es";
import { formatInt, formatMoney } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function SalesPage() {
  const page = tabletMessages.pages.sales;
  const sales = await getSalesConsole();
  const ux = getUxProKit();
  const topProductTiles = sales.topProducts.length
    ? sales.topProducts.map((product) => ({
        name: product.name,
        meta: product.sku,
        price: formatMoney(product.revenue),
        signal: `${formatInt(product.qty)} uds`
      }))
    : products.slice(0, 6).map((product) => ({
        name: product.name,
        meta: product.stock,
        price: product.price,
        signal: "favorito"
      }));

  const currentTicket = sales.recentTickets[0];

  return (
    <PrismaTabletShell
      currentPath="/sales"
      kicker={page.kicker}
      title={page.title}
      subtitle={page.subtitle}
      context={<PrismaStatusBadge tone={sales.queue.waitingTickets ? "warn" : "ok"}>{sales.queue.waitingTickets} pendientes</PrismaStatusBadge>}
      actions={<PrismaSearchActionStrip placeholder="Buscar producto, SKU o escanear código..." primaryLabel="ESCANEAR" secondaryLabel="Más" />}
    >
      <PrismaKpiStrip
        metrics={[
          { label: "Ventas netas", value: formatMoney(sales.kpis.netSales), note: "Lectura Sale.totalCents", icon: "wallet" },
          { label: "Tickets", value: formatInt(sales.kpis.tickets), note: "Tickets recientes", icon: "receipt" },
          { label: "Ticket promedio", value: formatMoney(sales.kpis.avgTicket), note: "Calculado desde líneas", icon: "chart" },
          { label: "Items", value: formatInt(sales.queue.waitingItems), note: "Unidades vendidas", icon: "package" }
        ]}
      />

      <div className={styles.salesConsoleLayout}>
        <div className={styles.salesCatalogPanel}>
          <PrismaPanel title="Venta rápida" subtitle="Atajos y productos calientes para que la caja llegue al cobro sin fricción." eyebrow="mostrador">
            <div className={styles.routeCategoryLine} aria-label="Categorías rápidas">
              {["Todos", "Bebidas", "Snacks", "Lácteos", "Abarrotes", "Limpieza", "Personal"].map((category, index) => (
                <span key={category} className={index === 0 ? styles.routeCategoryChipActive : styles.routeCategoryChip}>
                  {category}
                </span>
              ))}
            </div>
            <div style={{ height: 14 }} />
            <div className={styles.routeProductGrid}>
              {topProductTiles.map((product) => (
                <PrismaQuickProductCard key={`${product.name}-${product.meta}`} name={product.name} meta={product.meta} price={product.price} signal={product.signal} />
              ))}
            </div>
          </PrismaPanel>

          <div className="grid cols-2">
            <PrismaPanel title="Carril de caja" subtitle="Secuencia corta para escanear, ajustar y cobrar sin perder ritmo." eyebrow="flujo">
              <PrismaFlowList
                items={ux.salesDeck.queue.map((item) => ({
                  step: item.step,
                  title: item.title,
                  description: item.description,
                  tone: item.tone,
                  aside: item.aside
                }))}
              />
            </PrismaPanel>

            <PrismaPanel title="Favoritos del turno" subtitle="SKU sugeridos y acciones que bajan el tiempo por ticket." eyebrow="atajos">
              <PrismaPillCloud items={ux.salesDeck.favorites} tone="warn" />
              <div style={{ height: 14 }} />
              <div className={styles.routeFlowList}>
                {ux.salesDeck.suggestions.map((item, index) => (
                  <PrismaActionCard key={item} title={item} description="Atajo sugerido por comportamiento del turno y presión de stock." meta={`S-${index + 1}`} tone={index === 1 ? "warn" : "ok"} icon="sparkle" />
                ))}
              </div>
            </PrismaPanel>
          </div>
        </div>

        <aside className={styles.routeSideStack}>
          <PrismaPanel title="Panel de cobro" subtitle="Resumen vivo para decidir el siguiente movimiento." eyebrow="ticket">
            <PrismaTotalDisplay label="Ventas netas visibles" value={formatMoney(sales.kpis.netSales)} note="Total calculado desde tickets recientes" />
            <div style={{ height: 14 }} />
            {currentTicket ? (
              <div className={styles.routeSummaryRows}>
                <div className={styles.routeSummaryRow}>
                  <span>Último folio</span>
                  <strong>{currentTicket.folio}</strong>
                </div>
                <div className={styles.routeSummaryRow}>
                  <span>Cajero</span>
                  <strong>{currentTicket.cashier}</strong>
                </div>
                <div className={styles.routeSummaryRow}>
                  <span>Estado</span>
                  <PrismaStatusBadge tone={currentTicket.tone}>{currentTicket.status}</PrismaStatusBadge>
                </div>
              </div>
            ) : (
              <PrismaEmptyState title="Sin ticket activo" description="Escanea o busca un producto para iniciar la venta." icon="cart" />
            )}
            <div style={{ height: 14 }} />
            <PrismaPrimaryButton href="/checkout" shortcut="F2">IR A COBRO</PrismaPrimaryButton>
            <div style={{ height: 10 }} />
            <div className={styles.routeButtonGrid}>
              <PrismaSecondaryButton icon="save">Guardar</PrismaSecondaryButton>
              <PrismaSecondaryButton icon="trash">Limpiar</PrismaSecondaryButton>
            </div>
          </PrismaPanel>

          <PrismaPanel title="KPIs del módulo" subtitle="La venta sigue amarrada a indicadores operativos." eyebrow="control">
            <PrismaPillCloud items={page.bullets} tone="ok" />
          </PrismaPanel>
        </aside>
      </div>

      <PrismaPanel title="Tickets recientes" subtitle="Lectura runtime desde Prisma canónico." eyebrow="historial">
        <PrismaDataTable
          columns={["Folio", "Total", "Items", "Cajero", "Estado"]}
          emptyLabel="Aún no hay tickets recientes"
          rows={sales.recentTickets.map((ticket) => ({
            Folio: ticket.folio,
            Total: formatMoney(ticket.total),
            Items: formatInt(ticket.items),
            Cajero: ticket.cashier,
            Estado: <PrismaStatusBadge tone={ticket.tone}>{ticket.status}</PrismaStatusBadge>
          }))}
        />
      </PrismaPanel>
    </PrismaTabletShell>
  );
}
