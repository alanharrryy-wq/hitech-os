"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { QuickActionStrip, QuickActionTile } from "@components/tablet-action-tiles/tablet-action-tiles";
import { formatMoney, requestJson } from "@/lib/pos/cart-state";
import type { SalesTodaySummary, SalesTodayTicket } from "@/lib/sales-today/types";
import { DEFAULT_TABLET_RUNTIME_SNAPSHOT, type TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { RETURN_REASONS } from "@/lib/returns-contextual/return-reasons";
import type { ReturnSelection } from "@/lib/returns-contextual/types";
import { buildReturnPayload, lineReturnAlreadyReturnedQty, lineReturnAvailableQty, returnAmountCents } from "@/lib/returns-contextual/return-view-model";
import { createContextualReturn } from "@/lib/returns-contextual/return-flow";
import styles from "./returns.module.css";

type LoadState =
  | { status: "loading" }
  | { status: "ready"; ticket: SalesTodayTicket }
  | { status: "error"; message: string };

type ListState =
  | { status: "loading" }
  | { status: "ready"; summary: SalesTodaySummary }
  | { status: "error"; message: string };

function humanError(error: unknown, fallback: string) {
  if (error && typeof error === "object") {
    const maybe = error as { message?: string };
    if (typeof maybe.message === "string" && maybe.message.trim()) return maybe.message;
  }
  return fallback;
}

function clampQty(value: number, max: number) {
  if (!Number.isFinite(value)) return 0;
  return Math.max(0, Math.min(Math.trunc(value), Math.max(0, max)));
}

function ticketReturnHref(ticket: SalesTodayTicket) {
  const params = new URLSearchParams();
  if (ticket.businessId) params.set("businessId", ticket.businessId);
  const query = params.toString();
  return `/sales/today/${encodeURIComponent(ticket.saleId)}/return${query ? `?${query}` : ""}`;
}

function selectedCount(selection: ReturnSelection) {
  return Object.values(selection).reduce((sum, value) => sum + (Number.isFinite(value) ? Math.max(0, Math.trunc(value)) : 0), 0);
}

function HeaderState({ tone, children }: { tone: "ok" | "warn" | "danger" | "neutral"; children: string }) {
  return <TabletShellStatusPill tone={tone}>{children}</TabletShellStatusPill>;
}

export function ReturnsLandingScreen({
  businessId,
  runtimeSnapshot = DEFAULT_TABLET_RUNTIME_SNAPSHOT
}: {
  businessId?: string;
  runtimeSnapshot?: TabletRuntimeSnapshot;
}) {
  const searchParams = useSearchParams();
  const [state, setState] = useState<ListState>({ status: "loading" });
  const [reloadToken, setReloadToken] = useState(0);

  const returnFlash = useMemo(() => {
    const returnId = searchParams.get("returnId") ?? "";
    if (!returnId) return null;
    const amountCents = Number(searchParams.get("amountCents") ?? 0);
    const lineCount = Number(searchParams.get("lineCount") ?? 0);
    return {
      returnId,
      amountCents: Number.isFinite(amountCents) ? Math.max(0, Math.trunc(amountCents)) : 0,
      lineCount: Number.isFinite(lineCount) ? Math.max(0, Math.trunc(lineCount)) : 0
    };
  }, [searchParams]);

  useEffect(() => {
    let alive = true;
    const params = new URLSearchParams();
    if (businessId) params.set("businessId", businessId);
    const query = params.toString();
    setState({ status: "loading" });

    requestJson<{ summary: SalesTodaySummary }>(`/api/pos/sales/today${query ? `?${query}` : ""}`)
      .then((response) => {
        if (!alive) return;
        setState({ status: "ready", summary: response.data.summary });
      })
      .catch((error) => {
        if (!alive) return;
        setState({ status: "error", message: humanError(error, "No pude cargar los tickets cerrados para devolución.") });
      });

    return () => {
      alive = false;
    };
  }, [businessId, reloadToken]);

  const tickets = state.status === "ready" ? state.summary.tickets.filter((ticket) => ticket.lines.length > 0) : [];

  return (
    <PrismaTabletShellUnified
      currentPath="/returns"
      title="Devoluciones"
      subtitle="Elige un ticket cerrado y devuelve productos sin perder evidencia de caja."
      status={<HeaderState tone={state.status === "error" ? "danger" : tickets.length ? "ok" : "warn"}>{state.status === "error" ? "Revisar lectura" : `${tickets.length} tickets elegibles`}</HeaderState>}
      runtimeSnapshot={runtimeSnapshot}
    >
      <main className={styles.returnPage}
        data-surface="tablet"
        data-screen="returns"
        data-zone="pos"
        data-panel="return-from-ticket-screen"
        data-target="return-from-ticket-screen-ticket-109"
        data-kind="ticket"
        data-role="ticket-context"
      >
        <section className={styles.heroPanel}
          data-surface="tablet"
          data-screen="returns"
          data-zone="pos"
          data-panel="return-from-ticket-screen"
          data-target="return-from-ticket-screen-ticket-110"
          data-kind="ticket"
          data-role="ticket-context"
        >
          <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="return_from_ticket_screen" data-target="return-from-ticket-screen-span-1" data-kind="layout" data-role="layout" className={styles.eyebrow}>Devolución contextual</span>
          <h1>Selecciona el ticket origen</h1>
          <p>Las devoluciones se crean desde ventas cerradas para conservar folio, líneas, importe, stock y evidencia local.</p>
          <div className={styles.actionsRow}
            data-surface="tablet"
            data-screen="returns"
            data-zone="pos"
            data-panel="return-from-ticket-screen"
            data-target="return-from-ticket-screen-button-114"
            data-kind="button"
            data-role="ticket-context"
          >
<button className={styles.secondaryButton} type="button"
              data-surface="tablet"
              data-screen="returns"
              data-zone="pos"
              data-panel="return-from-ticket-screen"
              data-target="return-from-ticket-screen-button-115"
              data-kind="button"
              data-role="ticket-context"
              onClick={() => setReloadToken((value) => value + 1)}>Actualizar tickets</button>
            <a data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="return_from_ticket_screen" data-target="return-from-ticket-screen-a-2" data-kind="button" data-role="button" className={styles.secondaryButton} href="/sales/today">Ver ventas de hoy</a>
          </div>
        </section>

        <QuickActionStrip label="Acciones rapidas de devoluciones">
          <QuickActionTile title="Nueva devolucion" description="Selecciona un ticket cerrado y conserva evidencia local." actionLabel="Elegir ticket" icon="receipt" tone="inventory" href="#tickets-devolucion" owner="returns" kind="quick-create" />
          <QuickActionTile title="Buscar ticket" description="La lista muestra tickets elegibles del día." actionLabel="Buscar" icon="search" tone="neutral" href="#tickets-devolucion" owner="returns" />
          <QuickActionTile title="Ventas recientes" description="Consulta tickets cerrados antes de devolver." actionLabel="Ver ventas" icon="chart" tone="primary" href="/sales/today" owner="sales" />
          <QuickActionTile title="Actualizar tickets" description="Relee tickets cerrados sin cambiar datos." actionLabel="Actualizar" icon="bell" tone="sync" onClick={() => setReloadToken((value) => value + 1)} owner="returns" />
        </QuickActionStrip>

        {returnFlash ? (
          <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="return_from_ticket_screen" data-target="return-from-ticket-screen-div-3" data-kind="badge" data-role="container" className={styles.success} role="status" aria-live="polite">
            Devolución {returnFlash.returnId} registrada. Importe {formatMoney(returnFlash.amountCents)} · {returnFlash.lineCount} líneas. La operación quedó lista para caja, reportes e inventario local.
          </div>
        ) : null}

        {state.status === "loading" ? <section className={styles.panel}
          data-surface="tablet"
          data-screen="returns"
          data-zone="pos"
          data-panel="return-from-ticket-screen"
          data-target="return-from-ticket-screen-ticket-133"
          data-kind="ticket"
          data-role="ticket-context"
        >Cargando tickets cerrados…</section> : null}

        {state.status === "error" ? (
          <section className={styles.panel}
            data-surface="tablet"
            data-screen="returns"
            data-zone="pos"
            data-panel="return-from-ticket-screen"
            data-target="return-from-ticket-screen-ticket-136"
            data-kind="ticket"
            data-role="ticket-context"
          >
            <h2>No pude cargar devoluciones</h2>
            <p className={styles.error}>{state.message}</p>
<button className={styles.primary} type="button"
              data-surface="tablet"
              data-screen="returns"
              data-zone="pos"
              data-panel="return-from-ticket-screen"
              data-target="return-from-ticket-screen-button-139"
              data-kind="button"
              data-role="ticket-context"
              onClick={() => setReloadToken((value) => value + 1)}>Reintentar</button>
          </section>
        ) : null}

        {state.status === "ready" ? (
          <section className={styles.panel} id="tickets-devolucion"
            data-surface="tablet"
            data-screen="returns"
            data-zone="pos"
            data-panel="return-from-ticket-screen"
            data-target="return-from-ticket-screen-ticket-144"
            data-kind="ticket"
            data-role="ticket-context"
          >
            <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="return_from_ticket_screen" data-target="return-from-ticket-screen-div-4" data-kind="panel" data-role="container" className={styles.panelHeader}>
              <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="return_from_ticket_screen" data-target="return-from-ticket-screen-div-5" data-kind="panel" data-role="container">
                <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="return_from_ticket_screen" data-target="return-from-ticket-screen-span-6" data-kind="layout" data-role="layout" className={styles.eyebrow}>Tickets cerrados</span>
                <h2>{tickets.length ? "Listos para devolución" : "Sin tickets elegibles"}</h2>
              </div>
              <strong>{formatMoney(state.summary.totalCents)}</strong>
            </div>

            {tickets.length ? (
              <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="return_from_ticket_screen" data-target="return-from-ticket-screen-div-7" data-kind="layout" data-role="container" className={styles.ticketList}>
                {tickets.map((ticket) => (
                  <a data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="return_from_ticket_screen" data-target="return-from-ticket-screen-a-8" data-kind="layout" data-role="layout" className={styles.ticketRow} href={ticketReturnHref(ticket)} key={ticket.saleId}>
                    <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="return_from_ticket_screen" data-target="return-from-ticket-screen-div-9" data-kind="panel" data-role="container">
                      <strong>{ticket.folio}</strong>
                      <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="return_from_ticket_screen" data-target="return-from-ticket-screen-span-10" data-kind="text" data-role="text">{ticket.cashier} · {ticket.lineCount} líneas · {ticket.unitsSold} pzas</span>
                    </div>
                    <strong>{formatMoney(ticket.totalCents)}</strong>
                    <span className={styles.rowAction}
                      data-surface="tablet"
                      data-screen="returns"
                      data-zone="pos"
                      data-panel="return-from-ticket-screen"
                      data-target="return-from-ticket-screen-button-162"
                      data-kind="button"
                      data-role="ticket-context"
                    >Hacer devolución</span>
                  </a>
                ))}
              </div>
            ) : (
              <p className={styles.empty}>No hay tickets cerrados con líneas visibles para devolver. Crea una venta o revisa el historial.</p>
            )}
          </section>
        ) : null}
      </main>
    </PrismaTabletShellUnified>
  );
}

export function ReturnFromTicketScreen({
  saleId,
  businessId,
  runtimeSnapshot = DEFAULT_TABLET_RUNTIME_SNAPSHOT
}: {
  saleId: string;
  businessId?: string;
  runtimeSnapshot?: TabletRuntimeSnapshot;
}) {
  const router = useRouter();
  const [state, setState] = useState<LoadState>({ status: "loading" });
  const [selection, setSelection] = useState<ReturnSelection>({});
  const [reason, setReason] = useState("customer_request");
  const [notes, setNotes] = useState("");
  const [done, setDone] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let alive = true;
    const params = new URLSearchParams({ saleId });
    if (businessId) params.set("businessId", businessId);
    setState({ status: "loading" });
    setDone("");

    requestJson<{ ticket: SalesTodayTicket }>(`/api/pos/sales/detail?${params.toString()}`)
      .then((response) => {
        if (!alive) return;
        setState({ status: "ready", ticket: response.data.ticket });
        setSelection({});
      })
      .catch((error) => {
        if (!alive) return;
        setState({ status: "error", message: humanError(error, "No pude cargar el ticket origen para devolución.") });
      });

    return () => {
      alive = false;
    };
  }, [saleId, businessId, reloadToken]);

  const ticket = state.status === "ready" ? state.ticket : null;
  const amount = ticket ? returnAmountCents(ticket, selection) : 0;
  const qty = selectedCount(selection);

  function setLineQty(lineId: string, maxQty: number, nextQty: number) {
    setSelection((current) => ({ ...current, [lineId]: clampQty(nextQty, maxQty) }));
  }

  async function confirm() {
    if (!ticket || amount <= 0 || submitting) return;
    setSubmitting(true);
    setDone("");
    try {
      const payload = buildReturnPayload(ticket, selection, reason, notes);
      const result = await createContextualReturn(payload);
      const returnId = typeof result?.returnId === "string" ? result.returnId : "registrada";
      setDone(`Devolución ${returnId} registrada`);
      setSelection({});
      const params = new URLSearchParams();
      if (ticket.businessId) params.set("businessId", ticket.businessId);
      params.set("returnId", returnId);
      params.set("amountCents", String(result?.amountCents ?? amount));
      params.set("lineCount", String(result?.lineCount ?? qty));
      router.replace(`/returns?${params.toString()}`);
    } catch (error) {
      setState({ status: "error", message: humanError(error, "No pude registrar la devolución.") });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <PrismaTabletShellUnified
      currentPath={`/sales/today/${encodeURIComponent(saleId)}/return`}
      title="Devolución"
      subtitle="Selecciona productos del ticket cerrado y registra la devolución contextual."
      status={<HeaderState tone={done ? "ok" : amount > 0 ? "warn" : state.status === "error" ? "danger" : "neutral"}>{done || (amount > 0 ? `${qty} pzas · ${formatMoney(amount)}` : "Selecciona productos")}</HeaderState>}
      runtimeSnapshot={runtimeSnapshot}
    >
      <main data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="return_from_ticket_screen" data-target="return-from-ticket-screen-main-11" data-kind="panel" data-role="container" className={styles.returnPage}>
        {done ? <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="return_from_ticket_screen" data-target="return-from-ticket-screen-div-12" data-kind="panel" data-role="container" className={styles.success}>{done}</div> : null}

        {state.status === "loading" ? <section className={styles.panel}
          data-surface="tablet"
          data-screen="returns"
          data-zone="pos"
          data-panel="return-from-ticket-screen"
          data-target="return-from-ticket-screen-ticket-259"
          data-kind="ticket"
          data-role="ticket-context"
        >Cargando ticket origen…</section> : null}

        {state.status === "error" ? (
          <section className={styles.panel}
            data-surface="tablet"
            data-screen="returns"
            data-zone="pos"
            data-panel="return-from-ticket-screen"
            data-target="return-from-ticket-screen-ticket-262"
            data-kind="ticket"
            data-role="ticket-context"
          >
            <h1>No pude abrir la devolución</h1>
            <p className={styles.error}>{state.message}</p>
            <div className={styles.actionsRow}
              data-surface="tablet"
              data-screen="returns"
              data-zone="pos"
              data-panel="return-from-ticket-screen"
              data-target="return-from-ticket-screen-button-265"
              data-kind="button"
              data-role="ticket-context"
            >
<button className={styles.primary} type="button"
                data-surface="tablet"
                data-screen="returns"
                data-zone="pos"
                data-panel="return-from-ticket-screen"
                data-target="return-from-ticket-screen-button-266"
                data-kind="button"
                data-role="ticket-context"
                onClick={() => setReloadToken((value) => value + 1)}>Reintentar</button>
              <a data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="return_from_ticket_screen" data-target="return-from-ticket-screen-a-13" data-kind="button" data-role="button" className={styles.secondaryButton} href="/returns">Volver a devoluciones</a>
            </div>
          </section>
        ) : null}

        {ticket ? (
          <section data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="return_from_ticket_screen" data-target="return-from-ticket-screen-section-14" data-kind="panel" data-role="container" className={styles.returnGrid}>
            <article data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="return_from_ticket_screen" data-target="return-from-ticket-screen-article-15" data-kind="panel" data-role="container" className={styles.panel}>
              <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="return_from_ticket_screen" data-target="return-from-ticket-screen-div-16" data-kind="panel" data-role="container" className={styles.panelHeader}>
                <div>
                  <span className={styles.eyebrow}>Ticket origen</span>
                  <h1>{ticket.folio}</h1>
                  <p>{ticket.cashier} · {ticket.lineCount} líneas · {formatMoney(ticket.totalCents)}</p>
                </div>
                <a data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="return_from_ticket_screen" data-target="return-from-ticket-screen-a-17" data-kind="button" data-role="button" className={styles.secondaryButton} href="/returns">Cambiar ticket</a>
              </div>

              <div className={styles.ticketList}>
                {ticket.lines.map((line) => {
                  const availableQty = lineReturnAvailableQty(line);
                  const returnedQty = lineReturnAlreadyReturnedQty(line);
                  const currentQty = clampQty(selection[line.id] ?? 0, availableQty);
                  const fullyReturned = availableQty <= 0;
                  const partiallyReturned = returnedQty > 0 && !fullyReturned;
                  const lineClassName = [styles.line, fullyReturned ? styles.lineReturned : "", partiallyReturned ? styles.linePartialReturned : ""].filter(Boolean).join(" ");
                  return (
                    <div className={lineClassName} key={line.id} aria-disabled={fullyReturned}>
                      <div>
                        <div className={styles.lineTitleRow}
                          data-surface="tablet"
                          data-screen="returns"
                          data-zone="pos"
                          data-panel="return-from-ticket-screen"
                          data-target="return-from-ticket-screen-ticket-295"
                          data-kind="ticket"
                          data-role="ticket-context"
                        >
                          <strong>{line.productName}</strong>
                          {fullyReturned ? <span className={styles.returnedBadge}>Devuelto completo</span> : null}
                          {partiallyReturned ? <span className={styles.partialBadge}>Parcialmente devuelto</span> : null}
                        </div>
                        <span>{line.sku || "SKU sin registrar"} · vendido {line.qty} pzas · {formatMoney(line.priceCents)} c/u</span>
                        {returnedQty > 0 ? (
                          <span className={styles.returnedGhost}>Ya se devolvieron {returnedQty} de {line.qty} pzas. Disponible: {availableQty}.</span>
                        ) : (
                          <span className={styles.availableGhost}>Disponible para devolución: {availableQty} pzas.</span>
                        )}
                      </div>
                      <div className={styles.qtyControls}>
<button className={styles.qtyButton} type="button"
                          data-surface="tablet"
                          data-screen="returns"
                          data-zone="pos"
                          data-panel="return-from-ticket-screen"
                          data-target="return-from-ticket-screen-button-308"
                          data-kind="button"
                          data-role="ticket-context"
                          onClick={() => setLineQty(line.id, availableQty, currentQty - 1)} disabled={fullyReturned || currentQty <= 0}>−</button>
                        <strong>{currentQty}</strong>
<button className={styles.qtyButton} type="button"
                          data-surface="tablet"
                          data-screen="returns"
                          data-zone="pos"
                          data-panel="return-from-ticket-screen"
                          data-target="return-from-ticket-screen-button-310"
                          data-kind="button"
                          data-role="ticket-context"
                          onClick={() => setLineQty(line.id, availableQty, currentQty + 1)} disabled={fullyReturned || currentQty >= availableQty}>+</button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </article>

            <aside data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="return_from_ticket_screen" data-target="return-from-ticket-screen-aside-18" data-kind="panel" data-role="container" className={styles.panel}>
              <span className={styles.eyebrow}>Motivo</span>
              <div className={styles.reasonGrid}>
                {RETURN_REASONS.map((item) => (
                  <button
                    className={item.id === reason ? styles.reasonActive : styles.reasonButton}
                    key={item.id}
                    type="button"
                    data-surface="tablet"
                    data-screen="returns"
                    data-zone="pos"
                    data-panel="return-from-ticket-screen"
                    data-target="return-from-ticket-screen-button-322"
                    data-kind="button"
                    data-role="ticket-context"
                    onClick={() => setReason(item.id)}
                  >
                    {item.label}
                  </button>
                ))}
              </div>

              <label className={styles.notesLabel}>
                Notas opcionales
                <textarea className={styles.notes} value={notes} onChange={(event) => setNotes(event.target.value)} maxLength={500} placeholder="Ej. empaque abierto, cambio solicitado, error de captura…" />
              </label>

              <div className={styles.totalBox}>
                <span>Importe a devolver</span>
                <strong>{formatMoney(amount)}</strong>
                <small>{qty} piezas seleccionadas</small>
              </div>

<button className={styles.primary} type="button"
                data-surface="tablet"
                data-screen="returns"
                data-zone="pos"
                data-panel="return-from-ticket-screen"
                data-target="return-from-ticket-screen-button-344"
                data-kind="button"
                data-role="ticket-context"
                onClick={() => void confirm()} disabled={amount <= 0 || submitting}>
                {submitting ? "Registrando…" : "Confirmar devolución"}
              </button>
            </aside>
          </section>
        ) : null}
      </main>
    </PrismaTabletShellUnified>
  );
}
