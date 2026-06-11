import type { ReactNode } from "react";
import styles from "./prisma-checkout-light-safe-shell.module.css";

const PILOT_MARKER = "PRISMA_CHECKOUT_LIGHT_SAFE_SHELL_PILOT_08";

export default function CheckoutLightSafeShellLayout({ children }: { children: ReactNode }) {
  return (
    <section className={styles.shell} data-prisma-checkout-light-safe-shell={PILOT_MARKER}
      data-prisma-background="tablet-background-active">
      <div className={styles.content}>{children}</div>
    </section>
  );
}
