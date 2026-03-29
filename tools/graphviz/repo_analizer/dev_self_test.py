#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QEventLoop
from PySide6.QtWidgets import QApplication

SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

# Default self-test behavior avoids implicit auto-index from persisted settings.
os.environ.setdefault('HITECH_QT_SKIP_AUTO_INDEX', '1')

from app.gui_qt.main_window import RepoAnalyzerMainWindow


def _process_events_until(
    app: QApplication,
    predicate: Callable[[], bool],
    *,
    timeout_seconds: float,
) -> bool:
    start = time.monotonic()
    while True:
        app.processEvents(QEventLoop.AllEvents, 50)
        if predicate():
            return True
        if (time.monotonic() - start) >= timeout_seconds:
            return bool(predicate())
        time.sleep(0.01)


def _to_bool(value: object) -> bool:
    return bool(value)


def _contribution_id_from_action(action: object, expected_kind: str) -> str:
    if action is None or not hasattr(action, 'property'):
        return ''

    raw_id = action.property('pluginContributionId')
    raw_kind = action.property('pluginContributionKind')
    contribution_id = str(raw_id or '').strip()
    kind = str(raw_kind or '').strip().lower()
    if not contribution_id:
        return ''
    if kind and kind != expected_kind:
        return ''
    return contribution_id


def _collect_expected_ui_contributions(window: RepoAnalyzerMainWindow) -> dict[str, set[str]]:
    registry = window.service_container.get('ui_contribution_registry')
    if registry is None:
        return {'toolbar': set(), 'menu': set()}

    expected_toolbar_ids = {
        contribution.contribution_id
        for contribution in registry.get_toolbar_contributions()
        if str(contribution.contribution_id).strip()
    }
    expected_menu_ids = {
        contribution.contribution_id
        for contribution in registry.get_menu_contributions()
        if str(contribution.contribution_id).strip()
    }
    return {'toolbar': expected_toolbar_ids, 'menu': expected_menu_ids}


def _collect_attached_toolbar_ids(window: RepoAnalyzerMainWindow) -> set[str]:
    attached: set[str] = set()
    for toolbar_name in ('workspace_toolbar', 'command_toolbar'):
        toolbar = getattr(window, toolbar_name, None)
        if toolbar is None or not hasattr(toolbar, 'actions'):
            continue
        for action in toolbar.actions():
            contribution_id = _contribution_id_from_action(action, expected_kind='toolbar')
            if contribution_id:
                attached.add(contribution_id)
    return attached


def _iter_menu_actions(menu) -> list[object]:
    actions: list[object] = []
    if menu is None or not hasattr(menu, 'actions'):
        return actions

    for action in menu.actions():
        actions.append(action)
        child_menu = action.menu() if hasattr(action, 'menu') else None
        if child_menu is not None:
            actions.extend(_iter_menu_actions(child_menu))
    return actions


def _collect_attached_menu_ids(window: RepoAnalyzerMainWindow) -> set[str]:
    attached: set[str] = set()
    menu_bar = window.menuBar() if hasattr(window, 'menuBar') else None
    if menu_bar is None or not hasattr(menu_bar, 'actions'):
        return attached

    for root_action in menu_bar.actions():
        root_menu = root_action.menu() if hasattr(root_action, 'menu') else None
        if root_menu is None:
            continue
        for action in _iter_menu_actions(root_menu):
            contribution_id = _contribution_id_from_action(action, expected_kind='menu')
            if not contribution_id:
                continue
            parent = action.parent()
            if parent is not None and hasattr(parent, 'actions') and action in parent.actions():
                attached.add(contribution_id)
    return attached


def _run(
    repo: Path,
    query: str,
    timeout_seconds: float,
    debug_mode: bool,
    failure_mode: str,
) -> dict[str, object]:
    app = QApplication.instance()
    owns_app = app is None
    if app is None:
        app = QApplication(sys.argv)

    if app is None:
        raise RuntimeError('QApplication could not be created')

    window = RepoAnalyzerMainWindow()
    window.hide()

    if debug_mode:
        window.runtime_diagnostics.set_debug_mode(True)

    # If something started indexing before explicit self-test flow, wait it out first.
    if window._index_thread is not None:
        _process_events_until(
            app,
            lambda: window._index_thread is None,
            timeout_seconds=timeout_seconds,
        )

    window.repo_combo.setCurrentText(str(repo))
    needs_index = (
        window.index_data.get('root') != str(repo)
        or not _to_bool(window.index_data.get('files'))
    )
    if needs_index and window._index_thread is None:
        window.start_indexing(auto=True)

    index_ready = _process_events_until(
        app,
        lambda: window._index_thread is None and _to_bool(window.index_data.get('files')),
        timeout_seconds=timeout_seconds,
    )

    search_completed = False
    if index_ready:
        window.search_box.setText(query)
        window.start_search()
        search_completed = _process_events_until(
            app,
            lambda: window.search_controller._search_thread is None,
            timeout_seconds=timeout_seconds,
        )

    # Exercise idempotent explicit subtree reprocessing path used by future feature work.
    try:
        central = window.centralWidget()
        if central is not None:
            window.process_visual_subtree(central, reason='dev-self-test-pass-1', force=False)
            window.process_visual_subtree(central, reason='dev-self-test-pass-2', force=False)
    except Exception:
        pass

    # Exercise contribution idempotency path (second apply should skip existing IDs).
    try:
        window.shell_contribution_bridge.apply()
    except Exception:
        pass

    diagnostics_snapshot = window.get_developer_diagnostics_snapshot()
    startup_summary = diagnostics_snapshot.get('startup_summary', {})
    runtime_state = startup_summary.get('runtime_state', {}) if isinstance(startup_summary, dict) else {}
    plugin_report = diagnostics_snapshot.get('plugin_report', {})
    integration_report = diagnostics_snapshot.get('integration_report', {})
    expected_contributions = _collect_expected_ui_contributions(window)
    expected_toolbar_ids = expected_contributions['toolbar']
    expected_menu_ids = expected_contributions['menu']
    attached_toolbar_ids = _collect_attached_toolbar_ids(window)
    attached_menu_ids = _collect_attached_menu_ids(window)

    normalized_failure_mode = (failure_mode or 'off').strip().lower()
    checks = {
        'startup_ui_ready': bool(runtime_state.get('central_widget_ready')) and bool(runtime_state.get('status_bar_ready')),
        'index_ready': bool(index_ready),
        'search_flow_completed': bool(search_completed),
    }
    if normalized_failure_mode == 'off':
        checks.update(
            {
                'plugins_loaded': int(plugin_report.get('loaded_plugins_count', 0)) > 0,
                'plugin_docks_attached': int(runtime_state.get('plugin_dock_count', 0)) > 0,
                'integration_failures_zero': int(integration_report.get('failed_total', 0)) == 0,
                'plugin_toolbar_contributions_present': len(expected_toolbar_ids) > 0,
                'plugin_menu_contributions_present': len(expected_menu_ids) > 0,
                'plugin_toolbar_actions_attached': expected_toolbar_ids.issubset(attached_toolbar_ids),
                'plugin_menu_actions_attached': expected_menu_ids.issubset(attached_menu_ids),
            }
        )
        expected_failure_detected = True
    elif normalized_failure_mode == 'load':
        expected_failure_detected = int(plugin_report.get('load_failures_count', 0)) > 0
    elif normalized_failure_mode == 'init':
        expected_failure_detected = int(plugin_report.get('init_failures_count', 0)) > 0
    elif normalized_failure_mode == 'integration':
        expected_failure_detected = int(integration_report.get('failed_total', 0)) > 0
    else:
        expected_failure_detected = False

    if normalized_failure_mode != 'off':
        checks['expected_failure_detected'] = expected_failure_detected

    checks_passed = all(checks.values())

    report = {
        'ok': checks_passed,
        'repo': str(repo),
        'query': query,
        'debug_mode': bool(debug_mode),
        'failure_mode': normalized_failure_mode,
        'checks': checks,
        'startup_summary': startup_summary,
        'plugin_report_counts': {
            'loaded': int(plugin_report.get('loaded_plugins_count', 0)),
            'initialized': int(plugin_report.get('initialized_plugins_count', 0)),
            'load_failures': int(plugin_report.get('load_failures_count', 0)),
            'init_failures': int(plugin_report.get('init_failures_count', 0)),
            'contract_warnings': int(plugin_report.get('contract_warnings_count', 0)),
        },
        'integration_report_counts': {
            'applied': int(integration_report.get('applied_total', 0)),
            'failed': int(integration_report.get('failed_total', 0)),
            'skipped': int(integration_report.get('skipped_total', 0)),
        },
        'plugin_ui_attachment': {
            'expected_toolbar_contributions': len(expected_toolbar_ids),
            'attached_toolbar_actions': len(attached_toolbar_ids),
            'missing_toolbar_contribution_ids': sorted(
                expected_toolbar_ids.difference(attached_toolbar_ids)
            ),
            'expected_menu_contributions': len(expected_menu_ids),
            'attached_menu_actions': len(attached_menu_ids),
            'missing_menu_contribution_ids': sorted(
                expected_menu_ids.difference(attached_menu_ids)
            ),
        },
        'result_counts': {
            'indexed_files': len(window.index_data.get('files', {})),
            'search_results': len(getattr(window, 'search_results', [])),
            'dock_count': int(runtime_state.get('dock_count', 0)),
            'plugin_dock_count': int(runtime_state.get('plugin_dock_count', 0)),
            'warnings': len(diagnostics_snapshot.get('warnings', [])),
        },
    }

    window.close()
    app.processEvents(QEventLoop.AllEvents, 50)
    if owns_app:
        app.quit()
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Lightweight developer self-test for Repo Analyzer Qt shell.',
    )
    parser.add_argument(
        '--repo',
        default=str(SCRIPT_ROOT),
        help='Repository path to index during self-test.',
    )
    parser.add_argument(
        '--query',
        default='plugin',
        help='Search query to execute after indexing.',
    )
    parser.add_argument(
        '--timeout-seconds',
        type=float,
        default=120.0,
        help='Timeout per async phase (indexing and search).',
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable runtime trace mode for this run.',
    )
    parser.add_argument(
        '--show',
        action='store_true',
        help='Run with visible UI (default is offscreen for automation).',
    )
    parser.add_argument(
        '--failure-mode',
        choices=('off', 'load', 'init', 'integration'),
        default='off',
        help='Enable deterministic failure injection mode for plugin diagnostics.',
    )
    parser.add_argument(
        '--allow-auto-index',
        action='store_true',
        help='Allow implicit auto-index from persisted app settings.',
    )
    args = parser.parse_args()

    if not args.show:
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    if args.allow_auto_index:
        os.environ['HITECH_QT_SKIP_AUTO_INDEX'] = '0'
    else:
        os.environ['HITECH_QT_SKIP_AUTO_INDEX'] = '1'
    os.environ['HITECH_QT_FAILURE_INJECTION_MODE'] = str(args.failure_mode)
    if args.debug:
        os.environ['HITECH_QT_DEV_TRACE'] = '1'

    repo = Path(args.repo).resolve()
    if not repo.exists() or not repo.is_dir():
        print(json.dumps({'ok': False, 'error': f'invalid repo path: {repo}'}, ensure_ascii=False))
        return 2

    try:
        report = _run(
            repo=repo,
            query=str(args.query),
            timeout_seconds=float(args.timeout_seconds),
            debug_mode=bool(args.debug),
            failure_mode=str(args.failure_mode),
        )
    except Exception as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 1

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if bool(report.get('ok')) else 1


if __name__ == '__main__':
    raise SystemExit(main())
