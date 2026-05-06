import { OfflineExportAuditScreen } from "@components/offline/offline-export-audit-screen";

export const metadata = {
  title: "Offline y export - PRISMA Tablet",
  description: "Auditoría local de ventas, outbox, stock y exportaciones de Tablet."
};

export default function OfflineAuditPage() {
  return <OfflineExportAuditScreen />;
}
