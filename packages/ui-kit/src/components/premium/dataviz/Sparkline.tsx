import type { SVGAttributes } from "react";
import { cn } from "../../../lib/cn.js";

export interface SparklineProps extends Omit<SVGAttributes<SVGSVGElement>, "viewBox" | "values"> {
  readonly values: readonly number[];
  readonly width?: number;
  readonly height?: number;
  readonly strokeWidth?: number;
  readonly area?: boolean;
}

function normalize(values: readonly number[], height: number): number[] {
  if (values.length === 0) {
    return [];
  }

  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = Math.max(max - min, 1);

  return values.map((value) => height - ((value - min) / range) * height);
}

export function Sparkline({
  values,
  width = 160,
  height = 48,
  strokeWidth = 2,
  area = true,
  className,
  ...props
}: SparklineProps) {
  if (values.length < 2) {
    return (
      <svg
        className={cn("ui-viz-sparkline", className)}
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label="Sparkline"
        {...props}
      />
    );
  }

  const points = normalize(values, height - strokeWidth);
  const step = width / Math.max(values.length - 1, 1);

  const linePath = points
    .map((point, index) => `${index === 0 ? "M" : "L"}${(step * index).toFixed(2)},${point.toFixed(2)}`)
    .join(" ");

  const areaPath = `${linePath} L ${width},${height} L 0,${height} Z`;

  return (
    <svg
      className={cn("ui-viz-sparkline", className)}
      viewBox={`0 0 ${width} ${height}`}
      fill="none"
      role="img"
      aria-label="Sparkline"
      {...props}
    >
      <path className="ui-viz-track" d={`M0,${height - 1} H${width}`} strokeWidth={1} />
      {area ? <path className="ui-viz-value" d={areaPath} stroke="none" /> : null}
      <path className="ui-viz-value" d={linePath} strokeWidth={strokeWidth} fill="none" />
    </svg>
  );
}
