import type { CSSProperties } from "react";
import styles from "./PrismaComponents.module.css";
import type { PrismaBaseProps } from "./types";
import { cx } from "./types";
type Props = PrismaBaseProps<HTMLDivElement> & { imageVar?: string };
export function PrismaBackgroundLayer({ surface = "tablet", imageVar = "--prisma-bg-image-tablet", className, ...rest }: Props) { return <div aria-hidden="true" data-prisma-component="PrismaBackgroundLayer" data-surface={surface} className={cx(styles.backgroundLayer, className)} {...rest}><div className={styles.backgroundImage} style={{ "--prisma-background-image": `var(${imageVar})` } as CSSProperties} /><div className={styles.backgroundVeil} /></div>; }
