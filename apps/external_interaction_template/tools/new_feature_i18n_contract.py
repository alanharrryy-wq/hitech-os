#!/usr/bin/env python3
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
