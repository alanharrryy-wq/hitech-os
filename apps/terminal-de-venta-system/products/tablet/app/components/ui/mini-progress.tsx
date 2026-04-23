import { cn } from "@/lib/utils";

export function MiniProgress({
  label,
  value,
  note,
  tone = "ok",
}: {
  label: string;
  value: number;
  note?: string;
  tone?: "ok" | "warn" | "danger";
}) {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <div className="mini-progress">
      <div className="mini-progress-head">
        <strong>{label}</strong>
        <span>{clamped}%</span>
      </div>
      <div className="mini-progress-track">
        <div className={cn("mini-progress-fill", `tone-${tone}`)} style={{ width: `${clamped}%` }} />
      </div>
      {note ? <div className="subtle">{note}</div> : null}
    </div>
  );
}
