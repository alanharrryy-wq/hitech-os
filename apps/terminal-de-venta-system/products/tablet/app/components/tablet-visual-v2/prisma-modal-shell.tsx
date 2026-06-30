"use client";

import type { MutableRefObject, ReactNode } from "react";
import styles from "./prisma-modal-shell.module.css";

type PrismaModalShellProps = {
  children: ReactNode;
  className?: string;
  onOverlayMouseDown?: (event: any) => void;
  panelRef?: MutableRefObject<HTMLElement | null>;
  [key: string]: any;
};

export function PrismaModalShell({ children, className, onOverlayMouseDown, panelRef, ...props }: PrismaModalShellProps) {
  const panelClasses = className ? `${styles.panel} ${className}` : styles.panel;

  return (
    <section
      data-prisma-cobro-portal="visual-surface-v2-2406"
      data-prisma-panel="tablet.pos.cobro-visual-v2"
      data-prisma-surface="tablet"
      data-prisma-route="/pos"
      data-prisma-zone="tablet-pos-cobro-modal"
      data-prisma-overlay-root="document-body"
      data-prisma-payment-modal="true"
      data-prisma-qa="tablet-qa-cobro-visual-v2"
      data-prisma-layer="modalBackdrop"
      data-prisma-effect="modal-depth-dim focus-halo"
      className={styles.overlay}
      onMouseDown={onOverlayMouseDown}
      role="presentation"
    >
      <span className={styles.atmosphere} aria-hidden="true" />
      <article {...props} ref={panelRef} className={panelClasses} data-prisma-layer="modal" data-prisma-effect="softglass-surface modal-depth-dim focus-halo">
        {children}
      </article>
    </section>
  );
}
