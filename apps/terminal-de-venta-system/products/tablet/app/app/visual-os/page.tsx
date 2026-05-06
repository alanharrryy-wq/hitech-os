import PrismaStudioProQaClient from "./PrismaStudioProQaClient";
import styles from "./prisma-studio-pro-qa.module.css";

export const metadata = {
  title: "PRISMA Studio Pro QA",
  description: "Consola flotante pro con recetas, score visual, snapshots y publish gate para PRISMA Visual OS."
};

export default function VisualOsPage() {
  return (
    <main className={styles.launcherPage} data-prisma-vos="studio-pro-qa" data-prisma-layer="shell">
      <section className={styles.heroCrystal} data-prisma-layer="content">
        <p className={styles.eyebrow}>PRISMA Visual OS · 00R/00S</p>
        <h1>Studio Pro + Live QA</h1>
        <p>
          Consola flotante y pop-out con recetas, mixer de presets, inspector de capas, score vivo, snapshots y publish gate. Hecho para calibrar PRISMA como cristal cortado, no como CSS aventado con cuchara.
        </p>
        <div className={styles.heroActions}>
          <a href="/visual-os/detached" target="_blank" rel="noreferrer">Abrir pop-out</a>
          <a href="/visual-os/realtime" target="_blank" rel="noreferrer">Abrir bridge</a>
          <a href="/visual-os/pro" target="_blank" rel="noreferrer">Modo pro aislado</a>
        </div>
      </section>
      <PrismaStudioProQaClient defaultDetached={false} />
    </main>
  );
}
