import styles from "./PrismaComponents.module.css";
import type { PrismaBaseProps } from "./types";
import { cx } from "./types";
export function PrismaShellFrame({ surface = "tablet", tone = "default", children, className, ...rest }: PrismaBaseProps<HTMLDivElement>) { return <div data-prisma-component="PrismaShellFrame" data-surface={surface} data-tone={tone} className={cx(styles.prismaRoot, styles.shellFrame, className)} {...rest}>{children}</div>; }
