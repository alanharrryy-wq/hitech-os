import PrismaStudioProQaClient from "../PrismaStudioProQaClient";
import { PrismaTabletShellUnified } from "@components/tablet-shell/prisma-tablet-shell";
import { TabletReportSurfaceV2 } from "@components/tablet-visual-v2";
import styles from "../prisma-studio-pro-qa.module.css";

export const metadata = {
  title: "PRISMA Studio Pro Detached",
  description: "Ventana separada del PRISMA Studio Pro QA 00R/00S."
};

export default function DetachedVisualOsPage() {
  return (
    <PrismaTabletShellUnified
      currentPath="/visual-os/detached"
      title="Studio separado"
      subtitle="Ventana aislada para calibración visual avanzada."
      kicker="Visual OS"
    >
      <TabletReportSurfaceV2 routeId="/visual-os/detached" title="Studio separado" description="Ventana aislada para calibración visual avanzada." statusLabel="Detached">
        <main className={styles.detachedPage} data-prisma-vos="studio-pro-detached" data-prisma-layer="shell">
          <PrismaStudioProQaClient defaultDetached={true} />
        </main>
      </TabletReportSurfaceV2>
    </PrismaTabletShellUnified>
  );
}
