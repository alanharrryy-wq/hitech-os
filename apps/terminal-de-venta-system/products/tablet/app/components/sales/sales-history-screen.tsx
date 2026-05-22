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
    >
      <main className={styles.salesPage}>
        <section className={styles.hero}>
          <span>Historial local</span>
          <h1>Ventas anteriores en esta Tablet</h1>
          <p>Busca tickets locales por rangos acotados. La Tablet consulta su propia base y sigue vendiendo aunque PC no esté disponible.</p>
        </section>

        <div className={styles.rangeBar} role="tablist" aria-label="Rangos de historial">
          {PRESETS.map((item) => (
            <button
              key={item.key}
              type="button"
              className={preset === item.key ? styles.primary : styles.secondary}
              aria-pressed={preset === item.key}
              onClick={() => setPreset(item.key)}
            >
              {item.label}
            </button>
          ))}
        </div>

        <form className={styles.historyFilters} onSubmit={applyCustomRange}>
          <label>
            Buscar
            <input value={query} onChange={(event: ChangeEvent<HTMLInputElement>) => setQuery(event.target.value)} placeholder="Folio, cajero, SKU o producto" />
          </label>
          <label>
            Desde
            <input type="date" value={from} onChange={(event: ChangeEvent<HTMLInputElement>) => setFrom(event.target.value)} />
          </label>
          <label>
            Hasta
            <input type="date" value={to} onChange={(event: ChangeEvent<HTMLInputElement>) => setTo(event.target.value)} />
          </label>
          <button className={styles.primary} type="submit">Aplicar rango</button>
        </form>

        {error ? (
          <section className={styles.stateCard}>
            <h2>Rango bloqueado</h2>
            <p>{error}</p>
            <p>Usa un rango de hasta 60 días para proteger rendimiento de caja.</p>
          </section>
        ) : null}

        {summary ? <SalesKpiStrip items={buildSalesKpis(summary)} /> : !error ? <div className={styles.empty}>Cargando historial local…</div> : null}
        {summary ? <SalesTicketList tickets={tickets} basePath="/sales/history" emptyMessage="No hay tickets en este rango local." /> : null}
      </main>
    </PrismaTabletShellUnified>
  );
}
