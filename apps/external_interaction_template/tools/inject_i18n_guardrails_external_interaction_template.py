#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_NAME = "inject_i18n_guardrails_external_interaction_template.py"
DEFAULT_ROOT = Path(r"F:\repos\hitech-os\apps\external_interaction_template")
TX_DIR = Path("reports") / "patch_transactions"
RUN_DIR = Path("reports") / "patch_runs"
ROLLBACK_DIR = Path("reports") / "rollback"
BACKUP_SCOPE = "i18n_guardrails"
ENCODING = "utf-8"

ENUM_LABELS_TS = r'''import { translate } from "@/lib/i18n/dictionary";
import type { DispatchStatus, RecordState, SyncStatus } from "@/lib/core/types";
import { formatHumanLabel, resolveActiveLocale } from "@/lib/utils";

export type Translator = (key: string, values?: Record<string, string | number>) => string;

function fallbackLabel(value: string): string {
  return formatHumanLabel(value);
}

export function mapRecordStateLabel(state: RecordState | string, t: Translator): string {
  switch (state) {
    case "draft":
    case "submitted":
    case "in_review":
    case "awaiting_update":
    case "approved":
    case "rejected":
    case "dispatched":
    case "synced":
    case "failed":
      return t(`recordState.${state}.label`);
    default:
      return fallbackLabel(String(state));
  }
}

export function mapRecordStateDescription(state: RecordState | string, t: Translator): string {
  switch (state) {
    case "draft":
    case "submitted":
    case "in_review":
    case "awaiting_update":
    case "approved":
    case "rejected":
    case "dispatched":
    case "synced":
    case "failed":
      return t(`recordState.${state}.description`);
    default:
      return t("recordState.unknown.description");
  }
}

export function mapDispatchStatusLabel(status: DispatchStatus | string, t: Translator): string {
  switch (status) {
    case "pending":
    case "running":
    case "succeeded":
    case "failed":
      return t(`dispatchStatus.${status}.label`);
    default:
      return fallbackLabel(String(status));
  }
}

export function mapSyncStatusLabel(status: SyncStatus | string, t: Translator): string {
  switch (status) {
    case "pending":
    case "synced":
    case "failed":
    case "retryable":
      return t(`syncStatus.${status}.label`);
    default:
      return fallbackLabel(String(status));
  }
}

export function mapRecordStateLabelForLocale(state: RecordState | string, locale?: string | null): string {
  const activeLocale = resolveActiveLocale(locale);
  return mapRecordStateLabel(state, (key, values) => translate(activeLocale, key, values));
}

export function mapRecordStateDescriptionForLocale(state: RecordState | string, locale?: string | null): string {
  const activeLocale = resolveActiveLocale(locale);
  return mapRecordStateDescription(state, (key, values) => translate(activeLocale, key, values));
}
'''

FEATURE_CONTRACTS_TS = r'''export type DynamicContentMode = "frontend-owned" | "source-language" | "bilingual-data";

export interface FeatureI18nContract {
  namespace: string;
  ownsFrontendCopy: boolean;
  dynamicContentMode: DynamicContentMode;
  enumMaps: string[];
  requiredKeys: string[];
}

export function defineFeatureI18nContract(contract: FeatureI18nContract): FeatureI18nContract {
  return contract;
}
'''

FEATURE_CONTRACTS_README = r'''# Feature i18n contracts

Cada feature nueva debe declarar un archivo aquí para dejar explícito:

- namespace propietario
- si el copy es frontend-owned
- cómo se trata el schema dinámico
- qué enum maps reutiliza
- qué keys mínimas debe tener la feature

Ejemplo sugerido:

```ts
import { defineFeatureI18nContract } from "@/lib/i18n/feature-contracts";

export const paymentsI18nContract = defineFeatureI18nContract({
  namespace: "payments",
  ownsFrontendCopy: true,
  dynamicContentMode: "source-language",
  enumMaps: ["recordState", "syncStatus"],
  requiredKeys: [
    "payments.page.title",
    "payments.empty.title",
    "payments.filters.all"
  ]
});
```
'''

NEW_FEATURE_PY = r'''#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

DEFAULT_ROOT = Path(r"F:\repos\hitech-os\apps\external_interaction_template")

CONTRACT_TEMPLATE = """import {{ defineFeatureI18nContract }} from \"@/lib/i18n/feature-contracts\";

export const {name}I18nContract = defineFeatureI18nContract({{
  namespace: \"{slug}\",
  ownsFrontendCopy: true,
  dynamicContentMode: \"source-language\",
  enumMaps: [\"recordState\", \"syncStatus\"],
  requiredKeys: [
    \"{slug}.page.title\",
    \"{slug}.empty.title\",
    \"{slug}.filters.all\"
  ]
}});
"""

TEST_TEMPLATE = """import {{ describe, expect, it }} from \"vitest\";

import {{ getTranslator }} from \"@/lib/i18n/dictionary\";

describe(\"{slug} i18n contract\", () => {{
  it(\"keeps bilingual ownership keys wired\", () => {{
    const tEs = getTranslator(\"es\");
    const tEn = getTranslator(\"en\");

    expect(tEs(\"{slug}.page.title\")).not.toContain(\"[[missing:\");
    expect(tEn(\"{slug}.page.title\")).not.toContain(\"[[missing:\");
  }});
}});
"""

MESSAGE_BLOCK_ES = """
  \"{slug}.page.title\": \"TODO: título principal de {slug}\",
  \"{slug}.empty.title\": \"TODO: estado vacío de {slug}\",
  \"{slug}.filters.all\": \"Todos\",
"""

MESSAGE_BLOCK_EN = """
  \"{slug}.page.title\": \"TODO: primary title for {slug}\",
  \"{slug}.empty.title\": \"TODO: empty state for {slug}\",
  \"{slug}.filters.all\": \"All\",
"""


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def to_identifier(slug: str) -> str:
    parts = [part for part in slug.split("_") if part]
    if not parts:
        raise SystemExit("Feature name cannot be empty.")
    return parts[0] + "".join(part.title() for part in parts[1:])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a bilingual feature i18n contract scaffold.")
    parser.add_argument("feature", help="Feature slug or name, for example payments")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    slug = slugify(args.feature)
    identifier = to_identifier(slug)

    contracts_dir = root / "src" / "lib" / "i18n" / "feature-contracts"
    tests_dir = root / "tests"
    contracts_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)

    contract_path = contracts_dir / f"{slug}.ts"
    test_path = tests_dir / f"{slug}.i18n.contract.test.ts"

    contract_path.write_text(CONTRACT_TEMPLATE.format(name=identifier, slug=slug), encoding="utf-8")
    test_path.write_text(TEST_TEMPLATE.format(slug=slug), encoding="utf-8")

    for locale_path, block_template in [
        (root / "src" / "lib" / "i18n" / "messages" / "es.ts", MESSAGE_BLOCK_ES),
        (root / "src" / "lib" / "i18n" / "messages" / "en.ts", MESSAGE_BLOCK_EN),
    ]:
        text = locale_path.read_text(encoding="utf-8")
        if f'"{slug}.page.title"' not in text:
            idx = text.rfind("};")
            if idx == -1:
                raise SystemExit(f"Could not patch message file: {locale_path}")
            locale_path.write_text(text[:idx] + block_template.format(slug=slug) + text[idx:], encoding="utf-8")

    print(f"[OK] created {contract_path}")
    print(f"[OK] created {test_path}")
'''

I18N_POLICY_MD = r'''# i18n guardrails policy

## Core rule
UI text must be owned deliberately. No visible frontend copy should appear as an accidental inline string.

## Feature order of operations
1. Decide ownership.
   - Is this local copy?
   - Is this schema-driven content?
   - Is this actual state?
   - Is this backend evidence?
2. Put local copy under a clear namespace.
3. Do not place visible strings directly in JSX.
4. Use centralized enum display maps for states, roles, and statuses.
5. Declare the schema language contract explicitly.
6. Add minimum validation for locale switching and mixed-language regressions.

## Project rules
- Frontend-owned copy enters bilingual from day one.
- States and statuses use centralized label maps, not per-view improvisation.
- Dynamic schema content must choose a contract: `frontend-owned`, `source-language`, or `bilingual-data`.
- Backend evidence and raw errors stay as raw evidence unless a product decision says otherwise.

## Tooling
- `tools/enforce_i18n_guardrails.py` fails fast on message parity, placeholder drift, bad namespaces, and visible inline copy.
- `tools/i18n_guardrails_baseline.json` tracks current debt so CI only blocks new violations.
- `tools/new_feature_i18n_contract.py` scaffolds a new feature contract, bilingual keys, and a basic test.
'''

I18N_TEST_TS = r'''import { describe, expect, it } from "vitest";

import { stateDescription, stateLabel } from "@/lib/core/record-view";
import { getTranslator } from "@/lib/i18n/dictionary";
import { mapDispatchStatusLabel, mapRecordStateDescription, mapRecordStateLabel, mapSyncStatusLabel } from "@/lib/i18n/enum-labels";

describe("i18n guardrails", () => {
  it("centralizes record state labels and descriptions by locale", () => {
    expect(stateLabel("awaiting_update", "es")).toBe("Requiere actualización");
    expect(stateLabel("awaiting_update", "en")).toBe("Needs update");
    expect(stateDescription("approved", "es")).toBe("Aprobado y listo para despacho.");
    expect(stateDescription("approved", "en")).toBe("Approved and ready for dispatch.");
  });

  it("maps sync and dispatch statuses through a shared translator", () => {
    const tEs = getTranslator("es");
    const tEn = getTranslator("en");

    expect(mapRecordStateLabel("submitted", tEs)).toBe("Enviado");
    expect(mapRecordStateDescription("submitted", tEn)).toBe("Waiting for reviewer triage.");
    expect(mapDispatchStatusLabel("running", tEs)).toBe("En ejecución");
    expect(mapSyncStatusLabel("retryable", tEn)).toBe("Retryable");
  });
});
'''

GUARDRAILS_PY = r'''#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DEFAULT_ROOT = Path(r"F:\repos\hitech-os\apps\external_interaction_template")
MESSAGE_PATTERN = re.compile(r'"([^"]+)"\s*:\s*"((?:\\.|[^"\\])*)"')
PLACEHOLDER_PATTERN = re.compile(r"\{(\w+)\}")
JSX_TEXT_PATTERN = re.compile(r">\s*([^<{][^<>{}]*[A-Za-zÁÉÍÓÚáéíóúÑñ][^<>{}]*)\s*<")
VISIBLE_PROP_PATTERN = re.compile(r"\b(title|subtitle|description|label|placeholder|helperText|emptyText|tooltip|aria-label)\s*=\s*\"([^\"{][^\"]*[A-Za-zÁÉÍÓÚáéíóúÑñ][^\"]*)\"")
ALLOWED_DIRS = ("app", "components", "src")
IGNORE_DIRS = {"node_modules", ".next", ".turbo", ".git", "coverage", "reports", "storage"}
IGNORE_SUFFIXES = {".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx", ".stories.tsx"}

@dataclass
class Failure:
    code: str
    path: str
    line: int
    detail: str

    @property
    def signature(self) -> str:
        return f"{self.code}|{self.path}|{self.line}|{self.detail}"


def read_messages(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    return {match.group(1): bytes(match.group(2), "utf-8").decode("unicode_escape") for match in MESSAGE_PATTERN.finditer(text)}


def placeholders(value: str) -> tuple[str, ...]:
    return tuple(sorted(set(PLACEHOLDER_PATTERN.findall(value))))


def iter_code_files(root: Path) -> Iterable[Path]:
    for top in ALLOWED_DIRS:
        base = root / top
        if not base.exists():
            continue
        for current, dirnames, filenames in os.walk(base):
            dirnames[:] = [name for name in dirnames if name not in IGNORE_DIRS]
            current_path = Path(current)
            for name in filenames:
                path = current_path / name
                if path.suffix not in {".ts", ".tsx", ".js", ".jsx"}:
                    continue
                if any(str(path).endswith(suffix) for suffix in IGNORE_SUFFIXES):
                    continue
                yield path


def find_line(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def check_message_parity(root: Path) -> list[Failure]:
    failures: list[Failure] = []
    es_path = root / "src" / "lib" / "i18n" / "messages" / "es.ts"
    en_path = root / "src" / "lib" / "i18n" / "messages" / "en.ts"
    es = read_messages(es_path)
    en = read_messages(en_path)

    for missing in sorted(set(es) - set(en)):
        failures.append(Failure("missing-key-in-en", str(en_path.relative_to(root)), 1, missing))
    for missing in sorted(set(en) - set(es)):
        failures.append(Failure("missing-key-in-es", str(es_path.relative_to(root)), 1, missing))

    for key in sorted(set(es) & set(en)):
        if "." not in key:
            failures.append(Failure("non-namespaced-key", str(es_path.relative_to(root)), 1, key))
        if placeholders(es[key]) != placeholders(en[key]):
            failures.append(Failure("placeholder-mismatch", str(es_path.relative_to(root)), 1, f"{key}: es={placeholders(es[key])} en={placeholders(en[key])}"))
    return failures


def check_hardcoded_ui(root: Path) -> list[Failure]:
    failures: list[Failure] = []
    for path in iter_code_files(root):
        text = path.read_text(encoding="utf-8")
        relative = str(path.relative_to(root))
        for match in JSX_TEXT_PATTERN.finditer(text):
            value = " ".join(match.group(1).split())
            if value.startswith("//") or value.startswith("/*"):
                continue
            if value in {"use client", "GET", "POST", "PUT", "PATCH", "DELETE"}:
                continue
            failures.append(Failure("hardcoded-jsx-text", relative, find_line(text, match.start(1)), value))
        for match in VISIBLE_PROP_PATTERN.finditer(text):
            value = " ".join(match.group(2).split())
            failures.append(Failure("hardcoded-visible-prop", relative, find_line(text, match.start(2)), value))
    return failures


def check_contract_registry(root: Path) -> list[Failure]:
    failures: list[Failure] = []
    contracts_dir = root / "src" / "lib" / "i18n" / "feature-contracts"
    if not contracts_dir.exists():
        failures.append(Failure("missing-feature-contracts-dir", "src/lib/i18n/feature-contracts", 1, "directory missing"))
    return failures


def load_baseline(path: Path) -> set[str]:
    if not path.exists():
        return set()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return set()
    raw = payload.get("signatures")
    if not isinstance(raw, list):
        return set()
    return {str(item) for item in raw}


def save_baseline(path: Path, failures: list[Failure]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    signatures = sorted(item.signature for item in failures)
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
            if existing.get("signatures") == signatures:
                return
        except Exception:
            pass
    payload = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "signatures": signatures,
        "failures": [asdict(item) for item in failures],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def collect_failures(root: Path) -> list[Failure]:
    return [*check_message_parity(root), *check_contract_registry(root), *check_hardcoded_ui(root)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-fast i18n guardrails for external_interaction_template.")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--update-baseline", action="store_true")
    parser.add_argument("--baseline")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    baseline_path = Path(args.baseline).expanduser().resolve() if args.baseline else root / "tools" / "i18n_guardrails_baseline.json"
    failures = collect_failures(root)

    if args.update_baseline:
        save_baseline(baseline_path, failures)
        print(f"[OK] baseline updated: {baseline_path}")
        return 0

    baseline = load_baseline(baseline_path)
    new_failures = [item for item in failures if item.signature not in baseline]
    payload = {
        "root": str(root),
        "checked_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "baseline_path": str(baseline_path),
        "failure_count": len(failures),
        "new_failure_count": len(new_failures),
        "failures": [asdict(item) for item in failures],
        "new_failures": [asdict(item) for item in new_failures],
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        if new_failures:
            for item in new_failures:
                print(f"[FAIL] {item.code}: {item.path}:{item.line} -> {item.detail}")
        else:
            print("[OK] i18n guardrails passed without new violations.")
            if failures:
                print(f"[INFO] existing baseline violations tracked: {len(failures)}")

    return 1 if new_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

RECORD_VIEW_IMPORT_OLD = 'import { formatHumanLabel, formatValue } from "@/lib/utils";'
RECORD_VIEW_IMPORT_NEW = 'import { mapRecordStateDescriptionForLocale, mapRecordStateLabelForLocale } from "@/lib/i18n/enum-labels";\nimport { formatValue } from "@/lib/utils";'

STATE_LABEL_BLOCK_OLD = '''export function stateLabel(state: RecordState): string {
  return formatHumanLabel(state);
}

export function stateDescription(state: RecordState): string {
  switch (state) {
    case "draft":
      return "Collecting inputs before submission.";
    case "submitted":
      return "Waiting for reviewer triage.";
    case "in_review":
      return "Under active operator review.";
    case "awaiting_update":
      return "Needs another external update.";
    case "approved":
      return "Approved and ready for dispatch.";
    case "rejected":
      return "Closed with rejection outcome.";
    case "dispatched":
      return "Outbound dispatch has been triggered.";
    case "synced":
      return "External sync completed successfully.";
    case "failed":
      return "Requires intervention before continuing.";
    default:
      return "Status unavailable.";
  }
}
'''

STATE_LABEL_BLOCK_NEW = '''export function stateLabel(state: RecordState, locale?: string | null): string {
  return mapRecordStateLabelForLocale(state, locale);
}

export function stateDescription(state: RecordState, locale?: string | null): string {
  return mapRecordStateDescriptionForLocale(state, locale);
}
'''

MESSAGES_BLOCK_ES = '''
  /* I18N_GUARDRAILS_START */
  "recordState.draft.label": "Borrador",
  "recordState.draft.description": "Borrador en captura antes del envío.",
  "recordState.submitted.label": "Enviado",
  "recordState.submitted.description": "Esperando triage de revisión.",
  "recordState.in_review.label": "En revisión",
  "recordState.in_review.description": "Bajo revisión activa de un operador.",
  "recordState.awaiting_update.label": "Requiere actualización",
  "recordState.awaiting_update.description": "Hace falta otra actualización externa.",
  "recordState.approved.label": "Aprobado",
  "recordState.approved.description": "Aprobado y listo para despacho.",
  "recordState.rejected.label": "Rechazado",
  "recordState.rejected.description": "Cerrado con resultado de rechazo.",
  "recordState.dispatched.label": "Despachado",
  "recordState.dispatched.description": "El despacho saliente ya fue activado.",
  "recordState.synced.label": "Sincronizado",
  "recordState.synced.description": "La sincronización externa terminó correctamente.",
  "recordState.failed.label": "Fallido",
  "recordState.failed.description": "Requiere intervención antes de continuar.",
  "recordState.unknown.description": "Estado no disponible.",
  "dispatchStatus.pending.label": "Pendiente",
  "dispatchStatus.running.label": "En ejecución",
  "dispatchStatus.succeeded.label": "Exitoso",
  "dispatchStatus.failed.label": "Fallido",
  "syncStatus.pending.label": "Pendiente",
  "syncStatus.synced.label": "Sincronizado",
  "syncStatus.failed.label": "Fallido",
  "syncStatus.retryable.label": "Reintentable",
  /* I18N_GUARDRAILS_END */
'''

MESSAGES_BLOCK_EN = '''
  /* I18N_GUARDRAILS_START */
  "recordState.draft.label": "Draft",
  "recordState.draft.description": "Draft capture before submission.",
  "recordState.submitted.label": "Submitted",
  "recordState.submitted.description": "Waiting for reviewer triage.",
  "recordState.in_review.label": "In review",
  "recordState.in_review.description": "Under active operator review.",
  "recordState.awaiting_update.label": "Needs update",
  "recordState.awaiting_update.description": "Needs another external update.",
  "recordState.approved.label": "Approved",
  "recordState.approved.description": "Approved and ready for dispatch.",
  "recordState.rejected.label": "Rejected",
  "recordState.rejected.description": "Closed with rejection outcome.",
  "recordState.dispatched.label": "Dispatched",
  "recordState.dispatched.description": "Outbound dispatch has been triggered.",
  "recordState.synced.label": "Synced",
  "recordState.synced.description": "External sync completed successfully.",
  "recordState.failed.label": "Failed",
  "recordState.failed.description": "Requires intervention before continuing.",
  "recordState.unknown.description": "Status unavailable.",
  "dispatchStatus.pending.label": "Pending",
  "dispatchStatus.running.label": "Running",
  "dispatchStatus.succeeded.label": "Succeeded",
  "dispatchStatus.failed.label": "Failed",
  "syncStatus.pending.label": "Pending",
  "syncStatus.synced.label": "Synced",
  "syncStatus.failed.label": "Failed",
  "syncStatus.retryable.label": "Retryable",
  /* I18N_GUARDRAILS_END */
'''

PACKAGE_SCRIPTS = {
    "i18n:guardrails": "python tools/enforce_i18n_guardrails.py --root .",
    "i18n:new-feature": "python tools/new_feature_i18n_contract.py --root .",
    "i18n:guardrails:update-baseline": "python tools/enforce_i18n_guardrails.py --root . --update-baseline"
}


class InjectorError(RuntimeError):
    pass


@dataclass
class FileChange:
    path: str
    action: str
    changed: bool


@dataclass
class RunManifest:
    tool: str
    mode: str
    root: str
    timestamp_utc: str
    backup_dir: str | None
    changes: list[FileChange]


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso_now() -> str:
    return utc_now().isoformat()


def stamp_now() -> str:
    return utc_now().strftime("%Y%m%dT%H%M%SZ")


def read_text(path: Path) -> str:
    return path.read_text(encoding=ENCODING)


def write_text(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = content.replace("\r\n", "\n")
    if path.exists() and read_text(path) == normalized:
        return False
    path.write_text(normalized, encoding=ENCODING, newline="\n")
    return True


def ensure_root(root: Path) -> None:
    required = [root / "package.json", root / "src" / "lib" / "i18n", root / "tests"]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise InjectorError("Target root does not look like external_interaction_template. Missing: " + ", ".join(missing))


def backup_file(root: Path, path: Path, backup_root: Path) -> None:
    if not path.exists():
        return
    rel = path.relative_to(root)
    destination = backup_root / rel
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)


def relative(path: Path, root: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def replace_exact(text: str, old: str, new: str, path: Path) -> str:
    if new in text:
        return text
    if old not in text:
        raise InjectorError(f"Expected block not found while patching {path}")
    return text.replace(old, new, 1)


def insert_before_last(text: str, needle: str, block: str, path: Path) -> str:
    if "I18N_GUARDRAILS_START" in text:
        return text
    index = text.rfind(needle)
    if index == -1:
        raise InjectorError(f"Could not find insertion point '{needle}' in {path}")
    return text[:index] + block + text[index:]


def patch_package_json(path: Path) -> bool:
    data = json.loads(read_text(path))
    scripts = data.setdefault("scripts", {})
    changed = False
    for key, value in PACKAGE_SCRIPTS.items():
        if scripts.get(key) != value:
            scripts[key] = value
            changed = True
    if changed:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding=ENCODING, newline="\n")
    return changed


def apply_injection(root: Path, dry_run: bool = False) -> RunManifest:
    ensure_root(root)
    stamp = stamp_now()
    backup_root = root / ROLLBACK_DIR / BACKUP_SCOPE / stamp
    baseline_path = root / "tools" / "i18n_guardrails_baseline.json"
    changes: list[FileChange] = []

    owned_files: list[tuple[Path, str]] = [
        (root / "src" / "lib" / "i18n" / "enum-labels.ts", ENUM_LABELS_TS),
        (root / "src" / "lib" / "i18n" / "feature-contracts.ts", FEATURE_CONTRACTS_TS),
        (root / "src" / "lib" / "i18n" / "feature-contracts" / "README.md", FEATURE_CONTRACTS_README),
        (root / "tools" / "new_feature_i18n_contract.py", NEW_FEATURE_PY),
        (root / "tools" / "enforce_i18n_guardrails.py", GUARDRAILS_PY),
        (root / "docs" / "i18n-policy.md", I18N_POLICY_MD),
        (root / "tests" / "i18n-guardrails.contract.test.ts", I18N_TEST_TS),
    ]

    existing_files_to_patch = [
        root / "package.json",
        root / "src" / "lib" / "core" / "record-view.ts",
        root / "src" / "lib" / "i18n" / "messages" / "es.ts",
        root / "src" / "lib" / "i18n" / "messages" / "en.ts",
        baseline_path,
    ]

    if not dry_run:
        for file_path in existing_files_to_patch:
            backup_file(root, file_path, backup_root)

    for file_path, content in owned_files:
        changed = not (file_path.exists() and read_text(file_path) == content.replace("\r\n", "\n"))
        changes.append(FileChange(relative(file_path, root), "write", changed))
        if not dry_run and changed:
            write_text(file_path, content)
            if file_path.suffix == ".py":
                try:
                    file_path.chmod(file_path.stat().st_mode | 0o111)
                except OSError:
                    pass

    package_changed = False
    if root.joinpath("package.json").exists():
        if not dry_run:
            package_changed = patch_package_json(root / "package.json")
        else:
            data = json.loads(read_text(root / "package.json"))
            package_changed = any(data.get("scripts", {}).get(key) != value for key, value in PACKAGE_SCRIPTS.items())
    changes.append(FileChange("package.json", "patch-json", package_changed))

    record_path = root / "src" / "lib" / "core" / "record-view.ts"
    record_text_before = read_text(record_path)
    record_text_after = replace_exact(record_text_before, RECORD_VIEW_IMPORT_OLD, RECORD_VIEW_IMPORT_NEW, record_path)
    record_text_after = replace_exact(record_text_after, STATE_LABEL_BLOCK_OLD, STATE_LABEL_BLOCK_NEW, record_path)
    record_changed = record_text_after != record_text_before
    changes.append(FileChange(relative(record_path, root), "patch", record_changed))
    if not dry_run and record_changed:
        write_text(record_path, record_text_after)

    for locale_file, block in [
        (root / "src" / "lib" / "i18n" / "messages" / "es.ts", MESSAGES_BLOCK_ES),
        (root / "src" / "lib" / "i18n" / "messages" / "en.ts", MESSAGES_BLOCK_EN),
    ]:
        before = read_text(locale_file)
        after = insert_before_last(before, "};", block, locale_file)
        changed = after != before
        changes.append(FileChange(relative(locale_file, root), "patch", changed))
        if not dry_run and changed:
            write_text(locale_file, after)

    baseline_changed = False
    if not dry_run:
        baseline_before = read_text(baseline_path) if baseline_path.exists() else None
        result = subprocess.run(
            [sys.executable, str(root / "tools" / "enforce_i18n_guardrails.py"), "--root", str(root), "--update-baseline"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise InjectorError(f"Failed to update i18n baseline: {result.stderr or result.stdout}")
        baseline_after = read_text(baseline_path) if baseline_path.exists() else None
        baseline_changed = baseline_before != baseline_after
    changes.append(FileChange(relative(baseline_path, root), "baseline", baseline_changed))

    manifest = RunManifest(
        tool=SCRIPT_NAME,
        mode="dry-run" if dry_run else "apply",
        root=str(root),
        timestamp_utc=iso_now(),
        backup_dir=None if dry_run else str(backup_root),
        changes=changes,
    )

    if not dry_run:
        payload = asdict(manifest)
        for target in [
            root / TX_DIR / f"{BACKUP_SCOPE}_{stamp}.json",
            root / RUN_DIR / f"{BACKUP_SCOPE}_{stamp}.json",
        ]:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding=ENCODING, newline="\n")

    return manifest


def rollback_latest(root: Path) -> RunManifest:
    tx_root = root / TX_DIR
    manifests = sorted(tx_root.glob(f"{BACKUP_SCOPE}_*.json"))
    if not manifests:
        raise InjectorError("No rollback manifest found.")
    latest = manifests[-1]
    data = json.loads(read_text(latest))
    backup_dir_raw = data.get("backup_dir")
    if not backup_dir_raw:
        raise InjectorError("Latest manifest does not contain a backup directory.")
    backup_dir = Path(backup_dir_raw)
    if not backup_dir.exists():
        raise InjectorError(f"Backup directory does not exist: {backup_dir}")

    restored: list[FileChange] = []
    for item in data.get("changes", []):
        rel = item.get("path")
        if not rel:
            continue
        target = root / rel
        backup_path = backup_dir / rel
        if backup_path.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_path, target)
            restored.append(FileChange(rel, "restore", True))
        elif target.exists() and item.get("action") in {"write", "baseline"}:
            target.unlink()
            restored.append(FileChange(rel, "delete-generated", True))

    manifest = RunManifest(
        tool=SCRIPT_NAME,
        mode="rollback",
        root=str(root),
        timestamp_utc=iso_now(),
        backup_dir=str(backup_dir),
        changes=restored,
    )
    report = root / RUN_DIR / f"{BACKUP_SCOPE}_rollback_{stamp_now()}.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(asdict(manifest), indent=2, ensure_ascii=False) + "\n", encoding=ENCODING, newline="\n")
    return manifest


def print_manifest(manifest: RunManifest) -> None:
    print(f"[{manifest.mode.upper()}] {manifest.tool}")
    print(f"root: {manifest.root}")
    if manifest.backup_dir:
        print(f"backup: {manifest.backup_dir}")
    changed = [item for item in manifest.changes if item.changed]
    unchanged = [item for item in manifest.changes if not item.changed]
    print(f"changed: {len(changed)} | unchanged: {len(unchanged)}")
    for item in manifest.changes:
        flag = "WRITE" if item.changed else "SKIP"
        print(f"- {flag:<5} {item.action:<12} {item.path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inject i18n guardrails into external_interaction_template.")
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="Absolute path to apps/external_interaction_template")
    parser.add_argument("--dry-run", action="store_true", help="Preview file changes without writing them")
    parser.add_argument("--rollback-latest", action="store_true", help="Restore the latest backup created by this injector")
    args = parser.parse_args(argv)

    root = Path(args.root).expanduser().resolve()

    try:
        manifest = rollback_latest(root) if args.rollback_latest else apply_injection(root, dry_run=args.dry_run)
        print_manifest(manifest)
        return 0
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
