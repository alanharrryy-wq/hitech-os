import type { ReactNode } from "react";
import { PrismaRouteSurface, type PrismaRouteAction, type PrismaRouteMetric, type TabletSurfaceIntent } from "./prisma-route-surface";

type AdapterProps = {
  actions?: ReactNode;
  children: ReactNode;
  description?: ReactNode;
  emptyState?: ReactNode;
  metrics?: PrismaRouteMetric[];
  primaryAction?: PrismaRouteAction;
  rail?: ReactNode;
  routeId: string;
  statusLabel?: ReactNode;
  title?: ReactNode;
};

function SurfaceAdapter({
  children,
  description,
  intent,
  routeId,
  title,
  ...props
}: AdapterProps & { intent: TabletSurfaceIntent }) {
  return (
    <PrismaRouteSurface
      {...props}
      routeId={routeId}
      intent={intent}
      title={title ?? routeId}
      description={description ?? "Superficie Tablet operativa nocturna, táctil y translúcida con jerarquía clara."}
    >
      {children}
    </PrismaRouteSurface>
  );
}

export function TabletGenericSurfaceV2(props: AdapterProps) {
  return <SurfaceAdapter {...props} intent="generic" />;
}

export function TabletListSurfaceV2(props: AdapterProps) {
  return <SurfaceAdapter {...props} intent="generic" />;
}

export function TabletDetailSurfaceV2(props: AdapterProps) {
  return <SurfaceAdapter {...props} intent="detail" />;
}

export function TabletFormSurfaceV2(props: AdapterProps) {
  return <SurfaceAdapter {...props} intent="form" />;
}

export function TabletReportSurfaceV2(props: AdapterProps) {
  return <SurfaceAdapter {...props} intent="report" />;
}

export function TabletSettingsSurfaceV2(props: AdapterProps) {
  return <SurfaceAdapter {...props} intent="settings" />;
}

export function TabletSyncSurfaceV2(props: AdapterProps) {
  return <SurfaceAdapter {...props} intent="sync" />;
}

export function TabletInventorySurfaceV2(props: AdapterProps) {
  return <SurfaceAdapter {...props} intent="inventory" />;
}

export function TabletSalesSurfaceV2(props: AdapterProps) {
  return <SurfaceAdapter {...props} intent="sales" />;
}

export function TabletCatalogSurfaceV2(props: AdapterProps) {
  return <SurfaceAdapter {...props} intent="catalog" />;
}

export function TabletCustomerSurfaceV2(props: AdapterProps) {
  return <SurfaceAdapter {...props} intent="customer" />;
}

export function TabletHomeSurfaceV2(props: AdapterProps) {
  return <SurfaceAdapter {...props} intent="home" />;
}
