from __future__ import annotations

from typing import Any, Dict

from .adapters import CloudflareAdapter, OriginAdapter, RepoAnalyzerAdapter
from .alerts import AlertBus
from .health import build_engine_status, render_human_summary
from .paths import GuardianPaths, build_paths
from .policy import GuardianPolicy
from .preflight import run_preflight
from .scheduler import SchedulerManager
from .state_store import StateStore, utc_now_iso


class EngineGuardianOrchestrator:
    def __init__(self, paths: GuardianPaths | None = None, policy: GuardianPolicy | None = None) -> None:
        self.paths = paths or build_paths()
        self.policy = policy or GuardianPolicy()
        self.state_store = StateStore(self.paths, self.policy)
        self.alerts = AlertBus(self.state_store)
        self.origin = OriginAdapter(self.paths, self.policy, self.state_store)
        self.cloudflare = CloudflareAdapter(self.paths, self.policy, self.state_store)
        self.repo_analyzer = RepoAnalyzerAdapter(self.paths, self.policy, self.state_store)
        self.scheduler = SchedulerManager(self.paths, self.policy, self.state_store)

    def bootstrap(self) -> Dict[str, Any]:
        preflight = run_preflight(self.paths, self.state_store)
        self.state_store.seed_runtime_files()
        payload = {
            "timestamp_utc": utc_now_iso(),
            "status": "ok" if preflight.get("ok") else "degraded",
            "preflight": preflight,
            "runtime_root": str(self.paths.runtime_root),
            "state_paths": {
                "resolved_tools": str(self.state_store.resolved_tools_path),
                "boot_state": str(self.state_store.boot_state_path),
                "engine_status_latest": str(self.state_store.engine_status_path),
                "repo_analyzer_status": str(self.state_store.repo_analyzer_status_path),
                "last_actions": str(self.state_store.last_actions_path),
            },
        }
        self.alerts.emit("INFO", "Bootstrap executed.", {"status": payload["status"]})
        self.state_store.write_json(self.paths.reports_dir / "bootstrap_latest.json", payload)
        return payload

    def cycle(self, reason: str, repair: bool = False) -> Dict[str, Any]:
        canonical_reason = reason if reason in {"boot", "pulse", "manual"} else "manual"
        preflight = run_preflight(self.paths, self.state_store)
        if canonical_reason == "boot":
            boot_state = self.state_store.register_boot_attempt(reason=canonical_reason)
            if int(boot_state.get("attempt_count", 0)) > self.policy.max_boot_attempts_per_window:
                payload = {
                    "timestamp_utc": utc_now_iso(),
                    "status": "blocked",
                    "reason": canonical_reason,
                    "boot_state": boot_state,
                    "message": "Boot attempts exhausted for current window.",
                    "engine_public_healthy": False,
                }
                self.alerts.emit("ERROR", payload["message"], {"boot_state": boot_state})
                self.state_store.write_json(self.state_store.engine_status_path, payload)
                self.alerts.snapshot("engine_status", payload)
                return payload
        with self.state_store.locked(canonical_reason):
            origin_status = self.origin.ensure(repair=repair or canonical_reason == "boot")
            cf = self.cloudflare.ensure(repair=repair or canonical_reason == "boot")
            public_status = cf["public"]
            escalation_required = (
                bool(origin_status.get("healthy"))
                and bool(cf["tunnel"].get("healthy"))
                and not bool(public_status.get("healthy"))
            )
            escalation = {
                "required": escalation_required,
                "reason": (
                    "origin_and_tunnel_healthy_but_public_endpoint_still_failing"
                    if escalation_required
                    else None
                ),
            }
            if escalation_required:
                self.alerts.emit(
                    "ERROR",
                    "Public endpoint is still failing even though origin and tunnel look healthy.",
                    {"public_endpoint": public_status},
                )
            engine_status = build_engine_status(
                reason=canonical_reason,
                preflight=preflight,
                origin=origin_status,
                cloudflare_service=cf["service"],
                tunnel=cf["tunnel"],
                public_endpoint=public_status,
                escalation=escalation,
            )
            engine_status["timestamp_utc"] = utc_now_iso()
            engine_status["human_summary"] = render_human_summary(engine_status)
            self.state_store.write_json(self.state_store.engine_status_path, engine_status)
            self.alerts.snapshot("engine_status", engine_status)
            self.alerts.emit(
                "INFO",
                "Cycle completed.",
                {"reason": canonical_reason, "healthy": engine_status["engine_public_healthy"]},
            )
            return engine_status

    def validate(self) -> Dict[str, Any]:
        payload = self.cycle(reason="manual", repair=False)
        payload["mode"] = "validate"
        return payload

    def heal(self) -> Dict[str, Any]:
        payload = self.cycle(reason="manual", repair=True)
        payload["mode"] = "heal"
        return payload

    def status(self) -> Dict[str, Any]:
        latest = self.state_store.read_json(self.state_store.engine_status_path, {})
        if latest:
            latest["scheduler"] = self.scheduler.status()
            return latest
        return self.bootstrap()

    def install_scheduler(self, *, apply: bool = True) -> Dict[str, Any]:
        self.bootstrap()
        return self.scheduler.install_scheduler(apply=apply)

    def disable_legacy_cloudflare_tasks(self, *, apply: bool = False) -> Dict[str, Any]:
        self.bootstrap()
        return self.scheduler.export_and_disable_legacy_cloudflare_tasks(apply=apply)
