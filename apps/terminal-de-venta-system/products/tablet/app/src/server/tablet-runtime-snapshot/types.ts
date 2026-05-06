import type { TabletRuntimeSnapshot } from "@/lib/tablet-runtime-snapshot/shell-contract";

export type RuntimeSnapshotInput = {
  businessId: string;
  terminalId: string;
  operatorId: string;
  operatorName: string;
  date?: string;
};

export type RuntimeSnapshotQueryResult = {
  businessName: string | null;
  storeName: string | null;
  terminalName: string | null;
  openShift: {
    id: string;
    openedAt: Date;
    cashier: string;
  } | null;
  pendingEvents: number;
  failedEvents: number;
  conflictEvents: number;
  activeProducts: number;
  inactiveProducts: number;
  lowStockProducts: number;
  lastMovementAt: Date | null;
  sales: {
    date: string;
    ticketsClosed: number;
    totalCents: number;
    unitsSold: number;
    averageTicketCents: number;
  };
};

export type RuntimeSnapshotBuildResult = TabletRuntimeSnapshot;
