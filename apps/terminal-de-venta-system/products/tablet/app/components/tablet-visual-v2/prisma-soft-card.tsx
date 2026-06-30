import type { ReactNode } from "react";
import styles from "./prisma-soft-card.module.css";

type PrismaSoftCardProps = {
  as?: "article" | "aside" | "div" | "section";
  children: ReactNode;
  className?: string;
  tone?: "default" | "amount" | "warning" | "selected";
  [key: string]: any;
};

export function PrismaSoftCard({ as: Component = "section", children, className, tone = "default", ...props }: PrismaSoftCardProps) {
  const classes = className ? `${styles.card} ${className}` : styles.card;

  return (
    <Component {...props} className={classes} data-prisma-component="PrismaSoftCard" data-prisma-effect="softglass-surface inner-highlight rim-light" data-tone={tone}>
      {children}
    </Component>
  );
}
