import styles from "./license-ui.module.css";

export function LicenseBlockedCard({ title, reason }: { title: string; reason: string }) {
  return (
    <section className={styles.blockedCard}>
      <p className={styles.eyebrow}>Licencia</p>
      <h2 className={styles.sectionTitle}>{title}</h2>
      <p className={styles.copy}>{reason}</p>
      <p className={styles.helper}>La administración de la licencia debe realizarla el administrador fuera de esta Tablet.</p>
    </section>
  );
}
