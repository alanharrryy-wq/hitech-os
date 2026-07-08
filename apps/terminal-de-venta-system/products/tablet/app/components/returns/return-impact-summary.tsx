import { formatMoney } from "@/lib/pos/cart-state";
import type { ReturnPolicyDecision } from "@/lib/returns-contextual/return-policy-engine";
import styles from "./returns.module.css";

export function ReturnImpactSummary({ decision }: { decision: ReturnPolicyDecision }) {
  return (
    <aside className={styles.panel} aria-label="Impacto de devolución"
      data-surface="tablet"
      data-screen="returns"
      data-zone="checkout"
      data-panel="return-impact-summary"
      data-target="return-impact-summary-impacto-de-devoluci-n-7"
      data-kind="panel"
      data-role="revenue-core"
    >
      <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="return_impact_summary" data-target="return-impact-summary-span-1" data-kind="text" data-role="text">Importe a devolver</span>
      <strong
        data-surface="tablet"
        data-screen="returns"
        data-zone="checkout"
        data-panel="return-impact-summary"
        data-target="return-impact-summary-element-9"
        data-kind="element"
        data-role="revenue-core"
      >{formatMoney(decision.amountCents)}</strong>
      <small>{decision.totalQty} piezas seleccionadas</small>
      {decision.blockingReasons.length ? <ul
        data-surface="tablet"
        data-screen="returns"
        data-zone="checkout"
        data-panel="return-impact-summary"
        data-target="return-impact-summary-element-11"
        data-kind="element"
        data-role="revenue-core"
      >{decision.blockingReasons.map(reason => <li data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="return_impact_summary" data-target="return-impact-summary-li-2" data-kind="panel" data-role="panel" key={reason}>{reason}</li>)}</ul> : null}
      {decision.warnings.length ? <ul
        data-surface="tablet"
        data-screen="returns"
        data-zone="checkout"
        data-panel="return-impact-summary"
        data-target="return-impact-summary-element-12"
        data-kind="element"
        data-role="revenue-core"
      >{decision.warnings.map(warning => <li key={warning}
        data-surface="tablet"
        data-screen="returns"
        data-zone="checkout"
        data-panel="return-impact-summary"
        data-target="return-impact-summary-badge-12"
        data-kind="badge"
        data-role="state-feedback"
      >{warning}</li>)}</ul> : null}
    </aside>
  );
}
