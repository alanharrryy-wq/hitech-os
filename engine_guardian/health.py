from __future__ import annotations

import time
import urllib.error
import urllib.request
from typing import Any, Dict



def probe_url(url: str, timeout_seconds: int) -> Dict[str, Any]:
    started = time.monotonic()
    request = urllib.request.Request(url, headers={'User-Agent': 'engine_guardian/3'})
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            status_code = getattr(response, 'status', None) or response.getcode()
            latency_ms = round((time.monotonic() - started) * 1000, 2)
            return {
                'url': url,
                'status_code': status_code,
                'healthy': 200 <= int(status_code) < 400,
                'error': None,
                'latency_ms': latency_ms,
            }
    except urllib.error.HTTPError as exc:
        latency_ms = round((time.monotonic() - started) * 1000, 2)
        return {
            'url': url,
            'status_code': int(exc.code),
            'healthy': 200 <= int(exc.code) < 400,
            'error': str(exc),
            'latency_ms': latency_ms,
        }
    except Exception as exc:
        latency_ms = round((time.monotonic() - started) * 1000, 2)
        return {
            'url': url,
            'status_code': None,
            'healthy': False,
            'error': str(exc),
            'latency_ms': latency_ms,
        }



def build_engine_status(
    *,
    reason: str,
    preflight: Dict[str, Any],
    origin: Dict[str, Any],
    cloudflare_service: Dict[str, Any],
    tunnel: Dict[str, Any],
    public_endpoint: Dict[str, Any],
    escalation: Dict[str, Any],
) -> Dict[str, Any]:
    engine_public_healthy = bool(public_endpoint.get('healthy'))
    preflight_ok = bool(preflight.get('ok'))
    origin_ok = bool(origin.get('healthy'))
    service_ok = bool(cloudflare_service.get('healthy'))
    tunnel_ok = bool(tunnel.get('healthy'))
    public_ok = bool(public_endpoint.get('healthy'))

    if engine_public_healthy and preflight_ok:
        status = 'healthy'
    elif any([origin_ok, service_ok, tunnel_ok, public_ok, preflight_ok]):
        status = 'degraded'
    else:
        status = 'unhealthy'

    return {
        'status': status,
        'reason': reason,
        'engine_public_healthy': engine_public_healthy,
        'preflight_ok': preflight_ok,
        'summary': {
            'origin_ok': origin_ok,
            'service_ok': service_ok,
            'tunnel_ok': tunnel_ok,
            'public_ok': public_ok,
            'public_truth_model': 'public_2xx_or_3xx_required',
        },
        'origin': origin,
        'cloudflare_service': cloudflare_service,
        'tunnel': tunnel,
        'public_endpoint': public_endpoint,
        'preflight': preflight,
        'escalation': escalation,
    }



def render_human_summary(status_payload: Dict[str, Any]) -> str:
    summary = status_payload.get('summary', {})
    truth = 'healthy' if status_payload.get('engine_public_healthy') else 'degraded'
    return (
        'engine=' + truth + '; '
        + f"origin={summary.get('origin_ok')}; "
        + f"service={summary.get('service_ok')}; "
        + f"tunnel={summary.get('tunnel_ok')}; "
        + f"public={summary.get('public_ok')}"
    )
