"use client";

import type { ReactNode } from "react";
import styles from "./prisma-liquid-action.module.css";

type PrismaLiquidActionProps = {
  amount?: ReactNode;
  children: ReactNode;
  className?: string;
  disabled?: boolean;
  fullWidth?: boolean;
  icon?: ReactNode;
  sublabel?: ReactNode;
  status?: "ready" | "loading" | "disabled" | "success";
  type?: "button" | "submit" | "reset";
  variant?: "primary" | "secondary" | "success";
  [key: string]: any;
};

export function PrismaLiquidAction({
  amount,
  children,
  className,
  disabled,
  fullWidth,
  icon,
  status,
  sublabel,
  type = "button",
  variant = "primary",
  ...props
}: PrismaLiquidActionProps) {
  const resolvedStatus = disabled ? "disabled" : status ?? "ready";
  const classes = className ? `${styles.action} ${className}` : styles.action;

  return (
    <button
      {...props}
      type={type}
      disabled={disabled}
      className={classes}
      data-prisma-component="PrismaLiquidAction"
      data-prisma-effect="liquid-glow pressed-depth rim-light success-sweep disabled-frost focus-halo"
      data-status={resolvedStatus}
      data-variant={variant}
      data-full-width={fullWidth ? "true" : undefined}
    >
      {icon ? <span className={styles.icon} aria-hidden="true">{icon}</span> : null}
      <span className={styles.label}>
        <strong>{children}</strong>
        {sublabel ? <small>{sublabel}</small> : null}
      </span>
      {amount ? <span className={styles.amount}>{amount}</span> : null}
    </button>
  );
}
