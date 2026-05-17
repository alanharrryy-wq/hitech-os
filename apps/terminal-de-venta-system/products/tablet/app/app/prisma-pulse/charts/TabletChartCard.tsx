import type { ReactNode } from "react";
import type { PrismaChartQuality } from "@prisma-charts/prismaChartContracts";
import { formatPercent } from "@prisma-charts/prismaChartFormatters";
import styles from "../prisma-tablet-pulse.module.css";

export function TabletChartCard({ title, subtitle, quality, children }: { title: string; subtitle: string; quality: PrismaChartQuality; children: ReactNode }) {
  return (
    <article className={styles.card}>
      <header>
        <div>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
        <strong>{formatPercent(quality.confidence.score)}</strong>
      </header>
      <div className={styles.chartFrame}>{children}</div>
      <footer>
        <span>{quality.dataStatus} / {quality.sourceLabel}. {quality.emptyState}</span>
      </footer>
    </article>
  );
}
