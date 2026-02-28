import type { DoubleEngineViewModel } from '../../lib/pitch';
import styles from './DoubleEnginePanel.module.css';

export interface DoubleEnginePanelProps {
  readonly model: DoubleEngineViewModel;
}

export function DoubleEnginePanel({ model }: DoubleEnginePanelProps) {
  return (
    <section className={styles.root} aria-label="Double engine data panel">
      <article className={styles.card}>
        <h3 className={styles.cardTitle}>Engine Capability Matrix</h3>
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th scope="col">Engine</th>
                <th scope="col">Profile</th>
                <th scope="col">Fit</th>
                <th scope="col">Opex</th>
                <th scope="col">Throughput</th>
                <th scope="col">Risk</th>
                <th scope="col">Protocol</th>
                <th scope="col">Max Input</th>
              </tr>
            </thead>
            <tbody>
              {model.engines.map((engine) => (
                <tr key={engine.id}>
                  <th scope="row">{engine.name}</th>
                  <td>{engine.profile}</td>
                  <td>{engine.fitScore}</td>
                  <td>{engine.opexIndex}</td>
                  <td>{engine.throughputIndex}</td>
                  <td>{engine.riskIndex}</td>
                  <td>{engine.capabilities.protocolVersion}</td>
                  <td>{engine.capabilities.maxInputChars.toLocaleString('en-US')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>

      <article className={styles.card}>
        <h3 className={styles.cardTitle}>Strategy Narrative</h3>
        <ul className={styles.narrative}>
          {model.strategyNarrative.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
      </article>

      <article className={styles.card}>
        <h3 className={styles.cardTitle}>KPI Band Tracker</h3>
        <div className={styles.bandGrid}>
          {model.kpiBands.map((band) => (
            <div key={band.id} className={styles.bandItem}>
              <p className={styles.bandLabel}>{band.label}</p>
              <p className={styles.bandValues}>
                current {band.current} / target {band.target} / gap {band.gap}
              </p>
              <progress
                className={styles.progress}
                max={Math.max(100, band.target)}
                value={band.current}
                aria-label={`${band.label} progress`}
              />
            </div>
          ))}
        </div>
      </article>
    </section>
  );
}

export default DoubleEnginePanel;
