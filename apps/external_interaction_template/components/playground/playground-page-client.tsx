"use client";

import Link from "next/link";

import { Badge } from "@components/ui/badge";
import { Button } from "@components/ui/button";
import { PageHeader } from "@components/ui/page-header";
import { Surface } from "@components/ui/surface";
import { useT } from "@/lib/i18n/use-t";
import { localizeSchemaDisplay } from "@/lib/ui/schema-display";

interface PlaygroundPageClientProps {
  schemas: any[];
}

export function PlaygroundPageClient({ schemas }: PlaygroundPageClientProps) {
  const t = useT();

  return (
    <div className="grid gap-5">
      <PageHeader
        eyebrow={t("playground.eyebrow")}
        title={t("playground.title")}
        description={t("playground.description")}
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {schemas.map((schema) => {
          const displaySchema = localizeSchemaDisplay(schema, t);
          return (
            <Surface key={schema.id} title={displaySchema.title} subtitle={displaySchema.summary} variant="shell">
              <div className="mb-4 flex flex-wrap gap-2">
                <Badge tone="accent">{displaySchema.category}</Badge>
                <Badge>{displaySchema.accessMode}</Badge>
              </div>
              <ul className="mb-5 grid gap-2 text-sm text-muted">
                <li className="surface-muted flex items-center justify-between px-3 py-2.5"><span>{t("playground.metric.steps")}</span><span className="text-heading">{schema.flow.steps.length}</span></li>
                <li className="surface-muted flex items-center justify-between px-3 py-2.5"><span>{t("playground.metric.fields")}</span><span className="text-heading">{schema.fields.length}</span></li>
                <li className="surface-muted flex items-center justify-between px-3 py-2.5"><span>{t("playground.metric.actions")}</span><span className="text-heading">{schema.actions.length}</span></li>
                <li className="surface-muted flex items-center justify-between px-3 py-2.5"><span>{t("playground.metric.outbound")}</span><span className="text-heading">{schema.adapterBindings.outbound}</span></li>
              </ul>
              <div className="flex flex-wrap gap-2">
                <Link href={`/flow/${schema.id}`}>
                  <Button variant="primary" size="sm">
                    {t("playground.runFlow")}
                  </Button>
                </Link>
                <Link href={`/inbox?schemaId=${schema.id}`}>
                  <Button variant="ghost" size="sm">
                    {t("playground.inspectInbox")}
                  </Button>
                </Link>
              </div>
            </Surface>
          );
        })}
      </div>
    </div>
  );
}
