from __future__ import annotations

import difflib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .canonical import canonical_sha256, file_sha256, read_json, write_json
from .errors import ContractError, DriftError


TASK_ID = "ATLASFIN_COBRAR_FULL_GOVERNED_APPLICATION_V1"
CONTROL_ID = "ATLASFIN.CONTROL.TABLET.POS.COBRAR.V1"
TRANSACTION_ID = "ATLASFIN.APPLY.TABLET.POS.COBRAR.V1"
COMPONENT_UI_ID = "TB-POS-PAY-COBRAR-BTN-01"
RECIPE_ID = "REC.button.primary"
VISUAL_STACK_ID = "VSTACK.ACT.PRIMARY.TABLET.POS.COBRAR.V1"
BINDING_ID = "BND.ACT.PRIMARY.TABLET.POS.COBRAR.V1"
ADAPTER_ID = "ADP.TB.TOUCH.V2"
LAYER_ID = "LYR.ACT.PRIMARY.TABLET.POS.COBRAR.BASE"
IMPLEMENTATION_LAYER_ID = "products.tablet.app.components.pos.pos.module.css.cobrarreferencebutton"
PLAN_ID = "BRPLAN.ca4eebf8f3a79d3ec6944488"
PLAN_CHECKSUM = "cce8fd8567744602264cf386902ad2e8e1f78042919a4b9365d158c351f83153"
OWNER_PATH = "apps/terminal-de-venta-system/products/tablet/app/components/pos/pos-ticket-panel.tsx"
AUTHORITY_CSS_PATH = "prisma-html/authority/rifat/tablet/runtime-sources/modules/pos/pos.module.css"
PRODUCT_CSS_PATH = "apps/terminal-de-venta-system/products/tablet/app/components/pos/pos.module.css"
EXPECTED_SELECTORS = [
    ".cobrarReferenceButton",
    ".cobrarReferenceButton::before",
    ".cobrarReferenceButton:hover",
    ".cobrarReferenceButton:hover::before",
    ".cobrarReferenceButton:disabled",
    ".cobrarIcon",
    ".cobrarCopy",
    ".cobrarCopy strong",
    ".cobrarCopy small",
    ".cobrarAmount",
    '[data-prisma-state="loading"]',
]

OLD_BLOCK = """  .cobrarReferenceButton {
    position: relative;
    display: grid;
    grid-template-columns: 42px minmax(0, 1fr) auto;
    align-items: center;
    gap: 10px;
    min-height: 68px;
    padding: 9px 14px;
    overflow: hidden;
    border: 1px solid rgba(138, 231, 255, 0.72);
    border-radius: 18px;
    background:
      radial-gradient(circle at 14% 18%, rgba(129, 235, 255, 0.58), transparent 30%),
      linear-gradient(112deg, #287df5, #2153d2 54%, #3ac7f0);
    box-shadow:
      0 20px 46px rgba(30, 92, 226, 0.34),
      0 0 0 1px rgba(112, 224, 255, 0.13),
      inset 0 1px 0 rgba(255, 255, 255, 0.34);
    color: #ffffff;
    cursor: pointer;
    font: inherit;
    text-align: left;
    text-shadow: 0 1px 10px rgba(0, 31, 84, 0.34);
    transition:
      transform var(--prisma-motion-fast),
      filter var(--prisma-motion-fast),
      box-shadow var(--prisma-motion-fast);
  }

  .cobrarReferenceButton::before {
    content: "";
    position: absolute;
    top: -30%;
    bottom: -30%;
    left: -38%;
    width: 28%;
    pointer-events: none;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.42), transparent);
    transform: skewX(-18deg);
    transition: left 420ms cubic-bezier(0.22, 1, 0.36, 1);
  }

  .cobrarReferenceButton:hover {
    filter: saturate(1.04) brightness(1.03);
    box-shadow:
      0 24px 54px rgba(30, 92, 226, 0.40),
      0 0 28px rgba(70, 202, 255, 0.18),
      inset 0 1px 0 rgba(255, 255, 255, 0.38);
    transform: translateY(-2px);
  }

  .cobrarReferenceButton:hover::before {
    left: 112%;
  }

  .cobrarReferenceButton:disabled {
    cursor: not-allowed;
    filter: saturate(0.45);
    opacity: 0.56;
    transform: none;
  }

  .cobrarIcon {
    display: grid;
    width: 42px;
    height: 42px;
    place-items: center;
    border: 1px solid rgba(3, 17, 30, 0.2);
    border-radius: 14px;
    background: rgba(5, 31, 47, 0.13);
  }
"""

NEW_BLOCK = """  .cobrarReferenceButton {
    position: relative;
    display: grid;
    grid-template-columns: 42px minmax(0, 1fr) auto;
    align-items: center;
    gap: 10px;
    min-height: 68px;
    padding: 9px 14px;
    overflow: hidden;
    border: 1px solid color-mix(in srgb, #ffffff 34%, #2563eb);
    border-radius: 14px;
    background: linear-gradient(135deg, #2563eb, color-mix(in srgb, #2563eb 78%, #0f172a));
    box-shadow:
      0 14px 32px color-mix(in srgb, #2563eb 28%, transparent),
      inset 0 1px 0 color-mix(in srgb, #ffffff 30%, transparent);
    color: #ffffff;
    cursor: pointer;
    font: inherit;
    text-align: left;
    text-shadow: 0 1px 8px color-mix(in srgb, #0f172a 30%, transparent);
    transition:
      transform 120ms cubic-bezier(0.22, 1, 0.36, 1),
      filter 120ms cubic-bezier(0.22, 1, 0.36, 1),
      box-shadow 120ms cubic-bezier(0.22, 1, 0.36, 1),
      border-color 120ms cubic-bezier(0.22, 1, 0.36, 1),
      background 120ms cubic-bezier(0.22, 1, 0.36, 1);
  }

  .cobrarReferenceButton::before {
    content: "";
    position: absolute;
    top: -30%;
    bottom: -30%;
    left: -38%;
    width: 28%;
    pointer-events: none;
    background: linear-gradient(90deg, transparent, color-mix(in srgb, #ffffff 34%, transparent), transparent);
    opacity: 1;
    transform: translateX(0) skewX(-18deg);
    transition:
      transform 360ms cubic-bezier(0.22, 1, 0.36, 1),
      opacity 120ms cubic-bezier(0.22, 1, 0.36, 1);
  }

  .cobrarReferenceButton:hover {
    filter: saturate(1.03) brightness(1.02);
    border-color: color-mix(in srgb, #ffffff 46%, #2563eb);
    box-shadow:
      0 18px 40px color-mix(in srgb, #2563eb 34%, transparent),
      0 0 22px color-mix(in srgb, #60a5fa 16%, transparent),
      inset 0 1px 0 color-mix(in srgb, #ffffff 34%, transparent);
    transform: translateY(-1px);
  }

  .cobrarReferenceButton:hover::before {
    left: 112%;
    transform: translateX(535%) skewX(-18deg);
  }

  .cobrarReferenceButton:disabled {
    cursor: not-allowed;
    filter: saturate(0.20) brightness(0.96);
    box-shadow: none;
    opacity: 0.48;
    transform: none;
  }

  .cobrarIcon {
    display: grid;
    width: 42px;
    height: 42px;
    place-items: center;
    border: 1px solid color-mix(in srgb, #0f172a 20%, transparent);
    border-radius: 12px;
    background: color-mix(in srgb, #ffffff 14%, transparent);
    box-shadow: inset 0 1px 0 color-mix(in srgb, #ffffff 22%, transparent);
  }
"""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _fail(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".atlasfin-tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def validate_request(request: dict[str, Any]) -> None:
    exact = {
        "schema": "PRISMA_ATLASFIN_VISUAL_APPLICATION_REQUEST_V1",
        "schemaVersion": "1.0.0",
        "taskId": TASK_ID,
        "controlId": CONTROL_ID,
        "transactionId": TRANSACTION_ID,
        "componentUiId": COMPONENT_UI_ID,
        "recipeId": RECIPE_ID,
        "visualStackId": VISUAL_STACK_ID,
        "bindingId": BINDING_ID,
        "adapterId": ADAPTER_ID,
        "layerId": LAYER_ID,
        "implementationLayerId": IMPLEMENTATION_LAYER_ID,
        "planId": PLAN_ID,
        "planChecksum": PLAN_CHECKSUM,
        "authorization": "EXPLICIT_USER_AUTHORIZATION_ATLASFIN_COBRAR_V1",
    }
    for key, expected in exact.items():
        _fail(request.get(key) == expected, f"REQUEST_EXACT_VALUE_MISMATCH:{key}")
    _fail(request.get("productFiles") == [PRODUCT_CSS_PATH], "REQUEST_PRODUCT_ALLOWLIST_MISMATCH")
    _fail(request.get("maxProductFileCount") == 1, "REQUEST_PRODUCT_FILE_LIMIT_MISMATCH")
    _fail(request.get("selectors") == EXPECTED_SELECTORS, "REQUEST_SELECTOR_SET_OR_ORDER_MISMATCH")
    before = request.get("before")
    _fail(isinstance(before, dict), "REQUEST_BEFORE_REQUIRED")
    for key in ("ownerSha256", "authorityCssSha256", "productCssSha256"):
        _fail(isinstance(before.get(key), str) and len(before[key]) == 64, f"REQUEST_INVALID_HASH:{key}")
    evidence = request.get("beforeEvidence")
    _fail(isinstance(evidence, dict), "REQUEST_BEFORE_EVIDENCE_REQUIRED")
    _fail(evidence.get("phase") == "BEFORE", "REQUEST_BEFORE_EVIDENCE_PHASE_MISMATCH")
    _fail(evidence.get("status") == "PASS", "REQUEST_BEFORE_EVIDENCE_NOT_PASS")
    _fail(evidence.get("selector") == ".cobrarReferenceButton", "REQUEST_BEFORE_EVIDENCE_SELECTOR_MISMATCH")
    evidence_path = Path(str(evidence.get("path") or ""))
    _fail(evidence_path.is_absolute() and evidence_path.is_file(), "REQUEST_BEFORE_EVIDENCE_FILE_MISSING")
    _fail(file_sha256(evidence_path) == str(evidence.get("sha256")).lower(), "REQUEST_BEFORE_EVIDENCE_HASH_MISMATCH")


def _render_authority(current: bytes) -> tuple[bytes, str]:
    text = current.decode("utf-8")
    old_count = text.count(OLD_BLOCK)
    new_count = text.count(NEW_BLOCK)
    if old_count == 1 and new_count == 0:
        return text.replace(OLD_BLOCK, NEW_BLOCK, 1).encode("utf-8"), "PATCH_REQUIRED"
    if old_count == 0 and new_count == 1:
        return current, "ALREADY_APPLIED_AND_VERIFIED"
    raise DriftError(f"EXACT_COBRAR_BLOCK_DRIFT:old={old_count}:new={new_count}")


def _product_bytes(authority_bytes: bytes) -> bytes:
    header = (
        "/* @generated by prisma-html/tools/generate_tablet_visual_runtime.py\n"
        " * canonical-source: prisma-html/authority/rifat/tablet/runtime-sources/modules/pos/pos.module.css\n"
        " * manual-edits-forbidden: true\n"
        " */\n"
    ).encode("utf-8")
    return header + authority_bytes.lstrip(b"\xef\xbb\xbf")


def execute_cobrar_transaction(request_path: str | Path, repo_root: str | Path, evidence_root: str | Path, mode: str) -> dict[str, Any]:
    request_file = Path(request_path).resolve()
    repo = Path(repo_root).resolve()
    evidence = Path(evidence_root).resolve()
    request = read_json(request_file)
    validate_request(request)
    owner = repo / OWNER_PATH
    authority_css = repo / AUTHORITY_CSS_PATH
    product_css = repo / PRODUCT_CSS_PATH
    requested_before = request["before"]
    observed = {
        "ownerSha256": file_sha256(owner),
        "authorityCssSha256": file_sha256(authority_css),
        "productCssSha256": file_sha256(product_css),
    }
    original_authority = authority_css.read_bytes()
    original_product = product_css.read_bytes()
    desired_authority, disposition = _render_authority(original_authority)
    desired_product = _product_bytes(desired_authority)
    _fail(observed["ownerSha256"] == str(requested_before["ownerSha256"]).lower(), "SOURCE_DRIFT:ownerSha256")
    if disposition == "PATCH_REQUIRED":
        for key in ("authorityCssSha256", "productCssSha256"):
            _fail(observed[key] == str(requested_before[key]).lower(), f"SOURCE_DRIFT:{key}")
    _fail(original_product == _product_bytes(original_authority), "GENERATED_PRODUCT_NOT_EXACT_AUTHORITY_PROJECTION")
    _fail(b"!important" not in desired_authority, "IMPORTANT_FORBIDDEN")
    diff = "".join(difflib.unified_diff(
        original_authority.decode("utf-8").splitlines(keepends=True),
        desired_authority.decode("utf-8").splitlines(keepends=True),
        fromfile=AUTHORITY_CSS_PATH,
        tofile=AUTHORITY_CSS_PATH,
    ))
    evidence.mkdir(parents=True, exist_ok=True)
    backup_dir = evidence / "rollback" / "before"
    result_path = evidence / "PRISMA_ATLASFIN_VISUAL_APPLICATION_RESULT_V1.json"
    diff_path = evidence / "COBRAR_EXACT_TARGET.preview.patch"
    diff_path.write_text(diff, encoding="utf-8", newline="\n")
    applied = False
    if mode == "apply" and disposition == "PATCH_REQUIRED":
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(authority_css, backup_dir / "authority-pos.module.css")
        shutil.copy2(product_css, backup_dir / "product-pos.module.css")
        write_json(backup_dir / "manifest.json", {
            "schema": "prisma.atlasfin.cobrar.rollback-manifest.v1",
            "authorityCssPath": AUTHORITY_CSS_PATH,
            "productCssPath": PRODUCT_CSS_PATH,
            "authorityCssSha256": observed["authorityCssSha256"],
            "productCssSha256": observed["productCssSha256"],
        })
        try:
            _atomic_write(authority_css, desired_authority)
            _atomic_write(product_css, desired_product)
            _fail(authority_css.read_bytes() == desired_authority, "POST_WRITE_AUTHORITY_BYTES_MISMATCH")
            _fail(product_css.read_bytes() == desired_product, "POST_WRITE_PRODUCT_BYTES_MISMATCH")
            applied = True
        except Exception:
            _atomic_write(authority_css, original_authority)
            _atomic_write(product_css, original_product)
            raise
    elif mode not in {"preview", "verify", "apply"}:
        raise ContractError(f"UNSUPPORTED_EXACT_TRANSACTION_MODE:{mode}")
    post_disposition = _render_authority(authority_css.read_bytes())[1]
    after = {
        "ownerSha256": file_sha256(owner),
        "authorityCssSha256": file_sha256(authority_css),
        "productCssSha256": file_sha256(product_css),
    }
    mutation_observed = any(
        after[key] != str(requested_before[key]).lower()
        for key in ("authorityCssSha256", "productCssSha256")
    )
    status = (
        "APPLIED_SOURCE_VALIDATION_PENDING_RUNTIME_VISUAL_CERTIFICATION"
        if applied
        else "SOURCE_APPLIED_AND_VERIFIED_PENDING_RUNTIME_VISUAL_CERTIFICATION"
        if post_disposition == "ALREADY_APPLIED_AND_VERIFIED" and mutation_observed
        else "ALREADY_APPLIED_AND_VERIFIED"
        if post_disposition == "ALREADY_APPLIED_AND_VERIFIED"
        else "PREVIEW_READY"
    )
    result = {
        "schema": "PRISMA_ATLASFIN_VISUAL_APPLICATION_RESULT_V1",
        "schemaVersion": "1.0.0",
        "taskId": TASK_ID,
        "controlId": CONTROL_ID,
        "transactionId": TRANSACTION_ID,
        "requestSha256": file_sha256(request_file),
        "mode": mode,
        "status": status,
        "sourceMutationPerformed": applied or mutation_observed,
        "productFileCount": 1,
        "productFiles": [PRODUCT_CSS_PATH],
        "authorityFiles": [AUTHORITY_CSS_PATH],
        "selectors": EXPECTED_SELECTORS,
        "policyOnlySelectors": ['[data-prisma-state="loading"]'],
        "before": requested_before,
        "observedAtExecution": observed,
        "after": after,
        "preview": {"path": str(diff_path), "sha256": file_sha256(diff_path), "changedLineCount": len(diff.splitlines())},
        "rollback": {"ready": applied, "path": str(backup_dir) if applied else None},
        "idempotencyDisposition": post_disposition,
        "createdAt": _utc_now(),
    }
    result["integrity"] = {"algorithm": "SHA-256", "canonicalPayloadSha256": canonical_sha256(result)}
    write_json(result_path, result)
    return result
