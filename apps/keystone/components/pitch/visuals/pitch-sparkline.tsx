import { cn } from "@hitech/ui-kit";

export interface PitchSparklineProps {
  readonly points: readonly number[];
  readonly width?: number;
  readonly height?: number;
  readonly className?: string;
  readonly stroke?: string;
  readonly fill?: string;
  readonly label?: string;
}

function clampPoints(points: readonly number[]): readonly number[] {
  if (points.length === 0) {
    return [0, 0, 0, 0];
  }

  return points;
}

function toPath(points: readonly number[], width: number, height: number): string {
  const safe = clampPoints(points);
  const min = Math.min(...safe);
  const max = Math.max(...safe);
  const delta = max - min || 1;

  return safe
    .map((value, index) => {
      const x = (index / (safe.length - 1 || 1)) * width;
      const y = height - ((value - min) / delta) * height;
      return `${index === 0 ? "M" : "L"}${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
}

export function PitchSparkline({
  points,
  width = 180,
  height = 56,
  className,
  stroke = "#02A7CA",
  fill = "rgba(2,167,202,0.18)",
  label
}: PitchSparklineProps) {
  const safe = clampPoints(points);
  const path = toPath(safe, width, height);
  const area = `${path} L ${width} ${height} L 0 ${height} Z`;

  return (
    <figure className={cn("m-0 grid gap-1", className)}>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={label ?? "Sparkline"}>
        <path d={area} fill={fill} />
        <path d={path} fill="none" stroke={stroke} strokeWidth={2.2} strokeLinecap="round" />
      </svg>
      {label ? (
        <figcaption className="text-[0.68rem] text-[color:rgba(4,18,25,0.62)]">{label}</figcaption>
      ) : null}
    </figure>
  );
}
