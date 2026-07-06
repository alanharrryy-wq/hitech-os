import type { ReactNode } from "react";
import { getCurrentRouteMeta, getPrimaryNavigation, getSecondaryNavigationForPath } from "@/composition/navigation";
import { getPrimaryRouteActions } from "@/uiux/decision-model";
import { NavLink } from "./nav-link";
import { pcMessages } from "@/lib/i18n/messages/es";
import { PcSubnav } from "../uiux/pc-subnav";

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

export function AppShell({ currentPath, children }: { currentPath: string; children: ReactNode }) {
  const current = getCurrentRouteMeta(currentPath);
  const primaryNav = getPrimaryNavigation();
  const groupedNavigation = groupPrimaryNavigation(primaryNav);
  const secondaryNav = getSecondaryNavigationForPath(currentPath).filter((item) => item.href !== current.primaryHref && item.status !== "internal" && item.status !== "lab");
  const routeActions = getPrimaryRouteActions(currentPath);
  const hideRouteIntentStrip = currentPath === "/sales-control";

  return (
    <div className="shell" data-prisma-panel="pc.workspace" data-prisma-surface="pc" data-prisma-route={currentPath} data-prisma-component="AppShell" data-prisma-product="pc" data-uiux-gate="human-first-nav" data-route-intent={current.primaryQuestion}>
      <span hidden aria-hidden="true" data-prisma-panel="pc.workspace" data-prisma-surface="pc" data-prisma-route="*" />
      <a className="skip-link" href="#prisma-main-content">Saltar al contenido</a>
      <aside className="sidebar" data-prisma-component="Sidebar" aria-label="Navegación principal PC">
        <div className="brand-block prisma-brand-image-card" data-prisma-component="BrandBlock">
          <div className="brand-row">
            <img className="brand-logo-img" src="/brand/prisma-logo-official.png" alt="PRISMA" />
            <div>
              <div className="subtle">Command Center PC</div>
            </div>
          </div>
        </div>

        <div className="sidebar-main-scroll" role="region" aria-label="Módulos de navegación PC">
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

          {secondaryNav.length > 0 ? (
            <section className="sidebar-panel sidebar-utility-panel" data-prisma-component="SecondaryHumanNavigation">
              <p className="nav-group-title">{current.groupLabel}: pendientes y detalle</p>
              <nav className="nav" aria-label={`Vistas de ${current.groupLabel}`}>
                {secondaryNav.slice(0, 10).map((item) => (
                  <NavLink
                    key={item.href}
                    href={item.href}
                    title={item.title}
                    description={item.description}
                    active={isActive(currentPath, item.href)}
                    icon="•"
                  />
                ))}
              </nav>
            </section>
          ) : null}
        </div>
      </aside>

      <main className="main" id="prisma-main-content">
        <header className="topbar" data-prisma-component="TopBar" data-route-contract-resolved="true">
          <div className="topbar-brand">
            <span className="brand-mark" aria-hidden="true" style={{ width: 28, height: 28, fontSize: 14 }}>
              CC
            </span>
            <span>{current.title}</span>
          </div>

          <form className="search-shell" action="/sales-control" method="get" aria-label="Buscar en PRISMA PC" data-prisma-component="SearchBar">
            <span aria-hidden="true">⌕</span>
            <input name="q" placeholder="Buscar folio, producto o proveedor" />
          </form>

          <div className="user-shell" data-prisma-component="UserMenu">
            <div className="sync-chip" title="PC cliente final en modo comando">Command</div>
            {routeActions.slice(0, 1).map((action) => (
              <a key={action.label} className={action.primary ? "btn btn-primary" : "btn btn-secondary"} href={action.href}>
                {action.label}
              </a>
            ))}
            <div className="sync-chip">{pcMessages.shell.syncChip}</div>
            <div className="user-chip">
              <span className="avatar">PC</span>
              <span>Control PC</span>
            </div>
          </div>
        </header>

        {!hideRouteIntentStrip ? <section className="card" data-prisma-component="RouteIntentStrip" aria-label="Pregunta de esta pantalla">
          <div className="section-head">
            <div>
              <div className="kicker">pregunta de la pantalla</div>
              <h2 className="section-title">{current.primaryQuestion}</h2>
              <div className="section-copy">{current.description}</div>
            </div>
          </div>
          <PcSubnav currentPath={currentPath} />
        </section> : null}

        {children}
      </main>
    </div>
  );
}
