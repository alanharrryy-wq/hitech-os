import type { ReactNode } from "react";

export function InsightChartFrame({
  title,
  reading,
  action,
  source,
  children,
}: {
  title: string;
  reading: string;
  action?: string;
  source?: string;
  children: ReactNode;
}) {
  return (
    <section className="prisma-insight-chart-frame" data-prisma-panel-role="chart-insight">
      <header>
        <div>
          <h2>{title}</h2>
          <p>{reading}</p>
        </div>
        {source && <span className="prisma-source-pill">Fuente: {source}</span>}
      </header>
      <div className="prisma-chart-canvas">{children}</div>
      {action && <p className="prisma-chart-action">Acción sugerida: {action}</p>}
    </section>
  );
}
