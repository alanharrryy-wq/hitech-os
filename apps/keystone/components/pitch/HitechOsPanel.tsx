import type { HitechOsViewModel } from '../../lib/pitch';
import styles from './HitechOsPanel.module.css';

export interface HitechOsPanelProps {
  readonly model: HitechOsViewModel;
}

export function HitechOsPanel({ model }: HitechOsPanelProps) {
  return (
    <section className={styles.root} aria-label="Hitech OS panel">
      <article className={styles.card}>
        <h3 className={styles.cardTitle}>Contract Registry</h3>
        <ul className={styles.contracts}>
          {model.contracts.map((contract) => (
            <li key={contract}>{contract}</li>
          ))}
        </ul>
      </article>

      <article className={styles.card}>
        <h3 className={styles.cardTitle}>Module Map</h3>
        <div className={styles.moduleGrid}>
          {model.modules.map((module) => (
            <section key={module.id} className={styles.moduleCard}>
              <header className={styles.moduleHeader}>
                <h4 className={styles.moduleLabel}>{module.label}</h4>
                <p className={styles.moduleOwner}>owner {module.owner}</p>
                <p className={styles.moduleHealth}>
                  health {module.health.status} · checks {module.health.checks.length}
                </p>
              </header>

              <div className={styles.ioGrid}>
                <div>
                  <h5>Inputs</h5>
                  <ul>
                    {module.inputs.map((input) => (
                      <li key={input}>{input}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h5>Outputs</h5>
                  <ul>
                    {module.outputs.map((output) => (
                      <li key={output}>{output}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div>
                <h5>Safeguards</h5>
                <ul className={styles.safeguards}>
                  {module.safeguards.map((safeguard) => (
                    <li key={safeguard}>{safeguard}</li>
                  ))}
                </ul>
              </div>
            </section>
          ))}
        </div>
      </article>

      <article className={styles.card}>
        <h3 className={styles.cardTitle}>Reliability Narrative</h3>
        <ul className={styles.narrative}>
          {model.reliabilityNarrative.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </article>
    </section>
  );
}

export default HitechOsPanel;
