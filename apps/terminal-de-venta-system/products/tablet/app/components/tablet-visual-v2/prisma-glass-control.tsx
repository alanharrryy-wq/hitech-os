"use client";

import type { ReactNode } from "react";
import styles from "./prisma-glass-control.module.css";

type PrismaGlassControlProps = {
  children: ReactNode;
  className?: string;
  hint?: ReactNode;
  icon?: ReactNode;
  label: ReactNode;
};

export function PrismaGlassControl({ children, className, hint, icon, label }: PrismaGlassControlProps) {
  const classes = className ? `${styles.control} ${className}` : styles.control;

  return (
    <label className={classes} data-prisma-component="PrismaGlassControl" data-prisma-effect="inner-highlight focus-halo">
      <span className={styles.controlText}>
        <span>{label}</span>
        {hint ? <span className={styles.hint}>{hint}</span> : null}
      </span>
      <span className={styles.frame}>
        {icon ? <span className={styles.icon} aria-hidden="true">{icon}</span> : null}
        {children}
      </span>
    </label>
  );
}
