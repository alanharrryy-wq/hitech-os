import styles from "./sales.module.css";

export function SalesTicketStatusChip({ status }: { status: string }) {
  const normalized = status.toUpperCase();
  const label = normalized === "COMPLETED" ? "Cerrado" : normalized === "RETURNED" ? "Con devolución" : normalized === "CANCELLED" ? "Cancelado" : "Revisar";
  const tone = normalized === "COMPLETED" ? "ok" : normalized === "RETURNED" ? "warn" : "danger";
  return <span className={styles.statusChip} data-tone={tone}>{label}</span>;
}
