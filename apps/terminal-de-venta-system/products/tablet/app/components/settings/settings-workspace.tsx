import type { ReactNode } from "react";
import { PrismaIcon } from "@components/prisma-dark-pos/prisma-dark-pos-icons";
import type { PrismaIconName } from "@components/prisma-dark-pos/prisma-dark-pos-data";
import { PrismaTabletShellUnified } from "@components/tablet-shell/prisma-tablet-shell";
import styles from "./settings-workspace.module.css";

type SettingsRoute = "/settings/data" | "/settings/export" | "/settings/license";

const SECTIONS: Array<{ href: SettingsRoute; label: string; icon: PrismaIconName; accent: "cyan" | "amber" | "violet" }> = [
  { href: "/settings/data", label: "Datos", icon: "save", accent: "cyan" },
  { href: "/settings/export", label: "Exportaciones", icon: "receipt", accent: "amber" },
  { href: "/settings/license", label: "Licencia", icon: "terminal", accent: "violet" }
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
      <section
        className={styles.workspace}
        data-prisma-workspace="SettingsWorkspace"
        data-prisma-settings-route={currentPath}
      >
        <nav className={styles.sectionNav} aria-label="Secciones de configuración">
          {SECTIONS.map((section) => {
            const active = section.href === currentPath;
            return (
              <a
                key={section.href}
                className={active ? styles.sectionLinkActive : styles.sectionLink}
                href={section.href}
                aria-current={active ? "page" : undefined}
                data-accent={section.accent}
              >
                <PrismaIcon name={section.icon} size={18} />
                <span>{section.label}</span>
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
        <span className={styles.dataHeroIcon} aria-hidden="true">
          <PrismaIcon name="save" size={25} />
        </span>
        <span className={styles.dataEyebrow}>Continuidad local</span>
        <h2>Los datos operativos permanecen en esta Tablet.</h2>
        <p>Revisa el respaldo local o descarga únicamente los archivos que ya ofrece la aplicación.</p>
      </section>

      <div className={styles.dataActions}>
        <a className={styles.primaryAction} href="/offline">
          <span className={styles.actionIcon} aria-hidden="true">
            <PrismaIcon name="save" size={20} />
          </span>
          <span className={styles.actionCopy}>
            <strong>Revisar respaldo local</strong>
            <small>Ventas, pendientes, movimientos y diagnóstico offline.</small>
          </span>
          <PrismaIcon name="arrow-right" size={18} />
        </a>
        <a className={styles.secondaryAction} href="/settings/export">
          <span className={styles.actionIcon} aria-hidden="true">
            <PrismaIcon name="receipt" size={20} />
          </span>
          <span className={styles.actionCopy}>
            <strong>Abrir exportaciones</strong>
            <small>CSV y JSON disponibles desde los endpoints existentes.</small>
          </span>
          <PrismaIcon name="arrow-right" size={18} />
        </a>
      </div>
    </div>
  );
}
