import {
  PrismaActionCard,
  PrismaDataTable,
  PrismaKpiStrip,
  PrismaPanel,
  PrismaPillCloud,
  PrismaPrimaryButton,
  PrismaSearchActionStrip,
  PrismaSecondaryButton,
  PrismaStatusBadge,
  PrismaTabletShell,
  PrismaTotalDisplay
} from "@components/prisma-dark-pos/prisma-route-ui";
import styles from "@components/prisma-dark-pos/prisma-dark-pos.module.css";
import { getReturnsConsole } from "@/lib/services/returns";
import { getUxProKit } from "@/lib/services/ux-pro";
import { tabletMessages } from "@/lib/i18n/messages/es";
import { formatInt, formatMoney } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function ReturnsPage() {
  const page = tabletMessages.pages.returns;
  const returns = await getReturnsConsole();
  const ux = getUxProKit();

  return (
    <PrismaTabletShell
      currentPath="/returns"
      kicker={page.kicker}
      title={page.title}
      subtitle={page.subtitle}
      context={<PrismaStatusBadge tone={returns.kpis.returnCount ? "warn" : "ok"}>{formatInt(returns.kpis.returnCount)} casos</PrismaStatusBadge>}
      actions={<PrismaSearchActionStrip placeholder="Buscar folio, ticket o referencia de venta..." primaryLabel="BUSCAR FOLIO" secondaryLabel="Filtro" />}
    >
      <PrismaKpiStrip
        metrics={[
          { label: "Devoluciones", value: formatInt(returns.kpis.returnCount), note: "SaleReturn", icon: "receipt" },
          { label: "Monto", value: formatMoney(returns.kpis.amountToday), note: "amountCents", icon: "wallet" },
          { label: "Promedio", value: formatMoney(returns.kpis.avgRefund), note: "Refund calculado", icon: "chart" },
          { label: "Motivo top", value: returns.topReason.reason, note: `${formatInt(returns.topReason.count)} casos`, icon: "tag" }
        ]}
      />

      <div className={styles.returnsLayout}>
        <div className={styles.lookupPanel}>
          <PrismaPanel title="Lookup de devolución" subtitle="Primero el folio, luego motivo y evidencia. Menos ambigüedad en mostrador." eyebrow="control">
            <div className={styles.routeSummaryRows}>
              <div className={styles.routeSummaryRow}>
                <span>Folio origen</span>
                <strong>pendiente</strong>
              </div>
              <div className={styles.routeSummaryRow}>
                <span>Resolución</span>
                <PrismaStatusBadge tone="warn">por validar</PrismaStatusBadge>
              </div>
            </div>
            <div style={{ height: 14 }} />
            <PrismaPillCloud items={ux.returnsKit.reasons} tone="danger" />
          </PrismaPanel>

          <PrismaPanel title="Guardrails" subtitle="Candados que bajan fraude y suben trazabilidad sin matar el ritmo." eyebrow="seguridad">
            <div className={styles.routeFlowList}>
              {ux.returnsKit.guardrails.map((item) => (
                <PrismaActionCard key={item.title} title={item.title} description={item.description} meta={item.signal} tone={item.tone} icon={item.tone === "danger" ? "settings" : "receipt"} />
              ))}
            </div>
          </PrismaPanel>

          <PrismaPanel title="Checklist de caso" subtitle="Pasos mínimos para que la devolución salga limpia y defendible." eyebrow="auditoría">
            <PrismaPillCloud items={page.bullets} tone="ok" />
          </PrismaPanel>
        </div>

        <aside className={styles.routeSideStack}>
          <PrismaPanel title="Resumen de devolución" subtitle="El operador ve monto, motivo y cierre sin adivinar." eyebrow="ticket">
            <PrismaTotalDisplay label="Monto devuelto hoy" value={formatMoney(returns.kpis.amountToday)} note="Total desde SaleReturn" />
            <div style={{ height: 14 }} />
            <div className={styles.routeSummaryRows}>
              <div className={styles.routeSummaryRow}>
                <span>Motivo dominante</span>
                <strong>{returns.topReason.reason}</strong>
              </div>
              <div className={styles.routeSummaryRow}>
                <span>Restock</span>
                <strong>{formatInt(returns.kpis.restockableRate)}%</strong>
              </div>
              <div className={styles.routeSummaryRow}>
                <span>Cancelaciones</span>
                <strong>{formatInt(returns.kpis.cancelCount)}</strong>
              </div>
            </div>
            <div style={{ height: 14 }} />
            <PrismaPrimaryButton shortcut="F2">AUTORIZAR DEVOLUCIÓN</PrismaPrimaryButton>
            <div style={{ height: 10 }} />
            <div className={styles.routeButtonGrid}>
              <PrismaSecondaryButton icon="save">Guardar</PrismaSecondaryButton>
              <PrismaSecondaryButton icon="x">Cancelar</PrismaSecondaryButton>
            </div>
          </PrismaPanel>
        </aside>
      </div>

      <PrismaPanel title="Devoluciones recientes" subtitle="Lectura runtime desde SaleReturn canónico." eyebrow="historial">
        <PrismaDataTable
          columns={["Folio", "Motivo", "Monto", "Cajero", "Estado"]}
          emptyLabel="Aún no hay devoluciones recientes"
          rows={returns.recentReturns.map((row) => ({
            Folio: row.folio,
            Motivo: row.reason,
            Monto: formatMoney(row.amount),
            Cajero: row.cashier,
            Estado: <PrismaStatusBadge tone={row.tone}>{row.status}</PrismaStatusBadge>
          }))}
        />
      </PrismaPanel>
    </PrismaTabletShell>
  );
}
