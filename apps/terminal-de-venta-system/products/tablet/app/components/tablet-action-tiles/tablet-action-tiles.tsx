"use client";

import type { ReactNode } from "react";
import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import type { PrismaIconName } from "@components/prisma-dark-pos/prisma-dark-pos-data";
import styles from "./tablet-action-tiles.module.css";

export type QuickActionTone =
  | "primary"
  | "inventory"
  | "success"
  | "warning"
  | "dangerQuiet"
  | "jewel"
  | "sync"
  | "license"
  | "neutral";

export type QuickActionTileProps = {
  title: string;
  description: string;
  actionLabel?: string;
  icon?: PrismaIconName;
  tone?: QuickActionTone;
  href?: string;
  onClick?: () => void;
  disabled?: boolean;
  deferredReason?: string;
  owner?: string;
  kind?: string;
  controls?: string;
  children?: ReactNode;
};

function cx(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

function tileClassName(tone: QuickActionTone, disabled: boolean) {
  return cx(styles.tile, styles[`tone_${tone}`], disabled && styles.disabled);
}

function TileContent({
  title,
  description,
  actionLabel,
  icon,
  deferredReason,
  children
}: Pick<QuickActionTileProps, "title" | "description" | "actionLabel" | "icon" | "deferredReason" | "children">) {
  return (
    <>
      <span className={styles.icon} aria-hidden="true">
        {icon ? <PrismaIcon name={icon} size={22} /> : null}
      </span>
      <span className={styles.copy}>
        <strong>{title}</strong>
        <small>{deferredReason ?? description}</small>
        {children ? <span className={styles.extra}>{children}</span> : null}
      </span>
      <span className={styles.action}>{deferredReason ? "Pendiente" : actionLabel ?? "Abrir"}</span>
    </>
  );
}

export function QuickActionTile({
  title,
  description,
  actionLabel,
  icon = "sparkle",
  tone = "neutral",
  href,
  onClick,
  disabled = false,
  deferredReason,
  owner,
  kind = "surface-action",
  controls,
  children
}: QuickActionTileProps) {
  const isDeferred = Boolean(deferredReason);
  const state = isDeferred ? "deferred" : disabled ? "disabled" : "active";
  const commonProps = {
    className: tileClassName(tone, disabled || isDeferred),
    "data-quick-create-tile": title,
    "data-tile-state": state,
    "data-action-kind": kind,
    "data-action-owner": owner ?? "tablet",
    "data-action-target": href ?? (onClick ? "handler" : "none")
  };

  if (href && !disabled && !isDeferred) {
    return (
      <a {...commonProps} href={href} aria-describedby={controls}>
        <TileContent title={title} description={description} actionLabel={actionLabel} icon={icon} deferredReason={deferredReason}>
          {children}
        </TileContent>
      </a>
    );
  }

  if (onClick && !isDeferred) {
    return (
      <button {...commonProps} type="button" onClick={onClick} disabled={disabled} aria-controls={controls}>
        <TileContent title={title} description={description} actionLabel={actionLabel} icon={icon} deferredReason={deferredReason}>
          {children}
        </TileContent>
      </button>
    );
  }

  return (
    <span {...commonProps} aria-disabled="true" role="note">
      <TileContent title={title} description={description} actionLabel={actionLabel} icon={icon} deferredReason={deferredReason}>
        {children}
      </TileContent>
    </span>
  );
}

export function QuickActionGrid({
  label,
  children,
  density = "standard"
}: {
  label: string;
  children: ReactNode;
  density?: "compact" | "standard" | "wide";
}) {
  return (
    <section className={styles.gridShell} aria-label={label} data-quick-create-surface={label} data-density={density}>
      {children}
    </section>
  );
}

export function QuickActionStrip({ label, children }: { label: string; children: ReactNode }) {
  return (
    <section className={styles.strip} aria-label={label} data-quick-create-surface={label}>
      {children}
    </section>
  );
}
