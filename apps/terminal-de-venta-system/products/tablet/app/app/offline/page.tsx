import { OfflineResilienceWorkspace } from "@components/offline/offline-export-audit-screen";

export const metadata = {
  title: "Sin conexión y respaldo - PRISMA Tablet",
  description: "Revisión local de ventas, pendientes, existencias y respaldos de Tablet."
};

export default function OfflineAuditPage() {
  return <OfflineResilienceWorkspace />;
}
