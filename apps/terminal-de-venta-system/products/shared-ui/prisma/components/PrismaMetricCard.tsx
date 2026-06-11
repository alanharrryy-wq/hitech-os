import styles from "./PrismaComponents.module.css";
import type { PrismaBaseProps } from "./types";
import { cx } from "./types";
type Props = PrismaBaseProps<HTMLElement> & { label?: string; value?: string; delta?: string };
export function PrismaMetricCard({ surface = "pc", label, value, delta, children, className, ...rest }: Props) { return <article data-prisma-component="PrismaMetricCard" data-surface={surface} className={cx(styles.metricCard, styles.stack, className)} {...rest}>{label ? <p className={styles.cardMeta}>{label}</p> : null}{value ? <p className={styles.cardValue}>{value}</p> : null}{delta ? <p className={styles.cardMeta}>{delta}</p> : null}{children}</article>; }
