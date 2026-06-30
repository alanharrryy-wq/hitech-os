import { InventoryWorkspaceView } from "@components/inventory/inventory-workspace";
import { getInventoryWorkspace } from "@/server/services/inventory-ledger.service";

export const dynamic = "force-dynamic";

type SearchParams = Record<string, string | string[] | undefined>;

type AuditInventoryPageProps = {
  searchParams?: SearchParams | Promise<SearchParams>;
};

function single(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] : value;
}

export default async function AuditoriaInventarioPage({ searchParams }: AuditInventoryPageProps) {
  const resolved = searchParams ? await searchParams : {};
  const workspace = await getInventoryWorkspace({
    q: single(resolved.q) ?? "",
    location: single(resolved.location) ?? "all",
    state: "all",
    countStatus: "all",
    auditSeverity: single(resolved.severity) ?? single(resolved.auditSeverity) ?? "all"
  });

  return <InventoryWorkspaceView view="audit" workspace={workspace} currentPath="/auditoria-inventario" />;
}
