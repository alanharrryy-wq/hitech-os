import styles from "./license-ui.module.css";

export function LicenseGateBanner({ message }: { message: string }) {
  return (
    <div className={styles.gateBanner} role="status">
      <strong>Revisión de licencia</strong>
      <p className={styles.copy}>{message}</p>
    </div>
  );
}
