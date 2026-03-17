from pathlib import Path

from sentinel_shadow import prepare_shadow_run, finalize_shadow_run
from sentinel_shadow_apply import run_shadow_apply_engine
from sentinel_promotion import build_promotion_bundle

def main():
    ctx = prepare_shadow_run()
    workspace = ctx["workspace"]

    overlay_source = Path(r"F:\some\overlay")

    run_shadow_apply_engine(
        workspace=workspace,
        overlay_source=overlay_source,
        finalize_callable=finalize_shadow_run,
    )

    result = build_promotion_bundle(workspace_root=workspace.root)
    print(result["promotion_review_md"])
    print(result["decision"]["status"])

if __name__ == "__main__":
    main()
