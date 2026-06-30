import PrismaStudioProQaClient from "../PrismaStudioProQaClient";
import { PrismaTabletShellUnified } from "@components/tablet-shell/prisma-tablet-shell";
import { TabletReportSurfaceV2 } from "@components/tablet-visual-v2";
import styles from "../prisma-studio-pro-qa.module.css";

export const metadata = {
  title: "PRISMA Studio Pro Isolated",
  description: "Modo pro aislado del Live Studio para calibración visual avanzada."
};

export default function VisualOsProPage() {
  return (
    <PrismaTabletShellUnified
      currentPath="/visual-os/pro"
      title="Studio pro"
      subtitle="Modo aislado para calibración visual avanzada de Tablet."
      kicker="Visual OS"
    >
      <TabletReportSurfaceV2 routeId="/visual-os/pro" title="Studio pro" description="Modo aislado para calibración visual avanzada de Tablet." statusLabel="Pro">
        <main className={styles.detachedPage} data-prisma-vos="studio-pro-isolated" data-prisma-layer="shell">
          <PrismaStudioProQaClient defaultDetached={true} />
        </main>
      </TabletReportSurfaceV2>
    </PrismaTabletShellUnified>
  );
}
