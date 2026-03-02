import type { SVGAttributes } from "react";
import { cn } from "../../../lib/cn.js";

export interface DonutGaugeProps extends Omit<SVGAttributes<SVGSVGElement>, "viewBox"> {
  readonly value: number;
  readonly min?: number;
  readonly max?: number;
  readonly size?: number;
  readonly strokeWidth?: number;
  readonly label?: string;
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

export function DonutGauge({
  value,
  min = 0,
  max = 100,
  size = 88,
  strokeWidth = 10,
  label,
  className,
  ...props
}: DonutGaugeProps) {
  const center = size / 2;
  const radius = center - strokeWidth;
  const circumference = 2 * Math.PI * radius;
  const safeValue = clamp(value, min, max);
  const ratio = (safeValue - min) / Math.max(max - min, 1);
  const dashOffset = circumference * (1 - ratio);

  return (
    <svg
      className={cn("ui-viz-donut", className)}
      viewBox={`0 0 ${size} ${size}`}
      role="img"
      aria-label={label ?? `Gauge value ${safeValue}`}
      {...props}
    >
      <circle
        className="ui-viz-track"
        cx={center}
        cy={center}
        r={radius}
        fill="none"
        strokeWidth={strokeWidth}
      />
      <circle
        className="ui-viz-value"
        cx={center}
        cy={center}
        r={radius}
        fill="none"
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        transform={`rotate(-90 ${center} ${center})`}
        strokeDasharray={circumference}
        strokeDashoffset={dashOffset}
      />
      <text
        x={center}
        y={center}
        textAnchor="middle"
        dominantBaseline="middle"
        fontSize={Math.max(11, size * 0.19)}
        fill="currentColor"
      >
        {Math.round(ratio * 100)}%
      </text>
    </svg>
  );
}
