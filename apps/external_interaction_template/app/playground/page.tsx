import Link from "next/link";

import { Surface } from "@components/ui/surface";
import { Button } from "@components/ui/button";
import { Badge } from "@components/ui/badge";
import { listSchemas } from "@/lib/core/schema-registry";

export default function PlaygroundPage() {
  const schemas = listSchemas();

  return (
    <div className="grid gap-4">
      <Surface title="Schema Playground" subtitle="Switch demo schemas to validate neutral architecture across use cases.">
        <p className="text-sm text-muted">
          This playground demonstrates that external interactions are driven by schema, state and adapter bindings instead of a fixed business vertical.
        </p>
      </Surface>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {schemas.map((schema) => (
          <Surface key={schema.id} title={schema.title} subtitle={schema.summary}>
            <div className="mb-3 flex flex-wrap gap-1.5">
              <Badge tone="accent">{schema.category}</Badge>
              <Badge>{schema.flow.accessMode}</Badge>
            </div>
            <ul className="mb-3 grid gap-1 text-xs text-muted">
              <li>steps: {schema.flow.steps.length}</li>
              <li>fields: {schema.fields.length}</li>
              <li>actions: {schema.actions.length}</li>
              <li>inbound: {schema.adapterBindings.inbound}</li>
              <li>outbound: {schema.adapterBindings.outbound}</li>
            </ul>
            <div className="flex gap-2">
              <Link href={`/flow/${schema.id}`}>
                <Button variant="primary" className="h-8 px-2.5 text-xs">
                  Run flow
                </Button>
              </Link>
              <Link href={`/inbox?schemaId=${schema.id}`}>
                <Button variant="ghost" className="h-8 px-2.5 text-xs">
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
