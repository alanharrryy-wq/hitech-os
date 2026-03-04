# PITCH_ENGINE_SUPPORT

## Support Bundle Goals

Support bundle exists to provide deterministic incident payloads for dev-only Pitch Engine runs.

## Export Trigger

UI button in `SupportBundlePanel` invokes API:

`POST /api/pitch-engine/support-bundle?debug=1`

## Bundle Structure

```json
{
  "generatedAt": "ISO timestamp",
  "app": "keystone",
  "route": "/dev/pitch-engine",
  "selectedProgram": {},
  "selectedScene": {},
  "selectedSequence": {},
  "capabilityStatus": {},
  "operatorHud": {},
  "artifactRuns": [],
  "diagnostics": {
    "selectedProgramStats": {
      "scenes": 0,
      "sequences": 0,
      "markers": 0,
      "keyframes": 0
    },
    "links": [],
    "dodResultPath": "optional path"
  },
  "environment": {
    "userAgent": "...",
    "viewport": {
      "width": 0,
      "height": 0,
      "dpr": 1
    },
    "flags": []
  }
}
```

## Included Evidence

- Program JSON snapshot for current selection.
- Scene/sequence context.
- Capability requested/applied mode and degrade reasons.
- HUD state (server/run/error/artifact).
- Artifact index references from tooling run paths.
- Last DoD results path if available.

## Triage Notes Storage

API saves notes to deterministic path:

`tools/codex/runs/runtime/pitch-engine/triage-notes/<runId>/<sceneId>/<sequenceId>/DIFF_NOTES.md`

## Operational HUD Expectations

HUD displays:

- server lifecycle (`starting`, `ready`, `error`)
- last run result (`unknown`, `ok`, `fail`)
- last run path
- last error tail
- last artifact run id

Persisted in localStorage key:

`keystone.pitch-engine.hud`

## Recovery Guidance

1. Export support bundle after failure.
2. Save triage notes for affected artifact item.
3. Run local sanctions command for rerun.
4. Re-open triage panel and verify status transitions.

## Security Notes

- API unavailable in production by hard `404` behavior.
- API unavailable without gate (`debug=1` or env/capability).
- Bridge recorder validates origin and payload schema.

## Recommended Analyst Checklist

1. Confirm requested vs applied capability mode.
2. Validate degrade reasons match environment.
3. Check recorder rejected message count.
4. Inspect triage notes path and action command output.
5. Confirm DoD result path exists before escalation.
