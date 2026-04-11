import { cn } from "@/lib/utils";

export interface DetailListItem {
  label: string;
  value: string;
  emphasis?: boolean;
}

export interface DetailListProps {
  items: readonly DetailListItem[];
  columns?: 1 | 2 | 3;
  dense?: boolean;
  className?: string;
}

export function DetailList({ items, columns = 2, dense = false, className }: DetailListProps) {
  if (items.length === 0) return null;

  return (
    <dl
      className={cn(
        "grid gap-2",
        columns === 1 ? "grid-cols-1" : columns === 2 ? "grid-cols-1 sm:grid-cols-2" : "grid-cols-1 sm:grid-cols-2 xl:grid-cols-3",
        className
      )}
    >
      {items.map((item) => (
        <div
          key={`${item.label}:${item.value}`}
          className={cn(
            "rounded-xl border border-white/8 bg-canvas/30",
            dense ? "px-3 py-2" : "px-3.5 py-3"
          )}
        >
          <dt className="text-[11px] uppercase tracking-[0.16em] text-muted">{item.label}</dt>
          <dd className={cn("mt-1 text-sm", item.emphasis ? "font-semibold text-text" : "text-text")}>{item.value}</dd>
        </div>
      ))}
    </dl>
  );
}
