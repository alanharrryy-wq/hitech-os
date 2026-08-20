import type { ReactNode } from "react";
import * as ScrollArea from "@radix-ui/react-scroll-area";
import * as Tooltip from "@radix-ui/react-tooltip";
import { clsx } from "clsx";
import { PanelsTopLeft } from "lucide-react";
import { getCurrentRouteMeta, getPrimaryNavigation, getSecondaryNavigationForPath } from "@/composition/navigation";
import { PcLicenseNavigationGate } from "../licensing/pc-license-surface-provider";
import { NavLink } from "./nav-link";
import styles from "./app-shell.module.css";

function isActive(currentPath: string, href: string) {
  return currentPath === href || (href !== "/" && currentPath.startsWith(`${href}/`));
}

function stableId(value: string) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

const COMMAND_NAV_GROUP_LABELS: Record<string, string> = {
  hoy: "Operación",
  inventario: "Inventario",
  compras: "Compras",
  proveedores: "Compras",
  "ventas-caja": "Ventas / Caja",
  sincronizacion: "Sincronización",
  reportes: "Control / Auditoría",
  analisis: "Control / Auditoría",
  sistema: "Sistema",
  configuracion: "Configuración",
  ayuda: "Sistema"
};

function groupPrimaryNavigation(items: ReturnType<typeof getPrimaryNavigation>) {
  const groups = new Map<string, typeof items>();

  for (const item of items) {
    const label = COMMAND_NAV_GROUP_LABELS[item.group] ?? "Sistema";
    groups.set(label, [...(groups.get(label) ?? []), item]);
  }

  return [...groups.entries()].map(([label, groupItems]) => ({ label, items: groupItems }));
}

function SurfaceContextStrip({
  currentPath,
  groupLabel,
  secondaryNav
}: {
  currentPath: string;
  groupLabel: string;
  secondaryNav: ReturnType<typeof getSecondaryNavigationForPath>;
}) {
  if (secondaryNav.length === 0) return null;

  return (
    <Tooltip.Provider delayDuration={180} skipDelayDuration={80}>
      <nav
        className={styles.contextStrip}
        aria-label={`Vistas de ${groupLabel}`}
        data-prisma-component="SurfaceContextStrip"
        data-context-count={secondaryNav.length}
        data-context-mode={secondaryNav.length > 4 ? "overflow-governed" : "inline"}
      >
        <span className={styles.contextLabel}>{groupLabel}</span>
        <ScrollArea.Root className={styles.contextScroll} type="hover">
          <ScrollArea.Viewport className={styles.contextViewport}>
            <div className={styles.contextRow}>
              {secondaryNav.map((item) => {
                const active = isActive(currentPath, item.href);

                return (
                  <Tooltip.Root key={item.href}>
                    <Tooltip.Trigger asChild>
                      <a
                        className={clsx(styles.contextLink, active && styles.contextLinkActive)}
                        href={item.href}
                        aria-current={active ? "page" : undefined}
                        aria-label={`${item.title}. ${item.description}`}
                        data-active={active ? "true" : "false"}
                      >
                        <span className={styles.contextDot} aria-hidden="true" />
                        <span className={styles.contextTitle}>{item.title}</span>
                      </a>
                    </Tooltip.Trigger>
                    <Tooltip.Portal>
                      <Tooltip.Content
                        className={styles.contextTooltip}
                        sideOffset={8}
                        collisionPadding={16}
                      >
                        {item.description}
                        <Tooltip.Arrow className={styles.contextTooltipArrow} />
                      </Tooltip.Content>
                    </Tooltip.Portal>
                  </Tooltip.Root>
                );
              })}
            </div>
          </ScrollArea.Viewport>
          <ScrollArea.Scrollbar className={styles.contextScrollbar} orientation="horizontal">
            <ScrollArea.Thumb className={styles.contextThumb} />
          </ScrollArea.Scrollbar>
          <ScrollArea.Corner />
        </ScrollArea.Root>
      </nav>
    </Tooltip.Provider>
  );
}

export function AppShell({ currentPath, children }: { currentPath: string; children: ReactNode }) {
  const current = getCurrentRouteMeta(currentPath);
  const primaryNav = getPrimaryNavigation();
  const groupedNavigation = groupPrimaryNavigation(primaryNav);
  const secondaryNav = getSecondaryNavigationForPath(currentPath).filter(
    (item) => item.href !== current.primaryHref && item.status !== "internal" && item.status !== "lab"
  );
  const hideRouteIntentStrip = currentPath === "/sales-control";
  const routeLabelId = `pc-route-label-${stableId(current.route || currentPath) || "root"}`;

  return (
    <div
      className={styles.shell}
      data-prisma-panel="pc.workspace"
      data-prisma-surface="pc"
      data-prisma-route={currentPath}
      data-prisma-component="AppShell"
      data-prisma-product="pc"
      data-uiux-gate="human-first-nav"
      data-route-intent={current.primaryQuestion}
    >
      <span hidden aria-hidden="true" data-prisma-panel="pc.workspace" data-prisma-surface="pc" data-prisma-route="*" />
      <a className={styles.skipLink} href="#prisma-main-content">
        Saltar al contenido principal
      </a>

      <aside className={styles.sidebar} data-prisma-component="Sidebar" aria-label="Navegación principal PC">
        <div className={styles.brandBlock} data-prisma-component="BrandBlock">
          <div className={styles.brandRow}>
            <img className={styles.brandLogo} src="/brand/prisma-logo-official.png" alt="PRISMA" />
            <div className={styles.brandCopy}>
              <strong>Command Center</strong>
              <span className={styles.brandSubtitle}>Superficie PC</span>
            </div>
          </div>
          <div className={styles.brandSignals} aria-label="Estado del chrome">
            <span>PC</span>
            <span>Continuidad</span>
          </div>
        </div>

        <PcLicenseNavigationGate
          fallback={(
            <section className={styles.navPanel} data-prisma-component="PcLicenseNavigationGate" data-license-navigation="denied">
              <p className={styles.navHeading}>Navegación principal</p>
              <p>Navegación PC no disponible para esta licencia.</p>
            </section>
          )}
        >
          <section
            className={styles.navPanel}
            data-prisma-component="PrimaryHumanNavigation"
            data-uiux-first-level="human-only"
            data-license-navigation="allowed"
          >
            <p className={styles.navHeading}>Navegación principal</p>
            <nav className={styles.nav} aria-label="Áreas principales">
              {groupedNavigation.map((group) => {
                const groupId = `pc-nav-${stableId(group.label)}`;
                return (
                  <div className={styles.navSection} key={group.label} role="group" aria-labelledby={groupId}>
                    <span className={styles.navSectionTitle} id={groupId}>
                      {group.label}
                    </span>
                    <div className={styles.navItems}>
                      {group.items.map((item) => (
                        <NavLink
                          key={item.href}
                          href={item.href}
                          title={item.title}
                          description={item.description}
                          active={current.group === item.group || isActive(currentPath, item.href)}
                          icon={item.icon}
                        />
                      ))}
                    </div>
                  </div>
                );
              })}
            </nav>
          </section>
        </PcLicenseNavigationGate>
      </aside>

      <main
        className={styles.main}
        id="prisma-main-content"
        tabIndex={-1}
        aria-labelledby={routeLabelId}
        data-prisma-route-viewport="true"
      >
        <header className={styles.topbar} data-prisma-component="TopBar" data-route-contract-resolved="true">
          <div className={styles.topbarIdentity}>
            <span className={styles.topbarMark} aria-hidden="true">
              <PanelsTopLeft size={16} strokeWidth={1.8} />
            </span>
            <span className={styles.topbarCopy}>
              <span className={styles.topbarEyebrow}>{current.groupLabel}</span>
              <span className={styles.topbarTitle} id={routeLabelId}>{current.title}</span>
            </span>
          </div>
          <div className={styles.topbarSignals} aria-label="Contexto de la superficie">
            <span>PC</span>
            <span>Vista operativa</span>
          </div>
        </header>

        <PcLicenseNavigationGate>
          <SurfaceContextStrip currentPath={currentPath} groupLabel={current.groupLabel} secondaryNav={secondaryNav} />
        </PcLicenseNavigationGate>

        {!hideRouteIntentStrip ? (
          <section className={styles.routeIntent} data-prisma-component="RouteIntentStrip" aria-label="Pregunta de esta pantalla">
            <div className={styles.routeIntentCopy}>
              <span className={styles.routeIntentKicker}>Pregunta de la pantalla</span>
              <h2 className={styles.routeIntentTitle}>{current.primaryQuestion}</h2>
              <p className={styles.routeIntentDescription}>{current.description}</p>
            </div>
            <span className={styles.routeIntentBadge}>{current.groupLabel}</span>
          </section>
        ) : null}

        {children}
      </main>
    </div>
  );
}
