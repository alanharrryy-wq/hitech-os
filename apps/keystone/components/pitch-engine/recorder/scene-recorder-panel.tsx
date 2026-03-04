"use client";

import { useEffect, useMemo, useState } from "react";
import { buildBridgeOriginList, usePreviewBridge } from "../hooks/use-preview-bridge";
import { usePitchEngineStore } from "../state/use-pitch-engine-store";

function parseUnknownTokens(tokensInput: string): string[] {
  return tokensInput
    .split(",")
    .map((item) => item.trim())
    .filter((item) => item.length > 0);
}

export function SceneRecorderPanel() {
  const recordSnapshot = usePitchEngineStore((state) => state.recordSnapshot);
  const undoLastRecord = usePitchEngineStore((state) => state.undoLastRecord);
  const recorder = usePitchEngineStore((state) => state.recorder);
  const capability = usePitchEngineStore((state) => state.capabilityStatus);
  const setSecureOrigin = usePitchEngineStore((state) => state.setSecureOrigin);
  const incrementRejectedMessages = usePitchEngineStore((state) => state.incrementRejectedMessages);

  const [sequenceName, setSequenceName] = useState("Recorded Sequence");
  const [presetId, setPresetId] = useState("preset-01-01");
  const [createSequence, setCreateSequence] = useState(true);
  const [route, setRoute] = useState("/pitch/recorded");
  const [canonicalUrl, setCanonicalUrl] = useState("https://keystone.local/pitch/recorded");
  const [title, setTitle] = useState("Recorded Scene");
  const [resolvedFlagsInput, setResolvedFlagsInput] = useState("director-mode,timeline-tab");
  const [unknownTokensInput, setUnknownTokensInput] = useState("legacy-token");
  const [allowedOriginsInput, setAllowedOriginsInput] = useState("");

  const allowedOrigins = useMemo(
    () => buildBridgeOriginList(parseUnknownTokens(allowedOriginsInput)),
    [allowedOriginsInput]
  );

  usePreviewBridge({
    allowedOrigins,
    onOrigin: setSecureOrigin,
    onRejected: incrementRejectedMessages,
    onSnapshot: (snapshot) => {
      recordSnapshot({
        snapshot,
        createSequence,
        sequenceName,
        sequencePresetId: presetId
      });
    }
  });

  useEffect(() => {
    if (!capability.isRouteAllowed) {
      setCreateSequence(false);
    }
  }, [capability.isRouteAllowed]);

  const recordManualSnapshot = () => {
    const now = new Date().toISOString();
    recordSnapshot({
      snapshot: {
        route,
        canonicalUrl,
        title,
        capturedAt: now,
        flagSnapshot: {
          resolvedFlags: parseUnknownTokens(resolvedFlagsInput),
          unknownTokens: parseUnknownTokens(unknownTokensInput)
        },
        viewport: {
          width: typeof window === "undefined" ? 1280 : window.innerWidth,
          height: typeof window === "undefined" ? 720 : window.innerHeight,
          dpr: typeof window === "undefined" ? 1 : window.devicePixelRatio
        }
      },
      createSequence,
      sequenceName,
      sequencePresetId: presetId
    });
  };

  return (
    <section className="rounded-lg border border-slate-700 bg-slate-950/40 p-4">
      <header className="mb-3">
        <p className="keystone-kicker">Scene Recorder</p>
        <h2 className="text-lg font-semibold text-slate-100">Secure bridge capture + sequence generation</h2>
      </header>

      <p className="text-xs text-slate-400">
        Bridge security enforced with strict origin allow-list and payload validation.
      </p>

      <div className="mt-3 grid gap-2 md:grid-cols-2">
        <label className="grid gap-1 text-xs text-slate-300">
          Route
          <input
            className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
            value={route}
            onChange={(event) => {
              setRoute(event.target.value);
            }}
          />
        </label>

        <label className="grid gap-1 text-xs text-slate-300">
          Canonical URL
          <input
            className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
            value={canonicalUrl}
            onChange={(event) => {
              setCanonicalUrl(event.target.value);
            }}
          />
        </label>

        <label className="grid gap-1 text-xs text-slate-300">
          Title
          <input
            className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
            value={title}
            onChange={(event) => {
              setTitle(event.target.value);
            }}
          />
        </label>

        <label className="grid gap-1 text-xs text-slate-300">
          Allowed Bridge Origins (comma-separated)
          <input
            className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
            value={allowedOriginsInput}
            onChange={(event) => {
              setAllowedOriginsInput(event.target.value);
            }}
            placeholder="https://preview.local"
          />
        </label>

        <label className="grid gap-1 text-xs text-slate-300">
          Resolved Flags
          <input
            className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
            value={resolvedFlagsInput}
            onChange={(event) => {
              setResolvedFlagsInput(event.target.value);
            }}
          />
        </label>

        <label className="grid gap-1 text-xs text-slate-300">
          Unknown Tokens
          <input
            className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
            value={unknownTokensInput}
            onChange={(event) => {
              setUnknownTokensInput(event.target.value);
            }}
          />
        </label>
      </div>

      <div className="mt-3 grid gap-2 md:grid-cols-3">
        <label className="grid gap-1 text-xs text-slate-300">
          Sequence Name
          <input
            className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
            value={sequenceName}
            onChange={(event) => {
              setSequenceName(event.target.value);
            }}
          />
        </label>

        <label className="grid gap-1 text-xs text-slate-300">
          Sequence Preset ID
          <input
            className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
            value={presetId}
            onChange={(event) => {
              setPresetId(event.target.value);
            }}
          />
        </label>

        <label className="flex items-center gap-2 pt-6 text-xs text-slate-300">
          <input
            checked={createSequence}
            type="checkbox"
            onChange={(event) => {
              setCreateSequence(event.target.checked);
            }}
          />
          Create sequence from markers
        </label>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        <button
          className="rounded bg-emerald-700 px-3 py-1 text-xs font-semibold text-white"
          type="button"
          onClick={recordManualSnapshot}
        >
          Record Snapshot
        </button>

        <button
          className="rounded border border-amber-600 px-3 py-1 text-xs text-amber-300"
          type="button"
          onClick={undoLastRecord}
          disabled={!recorder.undoAvailable}
        >
          Undo Last Record
        </button>
      </div>

      <div className="mt-3 rounded border border-slate-800 p-2 text-xs text-slate-300">
        <p className="m-0">Secure origin: {recorder.secureOrigin ?? "n/a"}</p>
        <p className="m-0">Rejected bridge messages: {recorder.rejectedMessages}</p>
        <p className="m-0">Last message: {recorder.lastRecordMessage ?? "none"}</p>
      </div>
    </section>
  );
}
