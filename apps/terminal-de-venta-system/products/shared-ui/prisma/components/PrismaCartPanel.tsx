import styles from "./PrismaComponents.module.css";
import type { PrismaBaseProps } from "./types";
import { cx } from "./types";
export function PrismaCartPanel({ surface = "tablet", title = "Carrito", children, className, ...rest }: PrismaBaseProps<HTMLElement>) { return <aside data-prisma-component="PrismaCartPanel" data-surface={surface} className={cx(styles.cartPanel, styles.stack, className)} {...rest}><h2 className={styles.cardTitle}>{title}</h2>{children}</aside>; }
