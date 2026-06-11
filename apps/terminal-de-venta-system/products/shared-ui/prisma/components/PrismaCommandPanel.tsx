import styles from "./PrismaComponents.module.css";
import type { PrismaBaseProps } from "./types";
import { cx } from "./types";
export function PrismaCommandPanel({ surface = "pc", title = "Comando PRISMA", children, className, ...rest }: PrismaBaseProps<HTMLElement>) { return <section data-prisma-component="PrismaCommandPanel" data-surface={surface} className={cx(styles.commandPanel, styles.stack, className)} {...rest}><h2 className={styles.cardTitle}>{title}</h2>{children}</section>; }
