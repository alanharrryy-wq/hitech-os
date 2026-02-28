import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes, PropsWithChildren, ReactNode } from "react";
import { cn } from "../../lib/cn.js";

const panelVariants = cva("ui-panel", {
  variants: {
    elevated: {
      true: "",
      false: ""
    },
    muted: {
      true: "",
      false: ""
    }
  },
  defaultVariants: {
    elevated: false,
    muted: false
  }
});

export interface PanelProps
  extends PropsWithChildren,
    Omit<HTMLAttributes<HTMLDivElement>, "title">,
    VariantProps<typeof panelVariants> {
  readonly title?: ReactNode;
  readonly subtitle?: ReactNode;
  readonly description?: ReactNode;
  readonly footer?: ReactNode;
}

export function Panel({
  className,
  children,
  title,
  subtitle,
  description,
  footer,
  elevated,
  muted,
  ...props
}: PanelProps) {
  const resolvedDescription = description ?? subtitle;

  return (
    <section
      className={cn(panelVariants({ elevated, muted }), className)}
      data-elevated={elevated}
      data-muted={muted}
      {...props}
    >
      {title || resolvedDescription ? (
        <header className="ui-panel__header">
          {title ? <h2 className="ui-panel__title">{title}</h2> : null}
          {resolvedDescription ? (
            <p className="ui-panel__description">{resolvedDescription}</p>
          ) : null}
        </header>
      ) : null}
      <div className="ui-panel__body">{children}</div>
      {footer ? <footer className="ui-panel__footer">{footer}</footer> : null}
    </section>
  );
}
