import type { PosVisibleError } from "@/lib/pos/payment-error-normalizer";
import { normalizePosError } from "@/lib/pos/payment-error-normalizer";
import styles from "./pos.module.css";

export function PosPaymentRiskBanner({ error }: { error: unknown }) {
  if (!error) return null;
  const visible: PosVisibleError = normalizePosError(error);
  return (
    <div className={styles.paymentError} data-severity={visible.severity}
      data-surface="tablet"
      data-screen="pos"
      data-zone="checkout-risk"
      data-panel="pos-payment-risk-banner"
      data-target="pos-payment-risk-banner"
      data-kind="panel"
      data-role="status-alert">
      <strong
        data-surface="tablet"
        data-screen="pos"
        data-zone="checkout"
        data-panel="pos-payment-risk-banner"
        data-target="pos-payment-risk-banner-price-17"
        data-kind="price"
        data-role="financial-control"
      >{visible.title}</strong>
      <span
        data-surface="tablet"
        data-screen="pos"
        data-zone="checkout"
        data-panel="pos-payment-risk-banner"
        data-target="pos-payment-risk-banner-price-18"
        data-kind="price"
        data-role="financial-control"
      >{visible.message}</span>
      <small>{visible.operatorAction}</small>
    </div>
  );
}
