"use client";

import type { MutableRefObject, ReactNode } from "react";
import styles from "./prisma-modal-shell.module.css";

type PrismaModalShellProps = {
  children: ReactNode;
  className?: string;
  onOverlayMouseDown?: (event: any) => void;
  overlayClassName?: string;
  panelRef?: MutableRefObject<HTMLElement | null>;
  [key: string]: any;
};

export function PrismaModalShell({ children, className, onOverlayMouseDown, overlayClassName, panelRef, ...props }: PrismaModalShellProps) {
  const overlayClasses = overlayClassName ? `${styles.overlay} ${overlayClassName}` : styles.overlay;
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
      className={overlayClasses}
      onMouseDown={onOverlayMouseDown}
      role="presentation"
      data-surface="tablet"
      data-screen="visual_os"
      data-zone="checkout"
      data-panel="prisma-modal-shell"
      data-target="prisma-modal-shell-price-20"
      data-kind="price"
      data-role="financial-control"
    >
      <span className={styles.atmosphere} aria-hidden="true"
        data-surface="tablet"
        data-screen="visual_os"
        data-zone="pos"
        data-panel="prisma-modal-shell"
        data-target="prisma-modal-shell-panel-35"
        data-kind="panel"
        data-role="revenue-core"
      />
      <article {...props} ref={panelRef} className={panelClasses} data-prisma-layer="modal" data-prisma-effect="softglass-surface modal-depth-dim focus-halo"
        data-surface="tablet"
        data-screen="visual_os"
        data-zone="pos"
        data-panel="prisma-modal-shell"
        data-target="prisma-modal-shell-panel-36"
        data-kind="panel"
        data-role="revenue-core"
      >
        {children}
      </article>
    </section>
  );
}
