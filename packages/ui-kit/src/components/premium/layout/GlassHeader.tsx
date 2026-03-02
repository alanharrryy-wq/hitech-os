import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "../../../lib/cn.js";

export interface GlassHeaderProps extends Omit<HTMLAttributes<HTMLDivElement>, "title"> {
  readonly title: ReactNode;
  readonly kicker?: ReactNode;
  readonly description?: ReactNode;
  readonly actions?: ReactNode;
}

export function GlassHeader({
  className,
  title,
  kicker,
  description,
  actions,
  ...props
}: GlassHeaderProps) {
  return (
    <header className={cn("ui-glass-header", className)} {...props}>
      <div>
        {kicker ? <p className="ui-glass-header__kicker">{kicker}</p> : null}
        <h2 className="ui-glass-header__title">{title}</h2>
        {description ? <p className="ui-glass-header__description">{description}</p> : null}
      </div>
      {actions ? <div>{actions}</div> : null}
    </header>
  );
}
