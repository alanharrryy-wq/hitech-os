import { site } from "@/content/site";

export function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <strong>PRISMA</strong>
        <span>{site.tagline}</span>
        <span>{site.email}</span>
      </div>
    </footer>
  );
}
