import { cn } from "@hitech/ui-kit";

export interface PitchDataChipProps {
  readonly label: string;
  readonly value?: string;
  readonly tone?: "gold" | "teal" | "cyan" | "brown" | "neutral";
  readonly className?: string;
}

function chipTone(tone: PitchDataChipProps["tone"]): string {
  if (tone === "gold") {
    return "border-[rgba(171,123,38,0.36)] bg-[rgba(171,123,38,0.12)] text-[color:#553E13]";
  }

  if (tone === "teal") {
    return "border-[rgba(2,111,134,0.35)] bg-[rgba(2,111,134,0.12)] text-[color:#026F86]";
  }

  if (tone === "cyan") {
    return "border-[rgba(2,167,202,0.35)] bg-[rgba(2,167,202,0.14)] text-[color:#025E72]";
  }

  if (tone === "brown") {
    return "border-[rgba(85,62,19,0.32)] bg-[rgba(85,62,19,0.12)] text-[color:#553E13]";
  }

  return "border-[rgba(4,18,25,0.23)] bg-[rgba(4,18,25,0.05)] text-[color:#041219]";
}

export function PitchDataChip({ label, value, tone = "neutral", className }: PitchDataChipProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-[0.68rem] font-semibold tracking-[0.06em]",
        chipTone(tone),
        className
      )}
    >
      <span>{label}</span>
      {value ? <span className="opacity-80">{value}</span> : null}
    </span>
  );
}
