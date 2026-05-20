import type { TabletRuntimeSnapshot, TabletRuntimeTone } from "@/lib/tablet-runtime-snapshot/shell-contract";

export type OperationalGateCode = "OPEN_CASH_SESSION" | "SHIFT_NOT_OPEN";

export type CanSellDecision = {
  canSell: boolean;
  canOperatePos: boolean;
  canShowSellNavigation: boolean;
  canAddProduct: boolean;
  canCheckout: boolean;
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
      canShowSellNavigation: true,
      canAddProduct: true,
      canCheckout: true,
      code: "OPEN_CASH_SESSION",
      tone: "ok",
      title: "Caja abierta",
      detail: "Turno abierto: la Tablet puede vender con caja local trazable.",
      actionHref: "/pos",
      actionLabel: "Vender"
    };
  }

  return {
    canSell: false,
    canOperatePos: false,
    canShowSellNavigation: false,
    canAddProduct: false,
    canCheckout: false,
    code: "SHIFT_NOT_OPEN",
    tone: "warn",
    title: "Caja cerrada",
    detail: "Abre turno/caja antes de vender. PRISMA Tablet no abre turnos automáticamente para completar ventas.",
    actionHref: "/shift",
    actionLabel: "Abrir turno"
  };
}

export function hasOpenShiftOrCashSession(snapshot: Pick<TabletRuntimeSnapshot, "shift">): boolean {
  return snapshot.shift.state === "open" || Boolean(snapshot.shift.cashSessionId);
}

export function decideCanSellFromRuntimeSnapshot(snapshot: TabletRuntimeSnapshot): CanSellDecision {
  return buildDecision(hasOpenShiftOrCashSession(snapshot));
}

export function decideCanSellFromShiftSummary(shift: { status?: string | null; canSell?: boolean | null; id?: string | null } | null | undefined): CanSellDecision {
  return buildDecision(Boolean(shift && (shift.status === "OPEN" || shift.canSell === true || shift.id)));
}

export const CLOSED_CASH_OPERATIONAL_COPY = buildDecision(false);
