import PrismaRealtimeBridgeClient from "./PrismaRealtimeBridgeClient";
import { PrismaTabletShellUnified } from "@components/tablet-shell/prisma-tablet-shell";
import { TabletReportSurfaceV2 } from "@components/tablet-visual-v2";
import styles from "../prisma-studio-pro-qa.module.css";

export const metadata = {
  title: "PRISMA Studio Pro Bridge",
  description: "Cliente receptor SSE para validar cambios visuales realtime 00R/00S."
};

export default function RealtimeBridgePage() {
  return (
    <PrismaTabletShellUnified
      currentPath="/visual-os/realtime"
      title="Bridge visual"
      subtitle="Cliente receptor de cambios visuales realtime para calibración controlada."
      kicker="Visual OS"
    >
      <TabletReportSurfaceV2 routeId="/visual-os/realtime" title="Bridge visual" description="Cliente receptor de cambios visuales realtime para calibración controlada." statusLabel="Bridge">
        <main className={styles.bridgePage} data-prisma-vos="studio-pro-bridge" data-prisma-layer="shell">
          <PrismaRealtimeBridgeClient />
        </main>
      </TabletReportSurfaceV2>
    </PrismaTabletShellUnified>
  );
}
