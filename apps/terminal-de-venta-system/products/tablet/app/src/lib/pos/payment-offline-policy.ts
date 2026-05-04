export type OfflinePolicyInput = {
  runtimeMode: "standalone" | "managed" | "degraded_managed";
  connectionState: "online" | "offline" | "unstable";
  hasLocalCatalog: boolean;
  hasOpenShift: boolean;
  pendingEvents: number;
  cartTotalCents: number;
  maxOfflineSaleCents?: number;
};

export type OfflinePolicyDecision = {
  canSell: boolean;
  canComplete: boolean;
  statusLabel: string;
  operatorMessage: string;
  blockers: string[];
  warnings: string[];
};

export function evaluateOfflineSalePolicy(input: OfflinePolicyInput): OfflinePolicyDecision {
  const blockers: string[] = [];
  const warnings: string[] = [];
  const limit = input.maxOfflineSaleCents ?? 100_000;
  if (!input.hasLocalCatalog) blockers.push("No hay catálogo local para vender sin conexión.");
  if (!input.hasOpenShift) blockers.push("Abre turno antes de cerrar ventas.");
  if (input.connectionState !== "online") warnings.push("La venta puede quedar pendiente por enviar.");
  if (input.pendingEvents > 0) warnings.push(`Hay ${input.pendingEvents} movimientos pendientes.`);
  if (input.connectionState !== "online" && input.cartTotalCents > limit) blockers.push("El monto supera el límite permitido en modo sin conexión.");
  if (input.runtimeMode === "managed" && input.connectionState === "offline") warnings.push("La Tablet opera en modo administrado degradado: vende localmente y sincroniza después.");
  const canSell = blockers.length === 0;
  const statusLabel = blockers.length ? "Revisar operación" : warnings.length ? "Venta local pendiente" : "Listo para cobrar";
  const operatorMessage = blockers[0] ?? warnings[0] ?? "Puedes cerrar la venta con normalidad.";
  return { canSell, canComplete: canSell, statusLabel, operatorMessage, blockers, warnings };
}
