"use client";

import { useEffect, useMemo, useState, type ChangeEvent, type FormEvent } from "react";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { requestJson } from "@/lib/pos/cart-state";
import type { SalesTodaySummary } from "@/lib/sales-today/types";
import { buildSalesKpis, filterTickets } from "@/lib/sales-today/view-model";
import { DEFAULT_TABLET_RUNTIME_SNAPSHOT, type TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { SalesKpiStrip } from "./sales-kpi-strip";
import { SalesTicketList } from "./sales-ticket-list";
import styles from "./sales.module.css";

type Preset = "today" | "yesterday" | "7d" | "30d" | "custom";

const PRESETS: Array<{ key: Preset; label: string }> = [
  { key: "today", label: "Hoy" },
  { key: "yesterday", label: "Ayer" },
  { key: "7d", label: "7 días" },
  { key: "30d", label: "30 días" },
  { key: "custom", label: "Rango" }
];

function todayIsoDate() {
  const date = new Date();
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function addDays(dateText: string, days: number) {
  const date = new Date(`${dateText}T00:00:00`);
  date.setDate(date.getDate() + days);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function daysBetween(from: string, to: string) {
  const start = new Date(`${from}T00:00:00`);
  const end = new Date(`${to}T00:00:00`);
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return null;
  return Math.ceil((end.getTime() - start.getTime()) / 86_400_000) + 1;
}

export function SalesHistoryScreen({ runtimeSnapshot = DEFAULT_TABLET_RUNTIME_SNAPSHOT }: { runtimeSnapshot?: TabletRuntimeSnapshot }) {
  const today = todayIsoDate();
  const [summary, setSummary] = useState<SalesTodaySummary | null>(null);
  const [preset, setPreset] = useState<Preset>("7d");
  const [from, setFrom] = useState(addDays(today, -6));
  const [to, setTo] = useState(today);
  const [query, setQuery] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    const customDays = preset === "custom" ? daysBetween(from, to) : null;
    if (customDays !== null && customDays > 60) {
      setError("El rango personalizado no puede pasar de 60 días.");
      setSummary(null);
      return;
    }

    const params = new URLSearchParams({ preset, limit: "120" });
    if (preset === "custom") {
      params.set("from", from);
      params.set("to", to);
    }
    if (query.trim()) params.set("q", query.trim());

    setError(null);
    requestJson<{ summary: SalesTodaySummary }>(`/api/pos/sales/history?${params.toString()}`)
      .then((response) => setSummary(response.data.summary))
      .catch((requestError) => {
        const message = requestError && typeof requestError === "object" && "message" in requestError ? String((requestError as { message?: string }).message) : "No se pudo cargar historial local.";
        setError(message);
        setSummary(null);
      });
  }, [preset, from, to, query, reloadToken]);

  const tickets = useMemo(() => (summary ? filterTickets(summary.tickets, query).filter((ticket) => ticket.saleId && ticket.saleId !== "undefined") : []), [summary, query]);

  function applyCustomRange(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPreset("custom");
    setReloadToken((value) => value + 1);
  }

  return (
    <PrismaTabletShellUnified
      currentPath="/sales/history"
      title="Historial de ventas"
      subtitle="Consulta local de tickets sin depender de PC."
      status={<TabletShellStatusPill tone="ok">Consulta local</TabletShellStatusPill>}
      runtimeSnapshot={runtimeSnapshot}
      showRouteHeader={false}
    >
      <main className={styles.salesPage}
        data-surface="tablet"
        data-screen="sales"
        data-zone="pos"
        data-panel="sales-history-screen"
        data-target="sales-history-screen-panel-93"
        data-kind="panel"
        data-role="revenue-core"
      >
        <section className={styles.hero}
          data-surface="tablet"
          data-screen="sales"
          data-zone="pos"
          data-panel="sales-history-screen"
          data-target="sales-history-screen-panel-94"
          data-kind="panel"
          data-role="revenue-core"
        >
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="sales_history_screen" data-target="sales-history-screen-span-1" data-kind="text" data-role="text">Historial local</span>
          <h1
            data-surface="tablet"
            data-screen="sales"
            data-zone="pos"
            data-panel="sales-history-screen"
            data-target="sales-history-screen-text-96"
            data-kind="text"
            data-role="copy"
          >Ventas anteriores en esta Tablet</h1>
          <p data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="sales_history_screen" data-target="sales-history-screen-p-2" data-kind="text" data-role="text">Busca tickets locales por rangos acotados. La Tablet consulta su propia base y sigue vendiendo aunque PC no esté disponible.</p>
        </section>

        <nav className={styles.workspaceTabs} aria-label="Vistas de ventas">
          <a className={styles.workspaceTab} href="/sales/today">Hoy</a>
          <a className={styles.workspaceTabActive} href="/sales/history" aria-current="page">Historial</a>
          <a className={styles.workspaceTab} href="/returns">Devoluciones</a>
        </nav>

        <div className={styles.rangeBar} id="rango-ventas" role="tablist" aria-label="Rangos de historial"
          data-surface="tablet"
          data-screen="sales"
          data-zone="pos"
          data-panel="sales-history-screen"
          data-target="sales-history-screen-rangos-de-historial-107"
          data-kind="table"
          data-role="data-display"
        >
          {PRESETS.map((item) => (
            <button
              key={item.key}
              type="button"
              className={preset === item.key ? styles.primary : styles.secondary}
              aria-pressed={preset === item.key}
              data-surface="tablet"
              data-screen="sales"
              data-zone="pos"
              data-panel="sales-history-screen"
              data-target="sales-history-screen-button-109"
              data-kind="button"
              data-role="action"
                onClick={() => setPreset(item.key)}
              >
              {item.label}
            </button>
          ))}
        </div>

        <form className={styles.historyFilters} id="buscar-ticket-historial" onSubmit={applyCustomRange}
          data-surface="tablet"
          data-screen="sales"
          data-zone="pos"
          data-panel="sales-history-screen"
          data-target="sales-history-screen-button-121"
          data-kind="button"
          data-role="search-control"
        >
          <label
            data-surface="tablet"
            data-screen="sales"
            data-zone="pos"
            data-panel="sales-history-screen"
            data-target="sales-history-screen-text-122"
            data-kind="text"
            data-role="copy"
          >
            Buscar
            <input value={query} onChange={(event: ChangeEvent<HTMLInputElement>) => setQuery(event.target.value)} placeholder="Folio, cajero, SKU o producto"
              data-surface="tablet"
              data-screen="sales"
              data-zone="pos"
              data-panel="sales-history-screen"
              data-target="sales-history-screen-search-124"
              data-kind="search"
              data-role="search-control"
            />
          </label>
          <label
            data-surface="tablet"
            data-screen="sales"
            data-zone="pos"
            data-panel="sales-history-screen"
            data-target="sales-history-screen-text-126"
            data-kind="text"
            data-role="copy"
          >
            Desde
            <input type="date" value={from} onChange={(event: ChangeEvent<HTMLInputElement>) => setFrom(event.target.value)}
              data-surface="tablet"
              data-screen="sales"
              data-zone="pos"
              data-panel="sales-history-screen"
              data-target="sales-history-screen-field-128"
              data-kind="field"
              data-role="input"
            />
          </label>
          <label
            data-surface="tablet"
            data-screen="sales"
            data-zone="pos"
            data-panel="sales-history-screen"
            data-target="sales-history-screen-text-130"
            data-kind="text"
            data-role="copy"
          >
            Hasta
            <input type="date" value={to} onChange={(event: ChangeEvent<HTMLInputElement>) => setTo(event.target.value)}
              data-surface="tablet"
              data-screen="sales"
              data-zone="pos"
              data-panel="sales-history-screen"
              data-target="sales-history-screen-field-132"
              data-kind="field"
              data-role="input"
            />
          </label>
          <button className={styles.primary} type="submit"
            data-surface="tablet"
            data-screen="sales"
            data-zone="pos"
            data-panel="sales-history-screen"
            data-target="sales-history-screen-button-134"
            data-kind="button"
            data-role="action"
          >Aplicar rango</button>
        </form>

        {error ? (
          <section className={styles.stateCard}
            data-surface="tablet"
            data-screen="sales"
            data-zone="pos"
            data-panel="sales-history-screen"
            data-target="sales-history-screen-panel-138"
            data-kind="panel"
            data-role="revenue-core"
          >
            <h2
              data-surface="tablet"
              data-screen="sales"
              data-zone="pos"
              data-panel="sales-history-screen"
              data-target="sales-history-screen-text-139"
              data-kind="text"
              data-role="copy"
            >Rango bloqueado</h2>
            <p data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="sales_history_screen" data-target="sales-history-screen-p-3" data-kind="text" data-role="text">{error}</p>
            <p data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="sales_history_screen" data-target="sales-history-screen-p-4" data-kind="text" data-role="text">Usa un rango de hasta 60 días para proteger rendimiento de caja.</p>
          </section>
        ) : null}

        {summary ? <SalesKpiStrip items={buildSalesKpis(summary)} /> : !error ? <div className={styles.empty}
          data-surface="tablet"
          data-screen="sales"
          data-zone="pos"
          data-panel="sales-history-screen"
          data-target="sales-history-screen-text-145"
          data-kind="text"
          data-role="copy"
        >Cargando historial local…</div> : null}
        {summary ? <SalesTicketList tickets={tickets} basePath="/sales/history" emptyMessage="No hay tickets en este rango local." /> : null}
      </main>
    </PrismaTabletShellUnified>
  );
}
