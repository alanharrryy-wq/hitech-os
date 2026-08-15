import { getPcSubnavItems, normalizePcPathname } from "@/uiux/decision-model";

const HIDDEN_SURFACE_TRUTH_SUBNAV_ROUTES = new Set([
  "/acciones-masivas",
  "/contratos-reporte",
  "/detalle-registros",
  "/estados-operativos",
  "/forecast-basico",
  "/scorecards-negocio",
  "/tablas-operativas",
  "/tablero-kpi",
  "/vistas-ejecutivas"
]);

export function PcSubnav({ currentPath }: { currentPath: string }) {
  const items = getPcSubnavItems(currentPath).filter((item) => !HIDDEN_SURFACE_TRUTH_SUBNAV_ROUTES.has(item.href));
  const normalizedCurrentPath = normalizePcPathname(currentPath);

  return (
    <nav className="inline-list" aria-label="Subnavegación del módulo" data-prisma-component="PcSubnav" data-subnav-standard="true">
      {items.map((item) => {
        const isActive = normalizePcPathname(item.href) === normalizedCurrentPath;

        return (
          <a
            className={`footer-chip${isActive ? " is-active" : ""}`}
            href={item.href}
            key={`${item.label}-${item.href}`}
            aria-current={isActive ? "page" : undefined}
            data-active={isActive ? "true" : "false"}
            data-subnav-kind={item.kind}
          >
            {item.label}
          </a>
        );
      })}
    </nav>
  );
}
