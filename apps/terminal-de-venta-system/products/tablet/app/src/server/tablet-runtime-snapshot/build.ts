import { getTabletRuntimeInfo } from "@/server/pos-runtime";
import { getTabletLicenseGovernor } from "@/server/licensing/tablet-license-service";
import type { TabletCatalogState, TabletConnectionState, TabletRuntimeSnapshot, TabletRuntimeTone } from "@/lib/tablet-runtime-snapshot/shell-contract";
import { TABLET_RUNTIME_VISIBLE_COPY } from "@/lib/tablet-runtime-snapshot/visible-copy";
import { PRISMA_ORIGINAL_CUSTOMER } from "../../../../../../shared/customer/prisma-original-customer";
import type { RuntimeSnapshotInput, RuntimeSnapshotQueryResult } from "./types";
import { getRuntimeConnectionOverride } from "./env";

function todayText(date = new Date()) {
  const yyyy = String(date.getFullYear());
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const dd = String(date.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

function connectionTone(state: TabletConnectionState): TabletRuntimeTone {
  if (state === "offline" || state === "review") return "warn";
  if (state === "pending") return "neutral";
  return "ok";
}

function catalogTone(state: TabletCatalogState): TabletRuntimeTone {
  if (state === "empty" || state === "stale") return "warn";
  if (state === "review") return "neutral";
  return "ok";
}

function licenseLabel(state: string) {
  const labels: Record<string, string> = {
    active: "Licencia activa",
    development: "Licencia activa",
    offline_grace: "Licencia en gracia offline",
    missing: "Licencia pendiente",
    invalid: "Licencia inválida",
    expired: "Licencia vencida",
    suspended: "Licencia suspendida",
    revoked: "Licencia revocada"
  };
  return labels[state] ?? "Licencia por revisar";
}

function licenseTone(state: string, canUseLocalPos: boolean): TabletRuntimeTone {
  if (!canUseLocalPos) return "danger";
  if (state === "offline_grace") return "warn";
  if (state === "active" || state === "development") return "ok";
  return "neutral";
}

function resolveConnectionState(result: RuntimeSnapshotQueryResult): TabletConnectionState {
  const override = getRuntimeConnectionOverride();
  if (override) return override;
  if (result.conflictEvents > 0 || result.failedEvents > 0) return "review";
  if (result.pendingEvents > 0) return "pending";
  return "online";
}

function resolveCatalogState(result: RuntimeSnapshotQueryResult): TabletCatalogState {
  if (result.activeProducts <= 0) return "empty";
  if (result.lowStockProducts > 0) return "review";
  return "ready";
}

export function buildTabletRuntimeSnapshot(input: RuntimeSnapshotInput, result: RuntimeSnapshotQueryResult): TabletRuntimeSnapshot {
  const runtime = getTabletRuntimeInfo();
  const licenseGovernor = getTabletLicenseGovernor();
  const licenseStatus = licenseGovernor.status;
  const connectionState = resolveConnectionState(result);
  const catalogState = resolveCatalogState(result);
  const shiftOpen = Boolean(result.openShift);
  const shiftState = shiftOpen ? "open" : "closed";

  return {
    schemaVersion: "tablet-runtime-snapshot.03b",
    generatedAt: new Date().toISOString(),
    mode: runtime.mode,
    localSalesAllowed: true,
    pcRequiredForBasicSale: false,
    identity: {
      businessId: input.businessId,
      businessName: PRISMA_ORIGINAL_CUSTOMER.displayName,
      storeName: result.storeName || PRISMA_ORIGINAL_CUSTOMER.storeName,
      terminalId: input.terminalId,
      terminalName: result.terminalName || PRISMA_ORIGINAL_CUSTOMER.tabletTerminalName,
      operatorId: input.operatorId,
      operatorName: result.openShift?.cashier || input.operatorName || "Operador"
    },
    shift: {
      state: shiftState,
      label: shiftOpen ? TABLET_RUNTIME_VISIBLE_COPY.shift.open : TABLET_RUNTIME_VISIBLE_COPY.shift.closed,
      tone: shiftOpen ? "ok" : "warn",
      openedAt: result.openShift?.openedAt.toISOString() ?? null,
      cashSessionId: result.openShift?.id ?? null,
      actionHref: "/shift",
      actionLabel: shiftOpen ? "Ver turno" : TABLET_RUNTIME_VISIBLE_COPY.actions.openShift
    },
    connection: {
      state: connectionState,
      label: TABLET_RUNTIME_VISIBLE_COPY.connection[connectionState],
      tone: connectionTone(connectionState),
      pendingEvents: result.pendingEvents,
      failedEvents: result.failedEvents,
      conflictEvents: result.conflictEvents,
      actionHref: "/sync",
      actionLabel: TABLET_RUNTIME_VISIBLE_COPY.actions.reviewPending
    },
    catalog: {
      state: catalogState,
      label: TABLET_RUNTIME_VISIBLE_COPY.catalog[catalogState],
      tone: catalogTone(catalogState),
      activeProducts: result.activeProducts,
      lowStockProducts: result.lowStockProducts,
      inactiveProducts: result.inactiveProducts,
      lastMovementAt: result.lastMovementAt?.toISOString() ?? null,
      actionHref: catalogState === "ready" ? "/catalog" : "/stock",
      actionLabel: catalogState === "ready" ? TABLET_RUNTIME_VISIBLE_COPY.actions.reviewCatalog : TABLET_RUNTIME_VISIBLE_COPY.actions.reviewStock
    },
    sales: result.sales,
    capabilities: [
      { key: "local_sale", label: "Venta local", enabled: licenseGovernor.canUseLocalPos, reason: licenseGovernor.canUseLocalPos ? "La Tablet puede vender sin depender de PC." : "La licencia actual no permite completar ventas locales." },
      { key: "local_stock", label: "Stock local", enabled: true, reason: "Las existencias operativas viven en la terminal." },
      { key: "pending_events", label: "Pendientes visibles", enabled: true, reason: "La conexion y los pendientes se muestran como estado operativo." },
      { key: "contextual_export", label: "Exportacion contextual", enabled: true, reason: "Exportar vive en pantallas con datos, no como pestana principal." }
    ],
    license: {
      state: licenseStatus.state,
      label: licenseLabel(licenseStatus.state),
      tone: licenseTone(licenseStatus.state, licenseGovernor.canUseLocalPos),
      operationalDecision: licenseGovernor.operationalDecision,
      canUseLocalPos: licenseGovernor.canUseLocalPos,
      denialReason: licenseGovernor.denialReason,
      assignmentState: licenseStatus.assignmentState,
      actionHref: "/settings/license",
      actionLabel: licenseGovernor.canUseLocalPos ? "Ver licencia" : "Revisar licencia"
    },
    warnings: [runtime.warning].filter((warning): warning is string => Boolean(warning))
  };
}

export function buildEmptyRuntimeQueryResult(date = todayText()): RuntimeSnapshotQueryResult {
  return {
    businessName: null,
    storeName: null,
    terminalName: null,
    openShift: null,
    pendingEvents: 0,
    failedEvents: 0,
    conflictEvents: 0,
    activeProducts: 0,
    inactiveProducts: 0,
    lowStockProducts: 0,
    lastMovementAt: null,
    sales: {
      date,
      ticketsClosed: 0,
      totalCents: 0,
      unitsSold: 0,
      averageTicketCents: 0
    }
  };
}