from pathlib import Path

from sentinel_cutover import build_cutover_readiness_bundle

def main():
    workspace_root = Path(r"C:\Users\alanh\AppData\Local\HITECH-OS\git_sentinel\runtime\shadow_mode\shadow_20260317_000000_demo")
    result = build_cutover_readiness_bundle(workspace_root=workspace_root)
    print(result["summary_path"])
    print(result["decision"]["status"])

if __name__ == "__main__":
    main()
