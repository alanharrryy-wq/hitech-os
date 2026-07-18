import type { ReactNode } from "react";

type SectionCardProps = {
  title: string;
  subtitle?: string;
  children: ReactNode;
  eyebrow?: string;
  className?: string;
};

function joinClasses(...classes: Array<string | undefined>) {
  return classes.filter(Boolean).join(" ");
}

export function SectionCard({
  title,
  subtitle,
  children,
  eyebrow = "Módulo",
  className
}: SectionCardProps) {
  return (
    <section
      className={joinClasses("card", "pc-foundation-card", className)}
      data-prisma-component="SectionCard"
      data-material="translucent"
    >
      <div className="section-head pc-foundation-card__header">
        <div>
          <div className="kicker pc-foundation-card__eyebrow">{eyebrow}</div>
          <h2 className="section-title pc-foundation-card__title">{title}</h2>
          {subtitle ? <p className="section-copy pc-foundation-card__subtitle">{subtitle}</p> : null}
        </div>
      </div>
      <div className="pc-foundation-card__body">{children}</div>
    </section>
  );
}
