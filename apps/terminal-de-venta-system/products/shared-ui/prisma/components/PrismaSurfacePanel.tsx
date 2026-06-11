import styles from "./PrismaComponents.module.css";
import type { PrismaBaseProps } from "./types";
import { cx } from "./types";
export function PrismaSurfacePanel({ surface = "tablet", tone = "default", title, eyebrow, children, className, ...rest }: PrismaBaseProps<HTMLElement>) { return <section data-prisma-component="PrismaSurfacePanel" data-surface={surface} data-tone={tone} className={cx(styles.surfacePanel, styles.stack, className)} {...rest}>{eyebrow ? <p className={styles.cardMeta}>{eyebrow}</p> : null}{title ? <h2 className={styles.cardTitle}>{title}</h2> : null}{children}</section>; }
