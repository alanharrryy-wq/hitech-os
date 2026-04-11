from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING

from .menu_shell import ShellMenuBuilder

if TYPE_CHECKING:
    from ..main_window import RepoAnalyzerMainWindow


@dataclass(slots=True)
class ContributionIntegrationEvent:
    kind: str
    contribution_id: str
    status: str
    message: str = ''


class ShellContributionBridge:
    """Attach plugin UI contributions onto stable shell extension points."""

    def __init__(
        self,
        main_window: RepoAnalyzerMainWindow,
        menu_builder: ShellMenuBuilder,
    ) -> None:
        self.main = main_window
        self.menu_builder = menu_builder
        self._applied_dock_ids: set[str] = set()
        self._applied_toolbar_ids: set[str] = set()
        self._applied_menu_ids: set[str] = set()
        self._integration_events: list[ContributionIntegrationEvent] = []

    def apply(self) -> None:
        registry = self.main.service_container.get("ui_contribution_registry")
        if registry is None:
            self._record_event(
                kind='registry',
                contribution_id='ui_contribution_registry',
                status='failed',
                message='service not available',
            )
            return

        for contribution in registry.get_dock_contributions():
            contribution_id = contribution.contribution_id
            if contribution_id in self._applied_dock_ids:
                self._record_event(
                    kind='dock',
                    contribution_id=contribution_id,
                    status='skipped',
                    message='already applied',
                )
                continue
            try:
                self.main.dock_manager.add_plugin_dock(contribution, self.main._skin_tokens)
            except Exception as exc:
                self._log_apply_failure("dock", contribution_id, exc)
                self._record_event(
                    kind='dock',
                    contribution_id=contribution_id,
                    status='failed',
                    message=str(exc),
                )
                continue
            self._applied_dock_ids.add(contribution_id)
            self._record_event(
                kind='dock',
                contribution_id=contribution_id,
                status='applied',
            )

        for contribution in registry.get_toolbar_contributions():
            contribution_id = contribution.contribution_id
            if contribution_id in self._applied_toolbar_ids:
                self._record_event(
                    kind='toolbar',
                    contribution_id=contribution_id,
                    status='skipped',
                    message='already applied',
                )
                continue
            try:
                self.main.toolbar_controller.add_plugin_action(contribution)
            except Exception as exc:
                self._log_apply_failure("toolbar", contribution_id, exc)
                self._record_event(
                    kind='toolbar',
                    contribution_id=contribution_id,
                    status='failed',
                    message=str(exc),
                )
                continue
            self._applied_toolbar_ids.add(contribution_id)
            self._record_event(
                kind='toolbar',
                contribution_id=contribution_id,
                status='applied',
            )

        for contribution in registry.get_menu_contributions():
            contribution_id = contribution.contribution_id
            if contribution_id in self._applied_menu_ids:
                self._record_event(
                    kind='menu',
                    contribution_id=contribution_id,
                    status='skipped',
                    message='already applied',
                )
                continue
            try:
                self.menu_builder.add_plugin_menu_action(contribution)
            except Exception as exc:
                self._log_apply_failure("menu", contribution_id, exc)
                self._record_event(
                    kind='menu',
                    contribution_id=contribution_id,
                    status='failed',
                    message=str(exc),
                )
                continue
            self._applied_menu_ids.add(contribution_id)
            self._record_event(
                kind='menu',
                contribution_id=contribution_id,
                status='applied',
            )

        self.main.menuBar().update()

    def get_integration_report(self) -> dict[str, object]:
        events = [asdict(event) for event in self._integration_events]
        applied_total = sum(
            1 for event in self._integration_events if event.status == 'applied'
        )
        failed_total = sum(
            1 for event in self._integration_events if event.status == 'failed'
        )
        skipped_total = sum(
            1 for event in self._integration_events if event.status == 'skipped'
        )
        return {
            'applied_total': applied_total,
            'failed_total': failed_total,
            'skipped_total': skipped_total,
            'events': events,
        }

    def _record_event(
        self,
        *,
        kind: str,
        contribution_id: str,
        status: str,
        message: str = '',
    ) -> None:
        self._integration_events.append(
            ContributionIntegrationEvent(
                kind=kind,
                contribution_id=contribution_id,
                status=status,
                message=message,
            )
        )
        diagnostics = getattr(self.main, 'runtime_diagnostics', None)
        if diagnostics is not None and hasattr(diagnostics, 'trace'):
            diagnostics.trace(
                'contribution-bridge',
                f'{kind}:{status}',
                contribution_id=contribution_id,
                detail=message,
            )
        if status == 'failed' and diagnostics is not None and hasattr(diagnostics, 'warning'):
            diagnostics.warning(
                'contribution-bridge',
                f'{kind} integration failed',
                contribution_id=contribution_id,
                detail=message,
            )

    def _log_apply_failure(self, kind: str, contribution_id: str, error: Exception) -> None:
        message = (
            f"No se pudo aplicar contribución plugin ({kind}) "
            f"'{contribution_id}': {error}"
        )
        logger = getattr(self.main, "log", None)
        if callable(logger):
            try:
                logger(message)
                return
            except Exception:
                pass
        print(message)
