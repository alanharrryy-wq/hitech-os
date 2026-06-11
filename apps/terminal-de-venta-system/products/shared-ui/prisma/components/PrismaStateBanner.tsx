import styles from "./PrismaComponents.module.css";
import type { PrismaBaseProps } from "./types";
import { cx } from "./types";
export function PrismaStateBanner({ surface = "tablet", tone = "info", title, children, className, ...rest }: PrismaBaseProps<HTMLDivElement>) { return <div role="status" data-prisma-component="PrismaStateBanner" data-surface={surface} data-tone={tone} className={cx(styles.stateBanner, styles.stack, className)} {...rest}>{title ? <strong>{title}</strong> : null}{children ? <div>{children}</div> : null}</div>; }
