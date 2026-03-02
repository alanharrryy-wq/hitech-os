import { cn } from "@hitech/ui-kit";

export interface PitchRadialGaugeProps {
  readonly value: number;
  readonly max?: number;
  readonly size?: number;
  readonly label: string;
  readonly valueLabel?: string;
  readonly className?: string;
  readonly tone?: "teal" | "cyan" | "gold";
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function toneStroke(tone: PitchRadialGaugeProps["tone"]): string {
  if (tone === "gold") {
    return "#AB7B26";
  }

  if (tone === "teal") {
    return "#026F86";
  }

  return "#02A7CA";
}

export function PitchRadialGauge({
  value,
  max = 100,
  size = 136,
  label,
  valueLabel,
  className,
  tone = "cyan"
}: PitchRadialGaugeProps) {
  const normalized = clamp(Math.round((value / max) * 100), 0, 100);
  const radius = (size - 16) / 2;
  const circumference = 2 * Math.PI * radius;
  const dash = (normalized / 100) * circumference;

  return (
    <figure className={cn("m-0 inline-flex flex-col items-center gap-2", className)}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} role="img" aria-label={label}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(2,111,134,0.18)"
          strokeWidth={8}
          fill="none"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={toneStroke(tone)}
          strokeWidth={8}
          fill="none"
          strokeDasharray={`${dash} ${circumference}`}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
        <text
          x="50%"
          y="48%"
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="22"
          fontWeight="700"
          fill="#041219"
        >
          {valueLabel ?? `${normalized}%`}
        </text>
        <text
          x="50%"
          y="62%"
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="10"
          fill="rgba(4,18,25,0.65)"
        >
          {label}
        </text>
      </svg>
    </figure>
  );
}
