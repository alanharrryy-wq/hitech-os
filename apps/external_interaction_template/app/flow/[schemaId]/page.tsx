import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowUpRight, RotateCcw } from "lucide-react";

import { FlowRunner } from "@components/flow/flow-runner";
import { Button } from "@components/ui/button";
import { Input } from "@components/ui/input";
import { PageHeader } from "@components/ui/page-header";
import { Surface } from "@components/ui/surface";
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
    <div className="grid gap-5">
      <PageHeader
        eyebrow="Flow runner"
        title={`${schema.title} intake flow`}
        description="A guided, lower-friction runner for external users with clearer progress, stronger structure, and token-based resume support."
        children={
          <>
            <span className="rounded-full border border-border/70 bg-surface/80 px-3 py-1.5 text-sm text-muted">Access: {schema.flow.accessMode}</span>
            <span className="rounded-full border border-border/70 bg-surface/80 px-3 py-1.5 text-sm text-muted">Steps: {schema.flow.steps.length}</span>
            <span className="rounded-full border border-border/70 bg-surface/80 px-3 py-1.5 text-sm text-muted">Drafts: {schema.flow.allowDrafts ? "enabled" : "disabled"}</span>
          </>
        }
        actions={
          <>
            <Link href={`/flow/${schema.id}`}>
              <Button variant="ghost" size="sm">
                <RotateCcw className="h-4 w-4" />
                New session
              </Button>
            </Link>
            <Link href="/inbox">
              <Button variant="secondary" size="sm">
                <ArrowUpRight className="h-4 w-4" />
                Open inbox
              </Button>
            </Link>
          </>
        }
      />

      <Surface title="Resume an existing session" subtitle="Paste a secure token to continue from a previous save without losing progress." variant="shell">
        <form action={`/flow/${schema.id}`} method="get" className="grid gap-4 md:grid-cols-[minmax(0,1fr)_auto] md:items-end">
          <label className="grid gap-1.5 text-sm text-muted">
            <span className="eyebrow">Resume token</span>
            <Input name="token" placeholder="ext_xxx" defaultValue={query.token ?? ""} />
          </label>
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" type="submit">
              Resume with token
            </Button>
            <Link href={`/flow/${schema.id}`}>
              <Button variant="ghost">Clear</Button>
            </Link>
          </div>
        </form>
      </Surface>

      <FlowRunner schema={schema} initialRecord={initialRecord} />
    </div>
  );
}
