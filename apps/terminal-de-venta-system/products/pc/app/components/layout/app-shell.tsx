import type { ReactNode } from "react";
import { getNavigation } from "@/composition/navigation";
import { NavLink } from "./nav-link";
import { pcMessages } from "@/lib/i18n/messages/es";
import { PrismaDarkSelector } from "../ui/prisma-dark-selector";

const NAV_ICONS: Record<string, string> = {
  "/": "IN",
  "/dashboard": "OV",
  "/sales-control": "VE",
  "/cash-sessions": "CA",
  "/catalog": "CT",
  "/stock": "ST",
  "/movements": "MV",
  "/counts": "CN",
  "/purchasing": "OC",
  "/receiving": "RC",
  "/replenishment": "RB",
  "/proveedores": "PR",
  "/audit": "AU",
  "/sync": "SY",
  "/devices": "DV",
  "/tablet-communication": "TC",
  "/license-runtime": "LR",
  "/data-quality": "DQ",
  "/settings": "AJ"
};

const GROUP_ORDER = ["Overview", "Sales Control", "Inventory", "Purchasing", "Sync", "Devices", "Audit", "Runtime", "Settings"];

function isActive(currentPath: string, href: string) {
  return currentPath === href || (href !== "/" && currentPath.startsWith(`${href}/`));
}

function groupedNavigation(nav: ReturnType<typeof getNavigation>) {
  return GROUP_ORDER.map((group) => ({
    group,
    items: nav.filter((item) => item.groupLabel === group)
  })).filter((section) => section.items.length > 0);
}

export function AppShell({ currentPath, children }: { currentPath: string; children: ReactNode }) {
  const nav = getNavigation();
  const current =
    currentPath === "/"
      ? { title: pcMessages.shell.home, description: "Qué puede hacer PRISMA" }
    : currentPath === "/dashboard"
        ? { title: "Vista general", description: "KPIs y operación" }
        : nav.find((item) => isActive(currentPath, item.href));
  const navGroups = groupedNavigation(nav);

  return (
    <div className="shell" data-prisma-component="AppShell" data-prisma-product="pc">
      <a className="skip-link" href="#prisma-main-content">Saltar al contenido</a>
      <aside className="sidebar" data-prisma-component="Sidebar" aria-label="Navegación principal PC">
        <div className="brand-block prisma-brand-image-card" data-prisma-component="BrandBlock">
          <div className="brand-row">
            <img className="brand-logo-img" src="/brand/prisma-logo-official.png" alt="PRISMA" />
            <div>
              <div className="subtle">Sistema inteligente de gestión operativa</div>
            </div>
          </div>
        </div>

        <div className="sidebar-main-scroll" role="region" aria-label="Módulos de navegación PC">
          <section className="sidebar-panel sidebar-nav-panel" data-prisma-component="SecondaryActionCard">
            <p className="nav-group-title">Buscar módulo</p>
            <form className="search-shell" action="/sales-control" method="get" data-prisma-component="SidebarSearch">
              <span aria-hidden="true">⌕</span>
              <input name="q" placeholder="Folio, SKU, device o licencia" aria-label="Buscar en Ventas, Sync y Dispositivos" />
            </form>
          </section>

          <section className="sidebar-panel sidebar-nav-panel" data-prisma-component="SecondaryActionCard">
            <p className="nav-group-title">Navegación</p>
            <nav className="nav">
              <NavLink href="/" title={pcMessages.shell.home} description="Qué puede hacer PRISMA" active={currentPath === "/"} icon={NAV_ICONS["/"]} />
              <NavLink href="/dashboard" title="Vista general" description="KPIs y operación" active={currentPath === "/dashboard"} icon={NAV_ICONS["/dashboard"]} />
            </nav>
          </section>

          {navGroups.map((section) => (
            <section key={section.group} className="sidebar-panel sidebar-utility-panel" data-prisma-component="SecondaryActionCard">
              <p className="nav-group-title">{section.group}</p>
              <nav className="nav">
                {section.items.map((item) => (
                  <NavLink
                    key={item.href}
                    href={item.href}
                    title={item.title}
                    description={item.description}
                    active={isActive(currentPath, item.href)}
                    icon={NAV_ICONS[item.href] ?? "•"}
                  />
                ))}
              </nav>
            </section>
          ))}
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
            <div className="footer-chip">Guías</div>
            <div className="footer-chip">Sincronización</div>
          </div>
        </div>
      </aside>

      <main className="main" id="prisma-main-content">
        <header className="topbar" data-prisma-component="TopBar">
          <div className="topbar-brand">
            <span className="brand-mark" aria-hidden="true" style={{ width: 28, height: 28, fontSize: 14 }}>
              ●
            </span>
            <span>{current?.title ?? pcMessages.shell.home}</span>
          </div>

          <form className="search-shell" action="/sales-control" method="get" aria-label="Buscar en control de ventas" data-prisma-component="SearchBar">
            <span aria-hidden="true">⌕</span>
            <input name="q" placeholder="Buscar folio, SKU, terminal o cajero" />
          </form>

          <div className="user-shell" data-prisma-component="UserMenu">
            <PrismaDarkSelector />
            <div className="sync-chip">{pcMessages.shell.syncChip}</div>
            <div className="user-chip">
              <span className="avatar">PC</span>
              <span>{pcMessages.shell.userChip}</span>
            </div>
          </div>
        </header>

        {children}
      </main>
    </div>
  );
}
