import { PrismaMobilePwaInstallCard } from "./PrismaMobilePwaInstallCard";
import styles from "./prisma-mobile-pwa.module.css";

type PrismaMobilePwaInstallPageProps = {
  mode?: "install" | "offline";
  setupCode?: string;
};

export function PrismaMobilePwaInstallPage({ mode = "install", setupCode = "" }: PrismaMobilePwaInstallPageProps) {
  const offline = mode === "offline";
  const setupHref = setupCode ? `/prisma-app/setup?code=${encodeURIComponent(setupCode)}` : "/prisma-app/setup";

  return (
    <main
      className={styles.pageRoot}
      data-prisma-product="mobile"
      data-prisma-surface="prisma.mobile.pwa.install.whatsapp.black.landing"
      data-prisma-zone="mobile-pwa-install"
    >
      <div className={styles.ambientGlow} aria-hidden="true" />
      <div className={styles.starField} aria-hidden="true" />

      <section className={styles.phoneStage} aria-labelledby="prisma-install-title">
        <div className={styles.phoneShell}>
          <div className={styles.phoneButtonLeft} aria-hidden="true" />
          <div className={styles.phoneButtonRight} aria-hidden="true" />
          <div className={styles.phoneScreen}>
            <div className={styles.dynamicIsland} aria-hidden="true" />
            <div className={styles.screenContent}>
              <div className={styles.brandPill}>
                <span className={styles.whatsappGlyph} aria-hidden="true">☎</span>
                <span>{offline ? "PRISMA RESPALDO OFFLINE" : "LLEGASTE DESDE WHATSAPP"}</span>
              </div>

              <header className={styles.minimalHero}>
                <div className={styles.brandMark} aria-hidden="true">
                  <img src="/icons/prisma_whatsapp_install_icon.png" alt="" />
                  <span>PRISMA</span>
                </div>
                <h1 id="prisma-install-title">{offline ? "Supervisión móvil offline" : "Instala PRISMA Mobile para supervisar"}</h1>
                <p>
                  {offline
                    ? "Esta pantalla es respaldo visual. Tablet Solo vende sola sin Mobile, PC, Cloudflare ni internet."
                    : "Mobile supervisa. Tablet Solo vende sola. La instalación PWA es un adder premium; no es requisito para vender."}
                </p>
              </header>

              <PrismaMobilePwaInstallCard />
              <a className={styles.hiddenDashboardLink} href={setupHref} aria-label="Abrir Prisma Customer Setup para reclamar Mobile Companion Slot">
                Prisma Customer Setup
              </a>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
