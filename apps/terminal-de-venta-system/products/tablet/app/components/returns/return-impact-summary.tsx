import { formatMoney } from "@/lib/pos/cart-state";
import type { ReturnPolicyDecision } from "@/lib/returns-contextual/return-policy-engine";
import styles from "./returns.module.css";

export function ReturnImpactSummary({ decision }: { decision: ReturnPolicyDecision }) {
  return (
    <aside className={styles.panel} aria-label="Impacto de devolución">
      <span>Importe a devolver</span>
      <strong>{formatMoney(decision.amountCents)}</strong>
      <small>{decision.totalQty} piezas seleccionadas</small>
      {decision.blockingReasons.length ? <ul>{decision.blockingReasons.map(reason => <li key={reason}>{reason}</li>)}</ul> : null}
      {decision.warnings.length ? <ul>{decision.warnings.map(warning => <li key={warning}>{warning}</li>)}</ul> : null}
    </aside>
  );
}
