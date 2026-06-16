import type { ReactNode } from "react";
import { getCurrentRouteMeta, getPrimaryNavigation, getSecondaryNavigationForPath } from "@/composition/navigation";
import { getPrimaryRouteActions } from "@/uiux/decision-model";
import { NavLink } from "./nav-link";
import { pcMessages } from "@/lib/i18n/messages/es";
import { PcSubnav } from "../uiux/pc-subnav";

function isActive(currentPath: string, href: string) {
  return currentPath === href || (href !== "/" && currentPath.startsWith(`${href}/`));
}

export function AppShell({ currentPath, children }: { currentPath: string; children: ReactNode }) {
  const current = getCurrentRouteMeta(currentPath);
  const primaryNav = getPrimaryNavigation();
  const groupedNavigation = primaryNav;
  const secondaryNav = getSecondaryNavigationForPath(currentPath).filter((item) => item.href !== current.primaryHref && item.status !== "internal" && item.status !== "lab");
  const routeActions = getPrimaryRouteActions(currentPath);
  const hideRouteIntentStrip = currentPath === "/sales-control";

  return (
    <div className="shell" data-prisma-component="AppShell" data-prisma-product="pc" data-uiux-gate="human-first-nav" data-route-intent={current.primaryQuestion}>
      <a className="skip-link" href="#prisma-main-content">Saltar al contenido</a>
      <aside className="sidebar" data-prisma-component="Sidebar" aria-label="Navegación principal PC">
        <div className="brand-block prisma-brand-image-card" data-prisma-component="BrandBlock">
          <div className="brand-row">
            <img className="brand-logo-img" src="/brand/prisma-logo-official.png" alt="PRISMA" />
            <div>
              <div className="subtle">Centro de decisiones simple</div>
            </div>
          </div>
        </div>

        <div className="sidebar-main-scroll" role="region" aria-label="Módulos de navegación PC">
          <section className="sidebar-panel sidebar-nav-panel" data-prisma-component="SecondaryActionCard">
            <p className="nav-group-title">Buscar</p>
            <form className="search-shell" action="/sales-control" method="get" data-prisma-component="SidebarSearch">
              <span aria-hidden="true">⌕</span>
              <input name="q" placeholder="Buscar folio, producto, equipo o proveedor" aria-label="Buscar en venta, inventario, compras y sincronización" />
            </form>
          </section>

          <section className="sidebar-panel sidebar-nav-panel" data-prisma-component="PrimaryHumanNavigation" data-uiux-first-level="human-only">
            <p className="nav-group-title">Navegación principal</p>
            <nav className="nav" aria-label="Áreas principales">
              {groupedNavigation.map((item) => (
                <NavLink
                  key={item.href}
                  href={item.href}
                  title={item.title}
                  description={item.description}
                  active={current.group === item.group || isActive(currentPath, item.href)}
                  icon={item.icon}
                />
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

        <div className="footer-stack">
          <div className="footer-pill" data-prisma-component="TerminalStatusCard">
            <span className="subtle">Gemelo</span>
            <strong>{pcMessages.shell.twinStatus}</strong>
            <small>Tablet opera independiente</small>
          </div>
          <div className="footer-pill" data-prisma-component="TerminalStatusCard">
            <span className="subtle">Última sincronización</span>
            <strong>{pcMessages.shell.lastSync}</strong>
          </div>
          <div className="footer-actions">
            <a className="footer-chip" href="/glosario">Ayuda</a>
            <a className="footer-chip" href="/sync">Sincronización</a>
          </div>
        </div>
      </aside>

      <main className="main" id="prisma-main-content">
        <header className="topbar" data-prisma-component="TopBar" data-route-contract-resolved="true">
          <div className="topbar-brand">
            <span className="brand-mark" aria-hidden="true" style={{ width: 28, height: 28, fontSize: 14 }}>
              ●
            </span>
            <span>{current.title}</span>
          </div>

          <form className="search-shell" action="/sales-control" method="get" aria-label="Buscar en PRISMA PC" data-prisma-component="SearchBar">
            <span aria-hidden="true">⌕</span>
            <input name="q" placeholder="Buscar folio, producto, equipo o proveedor" />
          </form>

          <div className="user-shell" data-prisma-component="UserMenu">
            <div className="sync-chip" title="PC cliente final en modo claro">Modo claro</div>
            {routeActions.slice(0, 1).map((action) => (
              <a key={action.label} className={action.primary ? "btn btn-primary" : "btn btn-secondary"} href={action.href}>
                {action.label}
              </a>
            ))}
            <div className="sync-chip">{pcMessages.shell.syncChip}</div>
            <div className="user-chip">
              <span className="avatar">PC</span>
              <span>{pcMessages.shell.userChip}</span>
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
