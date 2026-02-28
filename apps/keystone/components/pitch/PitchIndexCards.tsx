import Link from 'next/link';
import type { PitchIndexViewModel } from '../../lib/pitch';
import styles from './PitchIndexCards.module.css';

export interface PitchIndexCardsProps {
  readonly model: PitchIndexViewModel;
}

export function PitchIndexCards({ model }: PitchIndexCardsProps) {
  return (
    <section className={styles.root} aria-label="Pitch chapter links">
      {model.routeCards.map((card) => (
        <Link key={card.id} href={card.href} className={styles.card}>
          <p className={styles.order}>Chapter {card.order}</p>
          <h3 className={styles.title}>{card.title}</h3>
          <p className={styles.subtitle}>{card.subtitle}</p>
        </Link>
      ))}
    </section>
  );
}

export default PitchIndexCards;
