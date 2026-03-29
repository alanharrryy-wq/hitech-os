import { cn } from "@hitech/ui-kit";

export interface PitchBulletCardsProps {
  readonly bullets: readonly string[];
  readonly className?: string;
  readonly tone?: "neutral" | "teal" | "cyan" | "gold";
}

function toneClass(tone: PitchBulletCardsProps["tone"]): string {
  if (tone === "teal") {
    return "border-[rgba(2,111,134,0.27)] bg-[rgba(2,111,134,0.08)]";
  }

  if (tone === "cyan") {
    return "border-[rgba(2,167,202,0.31)] bg-[rgba(2,167,202,0.09)]";
  }

  if (tone === "gold") {
    return "border-[rgba(171,123,38,0.31)] bg-[rgba(171,123,38,0.12)]";
  }

  return "border-[rgba(4,18,25,0.2)] bg-[rgba(255,255,255,0.68)]";
}

export function PitchBulletCards({ bullets, className, tone = "neutral" }: PitchBulletCardsProps) {
  return (
    <ul className={cn("m-0 grid list-none gap-2 p-0", className)}>
      {bullets.map((bullet, index) => (
        <li
          key={`${bullet}-${index}`}
          className={cn(
            "pitch-focus-ring pitch-neon-edge rounded-[var(--pitch-radius-md)] border px-3 py-2 text-sm leading-6 text-[color:var(--pitch-ink)] transition-transform hover:-translate-y-[1px]",
            toneClass(tone)
          )}
          tabIndex={0}
        >
          {bullet}
        </li>
      ))}
    </ul>
  );
}
