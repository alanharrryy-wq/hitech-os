import PrismaStudioProQaClient from "./PrismaStudioProQaClient";
import { PrismaTabletShellUnified } from "@components/tablet-shell/prisma-tablet-shell";
import { TabletReportSurfaceV2 } from "@components/tablet-visual-v2";
import styles from "./prisma-studio-pro-qa.module.css";

export const metadata = {
  title: "PRISMA Studio Pro QA",
  description: "Consola flotante pro con recetas, score visual, snapshots y publish gate para PRISMA Visual OS."
};

export default function VisualOsPage() {
  return (
    <PrismaTabletShellUnified
      currentPath="/visual-os"
      title="Visual OS"
      subtitle="Consola de calibración visual Tablet con recetas, score y publicación controlada."
      kicker="Visual OS"
    >
      <TabletReportSurfaceV2 routeId="/visual-os" title="Visual OS" description="Consola de calibración visual Tablet con recetas, score y publicación controlada." statusLabel="Studio">
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
      </TabletReportSurfaceV2>
    </PrismaTabletShellUnified>
  );
}
