export const POS_ENGINE_VERSION = "01A_ENGINE";

export const DEFAULT_BUSINESS_ID = "biz_tablet_standalone";
export const DEFAULT_TERMINAL_ID = "terminal_tablet_local_01";
export const DEFAULT_LOCATION = "tablet-floor";
export const DEFAULT_CASHIER = "tablet-cashier";

export const SALE_STATUS_COMPLETED = "COMPLETED";
export const SALE_STATUS_CANCELLED = "CANCELLED";

export const STOCK_MOVEMENT_SALE = "SALE";
export const STOCK_REASON_SALE_COMPLETED = "sale.completed";

export const OUTBOX_STATUS_PENDING = "pending";
export const OUTBOX_STATUS_SENT = "sent";
export const OUTBOX_STATUS_FAILED = "failed";
export const OUTBOX_STATUS_ACKED = "acked";
export const OUTBOX_STATUS_CONFLICT = "conflict";

export const POS_EVENT_SALE_CREATED = "sale.created";
export const POS_EVENT_SALE_COMPLETED = "sale.completed";
export const POS_EVENT_TICKET_CLOSED = "ticket.closed";
export const POS_EVENT_STOCK_DECREMENTED = "stock.decremented";
export const POS_EVENT_INVENTORY_LOW_STOCK_DETECTED = "inventory.low_stock_detected";

export const DEFAULT_LOW_STOCK_THRESHOLD = 5;
export const POS_EVENT_SCHEMA_VERSION = "1.0.0";
export const POS_EVENT_SOURCE = "tablet-pos";
