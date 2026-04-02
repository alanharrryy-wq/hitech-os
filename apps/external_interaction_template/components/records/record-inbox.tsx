"use client";

import Link from "next/link";
import { Filter, LayoutGrid, List, Search } from "lucide-react";
import { useMemo, useState } from "react";

import { Badge } from "@components/ui/badge";
import { Button } from "@components/ui/button";
import { Input } from "@components/ui/input";
import { Surface } from "@components/ui/surface";
import { recordPreviewFields, stateLabel, stateTone } from "@/lib/core/record-view";
import { type ExternalRecord, type RecordTypeSchema } from "@/lib/core/types";
import { formatDateTime } from "@/lib/utils";

interface RecordInboxProps {
  records: ExternalRecord[];
  schemas: RecordTypeSchema[];
}

export function RecordInbox({ records, schemas }: RecordInboxProps) {
  const [query, setQuery] = useState("");
  const [schemaFilter, setSchemaFilter] = useState<string>("all");
  const [view, setView] = useState<"list" | "grid">("list");

  const schemaMap = useMemo(() => new Map(schemas.map((schema) => [schema.id, schema])), [schemas]);

  const filtered = useMemo(() => {
    const normalizedQuery = query.toLowerCase().trim();
    return records.filter((record) => {
      if (schemaFilter !== "all" && record.recordTypeId !== schemaFilter) {
        return false;
      }
      if (!normalizedQuery) {
        return true;
      }
      const blob = `${record.title} ${JSON.stringify(record.fields)}`.toLowerCase();
      return blob.includes(normalizedQuery);
    });
  }, [records, query, schemaFilter]);

  return (
    <div className="grid gap-4">
      <Surface
        title="Record Inbox"
        subtitle="Review submitted, in-progress and externally updated records."
        actions={
          <div className="flex items-center gap-2">
            <Button variant={view === "list" ? "primary" : "ghost"} className="h-8 px-2" onClick={() => setView("list")}>
              <List className="h-3.5 w-3.5" />
            </Button>
            <Button variant={view === "grid" ? "primary" : "ghost"} className="h-8 px-2" onClick={() => setView("grid")}>
              <LayoutGrid className="h-3.5 w-3.5" />
            </Button>
          </div>
        }
      >
        <div className="grid gap-3 sm:grid-cols-[1fr_auto]">
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
            <Input className="pl-9" placeholder="Search title, values, context..." value={query} onChange={(event) => setQuery(event.target.value)} />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-muted" />
            <select
              value={schemaFilter}
              onChange={(event) => setSchemaFilter(event.target.value)}
              className="h-10 rounded-xl border border-white/12 bg-surface/60 px-3 text-sm text-text"
            >
              <option value="all">All schema types</option>
              {schemas.map((schema) => (
                <option key={schema.id} value={schema.id}>
                  {schema.title}
                </option>
              ))}
            </select>
          </div>
        </div>
      </Surface>

      {filtered.length === 0 ? (
        <Surface>
          <div className="rounded-xl border border-dashed border-white/20 bg-canvas/30 px-4 py-10 text-center">
            <div className="text-base font-medium text-text">No records match current filters</div>
            <p className="mt-2 text-sm text-muted">Try another schema filter or start a new flow from Launcher.</p>
            <Link href="/" className="mt-4 inline-flex">
              <Button variant="primary">Go to Launcher</Button>
            </Link>
          </div>
        </Surface>
      ) : (
        <div className={view === "grid" ? "grid gap-3 sm:grid-cols-2 xl:grid-cols-3" : "grid gap-2"}>
          {filtered.map((record) => {
            const schema = schemaMap.get(record.recordTypeId);
            const preview = recordPreviewFields(record);
            return (
              <Link
                key={record.id}
                href={`/record/${record.id}`}
                className="rounded-2xl border border-white/10 bg-surface/55 p-4 transition hover:border-accent/35 hover:bg-surface/65"
              >
                <div className="mb-2 flex items-start justify-between gap-3">
                  <div>
                    <div className="text-sm font-semibold text-text">{record.title}</div>
                    <div className="text-xs text-muted">{schema?.title ?? record.recordTypeId}</div>
                  </div>
                  <Badge tone={stateTone(record.state)}>{stateLabel(record.state)}</Badge>
                </div>
                <div className="grid gap-1.5 text-xs">
                  {preview.map((entry) => (
                    <div key={entry.label} className="flex items-center justify-between gap-3 rounded-md bg-canvas/30 px-2.5 py-1.5">
                      <span className="text-muted">{entry.label}</span>
                      <span className="max-w-[12rem] truncate text-text">{entry.value}</span>
                    </div>
                  ))}
                </div>
                <div className="mt-3 text-[11px] uppercase tracking-[0.08em] text-muted">Updated {formatDateTime(record.updatedAt)}</div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
