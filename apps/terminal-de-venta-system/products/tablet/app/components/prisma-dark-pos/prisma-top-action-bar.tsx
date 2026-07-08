"use client";

import { PrismaIcon } from "./prisma-dark-pos-icons";
import styles from "./prisma-dark-pos.module.css";

function emitTopAction(action: string) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent("prisma:pos-top-action", {
    detail: { action, source: "prisma-dark-pos-top-action-bar", ts: new Date().toISOString() }
  }));
}

export function PrismaTopActionBar() {
  return (
    <div className={styles.topActions} aria-label="Acciones de sesión" data-prisma-hardening="top-actions-260611"
      data-surface="tablet"
      data-screen="pos"
      data-zone="pos"
      data-panel="prisma-top-action-bar"
      data-target="prisma-top-action-bar-acciones-de-sesi-n-15"
      data-kind="button"
      data-role="action"
    >
      <button className={styles.iconButton} type="button" aria-label="Cambiar tema" onClick={() =
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="prisma-top-action-bar"
        data-target="prisma-top-action-bar-cambiar-tema-16"
        data-kind="button"
        data-role="action"
      > emitTopAction("theme") }>
        <PrismaIcon name="sun" size={20} />
      </button>
      <button className={styles.iconButtonBadge} type="button" aria-label="Notificaciones" onClick={() =
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="prisma-top-action-bar"
        data-target="prisma-top-action-bar-notificaciones-19"
        data-kind="button"
        data-role="action"
      > emitTopAction("notifications") }>
        <PrismaIcon name="bell" size={20} />
        <span
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="prisma-top-action-bar"
          data-target="prisma-top-action-bar-button-21"
          data-kind="button"
          data-role="action"
        >3</span>
      </button>
      <button className={styles.adminChip} type="button" onClick={() =
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="prisma-top-action-bar"
        data-target="prisma-top-action-bar-button-23"
        data-kind="button"
        data-role="action"
      > emitTopAction("profile") }>
        <span className={styles.adminAvatar}
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="prisma-top-action-bar"
          data-target="prisma-top-action-bar-button-24"
          data-kind="button"
          data-role="action"
        >AR</span>
        <span className={styles.adminMeta}
          data-surface="tablet"
          data-screen="pos"
          data-zone="pos"
          data-panel="prisma-top-action-bar"
          data-target="prisma-top-action-bar-button-25"
          data-kind="button"
          data-role="action"
        >
          <strong
            data-surface="tablet"
            data-screen="pos"
            data-zone="pos"
            data-panel="prisma-top-action-bar"
            data-target="prisma-top-action-bar-button-26"
            data-kind="button"
            data-role="action"
          >Administrador</strong>
          <small>Sucursal Centro</small>
        </span>
        <PrismaIcon name="chevron-down" size={15} />
      </button>
    </div>
  );
}
