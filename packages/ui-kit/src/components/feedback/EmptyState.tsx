import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "../../lib/cn.js";

export interface EmptyStateProps extends Omit<HTMLAttributes<HTMLDivElement>, "title"> {
  readonly title: ReactNode;
  readonly description?: ReactNode;
  readonly action?: ReactNode;
  readonly className?: string;
}

export function EmptyState({ className, title, description, action, ...props }: EmptyStateProps) {
  return (
    <div className={cn("ui-empty", className)} {...props}>
      <div>
        <h3 className="ui-empty__title">{title}</h3>
        {description ? <p className="ui-empty__description">{description}</p> : null}
        {action ? <div className="mt-3">{action}</div> : null}
      </div>
    </div>
  );
}
