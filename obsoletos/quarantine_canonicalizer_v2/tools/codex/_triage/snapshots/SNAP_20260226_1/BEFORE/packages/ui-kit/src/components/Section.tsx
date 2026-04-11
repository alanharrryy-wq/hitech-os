import type { PropsWithChildren } from "react";

export interface SectionProps {
  heading: string;
  description?: string;
}

export function Section({ children, heading, description }: PropsWithChildren<SectionProps>) {
  return (
    <section className="ui-section">
      <header className="ui-section__header">
        <h2 className="ui-section__heading">{heading}</h2>
        {description ? <p className="ui-section__description">{description}</p> : null}
      </header>
      <div className="ui-section__content">{children}</div>
    </section>
  );
}
