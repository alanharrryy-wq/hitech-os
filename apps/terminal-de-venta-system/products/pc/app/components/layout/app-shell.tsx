import type { ReactNode } from "react";
import * as ScrollArea from "@radix-ui/react-scroll-area";
import * as Tooltip from "@radix-ui/react-tooltip";
import { clsx } from "clsx";
import { PanelsTopLeft } from "lucide-react";
import { getCurrentRouteMeta, getPrimaryNavigation, getSecondaryNavigationForPath } from "@/composition/navigation";
import { NavLink } from "./nav-link";

function isActive(currentPath: string, href: string) {
  return currentPath === href || (href !== "/" && currentPath.startsWith(`${href}/`));
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
    <Tooltip.Provider delayDuration={180}>
      <nav className="surface-context-strip" aria-label={`Vistas de ${groupLabel}`} data-prisma-component="SurfaceContextStrip" data-context-count={secondaryNav.length} data-context-mode={secondaryNav.length > 4 ? "overflow-governed" : "inline"}>
        <span className="surface-context-label">{groupLabel}</span>
        <ScrollArea.Root className="surface-context-scroll" type="hover">
          <ScrollArea.Viewport className="surface-context-scroll-viewport">
            <div className="surface-context-pill-row">
              {secondaryNav.map((item) => {
                const active = isActive(currentPath, item.href);

                return (
                  <Tooltip.Root key={item.href}>
                    <Tooltip.Trigger asChild>
                      <a
                        className={clsx("surface-context-pill", active && "is-active")}
                        href={item.href}
                        aria-current={active ? "page" : undefined}
                        data-active={active ? "true" : "false"}
                      >
                        <span className="surface-context-pill-dot" aria-hidden="true" />
                        <span className="surface-context-pill-title">{item.title}</span>
                      </a>
                    </Tooltip.Trigger>
                    <Tooltip.Portal>
                      <Tooltip.Content className="surface-context-tooltip" sideOffset={8}>
                        {item.description}
                      </Tooltip.Content>
                    </Tooltip.Portal>
                  </Tooltip.Root>
                );
              })}
            </div>
          </ScrollArea.Viewport>
          <ScrollArea.Scrollbar className="surface-context-scrollbar" orientation="horizontal">
            <ScrollArea.Thumb className="surface-context-scroll-thumb" />
          </ScrollArea.Scrollbar>
        </ScrollArea.Root>
      </nav>
    </Tooltip.Provider>
  );
}

export function AppShell({ currentPath, children }: { currentPath: string; children: ReactNode }) {
  const current = getCurrentRouteMeta(currentPath);
  const primaryNav = getPrimaryNavigation();
  const groupedNavigation = groupPrimaryNavigation(primaryNav);
  const secondaryNav = getSecondaryNavigationForPath(currentPath).filter((item) => item.href !== current.primaryHref && item.status !== "internal" && item.status !== "lab");
  const hideRouteIntentStrip = currentPath === "/sales-control";

  return (
    <div className="shell" data-prisma-panel="pc.workspace" data-prisma-surface="pc" data-prisma-route={currentPath} data-prisma-component="AppShell" data-prisma-product="pc" data-uiux-gate="human-first-nav" data-route-intent={current.primaryQuestion}>
      <span hidden aria-hidden="true" data-prisma-panel="pc.workspace" data-prisma-surface="pc" data-prisma-route="*" />
      <a className="skip-link" href="#prisma-main-content">Saltar al contenido</a>
      <aside className="sidebar" data-prisma-component="Sidebar" aria-label="Navegación principal PC">
        <div className="brand-block" data-prisma-component="BrandBlock">
          <div className="brand-row">
            <img className="brand-logo-img" src="/brand/prisma-logo-official.png" alt="PRISMA" />
            <div>
              <div className="subtle">Command Center PC</div>
            </div>
          </div>
        </div>

        <section className="sidebar-panel sidebar-nav-panel" data-prisma-component="PrimaryHumanNavigation" data-uiux-first-level="human-only">
          <p className="nav-group-title">Navegación principal</p>
          <nav className="nav" aria-label="Áreas principales">
            {groupedNavigation.map((group) => (
              <div className="nav-section" key={group.label}>
                <span className="nav-section-title">{group.label}</span>
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
            ))}
          </nav>
        </section>
      </aside>

      <main className="main" id="prisma-main-content">
        <header className="topbar" data-prisma-component="TopBar" data-route-contract-resolved="true">
          <div className="topbar-brand">
            <span className="brand-mark" aria-hidden="true">
              <PanelsTopLeft size={15} strokeWidth={1.8} />
            </span>
            <span>CC {current.title}</span>
          </div>
        </header>

        <SurfaceContextStrip currentPath={currentPath} groupLabel={current.groupLabel} secondaryNav={secondaryNav} />

        {!hideRouteIntentStrip ? <section className="card" data-prisma-component="RouteIntentStrip" aria-label="Pregunta de esta pantalla">
          <div className="section-head">
            <div>
              <div className="kicker">pregunta de la pantalla</div>
              <h2 className="section-title">{current.primaryQuestion}</h2>
              <div className="section-copy">{current.description}</div>
            </div>
          </div>
        </section> : null}

        {children}
      </main>
    </div>
  );
}
