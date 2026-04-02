import Link from "next/link";
import { notFound } from "next/navigation";

import { FlowRunner } from "@components/flow/flow-runner";
import { Surface } from "@components/ui/surface";
import { Button } from "@components/ui/button";
import { Input } from "@components/ui/input";
import { getSchema } from "@/lib/core/schema-registry";
import { getRecordByToken } from "@/lib/services/records";

export const dynamic = "force-dynamic";

interface FlowPageProps {
  params: Promise<{ schemaId: string }>;
  searchParams: Promise<{ token?: string; mode?: string }>;
}

export default async function FlowPage({ params, searchParams }: FlowPageProps) {
  const { schemaId } = await params;
  const query = await searchParams;

  let schema;
  try {
    schema = getSchema(schemaId);
  } catch {
    notFound();
  }

  const initialRecord = query.token ? await getRecordByToken(query.token) : null;

  return (
    <div className="grid gap-4">
      <Surface title={`${schema.title} Flow Runner`} subtitle="Mobile-first external runner with validation, drafts and token resume support.">
        <div className="flex flex-wrap items-end gap-2">
          <form action={`/flow/${schema.id}`} method="get" className="flex flex-wrap items-end gap-2">
            <label className="grid gap-1 text-xs text-muted">
              Resume token
              <Input name="token" placeholder="ext_xxx" className="w-64" defaultValue={query.token ?? ""} />
            </label>
            <Button variant="secondary" type="submit" className="h-10">
              Resume
            </Button>
          </form>
          <Link href={`/flow/${schema.id}`}>
            <Button variant="ghost" className="h-10">
              New flow session
            </Button>
          </Link>
        </div>
      </Surface>

      <FlowRunner schema={schema} initialRecord={initialRecord} />
    </div>
  );
}
