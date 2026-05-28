import type { ReactNode } from "react";
import styles from "../prisma-mobile-thin-mist-shell.module.css";

const PILOT_MARKER = "PRISMA_MOBILE_SUPERVISOR_THIN_MIST_SHELL_PILOT_09";

export default function MobileThinMistRouteLayout({ children }: { children: ReactNode }) {
  return (
    <section className={styles.shell} data-prisma-mobile-thin-mist-shell={PILOT_MARKER} data-prisma-mobile-route="/prisma-app">
      <div className={styles.content}>{children}</div>
    </section>
  );
}
