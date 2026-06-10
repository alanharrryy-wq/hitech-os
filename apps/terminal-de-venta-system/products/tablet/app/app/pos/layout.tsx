import type { ReactNode } from "react";
import styles from "./prisma-pos-light-safe-shell.module.css";

const PILOT_MARKER = "PRISMA_POS_LIGHT_SAFE_SHELL_PILOT_07";

export default function PosLightSafeShellLayout({ children }: { children: ReactNode }) {
  return (
    <section className={styles.shell} data-prisma-pos-light-safe-shell={PILOT_MARKER}
      data-prisma-background="tablet-background-active">
      <div className={styles.content}>{children}</div>
    </section>
  );
}
