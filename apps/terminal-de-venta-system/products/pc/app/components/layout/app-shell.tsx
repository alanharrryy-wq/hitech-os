import type { ReactNode } from "react";
import { getNavigation } from "@/composition/navigation";
import { NavLink } from "./nav-link";
import { pcMessages } from "@/lib/i18n/messages/es";

const NAV_ICONS: Record<string, string> = {
  "/": "⌂",
  "/dashboard": "◫",
  "/catalog": "▣",
  "/stock": "▤",
  "/movements": "↕",
  "/counts": "◎",
  "/purchasing": "◴",
  "/receiving": "◌",
  "/replenishment": "↺",
  "/audit": "⌁",
  "/sync": "⇄",
  "/settings": "⚙"
};

export function AppShell({ currentPath, children }: { currentPath: string; children: ReactNode }) {
  const nav = getNavigation();
  const current =
    currentPath === "/"
      ? { title: pcMessages.shell.home, description: pcMessages.home.subtitle }
      : currentPath === "/dashboard"
        ? { title: "Tablero", description: "KPIs y sincronización" }
        : nav.find((item) => item.href === currentPath);
  const controlItems = nav.filter((item) => item.navGroup === "control");
  const utilityItems = nav.filter((item) => item.navGroup === "operation");

  return (
    <div className="shell" data-prisma-component="AppShell" data-prisma-product="pc">
      <a className="skip-link" href="#prisma-main-content">Saltar al contenido</a>
      <aside className="sidebar" data-prisma-component="Sidebar" aria-label="Navegación principal PC">
        <div className="brand-block" data-prisma-component="BrandBlock">
          <div className="brand-row">
            <span className="brand-mark prisma-mark" aria-hidden="true">
              <span className="prisma-shard" />
            </span>
            <div>
              <div className="brand">PRISMA</div>
              <div className="subtle">Sistema de gestión inteligente</div>
            </div>
          </div>
        </div>

        <div className="sidebar-main-scroll" role="region" aria-label="Módulos de navegación PC">
        <section className="sidebar-panel sidebar-nav-panel" data-prisma-component="SecondaryActionCard">
          <p className="nav-group-title">Navegación</p>
          <nav className="nav">
            <NavLink href="/" title={pcMessages.shell.home} description="vista ejecutiva" active={currentPath === "/"} icon={NAV_ICONS["/"]} />
            <NavLink href="/dashboard" title="Tablero" description="KPIs y sincronización" active={currentPath === "/dashboard"} icon={NAV_ICONS["/dashboard"]} />
            {controlItems.map((item) => (
              <NavLink
                key={item.href}
                href={item.href}
                title={item.title}
                description={item.description}
                active={currentPath === item.href}
                icon={NAV_ICONS[item.href] ?? "•"}
              />
            ))}
          </nav>
        </section>

        <section className="sidebar-panel sidebar-utility-panel" data-prisma-component="SecondaryActionCard">
          <p className="nav-group-title">Utilidades</p>
          <nav className="nav">
            {utilityItems.map((item) => (
              <NavLink
                key={item.href}
                href={item.href}
                title={item.title}
                description={item.description}
                active={currentPath === item.href}
                icon={NAV_ICONS[item.href] ?? "•"}
              />
            ))}
          </nav>
        </section>

        </div>

        <div className="footer-stack">
          <div className="footer-pill" data-prisma-component="TerminalStatusCard">
            <span className="subtle">Gemelo</span>
            <strong>{pcMessages.shell.twinStatus}</strong>
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

          <label className="search-shell" aria-label="Buscar" data-prisma-component="SearchBar">
            <span aria-hidden="true">⌕</span>
            <input readOnly value={pcMessages.shell.searchPlaceholder} />
          </label>

          <div className="user-shell" data-prisma-component="UserMenu">
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
