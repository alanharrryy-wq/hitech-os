export function NavLink({ href, title, active }: { href: string; title: string; active: boolean }) {
  return <a href={href} className={active ? "active" : undefined}>{title}</a>;
}
