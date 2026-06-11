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
    <div className={styles.topActions} aria-label="Acciones de sesión" data-prisma-hardening="top-actions-260611">
      <button className={styles.iconButton} type="button" aria-label="Cambiar tema" onClick={() => emitTopAction("theme") }>
        <PrismaIcon name="sun" size={20} />
      </button>
      <button className={styles.iconButtonBadge} type="button" aria-label="Notificaciones" onClick={() => emitTopAction("notifications") }>
        <PrismaIcon name="bell" size={20} />
        <span>3</span>
      </button>
      <button className={styles.adminChip} type="button" onClick={() => emitTopAction("profile") }>
        <span className={styles.adminAvatar}>AR</span>
        <span className={styles.adminMeta}>
          <strong>Administrador</strong>
          <small>Sucursal Centro</small>
        </span>
        <PrismaIcon name="chevron-down" size={15} />
      </button>
    </div>
  );
}
