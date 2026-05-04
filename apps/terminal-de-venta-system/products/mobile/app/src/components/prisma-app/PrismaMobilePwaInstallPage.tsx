import { PrismaMobilePwaInstallCard } from "./PrismaMobilePwaInstallCard";
import styles from "./prisma-mobile-pwa.module.css";

type PrismaMobilePwaInstallPageProps = {
  mode?: "install" | "offline";
};

export function PrismaMobilePwaInstallPage({ mode = "install" }: PrismaMobilePwaInstallPageProps) {
  const offline = mode === "offline";

  return (
    <main
      className={styles.pageRoot}
      data-prisma-product="mobile"
      data-prisma-surface="prisma.mobile.pwa.install.whatsapp.black.landing"
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
                <h1 id="prisma-install-title">{offline ? "PRISMA sigue a la mano" : "Instala PRISMA"}</h1>
                <p>
                  {offline
                    ? "Esta pantalla queda como respaldo cuando la red se pone payasa."
                    : "Elige tu dispositivo para instalar la app."}
                </p>
              </header>

              <PrismaMobilePwaInstallCard />
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
