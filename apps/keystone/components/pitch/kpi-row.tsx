import { cn } from "@hitech/ui-kit";
import { KpiBig, type KpiBigProps } from "./kpi-big";

export interface KpiRowProps {
  readonly items: readonly KpiBigProps[];
  readonly className?: string;
}

export function KpiRow({ items, className }: KpiRowProps) {
  return (
    <div
      className={cn(
        "grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5",
        className
      )}
    >
      {items.map((item) => (
        <KpiBig key={`${item.label}:${item.value}`} {...item} />
      ))}
    </div>
  );
}
