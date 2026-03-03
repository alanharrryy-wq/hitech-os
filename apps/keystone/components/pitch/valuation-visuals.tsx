"use client";

import { useLayerFlags } from "@hitech/ui-kit";
import { PITCH_VALUATION_ECONOMICS } from "@hitech/contracts";
import { useEffect, useMemo, useState } from "react";

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
      className="m-0 grid gap-2"
      onMouseEnter={() => setTooltipHover(true)}
      onMouseLeave={() => setTooltipHover(false)}
    >
      <svg viewBox="0 0 340 134" className="pitch-valuation-svg" role="img" aria-label="Timeline D0 D30 D90">
        <defs>
          <filter id="pitch-d30-gaussian" x="-80%" y="-80%" width="260%" height="260%">
            <feGaussianBlur stdDeviation="10" />
          </filter>
        </defs>
        <path
          d="M40 62 H170 H300"
          fill="none"
          stroke="var(--pitch-accent-teal)"
          strokeWidth="2.4"
          strokeLinecap="round"
          className={motionEnabled ? "pitch-draw-line" : undefined}
        />

        <circle cx="40" cy="62" r="8" fill="var(--pitch-card-bg-strong)" stroke="var(--pitch-accent-violet)" strokeWidth="2" />
        <circle
          cx="170"
          cy="62"
          r="17"
          className={motionEnabled ? "pitch-halo-d30 pitch-halo-d30-pulse" : "pitch-halo-d30"}
          fill="var(--pitch-accent-teal)"
          filter="url(#pitch-d30-gaussian)"
        />
        <circle cx="170" cy="62" r="8" fill="var(--pitch-card-bg-strong)" stroke="var(--pitch-accent-teal)" strokeWidth="2" />
        <circle cx="300" cy="62" r="8" fill="var(--pitch-card-bg-strong)" stroke="var(--pitch-accent-amber)" strokeWidth="2" />

        <text x="26" y="28" className="pitch-valuation-node-label">D0</text>
        <text x="150" y="28" className="pitch-valuation-node-label">D30</text>
        <text x="281" y="28" className="pitch-valuation-node-label">D90</text>

        <text x="12" y="95" className="pitch-valuation-node-copy">+$100k hoy</text>
        <text x="112" y="95" className="pitch-valuation-node-copy">Entrega + factura SRG +$200k</text>
        <text x="256" y="95" className="pitch-valuation-node-copy">Pago net 60</text>
      </svg>
      <button
        type="button"
        onClick={() => setTooltipPinned((value) => !value)}
        className="pitch-equity-tooltip-trigger w-fit rounded-md border px-2 py-1 text-xs"
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
      className="m-0 grid gap-2"
      onMouseEnter={() => setTooltipHover(true)}
      onMouseLeave={() => setTooltipHover(false)}
    >
      <svg viewBox="0 0 340 140" className="pitch-valuation-svg" role="img" aria-label="Curva de riesgo decreciente">
        <path
          d="M20 100 L120 100 L120 78 L220 78 L220 54 L320 54"
          fill="none"
          stroke="var(--pitch-accent-violet)"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
          className={motionEnabled ? "pitch-draw-line" : undefined}
        />
        <line x1="20" y1="112" x2="320" y2="112" stroke="var(--pitch-hairline)" strokeWidth="1" />
        <circle cx="120" cy="78" r="5" fill="var(--pitch-accent-teal)" />
        <circle cx="220" cy="54" r="5" fill="var(--pitch-accent-amber)" />
        <text x="14" y="132" className="pitch-valuation-node-copy">Hoy</text>
        <text x="102" y="132" className="pitch-valuation-node-copy">Con factura</text>
        <text x="202" y="132" className="pitch-valuation-node-copy">Con 12/mes</text>
      </svg>
      <button
        type="button"
        onClick={() => setTooltipPinned((value) => !value)}
        className="pitch-equity-tooltip-trigger w-fit rounded-md border px-2 py-1 text-xs"
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
      className="m-0 grid gap-2"
      onMouseEnter={() => setTooltipHover(true)}
      onMouseLeave={() => setTooltipHover(false)}
    >
      <div className="grid items-center gap-3 sm:grid-cols-[112px_1fr]">
        <svg viewBox="0 0 120 120" className="pitch-valuation-svg" role="img" aria-label="Meter de equity">
          <g transform="translate(60 60) rotate(-90)">
            <circle r={radius} fill="none" stroke="var(--pitch-hairline)" strokeWidth="12" />
            <circle
              r={radius}
              fill="none"
              stroke="var(--pitch-accent-teal)"
              strokeWidth="12"
              strokeLinecap="round"
              strokeDasharray={`${cashArc} ${circumference}`}
              className={motionEnabled ? "pitch-draw-circle" : undefined}
            />
            <circle
              r={radius}
              fill="none"
              stroke="var(--pitch-accent-amber)"
              strokeWidth="12"
              strokeLinecap="round"
              strokeDasharray={`${boostArc} ${circumference}`}
              strokeDashoffset={-cashArc}
              className={motionEnabled ? "pitch-draw-circle" : undefined}
            />
          </g>
          <text x="60" y="55" textAnchor="middle" className="pitch-valuation-node-label">Equity</text>
          <text x="60" y="73" textAnchor="middle" className="pitch-valuation-node-copy">{percentageLabel}</text>
        </svg>

        <div className="grid gap-1 text-sm text-[color:var(--pitch-ink)]">
          <p className="m-0">Cash: {formatUsd(cashAnimated)}</p>
          <p className="m-0">Efectivo equity: {formatUsd(effectiveAnimated)}</p>
          <p className="m-0 text-xs text-[color:var(--pitch-muted)]">
            Cap 6M → {equityAtHighCap.toFixed(1)}% | Cap 4M → {equityAtLowCap.toFixed(1)}%
          </p>
          <button
            type="button"
            onClick={() => setTooltipPinned((value) => !value)}
            className="pitch-equity-tooltip-trigger mt-1 w-fit rounded-md border px-2 py-1 text-xs"
          >
            {showTooltip ? "Ocultar fórmula" : "Ver fórmula"}
          </button>
        </div>
      </div>

      {showTooltip ? (
        <figcaption className="pitch-equity-tooltip">
          {formatUsd(totalEffective)} = {formatUsd(totalCash)} cash + {formatUsd(boost)} boost de conversión.
          Equity = efectivo/cap.
        </figcaption>
      ) : null}
    </figure>
  );
}
