"use client";

import Link from "next/link";
import { ArrowRight, FolderSync, ListChecks, PlayCircle, Sparkles } from "lucide-react";

import { Badge } from "@components/ui/badge";
import { Button } from "@components/ui/button";
import { PageHeader } from "@components/ui/page-header";
import { StatCard } from "@components/ui/stat-card";
import { Surface } from "@components/ui/surface";
import { useT } from "@/lib/i18n/use-t";
import { localizeSchemaDisplay } from "@/lib/ui/schema-display";

interface LauncherPageClientProps {
  schemas: any[];
  records: any[];
  syncData: {
    events: Array<{ status: string }>;
  };
}

export function LauncherPageClient({ schemas, records, syncData }: LauncherPageClientProps) {
  const t = useT();

  return (
    <div className="grid gap-4">
      <PageHeader
        eyebrow={t("launcher.eyebrow")}
        title={t("launcher.title")}
        description={t("launcher.description")}
        compact
        actions={
          <>
            <Link href="/playground">
              <Button variant="secondary" size="sm">
                <PlayCircle className="h-4 w-4" />
                {t("launcher.openSchemas")}
              </Button>
            </Link>
            <Link href="/inbox">
              <Button variant="primary" size="sm">
                <ListChecks className="h-4 w-4" />
                {t("launcher.reviewInbox")}
              </Button>
            </Link>
          </>
        }
      />

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label={t("launcher.records.label")}
          value={records.length.toString()}
          meta={t("launcher.records.meta")}
          tone="accent"
          icon={<Sparkles className="h-5 w-5" />}
        />
        <StatCard
          label={t("launcher.pendingSync.label")}
          value={syncData.events.filter((event) => event.status === "pending").length.toString()}
          meta={t("launcher.pendingSync.meta")}
          tone="warning"
          icon={<FolderSync className="h-5 w-5" />}
        />
        <StatCard
          label={t("launcher.retryable.label")}
          value={syncData.events.filter((event) => event.status === "retryable").length.toString()}
          meta={t("launcher.retryable.meta")}
          tone="danger"
          icon={<FolderSync className="h-5 w-5" />}
        />
        <StatCard
          label={t("launcher.schemas.label")}
          value={schemas.length.toString()}
          meta={t("launcher.schemas.meta")}
          icon={<PlayCircle className="h-5 w-5" />}
        />
      </div>

      <Surface
        title={t("launcher.surface.title")}
        subtitle={t("launcher.surface.subtitle")}
        variant="shell"
        padding="sm"
      >
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {schemas.map((schema) => {
            const displaySchema = localizeSchemaDisplay(schema, t);
            return (
              <Surface key={schema.id} title={displaySchema.title} subtitle={displaySchema.summary} variant="base" padding="sm">
                <div className="mb-3 flex flex-wrap gap-2">
                  <Badge tone="accent">{displaySchema.category}</Badge>
                  <Badge>{displaySchema.accessMode}</Badge>
                  {displaySchema.tags.slice(0, 2).map((tag: string) => (
                    <Badge key={tag}>{tag}</Badge>
                  ))}
                </div>

                <div className="grid gap-2 text-sm text-muted">
                  <div className="surface-muted flex items-center justify-between px-3 py-2.5">
                    <span>{t("launcher.metric.steps")}</span>
                    <span className="text-heading">{schema.flow.steps.length}</span>
                  </div>
                  <div className="surface-muted flex items-center justify-between px-3 py-2.5">
                    <span>{t("launcher.metric.fields")}</span>
                    <span className="text-heading">{schema.fields.length}</span>
                  </div>
                  <div className="surface-muted flex items-center justify-between px-3 py-2.5">
                    <span>{t("launcher.metric.outboundAdapter")}</span>
                    <span className="text-heading">{schema.adapterBindings.outbound}</span>
                  </div>
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  <Link href={`/flow/${schema.id}`}>
                    <Button variant="primary" size="sm">
                      {t("launcher.startFlow")}
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </Link>
                  <Link href={`/flow/${schema.id}?mode=resume`}>
                    <Button variant="ghost" size="sm">
                      {t("launcher.resumeToken")}
                    </Button>
                  </Link>
                </div>
              </Surface>
            );
          })}
        </div>
      </Surface>
    </div>
  );
}
