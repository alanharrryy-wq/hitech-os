import type { ReactNode } from "react";

export function SectionCard({ title, subtitle, children }: { title: string; subtitle?: string; children: ReactNode }) {
  return (
    <section className="card">
      <div className="section-head">
        <div>
          <div className="kicker">Módulo</div>
          <h2 className="section-title">{title}</h2>
          {subtitle ? <div className="section-copy" style={{ marginTop: 8 }}>{subtitle}</div> : null}
        </div>
      </div>
      {children}
    </section>
  );
}
