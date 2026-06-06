import type { ReactNode } from "react";
import styles from "./license-ui.module.css";

export function LicenseWarningBadge({ children }: { children: ReactNode }) {
  return <span className={`${styles.warningBadge} ${styles.warn}`}>{children}</span>;
}
