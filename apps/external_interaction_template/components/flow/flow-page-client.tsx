"use client";

import Link from "next/link";
import { ArrowUpRight, RotateCcw } from "lucide-react";

import { FlowRunner } from "@components/flow/flow-runner";
import { Button } from "@components/ui/button";
import { Input } from "@components/ui/input";
import { PageHeader } from "@components/ui/page-header";
import { Surface } from "@components/ui/surface";
import { useT } from "@/lib/i18n/use-t";
import { type ExternalRecord, type RecordTypeSchema } from "@/lib/core/types";
import { localizeSchemaAccessMode, localizeSchemaTitle } from "@/lib/ui/schema-display";

interface FlowPageClientProps {
  schema: RecordTypeSchema;
  initialRecord?: ExternalRecord | null;
  queryToken?: string;
}

export function FlowPageClient({ schema, initialRecord, queryToken = "" }: FlowPageClientProps) {
  const t = useT();
  const schemaTitle = localizeSchemaTitle(schema, t);
  const accessModeLabel = localizeSchemaAccessMode(schema.flow.accessMode, t);

  return (
    <div className="grid gap-5">
      <PageHeader
        eyebrow={t("flow.page.eyebrow")}
        title={schemaTitle}
        description={t("flow.page.description")}
        children={
          <>
            <span className="rounded-full border border-border/70 bg-surface/80 px-3 py-1.5 text-sm text-muted">
              {t("flow.page.accessChip", { value: accessModeLabel })}
            </span>
            <span className="rounded-full border border-border/70 bg-surface/80 px-3 py-1.5 text-sm text-muted">
              {t("flow.page.stepsChip", { count: schema.flow.steps.length })}
            </span>
            <span className="rounded-full border border-border/70 bg-surface/80 px-3 py-1.5 text-sm text-muted">
              {t(schema.flow.allowDrafts ? "flow.page.draftsChipEnabled" : "flow.page.draftsChipDisabled")}
            </span>
          </>
        }
        actions={
          <>
            <Link href={`/flow/${schema.id}`}>
              <Button variant="ghost" size="sm">
                <RotateCcw className="h-4 w-4" />
                {t("flow.page.newSession")}
              </Button>
            </Link>
            <Link href="/inbox">
              <Button variant="secondary" size="sm">
                <ArrowUpRight className="h-4 w-4" />
                {t("flow.page.openInbox")}
              </Button>
            </Link>
          </>
        }
      />

      <Surface
        title={t("flow.page.resume.title")}
        subtitle={t("flow.page.resume.subtitle")}
        variant="shell"
      >
        <form action={`/flow/${schema.id}`} method="get" className="grid gap-4 md:grid-cols-[minmax(0,1fr)_auto] md:items-end">
          <label className="grid gap-1.5 text-sm text-muted">
            <span className="eyebrow">{t("flow.page.resume.label")}</span>
            <Input name="token" placeholder={t("flow.page.resume.placeholder")} defaultValue={queryToken} />
          </label>
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" type="submit">
              {t("flow.page.resume.submit")}
            </Button>
            <Link href={`/flow/${schema.id}`}>
              <Button variant="ghost">{t("flow.page.resume.clear")}</Button>
            </Link>
          </div>
        </form>
      </Surface>

      <FlowRunner schema={schema} initialRecord={initialRecord} />
    </div>
  );
}
