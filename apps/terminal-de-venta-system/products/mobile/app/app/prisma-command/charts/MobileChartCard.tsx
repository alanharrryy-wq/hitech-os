import type { ReactNode } from "react";
import type { PrismaChartQuality } from "@prisma-charts/prismaChartContracts";
import { formatPercent } from "@prisma-charts/prismaChartFormatters";
import styles from "../prisma-mobile-command.module.css";

export function MobileChartCard({ title, subtitle, quality, children }: { title: string; subtitle: string; quality: PrismaChartQuality; children: ReactNode }) {
  return (
    <article className={styles.card}>
      <header className={styles.cardHeader}>
        <div>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
        <strong>{formatPercent(quality.confidence.score)}</strong>
      </header>
      <div className={styles.chartFrame}>{children}</div>
      <footer className={styles.cardFooter}>
        <span>{quality.sourceLabel}</span>
        <span>{quality.dataStatus} / {quality.confidence.level}</span>
      </footer>
    </article>
  );
}
