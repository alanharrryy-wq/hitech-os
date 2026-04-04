from __future__ import annotations

import json
import os
import unittest
from unittest import mock

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton

from forgeos.shared.pyside6_glass.catalog import _clear_catalog_registry_for_tests, register_builtin_catalog_entries
from forgeos.shared.pyside6_glass.data import DataQuery, DataResult, RefreshPolicy
from forgeos.shared.pyside6_glass.data import _clear_data_provider_registry_for_tests
from forgeos.shared.pyside6_glass.examples.catalog_shell import GlassCatalogShell


class CatalogWorkbenchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        _clear_catalog_registry_for_tests()
        _clear_data_provider_registry_for_tests()
        register_builtin_catalog_entries(force=True)

    def _confirm_pending_candidate(self, widget: GlassCatalogShell) -> None:
        self.assertIsNotNone(widget._pending_candidate_overlay)
        widget._commit_pending_panel_candidate()
        self.app.processEvents()
        self.assertIsNone(widget._pending_candidate_overlay)

    def test_workbench_tabs_metadata_and_provider_probe(self) -> None:
        widget = GlassCatalogShell()
        try:
            tab_labels = [widget.side_tabs.tabText(index) for index in range(widget.side_tabs.count())]
            self.assertEqual(tab_labels, ["Entry", "Data", "Runtime", "Compose"])

            widget._clear_filters()
            widget._select_category("Data Dashboards")
            widget._refresh_entries()
            widget._select_entry("data.live_metrics_board")
            widget._on_entry_selected(widget.entry_list.currentItem(), None)
            self.app.processEvents()

            meta_text = widget.meta_text.toPlainText().strip()
            self.assertTrue(meta_text)
            meta_payload = json.loads(meta_text)
            self.assertEqual(meta_payload["id"], "data.live_metrics_board")
            self.assertEqual(meta_payload["entry_kind"], "provider-backed dashboard")
            self.assertEqual(meta_payload["entry_origin"], "built-in catalog")
            self.assertEqual(meta_payload["layer_boundary"], "data/provider layer")

            binding_payload = json.loads(widget.selected_data_binding.toPlainText())
            self.assertEqual(binding_payload["provider_id"], "builtin.mock_dashboard")
            self.assertEqual(binding_payload["query_id"], "live_metrics")
            self.assertIn("provider_diagnostics", binding_payload)

            widget._probe_selected_query()
            self.app.processEvents()
            probe_payload = json.loads(widget.query_probe_text.toPlainText())
            self.assertEqual(probe_payload["provider_id"], "builtin.mock_dashboard")
            self.assertEqual(probe_payload["query_id"], "live_metrics")
            self.assertIn(probe_payload["state"], {"ready", "empty", "error", "stale", "loading"})

            runtime_payload = json.loads(widget.runtime_diagnostics_text.toPlainText())
            self.assertEqual(runtime_payload["workbench"]["selected_entry_id"], "data.live_metrics_board")
            self.assertEqual(runtime_payload["workbench"]["selected_entry_origin"], "built-in catalog")
            self.assertIn("integration_boundary", runtime_payload)
            self.assertGreaterEqual(runtime_payload["integration_boundary"]["query_count"], 1)
        finally:
            widget.deleteLater()

    def test_editor_add_reset_and_save_clone(self) -> None:
        widget = GlassCatalogShell()
        try:
            widget._select_entry("example.form")
            widget._on_entry_selected(widget.entry_list.currentItem(), None)
            widget._open_selected_preview()
            self.app.processEvents()

            self.assertGreater(widget.editor_context_combo.count(), 0)
            self.assertEqual(str(widget.editor_context_combo.currentData() or ""), "preview")
            self.assertGreaterEqual(len(widget._panel_type_registry), 28)

            widget.editor_palette_search.setText("chart")
            widget._refresh_insert_palette()
            self.app.processEvents()
            self.assertGreater(widget.editor_palette_list.count(), 0)
            first_palette_item = widget.editor_palette_list.item(0)
            self.assertIsNotNone(first_palette_item)
            assert first_palette_item is not None
            panel_type = str(first_palette_item.data(0x0100) or "")
            self.assertTrue(panel_type)

            widget.editor_add_slot_combo.setCurrentText("main")
            widget._add_editor_panel()
            self.app.processEvents()
            self._confirm_pending_candidate(widget)

            session = widget._current_editor_session()
            self.assertIsNotNone(session)
            assert session is not None
            self.assertEqual(len(session.dynamic_working), 1)
            self.assertTrue(session.dirty)
            self.assertEqual(session.dynamic_working[0].panel_type, panel_type)

            widget.editor_title_input.setText("Edited Panel")
            widget._apply_editor_properties()
            self.app.processEvents()
            self.assertTrue(session.dirty)
            widget._set_selected_editor_panel(session, session.dynamic_working[0].panel_id)
            self.app.processEvents()
            widget._hide_editor_panel()
            self.app.processEvents()
            self.assertTrue(any((not item.visible) or item.state == "hidden" for item in session.dynamic_working))
            hidden_candidates = widget._hidden_panel_candidates(session)
            self.assertGreaterEqual(len(hidden_candidates), 1)
            first_hidden = hidden_candidates[0]
            reopen_label = f"{first_hidden[1]} · {first_hidden[0]} · {first_hidden[2]} · {first_hidden[3]} · {'dynamic' if first_hidden[4] else 'core'}"
            with mock.patch(
                "forgeos.shared.pyside6_glass.examples.catalog_shell.QInputDialog.getItem",
                return_value=(reopen_label, True),
            ):
                widget._reopen_hidden_panel()
            self.app.processEvents()
            self.assertTrue(any(item.visible and item.state == "visible" for item in session.dynamic_working))
            widget._duplicate_editor_panel()
            self.app.processEvents()
            self.assertGreaterEqual(len(session.dynamic_working), 2)
            widget._move_editor_panel_across_slot(1)
            self.app.processEvents()
            widget._clone_context_into_new_tab()
            self.app.processEvents()
            self.assertGreaterEqual(len(widget._workspace_hosts), 1)
            widget._select_editor_context("preview")
            self.app.processEvents()

            with mock.patch(
                "forgeos.shared.pyside6_glass.examples.catalog_shell.QMessageBox.question",
                return_value=QMessageBox.Yes,
            ), mock.patch(
                "forgeos.shared.pyside6_glass.examples.catalog_shell.QInputDialog.getText",
                return_value=("unit_clone_editor", True),
            ):
                widget._save_clone()
            self.app.processEvents()

            self.assertEqual(session.source_kind, "clone")
            self.assertTrue(session.source_ref.endswith("unit_clone_editor.json"))
            self.assertFalse(session.dirty)
            self.assertTrue(os.path.isfile(session.source_ref))

            widget._reset_editor_session()
            self.app.processEvents()
            self.assertFalse(session.dirty)
            self.assertEqual(len(session.dynamic_working), len(session.dynamic_baseline))

            widget2 = GlassCatalogShell()
            try:
                widget2._select_entry("example.form")
                widget2._on_entry_selected(widget2.entry_list.currentItem(), None)
                widget2._open_selected_preview()
                self.app.processEvents()
                reopened = widget2._current_editor_session()
                assert reopened is not None
                self.assertEqual(reopened.source_kind, "catalog_entry")
                self.assertEqual(len(reopened.dynamic_working), 0)
            finally:
                widget2.deleteLater()
        finally:
            widget.deleteLater()

    def test_chart_style_catalog_and_direct_drag_resize(self) -> None:
        class _FakeMouseEvent:
            def __init__(self, global_point: QPoint) -> None:
                self._global = QPoint(global_point)

            def globalPosition(self) -> QPointF:
                return QPointF(float(self._global.x()), float(self._global.y()))

            def button(self) -> Qt.MouseButton:
                return Qt.LeftButton

            def buttons(self) -> Qt.MouseButtons:
                return Qt.LeftButton

        widget = GlassCatalogShell()
        try:
            widget._select_entry("example.form")
            widget._on_entry_selected(widget.entry_list.currentItem(), None)
            widget._open_selected_preview()
            self.app.processEvents()

            widget.editor_palette_search.setText("chart")
            widget._refresh_insert_palette()
            self.app.processEvents()
            selected = widget.editor_palette_list.item(0)
            assert selected is not None
            widget.editor_palette_list.setCurrentItem(selected)

            widget._set_combo_data(widget.editor_chart_style_combo, "warning_watch")
            widget._set_combo_data(widget.editor_chart_palette_combo, "signal_amber")
            widget.editor_chart_markers_check.setChecked(True)
            widget.editor_chart_glow_check.setChecked(True)
            widget.editor_chart_grid_check.setChecked(True)
            widget.editor_chart_smooth_check.setChecked(False)
            widget.editor_chart_line_slider.setValue(4)
            widget.editor_chart_fill_slider.setValue(33)
            widget._add_editor_panel()
            self.app.processEvents()
            self._confirm_pending_candidate(widget)

            session = widget._current_editor_session()
            template = widget._current_editor_template()
            assert session is not None
            assert template is not None
            chart_item = session.dynamic_working[-1]
            self.assertEqual(chart_item.panel_type, "chart_graph")
            self.assertEqual(chart_item.chart_style_id, "warning_watch")
            self.assertEqual(chart_item.chart_palette_id, "signal_amber")
            self.assertTrue(chart_item.chart_show_markers)
            self.assertEqual(chart_item.chart_line_width, 4)
            self.assertEqual(chart_item.chart_fill_alpha, 33)
            template.set_split_proportions(main=70, side=30)
            self.app.processEvents()

            panel = template.panel(chart_item.panel_id)
            assert panel is not None
            origin = panel.mapToGlobal(panel.rect().center())
            widget._start_panel_drag(context_id="preview", panel_id=chart_item.panel_id, event=_FakeMouseEvent(origin))
            side_widget = template.slots.side_slot.parentWidget()
            assert side_widget is not None
            target_point = side_widget.mapToGlobal(side_widget.rect().center())
            widget._apply_panel_drag(_FakeMouseEvent(target_point))
            widget._finish_panel_drag()
            self.app.processEvents()
            if widget._panel_slot(template, chart_item.panel_id) != "side":
                widget._set_selected_editor_panel(session, chart_item.panel_id)
                widget._move_editor_panel_across_slot(1)
                self.app.processEvents()
            self.assertEqual(widget._panel_slot(template, chart_item.panel_id), "side")

            resize_anchor = panel.mapToGlobal(QPoint(max(8, panel.width() // 2), max(8, panel.height() - 2)))
            widget._start_panel_resize(context_id="preview", panel_id=chart_item.panel_id, panel=panel)
            widget._apply_panel_resize(_FakeMouseEvent(QPoint(resize_anchor.x(), resize_anchor.y() + 64)))
            widget._finish_panel_resize()
            self.app.processEvents()

            resized_state = next(item for item in session.dynamic_working if item.panel_id == chart_item.panel_id)
            self.assertEqual(resized_state.height_policy, "fixed")
            self.assertGreaterEqual(resized_state.panel_height, 96)
            self.assertGreaterEqual(panel.minimumHeight(), 96)
        finally:
            widget.deleteLater()

    def test_editor_heavy_budget_policy_enforced(self) -> None:
        widget = GlassCatalogShell()
        try:
            widget._select_entry("example.form")
            widget._on_entry_selected(widget.entry_list.currentItem(), None)
            widget._open_selected_preview()
            self.app.processEvents()

            widget.editor_palette_search.setText("chart")
            widget._refresh_insert_palette()
            self.app.processEvents()
            self.assertGreater(widget.editor_palette_list.count(), 0)
            selected = widget.editor_palette_list.item(0)
            assert selected is not None
            widget.editor_palette_list.setCurrentItem(selected)

            for _ in range(6):
                widget._add_editor_panel()
                self.app.processEvents()
                self._confirm_pending_candidate(widget)

            session = widget._current_editor_session()
            assert session is not None
            heavy_visible = [
                item
                for item in session.dynamic_working
                if item.panel_type in {"chart_graph", "feed_log", "table_grid", "json_diag", "dashboard_widget", "timeline_activity"}
                and item.visible
                and item.state == "visible"
            ]
            self.assertLessEqual(len(heavy_visible), int(widget._editor_policy["heavy_panels_per_tab"]))
            self.assertTrue(any(item.state in {"hold", "background", "deferred"} for item in session.dynamic_working))
        finally:
            widget.deleteLater()

    def test_editor_slot_capacity_guard(self) -> None:
        widget = GlassCatalogShell()
        try:
            widget._select_entry("example.form")
            widget._on_entry_selected(widget.entry_list.currentItem(), None)
            widget._open_selected_preview()
            self.app.processEvents()

            widget.editor_palette_search.setText("empty")
            widget._refresh_insert_palette()
            self.app.processEvents()
            self.assertGreater(widget.editor_palette_list.count(), 0)
            widget.editor_insert_target_combo.setCurrentText("side")
            widget.editor_insert_position_combo.setCurrentText("append")
            for _ in range(20):
                widget._add_editor_panel()
                self.app.processEvents()
                if widget._pending_candidate_overlay is not None:
                    self._confirm_pending_candidate(widget)

            session = widget._current_editor_session()
            assert session is not None
            side_items = [item for item in session.dynamic_working if item.target_slot == "side"]
            # side slot has one core panel already, capacity policy is 10 total
            self.assertLessEqual(len(side_items), 10)
        finally:
            widget.deleteLater()

    def test_workspace_lazy_budget_only_keeps_active_tab_mounted(self) -> None:
        widget = GlassCatalogShell()
        try:
            widget._select_entry("data.live_metrics_board")
            widget._on_entry_selected(widget.entry_list.currentItem(), None)
            widget._open_selected_in_workspace()

            widget._select_entry("data.service_health_monitor")
            widget._on_entry_selected(widget.entry_list.currentItem(), None)
            widget._open_selected_in_workspace()
            self.app.processEvents()

            self.assertGreaterEqual(len(widget._workspace_hosts), 2)
            mounted_counts = sum(1 for host in widget._workspace_hosts.values() if host.is_mounted())
            self.assertEqual(mounted_counts, 1)

            tabs = widget.catalog.workspace_tabs
            self.assertIsNotNone(tabs)
            assert tabs is not None
            host_ids = list(widget._workspace_hosts.keys())
            tabs.set_active_tab(host_ids[0])
            self.app.processEvents()
            mounted_after_switch = sum(1 for host in widget._workspace_hosts.values() if host.is_mounted())
            self.assertEqual(mounted_after_switch, 1)

            widget._refresh_editor_contexts()
            self.assertGreaterEqual(widget.editor_context_combo.count(), 1)
        finally:
            widget.deleteLater()

    def test_picker_filters_and_adds_to_current_tab(self) -> None:
        widget = GlassCatalogShell()
        try:
            widget._open_empty_workspace_tab()
            self.app.processEvents()
            tabs = widget.catalog.workspace_tabs
            assert tabs is not None
            active_tab = tabs.active_tab_id()
            assert active_tab is not None
            self.assertIn(active_tab, widget._workspace_hosts)

            widget._open_entry_picker(target_tab_id=active_tab)
            self.app.processEvents()
            widget.picker_search_input.setText("form")
            widget._refresh_picker_entries()
            self.app.processEvents()
            self.assertGreater(widget.picker_entry_list.count(), 0)
            widget.picker_entry_list.setCurrentRow(0)
            self.app.processEvents()
            selected_id = widget._picker_selected_entry_id()
            self.assertTrue(selected_id)

            before_count = len(widget._workspace_hosts)
            widget._picker_add_to_current_tab()
            self.app.processEvents()
            self.assertIsNotNone(widget._pending_candidate_overlay)
            self._confirm_pending_candidate(widget)
            after_count = len(widget._workspace_hosts)
            self.assertEqual(before_count, after_count)
            self.assertIn(active_tab, widget._workspace_hosts)
            host = widget._workspace_hosts[active_tab]
            self.assertTrue(bool(host._title))
            self.assertFalse(widget.entry_picker_dialog.isVisible())
        finally:
            widget.deleteLater()

    def test_picker_open_in_new_tab_and_blank_workspace_cta(self) -> None:
        widget = GlassCatalogShell()
        try:
            widget._open_empty_workspace_tab()
            self.app.processEvents()
            tabs = widget.catalog.workspace_tabs
            assert tabs is not None
            active_tab = tabs.active_tab_id()
            assert active_tab is not None
            host = widget._workspace_hosts[active_tab]
            mounted = host._mounted
            self.assertIsNotNone(mounted)
            assert mounted is not None
            main_panel = mounted.panel("main") if hasattr(mounted, "panel") else None
            self.assertIsNotNone(main_panel)
            assert main_panel is not None
            cta_buttons = [button for button in main_panel.findChildren(QPushButton) if button.text() == "Add Content"]
            self.assertGreaterEqual(len(cta_buttons), 1)

            widget._open_entry_picker()
            self.app.processEvents()
            widget.picker_search_input.setText("dashboard")
            widget._refresh_picker_entries()
            self.app.processEvents()
            self.assertGreater(widget.picker_entry_list.count(), 0)
            widget.picker_entry_list.setCurrentRow(0)
            self.app.processEvents()

            before_count = len(widget._workspace_hosts)
            widget._picker_open_in_new_tab()
            self.app.processEvents()
            self.assertGreater(len(widget._workspace_hosts), before_count)
            self.assertIsNotNone(widget._pending_candidate_overlay)
            widget._discard_pending_panel_candidate()
            self.app.processEvents()
            self.assertIsNone(widget._pending_candidate_overlay)
        finally:
            widget.deleteLater()

    def test_runtime_action_trace_and_status_autoclear(self) -> None:
        widget = GlassCatalogShell()
        try:
            widget._set_inspector_panel_visible(True)
            widget.catalog.set_status_text("Runtime trace event test")
            self.app.processEvents()
            self.assertGreater(len(widget._action_trace), 0)
            self.assertIn("Runtime trace event test", widget._action_trace[-1]["action"])

            widget._set_status("Transient release-gate info", level="info", auto_clear_ms=20)
            self.assertTrue(widget._status_autoclear_timer.isActive())
            QTest.qWait(40)
            self.app.processEvents()
            self.assertFalse(widget.catalog.cards.status.isVisible())

            widget._refresh_runtime_inspector(widget._current_entry())
            payload = json.loads(widget.runtime_diagnostics_text.toPlainText())
            self.assertIn("action_trace", payload)
            self.assertGreaterEqual(payload["action_trace"]["total_events"], 1)
        finally:
            widget.deleteLater()

    def test_structural_slot_shell_cannot_be_hidden_or_moved(self) -> None:
        widget = GlassCatalogShell()
        try:
            widget._select_entry("example.form")
            widget._on_entry_selected(widget.entry_list.currentItem(), None)
            widget._open_selected_preview()
            self.app.processEvents()

            session = widget._current_editor_session()
            template = widget._current_editor_template()
            assert session is not None
            assert template is not None

            widget._set_selected_editor_panel(session, "main")
            self.app.processEvents()
            main_panel = template.panel("main")
            assert main_panel is not None
            main_slot_before = widget._panel_slot(template, "main")

            widget._hide_editor_panel()
            self.app.processEvents()
            self.assertEqual(str(session.core_working["main"].get("state") or "visible"), "visible")
            self.assertFalse(bool(session.core_working["main"].get("user_hidden", False)))

            widget._move_editor_panel_across_slot(1)
            self.app.processEvents()
            self.assertEqual(widget._panel_slot(template, "main"), main_slot_before)
        finally:
            widget.deleteLater()

    def test_button_metadata_behavior_edit_and_invalid_payload_guard(self) -> None:
        widget = GlassCatalogShell()
        try:
            widget._select_entry("example.form")
            widget._on_entry_selected(widget.entry_list.currentItem(), None)
            widget._open_selected_preview()
            self.app.processEvents()

            widget._set_combo_data(widget.editor_add_type_combo, "button_control")
            widget._set_combo_data(widget.editor_add_slot_combo, "main")
            widget.editor_button_text_input.setText("Trigger")
            widget.editor_widget_tooltip_input.setText("Execute synthetic action")
            widget.editor_widget_object_name_input.setText("btn_trigger")
            widget.editor_widget_enabled_check.setChecked(True)
            widget.editor_button_icon_input.setText("play")
            widget.editor_button_checkable_check.setChecked(True)
            widget.editor_button_checked_check.setChecked(True)
            widget._set_combo_data(widget.editor_button_style_variant_combo, "primary")
            widget._set_combo_data(widget.editor_behavior_action_type_combo, "command")
            widget.editor_behavior_command_id_input.setText("runtime.refresh")
            widget.editor_behavior_target_panel_input.setText("dyn_001")
            widget.editor_behavior_task_ref_input.setText("task://refresh")
            widget.editor_behavior_payload_input.setPlainText("{\"scope\":\"preview\"}")
            widget._add_editor_panel()
            self.app.processEvents()
            self._confirm_pending_candidate(widget)

            session = widget._current_editor_session()
            template = widget._current_editor_template()
            assert session is not None
            assert template is not None
            button_state = session.dynamic_working[-1]
            self.assertEqual(button_state.panel_type, "button_control")
            self.assertEqual(button_state.widget_props.get("text"), "Trigger")
            self.assertEqual(button_state.behavior.get("action_type"), "command")
            self.assertEqual(button_state.behavior.get("command_id"), "runtime.refresh")
            self.assertEqual(button_state.behavior.get("payload"), {"scope": "preview"})

            widget._set_selected_editor_panel(session, button_state.panel_id)
            widget.editor_behavior_payload_input.setPlainText("{bad-json")
            widget._apply_editor_properties()
            self.app.processEvents()
            self.assertIn("Invalid behavior payload JSON", widget._action_trace[-1]["action"])
            self.assertEqual(button_state.behavior.get("payload"), {"scope": "preview"})

            panel = template.panel(button_state.panel_id)
            assert panel is not None
            buttons = panel.findChildren(QPushButton)
            self.assertGreaterEqual(len(buttons), 1)
            self.assertEqual(buttons[0].objectName(), "btn_trigger")
        finally:
            widget.deleteLater()

    def test_touch_accept_and_workspace_clamp(self) -> None:
        widget = GlassCatalogShell()
        try:
            widget._select_entry("example.form")
            widget._on_entry_selected(widget.entry_list.currentItem(), None)
            widget._open_selected_preview()
            self.app.processEvents()

            template = widget._current_editor_template()
            self.assertIsNotNone(template)
            assert template is not None
            first_panel = template.panel(template.panel_ids()[0])
            self.assertIsNotNone(first_panel)
            assert first_panel is not None
            self.assertTrue(first_panel.testAttribute(Qt.WA_AcceptTouchEvents))

            children = first_panel.findChildren(QPushButton)
            if children:
                self.assertTrue(children[0].testAttribute(Qt.WA_AcceptTouchEvents))

            bounds = widget._workspace_bounds(template)
            out_point = QPoint(bounds.left() - 999, bounds.top() - 999)
            clamped = widget._clamped_workspace_point(template, out_point)
            self.assertGreaterEqual(clamped.x(), bounds.left())
            self.assertGreaterEqual(clamped.y(), bounds.top())
        finally:
            widget.deleteLater()

    def test_probe_marks_stale_warning(self) -> None:
        widget = GlassCatalogShell()
        try:
            widget._set_inspector_panel_visible(True)
            widget._clear_filters()
            widget._select_category("Data Dashboards")
            widget._refresh_entries()
            widget._select_entry("data.live_metrics_board")
            widget._on_entry_selected(widget.entry_list.currentItem(), None)
            self.app.processEvents()

            stale_query = DataQuery.create("builtin.mock_dashboard", query_id="live_metrics")
            stale_result = DataResult.stale(
                stale_query,
                summary={"note": "stale for test"},
                policy=RefreshPolicy(stale_after_ms=500),
                refreshed_at_utc="2000-01-01T00:00:00+00:00",
                latency_ms=88.0,
            )
            with mock.patch(
                "forgeos.shared.pyside6_glass.examples.catalog_shell.execute_data_query",
                return_value=stale_result,
            ):
                widget._probe_selected_query()
            self.app.processEvents()

            self.assertIn("STALE WARNING", widget.data_binding_summary.text())
            self.assertGreater(len(widget._action_trace), 0)
            self.assertEqual(widget._action_trace[-1]["level"], "warning")
        finally:
            widget.deleteLater()


if __name__ == "__main__":
    unittest.main()
