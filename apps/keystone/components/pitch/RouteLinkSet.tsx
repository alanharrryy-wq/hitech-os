import Link from 'next/link';
import type { PitchRouteNavigation } from '../../lib/pitch';
import styles from './RouteLinkSet.module.css';

export interface RouteLinkSetProps {
  readonly navigation: PitchRouteNavigation;
  readonly examples: ReadonlyArray<{
    readonly id: string;
    readonly label: string;
    readonly href: string;
  }>;
}

export function RouteLinkSet({ navigation, examples }: RouteLinkSetProps) {
  return (
    <section className={styles.root} aria-label="Route links">
      <article className={styles.block}>
        <h3 className={styles.title}>Prev / Next</h3>
        <div className={styles.navGrid}>
          {navigation.prev ? (
            <Link className={styles.link} href={navigation.prev.href}>
              ← {navigation.prev.title}
            </Link>
          ) : (
            <span className={styles.placeholder}>No previous route</span>
          )}

          {navigation.next ? (
            <Link className={styles.link} href={navigation.next.href}>
              {navigation.next.title} →
            </Link>
          ) : (
            <span className={styles.placeholder}>No next route</span>
          )}
        </div>
      </article>

      <article className={styles.block}>
        <h3 className={styles.title}>Query Presets</h3>
        <div className={styles.exampleGrid}>
          {examples.map((example) => (
            <Link key={example.id} className={styles.link} href={example.href}>
              {example.label}
            </Link>
          ))}
        </div>
      </article>
    </section>
  );
}

export default RouteLinkSet;
