import type { ReactNode } from "react";

export function SectionCard({ title, subtitle, children }: { title: string; subtitle?: string; children: ReactNode }) {
  return (
    <section className="card">
      <div className="kicker">{title}</div>
      {subtitle ? <div className="subtle" style={{ marginTop: 6, marginBottom: 12 }}>{subtitle}</div> : null}
      {children}
    </section>
  );
}
