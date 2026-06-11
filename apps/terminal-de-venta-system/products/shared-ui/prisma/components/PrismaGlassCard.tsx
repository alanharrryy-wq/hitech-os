import styles from "./PrismaComponents.module.css";
import type { PrismaBaseProps } from "./types";
import { cx } from "./types";
export function PrismaGlassCard({ surface = "tablet", tone = "default", title, eyebrow, children, className, ...rest }: PrismaBaseProps<HTMLElement>) { return <article data-prisma-component="PrismaGlassCard" data-surface={surface} data-tone={tone} className={cx(styles.glassCard, styles.stack, className)} {...rest}>{eyebrow ? <p className={styles.cardMeta}>{eyebrow}</p> : null}{title ? <h3 className={styles.cardTitle}>{title}</h3> : null}{children}</article>; }
