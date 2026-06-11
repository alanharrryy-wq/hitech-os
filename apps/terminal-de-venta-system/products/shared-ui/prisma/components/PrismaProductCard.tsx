import styles from "./PrismaComponents.module.css";
import type { PrismaBaseProps } from "./types";
import { cx } from "./types";
type Props = PrismaBaseProps<HTMLElement> & { name?: string; sku?: string; price?: string; stockLabel?: string };
export function PrismaProductCard({ surface = "tablet", name, sku, price, stockLabel, children, className, ...rest }: Props) { return <article data-prisma-component="PrismaProductCard" data-surface={surface} className={cx(styles.productCard, styles.stack, className)} {...rest}><h3 className={styles.cardTitle}>{name ?? "Producto PRISMA"}</h3>{sku ? <p className={styles.cardMeta}>SKU {sku}</p> : null}{price ? <p className={styles.cardValue}>{price}</p> : null}{stockLabel ? <p className={styles.cardMeta}>{stockLabel}</p> : null}{children}</article>; }
