import Link from "next/link";
import { ArrowUpRight, Clock3, Layers3 } from "lucide-react";

import { DetailList } from "@components/ui/detail-list";
import { StateBadge } from "@components/ui/state-badge";
import { type ExternalRecord, type RecordTypeSchema } from "@/lib/core/types";
import { normalizePreviewFields, normalizeRecordTitle } from "@/lib/ui/record-contracts";
import { formatDateTime } from "@/lib/utils";

export interface InboxRecordCardField {
  label: string;
  value: string;
}

export interface InboxRecordCardProps {
  record: ExternalRecord;
  schema?: RecordTypeSchema;
  previewFields?: InboxRecordCardField[];
  href?: string;
  layout?: "list" | "grid";
  className?: string;
}

export function InboxRecordCard({
  record,
  schema,
  previewFields = [],
  href = `/record/${record.id}`,
  layout = "list",
  className
}: InboxRecordCardProps) {
  const fields = normalizePreviewFields(previewFields, 4);

  return (
    <Link
      href={href}
      className={
        "group block rounded-[1.6rem] border border-white/10 bg-surface/56 p-4 shadow-glass transition duration-200 hover:border-accent/30 hover:bg-surface/70" +
        (className ? ` ${className}` : "")
      }
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 text-[11px] uppercase tracking-[0.18em] text-muted">
            <Layers3 className="h-3.5 w-3.5" />
            <span>{schema?.title ?? record.recordTypeId}</span>
          </div>
          <div className="mt-2 flex items-start justify-between gap-3">
            <div className="min-w-0">
              <h3 className="truncate text-base font-semibold text-text">{normalizeRecordTitle(record)}</h3>
              <p className="mt-1 max-w-[54ch] text-sm leading-6 text-muted">{schema?.summary ?? "Schema-neutral record surface ready for downstream integration."}</p>
            </div>
            <ArrowUpRight className="mt-1 h-4 w-4 shrink-0 text-muted transition group-hover:text-accent" />
          </div>
        </div>
        <StateBadge state={record.state} />
      </div>

      {fields.length > 0 ? <DetailList items={fields} columns={layout === "grid" ? 2 : 2} dense className="mt-4" /> : null}

      <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-white/8 pt-3 text-xs text-muted">
        <div className="inline-flex items-center gap-1.5">
          <Clock3 className="h-3.5 w-3.5" />
          Updated {formatDateTime(record.updatedAt)}
        </div>
        <div className="inline-flex items-center gap-2">
          <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1">{record.id}</span>
        </div>
      </div>
    </Link>
  );
}
