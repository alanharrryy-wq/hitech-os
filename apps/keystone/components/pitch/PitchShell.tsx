import Link from 'next/link';
import type { PropsWithChildren, ReactNode } from 'react';
import type { PitchRouteNavigation } from '../../lib/pitch';
import styles from './PitchShell.module.css';

export interface PitchShellProps {
  readonly title: string;
  readonly subtitle: string;
  readonly navigation: PitchRouteNavigation;
  readonly queryPills?: ReactNode;
  readonly debugPanel?: ReactNode;
}

export function PitchShell({
  title,
  subtitle,
  navigation,
  queryPills,
  debugPanel,
  children,
}: PropsWithChildren<PitchShellProps>) {
  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.headerBody}>
          <p className={styles.eyebrow}>Keystone Pitch</p>
          <h1 className={styles.title}>{title}</h1>
          <p className={styles.subtitle}>{subtitle}</p>
        </div>
        {queryPills ? <div className={styles.queryWrap}>{queryPills}</div> : null}
      </header>

      <nav className={styles.rail} aria-label="Pitch route rail">
        {navigation.items.map((item) => (
          <Link
            key={item.id}
            href={item.href}
            className={item.isCurrent ? styles.railItemCurrent : styles.railItem}
            aria-current={item.isCurrent ? 'page' : undefined}
          >
            <span className={styles.railTitle}>{item.title}</span>
            <span className={styles.railSubtitle}>{item.subtitle}</span>
          </Link>
        ))}
      </nav>

      <main className={styles.main}>{children}</main>

      <footer className={styles.footer}>
        <div className={styles.footerControls}>
          {navigation.prev ? (
            <Link href={navigation.prev.href} className={styles.footerLink}>
              ← {navigation.prev.title}
            </Link>
          ) : (
            <span className={styles.footerPlaceholder}>Start</span>
          )}

          {navigation.next ? (
            <Link href={navigation.next.href} className={styles.footerLink}>
              {navigation.next.title} →
            </Link>
          ) : (
            <span className={styles.footerPlaceholder}>End</span>
          )}
        </div>
        {debugPanel ? <div className={styles.debugSlot}>{debugPanel}</div> : null}
      </footer>
    </div>
  );
}

export default PitchShell;
