import { cn } from "@hitech/ui-kit";
import { useId } from "react";

export interface PitchSparklineProps {
  readonly points: readonly number[];
  readonly width?: number;
  readonly height?: number;
  readonly className?: string;
  readonly stroke?: string;
  readonly fill?: string;
  readonly label?: string;
  readonly variant?: "default" | "premium";
  readonly smooth?: boolean;
  readonly showStats?: boolean;
  readonly valueFormatter?: (value: number) => string;
}

function clampPoints(points: readonly number[]): readonly number[] {
  if (points.length === 0) {
    return [0, 0, 0, 0];
  }

  return points;
}

interface PlotPoint {
  readonly value: number;
  readonly x: number;
  readonly y: number;
}

function toPlotPoints(points: readonly number[], width: number, height: number): readonly PlotPoint[] {
  const safe = clampPoints(points);
  const min = Math.min(...safe);
  const max = Math.max(...safe);
  const delta = max - min || 1;

  return safe.map((value, index) => {
    const x = (index / (safe.length - 1 || 1)) * width;
    const y = height - ((value - min) / delta) * height;
    return { value, x, y };
  });
}

function toLinearPath(points: readonly PlotPoint[]): string {
  return points.map((point, index) => `${index === 0 ? "M" : "L"}${point.x.toFixed(2)} ${point.y.toFixed(2)}`).join(" ");
}

function toSmoothPath(points: readonly PlotPoint[]): string {
  if (points.length < 2) {
    return toLinearPath(points);
  }

  const pointAt = (index: number): PlotPoint =>
    points[Math.max(0, Math.min(points.length - 1, index))] as PlotPoint;
  const first = pointAt(0);
  let path = `M${first.x.toFixed(2)} ${first.y.toFixed(2)}`;

  for (let index = 0; index < points.length - 1; index += 1) {
    const p0 = pointAt(index - 1);
    const p1 = pointAt(index);
    const p2 = pointAt(index + 1);
    const p3 = pointAt(index + 2);

    const c1x = p1.x + (p2.x - p0.x) / 6;
    const c1y = p1.y + (p2.y - p0.y) / 6;
    const c2x = p2.x - (p3.x - p1.x) / 6;
    const c2y = p2.y - (p3.y - p1.y) / 6;

    path += ` C${c1x.toFixed(2)} ${c1y.toFixed(2)}, ${c2x.toFixed(2)} ${c2y.toFixed(2)}, ${p2.x.toFixed(2)} ${p2.y.toFixed(2)}`;
  }

  return path;
}

export function PitchSparkline({
  points,
  width = 180,
  height = 56,
  className,
  stroke = "#02A7CA",
  fill = "rgba(2,167,202,0.18)",
  label,
  variant = "default",
  smooth = false,
  showStats = false,
  valueFormatter
}: PitchSparklineProps) {
  const safe = clampPoints(points);
  const uid = useId().replaceAll(":", "");
  const pointsXY = toPlotPoints(safe, width, height);
  const linePath = smooth ? toSmoothPath(pointsXY) : toLinearPath(pointsXY);
  const areaPath = `${linePath} L ${width} ${height} L 0 ${height} Z`;
  const start = safe[0] ?? 0;
  const end = safe[safe.length - 1] ?? start;
  const delta = end - start;
  const deltaSign = delta >= 0 ? "+" : "";
  const format = valueFormatter ?? ((value: number) => `${Math.round(value)}`);
  const lastPoint = pointsXY[Math.max(0, pointsXY.length - 1)] as PlotPoint;
  const lineGradientId = `pitch-sparkline-line-${uid}`;
  const areaGradientId = `pitch-sparkline-area-${uid}`;
  const peakGradientId = `pitch-sparkline-peak-${uid}`;
  const isPremium = variant === "premium";

  return (
    <figure
      className={cn(
        "m-0 grid gap-1",
        isPremium
          ? "rounded-xl border border-[rgba(47,158,255,0.24)] bg-[linear-gradient(170deg,rgba(255,255,255,0.82),rgba(237,246,255,0.58))] p-2 shadow-[inset_0_1px_0_rgba(255,255,255,0.72),0_10px_20px_rgba(11,77,179,0.12)]"
          : undefined,
        className
      )}
    >
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={label ?? "Sparkline"}>
        {isPremium ? (
          <>
            <defs>
              <linearGradient id={lineGradientId} x1="0" y1="0" x2={String(width)} y2="0" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stopColor="#78ccff" />
                <stop offset="55%" stopColor={stroke} />
                <stop offset="100%" stopColor="#0d71e8" />
              </linearGradient>
              <linearGradient id={areaGradientId} x1="0" y1="0" x2="0" y2={String(height)} gradientUnits="userSpaceOnUse">
                <stop offset="0%" stopColor={fill} stopOpacity="0.56" />
                <stop offset="100%" stopColor={fill} stopOpacity="0.08" />
              </linearGradient>
              <radialGradient id={peakGradientId} cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#2f9eff" stopOpacity="0.38" />
                <stop offset="100%" stopColor="#2f9eff" stopOpacity="0" />
              </radialGradient>
            </defs>
            {[0.25, 0.5, 0.75].map((ratio) => (
              <line
                key={ratio}
                x1="0"
                y1={(height * ratio).toFixed(2)}
                x2={String(width)}
                y2={(height * ratio).toFixed(2)}
                stroke="rgba(15,64,106,0.12)"
                strokeWidth="1"
              />
            ))}
            <path d={areaPath} fill={`url(#${areaGradientId})`} />
            <path d={linePath} fill="none" stroke={`url(#${lineGradientId})`} strokeWidth={4.2} strokeLinecap="round" opacity="0.18" />
            <path d={linePath} fill="none" stroke={`url(#${lineGradientId})`} strokeWidth={2.5} strokeLinecap="round" />
            <circle cx={lastPoint.x} cy={lastPoint.y} r="10" fill={`url(#${peakGradientId})`} />
            <circle cx={lastPoint.x} cy={lastPoint.y} r="3.4" fill="#f4fbff" stroke="#0d71e8" strokeWidth="1.8" />
          </>
        ) : (
          <>
            <path d={areaPath} fill={fill} />
            <path d={linePath} fill="none" stroke={stroke} strokeWidth={2.2} strokeLinecap="round" />
          </>
        )}
      </svg>

      <div className={cn("flex items-center justify-between gap-2", !label && !showStats ? "sr-only" : undefined)}>
        {label ? (
          <figcaption className="text-[0.68rem] text-[color:rgba(4,18,25,0.62)]">{label}</figcaption>
        ) : (
          <span />
        )}
        {showStats ? (
          <span className="text-[0.68rem] font-semibold text-[color:#0f406a]">
            {format(end)} ({deltaSign}{format(Math.abs(delta))})
          </span>
        ) : null}
      </div>
    </figure>
  );
}
