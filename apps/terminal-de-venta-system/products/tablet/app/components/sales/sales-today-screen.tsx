"use client";

import { useEffect, useMemo, useState, type ChangeEvent } from "react";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { QuickActionStrip, QuickActionTile } from "@components/tablet-action-tiles/tablet-action-tiles";
import { requestJson } from "@/lib/pos/cart-state";
import type { SalesTodaySummary } from "@/lib/sales-today/types";
import { buildSalesKpis, filterTickets } from "@/lib/sales-today/view-model";
import { DEFAULT_TABLET_RUNTIME_SNAPSHOT, type TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { decideCanSellFromRuntimeSnapshot } from "@/lib/operational-gate/can-sell";
import { SalesKpiStrip } from "./sales-kpi-strip";
import { SalesTicketList } from "./sales-ticket-list";
import { ContextualExportActions } from "@components/reports/contextual-export-actions";
import styles from "./sales.module.css";

export function SalesTodayScreen({ runtimeSnapshot = DEFAULT_TABLET_RUNTIME_SNAPSHOT }: { runtimeSnapshot?: TabletRuntimeSnapshot }) {
  const [summary, setSummary] = useState<SalesTodaySummary | null>(null);
  const [query, setQuery] = useState("");
  const gate = useMemo(() => decideCanSellFromRuntimeSnapshot(runtimeSnapshot), [runtimeSnapshot]);

  useEffect(() => {
    requestJson<{ summary: SalesTodaySummary }>("/api/pos/sales/today").then((response) => setSummary(response.data.summary));
  }, []);

  const tickets = useMemo(() => (summary ? filterTickets(summary.tickets, query) : []), [summary, query]);

  return (
    <PrismaTabletShellUnified
      currentPath="/sales/today"
      title="Ventas de hoy"
      subtitle="Tickets cerrados y resumen operativo del día."
      status={<TabletShellStatusPill tone="ok">Tickets cerrados</TabletShellStatusPill>}
      runtimeSnapshot={runtimeSnapshot}
    >
      <main className={styles.salesPage}
        data-surface="tablet"
        data-screen="sales"
        data-zone="pos"
        data-panel="sales-today-screen"
        data-target="sales-today-screen-panel-35"
        data-kind="panel"
        data-role="revenue-core"
      >
        <section className={styles.hero}
          data-surface="tablet"
          data-screen="sales"
          data-zone="pos"
          data-panel="sales-today-screen"
          data-target="sales-today-screen-panel-36"
          data-kind="panel"
          data-role="revenue-core"
        >
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="sales_today_screen" data-target="sales-today-screen-span-1" data-kind="text" data-role="text">Ventas de hoy</span>
          <h1
            data-surface="tablet"
            data-screen="sales"
            data-zone="pos"
            data-panel="sales-today-screen"
            data-target="sales-today-screen-text-38"
            data-kind="text"
            data-role="copy"
          >Resumen de caja operativo</h1>
          <p data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="sales_today_screen" data-target="sales-today-screen-p-2" data-kind="text" data-role="text">Tickets reales del día, listos para revisar detalle o iniciar devolución desde el ticket.</p>
        </section>
        <QuickActionStrip label="Acciones rapidas de ventas de hoy">
          <QuickActionTile title="Nueva venta" description={gate.canShowSellNavigation ? "Abre POS para capturar otro ticket." : gate.detail} actionLabel={gate.canShowSellNavigation ? "Vender" : gate.actionLabel} icon="cart" tone={gate.canShowSellNavigation ? "primary" : "warning"} href={gate.actionHref} owner="pos" kind="quick-create" />
          <QuickActionTile title="Buscar ticket" description="Enfoca la búsqueda local por folio, cajero o producto." actionLabel="Buscar" icon="search" tone="neutral" href="#buscar-ticket" owner="sales" />
          <QuickActionTile title="Exportar ventas" description="Abre exportaciones locales confirmadas." actionLabel="Exportar" icon="save" tone="sync" href="/settings/export" owner="exports" />
          <QuickActionTile title="Nueva devolucion" description="Elige un ticket cerrado para devolver productos." actionLabel="Devolver" icon="receipt" tone="inventory" href="/returns" owner="returns" kind="quick-create" />
        </QuickActionStrip>
        {summary ? <SalesKpiStrip items={buildSalesKpis(summary)} /> : <div className={styles.empty}
          data-surface="tablet"
          data-screen="sales"
          data-zone="pos"
          data-panel="sales-today-screen"
          data-target="sales-today-screen-text-47"
          data-kind="text"
          data-role="copy"
        >Cargando ventas del día…</div>}
        <div className={styles.toolbar} id="buscar-ticket"
          data-surface="tablet"
          data-screen="sales"
          data-zone="pos"
          data-panel="sales-today-screen"
          data-target="sales-today-screen-search-48"
          data-kind="search"
          data-role="ticket-context"
        >
          <input value={query} onChange={(event: ChangeEvent<HTMLInputElement>) => setQuery(event.target.value)} placeholder="Buscar por folio, cajero o producto"
            data-surface="tablet"
            data-screen="sales"
            data-zone="pos"
            data-panel="sales-today-screen"
            data-target="sales-today-screen-search-49"
            data-kind="search"
            data-role="search-control"
          />
          <a className={styles.secondary} href={gate.canShowSellNavigation ? "/pos" : gate.actionHref}
            data-surface="tablet"
            data-screen="sales"
            data-zone="pos"
            data-panel="sales-today-screen"
            data-target="sales-today-screen-button-50"
            data-kind="button"
            data-role="action"
          >{gate.canShowSellNavigation ? "Volver a vender" : gate.actionLabel}</a>
        </div>
        <ContextualExportActions surface="sales" />
        <SalesTicketList tickets={tickets} />
      </main>
    </PrismaTabletShellUnified>
  );
}
