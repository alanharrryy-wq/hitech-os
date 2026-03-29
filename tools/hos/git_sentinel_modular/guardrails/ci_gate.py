import os

def prevent_ci_execution():

    ci_vars = [
        "CI",
        "GITHUB_ACTIONS",
        "GITLAB_CI",
        "BUILD_ID",
    ]

    for var in ci_vars:
        if os.getenv(var):
            raise RuntimeError(
                "Git Sentinel execution blocked in CI environment"
            )
