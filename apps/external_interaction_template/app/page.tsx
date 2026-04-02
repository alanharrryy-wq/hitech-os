import Link from "next/link";
import { ArrowRight, FolderSync, ListChecks, PlayCircle } from "lucide-react";

import { Badge } from "@components/ui/badge";
import { Button } from "@components/ui/button";
import { Surface } from "@components/ui/surface";
import { listSchemas } from "@/lib/core/schema-registry";
import { listRecords } from "@/lib/services/records";
import { listSyncCenterData } from "@/lib/services/actions";

export const dynamic = "force-dynamic";

export default async function LauncherPage() {
  const schemas = listSchemas();
  const [records, syncData] = await Promise.all([listRecords(), listSyncCenterData()]);

  return (
    <div className="grid gap-4">
      <Surface title="External Interaction Launcher" subtitle="Collect, review, update, approve, dispatch and sync through schema-driven external flows.">
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <Metric label="Records" value={records.length.toString()} tone="accent" />
          <Metric label="Pending Sync" value={syncData.events.filter((event) => event.status === "pending").length.toString()} tone="warning" />
          <Metric label="Retryable" value={syncData.events.filter((event) => event.status === "retryable").length.toString()} tone="danger" />
          <Metric label="Schemas" value={schemas.length.toString()} tone="success" />
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <Link href="/playground">
            <Button variant="primary">
              <PlayCircle className="mr-1.5 h-4 w-4" />
              Open Schema Playground
            </Button>
          </Link>
          <Link href="/inbox">
            <Button variant="secondary">
              <ListChecks className="mr-1.5 h-4 w-4" />
              Review Inbox
            </Button>
          </Link>
          <Link href="/sync">
            <Button variant="secondary">
              <FolderSync className="mr-1.5 h-4 w-4" />
              Sync Center
            </Button>
          </Link>
        </div>
      </Surface>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {schemas.map((schema) => (
          <Surface key={schema.id} title={schema.title} subtitle={schema.summary}>
            <div className="mb-3 flex flex-wrap gap-1.5">
              <Badge tone="accent">{schema.category}</Badge>
              {schema.tags.slice(0, 3).map((tag) => (
                <Badge key={tag}>{tag}</Badge>
              ))}
            </div>
            <div className="text-xs text-muted">
              access: <span className="text-text">{schema.flow.accessMode}</span> • steps: <span className="text-text">{schema.flow.steps.length}</span>
            </div>
            <div className="mt-3 flex gap-2">
              <Link href={`/flow/${schema.id}`}>
                <Button variant="primary" className="h-8 px-2.5 text-xs">
                  Start flow
                  <ArrowRight className="ml-1 h-3.5 w-3.5" />
                </Button>
              </Link>
              <Link href={`/flow/${schema.id}?mode=resume`}>
                <Button variant="ghost" className="h-8 px-2.5 text-xs">
                  Resume / token
                </Button>
              </Link>
            </div>
          </Surface>
        ))}
      </div>
    </div>
  );
}

function Metric({ label, value, tone }: { label: string; value: string; tone: "accent" | "warning" | "danger" | "success" }) {
  return (
    <div className="rounded-xl border border-white/10 bg-canvas/35 p-3">
      <div className="text-xs uppercase tracking-[0.1em] text-muted">{label}</div>
      <div className={`mt-1 text-2xl font-semibold ${tone === "accent" ? "text-accent" : tone === "warning" ? "text-warning" : tone === "danger" ? "text-danger" : "text-success"}`}>
        {value}
      </div>
    </div>
  );
}
