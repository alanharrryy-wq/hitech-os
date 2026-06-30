import type { ReactNode } from "react";
import styles from "./prisma-status-chip.module.css";

type PrismaStatusChipProps = {
  children: ReactNode;
  className?: string;
  icon?: ReactNode;
  tone?: "neutral" | "success" | "warning" | "danger";
  [key: string]: any;
};

export function PrismaStatusChip({ children, className, icon, tone = "neutral", ...props }: PrismaStatusChipProps) {
  const classes = className ? `${styles.chip} ${className}` : styles.chip;

  return (
    <span {...props} className={classes} data-prisma-component="PrismaStatusChip" data-prisma-effect="selected-pulse" data-tone={tone}>
      {icon ? <span aria-hidden="true">{icon}</span> : null}
      {children}
    </span>
  );
}
