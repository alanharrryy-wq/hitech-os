"use client";

import { useEffect, useMemo, useState, type ChangeEvent } from "react";
import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { formatMoney, requestJson } from "@/lib/pos/cart-state";
import { DEFAULT_TABLET_RUNTIME_SNAPSHOT, type TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { decideCanSellFromRuntimeSnapshot } from "@/lib/operational-gate/can-sell";
import type { ShiftCashSummary } from "@/lib/shift-cash-closure/shift-cash-closure-contract";
import { buildClosePreview, buildShiftKpis, cashInputToCents, shiftStatusCopy, varianceTone } from "@/lib/shift-cash-closure/shift-cash-closure-view-model";
import styles from "./shift-cash-closure.module.css";

type ApiCurrent = { shift: ShiftCashSummary | null };
type ApiShift = { shift: ShiftCashSummary };
type UiState = "idle" | "loading" | "ready" | "error" | "success";

const DEFAULT_CASHIER = "Cajero principal";

function readError(error: unknown) {
  if (typeof error === "object" && error && "message" in error) return String((error as { message?: string }).message ?? "No se pudo operar turno.");
  if (error instanceof Error) return error.message;
  return "No se pudo operar turno.";
}

function snapshotWithShift(runtimeSnapshot: TabletRuntimeSnapshot, shift: ShiftCashSummary | null): TabletRuntimeSnapshot {
  if (!shift || shift.status !== "OPEN") {
    return {
      ...runtimeSnapshot,
      shift: {
        ...runtimeSnapshot.shift,
        state: "closed",
        label: "Turno cerrado",
        tone: "warn",
        openedAt: null,
        cashSessionId: null,
        actionHref: "/shift",
        actionLabel: "Abrir turno"
      }
    };
  }

  return {
    ...runtimeSnapshot,
    shift: {
      ...runtimeSnapshot.shift,
      state: "open",
      label: "Turno abierto",
      tone: "ok",
      openedAt: shift.openedAt,
      cashSessionId: shift.id,
      actionHref: "/shift",
      actionLabel: "Ver turno"
    }
  };
}

export function ShiftCashClosureScreen({ runtimeSnapshot = DEFAULT_TABLET_RUNTIME_SNAPSHOT }: { runtimeSnapshot?: TabletRuntimeSnapshot }) {
  const [shift, setShift] = useState<ShiftCashSummary | null>(null);
  const [state, setState] = useState<UiState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [cashier, setCashier] = useState(DEFAULT_CASHIER);
  const [cashStart, setCashStart] = useState("500.00");
  const [cashCounted, setCashCounted] = useState("");
  const [closeNote, setCloseNote] = useState("");

  async function loadCurrentShift() {
    setState("loading");
    setError(null);
    try {
      const response = await requestJson<ApiCurrent>("/api/pos/shift/current");
      setShift(response.data.shift);
      setState("ready");
    } catch (caught) {
      setError(readError(caught));
      setState("error");
    }
  }

  useEffect(() => {
    void loadCurrentShift();
  }, []);

  async function openShift() {
    setState("loading");
    setError(null);
    try {
      const response = await requestJson<ApiShift>("/api/pos/shift/open", {
        method: "POST",
        body: JSON.stringify({ cashier, cashierId: cashier, cashStartCents: cashInputToCents(cashStart) })
      });
      setShift(response.data.shift);
      setCashCounted("");
      setState("success");
    } catch (caught) {
      setError(readError(caught));
      setState("error");
    }
  }

  async function closeShift() {
    setState("loading");
    setError(null);
    try {
      const response = await requestJson<ApiShift>("/api/pos/shift/close", {
        method: "POST",
        body: JSON.stringify({ countedCashCents: cashInputToCents(cashCounted), note: closeNote || undefined })
      });
      setShift(response.data.shift);
      setState("success");
    } catch (caught) {
      setError(readError(caught));
      setState("error");
    }
  }

  const shellSnapshot = useMemo(() => snapshotWithShift(runtimeSnapshot, shift), [runtimeSnapshot, shift]);
  const gate = useMemo(() => decideCanSellFromRuntimeSnapshot(shellSnapshot), [shellSnapshot]);
  const copy = shiftStatusCopy(shift, state);
  const kpis = useMemo(() => buildShiftKpis(shift), [shift]);
  const closePreview = useMemo(() => buildClosePreview(shift, cashCounted), [shift, cashCounted]);
  const canOpen = !shift || shift.status === "CLOSED";
  const canClose = Boolean(shift?.canClose && cashCounted.trim());
  const closePanelActive = shift?.status === "OPEN";
  const statusTone = shift?.status === "OPEN" ? "ok" : error ? "danger" : "neutral";

  return (
    <PrismaTabletShellUnified
      currentPath="/shift"
      title="Turno y caja"
      subtitle="Abre caja, controla venta del turno, captura conteo y cierra con diferencia visible."
      status={<TabletShellStatusPill tone={statusTone}>{copy.badge}</TabletShellStatusPill>}
      runtimeSnapshot={shellSnapshot}
      visualSurface="tablet-shift"
      visualPreset="shift-direct-workbench"
    >
      <main className={styles.page} data-prisma-shift-layer="root" data-prisma-shift-workbench="route-1006-1535">
        <section className={styles.hero} data-prisma-shift-layer="hero">
          <div>
            <span className={styles.eyebrow}>Caja del dia</span>
            <h1>{copy.title}</h1>
            <p>{copy.detail}</p>
          </div>
          <div className={styles.heroActions} data-prisma-shift-layer="hero-actions">
            {gate.canShowSellNavigation ? <a className={styles.secondaryLink} data-prisma-shift-layer="secondary-action" href={gate.actionHref}>Ir a vender</a> : <span className={styles.secondaryLink} data-prisma-shift-layer="secondary-action" aria-disabled="true">Abre turno para vender</span>}
            <button type="button" className={styles.ghostButton} data-prisma-shift-layer="secondary-action" onClick={() => void loadCurrentShift()} disabled={state === "loading"}>Actualizar</button>
          </div>
        </section>

        {error ? <div className={styles.errorBanner} role="alert">{error}</div> : null}

        <section className={styles.kpiGrid} aria-label="Resumen del turno" data-prisma-shift-layer="kpi-grid">
          {kpis.map((item) => <article className={styles.kpiCard} key={item.label} data-prisma-shift-layer="kpi-card"><span>{item.label}</span><strong>{item.value}</strong><small>{item.hint}</small></article>)}
        </section>

        <section className={styles.workspace} data-prisma-shift-layer="workspace">
          <article className={styles.panel} data-current={canOpen ? "true" : "false"} data-prisma-shift-layer="panel-open">
            <header className={styles.panelHeader} data-prisma-shift-layer="panel-header"><span>Abrir turno</span><strong>{canOpen ? "Caja lista para iniciar" : "Ya hay turno abierto"}</strong></header>
            <label className={styles.field} data-prisma-shift-layer="field"><span>Cajero</span><input value={cashier} onChange={(event: ChangeEvent<HTMLInputElement>) => setCashier(event.target.value)} disabled={!canOpen || state === "loading"} /></label>
            <label className={styles.field} data-prisma-shift-layer="field"><span>Caja inicial</span><input inputMode="decimal" value={cashStart} onChange={(event: ChangeEvent<HTMLInputElement>) => setCashStart(event.target.value)} disabled={!canOpen || state === "loading"} /></label>
            <button type="button" className={styles.primaryButton} data-prisma-shift-layer="primary-action" onClick={() => void openShift()} disabled={!canOpen || state === "loading" || !cashier.trim()}>Abrir turno</button>
            {!canOpen ? <p className={styles.note}>Para iniciar otro turno, primero cierra el turno abierto.</p> : null}
          </article>

          <article className={styles.panel} data-current={closePanelActive ? "true" : "false"} data-prisma-shift-layer="panel-close">
            <header className={styles.panelHeader} data-prisma-shift-layer="panel-header"><span>Cerrar turno</span><strong>{shift?.status === "OPEN" ? "Conteo requerido" : "Sin turno abierto"}</strong></header>
            <div className={styles.cashBreakdown} data-prisma-shift-layer="cash-breakdown">
              <div data-prisma-shift-layer="cash-tile"><span>Caja inicial</span><strong>{formatMoney(shift?.cashStartCents ?? 0)}</strong></div>
              <div data-prisma-shift-layer="cash-tile"><span>Ventas del turno</span><strong>{formatMoney(shift?.salesTotalCents ?? 0)}</strong></div>
              <div data-prisma-shift-layer="cash-tile"><span>Efectivo esperado</span><strong>{formatMoney(shift?.expectedCashCents ?? 0)}</strong></div>
            </div>
            <label className={styles.field} data-prisma-shift-layer="field"><span>Conteo fisico</span><input inputMode="decimal" value={cashCounted} onChange={(event: ChangeEvent<HTMLInputElement>) => setCashCounted(event.target.value)} disabled={shift?.status !== "OPEN" || state === "loading"} /></label>
            <label className={styles.field} data-prisma-shift-layer="field"><span>Nota opcional</span><textarea value={closeNote} onChange={(event: ChangeEvent<HTMLTextAreaElement>) => setCloseNote(event.target.value)} disabled={shift?.status !== "OPEN" || state === "loading"} /></label>
            <div className={styles.varianceBox} data-prisma-shift-layer="variance" data-tone={varianceTone(closePreview.varianceCents)}><span>Diferencia estimada</span><strong>{formatMoney(closePreview.varianceCents)}</strong><small>{closePreview.copy}</small></div>
            <button type="button" className={styles.dangerButton} data-prisma-shift-layer="danger-action" onClick={() => void closeShift()} disabled={!canClose || state === "loading"}>Cerrar turno</button>
          </article>
        </section>

        <section className={styles.flowGuard} data-prisma-shift-layer="flow-guard">
          <strong>{gate.canSell ? "Venta habilitada" : "Venta bloqueada hasta abrir turno"}</strong>
          <p>{gate.canSell ? "Los tickets nuevos quedaran ligados al turno abierto." : "Abre turno para que cada venta quede ligada a caja, ticket y corte."}</p>
        </section>
      </main>
    </PrismaTabletShellUnified>
  );
}
