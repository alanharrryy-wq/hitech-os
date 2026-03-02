import type { HTMLAttributes, PropsWithChildren, ReactNode } from "react";
import { cn } from "../../../lib/cn.js";

export interface GlassPanelProps
  extends PropsWithChildren,
    Omit<HTMLAttributes<HTMLDivElement>, "title"> {
  readonly title?: ReactNode;
  readonly description?: ReactNode;
  readonly kicker?: ReactNode;
  readonly actions?: ReactNode;
  readonly footer?: ReactNode;
  readonly materialClassName?: string;
}

export function GlassPanel({
  className,
  children,
  title,
  description,
  kicker,
  actions,
  footer,
  materialClassName,
  ...props
}: GlassPanelProps) {
  const hasHeader = title || description || kicker || actions;

  return (
    <section className={cn("ui-glass-panel ui-hitech-material", materialClassName, className)} {...props}>
      {hasHeader ? (
        <header className="ui-glass-header">
          <div>
            {kicker ? <p className="ui-glass-header__kicker">{kicker}</p> : null}
            {title ? <h2 className="ui-glass-header__title">{title}</h2> : null}
            {description ? <p className="ui-glass-header__description">{description}</p> : null}
          </div>
          {actions ? <div>{actions}</div> : null}
        </header>
      ) : null}
      <div className="p-4 sm:p-5">{children}</div>
      {footer ? (
        <footer className="border-t border-[rgba(2,167,202,0.24)] p-4 sm:p-5">{footer}</footer>
      ) : null}
    </section>
  );
}
