import type { PropsWithChildren } from "react";

export interface CardProps {
  title?: string;
  subtitle?: string;
}

export function Card({ children, title, subtitle }: PropsWithChildren<CardProps>) {
  return (
    <article className="ui-card">
      {(title || subtitle) && (
        <header className="ui-card__header">
          {title ? <h3 className="ui-card__title">{title}</h3> : null}
          {subtitle ? <p className="ui-card__subtitle">{subtitle}</p> : null}
        </header>
      )}
      <div className="ui-card__content">{children}</div>
    </article>
  );
}
