import type { PitchQueryState } from '../../lib/pitch';
import styles from './PitchQueryPills.module.css';

export interface PitchQueryPillsProps {
  readonly query: PitchQueryState;
}

export function PitchQueryPills({ query }: PitchQueryPillsProps) {
  return (
    <div className={styles.root} role="status" aria-label="Query state">
      <span className={styles.pill}>layers={query.layers}</span>
      <span className={styles.pill}>layerProfile={query.layerProfile}</span>
      <span className={styles.pill}>debug={query.debug}</span>
    </div>
  );
}

export default PitchQueryPills;
