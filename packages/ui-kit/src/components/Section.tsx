import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes, PropsWithChildren, ReactNode } from "react";
import { cn } from "../lib/cn.js";

const sectionVariants = cva("space-y-2", {
  variants: {
    tone: {
      default: "",
      muted: "text-[hsl(var(--ui-text-3))]"
    }
  },
  defaultVariants: {
    tone: "default"
  }
});

export interface SectionProps
  extends PropsWithChildren,
    Omit<HTMLAttributes<HTMLElement>, "title">,
    VariantProps<typeof sectionVariants> {
  readonly as?: "section" | "article" | "div";
  readonly heading?: ReactNode;
  readonly description?: ReactNode;
  readonly className?: string;
  readonly children?: React.ReactNode;
}

export function Section({
  as = "section",
  className,
  children,
  tone,
  heading,
  description,
  ...props
}: SectionProps) {
  const Comp = as;

  return (
    <Comp className={cn(sectionVariants({ tone }), className)} {...props}>
      {heading ? (
        <h2 className="m-0 text-xl font-semibold tracking-tight text-[hsl(var(--ui-text-1))]">
          {heading}
        </h2>
      ) : null}
      {description ? (
        <p className="m-0 text-sm text-[hsl(var(--ui-text-3))]">{description}</p>
      ) : null}
      {children}
    </Comp>
  );
}
