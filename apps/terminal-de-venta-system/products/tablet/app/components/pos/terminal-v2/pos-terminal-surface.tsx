"use client";

import type { ReactNode } from "react";
import styles from "./pos-terminal-surface.module.css";

export function PosTerminalSurface({ children, cartState, paymentOpen, visualState }: { children: ReactNode; cartState: string; paymentOpen: boolean; visualState: string }) {
  return (
    <div
      className={styles.surface}
      data-prisma-component="PosTerminalSurface"
      data-prisma-surface-component="PosTerminalSurface"
      data-prisma-panel="tablet.pos.terminal-nocturne-reference"
      data-prisma-surface="tablet"
      data-prisma-route="/pos"
      data-prisma-layer="surface"
      data-prisma-effect="nocturne-translucent-canvas"
      data-prisma-cart-state={cartState}
      data-prisma-payment-open={paymentOpen ? "true" : "false"}
      data-prisma-visual-state={visualState}
      data-prisma-canonical-pos="nocturne-reference-1607"

      data-surface="tablet"
      data-screen="pos"
      data-zone="terminal-shell"
      data-panel="pos-terminal-surface"
      data-target="pos-terminal-surface"
      data-kind="background"
      data-role="visual-backplane">
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
    <header className={styles.header} data-prisma-component="PosTerminalHeader" data-prisma-layer="context"
      data-surface="tablet"
      data-screen="pos"
      data-zone="terminal-header"
      data-panel="pos-terminal-header"
      data-target="pos-terminal-header"
      data-kind="background"
      data-role="visual-backplane">
      <span
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="pos-terminal-surface"
        data-target="pos-terminal-surface-panel-58"
        data-kind="panel"
        data-role="revenue-core"
      >{storeName}</span>
      <strong
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="pos-terminal-surface"
        data-target="pos-terminal-surface-panel-59"
        data-kind="panel"
        data-role="revenue-core"
      >{statusLabel}</strong>
      <small>{terminalName} · {cartQty} pzas · {cartTotal} · {activeCount} activos</small>
    </header>
  );
}

export function PosProductCanvas({ children }: { children: ReactNode }) {
  return (
    <section className={styles.canvas} data-prisma-component="PosProductCanvas" data-prisma-layer="content"
      data-surface="tablet"
      data-screen="pos"
      data-zone="product-grid"
      data-panel="pos-product-canvas"
      data-target="pos-product-canvas"
      data-kind="layout"
      data-role="product-canvas">
      {children}
    </section>
  );
}

export function PosTicketRail({ children }: { children: ReactNode }) {
  return (
    <aside className={styles.ticketRail} data-prisma-component="PosTicketRail" data-prisma-layer="ticket"
      data-surface="tablet"
      data-screen="pos"
      data-zone="checkout-rail"
      data-panel="pos-ticket-rail"
      data-target="pos-ticket-rail"
      data-kind="panel"
      data-role="sale-ticket">
      {children}
    </aside>
  );
}

export function PosCommandDock({ children }: { children: ReactNode }) {
  return (
    <nav className={styles.commandDock} data-prisma-component="PosCommandDock" data-prisma-layer="filter-dock" aria-label="Categorías y comandos de venta"
      data-surface="tablet"
      data-screen="pos"
      data-zone="command-dock"
      data-panel="pos-command-dock"
      data-target="pos-command-dock"
      data-kind="layout"
      data-role="navigation">
      <div className={styles.commandDockInner}
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="pos-terminal-surface"
        data-target="pos-terminal-surface-panel-105"
        data-kind="panel"
        data-role="revenue-core"
      >{children}</div>
    </nav>
  );
}

export function PosTerminalBody({ children }: { children: ReactNode }) {
  return <div className={styles.body}
     data-surface="tablet"
     data-screen="pos"
     data-zone="terminal-body"
     data-panel="pos-terminal-body"
     data-target="pos-terminal-body"
     data-kind="layout"
     data-role="layout">{children}</div>;
}
