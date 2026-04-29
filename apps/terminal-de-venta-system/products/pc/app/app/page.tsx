import { ExecutiveDashboard } from "@components/backoffice/executive-dashboard";
import { getBackofficeDashboard } from "@/lib/backoffice/dashboard";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const dashboard = await getBackofficeDashboard();
  return <ExecutiveDashboard dashboard={dashboard} currentPath="/" />;
}
