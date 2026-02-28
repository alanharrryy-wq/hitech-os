import type { IndustrialFlowViewModel } from '../../lib/pitch';
import styles from './IndustrialFlowPanel.module.css';

export interface IndustrialFlowPanelProps {
  readonly model: IndustrialFlowViewModel;
}

export function IndustrialFlowPanel({ model }: IndustrialFlowPanelProps) {
  return (
    <section className={styles.root} aria-label="Industrial flow panel">
      <article className={styles.card}>
        <h3 className={styles.cardTitle}>Flow Metrics</h3>
        <div className={styles.metricsGrid}>
          {model.flowMetrics.map((metric) => (
            <div key={metric.id} className={styles.metricItem}>
              <p className={styles.metricName}>{metric.name}</p>
              <p className={styles.metricValue}>
                {metric.value}
                <span className={styles.metricUnit}> {metric.unit}</span>
              </p>
            </div>
          ))}
        </div>
      </article>

      <article className={styles.card}>
        <h3 className={styles.cardTitle}>Stage Board</h3>
        <div className={styles.stageGrid}>
          {model.stages.map((stage) => (
            <section key={stage.id} className={styles.stageCard}>
              <header className={styles.stageHeader}>
                <h4 className={styles.stageName}>{stage.name}</h4>
                <p className={styles.stageMeta}>owner {stage.owner} · sla {stage.targetSlaHours}h</p>
              </header>
              <p className={styles.stageCounts}>
                requests {stage.requests.length} · results {stage.results.length}
              </p>
              <ul className={styles.blockers}>
                {stage.blockers.map((blocker) => (
                  <li key={blocker}>{blocker}</li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      </article>

      <article className={styles.card}>
        <h3 className={styles.cardTitle}>Process Guardrails</h3>
        <ul className={styles.guardrails}>
          {model.processGuardrails.map((guardrail) => (
            <li key={guardrail}>{guardrail}</li>
          ))}
        </ul>
      </article>
    </section>
  );
}

export default IndustrialFlowPanel;
