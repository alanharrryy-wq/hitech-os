import Link from "next/link";
import { ArrowRight, FolderSync, ListChecks, PlayCircle, Sparkles } from "lucide-react";

import { Badge } from "@components/ui/badge";
import { Button } from "@components/ui/button";
import { PageHeader } from "@components/ui/page-header";
import { StatCard } from "@components/ui/stat-card";
import { Surface } from "@components/ui/surface";
import { listSchemas } from "@/lib/core/schema-registry";
import { listRecords } from "@/lib/services/records";
import { listSyncCenterData } from "@/lib/services/actions";

export const dynamic = "force-dynamic";

export default async function LauncherPage() {
  const schemas = listSchemas();
  const [records, syncData] = await Promise.all([listRecords(), listSyncCenterData()]);

  return (
    <div className="grid gap-5">
      <PageHeader
        eyebrow="Launcher"
        title="Premium control surface for external interaction flows"
        description="Launch schema-driven intake flows, review active records, and monitor sync outcomes from one calmer, more deliberate workspace."
        actions={
          <>
            <Link href="/playground">
              <Button variant="secondary">
                <PlayCircle className="h-4 w-4" />
                Open schemas
              </Button>
            </Link>
            <Link href="/inbox">
              <Button variant="primary">
                <ListChecks className="h-4 w-4" />
                Review inbox
              </Button>
            </Link>
          </>
        }
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Records" value={records.length.toString()} meta="Across all schema-driven flows." tone="accent" icon={<Sparkles className="h-5 w-5" />} />
        <StatCard label="Pending sync" value={syncData.events.filter((event) => event.status === "pending").length.toString()} meta="Waiting for the next sync pass." tone="warning" icon={<FolderSync className="h-5 w-5" />} />
        <StatCard label="Retryable" value={syncData.events.filter((event) => event.status === "retryable").length.toString()} meta="Need an operator retry." tone="danger" icon={<FolderSync className="h-5 w-5" />} />
        <StatCard label="Schemas" value={schemas.length.toString()} meta="Neutral examples across use cases." icon={<PlayCircle className="h-5 w-5" />} />
      </div>

      <Surface title="Available flows" subtitle="Each schema inherits the same visual system but adapts to a different workflow shape." variant="shell">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {schemas.map((schema) => (
            <Surface key={schema.id} title={schema.title} subtitle={schema.summary} variant="base">
              <div className="mb-4 flex flex-wrap gap-2">
                <Badge tone="accent">{schema.category}</Badge>
                <Badge>{schema.flow.accessMode}</Badge>
                {schema.tags.slice(0, 2).map((tag) => (
                  <Badge key={tag}>{tag}</Badge>
                ))}
              </div>

              <div className="grid gap-2 text-sm text-muted">
                <div className="surface-muted flex items-center justify-between px-3 py-2.5">
                  <span>Steps</span>
                  <span className="text-heading">{schema.flow.steps.length}</span>
                </div>
                <div className="surface-muted flex items-center justify-between px-3 py-2.5">
                  <span>Fields</span>
                  <span className="text-heading">{schema.fields.length}</span>
                </div>
                <div className="surface-muted flex items-center justify-between px-3 py-2.5">
                  <span>Outbound adapter</span>
                  <span className="text-heading">{schema.adapterBindings.outbound}</span>
                </div>
              </div>

              <div className="mt-5 flex flex-wrap gap-2">
                <Link href={`/flow/${schema.id}`}>
                  <Button variant="primary" size="sm">
                    Start flow
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
                <Link href={`/flow/${schema.id}?mode=resume`}>
                  <Button variant="ghost" size="sm">
                    Resume / token
                  </Button>
                </Link>
              </div>
            </Surface>
          ))}
        </div>
      </Surface>
    </div>
  );
}
