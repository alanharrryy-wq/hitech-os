# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any


def normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or "").strip().casefold())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def normalize_email(value: Any) -> str:
    return str(value or "").strip().casefold()


def normalize_phone(value: Any) -> str:
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def load_customer_catalog_config(path: Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("catalogs"), dict):
        raise RuntimeError("CUSTOMER_REGISTRATION_CATALOG_INVALID")
    seen_catalogs: set[str] = set()
    for code, catalog in payload["catalogs"].items():
        if code in seen_catalogs or not re.fullmatch(r"[a-z0-9_]+", str(code)):
            raise RuntimeError(f"CUSTOMER_REGISTRATION_CATALOG_CODE_INVALID:{code}")
        seen_catalogs.add(code)
        if not isinstance(catalog, dict) or not isinstance(catalog.get("options"), list):
            raise RuntimeError(f"CUSTOMER_REGISTRATION_CATALOG_OPTIONS_INVALID:{code}")
        seen_options: set[str] = set()
        seen_labels: set[str] = set()
        for item in catalog["options"]:
            option_code = str(item.get("code") or "").strip()
            label = str(item.get("label") or "").strip()
            if not option_code or option_code in seen_options:
                raise RuntimeError(f"CUSTOMER_REGISTRATION_OPTION_DUPLICATE:{code}:{option_code}")
            label_key = normalize_text(label)
            if not label or label_key in seen_labels:
                raise RuntimeError(f"CUSTOMER_REGISTRATION_LABEL_DUPLICATE:{code}:{label}")
            seen_options.add(option_code)
            seen_labels.add(label_key)
    return payload


def catalog_tuples(config: dict[str, Any]) -> dict[str, tuple[str, bool, list[tuple[str, str, dict[str, Any]]]]]:
    out: dict[str, tuple[str, bool, list[tuple[str, str, dict[str, Any]]]]] = {}
    for code, cat in config.get("catalogs", {}).items():
        options = [(str(item["code"]), str(item["label"]), dict(item.get("metadata") or {})) for item in cat.get("options", [])]
        out[code] = (str(cat.get("label") or code), bool(cat.get("allowOther")), options)
    return out


def customer_fingerprint(payload: dict[str, Any]) -> str:
    name = normalize_text(payload.get("displayName"))
    email = normalize_email(payload.get("email"))
    phone = normalize_phone(payload.get("phone"))
    state = normalize_text(payload.get("state"))
    city = normalize_text(payload.get("city"))
    source = f"v2|{name}|{email}|{phone}" if (email or phone) else f"v2|{name}|{state}|{city}"
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def _option_map(catalogs: dict[str, Any], code: str) -> dict[str, dict[str, Any]]:
    return {str(item.get("code")): item for item in (catalogs.get(code, {}).get("options") or []) if item.get("active") is not False}


def _require_option(catalogs: dict[str, Any], catalog: str, value: Any, *, required: bool) -> str:
    raw = str(value or "").strip()
    if not raw:
        if required:
            raise ValueError(f"CUSTOMER_FIELD_REQUIRED:{catalog}")
        return ""
    if raw not in _option_map(catalogs, catalog):
        raise ValueError(f"CUSTOMER_CATALOG_VALUE_INVALID:{catalog}:{raw}")
    return raw


def validate_customer_payload(catalogs: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    name = str(payload.get("displayName") or "").strip()
    if len(name) < 2:
        raise ValueError("CUSTOMER_DISPLAY_NAME_REQUIRED")
    if len(name) > 90:
        raise ValueError("CUSTOMER_DISPLAY_NAME_TOO_LONG")
    email = normalize_email(payload.get("email"))
    phone = normalize_phone(payload.get("phone"))
    if not email and not phone:
        raise ValueError("CUSTOMER_CONTACT_METHOD_REQUIRED")
    if email and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise ValueError("CUSTOMER_EMAIL_INVALID")
    if phone and not (7 <= len(phone) <= 18):
        raise ValueError("CUSTOMER_PHONE_INVALID")

    vertical = _require_option(catalogs, "vertical", payload.get("vertical"), required=True)
    subvertical = _require_option(catalogs, "subvertical", payload.get("subvertical"), required=False)
    business_size = _require_option(catalogs, "business_size", payload.get("businessSize"), required=True)
    operation_mode = _require_option(catalogs, "operation_mode", payload.get("operationMode"), required=True)
    acquisition = _require_option(catalogs, "acquisition_channel", payload.get("acquisitionChannel"), required=True)
    contact_role = _require_option(catalogs, "contact_role", payload.get("contactRole"), required=False)
    country = _require_option(catalogs, "country", payload.get("country"), required=False)
    state = _require_option(catalogs, "state_mx", payload.get("state"), required=False) if country == "MX" else ""
    if country and country != "MX" and payload.get("state"):
        raise ValueError("CUSTOMER_STATE_ONLY_SUPPORTED_FOR_MX_CATALOG")

    if subvertical:
        item = _option_map(catalogs, "subvertical").get(subvertical) or {}
        parents = (item.get("metadata") or {}).get("parentVerticals") or []
        if parents and vertical not in parents and subvertical != "other":
            raise ValueError(f"CUSTOMER_SUBVERTICAL_MISMATCH:{vertical}:{subvertical}")

    other_values = dict(payload.get("other") or {})
    selected = {"vertical": vertical, "subvertical": subvertical, "operationMode": operation_mode, "acquisitionChannel": acquisition, "contactRole": contact_role, "country": country}
    catalog_by_field = {"vertical":"vertical","subvertical":"subvertical","operationMode":"operation_mode","acquisitionChannel":"acquisition_channel","contactRole":"contact_role","country":"country"}
    missing_other = [catalog_by_field[field] for field, value in selected.items() if value == "other" and not str(other_values.get(field) or "").strip()]
    if missing_other:
        raise ValueError("CUSTOMER_OTHER_TEXT_REQUIRED:" + ",".join(sorted(missing_other)))

    return {
        "displayName": name,
        "legalName": str(payload.get("legalName") or "").strip()[:140] or None,
        "contactName": str(payload.get("contactName") or "").strip()[:120] or None,
        "email": email or None,
        "phone": phone or None,
        "vertical": vertical,
        "subvertical": subvertical or None,
        "businessSize": business_size,
        "operationMode": operation_mode,
        "acquisitionChannel": acquisition,
        "contactRole": contact_role or None,
        "country": country or None,
        "state": state or None,
        "city": str(payload.get("city") or "").strip()[:100] or None,
        "zone": str(payload.get("zone") or "").strip()[:100] or None,
        "other": other_values,
        "sourceRequestId": str(payload.get("clientRequestId") or "").strip()[:120] or None,
    }


def recommendation_for(catalogs: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    plan_options = _option_map(catalogs, "license_plan")
    plan_rank = {code: int((item.get("metadata") or {}).get("tier") or 0) for code, item in plan_options.items()}
    valid_plans = set(plan_options)
    vertical = str(payload.get("vertical") or "")
    size = str(payload.get("businessSize") or "")
    operation = str(payload.get("operationMode") or "")
    vertical_meta = (_option_map(catalogs, "vertical").get(vertical) or {}).get("metadata") or {}
    size_meta = (_option_map(catalogs, "business_size").get(size) or {}).get("metadata") or {}
    op_meta = (_option_map(catalogs, "operation_mode").get(operation) or {}).get("metadata") or {}
    candidates = [vertical_meta.get("suggestedPlan"), size_meta.get("minimumPlan"), op_meta.get("minimumPlan")]
    candidates = [code for code in candidates if code in valid_plans]
    if not candidates:
        candidates = ["TABLET_PRO"] if "TABLET_PRO" in valid_plans else list(valid_plans)[:1]
    plan = max(candidates, key=lambda code: plan_rank.get(code, 0)) if candidates else "TABLET_PC_MANAGED"
    modules = list(dict.fromkeys(list(vertical_meta.get("modules") or [])))
    if not modules:
        modules = list((plan_options.get(plan) or {}).get("metadata", {}).get("features") or [])
    review = bool(size_meta.get("commercialReviewRequired"))
    return {
        "suggestedPlan": plan,
        "suggestedModules": modules,
        "suggestedDeviceType": str(op_meta.get("suggestedDeviceType") or "tablet_pos"),
        "commercialReviewRequired": review,
        "commercialReviewReason": str(size_meta.get("reason") or "") if review else "",
        "contractTemplate": f"contract_{vertical or 'general'}",
    }
