import { PendingOfflineSyncPanelScreen } from "@components/sync/pending-offline-sync-panel-screen";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Pendientes y conexión - PRISMA Tablet",
  description: "Panel operativo de pendientes, fallidos y trabajo local por enviar."
};

export default function SyncPage() {
  return <PendingOfflineSyncPanelScreen />;
}
