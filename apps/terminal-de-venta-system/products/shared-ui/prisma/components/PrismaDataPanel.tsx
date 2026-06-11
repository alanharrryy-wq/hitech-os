import styles from "./PrismaComponents.module.css";
import type { PrismaBaseProps } from "./types";
import { cx } from "./types";
export function PrismaDataPanel({ surface = "pc", title, eyebrow, children, className, ...rest }: PrismaBaseProps<HTMLElement>) { return <section data-prisma-component="PrismaDataPanel" data-surface={surface} className={cx(styles.dataPanel, styles.stack, className)} {...rest}>{eyebrow ? <p className={styles.cardMeta}>{eyebrow}</p> : null}{title ? <h2 className={styles.cardTitle}>{title}</h2> : null}{children}</section>; }
