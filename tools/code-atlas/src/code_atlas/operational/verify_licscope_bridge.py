from __future__ import annotations

import argparse
import json


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--evidence-zip", default="")
    parser.parse_args(argv)
    result = {
        "ok": False,
        "status": "BLOCKED_PROJECT_SCOPE_ADAPTER_REQUIRED",
        "productionCertified": False,
        "message": "Historical implicit project scope verification is disabled. Configure and verify an explicit adapter.",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
