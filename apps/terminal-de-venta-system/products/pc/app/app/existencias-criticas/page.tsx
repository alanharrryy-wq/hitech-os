import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";

type SearchParams = Promise<{ urgency?: string | string[]; q?: string | string[] }>;

function single(value?: string | string[]) {
  return Array.isArray(value) ? value[0] : value;
}

export default async function ExistenciasCriticasRedirect({ searchParams }: { searchParams?: SearchParams }) {
  const resolved = searchParams ? await searchParams : {};
  const urgency = single(resolved.urgency);
  const state = urgency === "today" ? "critical" : urgency === "3days" || urgency === "week" ? "low" : "critical";
  const params = new URLSearchParams({ state });
  const query = single(resolved.q)?.trim();
  if (query) params.set("q", query);
  redirect(`/stock?${params.toString()}`);
}
