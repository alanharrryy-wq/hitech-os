import styles from "./PrismaComponents.module.css";
import type { PrismaActionButtonProps } from "./types";
import { cx } from "./types";
export function PrismaActionButton({ href, surface = "tablet", tone = "default", children, className, ...rest }: PrismaActionButtonProps) { if (href) return <a data-prisma-component="PrismaActionButton" data-surface={surface} data-tone={tone} href={href} className={cx(styles.actionButton, className)} {...rest}>{children}</a>; return <button data-prisma-component="PrismaActionButton" data-surface={surface} data-tone={tone} className={cx(styles.actionButton, className)} {...rest}>{children}</button>; }
