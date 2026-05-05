import type { ReactNode } from "react";
import { getNavigation } from "@/composition/navigation";
import { NavLink } from "./nav-link";
import { tabletMessages } from "@/lib/i18n/messages/es";

export function AppShell({ currentPath, children }: { currentPath: string; children: ReactNode }) {
  const nav = getNavigation();
  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">{tabletMessages.shell.brand}</div>
        <div className="subtle">{tabletMessages.shell.subtitle}</div>
        <nav className="nav">
          <NavLink href="/" title={tabletMessages.shell.home} active={currentPath === "/"} />
          {nav.map((item) => (
            <NavLink key={item.href} href={item.href} title={item.title} active={currentPath === item.href} />
          ))}
        </nav>
        <div style={{ marginTop: 20 }} className="footer-note">{tabletMessages.shell.footer}</div>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}
