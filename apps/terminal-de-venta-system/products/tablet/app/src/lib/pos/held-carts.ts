import type { CartLine } from "./cart-state";
import { formatMoney } from "./cart-state";
import { calculateCartTotalCents, calculateCartTotalQty, sanitizeCart } from "./cart-engine";

export const POS_HELD_CARTS_STORAGE_KEY = "prisma.tablet.pos.heldCarts.v1";
export const POS_HELD_CARTS_LIMIT = 12;

export type HeldCart = {
  id: string;
  label: string;
  createdAt: string;
  lines: CartLine[];
  totalCents: number;
  totalQty: number;
  source: "pos";
};

function canUseStorage() {
  return typeof window !== "undefined" && Boolean(window.localStorage);
}

function makeId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
  return `held_${Date.now()}_${Math.random().toString(36).slice(2)}`;
}

function safeDate(value: unknown) {
  if (typeof value !== "string") return new Date().toISOString();
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return new Date().toISOString();
  return date.toISOString();
}

export function buildHeldCartLabel(lines: CartLine[], createdAt = new Date()) {
  const cleanLines = sanitizeCart(lines);
  const totalQty = calculateCartTotalQty(cleanLines);
  const totalCents = calculateCartTotalCents(cleanLines);
  const hour = new Intl.DateTimeFormat("es-MX", { hour: "2-digit", minute: "2-digit" }).format(createdAt);
  return `Ticket ${hour} · ${totalQty} pzas · ${formatMoney(totalCents)}`;
}

export function normalizeHeldCart(raw: unknown): HeldCart | null {
  if (!raw || typeof raw !== "object") return null;
  const item = raw as Partial<HeldCart>;
  const lines = sanitizeCart(item.lines ?? []);
  if (!item.id || !lines.length) return null;
  const createdAt = safeDate(item.createdAt);
  const totalCents = calculateCartTotalCents(lines);
  const totalQty = calculateCartTotalQty(lines);
  return {
    id: String(item.id),
    label: typeof item.label === "string" && item.label.trim() ? item.label : buildHeldCartLabel(lines, new Date(createdAt)),
    createdAt,
    lines,
    totalCents,
    totalQty,
    source: "pos"
  };
}

export function readHeldCartsFromStorage(): HeldCart[] {
  if (!canUseStorage()) return [];
  const raw = window.localStorage.getItem(POS_HELD_CARTS_STORAGE_KEY);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw) as unknown[];
    if (!Array.isArray(parsed)) return [];
    return parsed.map(normalizeHeldCart).filter((item): item is HeldCart => Boolean(item)).slice(0, POS_HELD_CARTS_LIMIT);
  } catch {
    return [];
  }
}

export function writeHeldCartsToStorage(heldCarts: HeldCart[]) {
  if (!canUseStorage()) return;
  const clean = heldCarts.map(normalizeHeldCart).filter((item): item is HeldCart => Boolean(item)).slice(0, POS_HELD_CARTS_LIMIT);
  if (!clean.length) {
    window.localStorage.removeItem(POS_HELD_CARTS_STORAGE_KEY);
    return;
  }
  window.localStorage.setItem(POS_HELD_CARTS_STORAGE_KEY, JSON.stringify(clean));
}

export function createHeldCart(lines: CartLine[]): HeldCart | null {
  const cleanLines = sanitizeCart(lines);
  if (!cleanLines.length) return null;
  const createdAt = new Date();
  return {
    id: makeId(),
    label: buildHeldCartLabel(cleanLines, createdAt),
    createdAt: createdAt.toISOString(),
    lines: cleanLines,
    totalCents: calculateCartTotalCents(cleanLines),
    totalQty: calculateCartTotalQty(cleanLines),
    source: "pos"
  };
}

export function addHeldCart(current: HeldCart[], lines: CartLine[]): { heldCarts: HeldCart[]; heldCart: HeldCart | null; warning?: string } {
  const heldCart = createHeldCart(lines);
  if (!heldCart) return { heldCarts: current, heldCart: null, warning: "No hay ticket activo para guardar." };
  const cleanCurrent = current.map(normalizeHeldCart).filter((item): item is HeldCart => Boolean(item));
  const next = [heldCart, ...cleanCurrent.filter((item) => item.id !== heldCart.id)].slice(0, POS_HELD_CARTS_LIMIT);
  return { heldCarts: next, heldCart };
}

export function removeHeldCart(current: HeldCart[], heldCartId: string): HeldCart[] {
  return current.filter((item) => item.id !== heldCartId);
}
