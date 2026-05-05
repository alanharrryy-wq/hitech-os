import { CatalogDashboard } from "@components/catalog/catalog-dashboard";
import { getCatalogWorkspace } from "@/server/services/catalog.service";

export const dynamic = "force-dynamic";

type SearchParams = Record<string, string | string[] | undefined>;

type CatalogPageProps = {
  searchParams?: SearchParams | Promise<SearchParams>;
};

function single(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] : value;
}

export default async function CatalogPage({ searchParams }: CatalogPageProps) {
  const resolved = searchParams ? await searchParams : {};
  const workspace = await getCatalogWorkspace({
    q: single(resolved.q) ?? "",
    status: single(resolved.status) ?? "all",
    category: single(resolved.category) ?? "all",
    issue: single(resolved.issue) ?? "all",
    selectedSku: single(resolved.sku) ?? ""
  });

  return <CatalogDashboard workspace={workspace} />;
}
