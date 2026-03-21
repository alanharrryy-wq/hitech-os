"use client";

import { useLayerFlags } from "@hitech/ui-kit";
import { PITCH_VALUATION_ECONOMICS } from "@hitech/contracts";
import { useEffect, useMemo, useState } from "react";

const VALUATION_BLUE = {
  start: "#78ccff",
  mid: "#2f9eff",
  end: "#0d71e8",
  deep: "#0b4db3",
  nodeFill: "#f5faff",
  trackTop: "rgba(129, 193, 255, 0.38)",
  trackBottom: "rgba(129, 193, 255, 0.12)",
  axis: "rgba(20, 68, 128, 0.24)"
} as const;

function useReducedMotionPreference(): boolean {
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
      return;
    }

    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const onChange = () => setReduced(media.matches);
    onChange();
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, []);

  return reduced;
}

function useMotionEnabled(): boolean {
  const { flags } = useLayerFlags();
  const reducedMotion = useReducedMotionPreference();
  return flags["motion.enabled"] && !reducedMotion;
}

function useCountUp(target: number, durationMs: number, motionEnabled: boolean): number {
  const [value, setValue] = useState(motionEnabled ? 0 : target);

  useEffect(() => {
    if (!motionEnabled) {
      setValue(target);
      return;
    }

    let rafId = 0;
    let start = 0;

    const frame = (timestamp: number) => {
      if (!start) {
        start = timestamp;
      }
      const elapsed = timestamp - start;
      const ratio = Math.min(1, elapsed / durationMs);
      setValue(Math.round(target * ratio));
      if (ratio < 1) {
        rafId = window.requestAnimationFrame(frame);
      }
    };

    rafId = window.requestAnimationFrame(frame);
    return () => window.cancelAnimationFrame(rafId);
  }, [durationMs, motionEnabled, target]);

  return value;
}

function formatUsd(value: number): string {
  return `$${value.toLocaleString("en-US")}`;
}

export function ValuationTimelineVisual() {
  const motionEnabled = useMotionEnabled();
  const [tooltipPinned, setTooltipPinned] = useState(false);
  const [tooltipHover, setTooltipHover] = useState(false);
  const showTooltip = tooltipPinned || tooltipHover;

  return (
    <figure
      className="pitch-valuation-figure pitch-valuation-figure--timeline m-0 grid gap-3"
      onMouseEnter={() => setTooltipHover(true)}
      onMouseLeave={() => setTooltipHover(false)}
    >
      <div className="pitch-valuation-meta-strip">
        <span className="pitch-valuation-meta-item">
          <span className="pitch-valuation-meta-label">Inicio</span>
          <span className="pitch-valuation-meta-value">D0</span>
        </span>
        <span className="pitch-valuation-meta-item">
          <span className="pitch-valuation-meta-label">Entrega + factura</span>
          <span className="pitch-valuation-meta-value">D30</span>
        </span>
        <span className="pitch-valuation-meta-item">
          <span className="pitch-valuation-meta-label">Cobro net 60</span>
          <span className="pitch-valuation-meta-value">D90</span>
        </span>
      </div>

      <svg
        viewBox="0 0 340 136"
        className="pitch-valuation-svg pitch-valuation-svg--premium"
        role="img"
        aria-label="Timeline D0 D30 D90"
      >
        <defs>
          <linearGradient id="pitch-timeline-gradient" x1="40" y1="0" x2="300" y2="0" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor={VALUATION_BLUE.start} stopOpacity="0.96" />
            <stop offset="52%" stopColor={VALUATION_BLUE.mid} stopOpacity="1" />
            <stop offset="100%" stopColor={VALUATION_BLUE.end} stopOpacity="0.95" />
          </linearGradient>
          <linearGradient id="pitch-timeline-track-fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={VALUATION_BLUE.trackTop} />
            <stop offset="100%" stopColor={VALUATION_BLUE.trackBottom} />
          </linearGradient>
          <radialGradient id="pitch-d30-emphasis" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={VALUATION_BLUE.mid} stopOpacity="0.26" />
            <stop offset="100%" stopColor={VALUATION_BLUE.mid} stopOpacity="0" />
          </radialGradient>
        </defs>
        <rect x="38" y="57" width="264" height="10" rx="5" fill="url(#pitch-timeline-track-fill)" opacity="0.92" />
        <path
          d="M40 62 H170 H300"
          fill="none"
          stroke="url(#pitch-timeline-gradient)"
          strokeWidth="2.8"
          strokeLinecap="round"
          className={motionEnabled ? "pitch-draw-line" : undefined}
        />

        <circle cx="40" cy="62" r="8" fill={VALUATION_BLUE.nodeFill} stroke={VALUATION_BLUE.start} strokeWidth="2.3" />
        <circle cx="170" cy="62" r="16" fill="url(#pitch-d30-emphasis)" />
        <circle cx="170" cy="62" r="12" fill="none" stroke={VALUATION_BLUE.mid} strokeWidth="1.8" opacity="0.36" />
        <circle cx="170" cy="62" r="8" fill={VALUATION_BLUE.nodeFill} stroke={VALUATION_BLUE.mid} strokeWidth="2.5" />
        <circle cx="300" cy="62" r="8" fill={VALUATION_BLUE.nodeFill} stroke={VALUATION_BLUE.end} strokeWidth="2.3" />

        <text x="26" y="28" className="pitch-valuation-node-label">D0</text>
        <text x="150" y="28" className="pitch-valuation-node-label">D30</text>
        <text x="281" y="28" className="pitch-valuation-node-label">D90</text>
      </svg>

      <div className="pitch-valuation-kpi-grid" role="list" aria-label="Resumen de ciclo de caja">
        <div className="pitch-valuation-kpi-card" role="listitem">
          <p className="pitch-valuation-kpi-label">D0</p>
          <p className="pitch-valuation-kpi-value">+$100k hoy</p>
        </div>
        <div className="pitch-valuation-kpi-card" role="listitem">
          <p className="pitch-valuation-kpi-label">D30</p>
          <p className="pitch-valuation-kpi-value">Entrega + factura SRG +$200k</p>
        </div>
        <div className="pitch-valuation-kpi-card" role="listitem">
          <p className="pitch-valuation-kpi-label">D90</p>
          <p className="pitch-valuation-kpi-value">Pago net 60</p>
        </div>
      </div>

      <button
        type="button"
        onClick={() => setTooltipPinned((value) => !value)}
        className="pitch-equity-tooltip-trigger pitch-valuation-action w-fit rounded-md border px-2 py-1 text-xs"
      >
        {showTooltip ? "Ocultar detalle" : "Ver detalle"}
      </button>
      {showTooltip ? (
        <figcaption className="pitch-equity-tooltip">
          D0 habilita ejecución. D30 dispara factura y Stage 2. D90 captura caja por condición net60.
        </figcaption>
      ) : null}
    </figure>
  );
}

export function ValuationDeriskVisual() {
  const motionEnabled = useMotionEnabled();
  const [tooltipPinned, setTooltipPinned] = useState(false);
  const [tooltipHover, setTooltipHover] = useState(false);
  const showTooltip = tooltipPinned || tooltipHover;

  return (
    <figure
      className="pitch-valuation-figure pitch-valuation-figure--derisk m-0 grid gap-3"
      onMouseEnter={() => setTooltipHover(true)}
      onMouseLeave={() => setTooltipHover(false)}
    >
      <div className="pitch-valuation-meta-strip">
        <span className="pitch-valuation-meta-item">
          <span className="pitch-valuation-meta-label">Riesgo inicial</span>
          <span className="pitch-valuation-meta-value">Alto</span>
        </span>
        <span className="pitch-valuation-meta-item">
          <span className="pitch-valuation-meta-label">Con factura SRG</span>
          <span className="pitch-valuation-meta-value">Medio</span>
        </span>
        <span className="pitch-valuation-meta-item">
          <span className="pitch-valuation-meta-label">Con 12/mes</span>
          <span className="pitch-valuation-meta-value">Controlado</span>
        </span>
      </div>

      <svg
        viewBox="0 0 340 142"
        className="pitch-valuation-svg pitch-valuation-svg--premium"
        role="img"
        aria-label="Curva de riesgo decreciente"
      >
        <defs>
          <linearGradient id="pitch-derisk-gradient" x1="20" y1="0" x2="320" y2="0" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor={VALUATION_BLUE.start} stopOpacity="0.96" />
            <stop offset="55%" stopColor={VALUATION_BLUE.mid} stopOpacity="1" />
            <stop offset="100%" stopColor={VALUATION_BLUE.end} stopOpacity="0.96" />
          </linearGradient>
        </defs>
        <path
          d="M20 100 C62 100 86 96 120 88 C156 79 188 69 220 58 C248 49 282 42 320 40"
          fill="none"
          stroke="url(#pitch-derisk-gradient)"
          strokeWidth="3.2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className={motionEnabled ? "pitch-draw-line" : undefined}
        />
        <line x1="20" y1="112" x2="320" y2="112" stroke={VALUATION_BLUE.axis} strokeWidth="1.2" />
        <circle cx="20" cy="100" r="4.8" fill={VALUATION_BLUE.start} />
        <circle cx="120" cy="88" r="5.4" fill={VALUATION_BLUE.mid} />
        <circle cx="220" cy="58" r="5.4" fill={VALUATION_BLUE.end} />
        <text x="14" y="132" className="pitch-valuation-node-copy">Hoy</text>
        <text x="102" y="132" className="pitch-valuation-node-copy">Con factura</text>
        <text x="202" y="132" className="pitch-valuation-node-copy">Con 12/mes</text>
      </svg>

      <div className="pitch-valuation-kpi-grid" role="list" aria-label="Resumen de reducción de riesgo">
        <div className="pitch-valuation-kpi-card" role="listitem">
          <p className="pitch-valuation-kpi-label">Hoy</p>
          <p className="pitch-valuation-kpi-value">Dependencia alta de validaciones</p>
        </div>
        <div className="pitch-valuation-kpi-card" role="listitem">
          <p className="pitch-valuation-kpi-label">Con factura</p>
          <p className="pitch-valuation-kpi-value">Evidencia comercial verificable</p>
        </div>
        <div className="pitch-valuation-kpi-card" role="listitem">
          <p className="pitch-valuation-kpi-label">Con 12/mes</p>
          <p className="pitch-valuation-kpi-value">Riesgo operativo en rango controlado</p>
        </div>
      </div>

      <button
        type="button"
        onClick={() => setTooltipPinned((value) => !value)}
        className="pitch-equity-tooltip-trigger pitch-valuation-action w-fit rounded-md border px-2 py-1 text-xs"
      >
        {showTooltip ? "Ocultar detalle" : "Ver detalle"}
      </button>
      {showTooltip ? (
        <figcaption className="pitch-equity-tooltip">
          El riesgo baja por evidencia: hoy sin factura, luego factura SRG, y finalmente operación mensual en curso.
        </figcaption>
      ) : null}
    </figure>
  );
}

export function ValuationEquityVisual() {
  const motionEnabled = useMotionEnabled();
  const [tooltipPinned, setTooltipPinned] = useState(false);
  const [tooltipHover, setTooltipHover] = useState(false);

  const economics = PITCH_VALUATION_ECONOMICS;
  const totalCash = economics.deal.totalCashUsd;
  const totalEffective = economics.deal.totalEffectiveUsd;
  const boost = totalEffective - totalCash;
  const equityAtLowCap = (totalEffective / economics.deal.capRangeUsd.low) * 100;
  const equityAtHighCap = (totalEffective / economics.deal.capRangeUsd.high) * 100;

  const radius = 44;
  const circumference = 2 * Math.PI * radius;
  const cashArc = (totalCash / totalEffective) * circumference;
  const boostArc = circumference - cashArc;

  const cashAnimated = useCountUp(totalCash, 600, motionEnabled);
  const effectiveAnimated = useCountUp(totalEffective, 750, motionEnabled);

  const showTooltip = tooltipPinned || tooltipHover;
  const percentageLabel = useMemo(
    () => `${equityAtHighCap.toFixed(1)}% - ${equityAtLowCap.toFixed(1)}%`,
    [equityAtHighCap, equityAtLowCap]
  );

  return (
    <figure
      className="pitch-valuation-figure pitch-valuation-figure--equity m-0 grid gap-3"
      onMouseEnter={() => setTooltipHover(true)}
      onMouseLeave={() => setTooltipHover(false)}
    >
      <div className="pitch-valuation-meta-strip">
        <span className="pitch-valuation-meta-item">
          <span className="pitch-valuation-meta-label">Cash comprometido</span>
          <span className="pitch-valuation-meta-value">{formatUsd(totalCash)}</span>
        </span>
        <span className="pitch-valuation-meta-item">
          <span className="pitch-valuation-meta-label">Efectivo equity</span>
          <span className="pitch-valuation-meta-value">{formatUsd(totalEffective)}</span>
        </span>
        <span className="pitch-valuation-meta-item">
          <span className="pitch-valuation-meta-label">Rango de equity</span>
          <span className="pitch-valuation-meta-value">{percentageLabel}</span>
        </span>
      </div>

      <div className="pitch-valuation-equity-layout">
        <div className="pitch-valuation-equity-ring">
          <svg
            viewBox="0 0 120 120"
            className="pitch-valuation-svg pitch-valuation-svg--premium"
            role="img"
            aria-label="Meter de equity"
          >
            <defs>
              <linearGradient id="pitch-equity-cash-gradient" x1="16" y1="16" x2="104" y2="104" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stopColor={VALUATION_BLUE.start} />
                <stop offset="100%" stopColor={VALUATION_BLUE.mid} />
              </linearGradient>
              <linearGradient id="pitch-equity-boost-gradient" x1="104" y1="16" x2="16" y2="104" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stopColor={VALUATION_BLUE.end} />
                <stop offset="100%" stopColor={VALUATION_BLUE.deep} />
              </linearGradient>
            </defs>
            <g transform="translate(60 60) rotate(-90)">
              <circle r={radius} fill="none" stroke={VALUATION_BLUE.axis} strokeWidth="11.5" />
              <circle
                r={radius}
                fill="none"
                stroke="url(#pitch-equity-cash-gradient)"
                strokeWidth="11.5"
                strokeLinecap="round"
                strokeDasharray={`${cashArc} ${circumference}`}
                className={motionEnabled ? "pitch-draw-circle" : undefined}
              />
              <circle
                r={radius}
                fill="none"
                stroke="url(#pitch-equity-boost-gradient)"
                strokeWidth="11.5"
                strokeLinecap="round"
                strokeDasharray={`${boostArc} ${circumference}`}
                strokeDashoffset={-cashArc}
                className={motionEnabled ? "pitch-draw-circle" : undefined}
              />
            </g>
            <text x="60" y="55" textAnchor="middle" className="pitch-valuation-node-label">Equity</text>
            <text x="60" y="73" textAnchor="middle" className="pitch-valuation-node-copy">{percentageLabel}</text>
          </svg>
        </div>

        <div className="pitch-valuation-equity-metrics text-sm text-[color:var(--pitch-ink)]">
          <div className="pitch-valuation-equity-metric">
            <p className="m-0 text-[10px] uppercase tracking-[0.08em] text-[color:var(--pitch-muted)]">Cash</p>
            <p className="m-0 text-base font-semibold text-[color:var(--pitch-neutral-ink-950)]">{formatUsd(cashAnimated)}</p>
          </div>
          <div className="pitch-valuation-equity-metric">
            <p className="m-0 text-[10px] uppercase tracking-[0.08em] text-[color:var(--pitch-muted)]">Efectivo equity</p>
            <p className="m-0 text-base font-semibold text-[color:var(--pitch-neutral-ink-950)]">{formatUsd(effectiveAnimated)}</p>
          </div>
          <div className="pitch-valuation-equity-metric">
            <p className="m-0 text-[10px] uppercase tracking-[0.08em] text-[color:var(--pitch-muted)]">Cap sensitivity</p>
            <p className="m-0 text-sm font-medium text-[color:var(--pitch-neutral-ink-950)]">
              Cap 6M → {equityAtHighCap.toFixed(1)}% | Cap 4M → {equityAtLowCap.toFixed(1)}%
            </p>
          </div>
        </div>
      </div>

      <button
        type="button"
        onClick={() => setTooltipPinned((value) => !value)}
        className="pitch-equity-tooltip-trigger pitch-valuation-action mt-1 w-fit rounded-md border px-2 py-1 text-xs"
      >
        {showTooltip ? "Ocultar fórmula" : "Ver fórmula"}
      </button>

      {showTooltip ? (
        <figcaption className="pitch-equity-tooltip">
          {formatUsd(totalEffective)} = {formatUsd(totalCash)} cash + {formatUsd(boost)} boost de conversión.
          Equity = efectivo/cap.
        </figcaption>
      ) : null}
    </figure>
  );
}
