import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes, PropsWithChildren, ReactNode } from "react";
import { cn } from "../../lib/cn.js";

const shellVariants = cva("ui-shell", {
  variants: {
    width: {
      default: "",
      tight: ""
    }
  },
  defaultVariants: {
    width: "default"
  }
});

export interface ShellProps
  extends PropsWithChildren,
    Omit<HTMLAttributes<HTMLDivElement>, "title">,
    VariantProps<typeof shellVariants> {
  readonly title?: ReactNode;
  readonly subtitle?: ReactNode;
  readonly actions?: ReactNode;
  readonly className?: string;
  readonly children?: React.ReactNode;
}

export function Shell({
  className,
  children,
  title,
  subtitle,
  actions,
  width,
  ...props
}: ShellProps) {
  return (
    <section
      className={cn(shellVariants({ width }), className)}
      data-tight={width === "tight"}
      {...props}
    >
      {title || subtitle || actions ? (
        <header className="ui-shell__header">
          <div>
            {title ? <h1 className="ui-shell__title">{title}</h1> : null}
            {subtitle ? <p className="ui-shell__subtitle">{subtitle}</p> : null}
          </div>
          {actions ? <div>{actions}</div> : null}
        </header>
      ) : null}
      {children}
    </section>
  );
}
