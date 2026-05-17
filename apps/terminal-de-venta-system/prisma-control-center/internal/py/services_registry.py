from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from config_loader import detect_lan_ip, load_services_config, render_placeholders


@dataclass(frozen=True)
class ServiceDef:
    id: str
    name: str
    port: int
    local_url: str
    lan_url: str
    health_path: str
    alternate_health_paths: tuple[str, ...]
    content_probe: dict[str, Any]
    start_command: str
    cwd: str
    required_for_local: bool
    required_for_cloudflare: bool
    criticality: str
    product_role: str
    public_host: str
    notes: str = ""

    @property
    def has_start_command(self) -> bool:
        return bool(self.start_command and self.start_command != "TO_DEFINE")


def load_services() -> list[ServiceDef]:
    lan_ip = detect_lan_ip()
    payload = render_placeholders(load_services_config(), lan_ip)
    services = []
    for raw in payload.get("services", []):
        services.append(
            ServiceDef(
                id=str(raw["id"]),
                name=str(raw["name"]),
                port=int(raw["port"]),
                local_url=str(raw["localUrl"]),
                lan_url=str(raw.get("lanUrl", "")),
                health_path=str(raw.get("healthPath", "/")),
                alternate_health_paths=tuple(raw.get("alternateHealthPaths", [])),
                content_probe=dict(raw.get("contentProbe", {})),
                start_command=str(raw.get("startCommand", "TO_DEFINE")),
                cwd=str(raw.get("cwd", "")),
                required_for_local=bool(raw.get("requiredForLocal", False)),
                required_for_cloudflare=bool(raw.get("requiredForCloudflare", False)),
                criticality=str(raw.get("criticality", "medium")),
                product_role=str(raw.get("productRole", "admin-health")),
                public_host=str(raw.get("publicHost", "")),
                notes=str(raw.get("notes", "")),
            )
        )
    return services


def service_by_port(port: int) -> ServiceDef | None:
    for service in load_services():
        if service.port == port:
            return service
    return None


def as_report_dict(service: ServiceDef) -> dict[str, Any]:
    return {
        "id": service.id,
        "name": service.name,
        "port": service.port,
        "localUrl": service.local_url,
        "lanUrl": service.lan_url,
        "healthPath": service.health_path,
        "alternateHealthPaths": list(service.alternate_health_paths),
        "contentProbe": service.content_probe,
        "startCommand": service.start_command,
        "cwd": service.cwd,
        "requiredForLocal": service.required_for_local,
        "requiredForCloudflare": service.required_for_cloudflare,
        "criticality": service.criticality,
        "productRole": service.product_role,
        "publicHost": service.public_host,
        "notes": service.notes,
    }
