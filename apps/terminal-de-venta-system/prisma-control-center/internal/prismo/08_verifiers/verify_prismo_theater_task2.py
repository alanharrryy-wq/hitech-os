from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


THIS = Path(__file__).resolve()
CONTROL_ROOT = THIS.parents[3]
PY_ROOT = CONTROL_ROOT / "internal" / "py"
WEB_ROOT = CONTROL_ROOT / "internal" / "web"
CONFIG_ROOT = CONTROL_ROOT / "internal" / "config"


REQUIRED_BLOCKS = {
    "hero_response",
    "executive_brief",
    "next_best_action",
    "protocol_ladder",
    "procedural_steps",
    "evidence_board",
    "risk_matrix",
    "memory_trace",
    "authority_strip",
    "insight_chips",
    "flow_diagram",
    "technical_drawer",
    "action_bar",
    "feedback_dock",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def add(results: list[dict[str, Any]], check_id: str, ok: bool, detail: str = "") -> None:
    results.append({"id": check_id, "status": "PASS" if ok else "FAIL", "ok": bool(ok), "detail": detail})


def main() -> int:
    results: list[dict[str, Any]] = []
    index = read(WEB_ROOT / "index.html")
    console = read(WEB_ROOT / "prismo_console.js")
    theater = read(WEB_ROOT / "prismo_ai_theater.js")
    renderers = read(WEB_ROOT / "prismo_renderers.js")
    css = read(WEB_ROOT / "prismo_console.css") + "\n" + read(WEB_ROOT / "prismo_ai_theater.css")
    bridge = read(PY_ROOT / "prismo_ai_bridge.py")
    panel = read(PY_ROOT / "panel_3150.py")
    contracts = read(PY_ROOT / "prismo_render_contracts.py")
    schema = read(CONFIG_ROOT / "prismo_render_blocks.schema.json")

    add(results, "theater-endpoint", "/api/prismo/theater/query" in panel and "prismo_theater_query_payload" in panel)
    add(results, "free-text-composer", "prismoPrompt" in index and "Decision Composer" in index)
    add(results, "exactly-three-guidance-dropdowns", index.count("data-prismo-guidance=") == 3 and all(f'data-prismo-guidance="{key}"' in index for key in ("intent", "area", "lens")))
    add(results, "no-manual-protocol-router", "data-prismo-protocol" not in index and "selectedProtocol" not in theater and "Protocolo solicitado" not in theater)
    add(results, "theater-query-js", '"/api/prismo/theater/query"' in console and 'fetchJson("/api/prismo/query"' not in console)
    add(results, "inferred-chips", "prismoInterpretationChips" in index and "renderInterpretationChips" in console)
    add(results, "feedback-dock", "prismoFeedbackDock" in index and "/api/prismo/learning/feedback" in console)
    add(results, "technical-drawer", "prismoTechnicalDrawer" in index and "renderTechnicalDrawer" in console)
    add(results, "response-memory-chain-ui", all(stage in index for stage in ("Question", "Interpretation", "Protocol", "Evidence", "Result", "Feedback")))
    add(results, "runtime-scripts-loaded", all(src in index for src in ("/prismo_renderers.js", "/prismo_console.js", "/prismo_ai_theater.js")))
    add(results, "required-renderers", REQUIRED_BLOCKS.issubset({block for block in REQUIRED_BLOCKS if f'"{block}"' in renderers}))
    add(results, "required-contract-types", REQUIRED_BLOCKS.issubset({block for block in REQUIRED_BLOCKS if f'"{block}"' in contracts and f'"{block}"' in schema}))
    add(results, "no-raw-html-render-path", "html_sandbox_preview" not in renderers and "<iframe" not in renderers and "srcdoc" not in renderers)
    add(results, "cloudglass-tokens", all(token in css for token in (
        "--prismo-glass-alpha",
        "--prismo-panel-alpha",
        "--prismo-border-alpha",
        "--prismo-z-drawer",
        "--prismo-reduced-motion",
        "--prismo-portal-layer",
    )))
    add(results, "reduced-motion-css", "prefers-reduced-motion" in css)
    add(results, "decorative-layers-noninteractive", "pointer-events: none" in css and "--prismo-z-background" in css)
    add(results, "backend-theater-memory", all(marker in bridge for marker in (
        "response_memory_chain",
        "memory_used",
        "render_plan",
        "feedback",
        "learning_recommend_protocol_payload",
    )))

    forbidden_visible = ["safe mode", "preview only", "coming soon", "future", "experimental", "Playwright Evidence"]
    visible_text = index
    for tag in ("script", "style"):
        while f"<{tag}" in visible_text.lower():
            start = visible_text.lower().find(f"<{tag}")
            end = visible_text.lower().find(f"</{tag}>", start)
            if end == -1:
                break
            visible_text = visible_text[:start] + " " + visible_text[end + len(tag) + 3 :]
    add(results, "forbidden-visible-labels", all(phrase.lower() not in visible_text.lower() for phrase in forbidden_visible))

    sys.path.insert(0, str(PY_ROOT))
    os.environ["PRISMO_AI_DEMO_MODE"] = "true"
    os.environ["PRISMO_AI_ENABLED"] = "false"
    os.environ.pop("GEMINI_API_KEY", None)
    try:
        from prismo_ai_bridge import prismo_theater_query_payload

        payload = prismo_theater_query_payload(
            {
                "message": "¿Qué evidencia reciente explica el riesgo de sync y qué render conviene?",
                "query": "¿Qué evidencia reciente explica el riesgo de sync y qué render conviene?",
                "intent": "",
                "area": "",
                "lens": "",
                "evidenceText": "Static verifier evidence.",
                "client_context": {"surface": "control_center", "route": "/prismo"},
            },
            public=False,
        )
        blocks = payload.get("blocks") or payload.get("render_blocks") or []
        chain = payload.get("response_memory_chain") or {}
        add(results, "python-probe-ok", payload.get("ok") is True and payload.get("read_only") is True and payload.get("mutation_allowed") is False)
        add(results, "python-probe-interpretation", all(key in (payload.get("interpretation") or {}) for key in ("intent", "area", "lens", "chips")))
        add(results, "python-probe-render-blocks", len(blocks) >= 10 and REQUIRED_BLOCKS.intersection({block.get("type") for block in blocks}) >= {"hero_response", "protocol_ladder", "feedback_dock"})
        add(results, "python-probe-memory-chain", all(key in chain for key in ("question", "interpretation", "protocol", "evidence", "result", "feedback")))
    except Exception as exc:  # noqa: BLE001 - verifier reports controlled failure.
        add(results, "python-probe", False, str(exc))

    status = "PASS" if all(item["ok"] for item in results) else "FAIL"
    print(json.dumps({"status": status, "results": results}, ensure_ascii=True, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
