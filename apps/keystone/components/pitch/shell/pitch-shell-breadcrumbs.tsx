import Link from "next/link";
import { cn } from "@hitech/ui-kit";

export interface PitchShellBreadcrumbsProps {
  readonly items: ReadonlyArray<{
    readonly label: string;
    readonly href?: string;
  }>;
  readonly className?: string;
}

export function PitchShellBreadcrumbs({ items, className }: PitchShellBreadcrumbsProps) {
  return (
    <nav className={cn("flex flex-wrap items-center gap-2 text-xs", className)} aria-label="Breadcrumb">
      {items.map((item, index) => {
        const isLast = index === items.length - 1;

        return (
          <span key={`${item.label}-${index}`} className="inline-flex items-center gap-2">
            {item.href && !isLast ? (
              <Link
                href={item.href}
                className="pitch-focus-ring rounded-md px-1.5 py-0.5 text-[color:var(--pitch-deep-teal)] no-underline hover:underline"
              >
                {item.label}
              </Link>
            ) : (
              <span className="rounded-md px-1.5 py-0.5 text-[color:var(--pitch-ink)]">{item.label}</span>
            )}
            {!isLast ? <span className="text-[color:rgba(4,18,25,0.45)]">/</span> : null}
          </span>
        );
      })}
    </nav>
  );
}
