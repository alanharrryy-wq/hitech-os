from pathlib import Path
from sentinel_execute import build_execution_bundle

def main():
    workspace_root = Path(r"C:\Users\alanh\AppData\Local\HITECH-OS\git_sentinel\runtime\shadow_mode\shadow_demo")
    target_root = Path(r"F:\repos\hitech-os\tools\hos\git_sentinel_modular")
    result = build_execution_bundle(workspace_root=workspace_root, target_root=target_root)
    print(result["execution_dir"])
    print(result["plan_payload"]["counts"])

if __name__ == "__main__":
    main()
