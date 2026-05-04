import type { PosVisibleError } from "@/lib/pos/payment-error-normalizer";
import { normalizePosError } from "@/lib/pos/payment-error-normalizer";
import styles from "./pos.module.css";

export function PosPaymentRiskBanner({ error }: { error: unknown }) {
  if (!error) return null;
  const visible: PosVisibleError = normalizePosError(error);
  return (
    <div className={styles.paymentError} data-severity={visible.severity}>
      <strong>{visible.title}</strong>
      <span>{visible.message}</span>
      <small>{visible.operatorAction}</small>
    </div>
  );
}
