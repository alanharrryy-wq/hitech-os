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
        ? { title: "Dashboard", description: "KPIs y sync" }
        : nav.find((item) => item.href === currentPath);
  const controlItems = nav.filter((item) => item.navGroup === "control");
  const utilityItems = nav.filter((item) => item.navGroup === "operation");

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-row">
            <span className="brand-mark" aria-hidden="true">
              ✦
            </span>
            <div>
              <div className="brand">{pcMessages.shell.brand}</div>
              <div className="subtle">{pcMessages.shell.subtitle}</div>
            </div>
          </div>
        </div>

        <section className="sidebar-panel">
          <p className="nav-group-title">Navegación</p>
          <nav className="nav">
            <NavLink href="/" title={pcMessages.shell.home} description="vista ejecutiva" active={currentPath === "/"} icon={NAV_ICONS["/"]} />
            <NavLink href="/dashboard" title="Dashboard" description="KPIs y sync" active={currentPath === "/dashboard"} icon={NAV_ICONS["/dashboard"]} />
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

        <section className="sidebar-panel">
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

        <div className="sidebar-spacer" />

        <div className="footer-stack">
          <div className="footer-pill">
            <span className="subtle">Twin</span>
            <strong>{pcMessages.shell.twinStatus}</strong>
          </div>
          <div className="footer-pill">
            <span className="subtle">Última sync</span>
            <strong>{pcMessages.shell.lastSync}</strong>
          </div>
          <div className="footer-actions">
            <div className="footer-chip">Docs</div>
            <div className="footer-chip">Sync</div>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div className="topbar-brand">
            <span className="brand-mark" aria-hidden="true" style={{ width: 28, height: 28, fontSize: 14 }}>
              ⬢
            </span>
            <span>{current?.title ?? pcMessages.shell.home}</span>
          </div>

          <label className="search-shell" aria-label="Buscar">
            <span aria-hidden="true">⌕</span>
            <input readOnly value={pcMessages.shell.searchPlaceholder} />
          </label>

          <div className="user-shell">
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
