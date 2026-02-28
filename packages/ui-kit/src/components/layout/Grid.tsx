import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes, PropsWithChildren } from "react";
import { cn } from "../../lib/cn.js";

const gridVariants = cva("ui-grid", {
  variants: {
    gap: {
      sm: "",
      md: "",
      lg: ""
    }
  },
  defaultVariants: {
    gap: "md"
  }
});

export interface GridProps
  extends PropsWithChildren,
    HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof gridVariants> {
  readonly cols?: number;
}

export interface GridItemProps extends PropsWithChildren, HTMLAttributes<HTMLDivElement> {
  readonly span?: number;
  readonly spanSm?: number;
  readonly spanMd?: number;
  readonly spanLg?: number;
  readonly spanXl?: number;
}

function clampSpan(span: number | undefined): number | undefined {
  if (span === undefined) {
    return undefined;
  }
  return Math.min(12, Math.max(1, span));
}

export function Grid({ className, children, cols = 12, gap, style, ...props }: GridProps) {
  return (
    <div
      className={cn(
        gridVariants({ gap }),
        cols <= 12 ? `grid-cols-${cols}` : "grid-cols-12",
        className
      )}
      style={{
        ...style,
        ["--ui-grid-cols" as string]: String(cols)
      }}
      data-gap={gap}
      {...props}
    >
      {children}
    </div>
  );
}

export function GridItem({
  className,
  children,
  span,
  spanSm,
  spanMd,
  spanLg,
  spanXl,
  ...props
}: GridItemProps) {
  const resolvedSpan = clampSpan(span) ?? 12;
  const resolvedSpanSm = clampSpan(spanSm);
  const resolvedSpanMd = clampSpan(spanMd);
  const resolvedSpanLg = clampSpan(spanLg);
  const resolvedSpanXl = clampSpan(spanXl);

  return (
    <div
      className={cn("ui-grid__item", className)}
      style={{
        ["--ui-grid-span" as string]: String(resolvedSpan),
        ["--ui-grid-span-sm" as string]:
          resolvedSpanSm !== undefined ? String(resolvedSpanSm) : undefined,
        ["--ui-grid-span-md" as string]:
          resolvedSpanMd !== undefined ? String(resolvedSpanMd) : undefined,
        ["--ui-grid-span-lg" as string]:
          resolvedSpanLg !== undefined ? String(resolvedSpanLg) : undefined,
        ["--ui-grid-span-xl" as string]:
          resolvedSpanXl !== undefined ? String(resolvedSpanXl) : undefined
      }}
      {...props}
    >
      {children}
    </div>
  );
}
