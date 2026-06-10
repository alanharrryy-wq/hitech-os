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

const DEFAULT_CASHIER = "tablet-cashier";

const SHIFT_INLINE_WORKBENCH_CSS = `
/* PRISMA_SHIFT_ROUTE_GLASSMAP_1006_1535::START
   Scope: /shift only.
   Intent: keep the atmospheric background visible once, make every block translucent,
   and preserve visible borders so the container map can be read at a glance.
*/
html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"][data-prisma-route="shift"] {
  --shift-route-bg-image: url('/visual-backgrounds/tablet/assets/tablet-cloudglass-default.jpg');
  --shift-route-ink: #10223a;
  --shift-route-muted: #536783;
  --shift-route-faint: #718199;
  --shift-route-line: rgba(36, 94, 161, .26);
  --shift-route-line-strong: rgba(18, 105, 238, .42);
  --shift-route-glass-root: rgba(248, 252, 255, .18);
  --shift-route-glass-panel: rgba(255, 255, 255, .34);
  --shift-route-glass-panel-strong: rgba(255, 255, 255, .42);
  --shift-route-glass-control: rgba(255, 255, 255, .58);
  --shift-route-shadow-soft: 0 10px 28px rgba(80, 116, 162, .08);
  --shift-route-sentinel: shift-route-glassmap-1006-1535;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"][data-prisma-route="shift"],
html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"][data-prisma-route="shift"] body {
  min-height: 100%;
  color: var(--shift-route-ink) !important;
  background: #edf6ff !important;
  text-shadow: none !important;
  filter: none !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"][data-prisma-route="shift"] body {
  background-image: none !important;
  isolation: isolate !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"][data-prisma-route="shift"] body::before {
  content: "" !important;
  display: block !important;
  position: fixed !important;
  inset: 0 !important;
  z-index: 0 !important;
  pointer-events: none !important;
  background: var(--shift-route-bg-image) center 56% / cover no-repeat fixed !important;
  opacity: .18 !important;
  filter: saturate(.76) contrast(.94) brightness(1.08) !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"][data-prisma-route="shift"] body::after {
  content: "" !important;
  display: block !important;
  position: fixed !important;
  inset: 0 !important;
  z-index: 0 !important;
  pointer-events: none !important;
  background:
    linear-gradient(180deg, rgba(255,255,255,.76) 0%, rgba(248,252,255,.60) 40%, rgba(237,246,255,.52) 100%),
    radial-gradient(circle at 48% 28%, rgba(255,255,255,.30), transparent 44%) !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-component="AppShell"][data-prisma-visual-preset="shift-direct-workbench"] {
  position: relative !important;
  z-index: 1 !important;
  isolation: isolate !important;
  background: transparent !important;
  background-image: none !important;
  box-shadow: none !important;
  filter: none !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-component="AppShell"][data-prisma-visual-preset="shift-direct-workbench"]::before,
html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-component="AppShell"][data-prisma-visual-preset="shift-direct-workbench"]::after,
html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-visual-preset="shift-direct-workbench"] [data-prisma-zone="tablet-shift-root"]::before,
html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-visual-preset="shift-direct-workbench"] [data-prisma-zone="tablet-shift-root"]::after {
  content: none !important;
  display: none !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-component="AppShell"][data-prisma-visual-preset="shift-direct-workbench"] [data-prisma-component="Sidebar"] {
  background: rgba(247, 252, 255, .62) !important;
  border-right: 1px solid rgba(54, 104, 168, .18) !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.52) !important;
  backdrop-filter: blur(8px) saturate(1.03) !important;
  -webkit-backdrop-filter: blur(8px) saturate(1.03) !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-component="AppShell"][data-prisma-visual-preset="shift-direct-workbench"] > main#contenido-principal {
  position: relative !important;
  z-index: 2 !important;
  background: transparent !important;
  box-shadow: none !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-component="TopCommandBar"] {
  margin: 0 0 10px !important;
  padding: 12px 0 10px !important;
  border-bottom: 1px solid rgba(29, 104, 205, .20) !important;
  background: rgba(250, 253, 255, .34) !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.44) !important;
  backdrop-filter: blur(8px) saturate(1.02) !important;
  -webkit-backdrop-filter: blur(8px) saturate(1.02) !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-zone="tablet-shift-root"] {
  position: relative !important;
  z-index: 2 !important;
  padding: 16px !important;
  border: 1px solid rgba(38, 104, 184, .22) !important;
  border-radius: 24px !important;
  color: var(--shift-route-ink) !important;
  background: var(--shift-route-glass-root) !important;
  background-image: none !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.52) !important;
  backdrop-filter: blur(10px) saturate(1.03) !important;
  -webkit-backdrop-filter: blur(10px) saturate(1.03) !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-zone="tablet-shift-root"] *,
html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-zone="tablet-shift-root"] *::before,
html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-zone="tablet-shift-root"] *::after {
  text-shadow: none !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer="root"] {
  display: grid !important;
  gap: 12px !important;
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer="hero"] {
  padding: 4px 0 14px !important;
  border: 0 !important;
  border-bottom: 1px solid var(--shift-route-line-strong) !important;
  background: transparent !important;
  box-shadow: none !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer="kpi-card"],
html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer^="panel"],
html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer="cash-tile"],
html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer="variance"],
html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer="flow-guard"] {
  border: 1px solid var(--shift-route-line) !important;
  background: var(--shift-route-glass-panel) !important;
  background-image: none !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.48), var(--shift-route-shadow-soft) !important;
  backdrop-filter: blur(10px) saturate(1.04) !important;
  -webkit-backdrop-filter: blur(10px) saturate(1.04) !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer^="panel"] {
  padding: 16px !important;
  border-radius: 18px !important;
  background: var(--shift-route-glass-panel-strong) !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer="kpi-card"] {
  border-radius: 16px !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer="workspace"] {
  display: grid !important;
  grid-template-columns: minmax(300px, .9fr) minmax(0, 1.1fr) !important;
  gap: 12px !important;
  align-items: start !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer="panel-header"] {
  display: flex !important;
  align-items: flex-start !important;
  justify-content: space-between !important;
  gap: 10px !important;
  padding: 0 0 8px !important;
  border-bottom: 1px solid var(--shift-route-line) !important;
  background: transparent !important;
  box-shadow: none !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer="cash-breakdown"] {
  display: grid !important;
  grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
  gap: 8px !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer="field"] input,
html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer="field"] textarea {
  border: 1px solid rgba(49, 99, 160, .26) !important;
  background: var(--shift-route-glass-control) !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.42) !important;
  backdrop-filter: blur(8px) saturate(1.03) !important;
  -webkit-backdrop-filter: blur(8px) saturate(1.03) !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer="field"] input:focus-visible,
html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer="field"] textarea:focus-visible {
  border-color: rgba(18, 110, 245, .66) !important;
  background: rgba(255,255,255,.76) !important;
  box-shadow: 0 0 0 3px rgba(18, 110, 245, .12) !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer="primary-action"],
html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer="danger-action"],
html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer="secondary-action"] {
  box-shadow: inset 0 1px 0 rgba(255,255,255,.26) !important;
  text-shadow: none !important;
}

html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer="secondary-action"] {
  background: rgba(255, 255, 255, .44) !important;
  color: var(--shift-route-ink) !important;
  border-color: var(--shift-route-line) !important;
  backdrop-filter: blur(8px) saturate(1.02) !important;
  -webkit-backdrop-filter: blur(8px) saturate(1.02) !important;
}

@media (max-width: 1120px) {
  html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-shift-layer="workspace"] {
    grid-template-columns: 1fr !important;
  }
}

@media (max-width: 720px) {
  html[data-prisma-skin="light"][data-prisma-surface="tablet-pos"] [data-prisma-zone="tablet-shift-root"] {
    padding: 10px !important;
    border-radius: 18px !important;
  }
}
/* PRISMA_SHIFT_ROUTE_GLASSMAP_1006_1535::END */
`;

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

  useEffect(() => {
    const root = document.documentElement;
    const body = document.body;
    const previousRootRoute = root.dataset.prismaRoute;
    const previousRootShiftMode = root.dataset.prismaShiftMode;
    const previousBodyRoute = body?.dataset.prismaRoute;
    root.dataset.prismaRoute = "shift";
    root.dataset.prismaShiftMode = "route-glassmap-1006-1535";
    if (body) body.dataset.prismaRoute = "shift";
    return () => {
      if (previousRootRoute === undefined) delete root.dataset.prismaRoute;
      else root.dataset.prismaRoute = previousRootRoute;
      if (previousRootShiftMode === undefined) delete root.dataset.prismaShiftMode;
      else root.dataset.prismaShiftMode = previousRootShiftMode;
      if (body) {
        if (previousBodyRoute === undefined) delete body.dataset.prismaRoute;
        else body.dataset.prismaRoute = previousBodyRoute;
      }
    };
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
      <style data-prisma-shift-inline-workbench="route-1006-1535" dangerouslySetInnerHTML={{ __html: SHIFT_INLINE_WORKBENCH_CSS }} />
      <main className={styles.page} data-prisma-shift-layer="root" data-prisma-shift-workbench="route-1006-1535">
        <section className={styles.hero} data-prisma-shift-layer="hero">
          <div>
            <span className={styles.eyebrow}>Corte operativo local</span>
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
          <article className={styles.panel} data-prisma-shift-layer="panel-open">
            <header className={styles.panelHeader} data-prisma-shift-layer="panel-header"><span>Abrir turno</span><strong>{canOpen ? "Caja lista para iniciar" : "Ya hay turno abierto"}</strong></header>
            <label className={styles.field} data-prisma-shift-layer="field"><span>Cajero</span><input value={cashier} onChange={(event: ChangeEvent<HTMLInputElement>) => setCashier(event.target.value)} disabled={!canOpen || state === "loading"} /></label>
            <label className={styles.field} data-prisma-shift-layer="field"><span>Caja inicial</span><input inputMode="decimal" value={cashStart} onChange={(event: ChangeEvent<HTMLInputElement>) => setCashStart(event.target.value)} disabled={!canOpen || state === "loading"} /></label>
            <button type="button" className={styles.primaryButton} data-prisma-shift-layer="primary-action" onClick={() => void openShift()} disabled={!canOpen || state === "loading" || !cashier.trim()}>Abrir turno</button>
            {!canOpen ? <p className={styles.note}>Para abrir otro turno, primero cierra el actual. Si no, esto se vuelve caja rusa, y no de las divertidas.</p> : null}
          </article>

          <article className={styles.panel} data-prisma-shift-layer="panel-close">
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
          <p>{gate.canSell ? "Los tickets nuevos quedaran ligados al turno abierto." : "La caja necesita turno abierto antes de cerrar ventas. Sin turno, vender seria como cobrar en servilleta: romantico, inutil y auditable con lupa."}</p>
        </section>
      </main>
    </PrismaTabletShellUnified>
  );
}
