export const FEATURE_KEYS = [
  "pos.open",
  "pos.product.search",
  "pos.sale.create",
  "pos.sale.complete",
  "pos.ticket.view",
  "pos.sales.today.view",
  "report.today.view",
  "inventory.local.decrement",
  "export.sales.basic",
  "shift.open",
  "shift.close",
  "pos.sale.cancel",
  "pos.return.create",
  "inventory.local.adjust",
  "event.outbox.view",
  "export.advanced",
  "report.operational.view",
  "pc.open",
  "pc.dashboard.view",
  "pc.dashboard.executive",
  "catalog.write",
  "stock.adjust",
  "inventory.counts",
  "purchase.write",
  "receiving.write",
  "replenishment.view",
  "audit.view",
  "sync.managed",
  "sync.conflict.resolve",
  "multi.branch",
  "multi.terminal",
  "multi.user.permissions",
  "forecast.replenishment",
  "advanced.analytics"
] as const;

export type FeatureKey = (typeof FEATURE_KEYS)[number] | (string & {});

export const BASIC_POS_FEATURES = new Set<string>([
  "pos.open",
  "pos.product.search",
  "pos.sale.create",
  "pos.sale.complete",
  "pos.ticket.view",
  "pos.sales.today.view",
  "report.today.view",
  "inventory.local.decrement",
  "export.sales.basic"
]);

export const TABLET_PRO_FEATURES = new Set<string>([
  "shift.open",
  "shift.close",
  "pos.sale.cancel",
  "pos.return.create",
  "inventory.local.adjust",
  "event.outbox.view",
  "export.advanced",
  "report.operational.view"
]);

export const PC_BACKOFFICE_FEATURES = new Set<string>([
  "pc.open",
  "pc.dashboard.view",
  "pc.dashboard.executive",
  "catalog.write",
  "stock.adjust",
  "inventory.counts",
  "purchase.write",
  "receiving.write",
  "replenishment.view",
  "audit.view",
  "sync.managed",
  "sync.conflict.resolve",
  "multi.branch",
  "multi.terminal",
  "multi.user.permissions",
  "forecast.replenishment",
  "advanced.analytics"
]);

export function isKnownFeatureKey(key: string): boolean {
  return FEATURE_KEYS.includes(key as never);
}
