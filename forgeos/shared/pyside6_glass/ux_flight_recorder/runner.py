from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from unittest import mock

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget

from ..examples.demo_app import create_workbench_window
from .capabilities import capability_matrix_delta, load_capability_contract
from .comparator import compare_semantic_baseline
from .recorder import SessionRecorder
from .specs import (
    BASELINE_ROOT,
    BASELINE_VERSION,
    GOLDEN_SESSIONS_PATH,
    PREMIUM_CONTRACT_PATH,
    SEMANTIC_BASELINE_PATH,
    VISUAL_BASELINE_PATH,
    load_golden_sessions,
    load_json_file,
)


@dataclass(slots=True)
class _FakeMouseEvent:
    global_point: QPoint

    def globalPosition(self) -> QPointF:
        return QPointF(float(self.global_point.x()), float(self.global_point.y()))

    def button(self) -> Qt.MouseButton:
        return Qt.LeftButton

    def buttons(self) -> Qt.MouseButtons:
        return Qt.LeftButton


def _contract_digest(path: Path) -> str:
    if not path.exists():
        return "missing"
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest()[:16]


def _find_shell(window: QWidget) -> Any:
    workbench = getattr(window, "workbench", None)
    shell = getattr(workbench, "_catalog", None)
    if shell is not None:
        return shell
    return workbench


def _process_events(app: QApplication) -> None:
    app.processEvents()
    app.processEvents()


def _set_picker_category(shell: Any, value: str) -> None:
    target = str(value or "").strip().lower()
    combo = shell.picker_category_combo
    for index in range(combo.count()):
        item = str(combo.itemData(index) or combo.itemText(index) or "").strip().lower()
        if item == target:
            combo.setCurrentIndex(index)
            return


def _prepare_editor_context(shell: Any) -> None:
    shell._set_inspector_panel_visible(True)
    shell._clear_filters()
    shell._select_entry("example.form")
    shell._on_entry_selected(shell.entry_list.currentItem(), None)
    shell._open_selected_preview()
    shell._refresh_editor_contexts(select_context="preview")


def _resolve_pending_candidate(shell: Any) -> Any | None:
    candidate = getattr(shell, "_pending_candidate_overlay", None)
    if candidate is None:
        return None
    try:
        candidate.parentWidget()
    except RuntimeError:
        return None
    return candidate


def _confirm_pending_candidate(shell: Any) -> bool:
    candidate = _resolve_pending_candidate(shell)
    if candidate is None:
        return False
    shell._commit_pending_panel_candidate()
    return True


def _insert_chart_panel(shell: Any) -> None:
    shell.editor_palette_search.setText("chart")
    shell._refresh_insert_palette()
    if shell.editor_palette_list.count() <= 0:
        raise RuntimeError("insert palette has no chart entries")
    shell.editor_palette_list.setCurrentRow(0)
    shell._add_editor_panel()
    _confirm_pending_candidate(shell)
    session = shell._current_editor_session()
    if session is None or not session.dynamic_working:
        raise RuntimeError("dynamic panel insert failed")
    shell._set_selected_editor_panel(session, session.dynamic_working[-1].panel_id)


def _selected_panel(shell: Any) -> tuple[Any, Any, str]:
    session = shell._current_editor_session()
    template = shell._current_editor_template()
    if session is None or template is None:
        raise RuntimeError("editor context unavailable")
    panel_id = str(session.selected_panel_id or "")
    if not panel_id and session.dynamic_working:
        panel_id = session.dynamic_working[-1].panel_id
    if not panel_id:
        raise RuntimeError("no selected panel")
    panel = template.panel(panel_id)
    if panel is None:
        raise RuntimeError(f"panel '{panel_id}' not found")
    return session, template, panel_id


def _drag_selected_panel_to_side(shell: Any) -> None:
    session, template, panel_id = _selected_panel(shell)
    panel = template.panel(panel_id)
    if panel is None:
        raise RuntimeError("panel missing for drag")
    origin = panel.mapToGlobal(panel.rect().center())
    shell._start_panel_drag(context_id=session.context_id, panel_id=panel_id, event=_FakeMouseEvent(origin))
    side_widget = template.slots.side_slot.parentWidget()
    if side_widget is None:
        raise RuntimeError("side slot widget missing")
    target = side_widget.mapToGlobal(side_widget.rect().center())
    shell._apply_panel_drag(_FakeMouseEvent(target))
    shell._finish_panel_drag()


def _resize_selected_panel(shell: Any, *, delta_y: int) -> None:
    session, template, panel_id = _selected_panel(shell)
    panel = template.panel(panel_id)
    if panel is None:
        raise RuntimeError("panel missing for resize")
    anchor = panel.mapToGlobal(QPoint(max(8, panel.width() // 2), max(8, panel.height() - 2)))
    shell._start_panel_resize(context_id=session.context_id, panel_id=panel_id, panel=panel)
    shell._apply_panel_resize(_FakeMouseEvent(QPoint(anchor.x(), anchor.y() + int(delta_y))))
    shell._finish_panel_resize()


def _execute_action(
    *,
    action: dict[str, Any],
    shell: Any,
    window: QWidget,
    app: QApplication,
    recorder: SessionRecorder,
    screenshots_enabled: bool,
) -> None:
    name = str(action.get("action") or "").strip().lower()
    if name == "show":
        window.show()
        _process_events(app)
        recorder.log_event("ui", "Window shown")
        return
    if name == "open_picker":
        shell._open_entry_picker()
        _process_events(app)
        recorder.log_event("ui", "Picker opened")
        return
    if name == "close_picker":
        if hasattr(shell, "entry_picker_dialog"):
            shell.entry_picker_dialog.hide()
        _process_events(app)
        recorder.log_event("ui", "Picker closed")
        return
    if name == "picker_search":
        shell.picker_search_input.setText(str(action.get("text") or ""))
        shell._refresh_picker_entries()
        _process_events(app)
        recorder.log_event("interaction", "Picker search applied", text=str(action.get("text") or ""))
        return
    if name == "picker_set_category":
        _set_picker_category(shell, str(action.get("value") or "All"))
        shell._refresh_picker_entries()
        _process_events(app)
        recorder.log_event("interaction", "Picker category set", category=str(action.get("value") or ""))
        return
    if name == "picker_select_first":
        if shell.picker_entry_list.count() > 0:
            shell.picker_entry_list.setCurrentRow(0)
            _process_events(app)
        recorder.log_event("interaction", "Picker first entry selected")
        return
    if name == "picker_add_current":
        shell._picker_add_to_current_tab()
        _process_events(app)
        _confirm_pending_candidate(shell)
        recorder.log_event("interaction", "Picker add to current tab")
        return
    if name == "picker_open_new_tab":
        shell._picker_open_in_new_tab()
        _process_events(app)
        _confirm_pending_candidate(shell)
        recorder.log_event("interaction", "Picker open in new tab")
        return
    if name == "open_empty_tab":
        shell._open_empty_workspace_tab()
        _process_events(app)
        recorder.log_event("interaction", "Empty workspace tab opened")
        return
    if name == "select_category":
        shell._clear_filters()
        shell._select_category(str(action.get("value") or "All"))
        shell._refresh_entries()
        _process_events(app)
        recorder.log_event("interaction", "Category selected", category=str(action.get("value") or ""))
        return
    if name == "select_entry":
        shell._select_entry(str(action.get("value") or ""))
        shell._on_entry_selected(shell.entry_list.currentItem(), None)
        _process_events(app)
        recorder.log_event("interaction", "Entry selected", entry_id=str(action.get("value") or ""))
        return
    if name == "prepare_editor_context":
        _prepare_editor_context(shell)
        _process_events(app)
        recorder.log_event("interaction", "Editor context prepared")
        return
    if name == "insert_chart_panel":
        _insert_chart_panel(shell)
        _process_events(app)
        recorder.log_event("interaction", "Chart panel inserted")
        return
    if name == "drag_selected_panel_to_side":
        _drag_selected_panel_to_side(shell)
        _process_events(app)
        recorder.log_event("interaction", "Selected panel dragged to side slot")
        return
    if name == "resize_selected_panel":
        _resize_selected_panel(shell, delta_y=int(action.get("delta_y") or 60))
        _process_events(app)
        recorder.log_event("interaction", "Selected panel resized", delta_y=int(action.get("delta_y") or 60))
        return
    if name == "save_clone":
        clone_name = str(action.get("name") or f"golden_clone_{datetime.now().strftime('%H%M%S')}")
        with mock.patch(
            "forgeos.shared.pyside6_glass.examples.catalog_shell.QMessageBox.question",
            return_value=QMessageBox.Yes,
        ), mock.patch(
            "forgeos.shared.pyside6_glass.examples.catalog_shell.QInputDialog.getText",
            return_value=(clone_name, True),
        ):
            shell._save_clone()
        _process_events(app)
        recorder.log_event("interaction", "Clone saved", clone_name=clone_name)
        return
    if name == "reset_editor":
        shell._reset_editor_session()
        _process_events(app)
        recorder.log_event("interaction", "Editor session reset")
        return
    if name == "probe_selected_query":
        shell._set_inspector_panel_visible(True)
        shell._probe_selected_query()
        _process_events(app)
        recorder.log_event("interaction", "Selected query probed")
        return
    if name == "refresh_runtime":
        shell._set_inspector_panel_visible(True)
        shell._refresh_runtime_button()
        _process_events(app)
        recorder.log_event("interaction", "Runtime diagnostics refreshed")
        return
    if name == "checkpoint":
        checkpoint_id = str(action.get("id") or "").strip()
        if not checkpoint_id:
            raise RuntimeError("checkpoint step missing id")
        snapshot = shell.capture_semantic_checkpoint(checkpoint_id)
        screenshot_rel = ""
        if screenshots_enabled:
            target = recorder.output_dir / "screenshots" / f"{checkpoint_id}.png"
            if shell.capture_checkpoint_screenshot(target):
                screenshot_rel = str(target.relative_to(recorder.output_dir))
        recorder.checkpoint(
            checkpoint_id=checkpoint_id,
            snapshot=snapshot,
            screenshot_path=screenshot_rel,
        )
        return
    raise RuntimeError(f"Unsupported session action: {name}")


def _validate_session(session_id: str, recorder: SessionRecorder) -> None:
    checkpoints = recorder.checkpoints
    if not checkpoints:
        recorder.fail("Session produced no checkpoints.")
        return
    if session_id == "startup_blank_workspace":
        snap = checkpoints["startup.blank"]["snapshot"]
        if not snap.get("active_workspace_id"):
            recorder.fail("Startup snapshot has no active workspace id.")
    elif session_id == "picker_search_and_category":
        snap = checkpoints["picker.filtered"]["snapshot"]
        if not snap.get("picker_open"):
            recorder.fail("Picker filtered checkpoint expected picker_open=True.")
    elif session_id == "add_to_current_tab":
        snap = checkpoints["tab.current.added"]["snapshot"]
        active_tab = str(snap.get("active_tab_id") or "")
        lazy = snap.get("lazy_mount_state", {})
        if not active_tab or not isinstance(lazy, dict):
            recorder.fail("Add-to-current checkpoint missing active tab or lazy state.")
        elif not bool(lazy.get(active_tab, {}).get("mounted", False)):
            recorder.fail("Active tab is not mounted after add-to-current.")
    elif session_id == "open_in_new_tab":
        snap = checkpoints["tab.new.opened"]["snapshot"]
        if len(snap.get("workspace_tab_ids", [])) < 2:
            recorder.fail("Open-in-new-tab did not increase workspace tab count.")
    elif session_id == "drag_panel_cross_slot":
        snap = checkpoints["panel.drag.cross_slot"]["snapshot"]
        slots = snap.get("slot_assignments", {})
        if not any(str(slot).lower() == "side" for slot in slots.values()):
            recorder.fail("Drag cross-slot checkpoint does not show panel in side slot.")
    elif session_id == "resize_panel_and_clamp":
        snap = checkpoints["panel.resize.clamped"]["snapshot"]
        geometries = snap.get("panel_geometries", {})
        if not geometries:
            recorder.fail("Resize checkpoint has no panel geometries.")
        elif min(int(item.get("height", 0)) for item in geometries.values()) < 90:
            recorder.fail("Resize checkpoint geometry below expected clamp minimum.")
    elif session_id == "clone_reset_isolation":
        saved = checkpoints["clone.saved"]["snapshot"]
        reset = checkpoints["clone.reset"]["snapshot"]
        if str(saved.get("clone_state", {}).get("source_kind", "")) != "clone":
            recorder.fail("Clone saved checkpoint expected source_kind='clone'.")
        if bool(reset.get("dirty_state", {}).get("is_dirty", False)):
            recorder.fail("Reset checkpoint expected dirty_state=False.")
    elif session_id == "data_runtime_probe_states":
        snap = checkpoints["data.runtime.probed"]["snapshot"]
        data_state = snap.get("data_state", {})
        runtime_state = snap.get("runtime_state", {})
        if not data_state or "query_id" not in data_state:
            recorder.fail("Data/runtime checkpoint missing query probe payload.")
        if not runtime_state or "integration_boundary" not in runtime_state:
            recorder.fail("Data/runtime checkpoint missing runtime diagnostics payload.")


def _session_required_capabilities(spec: dict[str, Any]) -> list[int]:
    result: list[int] = []
    for item in spec.get("sacred_capabilities", []):
        text = str(item).strip()
        if not text.isdigit():
            continue
        value = int(text)
        if value not in result:
            result.append(value)
    return result


def _session_expected_checkpoints(spec: dict[str, Any]) -> list[str]:
    result: list[str] = []
    for item in spec.get("checkpoints", []):
        text = str(item).strip()
        if text and text not in result:
            result.append(text)
    return result


def _collect_covered_capabilities(
    *,
    sessions_spec: list[dict[str, Any]],
    run_sessions: dict[str, dict[str, Any]],
) -> list[int]:
    covered: set[int] = set()
    by_session = {str(spec.get("session_id", "")).strip(): spec for spec in sessions_spec}
    for session_id, payload in run_sessions.items():
        if not bool(payload.get("passed", False)):
            continue
        spec = by_session.get(session_id, {})
        for capability_id in _session_required_capabilities(spec):
            covered.add(capability_id)
    return sorted(covered)


def _build_markdown_report(
    *,
    output_dir: Path,
    summary: dict[str, Any],
) -> str:
    lines: list[str] = []
    lines.append("# UX Release Proof")
    lines.append("")
    lines.append(f"- Generated UTC: {summary.get('generated_at_utc')}")
    lines.append(f"- Passed: {summary.get('passed')}")
    lines.append(f"- Sacred contract digest: `{summary.get('sacred_contract_digest')}`")
    lines.append(f"- Baseline version: `{summary.get('baseline_version')}`")
    lines.append(f"- Baseline digest: `{summary.get('baseline_digest')}`")
    lines.append("")
    lines.append("## Session Results")
    for row in summary.get("sessions_summary", []):
        lines.append(
            f"- `{row['session_id']}`: {'PASS' if row.get('passed') else 'FAIL'} "
            f"(events={row.get('event_count')} checkpoints={row.get('checkpoint_count')} "
            f"severity={row.get('failure_severity')})"
        )
    lines.append("")
    lines.append("## Comparator")
    comparator = summary.get("comparator", {})
    lines.append(f"- Passed: {comparator.get('passed')}")
    lines.append(f"- Max severity: {comparator.get('max_severity')}")
    lines.append(f"- Diff count: {comparator.get('diff_count')}")
    lines.append(f"- Severity counts: {comparator.get('counts_by_severity')}")
    lines.append("")
    lines.append("## Capability Delta")
    capability_delta = summary.get("capability_delta", [])
    lines.append(f"- Total capabilities: {len(capability_delta)}")
    if capability_delta:
        solid = sum(1 for item in capability_delta if item.get("after_status") == "solid")
        improved_partial = sum(1 for item in capability_delta if item.get("after_status") == "improved_partial")
        partial = sum(1 for item in capability_delta if item.get("after_status") == "partial")
        deferred = sum(1 for item in capability_delta if item.get("after_status") == "deferred")
        lines.append(f"- Solid: {solid}")
        lines.append(f"- Improved partial: {improved_partial}")
        lines.append(f"- Partial: {partial}")
        lines.append(f"- Deferred: {deferred}")
    lines.append("")
    lines.append("## Baseline")
    lines.append(f"- Semantic baseline: `{summary.get('baseline_path')}`")
    lines.append(f"- Visual baseline manifest: `{summary.get('visual_baseline_path')}`")
    lines.append(f"- Refreshed baseline this run: `{summary.get('refresh_baseline')}`")
    lines.append("")
    lines.append("## Artifacts")
    lines.append("- `golden_sessions_summary.json`")
    lines.append("- `comparison_report.json`")
    lines.append("- `capability_matrix_delta.json`")
    lines.append("- `semantic_run_payload.json`")
    lines.append("- `sessions/*` (manifests, events, checkpoints, screenshots)")
    lines.append("")
    report = "\n".join(lines)
    (output_dir / "UX_RELEASE_PROOF.md").write_text(report, encoding="utf-8")
    return report


def _resolve_path(value: Path | str | None, fallback: Path) -> Path:
    if value is None:
        return Path(fallback)
    return Path(value).resolve()


def run_ux_release_proof(
    *,
    refresh_baseline: bool = False,
    screenshots_enabled: bool = True,
    headless: bool = True,
    output_root: Path | None = None,
    extra_evidence_tags: Iterable[str] | None = None,
    semantic_baseline_path: Path | None = None,
    visual_baseline_path: Path | None = None,
    baseline_root: Path | None = None,
) -> dict[str, Any]:
    if headless:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    sessions_spec_payload = load_golden_sessions()
    sessions_spec = sessions_spec_payload.get("sessions", [])
    if not isinstance(sessions_spec, list) or not sessions_spec:
        raise RuntimeError("Golden sessions specification is missing or empty.")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_output = output_root or (Path(__file__).resolve().parents[1] / "artifacts" / "ux_release_proof")
    run_dir = base_output / stamp
    sessions_root = run_dir / "sessions"
    sessions_root.mkdir(parents=True, exist_ok=True)

    resolved_semantic_baseline = _resolve_path(semantic_baseline_path, SEMANTIC_BASELINE_PATH)
    resolved_visual_baseline = _resolve_path(visual_baseline_path, VISUAL_BASELINE_PATH)
    resolved_baseline_root = _resolve_path(baseline_root, BASELINE_ROOT)

    app = QApplication.instance() or QApplication([])
    window = create_workbench_window()
    shell = _find_shell(window)
    if shell is None:
        raise RuntimeError("Unable to resolve GlassCatalogShell from workbench window.")
    window.show()
    _process_events(app)

    run_sessions: dict[str, dict[str, Any]] = {}
    evidence_tags: set[str] = {str(tag).strip() for tag in (extra_evidence_tags or []) if str(tag).strip()}
    try:
        for spec in sessions_spec:
            session_id = str(spec.get("session_id") or "").strip()
            if not session_id:
                continue
            recorder = SessionRecorder(
                session_id=session_id,
                output_dir=sessions_root / session_id,
                purpose=str(spec.get("purpose") or ""),
                failure_severity=str(spec.get("failure_severity") or "major"),
                required_capabilities=_session_required_capabilities(spec),
                expected_checkpoints=_session_expected_checkpoints(spec),
            )
            try:
                for step in spec.get("steps", []):
                    if not isinstance(step, dict):
                        continue
                    _execute_action(
                        action=step,
                        shell=shell,
                        window=window,
                        app=app,
                        recorder=recorder,
                        screenshots_enabled=screenshots_enabled,
                    )
                _validate_session(session_id, recorder)
            except Exception as exc:  # noqa: BLE001
                recorder.fail(f"Session exception: {exc}")
            manifest = recorder.finalize(passed=not recorder.errors)
            run_sessions[session_id] = {
                "manifest": manifest,
                "passed": bool(manifest.get("passed", False)),
                "checkpoints": recorder.checkpoints,
                "events": recorder.events,
            }
            if manifest.get("passed", False):
                evidence_tags.add(f"session:{session_id}:pass")
            else:
                evidence_tags.add(f"session:{session_id}:fail")

        covered_capabilities = _collect_covered_capabilities(
            sessions_spec=sessions_spec,
            run_sessions=run_sessions,
        )
        required_capabilities = sorted({cap for spec in sessions_spec for cap in _session_required_capabilities(spec)})
        required_session_ids = [str(spec.get("session_id") or "").strip() for spec in sessions_spec if str(spec.get("session_id") or "").strip()]

        semantic_run = {
            "version": BASELINE_VERSION,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "sessions": {
                session_id: {
                    "passed": bool(payload.get("passed", False)),
                    "purpose": str(payload.get("manifest", {}).get("purpose", "")),
                    "failure_severity": str(payload.get("manifest", {}).get("failure_severity", "major")),
                    "required_capabilities": list(payload.get("manifest", {}).get("required_capabilities", [])),
                    "expected_checkpoints": list(payload.get("manifest", {}).get("expected_checkpoints", [])),
                    "event_count": int(payload.get("manifest", {}).get("event_count", 0)),
                    "event_types": list(payload.get("manifest", {}).get("event_types", [])),
                    "checkpoints": payload.get("checkpoints", {}),
                }
                for session_id, payload in run_sessions.items()
            },
            "covered_capabilities": covered_capabilities,
        }

        baseline = load_json_file(resolved_semantic_baseline)
        visual_baseline_manifest = load_json_file(resolved_visual_baseline)
        baseline_digest = _contract_digest(resolved_semantic_baseline) if baseline else "missing"
        visual_baseline_digest = _contract_digest(resolved_visual_baseline) if visual_baseline_manifest else "missing"

        if refresh_baseline:
            resolved_baseline_root.mkdir(parents=True, exist_ok=True)
            resolved_semantic_baseline.write_text(
                json.dumps(semantic_run, indent=2, ensure_ascii=True),
                encoding="utf-8",
            )
            visual_manifest = {
                "version": BASELINE_VERSION,
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "screenshots_root": "sessions/*/screenshots",
                "note": "Visual evidence is secondary. Semantic baseline is release authority.",
            }
            resolved_visual_baseline.write_text(
                json.dumps(visual_manifest, indent=2, ensure_ascii=True),
                encoding="utf-8",
            )
            baseline = semantic_run
            visual_baseline_manifest = visual_manifest
            baseline_digest = _contract_digest(resolved_semantic_baseline)
            visual_baseline_digest = _contract_digest(resolved_visual_baseline)

        comparator = compare_semantic_baseline(
            baseline=baseline,
            run_payload=semantic_run,
            required_session_ids=required_session_ids,
            required_capabilities=required_capabilities,
        )
        evidence_tags.add("check:proof_runner:pass" if comparator.get("passed", False) else "check:proof_runner:fail")

        sessions_summary = []
        for session_id, payload in run_sessions.items():
            manifest = payload.get("manifest", {})
            sessions_summary.append(
                {
                    "session_id": session_id,
                    "purpose": str(manifest.get("purpose", "")),
                    "failure_severity": str(manifest.get("failure_severity", "major")),
                    "required_capabilities": list(manifest.get("required_capabilities", [])),
                    "passed": bool(manifest.get("passed", False)),
                    "event_count": int(manifest.get("event_count", 0)),
                    "event_types": list(manifest.get("event_types", [])),
                    "checkpoint_count": int(manifest.get("checkpoint_count", 0)),
                    "warnings": list(manifest.get("warnings", [])),
                    "errors": list(manifest.get("errors", [])),
                }
            )

        all_sessions_passed = all(item.get("passed", False) for item in sessions_summary)
        summary_passed = all_sessions_passed and bool(comparator.get("passed", False))
        if all_sessions_passed:
            evidence_tags.add("check:session_suite_complete:pass")
        if bool(comparator.get("passed", False)):
            evidence_tags.add("check:semantic_comparator:pass")
        sacred_contract_path = Path(__file__).resolve().parents[1] / "SACRED_CAPABILITIES_CONTRACT.md"
        all_capabilities = load_capability_contract()
        summary = {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "run_dir": str(run_dir),
            "sessions_spec_path": str(GOLDEN_SESSIONS_PATH),
            "baseline_version": BASELINE_VERSION,
            "baseline_path": str(resolved_semantic_baseline),
            "visual_baseline_path": str(resolved_visual_baseline),
            "baseline_digest": baseline_digest,
            "visual_baseline_digest": visual_baseline_digest,
            "baseline_present": bool(baseline),
            "sacred_contract_path": str(sacred_contract_path),
            "sacred_contract_digest": _contract_digest(sacred_contract_path),
            "premium_contract_path": str(PREMIUM_CONTRACT_PATH),
            "premium_contract_digest": _contract_digest(PREMIUM_CONTRACT_PATH),
            "premium_capability_count": len(all_capabilities),
            "refresh_baseline": bool(refresh_baseline),
            "passed": bool(summary_passed),
            "sessions_summary": sessions_summary,
            "required_session_ids": required_session_ids,
            "required_capabilities": required_capabilities,
            "covered_capabilities": covered_capabilities,
            "comparator": comparator,
        }

        capability_delta = capability_matrix_delta(evidence_tags)
        summary["capability_delta"] = capability_delta
        summary["evidence_tags"] = sorted(evidence_tags)

        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "session_specs.json").write_text(
            json.dumps(sessions_spec_payload, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
        (run_dir / "golden_sessions_summary.json").write_text(
            json.dumps(summary, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
        (run_dir / "comparison_report.json").write_text(
            json.dumps(comparator, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
        (run_dir / "semantic_run_payload.json").write_text(
            json.dumps(semantic_run, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
        (run_dir / "capability_matrix_delta.json").write_text(
            json.dumps(capability_delta, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
        _build_markdown_report(output_dir=run_dir, summary=summary)
        return summary
    finally:
        window.close()
        _process_events(app)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run pyside6_glass UX release proof golden sessions.")
    parser.add_argument("--refresh-baseline", action="store_true", help="Refresh semantic + visual baseline with current run.")
    parser.add_argument("--no-screenshots", action="store_true", help="Disable checkpoint screenshots.")
    parser.add_argument("--headed", action="store_true", help="Run in headed mode (not offscreen).")
    parser.add_argument("--output-root", type=str, default="", help="Optional output root for release proof artifacts.")
    parser.add_argument("--baseline-root", type=str, default="", help="Optional baseline root override.")
    parser.add_argument("--semantic-baseline-path", type=str, default="", help="Optional semantic baseline path override.")
    parser.add_argument("--visual-baseline-path", type=str, default="", help="Optional visual baseline path override.")
    parser.add_argument(
        "--extra-evidence-tag",
        action="append",
        default=[],
        help="Append evidence tags used by capability delta (repeatable).",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    output_root = Path(args.output_root).resolve() if str(args.output_root).strip() else None
    baseline_root = Path(args.baseline_root).resolve() if str(args.baseline_root).strip() else None
    semantic_baseline_path = (
        Path(args.semantic_baseline_path).resolve() if str(args.semantic_baseline_path).strip() else None
    )
    visual_baseline_path = Path(args.visual_baseline_path).resolve() if str(args.visual_baseline_path).strip() else None
    summary = run_ux_release_proof(
        refresh_baseline=bool(args.refresh_baseline),
        screenshots_enabled=not bool(args.no_screenshots),
        headless=not bool(args.headed),
        output_root=output_root,
        extra_evidence_tags=args.extra_evidence_tag,
        baseline_root=baseline_root,
        semantic_baseline_path=semantic_baseline_path,
        visual_baseline_path=visual_baseline_path,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    return 0 if bool(summary.get("passed", False)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
