import styles from "./catalog.module.css";

type Props = {
  value: string;
  onChange: (value: string) => void;
};

export function CatalogStockField({ value, onChange }: Props) {
  const parsed = Number.parseInt(value || "0", 10);
  const tone = parsed <= 0 ? styles.stockDanger : parsed <= 5 ? styles.stockWarn : styles.stockOk;
  return (
    <label className={styles.field}>
      <span>Existencia actual</span>
      <input value={value} onChange={(event) => onChange(event.target.value)} type="number" min="0" step="1" />
      <small className={tone}>{parsed <= 0 ? "Sin existencias." : parsed <= 5 ? "Existencia baja." : "Existencia suficiente."}</small>
    </label>
  );
}
