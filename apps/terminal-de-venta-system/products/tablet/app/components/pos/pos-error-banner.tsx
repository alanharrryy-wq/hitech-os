import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import { friendlyPosError } from "@/lib/pos/pos-visible-errors";
import styles from "./pos.module.css";

export function PosErrorBanner({ error }: { error: unknown }) {
  if (!error) return null;
  return (
    <div className={styles.errorBanner} role="alert" data-prisma-zone="tablet-pos-error-state" data-prisma-role="status-surface" data-prisma-state="error" data-prisma-motion="error-feedback">
      <PrismaIcon name="bell" size={18} />
      <span>{friendlyPosError(error)}</span>
    </div>
  );
}
