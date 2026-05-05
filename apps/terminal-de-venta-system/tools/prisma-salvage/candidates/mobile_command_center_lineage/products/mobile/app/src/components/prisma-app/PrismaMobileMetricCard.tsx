import type { PrismaMobileKpi } from "@/lib/prisma-app/prisma-app-api-contracts";
import styles from "./prisma-mobile-dashboard.module.css";

const metricToneClass: Record<PrismaMobileKpi["tone"], string> = {
  gold: styles.metricGold,
  green: styles.metricGreen,
  blue: styles.metricBlue,
  red: styles.metricRed,
  neutral: styles.metricNeutral
};

export function PrismaMobileMetricCard({ metric }: { metric: PrismaMobileKpi }) {
  return (
    <article className={`${styles.metricCard} ${metricToneClass[metric.tone]}`}>
      <span>{metric.label}</span>
      <strong>{metric.value}</strong>
      <small>{metric.note}</small>
    </article>
  );
}
