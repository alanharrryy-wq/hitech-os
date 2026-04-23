export type KpiCard = { label: string; value: string; note: string };
export type TableRow = Record<string, string | number>;

export type PosArea = "launcher" | "sales" | "checkout" | "shift" | "returns" | "sync";

export type SyncEventEnvelope = {
  id: string;
  topic: string;
  aggregateId: string;
  createdAt: string;
  status: "pending" | "sent" | "failed";
};
