import "./DemoGlassCard.styles.css";
import type { ReactNode } from "react";

export interface DemoGlassCardProps {
  readonly title: string;
  readonly subtitle?: string;
  readonly children?: ReactNode;
}

export function DemoGlassCard(props: DemoGlassCardProps): JSX.Element {
  const { title, subtitle, children } = props;
  return (
    <section className="demoglasscard-root" data-component="DemoGlassCard">
      <header className="demoglasscard-header">
        <h3 className="demoglasscard-title">{title}</h3>
        {subtitle ? <p className="demoglasscard-subtitle">{subtitle}</p> : null}
      </header>
      <div className="demoglasscard-body">{children}</div>
    </section>
  );
}
