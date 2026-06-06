import { DecisionScreen } from "@components/uiux/decision-screen";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  return (
    <DecisionScreen
      currentPath="/dashboard"
      title="Hoy"
      subtitle="Resumen de lo que necesita atención antes de vender, comprar o cerrar caja."
      status="Listo para operar"
      tableTitle="Prioridades del día"
      tableSubtitle="Pendientes entendibles para dueño, gerente y soporte."
      columns={["Prioridad", "Estado", "Qué hacer"]}
      rows={[
        { Prioridad: "Productos críticos", Estado: "Revisar", "Qué hacer": "Abrir Inventario y atender existencias bajas" },
        { Prioridad: "Sincronización", Estado: "Vigilar", "Qué hacer": "Revisar cambios pendientes PC-tablet" },
        { Prioridad: "Ventas y caja", Estado: "Operativo", "Qué hacer": "Validar cortes y movimientos sensibles" }
      ]}
    />
  );
}
