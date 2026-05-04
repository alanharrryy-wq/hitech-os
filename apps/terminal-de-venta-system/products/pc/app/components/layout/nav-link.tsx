export function NavLink({
  href,
  title,
  active,
  description,
  icon
}: {
  href: string;
  title: string;
  active: boolean;
  description?: string;
  icon?: string;
}) {
  return (
    <a href={href} className={active ? "active" : ""} aria-current={active ? "page" : undefined} data-prisma-component="NavItem" data-active={active ? "true" : undefined}>
      <span className="nav-icon" aria-hidden="true">
        {icon ?? "•"}
      </span>
      <span className="nav-copy">
        <span className="nav-title">{title}</span>
        {description ? <span className="nav-desc">{description}</span> : null}
      </span>
    </a>
  );
}
