import { cn } from "@hitech/ui-kit";

export interface PitchMiniBarsSeries {
  readonly label: string;
  readonly value: number;
  readonly tone?: "teal" | "cyan" | "gold";
}

export interface PitchMiniBarsProps {
  readonly series: readonly PitchMiniBarsSeries[];
  readonly max?: number;
  readonly className?: string;
}

function toneClass(tone: PitchMiniBarsSeries["tone"]): string {
  if (tone === "teal") {
    return "bg-[linear-gradient(90deg,#026F86,#028EA7)]";
  }

  if (tone === "gold") {
    return "bg-[linear-gradient(90deg,#553E13,#AB7B26)]";
  }

  return "bg-[linear-gradient(90deg,#02A7CA,#026F86)]";
}

export function PitchMiniBars({ series, max, className }: PitchMiniBarsProps) {
  const upper = max ?? Math.max(...series.map((entry) => entry.value), 1);

  return (
    <ul className={cn("m-0 grid list-none gap-2 p-0", className)}>
      {series.map((entry) => {
        const width = Math.max(6, Math.round((entry.value / upper) * 100));

        return (
          <li key={entry.label} className="grid gap-1">
            <div className="flex items-center justify-between gap-2 text-xs">
              <span className="font-medium text-[color:rgba(4,18,25,0.76)]">{entry.label}</span>
              <span className="font-semibold text-[color:var(--pitch-ink)]">{entry.value}</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-[rgba(4,18,25,0.08)]">
              <span className={cn("block h-full rounded-full", toneClass(entry.tone))} style={{ width: `${width}%` }} />
            </div>
          </li>
        );
      })}
    </ul>
  );
}
