import type { ReactNode } from "react";
import { PrismaTabletShellUnified } from "@components/tablet-shell/prisma-tablet-shell";
import styles from "./settings-workspace.module.css";

type SettingsRoute = "/settings/data" | "/settings/export" | "/settings/license";

const SECTIONS: Array<{ href: SettingsRoute; label: string }> = [
  { href: "/settings/data", label: "Datos" },
  { href: "/settings/export", label: "Exportaciones" },
  { href: "/settings/license", label: "Licencia" }
];

export function SettingsWorkspace({
  currentPath,
  title,
  subtitle,
  status,
  children
}: {
  currentPath: SettingsRoute;
  title: string;
  subtitle: string;
  status?: ReactNode;
  children: ReactNode;
}) {
  return (
    <PrismaTabletShellUnified
      currentPath={currentPath}
      title={title}
      subtitle={subtitle}
      kicker="Configuración Tablet"
      status={status}
    >
      <section className={styles.workspace} data-prisma-workspace="SettingsWorkspace">
        <nav className={styles.sectionNav} aria-label="Secciones de configuración">
          {SECTIONS.map((section) => {
            const active = section.href === currentPath;
            return (
              <a key={section.href} className={active ? styles.sectionLinkActive : styles.sectionLink} href={section.href} aria-current={active ? "page" : undefined}>
                {section.label}
              </a>
            );
          })}
        </nav>
        <div className={styles.content}>{children}</div>
      </section>
    </PrismaTabletShellUnified>
  );
}

export function DataSettingsOverview() {
  return (
    <div className={styles.dataOverview}>
      <section className={styles.dataHero}>
        <span>Continuidad local</span>
        <h2>Los datos operativos permanecen en esta Tablet.</h2>
        <p>Revisa el respaldo local o descarga únicamente los archivos que ya ofrece la aplicación.</p>
      </section>
      <div className={styles.dataActions}>
        <a className={styles.primaryAction} href="/offline">
          <strong>Revisar respaldo local</strong>
          <span>Ventas, pendientes, movimientos y diagnóstico offline.</span>
        </a>
        <a className={styles.secondaryAction} href="/settings/export">
          <strong>Abrir exportaciones</strong>
          <span>CSV y JSON disponibles desde los endpoints existentes.</span>
        </a>
      </div>
    </div>
  );
}
