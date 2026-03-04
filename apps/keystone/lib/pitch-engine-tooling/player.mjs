import path from "node:path"
import { OFFLINE_PLAYER_FILES } from "./constants.mjs"
import { ensureDir, writeJsonFile, writeTextFile } from "./fs-utils.mjs"
import { resolvePlayerDir, toRelativeFromArtifacts } from "./paths.mjs"

function buildPlayerHtml() {
  return [
    "<!doctype html>",
    '<html lang="en">',
    "<head>",
    '  <meta charset="utf-8" />',
    '  <meta name="viewport" content="width=device-width,initial-scale=1" />',
    "  <title>Keystone Pitch Engine Player</title>",
    '  <link rel="stylesheet" href="./styles.css" />',
    "</head>",
    "<body>",
    '  <main class="shell">',
    '    <header class="shell__header">',
    "      <h1>Keystone Pitch Engine Player</h1>",
    '      <p id="meta" class="meta">Loading run metadata…</p>',
    "    </header>",
    '    <section class="controls">',
    "      <label>",
    "        Sequence",
    '        <select id="sequence"></select>',
    "      </label>",
    "      <label>",
    "        Frame",
    '        <select id="frame"></select>',
    "      </label>",
    "    </section>",
    '    <section class="viewer">',
    '      <img id="frameImage" alt="Rendered frame" />',
    "    </section>",
    '    <section class="timeline">',
    '      <pre id="timeline"></pre>',
    "    </section>",
    "  </main>",
    '  <script type="module" src="./player.js"></script>',
    "</body>",
    "</html>",
    ""
  ].join("\n")
}

function buildPlayerCss() {
  return [
    ":root {",
    "  --bg: #f1f5f9;",
    "  --surface: #ffffff;",
    "  --ink: #0f172a;",
    "  --muted: #475569;",
    "  --line: #cbd5e1;",
    "}",
    "* { box-sizing: border-box; }",
    "body {",
    "  margin: 0;",
    "  font-family: \"Segoe UI\", Tahoma, Geneva, Verdana, sans-serif;",
    "  color: var(--ink);",
    "  background: radial-gradient(circle at top left, #e2e8f0, #f8fafc 45%);",
    "}",
    ".shell {",
    "  max-width: 1100px;",
    "  margin: 0 auto;",
    "  padding: 24px;",
    "}",
    ".shell__header { margin-bottom: 18px; }",
    ".meta { color: var(--muted); font-size: 0.95rem; }",
    ".controls { display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 16px; }",
    "label { display: flex; flex-direction: column; gap: 6px; min-width: 180px; }",
    "select { border: 1px solid var(--line); border-radius: 6px; padding: 8px 10px; background: var(--surface); }",
    ".viewer { border: 1px solid var(--line); background: var(--surface); border-radius: 10px; padding: 10px; }",
    "#frameImage { width: 100%; border-radius: 6px; background: linear-gradient(180deg, #f8fafc, #e2e8f0); }",
    ".timeline { margin-top: 14px; border: 1px solid var(--line); border-radius: 8px; background: var(--surface); padding: 10px; }",
    "pre { margin: 0; white-space: pre-wrap; font-size: 0.85rem; color: #1e293b; }",
    "@media (max-width: 700px) { .shell { padding: 14px; } }",
    ""
  ].join("\n")
}

function buildPlayerJs() {
  return [
    "const state = { runData: null };",
    "const sequenceSelect = document.getElementById('sequence');",
    "const frameSelect = document.getElementById('frame');",
    "const frameImage = document.getElementById('frameImage');",
    "const meta = document.getElementById('meta');",
    "const timelineView = document.getElementById('timeline');",
    "",
    "async function loadData() {",
    "  const response = await fetch('../timeline.json', { cache: 'no-store' });",
    "  const timeline = await response.json();",
    "  state.runData = timeline;",
    "",
    "  sequenceSelect.innerHTML = '';",
    "  for (const sequence of timeline.sequences || []) {",
    "    const option = document.createElement('option');",
    "    option.value = sequence.sequenceId;",
    "    option.textContent = sequence.sequenceId;",
    "    sequenceSelect.appendChild(option);",
    "  }",
    "",
    "  if ((timeline.sequences || []).length > 0) {",
    "    sequenceSelect.value = timeline.sequences[0].sequenceId;",
    "    updateFrames();",
    "  }",
    "",
    "  meta.textContent = 'Run profile: ' + timeline.runProfile + ' | Sequences: ' + (timeline.sequences || []).length;",
    "  timelineView.textContent = JSON.stringify({ generatedAtUtc: timeline.generatedAtUtc, totalCaptures: timeline.totalCaptures, hash: timeline.hash }, null, 2);",
    "}",
    "",
    "function updateFrames() {",
    "  if (!state.runData) return;",
    "  const sequence = (state.runData.sequences || []).find((entry) => entry.sequenceId === sequenceSelect.value);",
    "  if (!sequence) return;",
    "",
    "  frameSelect.innerHTML = '';",
    "  for (const tMs of sequence.timestampsMs || []) {",
    "    const option = document.createElement('option');",
    "    option.value = String(tMs);",
    "    option.textContent = String(tMs).padStart(5, '0') + ' ms';",
    "    frameSelect.appendChild(option);",
    "  }",
    "",
    "  if ((sequence.timestampsMs || []).length > 0) {",
    "    frameSelect.value = String(sequence.timestampsMs[0]);",
    "    updateImage();",
    "  }",
    "}",
    "",
    "function updateImage() {",
    "  const sequenceId = sequenceSelect.value;",
    "  const frameName = String(frameSelect.value).padStart(5, '0') + '.png';",
    "  frameImage.src = '../sequences/' + sequenceId + '/frames/' + frameName;",
    "  frameImage.alt = sequenceId + ' ' + frameName;",
    "}",
    "",
    "sequenceSelect.addEventListener('change', updateFrames);",
    "frameSelect.addEventListener('change', updateImage);",
    "",
    "loadData().catch((error) => {",
    "  meta.textContent = 'Failed to load player data: ' + error.message;",
    "});",
    ""
  ].join("\n")
}

export async function generateOfflinePlayer(programId, runId, timelineData) {
  const playerDir = resolvePlayerDir(programId, runId)
  await ensureDir(playerDir)

  const htmlPath = path.join(playerDir, OFFLINE_PLAYER_FILES[0])
  const jsPath = path.join(playerDir, OFFLINE_PLAYER_FILES[1])
  const cssPath = path.join(playerDir, OFFLINE_PLAYER_FILES[2])

  await writeTextFile(htmlPath, buildPlayerHtml())
  await writeTextFile(jsPath, buildPlayerJs())
  await writeTextFile(cssPath, buildPlayerCss())
  await writeJsonFile(path.join(playerDir, "player.meta.json"), {
    generatedAtUtc: new Date().toISOString(),
    files: OFFLINE_PLAYER_FILES,
    timelineHash: timelineData.hash,
    sequenceCount: timelineData.sequences.length
  })

  return {
    playerDir: toRelativeFromArtifacts(playerDir),
    files: OFFLINE_PLAYER_FILES.map((fileName) => `${toRelativeFromArtifacts(playerDir)}/${fileName}`)
  }
}
