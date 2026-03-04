"use client";

export function SceneStudioHelpPanel() {
  return (
    <aside className="rounded-lg border border-slate-700 bg-slate-950/40 p-3 text-xs text-slate-300">
      <p className="keystone-kicker">Scene Studio Help</p>
      <ul className="m-0 mt-2 list-disc pl-4">
        <li>Use Timeline tab to select an existing scene from the studio list.</li>
        <li>Apply a cinematic preset script to inject a sequence template.</li>
        <li>Scrub playback to preview live transport state before recording.</li>
        <li>When reduced motion is active, preview snaps to final keyframe.</li>
      </ul>
    </aside>
  );
}
