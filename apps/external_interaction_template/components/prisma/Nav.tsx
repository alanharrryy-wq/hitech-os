import { site } from "@/content/site";

export function Nav() {
  return (
    <header className="nav">
      <div className="nav-inner">
        <a className="brand" href="/" aria-label="PRISMA inicio">
          <span className="brand-mark" aria-hidden="true" />
          <span>PRISMA</span>
        </a>
        <nav className="nav-links" aria-label="Navegación principal">
          <a href="/commerce">Commerce</a>
          <a href="/industrial">Industrial</a>
          <a href="/field">Field</a>
          <a href="/control">Control</a>
        </nav>
        <a className="nav-cta" href={site.whatsappUrl}>Demo</a>
      </div>
    </header>
  );
}
