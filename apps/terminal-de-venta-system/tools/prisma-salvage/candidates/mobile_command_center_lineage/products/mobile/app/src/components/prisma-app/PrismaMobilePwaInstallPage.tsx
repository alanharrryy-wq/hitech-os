import { PrismaMobilePwaInstallCard } from "./PrismaMobilePwaInstallCard";
import styles from "./prisma-mobile-pwa.module.css";

export function PrismaMobilePwaInstallPage({ mode = "install" }: { mode?: "install" | "offline" }) {
  const offline = mode === "offline";

  return (
    <main
      className={styles.pageRoot}
      data-prisma-product="mobile"
      data-prisma-surface="prisma.mobile.pwa.install.minimal.selector"
    >
      <div className={styles.ambientGlow} aria-hidden="true" />
      <section className={styles.minimalShell} aria-labelledby="prisma-install-title">
        <div className={styles.brandPill}>PRISMA App</div>
        <header className={styles.minimalHero}>
          <span>{offline ? "Modo offline" : "Instalación desde WhatsApp"}</span>
          <h1 id="prisma-install-title">Elige tu celular</h1>
          <p>{offline ? "PRISMA conserva una pantalla de respaldo cuando la red se pone dramática." : "Dos opciones. Sin menú raro. Sin páginas de manual como si estuviéramos armando mueble sueco."}</p>
        </header>
        <PrismaMobilePwaInstallCard />
      </section>
    </main>
  );
}
