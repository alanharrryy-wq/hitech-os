import { resolveMobileCustomerSetup, MOBILE_CUSTOMER_SETUP_SLOT_LABEL } from "@/lib/prisma-app/prisma-mobile-customer-setup";
import styles from "@/components/prisma-app/prisma-mobile-pwa.module.css";

export const metadata = {
  title: "Prisma Customer Setup | Mobile Companion",
  description: "Setup Link, Setup Code y Device Claim para PRISMA Mobile."
};

export default function PrismaMobileCustomerSetupPage({ searchParams }: { searchParams?: { code?: string; setupCode?: string } }) {
  const code = searchParams?.code || searchParams?.setupCode || "";
  const setup = resolveMobileCustomerSetup(code);

  return (
    <main className={styles.pageRoot} data-prisma-customer-setup-surface="mobile">
      <section className={styles.phoneStage} aria-labelledby="mobile-setup-title">
        <div className={styles.phoneShell}>
          <div className={styles.phoneScreen}>
            <div className={styles.screenContent}>
              <header className={styles.minimalHero}>
                <div className={styles.brandMark} aria-hidden="true"><span>PRISMA</span></div>
                <h1 id="mobile-setup-title">Prisma Customer Setup</h1>
                <p>Este Mobile reclama {MOBILE_CUSTOMER_SETUP_SLOT_LABEL} con Setup Code, sin admin token y sin duplicar activación.</p>
              </header>
              <section className={styles.installCard}>
                <div className={styles.installHeader}>
                  <span>Setup Code</span>
                  <strong>{setup.setupCode || "Pendiente"}</strong>
                </div>
                <p className={styles.installContextNote}>{setup.customerMessage}</p>
                <div className={styles.installStatusGrid}>
                  {setup.slots.map((slot) => (
                    <span key={slot.surface}>{slot.label}: {slot.claimed}/{slot.allowed}</span>
                  ))}
                </div>
                <div className={styles.installActions}>
                  <a href={`/prisma-app/install?code=${encodeURIComponent(setup.setupCode || "")}`}>Continuar instalación</a>
                </div>
              </section>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
