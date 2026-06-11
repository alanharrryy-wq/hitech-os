import styles from "./PrismaComponents.module.css";
import type { PrismaBaseProps } from "./types";
import { cx } from "./types";
export function PrismaRouteFrame({ surface = "tablet", tone = "default", children, className, ...rest }: PrismaBaseProps<HTMLElement>) { return <main data-prisma-component="PrismaRouteFrame" data-surface={surface} data-tone={tone} className={cx(styles.prismaRoot, styles.routeFrame, styles.stack, className)} {...rest}>{children}</main>; }
