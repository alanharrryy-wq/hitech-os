export type KpiCard = { label: string; value: string; note: string };
export type TableRow = Record<string, string | number>;

export type InventoryArea =
  | "launcher"
  | "catalog"
  | "stock"
  | "counts"
  | "purchasing"
  | "receiving"
  | "replenishment"
  | "audit"
  | "sync";

export type SyncEventEnvelope = {
  id: string;
  topic: string;
  aggregateId: string;
  createdAt: string;
  status: "pending" | "sent" | "failed";
};
