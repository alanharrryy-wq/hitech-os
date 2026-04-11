"use client";

import Link from "next/link";
import { Filter, LayoutGrid, List, Search, SearchX, X } from "lucide-react";
import { useMemo, useState } from "react";

import { InboxRecordCard } from "@components/records/inbox-record-card";
import { Button } from "@components/ui/button";
import { EmptyState } from "@components/ui/empty-state";
import { FilterPills } from "@components/ui/filter-pills";
import { Input } from "@components/ui/input";
import { PageHeader } from "@components/ui/page-header";
import { Select } from "@components/ui/select";
import { StateBadge } from "@components/ui/state-badge";
import { StatCard } from "@components/ui/stat-card";
import { Surface } from "@components/ui/surface";
import {
  INBOX_STATE_ORDER,
  recordPreviewFields,
  sortRecordsForInbox,
  stateDescription,
  stateLabel,
  stateTone
} from "@/lib/core/record-view";
import { RECORD_STATES, type ExternalRecord, type RecordTypeSchema } from "@/lib/core/types";
import { useT } from "@/lib/i18n/use-t";
import { localizeSchemaTitle } from "@/lib/ui/schema-display";

interface RecordInboxProps {
  records: ExternalRecord[];
  schemas: RecordTypeSchema[];
}

export function RecordInbox({ records, schemas }: RecordInboxProps) {
  const t = useT();
  const [query, setQuery] = useState("");
  const [schemaFilter, setSchemaFilter] = useState<string>("all");
  const [stateFilter, setStateFilter] = useState<ExternalRecord["state"] | "all">("all");
  const [view, setView] = useState<"list" | "grid">("list");

  const schemaMap = useMemo(() => new Map(schemas.map((schema) => [schema.id, schema])), [schemas]);
  const hasActiveFilters = query.trim().length > 0 || schemaFilter !== "all" || stateFilter !== "all";

  const stateCounts = useMemo(() => {
    return records.reduce<Record<string, number>>((accumulator, record) => {
      accumulator[record.state] = (accumulator[record.state] ?? 0) + 1;
      return accumulator;
    }, {});
  }, [records]);

  const filtered = useMemo(() => {
    const normalizedQuery = query.toLowerCase().trim();
    return sortRecordsForInbox(
      records.filter((record) => {
        if (schemaFilter !== "all" && record.recordTypeId !== schemaFilter) {
          return false;
        }
        if (stateFilter !== "all" && record.state !== stateFilter) {
          return false;
        }
        if (!normalizedQuery) {
          return true;
        }
        const blob = `${record.title} ${record.id} ${JSON.stringify(record.fields)}`.toLowerCase();
        return blob.includes(normalizedQuery);
      })
    );
  }, [records, query, schemaFilter, stateFilter]);

  const visibleCounts = useMemo(() => {
    return filtered.reduce<Record<string, number>>((accumulator, record) => {
      accumulator[record.state] = (accumulator[record.state] ?? 0) + 1;
      return accumulator;
    }, {});
  }, [filtered]);

  const groupedRecords = useMemo(() => {
    return INBOX_STATE_ORDER.map((state) => ({
      state,
      records: filtered.filter((record) => record.state === state)
    })).filter((group) => group.records.length > 0);
  }, [filtered]);

  const laneItems = useMemo(
    () => [
      { value: "all" as const, label: t("inbox.lane.all"), count: records.length },
      ...RECORD_STATES.map((state) => ({
        value: state,
        label: stateLabel(state),
        count: stateCounts[state] ?? 0,
        tone: stateTone(state)
      }))
    ],
    [records.length, stateCounts, t]
  );

  function clearFilters() {
    setQuery("");
    setSchemaFilter("all");
    setStateFilter("all");
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow={t("inbox.eyebrow")}
        title={t("inbox.title")}
        description={t("inbox.description")}
        compact
        stats={
          <>
            <StatCard
              label={t("inbox.stats.visibleRecords.label")}
              value={filtered.length.toString()}
              meta={t("inbox.stats.visibleRecords.meta")}
            />
            <StatCard
              label={t("inbox.stats.needsAttention.label")}
              value={String((visibleCounts.awaiting_update ?? 0) + (visibleCounts.failed ?? 0))}
              meta={t("inbox.stats.needsAttention.meta")}
              tone="danger"
            />
            <StatCard
              label={t("inbox.stats.submitted.label")}
              value={String(visibleCounts.submitted ?? 0)}
              meta={t("inbox.stats.submitted.meta")}
              tone="warning"
            />
            <StatCard
              label={t("inbox.stats.inReview.label")}
              value={String(visibleCounts.in_review ?? 0)}
              meta={t("inbox.stats.inReview.meta")}
              tone="accent"
            />
          </>
        }
        actions={
          <div className="flex flex-wrap items-center gap-2">
            {hasActiveFilters ? (
              <Button variant="ghost" size="sm" onClick={clearFilters}>
                <X className="h-4 w-4" />
                {t("inbox.clearFilters")}
              </Button>
            ) : null}
            <div className="flex items-center gap-2 rounded-[18px] border border-border/70 bg-surface/80 p-1 shadow-inset">
              <Button variant={view === "list" ? "secondary" : "ghost"} size="sm" className="min-w-10 px-3" onClick={() => setView("list")}>
                <List className="h-4 w-4" />
              </Button>
              <Button variant={view === "grid" ? "secondary" : "ghost"} size="sm" className="min-w-10 px-3" onClick={() => setView("grid")}>
                <LayoutGrid className="h-4 w-4" />
              </Button>
            </div>
          </div>
        }
      />

      <Surface
        title={t("inbox.controls.title")}
        subtitle={t("inbox.controls.subtitle")}
        variant="shell"
        padding="sm"
        actions={<div className="metric-label">{t("inbox.totalRecords", { count: records.length })}</div>}
      >
        <div className="grid gap-3 xl:grid-cols-[minmax(0,1.3fr)_repeat(2,minmax(0,220px))]">
          <div className="relative">
            <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-subtle" />
            <Input
              className="pl-10"
              placeholder={t("inbox.searchPlaceholder")}
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
          </div>

          <label className="grid gap-1.5 text-sm text-muted">
            <span className="eyebrow">{t("inbox.schemaLabel")}</span>
            <Select value={schemaFilter} onChange={(event) => setSchemaFilter(event.target.value)}>
              <option value="all">{t("inbox.schemaTypes")}</option>
              {schemas.map((schema) => (
                <option key={schema.id} value={schema.id}>
                  {localizeSchemaTitle(schema, t)}
                </option>
              ))}
            </Select>
          </label>

          <label className="grid gap-1.5 text-sm text-muted">
            <span className="eyebrow">{t("inbox.state")}</span>
            <Select value={stateFilter} onChange={(event) => setStateFilter(event.target.value as ExternalRecord["state"] | "all")}>
              <option value="all">{t("inbox.allStates")}</option>
              {RECORD_STATES.map((state) => (
                <option key={state} value={state}>
                  {stateLabel(state)}
                </option>
              ))}
            </Select>
          </label>
        </div>

        <div className="mt-4 grid gap-3 lg:grid-cols-[auto_minmax(0,1fr)] lg:items-start">
          <div className="inline-flex items-center gap-2 pr-2 pt-2 text-xs font-medium uppercase tracking-[0.14em] text-subtle">
            <Filter className="h-3.5 w-3.5" />
            {t("inbox.stateLanes")}
          </div>
          <FilterPills options={laneItems} value={stateFilter} onChange={setStateFilter} size="sm" />
        </div>

        <div className="mt-4 queue-header">
          <div className="space-y-1">
            <div className="text-sm font-medium text-heading">
              {t(
                filtered.length === 1 && groupedRecords.length === 1
                  ? "inbox.showingSummary.one"
                  : "inbox.showingSummary.many",
                { count: filtered.length, lanes: groupedRecords.length }
              )}
            </div>
            <div className="text-sm text-muted">{t("inbox.listGridExplanation")}</div>
          </div>
          {hasActiveFilters ? (
            <div className="text-sm text-muted">{t("inbox.filteredViewActive")}</div>
          ) : (
            <div className="text-sm text-muted">{t("inbox.defaultQueueOrder")}</div>
          )}
        </div>
      </Surface>

      {filtered.length === 0 ? (
        <EmptyState
          eyebrow={t("inbox.empty.eyebrow")}
          icon={<SearchX className="h-6 w-6" />}
          title={t("inbox.empty.title")}
          description={t("inbox.empty.description")}
          action={
            <Link href="/">
              <Button variant="primary">{t("inbox.empty.cta")}</Button>
            </Link>
          }
        />
      ) : view === "grid" ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {filtered.map((record) => {
            const schema = schemaMap.get(record.recordTypeId);
            const preview = recordPreviewFields(record);
            return <InboxRecordCard key={record.id} record={record} schema={schema} previewFields={preview} layout="grid" />;
          })}
        </div>
      ) : (
        <div className="grid gap-5">
          {groupedRecords.map((group) => (
            <section key={group.state} className="queue-section">
              <div className="queue-header">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-3">
                  <StateBadge state={group.state} />
                  <p className="text-sm text-muted">{stateDescription(group.state)}</p>
                </div>
                <div className="text-sm text-muted">
                  {t(group.records.length === 1 ? "inbox.groupedCount.one" : "inbox.groupedCount.many", { count: group.records.length })}
                </div>
              </div>

              <div className="grid gap-3">
                {group.records.map((record) => {
                  const schema = schemaMap.get(record.recordTypeId);
                  const preview = recordPreviewFields(record);
                  return <InboxRecordCard key={record.id} record={record} schema={schema} previewFields={preview} layout="list" />;
                })}
              </div>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}
