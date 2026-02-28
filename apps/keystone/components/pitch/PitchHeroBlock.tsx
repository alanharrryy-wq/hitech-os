import styles from './PitchHeroBlock.module.css';

export interface PitchHeroBlockProps {
  readonly eyebrow: string;
  readonly title: string;
  readonly subtitle: string;
  readonly bullets: ReadonlyArray<string>;
}

export function PitchHeroBlock({ eyebrow, title, subtitle, bullets }: PitchHeroBlockProps) {
  return (
    <section className={styles.root} aria-label={title}>
      <div className={styles.primary}>
        <p className={styles.eyebrow}>{eyebrow}</p>
        <h2 className={styles.title}>{title}</h2>
        <p className={styles.subtitle}>{subtitle}</p>
      </div>
      <ul className={styles.bullets}>
        {bullets.map((bullet) => (
          <li key={bullet}>{bullet}</li>
        ))}
      </ul>
    </section>
  );
}

export default PitchHeroBlock;
