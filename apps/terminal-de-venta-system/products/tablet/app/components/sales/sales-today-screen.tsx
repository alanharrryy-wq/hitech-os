"use client";

import { useEffect, useMemo, useState, type ChangeEvent } from "react";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
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
  const [error, setError] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);
  const gate = useMemo(() => decideCanSellFromRuntimeSnapshot(runtimeSnapshot), [runtimeSnapshot]);

  useEffect(() => {
    let alive = true;
    setSummary(null);
    setError(null);
    requestJson<{ summary: SalesTodaySummary }>("/api/pos/sales/today")
      .then((response) => {
        if (alive) setSummary(response.data.summary);
      })
      .catch((caught) => {
        if (!alive) return;
        const message = caught && typeof caught === "object" && "message" in caught
          ? String((caught as { message?: string }).message ?? "No se pudieron cargar las ventas de hoy.")
          : "No se pudieron cargar las ventas de hoy.";
        setError(message);
      });
    return () => {
      alive = false;
    };
  }, [reloadToken]);

  const tickets = useMemo(() => (summary ? filterTickets(summary.tickets, query) : []), [summary, query]);

  return (
    <PrismaTabletShellUnified
      currentPath="/sales/today"
      title="Ventas de hoy"
      subtitle="Tickets cerrados y resumen operativo del día."
      status={
        <TabletShellStatusPill tone={error ? "danger" : summary ? "ok" : "neutral"}>
          {error ? "Revisar ventas" : summary ? `${summary.tickets.length} tickets` : "Cargando"}
        </TabletShellStatusPill>
      }
      runtimeSnapshot={runtimeSnapshot}
      showRouteHeader={false}
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
        <nav className={styles.workspaceTabs} aria-label="Vistas de ventas">
          <a className={styles.workspaceTabActive} href="/sales/today" aria-current="page">Hoy</a>
          <a className={styles.workspaceTab} href="/sales/history">Historial</a>
          <a className={styles.workspaceTab} href="/returns">Devoluciones</a>
        </nav>
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
          <button className={styles.secondary} type="button" onClick={() => setReloadToken((value) => value + 1)} disabled={!summary && !error}>
            Actualizar
          </button>
        </div>
        <ContextualExportActions surface="sales" />
        {error ? (
          <section className={styles.stateCard} role="alert">
            <h2>No se pudieron cargar las ventas</h2>
            <p>{error}</p>
            <button className={styles.primary} type="button" onClick={() => setReloadToken((value) => value + 1)}>Reintentar</button>
          </section>
        ) : null}
        {summary ? <SalesTicketList tickets={tickets} /> : null}
      </main>
    </PrismaTabletShellUnified>
  );
}
