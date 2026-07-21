import { DataSettingsOverview, SettingsWorkspace } from "@components/settings/settings-workspace";
import { TabletShellStatusPill } from "@components/tablet-shell/prisma-tablet-shell";

export default function DataSettingsPage() {
  return (
    <SettingsWorkspace
      currentPath="/settings/data"
      title="Datos y respaldo"
      subtitle="Continuidad local, auditoría y salidas disponibles sin inventar una segunda base."
      status={<TabletShellStatusPill tone="ok">Guardado local</TabletShellStatusPill>}
    >
      <DataSettingsOverview />
    </SettingsWorkspace>
  );
}
