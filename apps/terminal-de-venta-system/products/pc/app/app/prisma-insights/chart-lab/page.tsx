import { prismaChartAtlas } from "@prisma-charts/prismaChartAtlas";
import { resolvePrismaChartFlags } from "@prisma-charts/prismaChartFlags";
import styles from "../prisma-pc-insights.module.css";

type SearchParams = Record<string, string | string[] | undefined>;

export const dynamic = "force-dynamic";

export const metadata = {
  title: "PRISMA Chart Lab",
  description: "Inspector preview para atlas, pasaportes, recetas y metadata ChartOps."
};

export default async function PrismaChartLabPage({ searchParams }: { searchParams?: Promise<SearchParams> | SearchParams }) {
  const resolvedSearchParams = searchParams ? await searchParams : {};
  const flags = resolvePrismaChartFlags("pc", resolvedSearchParams);
  const grouped = prismaChartAtlas.reduce<Record<string, typeof prismaChartAtlas>>((memo, chart) => {
    memo[chart.surface] = memo[chart.surface] ?? [];
    memo[chart.surface].push(chart);
    return memo;
  }, {});

  if (!flags.enabled) {
    return (
      <main className={styles.shell} data-prisma-chart-lab="disabled">
        <section className={styles.disabledPanel}>
          <p className={styles.eyebrow}>PRISMA Chart Lab</p>
          <h1>Inspector apagado</h1>
          <p>{flags.reason}</p>
          <span>Use <strong>?preview=charts</strong> para abrir el laboratorio sin activar produccion.</span>
        </section>
      </main>
    );
  }

  return (
    <main className={styles.shell} data-prisma-chart-lab="enabled">
      <section className={styles.hero}>
        <div>
          <p className={styles.eyebrow}>ChartOps</p>
          <h1>PRISMA Chart Lab</h1>
          <p>Inspector de las 14 graficas: pasaporte, fuente, contrato, adapter, mock, receta visual y estados soportados.</p>
        </div>
        <aside className={styles.telemetry} aria-label="Resumen Chart Lab">
          <span>Atlas activo</span>
          <strong>{prismaChartAtlas.length} charts</strong>
          <small>Feature flags siguen apagados por defecto.</small>
        </aside>
      </section>

      {(["pc", "tablet", "mobile"] as const).map((surface) => (
        <section className={styles.grid} aria-label={`Charts ${surface}`} key={surface} style={{ marginBottom: 18 }}>
          {(grouped[surface] ?? []).map((chart) => (
            <article className={styles.card} key={chart.chartId} data-chart-id={chart.chartId}>
              <header className={styles.cardHeader}>
                <div>
                  <span>{chart.surface} / {chart.family}</span>
                  <h2>{chart.displayName}</h2>
                </div>
                <small>{chart.status}</small>
              </header>
              <div>
                <p><strong>chartId:</strong> {chart.chartId}</p>
                <p><strong>Pregunta:</strong> {chart.questionAnswered}</p>
                <p><strong>Componente:</strong> {chart.componentFile}</p>
                <p><strong>Adapter:</strong> {chart.adapterName}</p>
                <p><strong>Contrato:</strong> {chart.contractType}</p>
                <p><strong>Mock:</strong> {chart.mockName}</p>
                <p><strong>Recipe:</strong> {chart.visualRecipe}</p>
                <p><strong>States:</strong> {chart.states.join(", ")}</p>
              </div>
              <footer className={styles.cardFooter}>
                <span>{chart.routePreview}</span>
                <span>{chart.visualKnobs.length} knobs</span>
              </footer>
            </article>
          ))}
        </section>
      ))}
    </main>
  );
}
