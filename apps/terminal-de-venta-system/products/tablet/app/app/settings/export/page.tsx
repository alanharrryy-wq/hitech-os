import { ExportSettingsScreen } from "@components/tablet-pos/touch-pos-ui";
import { SettingsWorkspace } from "@components/settings/settings-workspace";
import { TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";

export const metadata = {
  title: "Exportaciones - PRISMA Tablet",
  description: "Exportación local de ventas, pendientes y movimientos."
};

export default function SettingsExportPage() {
  return (
    <SettingsWorkspace
      currentPath="/settings/export"
      title="Exportaciones locales"
      subtitle="Descarga únicamente las salidas operativas disponibles en esta Tablet."
      status={<TabletShellStatusPill tone="neutral">Archivos locales</TabletShellStatusPill>}
    >
      <ExportSettingsScreen embedded />
    </SettingsWorkspace>
  );
}
