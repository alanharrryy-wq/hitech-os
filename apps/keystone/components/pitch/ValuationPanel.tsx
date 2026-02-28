import type { ValuationViewModel } from '../../lib/pitch';
import styles from './ValuationPanel.module.css';

export interface ValuationPanelProps {
  readonly model: ValuationViewModel;
}

function toCurrencyMillions(value: number): string {
  return `$${value.toFixed(1)}m`;
}

function toImpliedValue(multiple: number, runRate: number): string {
  return `$${(multiple * runRate).toFixed(1)}m`;
}

export function ValuationPanel({ model }: ValuationPanelProps) {
  return (
    <section className={styles.root} aria-label="Valuation panel">
      <article className={styles.card}>
        <h3 className={styles.cardTitle}>Contract Version</h3>
        <dl className={styles.versionGrid}>
          <div>
            <dt>Package</dt>
            <dd>{model.contractVersion.packageVersion}</dd>
          </div>
          <div>
            <dt>Protocol</dt>
            <dd>{model.contractVersion.protocolVersion}</dd>
          </div>
          <div>
            <dt>Schema File</dt>
            <dd>{model.contractVersion.schemaVersionFile}</dd>
          </div>
          <div>
            <dt>Generated</dt>
            <dd>{model.contractVersion.generatedAt}</dd>
          </div>
        </dl>
      </article>

      <article className={styles.card}>
        <h3 className={styles.cardTitle}>Scenario Board</h3>
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th scope="col">Scenario</th>
                <th scope="col">Multiple</th>
                <th scope="col">Run Rate</th>
                <th scope="col">Confidence</th>
                <th scope="col">Implied</th>
                <th scope="col">Flags</th>
              </tr>
            </thead>
            <tbody>
              {model.scenarios.map((scenario) => (
                <tr key={scenario.id}>
                  <th scope="row">{scenario.label}</th>
                  <td>{scenario.multiple.toFixed(2)}x</td>
                  <td>{toCurrencyMillions(scenario.revenueRunRateM)}</td>
                  <td>{scenario.confidence}%</td>
                  <td>{toImpliedValue(scenario.multiple, scenario.revenueRunRateM)}</td>
                  <td>
                    ai={scenario.flags.enableAiExecution ? '1' : '0'} · proxy=
                    {scenario.flags.enableCapabilitiesProxy ? '1' : '0'} · ui=
                    {scenario.flags.enableExperimentalUi ? '1' : '0'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>

      <article className={styles.card}>
        <h3 className={styles.cardTitle}>Bridge Series</h3>
        <div className={styles.bridgeGrid}>
          {model.bridgeSeries.map((step) => (
            <div key={step.id} className={styles.bridgeItem}>
              <p className={styles.bridgeStep}>{step.step}</p>
              <p className={step.deltaM >= 0 ? styles.bridgePositive : styles.bridgeNegative}>
                {step.deltaM >= 0 ? '+' : ''}
                {step.deltaM}m
              </p>
            </div>
          ))}
        </div>
      </article>

      <article className={styles.card}>
        <h3 className={styles.cardTitle}>Risk Notes</h3>
        <ul className={styles.risks}>
          {model.riskNotes.map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
      </article>
    </section>
  );
}

export default ValuationPanel;
