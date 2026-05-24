"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useState } from "react";
import type { EditorProps } from "@monaco-editor/react";
import type { LabChartEntry } from "@/prisma-charts/chart-lab-types";

const MonacoEditor = dynamic<EditorProps>(
  () => import("@monaco-editor/react").then((module) => module.default),
  {
    ssr: false,
    loading: () => <div className="prisma-option-studio-editor-loading">Loading Monaco...</div>
  }
);

type ValidationState =
  | { status: "idle"; message: string }
  | { status: "valid"; message: string }
  | { status: "invalid"; message: string };

type OptionStudioPanelProps = {
  chart: LabChartEntry;
  canonicalOption?: Record<string, unknown>;
  previewOption?: Record<string, unknown>;
  hasPreviewOverride: boolean;
  onApplyPreview: (option: Record<string, unknown>) => void;
  onResetPreview: () => void;
};

function stringifyOption(option: Record<string, unknown> | undefined) {
  return JSON.stringify(option ?? {}, null, 2);
}

function parseOptionText(text: string): { ok: true; option: Record<string, unknown> } | { ok: false; message: string } {
  try {
    const parsed = JSON.parse(text);
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return { ok: false, message: "Option must be a JSON object." };
    }
    return { ok: true, option: parsed as Record<string, unknown> };
  } catch (error) {
    return { ok: false, message: error instanceof Error ? error.message : "Invalid JSON option." };
  }
}

function downloadTextFile(filename: string, text: string, type: string) {
  const blob = new Blob([text], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.rel = "noopener";
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 0);
}

function safeChartSlug(chartId: string) {
  return chartId.replace(/[^a-z0-9.-]+/gi, "-").toLowerCase();
}

function timestampSlug() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

function draftName(chart: LabChartEntry) {
  return safeChartSlug(chart.id).replace(/(^|[-.])([a-z0-9])/g, (_match, prefix: string, letter: string) => `${prefix}${letter.toUpperCase()}`).replace(/[-.]/g, "");
}

export function OptionStudioPanel({
  chart,
  canonicalOption,
  previewOption,
  hasPreviewOverride,
  onApplyPreview,
  onResetPreview
}: OptionStudioPanelProps) {
  const canonicalText = useMemo(() => stringifyOption(canonicalOption), [canonicalOption]);
  const activeText = useMemo(() => stringifyOption(previewOption ?? canonicalOption), [canonicalOption, previewOption]);
  const [text, setText] = useState(activeText);
  const [validation, setValidation] = useState<ValidationState>({ status: "idle", message: "Not validated yet." });
  const [copyState, setCopyState] = useState("idle");

  useEffect(() => {
    setText(activeText);
    setValidation({ status: "idle", message: "Not validated yet." });
    setCopyState("idle");
  }, [activeText, chart.id]);

  function validateCurrentText() {
    const result = parseOptionText(text);
    if (!result.ok) {
      setValidation({ status: "invalid", message: result.message });
      return result;
    }
    setValidation({ status: "valid", message: "JSON option is valid." });
    return result;
  }

  function applyPreview() {
    const result = validateCurrentText();
    if (!result.ok) return;
    onApplyPreview(result.option);
  }

  function resetToCanonical() {
    setText(canonicalText);
    setValidation({ status: "idle", message: "Canonical option restored." });
    onResetPreview();
  }

  async function copyJson() {
    try {
      await navigator.clipboard.writeText(text);
      setCopyState("copied");
    } catch {
      setCopyState("copy failed");
    }
  }

  function exportJson() {
    downloadTextFile(`${safeChartSlug(chart.id)}-option-${timestampSlug()}.json`, text, "application/json;charset=utf-8");
  }

  function exportTsDraft() {
    const draft = [
      `// PRISMA Chart Lab Option Studio draft for ${chart.id}.`,
      "// Generated in the browser. Not applied to the repo.",
      `export const ${draftName(chart)}OptionDraft = ${text} as const;`,
      ""
    ].join("\n");
    downloadTextFile(`${safeChartSlug(chart.id)}-option-draft-${timestampSlug()}.ts.txt`, draft, "text/plain;charset=utf-8");
  }

  function exportPatchDraft() {
    const draft = [
      `PRISMA Chart Lab Option Studio patch draft`,
      ``,
      `Chart: ${chart.id}`,
      `Option builder: ${chart.optionBuilderName ?? "not registered"}`,
      `Suggested source module: ${chart.sourceModule}`,
      `Target boundary: ${chart.promotionBoundary}`,
      ``,
      `This file is a browser download only. It was not applied to the repo.`,
      ``,
      `--- draft option JSON ---`,
      text,
      ""
    ].join("\n");
    downloadTextFile(`${safeChartSlug(chart.id)}-option-patch-draft-${timestampSlug()}.patch.txt`, draft, "text/plain;charset=utf-8");
  }

  const optionSafety = useMemo(() => {
    const checks = [
      { label: "Windows path", pattern: /[A-Z]:\\|[A-Z]:\//i },
      { label: "SQLite or DB artifact", pattern: /\.(sqlite|db)\b|tablet-pos\.db/i },
      { label: "Secret token vocabulary", pattern: /(api[_-]?token|password|private[_-]?key|secret)/i },
      { label: "Local user path", pattern: /Users\\|repos\\|home\//i }
    ];
    const hits = checks.filter((check) => check.pattern.test(text)).map((check) => check.label);
    return { safe: hits.length === 0, hits };
  }, [text]);

  const optionDiffSummary = useMemo(() => {
    if (text === canonicalText) return "No local diff from canonical option.";
    return `${Math.abs(text.length - canonicalText.length)} character delta from canonical option.`;
  }, [canonicalText, text]);

  const editorAvailable = Boolean(chart.getOption);

  return (
    <section className="prisma-option-studio-panel" aria-label="Option Studio">
      <div className="prisma-option-studio-toolbar">
        <div>
          <span className="eyebrow">Option Studio</span>
          <h3>{chart.title}</h3>
        </div>
        <div className="prisma-option-studio-actions">
          <button type="button" onClick={validateCurrentText} disabled={!editorAvailable}>
            Validate
          </button>
          <button type="button" onClick={applyPreview} disabled={!editorAvailable}>
            Apply Preview
          </button>
          <button type="button" onClick={resetToCanonical}>
            Reset
          </button>
          <button type="button" onClick={copyJson}>
            Copy JSON
          </button>
          <button type="button" onClick={exportJson}>
            Export JSON
          </button>
          <button type="button" onClick={exportTsDraft}>
            Export TS Draft
          </button>
          <button type="button" onClick={exportPatchDraft}>
            Export Patch Draft
          </button>
        </div>
      </div>

      <div className="prisma-option-studio-status" data-status={validation.status} aria-live="polite">
        <strong>{hasPreviewOverride ? "Preview override active" : "Canonical preview"}</strong>
        <span>{validation.message}</span>
        <small>{copyState}</small>
      </div>

      <div className="prisma-option-studio-safety" data-safe={optionSafety.safe ? "true" : "false"} aria-label="Public safety and diff hints">
        <strong>{optionSafety.safe ? "Public-safe option draft" : "Review before export"}</strong>
        <span>{optionSafety.safe ? "No obvious local path, database, or secret marker detected." : optionSafety.hits.join(" · ")}</span>
        <small>{optionDiffSummary}</small>
      </div>

      {editorAvailable ? (
        <div className="prisma-option-studio-editor">
          <MonacoEditor
            height="520px"
            language="json"
            path={`${chart.id}.option.json`}
            theme="vs-dark"
            value={text}
            onChange={(value) => setText(value ?? "")}
            options={{
              automaticLayout: true,
              fontSize: 12,
              minimap: { enabled: false },
              renderLineHighlight: "line",
              scrollBeyondLastLine: false,
              tabSize: 2,
              wordWrap: "on"
            }}
          />
        </div>
      ) : (
        <div className="prisma-option-studio-empty">
          <strong>This registered chart does not expose an ECharts option.</strong>
          <p>Option Studio can export the draft shell, but Apply Preview is disabled for component-only entries.</p>
        </div>
      )}
    </section>
  );
}
