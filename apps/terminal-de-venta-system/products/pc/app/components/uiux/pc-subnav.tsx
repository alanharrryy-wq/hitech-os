import { getPcSubnavItems } from "@/uiux/decision-model";

export function PcSubnav({ currentPath }: { currentPath: string }) {
  const items = getPcSubnavItems(currentPath);

  return (
    <nav className="inline-list" aria-label="Subnavegación del módulo" data-prisma-component="PcSubnav" data-subnav-standard="true">
      {items.map((item) => (
        <a className="footer-chip" href={item.href} key={`${item.label}-${item.href}`} data-subnav-kind={item.kind}>
          {item.label}
        </a>
      ))}
    </nav>
  );
}
