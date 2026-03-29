from __future__ import annotations

from dataclasses import dataclass

from forge_kernel import ContractRuntime

from .config_policy import ConfigPolicyCapability
from .diagnostics import DiagnosticsCapability
from .export_artifacts import ExportArtifactsCapability
from .history_runs import HistoryRunsCapability
from .process_execution import ProcessExecutionCapability


@dataclass
class ForgeCommonsRuntime:
    config_policy: ConfigPolicyCapability
    diagnostics: DiagnosticsCapability
    process_execution: ProcessExecutionCapability
    history_runs: HistoryRunsCapability
    export_artifacts: ExportArtifactsCapability

    def dispose(self) -> None:
        self.export_artifacts.dispose()
        self.history_runs.dispose()
        self.process_execution.dispose()
        self.diagnostics.dispose()
        self.config_policy.dispose()


class ForgeCommonsBootstrap:
    """Bootstrap for phase-3 commons capability runtime."""

    @staticmethod
    def start(contracts: ContractRuntime) -> ForgeCommonsRuntime:
        config_policy = ConfigPolicyCapability()
        diagnostics = DiagnosticsCapability()
        process_execution = ProcessExecutionCapability(contracts=contracts)
        history_runs = HistoryRunsCapability(contracts=contracts)
        export_artifacts = ExportArtifactsCapability()

        config_policy.activate()
        diagnostics.activate()
        process_execution.activate()
        history_runs.activate()
        export_artifacts.activate()

        return ForgeCommonsRuntime(
            config_policy=config_policy,
            diagnostics=diagnostics,
            process_execution=process_execution,
            history_runs=history_runs,
            export_artifacts=export_artifacts,
        )
