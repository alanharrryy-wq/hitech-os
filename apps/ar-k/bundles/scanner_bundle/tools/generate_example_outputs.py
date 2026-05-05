from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

if __package__ in {None, ''}:
    bundle_root = Path(__file__).resolve().parents[1]
    if str(bundle_root) not in sys.path:
        sys.path.insert(0, str(bundle_root))

from contracts_py.scanner_logic import scan_tree
from fixtures_py.catalog import selected_verification_cases


def generate_example_outputs(output_root: Path) -> list[Path]:
    output_root.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for case in selected_verification_cases():
        with tempfile.TemporaryDirectory() as tmp:
            source_root = Path(tmp) / case.name
            case.write_tree(source_root)
            artifacts = scan_tree(source_root)
            case_root = output_root / case.name
            case_root.mkdir(parents=True, exist_ok=True)
            for name, payload in artifacts.items():
                target = case_root / name
                target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')
                written.append(target)
    return written


def main(argv: list[str]) -> int:
    output_root = Path(argv[1]) if len(argv) > 1 else Path.cwd() / '.ark_install' / 'scanner_bundle' / 'verification_outputs' / 'manual'
    written = generate_example_outputs(output_root)
    print(f'generated_files={len(written)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
