import { clsx } from "clsx";
import styles from "./nav-link.module.css";

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
    <a
      href={href}
      className={clsx("nav-link", styles.link, active && "active", active && styles.active)}
      aria-current={active ? "page" : undefined}
      aria-label={description ? `${title}. ${description}` : title}
      data-prisma-component="NavItem"
      data-active={active ? "true" : "false"}
    >
      <span className={clsx("nav-icon", styles.icon)} aria-hidden="true">
        {icon ?? "•"}
      </span>
      <span className={clsx("nav-copy", styles.copy)}>
        <span className={clsx("nav-title", styles.title)}>{title}</span>
        {description ? <span className={clsx("nav-desc", styles.description)}>{description}</span> : null}
      </span>
      <span className={styles.activeRail} aria-hidden="true" />
    </a>
  );
}
