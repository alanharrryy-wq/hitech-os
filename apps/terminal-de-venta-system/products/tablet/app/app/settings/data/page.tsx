import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { LocalUsersRolesPanel } from "@components/settings/local-users-roles-panel";
import { SalesResetPanel } from "@components/settings/sales-reset-panel";
import { getLocalAdminSnapshot } from "@/server/pos-api/local-admin.prisma";
import { previewSalesReset } from "@/server/pos-api/sales-reset.prisma";
import { getTabletRuntimeSnapshot } from "@/server/tablet-runtime-snapshot";
import { readRuntimeSnapshotInput } from "@/server/tablet-runtime-snapshot/env";
import styles from "@components/license/license-ui.module.css";

export const dynamic = "force-dynamic";

export default async function TabletDataToolsPage() {
  const [runtimeSnapshot, resetPreview, localAdminSnapshot] = await Promise.all([
    getTabletRuntimeSnapshot(readRuntimeSnapshotInput()),
    previewSalesReset(),
    getLocalAdminSnapshot()
  ]);

  return (
    <PrismaTabletShellUnified
      currentPath="/settings/data"
      title="Datos locales"
      subtitle="Herramientas bloqueadas para soporte sin tocar licencia ni catálogo."
      kicker="Soporte Tablet"
      status={<TabletShellStatusPill tone="warn">Acceso controlado</TabletShellStatusPill>}
      runtimeSnapshot={runtimeSnapshot}
    >
      <main className={styles.pageStack}>
        <section className={styles.card}>
          <p className={styles.eyebrow}>Continuidad local</p>
          <h1 className={styles.title}>La Tablet sigue operando con su base local</h1>
          <p className={styles.copy}>
            Estas herramientas no conectan la venta a PC ni a internet. Cualquier reset destructivo queda limitado, confirmado y auditado.
          </p>
        </section>
        <LocalUsersRolesPanel initialSnapshot={localAdminSnapshot} />
        <SalesResetPanel preview={resetPreview} />
      </main>
    </PrismaTabletShellUnified>
  );
}
