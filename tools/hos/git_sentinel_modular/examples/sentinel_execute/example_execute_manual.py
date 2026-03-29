from pathlib import Path
from sentinel_execute import execute_manual_promotion

def main():
    workspace_root = Path(r"C:\Users\alanh\AppData\Local\HITECH-OS\git_sentinel\runtime\shadow_mode\shadow_demo")
    target_root = Path(r"F:\repos\hitech-os\tools\hos\git_sentinel_modular")

    result = execute_manual_promotion(
        workspace_root=workspace_root,
        target_root=target_root,
        do_execute=False,
    )
    print(result["summary"])

if __name__ == "__main__":
    main()
