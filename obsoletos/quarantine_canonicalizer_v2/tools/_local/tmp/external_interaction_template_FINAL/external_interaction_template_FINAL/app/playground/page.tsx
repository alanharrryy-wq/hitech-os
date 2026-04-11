import Link from "next/link";

import { Badge } from "@components/ui/badge";
import { Button } from "@components/ui/button";
import { PageHeader } from "@components/ui/page-header";
import { Surface } from "@components/ui/surface";
import { listSchemas } from "@/lib/core/schema-registry";

export default function PlaygroundPage() {
  const schemas = listSchemas();

  return (
    <div className="grid gap-5">
      <PageHeader
        eyebrow="Schema playground"
        title="Visual system check across different workflow shapes"
        description="Switch across service requests, approval packets, and inspection flows to confirm the product stays coherent while the schema changes underneath it."
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {schemas.map((schema) => (
          <Surface key={schema.id} title={schema.title} subtitle={schema.summary} variant="shell">
            <div className="mb-4 flex flex-wrap gap-2">
              <Badge tone="accent">{schema.category}</Badge>
              <Badge>{schema.flow.accessMode}</Badge>
            </div>
            <ul className="mb-5 grid gap-2 text-sm text-muted">
              <li className="surface-muted flex items-center justify-between px-3 py-2.5"><span>Steps</span><span className="text-heading">{schema.flow.steps.length}</span></li>
              <li className="surface-muted flex items-center justify-between px-3 py-2.5"><span>Fields</span><span className="text-heading">{schema.fields.length}</span></li>
              <li className="surface-muted flex items-center justify-between px-3 py-2.5"><span>Actions</span><span className="text-heading">{schema.actions.length}</span></li>
              <li className="surface-muted flex items-center justify-between px-3 py-2.5"><span>Outbound</span><span className="text-heading">{schema.adapterBindings.outbound}</span></li>
            </ul>
            <div className="flex flex-wrap gap-2">
              <Link href={`/flow/${schema.id}`}>
                <Button variant="primary" size="sm">
                  Run flow
                </Button>
              </Link>
              <Link href={`/inbox?schemaId=${schema.id}`}>
                <Button variant="ghost" size="sm">
                  Inspect inbox
                </Button>
              </Link>
            </div>
          </Surface>
        ))}
      </div>
    </div>
  );
}
