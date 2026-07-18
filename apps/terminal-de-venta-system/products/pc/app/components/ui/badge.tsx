import type { ComponentPropsWithoutRef, ReactNode } from "react";

export type BadgeTone = "ok" | "warn" | "danger";

type BadgeProps = Omit<ComponentPropsWithoutRef<"span">, "children"> & {
  tone: BadgeTone;
  children: ReactNode;
};

function joinClasses(...classes: Array<string | undefined>) {
  return classes.filter(Boolean).join(" ");
}

export function Badge({ tone, children, className, ...props }: BadgeProps) {
  return (
    <span
      {...props}
      className={joinClasses("badge", tone, "pc-foundation-badge", `pc-foundation-badge--${tone}`, className)}
      data-prisma-component="Badge"
      data-status-tone={tone}
    >
      {children}
    </span>
  );
}
