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
      className={`${styles.link}${active ? ` ${styles.active}` : ""}`}
      aria-current={active ? "page" : undefined}
      aria-label={description ? `${title}. ${description}` : title}
      data-prisma-component="NavItem"
      data-active={active ? "true" : "false"}
    >
      <span className={styles.icon} aria-hidden="true">
        {icon ?? "•"}
      </span>
      <span className={styles.copy}>
        <span className={styles.title}>{title}</span>
        {description ? <span className={styles.description}>{description}</span> : null}
      </span>
      <span className={styles.activeRail} aria-hidden="true" />
    </a>
  );
}
