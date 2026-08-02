import type { TabletRuntimeSnapshot, TabletRuntimeTone } from "@/lib/tablet-runtime-snapshot/shell-contract";

export type OperationalGateCode = "OPEN_CASH_SESSION" | "SHIFT_NOT_OPEN" | "LICENSE_BLOCKED" | "POS_PREVIEW";

export type CanSellDecision = {
  canSell: boolean;
  canOperatePos: boolean;
  canBrowseCatalog: boolean;
  canShowSellNavigation: boolean;
  canAddProduct: boolean;
  canCheckout: boolean;
  previewOnly: boolean;
  code: OperationalGateCode;
  tone: TabletRuntimeTone;
  title: string;
  detail: string;
  actionHref: string;
  actionLabel: string;
};

function buildDecision(open: boolean): CanSellDecision {
  if (open) {
    return {
      canSell: true,
      canOperatePos: true,
      canBrowseCatalog: true,
      canShowSellNavigation: true,
      canAddProduct: true,
      canCheckout: true,
      previewOnly: false,
      code: "OPEN_CASH_SESSION",
      tone: "ok",
      title: "Caja abierta",
      detail: "Turno abierto: la Tablet puede vender con caja local trazable.",
      actionHref: "/pos",
      actionLabel: "Vender"
    };
  }

  // PRISMA_SHIFT_CLOSED_CATALOG_BROWSE_01
  // Browsing is read-only while the shift is closed; cart mutation and checkout remain blocked.
  return {
    canSell: false,
    canOperatePos: true,
    canBrowseCatalog: true,
    canShowSellNavigation: true,
    canAddProduct: false,
    canCheckout: false,
    previewOnly: false,
    code: "SHIFT_NOT_OPEN",
    tone: "warn",
    title: "Caja cerrada",
    detail: "Puedes revisar el catálogo. Abre turno/caja para agregar productos y cobrar; PRISMA no registra ventas sin una sesión abierta.",
    actionHref: "/shift",
    actionLabel: "Abrir turno"
  };
}

function buildPreviewDecision(): CanSellDecision {
  return {
    canSell: false,
    canOperatePos: true,
    canBrowseCatalog: false,
    canShowSellNavigation: true,
    canAddProduct: false,
    canCheckout: false,
    previewOnly: true,
    code: "POS_PREVIEW",
    tone: "neutral",
    title: "Vista POS de consulta",
    detail: "Esta Tablet no tiene una terminal local registrada. Puedes recorrer la interfaz, pero el catálogo, carrito y cobro permanecen bloqueados y no se registra ninguna venta.",
    actionHref: "/setup",
    actionLabel: "Configurar terminal"
  };
}

function buildLicenseBlockedDecision(snapshot: TabletRuntimeSnapshot): CanSellDecision | null {
  const license = snapshot.license;
  if (license.canUseLocalPos) return null;

  return {
    canSell: false,
    canOperatePos: false,
    canBrowseCatalog: false,
    canShowSellNavigation: false,
    canAddProduct: false,
    canCheckout: false,
    previewOnly: false,
    code: "LICENSE_BLOCKED",
    tone: license.tone === "danger" ? "danger" : "warn",
    title: license.label || "Licencia requiere atención",
    detail: license.denialReason
      ? `La licencia bloquea venta local (${license.denialReason}). Revisa Licencia y equipo antes de vender.`
      : "La licencia actual no permite completar ventas locales. Revisa Licencia y equipo antes de vender.",
    actionHref: license.actionHref || "/settings/license",
    actionLabel: license.actionLabel || "Revisar licencia"
  };
}

export function hasOpenShiftOrCashSession(snapshot: Pick<TabletRuntimeSnapshot, "shift">): boolean {
  return snapshot.shift.state === "open" || Boolean(snapshot.shift.cashSessionId);
}

export function decideCanSellFromRuntimeSnapshot(snapshot: TabletRuntimeSnapshot): CanSellDecision {
  if (!snapshot.terminalRegistered) return buildPreviewDecision();
  return buildLicenseBlockedDecision(snapshot) ?? buildDecision(hasOpenShiftOrCashSession(snapshot));
}

export function decideCanSellFromShiftSummary(shift: { status?: string | null; canSell?: boolean | null; id?: string | null } | null | undefined): CanSellDecision {
  return buildDecision(Boolean(shift && (shift.status === "OPEN" || shift.canSell === true || shift.id)));
}

export const CLOSED_CASH_OPERATIONAL_COPY = buildDecision(false);
