import { PrismaTabletShellUnified, TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";
import { TabletSettingsSurfaceV2 } from "@components/tablet-visual-v2";
import { getTabletLicenseGovernor } from "@/server/licensing/tablet-license-service";
import { resolveTabletCustomerSetup, TABLET_CUSTOMER_SETUP_SLOT_LABEL } from "@/server/licensing/tablet-customer-setup";
import styles from "@components/license/license-ui.module.css";

export const dynamic = "force-dynamic";

export default function TabletCustomerSetupPage({ searchParams }: { searchParams?: { code?: string; setupCode?: string } }) {
  const code = searchParams?.code || searchParams?.setupCode || "";
  const setup = resolveTabletCustomerSetup(code);
  const governor = getTabletLicenseGovernor();

  return (
    <PrismaTabletShellUnified
      currentPath="/setup"
      title="Prisma Customer Setup"
      subtitle="Setup Link, Setup Code y Device Claim para esta Tablet POS."
      kicker="Configuración cliente"
      status={<TabletShellStatusPill tone="warn">Source ready</TabletShellStatusPill>}
    >
      <TabletSettingsSurfaceV2 routeId="/setup" title="Prisma Customer Setup" description="Esta Tablet reclama el Tablet POS Slot sin admin token y sin depender de PC para vender." statusLabel="Source ready">
        <main className={styles.pageStack} data-prisma-customer-setup-surface="tablet">
          <section className={styles.card}>
            <p className={styles.eyebrow}>Setup Code</p>
            <h2 className={styles.sectionTitle}>{setup.setupCode || "Pendiente"}</h2>
            <p className={styles.copy}>This tablet will claim {TABLET_CUSTOMER_SETUP_SLOT_LABEL} 1 of allowed slots.</p>
            <p className={styles.helper}>{setup.customerMessage}</p>
          </section>
          <section className={styles.card}>
            <p className={styles.eyebrow}>Device Claim</p>
            <h2 className={styles.sectionTitle}>Tablet POS Slot</h2>
            <p className={styles.copy}>Surface fijo: tablet. No admin token. Si el gateway no esta desplegado, la venta local continua bajo la licencia actual.</p>
            <p className={styles.helper}>Licencia actual: {governor.status.state} · Plan {governor.status.plan}</p>
          </section>
        </main>
      </TabletSettingsSurfaceV2>
    </PrismaTabletShellUnified>
  );
}
