import { FormsFlow } from "@/components/forms/forms-flow";
import { resolveFormTypeId } from "@/lib/forms";

interface FormsLandingPageProps {
  searchParams: Promise<{ form?: string }>;
}

export default async function Page({ searchParams }: FormsLandingPageProps) {
  const query = await searchParams;
  const initialFormTypeId = resolveFormTypeId(query.form);

  return <FormsFlow initialFormTypeId={initialFormTypeId} />;
}
