import { getSecondaryNavigationForPath } from "@/composition/navigation";
import { normalizePcPathname } from "@/uiux/decision-model";

export function PcSubnav({ currentPath }: { currentPath: string }) {
  const items = getSecondaryNavigationForPath(currentPath);
  const normalizedCurrentPath = normalizePcPathname(currentPath);

  return (
    <nav className="inline-list" aria-label="Subnavegación del módulo" data-prisma-component="PcSubnav" data-subnav-standard="true">
      {items.map((item) => {
        const isActive = normalizePcPathname(item.href) === normalizedCurrentPath;

        return (
          <a
            className={`footer-chip${isActive ? " is-active" : ""}`}
            href={item.href}
            key={`${item.title}-${item.href}`}
            aria-current={isActive ? "page" : undefined}
            data-active={isActive ? "true" : "false"}
            data-subnav-kind={item.status}
          >
            {item.title}
          </a>
        );
      })}
    </nav>
  );
}
