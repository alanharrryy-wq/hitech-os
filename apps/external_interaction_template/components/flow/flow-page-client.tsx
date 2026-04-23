"use client";

import { useEffect, useMemo, useState } from "react";

import { FlowContextStack } from "@components/flow/flow-context-stack";
import { FlowMainCard } from "@components/flow/flow-main-card";
import { FlowRouteScreen } from "@components/flow/flow-route-screen";
import { FlowRunner, type FlowRunnerContextSnapshot } from "@components/flow/flow-runner";
import { FlowSummaryStrip } from "@components/flow/flow-summary-strip";
import { FlowWorkbench } from "@components/flow/flow-workbench";
import { ProgressOverviewCard } from "@components/flow/progress-overview-card";
import { ResumeSessionCard } from "@components/flow/resume-session-card";
import { SchemaMetaCard } from "@components/flow/schema-meta-card";
import { useT } from "@/lib/i18n/use-t";
import { type ExternalRecord, type RecordTypeSchema } from "@/lib/core/types";
import {
  localizeSchemaAccessMode,
  localizeSchemaCategory,
  localizeSchemaSummary,
  localizeSchemaTag,
  localizeSchemaTitle
} from "@/lib/ui/schema-display";

interface FlowPageClientProps {
  schema: RecordTypeSchema;
  initialRecord?: ExternalRecord | null;
  queryToken?: string;
}

function createInitialSnapshot(schema: RecordTypeSchema, initialRecord?: ExternalRecord | null): FlowRunnerContextSnapshot {
  const firstStep = schema.flow.steps[0];

  return {
    stepIndex: 0,
    totalSteps: schema.flow.steps.length,
    progress: 0,
    remainingRequired: schema.flow.steps.length,
    recordState: initialRecord?.state ?? "draft",
    recordId: initialRecord?.id ?? null,
    secureToken: initialRecord?.secureToken ?? null,
    lastSavedAt: initialRecord?.updatedAt ?? null,
    errorCount: 0,
    activeStepId: firstStep?.id ?? "",
    activeStepTitle: firstStep?.title ?? "",
    stepSummaries: schema.flow.steps.map((step) => ({
      id: step.id,
      title: step.title,
      complete: false,
      requiredTotal: 0,
      completedRequired: 0
    }))
  };
}

export function FlowPageClient({ schema, initialRecord, queryToken = "" }: FlowPageClientProps) {
  const t = useT();
  const schemaTitle = localizeSchemaTitle(schema, t);
  const schemaSummary = localizeSchemaSummary(schema, t);
  const categoryLabel = localizeSchemaCategory(schema.category, t);
  const accessModeLabel = localizeSchemaAccessMode(schema.flow.accessMode, t);
  const localizedTags = useMemo(() => schema.tags.map((tag) => localizeSchemaTag(tag, t)), [schema.tags, t]);

  const baseSnapshot = useMemo(() => createInitialSnapshot(schema, initialRecord), [schema, initialRecord]);
  const [runnerContext, setRunnerContext] = useState<FlowRunnerContextSnapshot>(baseSnapshot);

  useEffect(() => {
    setRunnerContext(baseSnapshot);
  }, [baseSnapshot]);

  return (
    <FlowRouteScreen
      summaryStrip={
        <FlowSummaryStrip
          schemaId={schema.id}
          schemaTitle={schemaTitle}
          schemaSummary={schemaSummary}
          accessModeLabel={accessModeLabel}
          stepCount={schema.flow.steps.length}
          allowDrafts={schema.flow.allowDrafts}
          t={t}
        />
      }
      workbench={
        <FlowWorkbench
          main={
            <FlowMainCard>
              <FlowRunner
                schema={schema}
                initialRecord={initialRecord}
                sidebarMode="none"
                onContextChange={setRunnerContext}
              />
            </FlowMainCard>
          }
          context={
            <FlowContextStack>
              <ResumeSessionCard schemaId={schema.id} queryToken={queryToken} t={t} />
              <ProgressOverviewCard context={runnerContext} t={t} />
              <SchemaMetaCard
                categoryLabel={categoryLabel}
                accessModeLabel={accessModeLabel}
                inboundAdapter={schema.adapterBindings.inbound}
                outboundAdapter={schema.adapterBindings.outbound}
                tags={localizedTags}
                t={t}
              />
            </FlowContextStack>
          }
        />
      }
    />
  );
}
