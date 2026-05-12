"use client";

import { PrismaEChart } from "@prisma-charts/PrismaEChart";
import type { IncidentSparkCard, PrismaChartQuality } from "@prisma-charts/prismaChartContracts";
import { incidentSparkOption } from "@prisma-charts/prismaChartOptions";
import { MobileChartCard } from "./MobileChartCard";
import styles from "../prisma-mobile-command.module.css";

export function MobileIncidentSparkCards({ data, quality, onFocusLabel }: { data: IncidentSparkCard[]; quality: PrismaChartQuality; onFocusLabel: (label: string) => void }) {
  return (
    <MobileChartCard title="Incident Spark Cards" subtitle="Microtendencias activas" quality={quality}>
      <div className={styles.sparkGrid}>
        {data.length === 0 ? (
          <div className={styles.emptySpark}>No hay incidentes con evidencia suficiente</div>
        ) : data.map((incident) => (
          <article className={styles.sparkCard} key={incident.incidentId}>
            <header>
              <strong>{incident.title}</strong>
              <span>{incident.severity}</span>
            </header>
            <PrismaEChart option={incidentSparkOption(incident)} renderer="svg" height={78} label={`Incident ${incident.incidentId}`} description={`Microtrend de incidente ${incident.title}.`} onFocusLabel={onFocusLabel} />
            <small>{incident.recommendedNextAction}</small>
          </article>
        ))}
      </div>
    </MobileChartCard>
  );
}
