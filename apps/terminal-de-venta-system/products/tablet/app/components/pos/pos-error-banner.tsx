import { PrismaIcon } from "@generated/prisma-visual-runtime/prisma-icon";
import { friendlyPosError } from "@/lib/pos/pos-visible-errors";
import styles from "./pos.module.css";

export function PosErrorBanner({ error }: { error: unknown }) {
  if (!error) return null;
  return (
    <div className={styles.errorBanner} role="alert" data-prisma-zone="tablet-pos-error-state" data-prisma-role="status-surface" data-prisma-state="error" data-prisma-motion="error-feedback"
      data-surface="tablet"
      data-screen="pos"
      data-zone="pos-error-state"
      data-panel="pos-error-banner"
      data-target="pos-error-banner"
      data-kind="panel"
      data-role="status-alert">
      <PrismaIcon name="bell" size={18} />
      <span
        data-surface="tablet"
        data-screen="pos"
        data-zone="pos"
        data-panel="pos-error-banner"
        data-target="pos-error-banner-badge-17"
        data-kind="badge"
        data-role="state-feedback"
      >{friendlyPosError(error)}</span>
    </div>
  );
}
