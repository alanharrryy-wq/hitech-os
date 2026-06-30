"use client";

import type { ReactNode } from "react";
import styles from "./pos-terminal-surface.module.css";

export function PosTerminalSurface({ children, cartState, paymentOpen, visualState }: { children: ReactNode; cartState: string; paymentOpen: boolean; visualState: string }) {
  return (
    <div
      className={styles.surface}
      data-prisma-component="PosTerminalSurface"
      data-prisma-surface-component="PosTerminalSurface"
      data-prisma-panel="tablet.pos.terminal-softglass-reference"
      data-prisma-surface="tablet"
      data-prisma-route="/pos"
      data-prisma-layer="surface"
      data-prisma-effect="softglass-reference-canvas"
      data-prisma-cart-state={cartState}
      data-prisma-payment-open={paymentOpen ? "true" : "false"}
      data-prisma-visual-state={visualState}
      data-prisma-canonical-pos="softglass-reference-2606"
    >
      {children}
    </div>
  );
}

export function PosTerminalHeader({
  activeCount,
  cartQty,
  cartTotal,
  statusLabel,
  storeName,
  terminalName
}: {
  activeCount: number;
  cartQty: number;
  cartTotal: string;
  statusLabel: string;
  storeName: string;
  terminalName: string;
}) {
  return (
    <header className={styles.header} data-prisma-component="PosTerminalHeader" data-prisma-layer="context">
      <span>{storeName}</span>
      <strong>{statusLabel}</strong>
      <small>{terminalName} · {cartQty} pzas · {cartTotal} · {activeCount} activos</small>
    </header>
  );
}

export function PosProductCanvas({ children }: { children: ReactNode }) {
  return (
    <section className={styles.canvas} data-prisma-component="PosProductCanvas" data-prisma-layer="content">
      {children}
    </section>
  );
}

export function PosTicketRail({ children }: { children: ReactNode }) {
  return (
    <aside className={styles.ticketRail} data-prisma-component="PosTicketRail" data-prisma-layer="ticket">
      {children}
    </aside>
  );
}

export function PosCommandDock({ children }: { children: ReactNode }) {
  return (
    <nav className={styles.commandDock} data-prisma-component="PosCommandDock" data-prisma-layer="filter-dock" aria-label="Categorías y comandos de venta">
      <div className={styles.commandDockInner}>{children}</div>
    </nav>
  );
}

export function PosTerminalBody({ children }: { children: ReactNode }) {
  return <div className={styles.body}>{children}</div>;
}
