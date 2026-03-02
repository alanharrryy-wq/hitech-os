import type { SVGAttributes } from "react";
import { cn } from "../../../lib/cn.js";

export interface RadialMeterProps extends Omit<SVGAttributes<SVGSVGElement>, "viewBox"> {
  readonly value: number;
  readonly min?: number;
  readonly max?: number;
  readonly size?: number;
  readonly ticks?: number;
  readonly label?: string;
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function polar(cx: number, cy: number, radius: number, angleDeg: number): [number, number] {
  const angle = (angleDeg * Math.PI) / 180;
  return [cx + radius * Math.cos(angle), cy + radius * Math.sin(angle)];
}

export function RadialMeter({
  value,
  min = 0,
  max = 100,
  size = 140,
  ticks = 10,
  label,
  className,
  ...props
}: RadialMeterProps) {
  const safeValue = clamp(value, min, max);
  const ratio = (safeValue - min) / Math.max(max - min, 1);
  const start = 150;
  const end = 390;
  const sweep = end - start;
  const current = start + sweep * ratio;

  const cx = size / 2;
  const cy = size / 2;
  const outer = size * 0.43;
  const inner = size * 0.34;

  const [sx, sy] = polar(cx, cy, outer, start);
  const [ex, ey] = polar(cx, cy, outer, end);
  const [vx, vy] = polar(cx, cy, outer, current);

  const arcPath = `M ${sx.toFixed(2)} ${sy.toFixed(2)} A ${outer.toFixed(2)} ${outer.toFixed(2)} 0 1 1 ${ex.toFixed(2)} ${ey.toFixed(2)}`;
  const valuePath = `M ${sx.toFixed(2)} ${sy.toFixed(2)} A ${outer.toFixed(2)} ${outer.toFixed(2)} 0 ${ratio > 0.5 ? 1 : 0} 1 ${vx.toFixed(2)} ${vy.toFixed(2)}`;

  return (
    <svg
      className={cn("ui-viz-radial", className)}
      viewBox={`0 0 ${size} ${size}`}
      role="img"
      aria-label={label ?? `Radial value ${safeValue}`}
      {...props}
    >
      <path className="ui-viz-track" d={arcPath} fill="none" strokeWidth={size * 0.06} strokeLinecap="round" />
      <path className="ui-viz-value" d={valuePath} fill="none" strokeWidth={size * 0.06} strokeLinecap="round" />

      {Array.from({ length: ticks + 1 }, (_, tick) => {
        const angle = start + (sweep / ticks) * tick;
        const [x1, y1] = polar(cx, cy, inner, angle);
        const [x2, y2] = polar(cx, cy, outer, angle);
        return (
          <line
            key={tick}
            x1={x1}
            y1={y1}
            x2={x2}
            y2={y2}
            className="ui-viz-gridline"
            strokeLinecap="round"
          />
        );
      })}

      <circle cx={vx} cy={vy} r={size * 0.03} fill="currentColor" />
      <text
        x={cx}
        y={cy + size * 0.16}
        textAnchor="middle"
        fontSize={Math.max(12, size * 0.14)}
        fill="currentColor"
      >
        {Math.round(ratio * 100)}%
      </text>
    </svg>
  );
}
