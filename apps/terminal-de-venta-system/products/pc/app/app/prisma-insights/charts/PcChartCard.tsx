import type { ReactNode } from "react";
import type { PrismaChartQuality } from "@prisma-charts/prismaChartContracts";
import { formatPercent } from "@prisma-charts/prismaChartFormatters";
import styles from "../prisma-pc-insights.module.css";

export function ChartCard({ title, kicker, quality, wide, children }: { title: string; kicker: string; quality: PrismaChartQuality; wide?: boolean; children: ReactNode }) {
  return (
    <article className={`${styles.card} ${wide ? styles.wideCard : ""}`}>
      <header className={styles.cardHeader}>
        <div>
          <span>{kicker}</span>
          <h2>{title}</h2>
        </div>
        <small>{formatPercent(quality.confidence.score)}</small>
      </header>
      <div className={styles.chartFrame}>{children}</div>
      <footer className={styles.cardFooter}>
        <span>{quality.sourceLabel}</span>
        <span>{quality.dataStatus} / {quality.confidence.level}</span>
      </footer>
    </article>
  );
}
