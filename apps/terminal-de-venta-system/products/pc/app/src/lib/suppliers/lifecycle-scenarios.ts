import type { ConfirmReceivingInput, CreateSuggestedOrderInput, PurchaseSimulationInput, RegisterSupplierPaymentInput, SupplierActor } from "./types";

export type SupplierScenarioKind = "simulation" | "create_order" | "receiving" | "payment" | "boundary";
export interface SupplierScenario {
  id: string;
  kind: SupplierScenarioKind;
  title: string;
  goal: string;
  input: PurchaseSimulationInput | CreateSuggestedOrderInput | ConfirmReceivingInput | RegisterSupplierPaymentInput | Record<string, unknown>;
  expected: string[];
  riskCovered: string;
}

const admin: SupplierActor = { id: "usr_admin_prisma", name: "Administrador PRISMA", role: "Administrador" };
const owner: SupplierActor = { id: "usr_owner_prisma", name: "Dueño PRISMA", role: "Dueño" };
const cashier: SupplierActor = { id: "usr_cashier_prisma", name: "Cajero PRISMA", role: "Cajero" };

export const supplierLifecycleScenarios: SupplierScenario[] = [
  {
    id: "SIM_SAFE_BEVERAGES",
    kind: "simulation",
    title: "Simular compra segura de bebidas",
    goal: "Validar que el usuario pueda bajar cantidad sin perder cobertura critica.",
    input: { recommendationId: "rec_sup_beverages", budgetCents: 620000, excludedLineIds: [], quantityOverrides: { "line_prod_001": 48 } },
    expected: ["canCreateOrder=true", "cashImpact no debe ser blocked", "warnings explican si queda caja justa"],
    riskCovered: "Compra util que aun respeta caja."
  },
  {
    id: "SIM_REMOVE_CRITICAL",
    kind: "simulation",
    title: "Quitar producto critico de simulacion",
    goal: "Asegurar que el sistema advierta cuando el usuario excluye una linea critica.",
    input: { recommendationId: "rec_sup_beverages", budgetCents: 620000, excludedLineIds: ["line_prod_001"], quantityOverrides: {} },
    expected: ["warning menciona producto critico", "coverageSummary recalculado", "canCreateOrder depende de lineas restantes"],
    riskCovered: "Usuario protege caja pero puede provocar quiebre."
  },
  {
    id: "ORDER_FROM_RECOMMENDATION",
    kind: "create_order",
    title: "Crear pedido sugerido desde recomendacion",
    goal: "Convertir recomendacion explicable en pedido con folio y auditoria.",
    input: { recommendationId: "rec_sup_beverages", actor: admin, reason: "Se reviso cobertura y proveedor antes del fin de semana." },
    expected: ["code=SUGGESTED_ORDER_CREATED", "source=smart_purchase", "auditEvents incluye smart_purchase.recommendation.converted_to_order"],
    riskCovered: "La recomendacion no muere como postal bonita."
  },
  {
    id: "ORDER_BLOCKED_BY_CASHIER",
    kind: "create_order",
    title: "Bloquear pedido creado por cajero",
    goal: "Validar frontera de permisos entre Tablet/caja y PC/backoffice.",
    input: { recommendationId: "rec_sup_beverages", actor: cashier, reason: "Intento no autorizado desde caja." },
    expected: ["ok=false", "code=PERMISSION_DENIED", "no crea pedido"],
    riskCovered: "Tablet no administra proveedores ni aprueba compras relevantes."
  },
  {
    id: "RECEIVE_WITH_DIFFERENCE",
    kind: "receiving",
    title: "Confirmar recepcion parcial con diferencia",
    goal: "Registrar llegada incompleta, warnings y movimiento de inventario previsto.",
    input: { orderId: "po_001", actor: admin, reason: "Factura recibida con faltante documentado.", receivedUnitsByLineId: { "pol_001": 24, "pol_002": 12 } },
    expected: ["code=RECEIVING_CONFIRMED_WITH_DIFFERENCES", "warnings por SKU", "auditEvents incluye receiving.completed_with_differences"],
    riskCovered: "No maquillar recepciones incompletas."
  },
  {
    id: "RECEIVE_FULL",
    kind: "receiving",
    title: "Confirmar recepcion completa",
    goal: "Validar que una recepcion completa cree movimiento y cuenta por pagar.",
    input: { orderId: "po_002", actor: admin, reason: "Mercancia cotejada contra pedido y factura.", receivedUnitsByLineId: {} },
    expected: ["code=RECEIVING_CONFIRMED", "movementPreview no vacio", "payable generado si total > 0"],
    riskCovered: "Inventario y deuda quedan conectados."
  },
  {
    id: "PAYMENT_PARTIAL",
    kind: "payment",
    title: "Registrar pago parcial",
    goal: "Registrar abono sin cerrar cuenta por pagar completa.",
    input: { payableId: "pay_001", actor: owner, amountCents: 120000, reason: "Abono registrado desde banca." },
    expected: ["code=PAYABLE_PARTIAL_PAYMENT", "remainingCents > 0", "auditEvents incluye supplier_payable.partial_paid"],
    riskCovered: "Caja y deuda no se hacen pato."
  },
  {
    id: "PAYMENT_DENIED_TO_CASHIER",
    kind: "payment",
    title: "Bloquear pago por cajero",
    goal: "Evitar que caja registre pagos administrativos.",
    input: { payableId: "pay_001", actor: cashier, amountCents: 120000, reason: "Intento desde caja." },
    expected: ["ok=false", "code=PERMISSION_DENIED"],
    riskCovered: "Separacion de caja y backoffice."
  },
  {
    id: "BOUNDARY_TABLET_SIGNALS_ONLY",
    kind: "boundary",
    title: "Tablet solo recibe senales ligeras",
    goal: "Validar que las senales no expongan mantenimiento de proveedor.",
    input: { surface: "tablet", forbidden: ["cuentas por pagar", "reglas de credito", "motor de score"] },
    expected: ["signal.allowedAction es aviso", "signal.forbiddenAction declara limite"],
    riskCovered: "Tablet no se convierte en PC chiquita."
  },
  {
    id: "BOUNDARY_MOBILE_APPROVAL_LIMIT",
    kind: "boundary",
    title: "App movil como radar, no escritorio contable",
    goal: "Mantener aprobacion movil limitada y clara.",
    input: { surface: "mobile", allowed: ["ver impacto", "posponer", "aprobar bajo limite"], forbidden: ["recepcion con diferencia", "configuracion pesada"] },
    expected: ["señales moviles tienen accion limitada", "conflictos requieren PC"],
    riskCovered: "Evitar captura pesada en movil."
  }
];

export function getSupplierLifecycleScenarioById(id: string): SupplierScenario | undefined {
  return supplierLifecycleScenarios.find((scenario) => scenario.id === id);
}

export function listSupplierLifecycleScenarioSummary() {
  return supplierLifecycleScenarios.map((scenario) => ({ id: scenario.id, kind: scenario.kind, title: scenario.title, riskCovered: scenario.riskCovered }));
}
