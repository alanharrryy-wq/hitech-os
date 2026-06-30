import { PRISMA_ORIGINAL_CUSTOMER } from "../../../../../../shared/customer/prisma-original-customer";

export const POS_ENGINE_VERSION = "01A_ENGINE";

export const DEFAULT_BUSINESS_ID = process.env.PRISMA_SYNC_BUSINESS_ID?.trim() || process.env.PRISMA_TABLET_BUSINESS_ID?.trim() || process.env.NEXT_PUBLIC_PRISMA_SYNC_BUSINESS_ID?.trim() || PRISMA_ORIGINAL_CUSTOMER.businessId;
export const DEFAULT_TERMINAL_ID = process.env.PRISMA_TABLET_TERMINAL_ID?.trim() || process.env.NEXT_PUBLIC_PRISMA_TABLET_TERMINAL_ID?.trim() || PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId;
export const DEFAULT_LOCATION = "tablet-floor";
export const DEFAULT_CASHIER = process.env.PRISMA_TABLET_CASHIER?.trim() || "tablet-cashier";

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
export const POS_EVENT_CASH_SESSION_OPENED = "cash.session.opened";
export const POS_EVENT_CASH_MOVEMENT_RECORDED = "cash.movement.recorded";
export const POS_EVENT_SHIFT_OPENED = "shift.opened";
export const POS_EVENT_SHIFT_CLOSED = "shift.closed";
export const POS_EVENT_SUPPLIER_CREATED = "supplier.created";
export const POS_EVENT_SUPPLIER_UPDATED = "supplier.updated";
export const POS_EVENT_SUPPLIER_DISABLED = "supplier.disabled";
export const POS_EVENT_PRODUCT_SUPPLIER_LINKED = "product.supplier.linked";
export const POS_EVENT_PRODUCT_SUPPLIER_UNLINKED = "product.supplier.unlinked";
export const POS_EVENT_PRODUCT_SUPPLIER_UPDATED = "product.supplier.updated";


export const DEFAULT_LOW_STOCK_THRESHOLD = 5;
export const POS_EVENT_SCHEMA_VERSION = "1.0.0";
export const POS_EVENT_SOURCE = "tablet-pos";
