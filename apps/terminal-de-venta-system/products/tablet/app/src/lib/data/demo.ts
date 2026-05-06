import { tabletMessages } from "@/lib/i18n/messages/es";

export const salesByHour = [
  ["07:00", 4200], ["08:00", 6700], ["09:00", 9100], ["10:00", 11400], ["11:00", 13800], ["12:00", 15200],
  ["13:00", 14100], ["14:00", 12600], ["15:00", 11900], ["16:00", 12400], ["17:00", 14700], ["18:00", 17100]
] as const;

export const topSkus = [
  { sku: "REF-355ML", name: "Refresco 355 ml", qty: 286, revenue: 8580 },
  { sku: "BOT-600ML", name: "Agua 600 ml", qty: 241, revenue: 4820 },
  { sku: "PAP-ADOBO", name: "Papas adobadas", qty: 184, revenue: 6440 },
  { sku: "CAF-AMER", name: "Café americano", qty: 133, revenue: 4921 },
  { sku: "GOM-MIX", name: "Gomitas mix", qty: 121, revenue: 3025 }
];

export const pendingSync = [
  { id: "evt_001", topic: "sale.created", age: "00:01:22", status: tabletMessages.statuses.pending },
  { id: "evt_002", topic: "ticket.closed", age: "00:03:14", status: tabletMessages.statuses.pending },
  { id: "evt_003", topic: "return.created", age: "00:07:09", status: tabletMessages.statuses.failed },
  { id: "evt_004", topic: "sync.started", age: "00:08:45", status: tabletMessages.statuses.sent }
];
