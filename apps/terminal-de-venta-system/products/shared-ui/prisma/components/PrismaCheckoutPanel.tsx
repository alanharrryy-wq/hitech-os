import styles from "./PrismaComponents.module.css";
import type { PrismaBaseProps } from "./types";
import { cx } from "./types";
export function PrismaCheckoutPanel({ surface = "tablet", title = "Cobro", children, className, ...rest }: PrismaBaseProps<HTMLElement>) { return <section data-prisma-component="PrismaCheckoutPanel" data-surface={surface} className={cx(styles.checkoutPanel, styles.stack, className)} {...rest}><h2 className={styles.cardTitle}>{title}</h2>{children}</section>; }
